"""
MCP Server Implementation using FastMCP
Simplified implementation using FastMCP for all communication modes.
"""

from mcp.server.fastmcp import FastMCP
from tools.ad_tools import TOOL_EXECUTORS


def create_mcp_server() -> FastMCP:
    """Create and configure FastMCP server with advertising tools."""

    # Create FastMCP server
    server = FastMCP("advertising-agent")

    # Add tools using decorators
    @server.tool()
    def budget_calculator(budget: float, platforms: list[str], region: str, duration_days: int):
        """Calculate optimal budget allocation for advertising campaigns across multiple platforms."""
        return TOOL_EXECUTORS["budget_calculator"](budget=budget, platforms=platforms, region=region, duration_days=duration_days)

    @server.tool()
    def effect_analyzer(platform: str, budget: float, target_audience: str, campaign_type: str):
        """Analyze expected performance metrics for advertising campaigns."""
        return TOOL_EXECUTORS["effect_analyzer"](platform=platform, budget=budget, target_audience=target_audience, campaign_type=campaign_type)

    @server.tool()
    def compliance_checker(platform: str, region: str, ad_content: str, target_audience: str):
        """Check advertising content compliance with regional regulations."""
        return TOOL_EXECUTORS["compliance_checker"](platform=platform, region=region, ad_content=ad_content, target_audience=target_audience)

    return server


# Convenience functions for different modes
async def run_stdio_server():
    """Run MCP server in stdio mode."""
    server = create_mcp_server()
    await server.run_stdio_async()


async def run_sse_server(host: str = "127.0.0.1", port: int = 8000):
    """Run MCP server in SSE mode."""
    server = create_mcp_server()
    print(f"SSE server running on http://{host}:{port}")
    await server.run_sse_async(host=host, port=port)


async def run_streamable_http_server(host: str = "127.0.0.1", port: int = 8000):
    """Run MCP server in streamable HTTP mode."""
    server = create_mcp_server()
    print(f"Streamable HTTP server running on http://{host}:{port}")
    await server.run_streamable_http_async(host=host, port=port)

import asyncio
import json
import sys
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
import uvicorn

from tools.ad_tools import AD_TOOLS, TOOL_EXECUTORS


class MCPServerInterface(ABC):
    """Abstract interface for MCP servers."""

    @abstractmethod
    async def send_response(self, response: Dict[str, Any]) -> None:
        """Send response to client."""
        pass

    @abstractmethod
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming request."""
        pass


class StdioMCPServer(MCPServerInterface):
    """MCP Server using stdio communication."""

    def __init__(self):
        self.tools = {tool.name: tool for tool in AD_TOOLS}
        self.executors = TOOL_EXECUTORS

    async def send_response(self, response: Dict[str, Any]) -> None:
        """Send response via stdout."""
        response_json = json.dumps(response, ensure_ascii=False)
        print(response_json, flush=True)

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool execution request."""
        try:
            tool_name = request.get("tool")
            tool_args = request.get("args", {})

            if tool_name not in self.executors:
                return {
                    "error": f"Tool '{tool_name}' not found",
                    "available_tools": list(self.executors.keys())
                }

            # Execute tool using the executor function
            result = self.executors[tool_name](**tool_args)

            return {
                "tool": tool_name,
                "result": result.dict() if hasattr(result, 'dict') else result,
                "status": "success"
            }

        except Exception as e:
            return {
                "error": str(e),
                "status": "error"
            }

    async def run(self):
        """Run the stdio server."""
        try:
            for line in sys.stdin:
                request = json.loads(line.strip())
                response = await self.handle_request(request)
                await self.send_response(response)
        except KeyboardInterrupt:
            pass


class SSEMCPServer(MCPServerInterface):
    """MCP Server using Server-Sent Events."""

    def __init__(self):
        self.tools = {tool.name: tool for tool in AD_TOOLS}
        self.executors = TOOL_EXECUTORS
        self.app = FastAPI()
        self.setup_routes()

    def setup_routes(self):
        @self.app.get("/sse")
        async def sse_endpoint():
            async def event_generator():
                while True:
                    # Keep connection alive
                    yield {"event": "ping", "data": "keep-alive"}
                    await asyncio.sleep(30)

            return EventSourceResponse(event_generator())

        @self.app.post("/execute")
        async def execute_tool(request: Request):
            data = await request.json()
            response = await self.handle_request(data)
            return response

    async def send_response(self, response: Dict[str, Any]) -> None:
        """Send response via SSE (not directly used in this implementation)."""
        pass

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool execution request."""
        try:
            tool_name = request.get("tool")
            tool_args = request.get("args", {})

            if tool_name not in self.executors:
                return {
                    "error": f"Tool '{tool_name}' not found",
                    "available_tools": list(self.executors.keys())
                }

            # Execute tool using the executor function
            result = self.executors[tool_name](**tool_args)

            return {
                "tool": tool_name,
                "result": result.dict() if hasattr(result, 'dict') else result,
                "status": "success"
            }

        except Exception as e:
            return {
                "error": str(e),
                "status": "error"
            }

    async def run(self, host: str = "127.0.0.1", port: int = 8000):
        """Run the SSE server."""
        config = uvicorn.Config(self.app, host=host, port=port)
        server = uvicorn.Server(config)
        await server.serve()


class StreamableHTTPMCPServer(MCPServerInterface):
    """MCP Server using streamable HTTP."""

    def __init__(self):
        self.tools = {tool.name: tool for tool in AD_TOOLS}
        self.executors = TOOL_EXECUTORS
        self.app = FastAPI()
        self.setup_routes()

    def setup_routes(self):
        @self.app.post("/stream")
        async def stream_tool_execution(request: Request):
            data = await request.json()
            response = await self.handle_request(data)

            async def generate():
                # Stream the response
                response_json = json.dumps(response, ensure_ascii=False)
                yield f"data: {response_json}\n\n"
                yield "data: [DONE]\n\n"

            return StreamingResponse(
                generate(),
                media_type="text/plain"
            )

    async def send_response(self, response: Dict[str, Any]) -> None:
        """Send response via HTTP streaming (not directly used)."""
        pass

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool execution request."""
        try:
            tool_name = request.get("tool")
            tool_args = request.get("args", {})

            if tool_name not in self.executors:
                return {
                    "error": f"Tool '{tool_name}' not found",
                    "available_tools": list(self.executors.keys())
                }

            # Execute tool using the executor function
            result = self.executors[tool_name](**tool_args)

            return {
                "tool": tool_name,
                "result": result.dict() if hasattr(result, 'dict') else result,
                "status": "success"
            }

        except Exception as e:
            return {
                "error": str(e),
                "status": "error"
            }

    async def run(self, host: str = "127.0.0.1", port: int = 8000):
        """Run the streamable HTTP server."""
        config = uvicorn.Config(self.app, host=host, port=port)
        server = uvicorn.Server(config)
        await server.serve()


class MCPServerFactory:
    """Factory for creating MCP servers based on mode."""

    @staticmethod
    def create_server(mode: str) -> MCPServerInterface:
        """Create server instance based on communication mode."""
        if mode == "stdio":
            return StdioMCPServer()
        elif mode == "sse":
            return SSEMCPServer()
        elif mode == "streamhttp":
            return StreamableHTTPMCPServer()
        else:
            raise ValueError(f"Unsupported mode: {mode}")


# Unified interface functions
async def send_request(server: MCPServerInterface, request: Dict[str, Any]) -> Dict[str, Any]:
    """Unified function to send request to server."""
    return await server.handle_request(request)


async def handle_response(response: Dict[str, Any]) -> None:
    """Unified function to handle server response."""
    if "error" in response:
        print(f"Error: {response['error']}")
    else:
        print(f"Success: {response}")