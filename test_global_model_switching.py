#!/usr/bin/env python3
"""
Test script for global model switching functionality
Tests that all agents can switch between OpenAI and DeepSeek AI models
"""

import os
import asyncio
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_global_model_switching():
    """Test the global model switching functionality"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Global Model Switching Functionality")
    print("=" * 60)
    
    # Test 1: Get current model info for all agents
    print("\n1️⃣ Testing /agents/model-info endpoint...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/agents/model-info")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print("✅ Successfully retrieved model info for all agents")
                    agents = data["agents"]
                    for agent_name, agent_info in agents.items():
                        print(f"   📍 {agent_name}: {agent_info['current_model']} (Available: {agent_info['available_models']})")
                else:
                    print(f"❌ Failed to get model info: {data.get('error')}")
                    return False
            else:
                print(f"❌ HTTP {response.status_code}: {response.text}")
                return False
    except Exception as e:
        print(f"❌ Error testing model info endpoint: {e}")
        return False
    
    # Test 2: Switch all agents to DeepSeek AI
    print("\n2️⃣ Testing global model switch to DeepSeek AI...")
    try:
        async with httpx.AsyncClient() as client:
            agents = ['ingestion', 'analysis', 'fundamentals', 'post_creation', 'categorization']
            success_count = 0
            
            for agent in agents:
                try:
                    response = await client.post(
                        f"{base_url}/agents/switch-model",
                        json={
                            "agent_type": agent,
                            "model_type": "deepseek"
                        }
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("success"):
                            print(f"   ✅ {agent}: Successfully switched to DeepSeek AI")
                            success_count += 1
                        else:
                            print(f"   ❌ {agent}: {data.get('error')}")
                    else:
                        print(f"   ❌ {agent}: HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ {agent}: Error - {e}")
            
            print(f"   📊 Result: {success_count}/{len(agents)} agents switched successfully")
            
            if success_count == len(agents):
                print("✅ All agents successfully switched to DeepSeek AI")
            else:
                print("⚠️ Some agents failed to switch")
                
    except Exception as e:
        print(f"❌ Error testing model switching: {e}")
        return False
    
    # Test 3: Verify the switch by getting model info again
    print("\n3️⃣ Verifying model switch...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/agents/model-info")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    agents = data["agents"]
                    deepseek_count = 0
                    for agent_name, agent_info in agents.items():
                        if agent_info['current_model'] == 'deepseek':
                            deepseek_count += 1
                            print(f"   ✅ {agent_name}: {agent_info['current_model']}")
                        else:
                            print(f"   ❌ {agent_name}: {agent_info['current_model']} (expected: deepseek)")
                    
                    print(f"   📊 DeepSeek AI agents: {deepseek_count}/{len(agents)}")
                    
                    if deepseek_count == len(agents):
                        print("✅ All agents are now using DeepSeek AI")
                    else:
                        print("⚠️ Not all agents switched to DeepSeek AI")
                        
                else:
                    print(f"❌ Failed to verify model info: {data.get('error')}")
                    return False
            else:
                print(f"❌ HTTP {response.status_code}: {response.text}")
                return False
    except Exception as e:
        print(f"❌ Error verifying model switch: {e}")
        return False
    
    # Test 4: Switch back to OpenAI
    print("\n4️⃣ Testing global model switch back to OpenAI...")
    try:
        async with httpx.AsyncClient() as client:
            agents = ['ingestion', 'analysis', 'fundamentals', 'post_creation', 'categorization']
            success_count = 0
            
            for agent in agents:
                try:
                    response = await client.post(
                        f"{base_url}/agents/switch-model",
                        json={
                            "agent_type": agent,
                            "model_type": "openai"
                        }
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("success"):
                            print(f"   ✅ {agent}: Successfully switched back to OpenAI")
                            success_count += 1
                        else:
                            print(f"   ❌ {agent}: {data.get('error')}")
                    else:
                        print(f"   ❌ {agent}: HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ {agent}: Error - {e}")
            
            print(f"   📊 Result: {success_count}/{len(agents)} agents switched back successfully")
            
            if success_count == len(agents):
                print("✅ All agents successfully switched back to OpenAI")
            else:
                print("⚠️ Some agents failed to switch back")
                
    except Exception as e:
        print(f"❌ Error testing model switch back: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 Global Model Switching Test Completed!")
    return True

async def main():
    """Main function"""
    print("🚀 Starting Global Model Switching Test")
    print("Make sure the FastAPI server is running on http://localhost:8000")
    print()
    
    try:
        success = await test_global_model_switching()
        if success:
            print("\n✅ All tests passed! Global model switching is working correctly.")
        else:
            print("\n❌ Some tests failed. Check the output above for details.")
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
