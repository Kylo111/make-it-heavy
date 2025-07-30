#!/usr/bin/env python3
"""
Test script to verify DeepSeek integration fixes
"""

import sys
from agent import UniversalAgent
from orchestrator import TaskOrchestrator

def test_agent_empty_tools():
    """Test that agent handles empty tools array correctly"""
    print("🧪 Testing agent with empty tools array...")
    
    try:
        agent = UniversalAgent('config_deepseek.yaml', silent=True)
        print(f"✅ Agent initialized with {len(agent.tools)} tools")
        
        # Simulate empty tools scenario
        original_tools = agent.tools.copy()
        agent.tools = []
        
        # Test API call with empty tools
        response = agent.call_llm([{'role': 'user', 'content': 'Say hello'}])
        print("✅ Empty tools handled correctly - no API error")
        
        # Restore tools
        agent.tools = original_tools
        return True
        
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        return False

def test_orchestrator_synthesis():
    """Test that orchestrator synthesis works without tools errors"""
    print("\n🧪 Testing orchestrator synthesis...")
    
    try:
        orchestrator = TaskOrchestrator('config_deepseek.yaml', silent=True)
        print("✅ Orchestrator initialized")
        
        # Test synthesis with mock responses
        test_responses = [
            "This is response from agent 1",
            "This is response from agent 2"
        ]
        
        result = orchestrator._aggregate_consensus(test_responses, [])
        print("✅ Synthesis completed without errors")
        print(f"✅ Result generated ({len(result)} characters)")
        return True
        
    except Exception as e:
        print(f"❌ Orchestrator test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing DeepSeek Integration Fixes")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 2
    
    # Test 1: Agent with empty tools
    if test_agent_empty_tools():
        tests_passed += 1
    
    # Test 2: Orchestrator synthesis
    if test_orchestrator_synthesis():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! DeepSeek integration is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())