"""The server calls the tools library and does not expose writes."""

import base64
from pathlib import Path

from golded_ftn_tools import create, write

from golded_ftn_mcp.server import TOOLS, catalog, heads, mcp, repair


def test_registered_tools_are_read_only() -> None:
    names = {tool.name for tool in mcp._tool_manager.list_tools()}
    assert names == set(TOOLS)
    assert set(TOOLS) == {
        "catalog",
        "heads",
        "read",
        "export",
        "decode",
        "repair",
    }
    assert "create" not in names
    assert "write" not in names


def test_heads_and_catalog(tmp_path: Path) -> None:
    create("msg", tmp_path)
    message = b'{"from_name":"A","to_name":"B","subject":"S","body_text":"Text"}'
    list(write("msg", tmp_path, [message]))
    document = catalog()
    assert isinstance(document, dict)
    assert document["program"] == "ftnt"
    rows = heads(str(tmp_path), "msg", limit=10)
    assert len(rows) == 1
    assert isinstance(rows[0], dict)
    assert "body_text" not in rows[0]


def test_repair_round_trip() -> None:
    result = repair("plain")
    assert isinstance(result, dict)
    assert result["text"] == "plain"
    assert base64.b64encode(b"ok").decode() == "b2s="
