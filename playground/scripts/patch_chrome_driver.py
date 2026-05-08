import io
import re

FILE_PATH = r"C:\Users\adams\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"

def patch_exe(file_path):
    print('patchujem')
    with io.open(file_path, "r+b") as fh:
        content = fh.read()
        # match_injected_codeblock = re.search(rb"{window.*;}", content)
        match_injected_codeblock = re.search(rb"\{window\.cdc.*?;\}", content)
        if match_injected_codeblock:
            target_bytes = match_injected_codeblock[0]
            print(target_bytes)
            new_target_bytes = (
                b'{console.log(console.trace("patch"))}'.ljust(
                    len(target_bytes), b" "
                )
            )
            new_content = content.replace(target_bytes, new_target_bytes)
            if new_content == content:
                print(
                    "something went wrong patching the driver binary. could not find injection code block"
                )
            else:
                print(
                    "found block:\n%s\nreplacing with:\n%s"
                    % (target_bytes, new_target_bytes)
                )
            fh.seek(0)
            fh.write(new_content)

patch_exe(FILE_PATH)