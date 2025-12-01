from __future__ import annotations
import os, pathlib
os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.adk.agents.llm_agent import LlmAgent

# ---------------------------
# Model LLM (Ollama)
# ---------------------------

OLLAMA_BASE = os.environ.get("OLLAMA_API_BASE", "http://localhost:11434")
model = LiteLlm(model="ollama_chat/llama3.2:3b", api_base=OLLAMA_BASE)

# ---------------------------
# MCP SERVER – HTTP Connection
# ---------------------------

# Pentru docker-compose, serverul MCP va avea serviciul: mcp-server
MCP_HTTP_URL = os.environ.get("MCP_SERVER_URL", "http://mcp-server:9000/mcp")

mcp_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=MCP_HTTP_URL
    )
)

# ---------------------------
# Agent Definition
# ---------------------------

sysadmin_agent = LlmAgent(
    model=model,
    name="sysadmin_sysfs_agent",
    description=(
        "AI system administrator focused on local filesystem management within MANAGED_ROOT. "
        "Capabilities: discover and call MCP tools; validate paths; provide safe and accurate summaries."
    ),
    instruction=(
        "You are a sysadmin agent responsible for managing MANAGED_ROOT.\n"
        "\n"
        "You MUST use the MCP tools exposed by the FileManager server:\n"
        "- list_directory(dir_path: str) -> list[str]\n"
        "- get_file_content(file_path: str) -> str\n"
        "- stat_path(path: str) -> dict\n"
        "- search_files(pattern: str, dir_path: str = '.') -> list[str]\n"
        "\n"
        "Rules:\n"
        "- Always treat user paths as RELATIVE to MANAGED_ROOT.\n"
        "- ALWAYS prefer calling the appropriate tool instead of reasoning.\n"
        "- Never invent file contents, directory listings, or stats.\n"
        "- If a tool error happens (file missing, not a directory, etc.), explain the exact issue.\n"
        "- Use list_directory for browsing, get_file_content for reading, stat_path for metadata, and search_files for wildcard lookups.\n"
        "- Keep answers short, precise, and based ONLY on tool outputs.\n"
    ),
    tools=[mcp_toolset],
)

root_agent = sysadmin_agent
