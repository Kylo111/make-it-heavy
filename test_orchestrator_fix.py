#!/usr/bin/env python3
"""
Test script to verify orchestrator synthesis fix
"""

import sys
from orchestrator import TaskOrchestrator

def test_orchestrator_synthesis():
    """Test that orchestrator synthesis works without tools errors"""
    print("🧪 Testing orchestrator synthesis with dummy tool fix...")
    
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
        print(f"❌ Orchestrator test failed: {e}")
        return False

def main():
    """Run the test"""
    print("🚀 Testing Orchestrator Synthesis Fix")
    print("=" * 50)
    
    success = test_orchestrator_synthesis()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Test passed! Orchestrator synthesis is working correctly.")
        return 0
    else:
        print("⚠️ Test failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())