"""Stdio MCP server. It calls golded-ftn-tools and does not open formats itself."""

from __future__ import annotations

import base64
from collections.abc import Iterator
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import cast

from golded_ftn_tools import catalog as catalog_base
from golded_ftn_tools import decode as decode_base
from golded_ftn_tools import export as export_base
from golded_ftn_tools import heads as heads_base
from golded_ftn_tools import read as read_base
from golded_ftn_tools import repair as repair_base
from mcp.server.mcpserver import MCPServer

TOOLS = ("catalog", "heads", "read", "export", "decode", "repair")

mcp = MCPServer("golded-ftn")


def _plain(value: object) -> object:
    if isinstance(value, datetime):
        return value.isoformat()
    if is_dataclass(value) and not isinstance(value, type):
        return {key: _plain(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    return value


def _rows(stream: Iterator[dict[str, object]]) -> list[object]:
    return cast(list[object], _plain(list(stream)))


@mcp.tool()
def catalog() -> object:
    """Describe the installed ftnt binary. No base is opened."""
    return _plain(catalog_base())


@mcp.tool()
def heads(
    base: str,
    format: str,
    board: int | None = None,
    limit: int = 100,
    after: int | None = None,
) -> list[object]:
    """Index a base without message bodies. limit 0 reads the whole base."""
    stream = heads_base(format, Path(base), board=board, limit=limit, after=after)
    return _rows(iter(stream))


@mcp.tool()
def read(
    base: str,
    format: str,
    msgno: int,
    board: int | None = None,
    body: bool = False,
) -> object:
    """Read one message envelope, or the body text when body is true."""
    return _plain(
        read_base(format, Path(base), msgno, board=board, body=body, revision=False)
    )


@mcp.tool()
def export(
    base: str,
    format: str,
    board: int | None = None,
    limit: int = 20,
) -> list[object]:
    """Export message envelopes. The default limit is 20. 0 means the whole base."""
    stream = export_base(format, Path(base), board=board)
    rows: list[dict[str, object]] = []
    for envelope in stream:
        if limit and len(rows) >= limit:
            break
        rows.append(envelope)
    return _rows(iter(rows))


@mcp.tool()
def decode(data_base64: str, charset: str) -> str:
    """Decode one buffer. data_base64 is the raw bytes, not Unicode text."""
    return decode_base(base64.b64decode(data_base64), charset)


@mcp.tool()
def repair(text: str, charset: str | None = None) -> object:
    """Repair UTF-8 text and return the repair_result object."""
    return _plain(repair_base(text.encode("utf-8"), charset=charset, as_json=True))


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
