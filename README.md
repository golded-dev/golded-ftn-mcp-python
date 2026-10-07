# golded-ftn-mcp

A local stdio MCP server for FTN message bases. It imports `golded-ftn-tools` and does not open JAM, Squish, Hudson or MSG files itself.

The tools are `catalog`, `heads`, `read`, `export`, `decode` and `repair`. `create` and `write` are not exposed. `export` defaults to 20 messages.

Run it over stdio:

```
golded-ftn-mcp
```

Keep message bases offline. Close GoldED before a client calls a tool. Do not expose this server on the network. The bases can hold private netmail.

Version 1.0.0. Publication follows `golded-ftn-tools` 1.0.0.
