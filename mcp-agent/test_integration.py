#!/usr/bin/env python3
"""
Test script for ModelScope Qwen integration with MCP
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.append('.')

async def test_integration():
    """Test the integration between ModelScope Qwen and MCP"""
    print("Testing ModelScope Qwen + MCP Integration")
    print("=" * 50)

    try:
        # Test agent import
        from agent.agent import AgentConfig, AdvertisingAgent
        print("✓ Agent module imported successfully")

        # Test config
        config = AgentConfig()
        print(f"✓ Config created: model={config.llm_model}, device={config.device}")

        # Test agent creation (lazy model loading)
        agent = AdvertisingAgent(config)
        print("✓ Agent created successfully")
        print(f"  Model loaded: {agent.model_loaded}")

        # Test MCP server
        from mcp_impl.server import create_mcp_server
        server = create_mcp_server()
        tools = await server.list_tools()
        tool_names = [tool.name for tool in tools]
        print(f"✓ MCP server created with tools: {tool_names}")

        # Test MCP client
        from mcp_impl.client import MCPClientFactory
        client = MCPClientFactory.create_client("stdio")
        print("✓ MCP client created successfully")

        print("\n" + "=" * 50)
        print("🎉 All components initialized successfully!")
        print("\nTo run the full system:")
        print("1. Start server: python main.py server --mode stdio")
        print("2. Start agent: python main.py agent")
        print("\nNote: Qwen3-30B-A3B will be downloaded on first use (~60GB)")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    success = asyncio.run(test_integration())
    sys.exit(0 if success else 1)