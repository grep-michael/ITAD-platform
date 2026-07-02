

import base64, gzip, pathlib



if __name__ == "__main__":
    FILES = {"mvcli": "mvcli", "libmvraid.so": "libmvraid.so"}  # name_on_disk: source_path

    with open("_mvcli_data.py", "w") as out:
        out.write("# Auto-generated. Do not edit by hand.\nBLOBS = {\n")
        for name, path in FILES.items():
            packed = base64.b64encode(gzip.compress(pathlib.Path(path).read_bytes())).decode()
            out.write(f"    {name!r}: {packed!r},\n")
        out.write("}\n")