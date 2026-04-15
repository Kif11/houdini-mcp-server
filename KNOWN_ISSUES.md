# Houdini MCP Server - Known Issues

## Asyncio Incompatibility

**Problem:** Houdini 20.5 uses a custom asyncio event loop (`haio.py`) that doesn't fully implement the standard asyncio API. Specifically:

- `loop.get_task_factory()` raises `NotImplementedError`
- The custom event loop has bugs (e.g., `closing_agens` typo instead of `closing_asyncgens`)
- The MCP SDK uses `anyio` which requires a standard-compliant asyncio implementation

**Impact:** The MCP server cannot run directly inside hython/Houdini's Python environment.

## Workarounds

###  Option 1: HTTP Bridge (Recommended)

Run two processes:
1. MCP Server (standard Python) - Communicates with OpenCode via stdio
2. Houdini HTTP Service - Runs inside Houdini, executes commands

### Option 2: Wait for Houdini Fix

SideFX may fix the asyncio implementation in future versions.

### Option 3: Use Alternative Transport

Instead of stdio, use HTTP/SSE transport for MCP (requires different setup).

## Current Status

This package is **not yet functional** due to the asyncio incompatibility. We're working on implementing Option 1 (HTTP Bridge).
