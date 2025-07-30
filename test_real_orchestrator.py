#!/usr/bin/env python3
"""
Test real orchestrator scenario
"""

import sys
from orchestrator import TaskOrchestrator

def test_real_orchestrator():
    """Test orchestrator with a real query"""
    print("🧪 Testing real orchestrator scenario...")
    
    try:
        orchestrator = TaskOrchestrator('config_deepseek.yaml', silent=False)
        
        # Test with a simple query
        user_input = "What is artificial intelligence?"
        
        print(f"\nTesting with query: {user_input}")
        result = orchestrator.orchestrate(user_input)
        
        print("✅ Orchestration successful!")
        print(f"Result length: {len(result)} characters")
        print(f"First 200 chars: {result[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Orchestration failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_real_orchestrator()
    sys.exit(0 if success else 1)