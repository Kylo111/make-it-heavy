#!/usr/bin/env python3
"""
Test the final fix for DeepSeek empty tools issue
"""

import sys
from agent import UniversalAgent
from orchestrator import TaskOrchestrator

def test_empty_tools():
    """Test agent with empty tools"""
    print("🧪 Testing agent with empty tools...")
    
    try:
        agent = UniversalAgent('config_deepseek.yaml', silent=True)
        print(f"✅ Agent initialized with {len(agent.tools)} tools")
        
        # Force empty tools
        agent.tools = []
        
        # Test run method
        result = agent.run("Hello, please respond to this message.")
        print("✅ Run with empty tools successful")
        print(f"Result: {result[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_orchestrator_synthesis():
    """Test orchestrator synthesis"""
    print("\n🧪 Testing orchestrator synthesis...")
    
    try:
        orchestrator = TaskOrchestrator('config_deepseek.yaml', silent=True)
        print("✅ Orchestrator initialized")
        
        # Test synthesis with mock responses
        test_responses = [
            "This is response from agent 1 with some detailed information.",
            "This is response from agent 2 with alternative perspective."
        ]
        
        result = orchestrator._aggregate_consensus(test_responses, [])
        print("✅ Synthesis completed without errors")
        print(f"✅ Result generated ({len(result)} characters)")
        print(f"First 100 chars: {result[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Final DeepSeek Fix")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 2
    
    # Test 1: Empty tools
    if test_empty_tools():
        tests_passed += 1
    
    # Test 2: Orchestrator synthesis
    if test_orchestrator_synthesis():
        tests_passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! DeepSeek integration is working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())