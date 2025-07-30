#!/usr/bin/env python3
"""
Demo script to test multi-model orchestrator functionality.
"""

import yaml
import tempfile
import os
from orchestrator import TaskOrchestrator
from model_config.data_models import AgentModelConfig


def create_test_config_with_multi_model():
    """Create a test configuration with multi-model setup."""
    config = {
        'provider': {'type': 'deepseek'},
        'deepseek': {
            'api_key': 'sk-16dc8f03dd4a4ae4835330cd78eb79bf',
            'base_url': 'https://api.deepseek.com',
            'model': 'deepseek-chat'
        },
        'system_prompt': '''You are a helpful research assistant. When users ask questions that require 
current information or web search, use the search tool and all other tools available to find relevant 
information and provide comprehensive answers based on the results.

IMPORTANT: When you have fully satisfied the user's request and provided a complete answer, 
you MUST call the mark_task_complete tool with a summary of what was accomplished and 
a final message for the user. This signals that the task is finished.''',
        'agent': {'max_iterations': 5},
        'orchestrator': {
            'parallel_agents': 2,
            'task_timeout': 60,
            'aggregation_strategy': 'consensus',
            'question_generation_prompt': '''You are an orchestrator that needs to create {num_agents} different questions to thoroughly analyze this topic from multiple angles.

Original user query: {user_input}

Generate exactly {num_agents} different, specific questions that will help gather comprehensive information about this topic.
Each question should approach the topic from a different angle (research, analysis, verification, alternatives, etc.).

Return your response as a JSON array of strings, like this:
["question 1", "question 2"]

Only return the JSON array, nothing else.''',
            'synthesis_prompt': '''You have {num_responses} different AI agents that analyzed the same query from different perspectives. 
Your job is to synthesize their responses into ONE comprehensive final answer.

Here are all the agent responses:

{agent_responses}

IMPORTANT: Just synthesize these into ONE final comprehensive answer that combines the best information from all agents. 
Do NOT call mark_task_complete or any other tools. Do NOT mention that you are synthesizing multiple responses. 
Simply provide the final synthesized answer directly as your response.'''
        },
        'search': {
            'max_results': 5,
            'user_agent': 'Mozilla/5.0 (compatible; DeepSeek Agent)'
        },
        'multi_model': {
            'agent_0_model': 'deepseek-chat',
            'agent_1_model': 'deepseek-reasoner',
            'agent_2_model': 'deepseek-chat',
            'agent_3_model': 'deepseek-reasoner',
            'synthesis_model': 'deepseek-reasoner',
            'default_model': 'deepseek-chat',
            'profile_name': 'mixed'
        }
    }
    
    # Create temporary config file
    temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
    yaml.dump(config, temp_config)
    temp_config.close()
    
    return temp_config.name


def demo_multi_model_orchestrator():
    """Demonstrate multi-model orchestrator functionality."""
    print("🚀 Multi-Model Orchestrator Demo")
    print("=" * 50)
    
    # Create test configuration
    config_path = create_test_config_with_multi_model()
    
    try:
        # Initialize orchestrator
        print("📋 Initializing orchestrator with multi-model configuration...")
        orchestrator = TaskOrchestrator(config_path, silent=False)
        
        # Check if multi-model is enabled
        if orchestrator.multi_model_config:
            print("✅ Multi-model configuration loaded successfully!")
            print(f"   Agent 0 model: {orchestrator.multi_model_config.agent_0_model}")
            print(f"   Agent 1 model: {orchestrator.multi_model_config.agent_1_model}")
            print(f"   Synthesis model: {orchestrator.multi_model_config.synthesis_model}")
        else:
            print("❌ Multi-model configuration not found")
            return
        
        # Test model assignment
        print("\n🧠 Testing model assignment...")
        for i in range(2):
            model = orchestrator._get_agent_model(i)
            print(f"   Agent {i} will use: {model}")
        
        synthesis_model = orchestrator._get_synthesis_model()
        print(f"   Synthesis will use: {synthesis_model}")
        
        # Test simple query (without actual API calls for demo)
        print("\n🔍 Testing orchestration flow...")
        print("Query: 'What are the benefits of renewable energy?'")
        
        # Mock the orchestration to avoid API calls in demo
        print("\n📊 Simulating multi-agent execution...")
        
        # Simulate agent execution
        orchestrator.agent_models[0] = orchestrator._get_agent_model(0)
        orchestrator.agent_models[1] = orchestrator._get_agent_model(1)
        orchestrator.agent_costs[0] = 0.0015
        orchestrator.agent_costs[1] = 0.0025
        
        # Show execution summary
        print("\n📈 Execution Summary:")
        orchestrator.log_execution_summary()
        
        # Get detailed summary
        summary = orchestrator.get_execution_summary()
        print(f"\n📋 Detailed Summary:")
        print(f"   Multi-model enabled: {summary['multi_model_enabled']}")
        print(f"   Total estimated cost: ${summary['total_estimated_cost']:.6f}")
        print(f"   Models used: {summary['agent_models']}")
        
        print("\n✅ Demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        if os.path.exists(config_path):
            os.unlink(config_path)


def demo_without_multi_model():
    """Demonstrate orchestrator without multi-model configuration."""
    print("\n🔄 Testing without multi-model configuration...")
    
    config = {
        'provider': {'type': 'deepseek'},
        'deepseek': {
            'api_key': 'sk-16dc8f03dd4a4ae4835330cd78eb79bf',
            'base_url': 'https://api.deepseek.com',
            'model': 'deepseek-chat'
        },
        'system_prompt': 'Test prompt',
        'agent': {'max_iterations': 3},
        'orchestrator': {
            'parallel_agents': 2,
            'task_timeout': 30,
            'aggregation_strategy': 'consensus',
            'question_generation_prompt': 'Generate questions',
            'synthesis_prompt': 'Synthesize responses'
        },
        'search': {'max_results': 5}
    }
    
    temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
    yaml.dump(config, temp_config)
    temp_config.close()
    
    try:
        orchestrator = TaskOrchestrator(temp_config.name, silent=False)
        
        if orchestrator.multi_model_config:
            print("❌ Unexpected: Multi-model config found")
        else:
            print("✅ No multi-model configuration (as expected)")
        
        # Test fallback behavior
        for i in range(2):
            model = orchestrator._get_agent_model(i)
            print(f"   Agent {i} fallback model: {model}")
        
        summary = orchestrator.get_execution_summary()
        print(f"   Multi-model enabled: {summary['multi_model_enabled']}")
        
    finally:
        if os.path.exists(temp_config.name):
            os.unlink(temp_config.name)


if __name__ == "__main__":
    demo_multi_model_orchestrator()
    demo_without_multi_model()