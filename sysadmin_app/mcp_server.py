"""
MCP Server – File Manager Tools (Etapa 1 ASO)

Expune tool-uri pentru lucrul cu un director administrat.
Cerintele minime (Etapa 1):
  • list_directory(dir_path: str) -> list[str]
  • get_file_content(file_path: str) -> str

Note:
- Serverul limiteaza accesul la o radacina MANAGED_ROOT (implicit ./managed_dir),
  evitand traversarea path-urilor in afara acestei radacini.
- Parametrii sunt adnotati si fiecare tool are docstring explicit, conform cerintei.

Rulare (stdio):
    python mcp_server.py

Variabile de mediu optionale:
    MANAGED_ROOT  – calea absoluta catre directorul administrat (default: ./managed_dir)

Bonus tools (opțional, utile la testat):
  • stat_path(path: str) -> dict  – informatii despre fisier/director
  • search_files(pattern: str, dir_path: str = ".") -> list[str] – cauta recursiv
"""
from __future__ import annotations
import os
import fnmatch
from dataclasses import dataclass
from typing import List, Dict, Any

try:
    from fastmcp import FastMCP
    from fastmcp.tools import tool

except Exception as e:
    import traceback
    traceback.print_exc()
    raise SystemExit("Import fastmcp a esuat (vezi traceback-ul de mai sus).") from e


# --------------------------- Config si utilitare ---------------------------

def _abs(p: str) -> str:
    return os.path.abspath(os.path.expanduser(p))

MANAGED_ROOT = _abs(os.environ.get("MANAGED_ROOT", "./managed_dir"))
os.makedirs(MANAGED_ROOT, exist_ok=True)


def _ensure_under_root(path: str) -> str:
    """Rezolva calea si se asigura ca este sub MANAGED_ROOT. Ridica ValueError altfel."""
    abs_path = _abs(os.path.join(MANAGED_ROOT, path))
    root = _abs(MANAGED_ROOT)
    if not abs_path.startswith(root + os.sep) and abs_path != root:
        raise ValueError("Acces interzis in afara MANAGED_ROOT")
    return abs_path


app = FastMCP("FileManager")


# ------------------------------ Tool-uri MCP ------------------------------

@app.tool
def list_directory(dir_path: str = ".") -> List[str]:
    """Returneaza lista fisierelor si subdirectoarelor din calea data,
    relativa la MANAGED_ROOT.

    Args:
        dir_path: Calea relativa (ex: ".", "subdir"). Valori speciale: "." pentru radacina.

    Returns:
        Lista de nume (fisier/subdirector) sortata alfabetic.

    Raises:
        ValueError: daca dir_path iese in afara MANAGED_ROOT sau nu este director.
    """
    target = _ensure_under_root(dir_path)
    if not os.path.isdir(target):
        raise ValueError("Calea specificata nu este un director sau nu exista.")
    return sorted(os.listdir(target))


@app.tool
def get_file_content(file_path: str) -> str:
    """Citeste si returneaza continutul unui fisier text din MANAGED_ROOT.

    Args:
        file_path: Cale relativa catre fisierul text (ex: "notes.txt", "sub/README.md").

    Returns:
        Continutul fisierului ca string.

    Raises:
        ValueError: daca path-ul iese in afara MANAGED_ROOT, nu exista sau e director.
        UnicodeDecodeError: daca fisierul nu este text (se poate prinde la nivel de agent).
    """
    target = _ensure_under_root(file_path)
    if not os.path.exists(target):
        raise ValueError("Fisier inexistent.")
    if os.path.isdir(target):
        raise ValueError("Calea indicata este un director, nu un fisier.")
    with open(target, "r", encoding="utf-8") as f:
        return f.read()


# ------------------------------- Bonus tools ------------------------------

@app.tool
def stat_path(path: str = ".") -> Dict[str, Any]:
    """Returneaza informatii despre o cale (fisier sau director) din MANAGED_ROOT.

    Args:
        path: Cale relativa din MANAGED_ROOT.

    Returns:
        Dict cu chei: exists, is_dir, size, abs_path, mtime, ctime, atime.
    """
    target = _ensure_under_root(path)
    info: Dict[str, Any] = {
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
    """Cauta recursiv fisiere/directoare care se potrivesc unui pattern (glob) sub dir_path.

    Args:
        pattern: Ex. "*.txt", "README*", "data_??.csv".
        dir_path: Director de start (relativ la MANAGED_ROOT), default ".".

    Returns:
        Lista de cai relative (din MANAGED_ROOT) care se potrivesc.
    """
    start = _ensure_under_root(dir_path)
    results: List[str] = []
    for root, dirs, files in os.walk(start):
        rel_root = os.path.relpath(root, MANAGED_ROOT)
        # Directoare
        for d in dirs:
            rel = os.path.normpath(os.path.join(rel_root, d))
            if fnmatch.fnmatch(d, pattern):
                results.append(rel)
        # Fisiere
        for f in files:
            rel = os.path.normpath(os.path.join(rel_root, f))
            if fnmatch.fnmatch(f, pattern):
                results.append(rel)
    results = sorted({r if r != "." else "" for r in results})
    return results


# ------------------------------- Entry point ------------------------------

if __name__ == "__main__":
    # Rulare in modul stdio (Etapa 1). Daca intampini probleme, inlocuieste cu app.run().
    try:
        app.run_stdio()
    except AttributeError:
        # Fallback pentru versiuni FastMCP mai vechi/noi
        app.run()
