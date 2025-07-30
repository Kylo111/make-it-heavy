#!/usr/bin/env python3
"""
Debug script for synthesis issues with DeepSeek
"""

import json
import yaml
import sys
from agent import UniversalAgent
from orchestrator import TaskOrchestrator

def debug_synthesis():
    """Debug the synthesis process in detail"""
    print("🔍 Debugging Synthesis Process")
    print("=" * 60)
    
    try:
        # Initialize orchestrator
        config_path = 'config_deepseek.yaml'
        print(f"Loading configuration from: {config_path}")
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            print(f"Provider type: {config.get('provider', {}).get('type', 'unknown')}")
            
            if 'deepseek' in config:
                print(f"DeepSeek model: {config['deepseek'].get('model', 'unknown')}")
        
        # Create synthesis agent directly
        print("\nInitializing synthesis agent...")
        synthesis_agent = UniversalAgent(config_path=config_path, silent=False)
        
        print(f"Agent provider type: {synthesis_agent.provider_type}")
        print(f"Initial tools count: {len(synthesis_agent.tools)}")
        
        # Print tool names
        tool_names = [tool.get('function', {}).get('name', 'unknown') for tool in synthesis_agent.tools]
        print(f"Tool names: {tool_names}")
        
        # Remove ALL tools to simulate the issue
        print("\nRemoving ALL tools...")
        original_tools = synthesis_agent.tools.copy()
        synthesis_agent.tools = []
        synthesis_agent.tool_mapping = {}
        
        print(f"Tools after removal: {len(synthesis_agent.tools)}")
        if len(synthesis_agent.tools) == 0:
            print("WARNING: Tools array is empty!")
        
        # Test API call
        print("\nTesting API call with current tools configuration...")
        test_messages = [{"role": "user", "content": "Hello, please synthesize this information."}]
        
        # Debug the call_llm method
        print("Preparing API parameters...")
        api_params = {
            "model": synthesis_agent.provider_config.model,
            "messages": test_messages
        }
        
        if synthesis_agent.tools:
            print(f"Including {len(synthesis_agent.tools)} tools in API call")
            api_params["tools"] = synthesis_agent.tools
        else:
            print("NOT including tools parameter (empty array)")
        
        # Make the API call
        print("\nMaking API call...")
        try:
            response = synthesis_agent.client.chat.completions.create(**api_params)
            print("✅ API call successful!")
            print(f"Response: {response.choices[0].message.content[:100]}...")
        except Exception as e:
            print(f"❌ API call failed: {str(e)}")
            
            # Try again with a dummy tool if we had an empty tools error
            if "empty array" in str(e).lower():
                print("\n🔧 Attempting fix: Adding dummy tool...")
                
                # Create a dummy tool that won't be used
                dummy_tool = {
                    "type": "function",
                    "function": {
                        "name": "dummy_tool",
                        "description": "A dummy tool that does nothing",
                        "parameters": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    }
                }
                
                # Add dummy tool and try again
                api_params["tools"] = [dummy_tool]
                print("Making API call with dummy tool...")
                try:
                    response = synthesis_agent.client.chat.completions.create(**api_params)
                    print("✅ API call with dummy tool successful!")
                    print(f"Response: {response.choices[0].message.content[:100]}...")
                    print("\n🔍 SOLUTION: Add a dummy tool when tools array would be empty")
                except Exception as e2:
                    print(f"❌ API call with dummy tool also failed: {str(e2)}")
        
        # Restore original tools
        synthesis_agent.tools = original_tools
        
        print("\n=" * 30)
        print("Debug complete!")
        
    except Exception as e:
        print(f"❌ Debug process failed: {str(e)}")

if __name__ == "__main__":
    debug_synthesis()