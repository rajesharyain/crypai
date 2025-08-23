#!/usr/bin/env python3
"""
Simple test script for the Orchestrator Agent
Tests basic initialization and status without running the full pipeline
"""

import asyncio
from orchestrator import OrchestratorAgent

async def test_orchestrator_basics():
    """Test basic orchestrator functionality"""
    print("🧪 Testing Orchestrator Agent Basics...")
    print("=" * 60)
    
    try:
        # Test initialization
        orchestrator = OrchestratorAgent()
        print("✅ Orchestrator Agent initialized successfully")
        
        # Test status
        status = orchestrator.get_agent_status()
        print(f"   Status: {status['orchestrator_status']}")
        print(f"   Default Symbol: {status['default_symbol']}")
        
        # Test pipeline info
        pipeline_info = orchestrator.get_pipeline_info()
        print(f"   Pipeline Steps: {len(pipeline_info['pipeline_steps'])}")
        print(f"   Supported Operations: {len(pipeline_info['supported_operations'])}")
        
        # Display pipeline structure
        print(f"\n📋 Pipeline Structure:")
        for step in pipeline_info['pipeline_steps']:
            print(f"   {step['step']}. {step['name']} ({step['agent']})")
            print(f"      {step['description']}")
        
        # Display agent statuses
        print(f"\n🤖 Agent Statuses:")
        for agent_name, agent_status in status['agents'].items():
            if isinstance(agent_status, dict):
                print(f"   {agent_name}: {agent_status.get('status', 'available')}")
            else:
                print(f"   {agent_name}: {agent_status}")
        
        print("\n🎉 Basic orchestrator test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error in basic orchestrator test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🚀 Simple Orchestrator Agent Test")
    print("=" * 60)
    
    try:
        result = await test_orchestrator_basics()
        if result:
            print("\n✅ All basic tests passed!")
            print("\n💡 Next steps:")
            print("   - Test with valid OpenAI API key")
            print("   - Test the /run_pipeline endpoint")
            print("   - Test multiple news pipeline")
            print("   - Check orchestrator status")
        else:
            print("\n❌ Some tests failed. Check the output above for details.")
            
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
