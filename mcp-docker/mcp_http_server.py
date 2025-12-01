from __future__ import annotations
import os, fnmatch
from typing import List, Dict, Any

from fastmcp import FastMCP
from fastmcp.tools import tool

# === MANAGED ROOT ===
def _abs(p: str) -> str:
    return os.path.abspath(os.path.expanduser(p))

MANAGED_ROOT = _abs(os.environ.get("MANAGED_ROOT", "./managed_dir"))
os.makedirs(MANAGED_ROOT, exist_ok=True)

def _ensure(path: str) -> str:
    full = _abs(os.path.join(MANAGED_ROOT, path))
    root = _abs(MANAGED_ROOT)
    if not (full.startswith(root + os.sep) or full == root):
        raise ValueError("Access outside MANAGED_ROOT not allowed.")
    return full

app = FastMCP("FileManager")

# === Tools ===

@app.tool
def list_directory(dir_path: str = ".") -> List[str]:
    target = _ensure(dir_path)
    if not os.path.isdir(target):
        raise ValueError("Not a directory.")
    return sorted(os.listdir(target))

@app.tool
def get_file_content(file_path: str) -> str:
    target = _ensure(file_path)
    if not os.path.exists(target):
        raise ValueError("File not found.")
    if os.path.isdir(target):
        raise ValueError("Path is directory.")
    with open(target, "r", encoding="utf-8") as f:
        return f.read()

@app.tool
def stat_path(path: str = ".") -> Dict[str, Any]:
    target = _ensure(path)
    info = {
        "abs_path": target,
        "exists": os.path.exists(target),
        "is_dir": os.path.isdir(target),
        "size": None,
        "mtime": None,
        "ctime": None,
        "atime": None,
    }
    if info["exists"]:
        st = os.stat(target)
        info.update({
            "size": st.st_size,
            "mtime": st.st_mtime,
            "ctime": st.st_ctime,
            "atime": st.st_atime,
        })
    return info

@app.tool
def search_files(pattern: str, dir_path: str = ".") -> List[str]:
    start = _ensure(dir_path)
    results = []
    for root, dirs, files in os.walk(start):
        rel = os.path.relpath(root, MANAGED_ROOT)
        for d in dirs:
            if fnmatch.fnmatch(d, pattern):
                results.append(os.path.join(rel, d))
        for f in files:
            if fnmatch.fnmatch(f, pattern):
                results.append(os.path.join(rel, f))
    return sorted(results)

# === HTTP Entry Point ===
if __name__ == "__main__":
    print("MCP HTTP server running on http://0.0.0.0:9000")
    app.run(transport="http", host="0.0.0.0", port=9000)

