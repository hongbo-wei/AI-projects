"""
Advertising Agent Implementation
LLM-driven agent that calls advertising tools via MCP protocol.
"""

import os
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from dotenv import load_dotenv

from mcp_impl.client import MCPClientInterface, MCPClientFactory
from tools.ad_tools import BudgetCalculatorInput, EffectAnalyzerInput, ComplianceCheckerInput

load_dotenv()


@dataclass
class AgentConfig:
    """Configuration for the advertising agent."""
    llm_model: str = "qwen/Qwen3-30B-A3B"
    temperature: float = 0.7
    max_tokens: int = 1000
    device: str = "auto"  # auto, cpu, cuda, mps
    mcp_mode: str = "stdio"
    mcp_base_url: str = "http://127.0.0.1:8000"
    mcp_server_command: str = "python mcp_impl/server.py"


class AdvertisingAgent:
    """LLM-driven agent for advertising campaign management."""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.client: Optional[MCPClientInterface] = None
        
        # Lazy load ModelScope components
        try:
            from modelscope import AutoModelForCausalLM, AutoTokenizer
            from modelscope.pipelines import pipeline
            from modelscope.utils.constant import Tasks
            
            # Initialize ModelScope Qwen model
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.config.llm_model, 
                trust_remote_code=True
            )
            self.model = AutoModelForCausalLM.from_pretrained(
                self.config.llm_model,
                device_map=self.config.device,
                trust_remote_code=True
            )
            
            # Create pipeline for text generation with tool calling
            self.llm_pipeline = pipeline(
                Tasks.text_generation,
                model=self.model,
                tokenizer=self.tokenizer,
                device_map=self.config.device,
                model_revision="master"
            )
            self.model_loaded = True
        except Exception as e:
            print(f"Warning: Could not load ModelScope model: {e}")
            print("Make sure you have sufficient resources (RAM/VRAM) for Qwen3-30B-A3B")
            self.model_loaded = False

        # Agent's knowledge about available tools
        self.available_tools = {
            "budget_calculator": {
                "description": "Calculate optimal budget allocation across advertising platforms",
                "parameters": {
                    "budget": "Total advertising budget in USD (float)",
                    "platforms": "List of platforms to advertise on (list of strings)",
                    "region": "Target region (string, e.g., 'southeast_asia')",
                    "duration_days": "Campaign duration in days (int)"
                }
            },
            "effect_analyzer": {
                "description": "Analyze expected performance metrics for campaigns",
                "parameters": {
                    "platform": "Platform to analyze (string)",
                    "budget": "Budget allocated to this platform (float)",
                    "target_audience": "Target audience description (string)",
                    "campaign_type": "Type of campaign (string: awareness, conversion, etc.)"
                }
            },
            "compliance_checker": {
                "description": "Check advertising content compliance with regional regulations",
                "parameters": {
                    "platform": "Platform for compliance check (string)",
                    "region": "Target region (string)",
                    "ad_content": "Ad content to check (string)",
                    "target_audience": "Target audience description (string)"
                }
            }
            ,
            "var_image_generator": {
                "description": "Generate advertising images from text prompts (VAR)",
                "parameters": {
                    "prompt": "Text prompt describing the desired ad image (string)",
                    "width": "Image width in pixels (int, optional)",
                    "height": "Image height in pixels (int, optional)",
                    "style": "Optional visual style (string, optional)"
                }
            }
        }

    async def initialize_mcp_client(self):
        """Initialize MCP client based on configuration."""
        if self.config.mcp_mode == "stdio":
            self.client = MCPClientFactory.create_client(
                "stdio",
                server_command=self.config.mcp_server_command
            )
        elif self.config.mcp_mode in ["sse", "streamhttp"]:
            self.client = MCPClientFactory.create_client(
                self.config.mcp_mode,
                base_url=self.config.mcp_base_url
            )
        else:
            raise ValueError(f"Unsupported MCP mode: {self.config.mcp_mode}")

    async def call_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool via the client."""
        if not self.client:
            await self.initialize_mcp_client()

        request = {
            "tool": tool_name,
            "args": tool_args
        }

        response = await self.client.send_request(request)
        await self.client.handle_response(response)

        return response

    def create_tool_calling_prompt(self, user_query: str) -> str:
        """Create a prompt that instructs the LLM to call tools."""
        tools_description = "\n".join([
            f"- {name}: {info['description']}\n  Parameters: {json.dumps(info['parameters'], indent=2)}"
            for name, info in self.available_tools.items()
        ])

        prompt = f"""You are an expert advertising campaign manager. Help users plan and optimize their advertising campaigns.

Available tools:
{tools_description}

When a user asks about advertising, analyze their request and determine which tools to call. For each tool call, provide:
1. The tool name
2. The required parameters in JSON format

Example response format:
TOOL_CALL: budget_calculator
{{
  "budget": 100000,
  "platforms": ["tiktok", "facebook"],
  "region": "southeast_asia",
  "duration_days": 30
}}

If you need to call multiple tools, list them sequentially.

User query: {user_query}

Your analysis and tool calls:"""

        return prompt

    async def process_user_query(self, user_query: str) -> str:
        """Process user query using LLM and tool calling."""
        if not self.model_loaded:
            return "Error: LLM model not loaded. Please check your ModelScope installation and ensure you have sufficient resources for Qwen3-30B-A3B."
            
        # Create prompt for tool calling
        prompt = self.create_tool_calling_prompt(user_query)

        # Get LLM response using ModelScope
        messages = [{"role": "user", "content": prompt}]
        
        # Use pipeline for generation
        inputs = self.tokenizer.apply_chat_template(
            messages, 
            tokenize=False, 
            add_generation_prompt=True
        )
        
        # Generate response
        outputs = self.llm_pipeline(
            inputs,
            max_new_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            do_sample=True,
            top_p=0.9,
            return_full_text=False
        )
        
        llm_response = outputs[0]['generated_text']
        print(f"LLM Response: {llm_response}")

        # Parse tool calls from LLM response
        tool_calls = self.parse_tool_calls(llm_response)

        # Execute tool calls
        results = []
        for tool_call in tool_calls:
            try:
                result = await self.call_tool(tool_call["tool"], tool_call["args"])
                results.append(result)
            except Exception as e:
                results.append({"error": str(e), "tool": tool_call["tool"]})

        # Generate final response using results
        final_response = await self.generate_final_response(user_query, results)

        return final_response

    def parse_tool_calls(self, llm_response: str) -> List[Dict[str, Any]]:
        """Parse tool calls from LLM response."""
        tool_calls = []
        lines = llm_response.split('\n')

        current_tool = None
        current_args = None

        for line in lines:
            line = line.strip()
            if line.startswith('TOOL_CALL:'):
                if current_tool and current_args:
                    tool_calls.append({"tool": current_tool, "args": current_args})

                current_tool = line.split(':', 1)[1].strip()
                current_args = {}
            elif line.startswith('{') and current_tool:
                try:
                    current_args = json.loads(line)
                except json.JSONDecodeError:
                    continue

        # Add the last tool call
        if current_tool and current_args:
            tool_calls.append({"tool": current_tool, "args": current_args})

        return tool_calls

    async def generate_final_response(self, user_query: str, tool_results: List[Dict[str, Any]]) -> str:
        """Generate final response using tool results."""
        if not self.model_loaded:
            return f"Tool execution completed, but LLM not available for final response. Results: {json.dumps(tool_results, indent=2)}"
            
        results_summary = "\n".join([
            f"Tool {i+1} ({result.get('tool', 'unknown')}): {json.dumps(result, indent=2)}"
            for i, result in enumerate(tool_results)
        ])

        prompt = f"""Based on the user's query and the tool execution results, provide a comprehensive response about their advertising campaign.

User Query: {user_query}

Tool Results:
{results_summary}

Provide actionable recommendations and insights based on the results. Explain what the numbers mean and suggest next steps."""

        # Use ModelScope for final response generation
        messages = [{"role": "user", "content": prompt}]
        inputs = self.tokenizer.apply_chat_template(
            messages, 
            tokenize=False, 
            add_generation_prompt=True
        )
        
        outputs = self.llm_pipeline(
            inputs,
            max_new_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            do_sample=True,
            top_p=0.9,
            return_full_text=False
        )
        
        return outputs[0]['generated_text']

    async def run_interactive_session(self):
        """Run an interactive session with the user."""
        print("Advertising Campaign Assistant")
        print("Ask me about planning advertising campaigns (e.g., '10万美元投东南亚TikTok')")
        print("Type 'quit' to exit.")

        while True:
            user_input = input("\nYour query: ").strip()
            if user_input.lower() in ['quit', 'exit']:
                break

            try:
                response = await self.process_user_query(user_input)
                print(f"\nAssistant: {response}")
            except Exception as e:
                print(f"Error processing query: {e}")

    async def close(self):
        """Close the agent and cleanup resources."""
        if self.client and hasattr(self.client, 'close'):
            await self.client.close()


# Convenience functions for different use cases
async def create_advertising_agent_from_config(config_path: str = "config/config.yaml") -> AdvertisingAgent:
    """Create agent from YAML configuration."""
    import yaml

    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)

    config = AgentConfig(
        llm_model=config_data['llm']['model'],
        temperature=config_data['llm']['temperature'],
        max_tokens=config_data['llm']['max_tokens'],
        device=config_data['llm'].get('device', 'auto'),
        mcp_mode=config_data['mode'],
        mcp_base_url=f"http://{config_data['server']['host']}:{config_data['server']['port']}"
    )

    agent = AdvertisingAgent(config)
    await agent.initialize_mcp_client()

    return agent


async def demo_advertising_agent():
    """Demo function showing agent usage."""
    config = AgentConfig(mcp_mode="stdio")
    agent = AdvertisingAgent(config)
    await agent.initialize_mcp_client()

    # Example query
    query = "10万美元投东南亚TikTok广告，应该怎么分配预算？"
    response = await agent.process_user_query(query)
    print(f"Response: {response}")

    await agent.close()