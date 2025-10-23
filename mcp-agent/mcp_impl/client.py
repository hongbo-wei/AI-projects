"""
MCP Client Implementation
Supports stdio, SSE, and streamable HTTP communication modes.
"""

import asyncio
import json
import sys
import subprocess
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

import httpx


class MCPClientInterface(ABC):
    """Abstract interface for MCP clients."""

    @abstractmethod
    async def send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send request to server."""
        pass

    @abstractmethod
    async def handle_response(self, response: Dict[str, Any]) -> None:
        """Handle server response."""
        pass


class StdioMCPClient(MCPClientInterface):
    """MCP Client using stdio communication."""

    def __init__(self, server_command: str):
        self.server_command = server_command
        self.process: Optional[subprocess.Popen] = None

    async def start_server(self):
        """Start the stdio server process."""
        # Accept either a list of args or a string command. Prefer list for safety.
        cmd = self.server_command
        if isinstance(cmd, str):
            # Default to using main.py entrypoint if a simple string was provided
            # Split into args for Popen
            import shlex
            cmd = shlex.split(cmd)

        self.process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

    async def send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send request via stdin and receive response via stdout."""
        if not self.process:
            await self.start_server()

        request_json = json.dumps(request, ensure_ascii=False)
        self.process.stdin.write(request_json + "\n")
        self.process.stdin.flush()

        response_line = self.process.stdout.readline().strip()
        response = json.loads(response_line)

        return response

    async def handle_response(self, response: Dict[str, Any]) -> None:
        """Handle server response."""
        if "error" in response:
            print(f"Client received error: {response['error']}")
        else:
            print(f"Client received result: {response}")


class SSEMCPClient(MCPClientInterface):
    """MCP Client using Server-Sent Events."""

    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send request via HTTP POST."""
        url = f"{self.base_url}/execute"
        response = await self.client.post(url, json=request)
        response.raise_for_status()
        return response.json()

    async def handle_response(self, response: Dict[str, Any]) -> None:
        """Handle server response."""
        if "error" in response:
            print(f"SSE Client received error: {response['error']}")
        else:
            print(f"SSE Client received result: {response}")

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


class StreamableHTTPMCPClient(MCPClientInterface):
    """MCP Client using streamable HTTP."""

    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send request via streaming HTTP POST."""
        url = f"{self.base_url}/stream"
        response = await self.client.post(url, json=request)
        response.raise_for_status()

        # Read streaming response
        full_response = ""
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                data = line[6:]  # Remove "data: " prefix
                if data == "[DONE]":
                    break
                full_response += data

        return json.loads(full_response)

    async def handle_response(self, response: Dict[str, Any]) -> None:
        """Handle server response."""
        if "error" in response:
            print(f"Stream HTTP Client received error: {response['error']}")
        else:
            print(f"Stream HTTP Client received result: {response}")

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


class MCPClientFactory:
    """Factory for creating MCP clients based on mode."""

    @staticmethod
    def create_client(mode: str, **kwargs) -> MCPClientInterface:
        """Create client instance based on communication mode."""
        if mode == "stdio":
            server_command = kwargs.get("server_command", "python mcp_impl/server.py")
            return StdioMCPClient(server_command)
        elif mode == "sse":
            base_url = kwargs.get("base_url", "http://127.0.0.1:8000")
            return SSEMCPClient(base_url)
        elif mode == "streamhttp":
            base_url = kwargs.get("base_url", "http://127.0.0.1:8000")
            return StreamableHTTPMCPClient(base_url)
        else:
            raise ValueError(f"Unsupported mode: {mode}")


# Unified interface functions
async def send_request(client: MCPClientInterface, request: Dict[str, Any]) -> Dict[str, Any]:
    """Unified function to send request via client."""
    return await client.send_request(request)


async def handle_response(client: MCPClientInterface, response: Dict[str, Any]) -> None:
    """Unified function to handle response via client."""
    await client.handle_response(response)