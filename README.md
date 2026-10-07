# golded-ftn-mcp

A local stdio MCP server for FTN message bases. It imports `golded-ftn-tools` and does not open JAM, Squish, Hudson or MSG files itself.

The tools are `catalog`, `heads`, `read`, `export`, `decode` and `repair`. `create` and `write` are not exposed. `export` defaults to 20 messages.

Install version 1.0.1 from PyPI with Python 3.12+, then run it over stdio:

```sh
python -m pip install golded-ftn-mcp==1.0.1
golded-ftn-mcp
```

Keep message bases offline. Close GoldED before a client calls a tool. Do not expose this server on the network. The bases can hold private netmail.

Version 1.0.1 is published on PyPI and requires `golded-ftn-tools>=1.0.1,<2`.
Linux and macOS CI passed with Python 3.12 and 3.14 using public PyPI
dependencies. Windows is unsupported.

Release archive SHA-256 values are in `RELEASE-SHA256.txt`.
