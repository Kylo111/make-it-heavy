#!/usr/bin/env python3
"""
Detailed debug script for synthesis issues with DeepSeek
"""

import json
import yaml
import sys
from agent import UniversalAgent
from orchestrator import TaskOrchestrator

def debug_synthesis_step_by_step():
    """Debug the synthesis process step by step with detailed logging"""
    print("🔍 Detailed Synthesis Debug")
    print("=" * 60)
    
    try:
        # Create orchestrator
        orchestrator = TaskOrchestrator('config_deepseek.yaml', silent=True)
        
        # Mock responses for testing
        test_responses = [
            "Response from agent 1: This is some detailed analysis.",
            "Response from agent 2: This is an alternative perspective."
        ]
        
        print("🧪 Testing _aggregate_consensus method directly...")
        
        # Call the method that's failing
        try:
            result = orchestrator._aggregate_consensus(test_responses, [])
            print("✅ Synthesis successful!")
            print(f"Result: {result[:100]}...")
        except Exception as e:
            print(f"❌ Synthesis failed: {str(e)}")
            
            # Let's debug the synthesis agent creation manually
            print("\n🔧 Manual synthesis agent debug...")
            
            # Create synthesis agent manually
            synthesis_agent = UniversalAgent(config_path='config_deepseek.yaml', silent=False)
            
            print(f"Initial tools: {len(synthesis_agent.tools)}")
            for i, tool in enumerate(synthesis_agent.tools):
                print(f"  {i+1}. {tool.get('function', {}).get('name', 'unknown')}")
            
            # Apply filtering
            print("\nApplying tool filtering...")
            synthesis_agent.tools = [tool for tool in synthesis_agent.tools if tool.get('function', {}).get('name') != 'mark_task_complete']
            synthesis_agent.tool_mapping = {name: func for name, func in synthesis_agent.tool_mapping.items() if name != 'mark_task_complete'}
            
            print(f"After filtering: {len(synthesis_agent.tools)}")
            for i, tool in enumerate(synthesis_agent.tools):
                print(f"  {i+1}. {tool.get('function', {}).get('name', 'unknown')}")
            
            # Check if we need dummy tool
            if not synthesis_agent.tools:
                print("⚠️ No tools left! Adding dummy tool...")
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
                synthesis_agent.tools = [dummy_tool]
                print("✅ Dummy tool added")
            
            # Test synthesis prompt
            agent_responses_text = ""
            for i, response in enumerate(test_responses, 1):
                agent_responses_text += f"=== AGENT {i} RESPONSE ===\n{response}\n\n"
            
            synthesis_prompt_template = orchestrator.config['orchestrator']['synthesis_prompt']
            synthesis_prompt = synthesis_prompt_template.format(
                num_responses=len(test_responses),
                agent_responses=agent_responses_text
            )
            
            print(f"\nSynthesis prompt length: {len(synthesis_prompt)}")
            print(f"Tools count before run: {len(synthesis_agent.tools)}")
            
            # Try to run synthesis
            print("\n🚀 Running synthesis...")
            try:
                final_answer = synthesis_agent.run(synthesis_prompt)
                print("✅ Synthesis successful!")
                print(f"Result: {final_answer[:100]}...")
            except Exception as e2:
                print(f"❌ Synthesis run failed: {str(e2)}")
                
                # Check tools state after failure
                print(f"Tools count after failure: {len(synthesis_agent.tools)}")
                
                # Try direct API call
                print("\n🔧 Trying direct API call...")
                try:
                    test_messages = [{"role": "user", "content": "Hello"}]
                    response = synthesis_agent.call_llm(test_messages)
                    print("✅ Direct API call successful!")
                except Exception as e3:
                    print(f"❌ Direct API call failed: {str(e3)}")
                    print(f"Tools at failure: {synthesis_agent.tools}")
        
    except Exception as e:
        print(f"❌ Debug process failed: {str(e)}")

if __name__ == "__main__":
    debug_synthesis_step_by_step()