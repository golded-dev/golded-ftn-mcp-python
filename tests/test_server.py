"""The server calls the tools library and does not expose writes."""

import asyncio
import base64
import sys
from pathlib import Path

from golded_ftn_tools import create, write
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

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


def test_stdio_tools_against_offline_base(tmp_path: Path) -> None:
    create("msg", tmp_path)
    list(
        write(
            "msg",
            tmp_path,
            [b'{"from_name":"A","to_name":"B","subject":"S","body_text":"Text"}'],
        )
    )

    async def exercise() -> None:
        parameters = StdioServerParameters(
            command=sys.executable, args=["-m", "golded_ftn_mcp.server"]
        )
        async with stdio_client(parameters) as (reader, writer):
            async with ClientSession(reader, writer) as session:
                await session.initialize()
                registered = await session.list_tools()
                assert {tool.name for tool in registered.tools} == set(TOOLS)
                base: dict[str, object] = {"base": str(tmp_path), "format": "msg"}
                calls: list[tuple[str, dict[str, object]]] = [
                    ("catalog", {}),
                    ("heads", base),
                    ("read", {**base, "msgno": 1}),
                    ("export", base),
                    ("decode", {"data_base64": "VGV4dA==", "charset": "UTF-8"}),
                    ("repair", {"text": "plain"}),
                ]
                for name, arguments in calls:
                    result = await session.call_tool(name, arguments)
                    assert not result.is_error, (name, result)
                    assert result.content, name

    asyncio.run(exercise())
