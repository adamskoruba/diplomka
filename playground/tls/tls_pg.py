#!/usr/bin/env python3
"""
tls_compare.py - porovnanie TLS ClientHello HELLO paketov z Wireshark JSON exportu.

Práca s vlastným parsovaním ClientHello (nie len polia z JSON), pretože
Wireshark JSON export prepíše duplicitné kľúče ( tls.handshake.extension,
tls.handshake.ciphersuite, ...) - v JSON donc ostane len posledná hodnota.

Použitie:
    python tls_compare.py file1.json [file2.json ...]
    python tls_compare.py packet_chrome_157.json packet_firefox.json

Vstup: Wireshark "Export Packet Dissections - JSON" (aj Elasticsearch-like
formát s _source.layers), alebo output z ES search hit-ov (list of hits).

Výstup: pre každý súbor zhrnutie ClientHello, potom porovnanie každého
súboru s prvým (baseline) - verzie, cipher suites, extensions ( poradie a
hodnoty), JA3/JA4 fingerprinty, SNI, ALPN, supported groups, key shares, atď.
"""

import json
import sys
import argparse
from difflib import unified_diff

# ----------------------------------------------------------------------
# Pomocné: nájdenie reassembled TLS bytov v ľubovoľnom (vnorenom) JSON
# ----------------------------------------------------------------------

def find_key(obj, key):
    """Rekurzívne nájde prvú hodnotu pre kľúč v vnorenej štruktúre."""
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for v in obj.values():
            r = find_key(v, key)
            if r is not None:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = find_key(v, key)
            if r is not None:
                return r
    return None


def load_packets(path):
    """Načíta JSON súbor a vráti list 'paketov' (dict s layers ak existujú)."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    packets = []
    if isinstance(data, list):
        # ES search hits: [{'_index':..., '_source': {'layers': ...}}, ...]
        for item in data:
            if isinstance(item, dict) and "_source" in item:
                packets.append(item["_source"])
            elif isinstance(item, dict) and "layers" in item:
                packets.append(item)
        data = [p.get("layers", {}) for p in packets]
    elif isinstance(data, dict):
        # klasický Wireshark JSON export: {'_index':..., '_source': {'layers': ...}}
        src = data.get("_source", data)
        data = [src.get("layers", {})]
    else:
        raise ValueError(f"{path}: neznámy JSON formát")
    return data


def get_tls_plaintext(layers):
    """Vyťaží reassembled TLS data ako bytes (z tcp.reassembled.data)."""
    hexstr = find_key(layers, "tcp.reassembled.data")
    if hexstr is None:
        # fallback: spojiť vsetky tcp.payload / tcp.segment_data segmenty
        hexstr = find_key(layers, "tcp.segment_data")
    if hexstr is None:
        hexstr = find_key(layers, "tcp.payload")
    if hexstr is None:
        return None
    if isinstance(hexstr, list):
        hexstr = "".join(hexstr)
    return bytes.fromhex(hexstr.replace(":", ""))


# ----------------------------------------------------------------------
# Minimálny TLS ClientHello parser
# ----------------------------------------------------------------------

class R:
    """Reader cez bytes s bezpečným slicingom."""
    def __init__(self, b):
        self.b = b
        self.o = 0
    def u8(self):
        v = self.b[self.o]; self.o += 1; return v
    def u16(self):
        v = int.from_bytes(self.b[self.o:self.o+2], "big"); self.o += 2; return v
    def u24(self):
        v = int.from_bytes(self.b[self.o:self.o+3], "big"); self.o += 3; return v
    def take(self, n):
        v = self.b[self.o:self.o+n]; self.o += n; return v
    def rest(self):
        return self.b[self.o:]


def parse_client_hello(raw):
    """Parse TLS record(s) -> client hello handshake. Vráti dict alebo None."""
    r = R(raw)
    while r.o + 5 <= len(r.b):
        ct = r.u8(); ver = r.u16(); ln = r.u16()
        body = r.take(ln)
        if ct != 22:  # handshake
            continue
        hr = R(body)
        while hr.o + 4 <= len(hr.b):
            htype = hr.u8(); hlen = hr.u24()
            hbody = hr.take(hlen)
            if htype == 1:  # ClientHello
                return parse_ch_body(hbody)
    return None


def parse_ch_body(b):
    r = R(b)
    ch = {}
    ch["legacy_version"] = f"0x{r.u16():04x}"
    ch["random"] = r.take(32).hex(":")
    sid_len = r.u8()
    ch["session_id_len"] = sid_len
    ch["session_id"] = r.take(sid_len).hex(":")
    # cipher suites: 2-byte každý
    cs_raw = r.take(r.u16())
    ch["cipher_suites"] = [f"0x{int.from_bytes(cs_raw[i:i+2],'big'):04x}"
                           for i in range(0, len(cs_raw), 2)]
    cm_len = r.u8()
    ch["compression"] = [f"0x{x:02x}" for x in r.take(cm_len)]
    exts = []
    if r.o < len(r.b):
        ext_total = r.u16()
        er = R(r.take(ext_total))
        while er.o + 4 <= len(er.b):
            etype = er.u16(); elen = er.u16()
            edata = er.take(elen)
            exts.append((etype, edata))
    ch["extensions"] = exts
    ch["ext_types"] = [e[0] for e in exts]
    ch["parsed"] = parse_extensions(exts)
    return ch


# ----------------------------------------------------------------------
# Rozparsovanie hodnôt známych extensions
# ----------------------------------------------------------------------

EXT_NAMES = {
    0: "server_name", 5: "status_request", 10: "supported_groups",
    11: "ec_point_formats", 13: "signature_algorithms", 16: "ALPN",
    18: "signed_certificate_timestamp", 21: "padding",
    23: "ext_master_secret", 27: "compress_certificate",
    28: "record_size_limit", 31: "pre_shared_key",
    35: "session_ticket", 41: "pre_shared_key_modes",
    43: "supported_versions", 45: "psk_key_exchange_modes",
    51: "key_share", 65281: "renegotiation_info",
    65037: "ECH / encrypted_client_hello (grease)",
    17513: "application_settings", 30032: "30032 (Chrome private)",
}

GROUPS = {0x001d: "x25519", 0x0017: "secp256r1", 0x0018: "secp384r1",
          0x0019: "secp521r1", 0x0100: "ffdhe2048", 0x001a: "x448",
          0x0029: "x25519mlkem768", 0x0300: "gcsv256", 0x0101: "gcsv512"}
SIGS = {0x0403: "ecdsa_secp256r1_sha256", 0x0503: "rsa_pss_rsae_sha256",
        0x0804: "rsa_pss_rsae_sha256", 0x0805: "rsa_pss_pss_sha256",
        0x0401: "rsa_pkcs1_sha256", 0x0601: "rsa_pkcs1_sha512",
        0x0603: "ecdsa_secp521r1_sha512", 0x0809: "rsa_pss_pss_sha256",
        0xfe0d: "GDAPP-256", 0x0808: "rsa_pss_pss_sha384"}

def _list(b, item=2):
    return [int.from_bytes(b[i:i+item], "big") for i in range(0, len(b), item)]


def parse_extensions(exts):
    """Rozparsuje hodnoty najdôležitejších extensions -> dict type->summary."""
    out = {}
    for etype, edata in exts:
        name = EXT_NAMES.get(etype, f"ext_{etype}")
        try:
            if etype == 0:  # server_name
                r = R(edata); r.u16(); t = r.u8(); l = r.u16()
                out[etype] = r.take(l).decode("ascii", "replace")
            elif etype == 13:  # signature_algorithms
                l = int.from_bytes(edata[:2], "big")
                vals = _list(edata[2:2+l])
                out[etype] = ",".join(SIGS.get(v, f"0x{v:04x}") for v in vals)
            elif etype == 10:  # supported_groups
                l = int.from_bytes(edata[:2], "big")
                vals = _list(edata[2:2+l])
                out[etype] = ",".join(GROUPS.get(v, f"0x{v:04x}") for v in vals)
            elif etype == 16:  # ALPN
                r = R(edata); r.u16()
                protos = []
                while r.o < len(r.b):
                    pl = r.u8(); protos.append(r.take(pl).decode("ascii", "replace"))
                out[etype] = ",".join(protos)
            elif etype == 43:  # supported_versions
                ln = edata[0]; out[etype] = ",".join(
                    f"0x{int.from_bytes(edata[1+i:3+i],'big'):04x}"
                    for i in range(0, ln, 2))
            elif etype == 51:  # key_share
                r = R(edata); total = r.u16()
                shares = []
                while r.o < len(r.b):
                    g = r.u16(); l = r.u16()
                    gn = GROUPS.get(g, f"0x{g:04x}")
                    shares.append(f"{gn}({l}B)")
                out[etype] = ",".join(shares)
            elif etype == 41 or etype == 45:  # psk_key_exchange_modes
                ln = edata[0]
                out[etype] = ",".join(f"0x{x:02x}" for x in edata[1:1+ln])
            elif etype == 28 or etype == 0x001c:  # record_size_limit
                out[etype] = str(int.from_bytes(edata[:2], "big"))
            elif etype == 11:
                ln = edata[0]; out[etype] = ",".join(f"0x{x:02x}" for x in edata[1:1+ln])
            elif etype == 65281:
                out[etype] = "renegotiation_info (empty)"
            elif etype == 23:
                out[etype] = "present"
            elif etype == 35:
                out[etype] = "present (session_ticket)"
            else:
                out[etype] = f"{len(edata)}B: {edata[:24].hex(':' )}{'...' if len(edata)>24 else ''}"
        except Exception:
            out[etype] = f"<parse error> {edata.hex(':')[:60]}"
    return out


# ----------------------------------------------------------------------
# Zhrnutie jedného ClientHello
# ----------------------------------------------------------------------

def summarize(ch, layers, label):
    print(f"\n{'='*70}\n  {label}\n{'='*70}")
    print(f"  legacy_version      : {ch['legacy_version']}")
    print(f"  random              : {ch['random'][:47]}...")
    print(f"  session_id ({ch['session_id_len']:2d}B)  : {ch['session_id'][:47]}...")
    print(f"  compression         : {', '.join(ch['compression'])}")
    print(f"  ciphersuites ({len(ch['cipher_suites'])})   :")
    for i in range(0, len(ch["cipher_suites"]), 8):
        print("      " + " ".join(ch["cipher_suites"][i:i+8]))
    print(f"  extensions ({len(ch['ext_types'])}):")
    for etype, edata in ch["extensions"]:
        nm = EXT_NAMES.get(etype, "")
        val = ch["parsed"].get(etype, "")
        print(f"      0x{etype:04x} ({elen_len(edata):4d}B) {nm:<45} {val if isinstance(val,str) and len(str(val))<70 else str(val)[:70]+'...'}")
    ja3 = find_key(layers, "tls.handshake.ja3")
    ja3f = find_key(layers, "tls.handshake.ja3_full")
    ja4 = find_key(layers, "tls.handshake.ja4")
    ja4r = find_key(layers, "tls.handshake.ja4_r")
    if ja3: print(f"  JA3     : {ja3}")
    if ja3f: print(f"  JA3_full: {ja3f}")
    if ja4:  print(f"  JA4     : {ja4}")
    if ja4r: print(f"  JA4_r   : {ja4r}")


def elen_len(b):
    return len(b)


# ----------------------------------------------------------------------
# Porovnanie
# ----------------------------------------------------------------------

def diff_list(name, a, b, la, lb):
    if a == b:
        print(f"  [OK] {name}: identické")
        return
    print(f"  [DIFF] {name}:")
    d = list(unified_diff(a, b, fromfile=la, tofile=lb, lineterm="", n=0))
    for line in d[2:]:
        print(f"      {line}")
    sa, sb = set(a), set(b)
    if sa - sb: print(f"      len A (v {la}):      + {sorted(sa-sb)}")
    if sb - sa: print(f"      len B (v {lb}):      + {sorted(sb-sa)}")
    if a and b and a != b and set(a) == set(b):
        print("      => rovnaké hodnoty, ROZDIELNE PORADIE")


def diff_value(name, va, vb):
    if va == vb:
        print(f"  [OK] {name}: {va}")
    else:
        print(f"  [DIFF] {name}:\n      A: {va}\n      B: {vb}")


def compare(cha, chb, la, lb):
    print(f"\n{'='*70}\n  POROVNANIE: {la}  vs  {lb}\n{'='*70}")
    diff_value("legacy_version", cha["legacy_version"], chb["legacy_version"])
    diff_value("session_id_len", cha["session_id_len"], chb["session_id_len"])
    diff_value("compression", cha["compression"], chb["compression"])
    diff_list("cipher_suites", cha["cipher_suites"], chb["cipher_suites"], la, lb)
    diff_list("extension order", [f"0x{t:04x}" for t in cha["ext_types"]],
                                 [f"0x{t:04x}" for t in chb["ext_types"]], la, lb)
    print(f"  --- hodnoty spoločných extensions ---")
    common = [t for t in cha["ext_types"] if t in chb["ext_types"]]
    only_a = [t for t in cha["ext_types"] if t not in chb["ext_types"]]
    only_b = [t for t in chb["ext_types"] if t not in cha["ext_types"]]
    for t in common:
        nm = EXT_NAMES.get(t, f"ext_{t}")
        diff_value(f"0x{t:04x} {nm}", cha["parsed"].get(t, "?"), chb["parsed"].get(t, "?"))
    if only_a: print(f"  len A: {['0x%04x' % t for t in only_a]}")
    if only_b: print(f"  len B (v {lb}): {['0x%04x' % t for t in only_b]}")


def extract_ja(layers):
    return (find_key(layers, "tls.handshake.ja3"),
            find_key(layers, "tls.handshake.ja4"))


def main():
    ap = argparse.ArgumentParser(description="Porovnanie TLS ClientHello JSON exportov")
    ap.add_argument("files", nargs="+", help="Wireshark JSON súbory")
    ap.add_argument("--no-summary", action="store_true", help="bez zhrnutia každého súboru")
    args = ap.parse_args()

    parsed = []
    for path in args.files:
        layers_list = load_packets(path)
        ch = None
        used_layers = None
        for layers in layers_list:
            raw = get_tls_plaintext(layers)
            if raw is None:
                continue
            ch = parse_client_hello(raw)
            if ch:
                used_layers = layers
                break
        if ch is None:
            print(f"!! {path}: nenašiel som ClientHello", file=sys.stderr)
            sys.exit(1)
        parsed.append((path, ch, used_layers))

    if not args.no_summary:
        for path, ch, layers in parsed:
            summarize(ch, layers, path)

    if len(parsed) > 1:
        base = parsed[0]
        for path, ch, layers in parsed[1:]:
            compare(base[1], ch, base[0], path)
    else:
        print("\n(Poskytol si len jeden súbor - iba zhrnutie.)")


if __name__ == "__main__":
    main()