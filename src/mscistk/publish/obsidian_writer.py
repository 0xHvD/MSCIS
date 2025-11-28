import os, pathlib, datetime, json
def write_obsidian(root, subpath, filename, content):
    path = pathlib.Path(root)/subpath
    path.mkdir(parents=True, exist_ok=True)
    fp = path/filename
    fp.write_text(content, encoding="utf-8")
    return str(fp)
