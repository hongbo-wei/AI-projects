"""
Main entry point for the Advertising Agent MCP project.
Supports running servers and agents in different modes.
"""

import asyncio
import sys
import argparse
from pathlib import Path

from agent.agent import create_advertising_agent_from_config, demo_advertising_agent
from mcp_impl.server import run_stdio_server, run_sse_server, run_streamable_http_server


async def run_server(mode: str, config_path: str = "config/config.yaml"):
    """Run MCP server in specified mode."""
    import yaml

    # Load config
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    host = config['server']['host']
    port = config['server']['port']

    if mode == "stdio":
        await run_stdio_server()
    elif mode == "sse":
        await run_sse_server(host=host, port=port)
    elif mode == "streamhttp":
        await run_streamable_http_server(host=host, port=port)
    else:
        raise ValueError(f"Unsupported mode: {mode}")


async def run_agent(config_path: str = "config/config.yaml"):
    """Run the advertising agent interactively."""
    agent = await create_advertising_agent_from_config(config_path)

    try:
        await agent.run_interactive_session()
    finally:
        await agent.close()


async def run_demo():
    """Run a demo of the advertising agent."""
    print("Running Advertising Agent Demo...")
    await demo_advertising_agent()


def main():
    parser = argparse.ArgumentParser(description="Advertising Agent MCP Project")
    parser.add_argument(
        "command",
        choices=["server", "agent", "demo"],
        help="Command to run: server, agent, or demo"
    )
    parser.add_argument(
        "--mode",
        choices=["stdio", "sse", "streamhttp"],
        default="stdio",
        help="Communication mode for server (default: stdio)"
    )
    parser.add_argument(
        "--config",
        default="config/config.yaml",
        help="Path to configuration file (default: config/config.yaml)"
    )

    args = parser.parse_args()

    # Ensure config file exists
    if not Path(args.config).exists():
        print(f"Error: Configuration file '{args.config}' not found.")
        sys.exit(1)

    if args.command == "server":
        asyncio.run(run_server(args.mode, args.config))
    elif args.command == "agent":
        asyncio.run(run_agent(args.config))
    elif args.command == "demo":
        asyncio.run(run_demo())


if __name__ == "__main__":
    main()