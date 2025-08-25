#!/usr/bin/env python3
"""
Test script to verify that global model switching is working properly
for all agents in the pipeline.
"""

import asyncio
import json
import httpx
import time

async def test_global_model_switching():
    """Test the global model switching functionality"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Global Model Switching Functionality")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        try:
            # Step 1: Check current model status for all agents
            print("\n1️⃣ Checking current model status for all agents...")
            response = await client.get(f"{base_url}/agents/model-info")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print("✅ Current model status:")
                    for agent_name, agent_info in data["agents"].items():
                        print(f"   • {agent_name}: {agent_info['current_model']}")
                else:
                    print(f"❌ Failed to get model info: {data.get('error')}")
                    return
            else:
                print(f"❌ Failed to get model info: {response.status_code}")
                return
            
            # Step 2: Switch all agents to DeepSeek AI
            print("\n2️⃣ Switching all agents to DeepSeek AI...")
            agents_to_switch = ["ingestion", "analysis", "fundamentals", "post_creation", "categorization"]
            success_count = 0
            
            for agent in agents_to_switch:
                try:
                    response = await client.post(
                        f"{base_url}/agents/switch-model",
                        json={"agent_type": agent, "model_type": "deepseek"}
                    )
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("success"):
                            print(f"   ✅ {agent}: Switched to {data['current_model']}")
                            success_count += 1
                        else:
                            print(f"   ❌ {agent}: {data.get('error')}")
                    else:
                        print(f"   ❌ {agent}: HTTP {response.status_code}")
                except Exception as e:
                    print(f"   ❌ {agent}: Error - {e}")
            
            print(f"\n📊 Successfully switched {success_count}/{len(agents_to_switch)} agents")
            
            # Step 3: Verify the switch by checking model status again
            print("\n3️⃣ Verifying model switch...")
            await asyncio.sleep(1)  # Give some time for the switch to take effect
            
            response = await client.get(f"{base_url}/agents/model-info")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print("✅ Updated model status:")
                    for agent_name, agent_info in data["agents"].items():
                        print(f"   • {agent_name}: {agent_info['current_model']}")
                else:
                    print(f"❌ Failed to get updated model info: {data.get('error')}")
            
            # Step 4: Test ingestion pipeline to ensure it uses the new model
            print("\n4️⃣ Testing ingestion pipeline with new model...")
            response = await client.post(
                f"{base_url}/pipeline/ingestion",
                json={"sources": ["CoinDesk"], "news_limit": 2, "crypto_focus": True}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print("✅ Ingestion pipeline executed successfully!")
                    print(f"   📰 Fetched {len(data['result']['news_items'])} news items")
                else:
                    print(f"❌ Ingestion pipeline failed: {data.get('error')}")
            else:
                print(f"❌ Ingestion pipeline HTTP error: {response.status_code}")
            
            # Step 5: Switch back to OpenAI
            print("\n5️⃣ Switching all agents back to OpenAI...")
            success_count = 0
            
            for agent in agents_to_switch:
                try:
                    response = await client.post(
                        f"{base_url}/agents/switch-model",
                        json={"agent_type": agent, "model_type": "openai"}
                    )
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("success"):
                            print(f"   ✅ {agent}: Switched to {data['current_model']}")
                            success_count += 1
                        else:
                            print(f"   ❌ {agent}: {data.get('error')}")
                    else:
                        print(f"   ❌ {agent}: HTTP {response.status_code}")
                except Exception as e:
                    print(f"   ❌ {agent}: Error - {e}")
            
            print(f"\n📊 Successfully switched back {success_count}/{len(agents_to_switch)} agents")
            
            # Step 6: Final verification
            print("\n6️⃣ Final model status verification...")
            await asyncio.sleep(1)
            
            response = await client.get(f"{base_url}/agents/model-info")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print("✅ Final model status:")
                    for agent_name, agent_info in data["agents"].items():
                        print(f"   • {agent_name}: {agent_info['current_model']}")
                else:
                    print(f"❌ Failed to get final model info: {data.get('error')}")
            
            print("\n🎉 Global model switching test completed!")
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Global Model Switching Test")
    print("Make sure the server is running on http://localhost:8000")
    print()
    
    asyncio.run(test_global_model_switching())
