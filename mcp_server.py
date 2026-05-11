"""
MCP Server — DSL File Reader
-----------------------------
A real MCP server using the official Python MCP SDK (FastMCP).
Runs as a separate process and communicates via JSON-RPC over stdio transport.

Start manually:   python mcp_server.py
(The MCP client in tools/mcp_client.py spawns this automatically as a subprocess)
"""

from mcp.server.fastmcp import FastMCP
from pathlib import Path
from typing import Dict, Any

mcp = FastMCP("dsl-file-reader")

_EXTENSION_LANGUAGE_MAP: Dict[str, str] = {
    ".v":    "verilog",
    ".sv":   "systemverilog",
    ".vh":   "verilog",
    ".svh":  "systemverilog",
    ".sql":  "sql",
    ".cu":   "cuda",
    ".cuh":  "cuda",
    ".vhd":  "vhdl",
    ".vhdl": "vhdl",
    ".asm":  "assembly",
    ".s":    "assembly",
    ".m":    "matlab",
}


@mcp.tool()
def read_code_file(file_path: str) -> Dict[str, Any]:
    """
    Read a domain-specific language code file from the filesystem.
    Automatically detects the language from the file extension.

    Args:
        file_path: Absolute or relative path to the code file.

    Returns:
        Dict with keys: code (str), language (str), file_path (str)
        On error: Dict with key: error (str)
    """
    path = Path(file_path)

    if not path.exists():
        return {"error": f"File not found: {file_path}"}
    if not path.is_file():
        return {"error": f"Path is not a file: {file_path}"}

    extension = path.suffix.lower()
    language  = _EXTENSION_LANGUAGE_MAP.get(extension, "unknown")

    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            code = f.read()
    except OSError as e:
        return {"error": f"Could not read file: {e}"}

    return {
        "code":      code,
        "language":  language,
        "file_path": str(path.resolve()),
        "lines":     len(code.splitlines()),
        "size_bytes": path.stat().st_size,
    }


@mcp.tool()
def list_code_files(directory: str = ".") -> Dict[str, Any]:
    """
    List all supported DSL code files in a directory (recursive).

    Args:
        directory: Path to the directory to scan.

    Returns:
        Dict with key: files (list of {path, language})
        On error: Dict with key: error (str)
    """
    dir_path = Path(directory)

    if not dir_path.exists():
        return {"error": f"Directory not found: {directory}"}
    if not dir_path.is_dir():
        return {"error": f"Path is not a directory: {directory}"}

    files = []
    for ext, lang in _EXTENSION_LANGUAGE_MAP.items():
        for f in dir_path.rglob(f"*{ext}"):
            files.append({"path": str(f), "language": lang})

    return {"files": sorted(files, key=lambda x: x["path"]), "count": len(files)}


if __name__ == "__main__":
    mcp.run(transport="stdio")
