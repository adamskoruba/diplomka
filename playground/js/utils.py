def load_js(path: str) -> str:
    full_path = "js/" + path
    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()