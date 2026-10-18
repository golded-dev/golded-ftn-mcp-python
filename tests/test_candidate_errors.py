"""The tools 1.1 candidate keeps MCP's read-only error boundary."""

import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def test_stdio_operational_errors_do_not_expose_paths(tmp_path: Path) -> None:
    secret_path = str(tmp_path / "private-mailbox-sentinel")

    async def exercise() -> None:
        parameters = StdioServerParameters(
            command=sys.executable, args=["-m", "golded_ftn_mcp.server"]
        )
        async with stdio_client(parameters) as (reader, writer):
            async with ClientSession(reader, writer) as session:
                await session.initialize()
                for arguments in (
                    {"base": secret_path, "format": "msg", "msgno": 1},
                    {"base": secret_path, "format": "invalid", "msgno": 1},
                ):
                    result = await session.call_tool("read", arguments)
                    assert result.is_error
                    assert "private-mailbox-sentinel" not in str(result)
                    assert "Traceback" not in str(result)
                forbidden = await session.call_tool("node", {})
                assert forbidden.is_error

    asyncio.run(exercise())
