"""
MCP Client
-----------
Connects to the DSL File Reader MCP server via stdio transport.
Spawns mcp_server.py as a subprocess and communicates via JSON-RPC
using the official MCP Python SDK.
"""

import json
import os
import sys
from pathlib import Path
from typing import Tuple, List, Dict, Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# Resolve path to mcp_server.py relative to this file
_SERVER_SCRIPT = str(Path(__file__).parent.parent / "mcp_server.py")


async def _call_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Open a fresh MCP session, call a tool, and return the result.
    Each call spawns mcp_server.py as a subprocess over stdio transport.
    """
    server_params = StdioServerParameters(
        command=sys.executable,   # same Python interpreter
        args=[_SERVER_SCRIPT],
        env={**os.environ},       # inherit environment (for PYTHONPATH etc.)
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)

    # MCP tool results come back as a list of content blocks
    if not result.content:
        return {}

    raw = result.content[0].text
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}


async def read_file_via_mcp(file_path: str) -> Tuple[str, str]:
    """
    Use the MCP server to read a code file.

    Returns:
        (code, language)

    Raises:
        FileNotFoundError: if MCP server reports file not found
        RuntimeError: for other MCP errors
    """
    result = await _call_tool("read_code_file", {"file_path": file_path})

    if "error" in result:
        if "not found" in result["error"].lower():
            raise FileNotFoundError(result["error"])
        raise RuntimeError(result["error"])

    return result["code"], result["language"]


async def list_files_via_mcp(directory: str = ".") -> List[Dict]:
    """
    Use the MCP server to list all DSL code files in a directory.

    Returns:
        List of {"path": str, "language": str}
    """
    result = await _call_tool("list_code_files", {"directory": directory})

    if "error" in result:
        raise RuntimeError(result["error"])

    return result.get("files", [])
