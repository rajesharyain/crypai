#!/usr/bin/env python3
"""
Test script for the News Impact Analysis Workflow

This script tests the new orchestration workflow that:
1. Fetches news and stores in fetched_news_cache
2. Analyzes news impact using DeepSeek AI
3. Returns structured JSON for human decision making
"""

import asyncio
import json
import httpx
import time

async def test_news_impact_workflow():
    """Test the news impact analysis workflow"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing News Impact Analysis Workflow")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        try:
            # Step 1: Check if the server is running
            print("\n1️⃣ Checking server status...")
            response = await client.get(f"{base_url}/ping")
            if response.status_code == 200:
                print("✅ Server is running")
            else:
                print("❌ Server is not responding")
                return
            
            # Step 2: Check the news impact agent status
            print("\n2️⃣ Checking news impact agent status...")
            response = await client.get(f"{base_url}/news-impact/agent/status")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Agent status: {data['status']['model_type']}")
                print(f"   Fetched news cache size: {data['status']['fetched_news_cache_size']}")
                print(f"   Analysis cache size: {data['status']['analysis_cache_size']}")
            else:
                print("❌ Failed to get agent status")
                return
            
            # Step 3: Run the news impact workflow
            print("\n3️⃣ Running news impact analysis workflow...")
            workflow_request = {
                "sources": ["coindesk", "cointelegraph"],
                "news_limit": 5,
                "crypto_focus": True
            }
            
            start_time = time.time()
            response = await client.post(
                f"{base_url}/news-impact/workflow",
                json=workflow_request,
                timeout=120.0  # 2 minutes timeout for the workflow
            )
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    result = data['result']
                    print("✅ News impact workflow completed successfully!")
                    print(f"   Workflow ID: {result['workflow_id']}")
                    print(f"   Fetched News: {result['fetched_news_count']}")
                    print(f"   Analyzed News: {result['analyzed_news_count']}")
                    print(f"   Execution Time: {result['execution_time']:.2f}s")
                    print(f"   Total Time (including network): {end_time - start_time:.2f}s")
                    
                    # Display sentiment distribution
                    if result['sentiment_summary']:
                        print(f"\n📊 Sentiment Distribution:")
                        for sentiment, count in result['sentiment_summary'].items():
                            print(f"   {sentiment}: {count}")
                    
                    # Display market impact distribution
                    if result['impact_summary']:
                        print(f"\n📈 Market Impact Distribution:")
                        for impact, count in result['impact_summary'].items():
                            print(f"   {impact}: {count}")
                    
                    # Display trading insights
                    if result['trading_insights'] and not result['trading_insights'].get('error'):
                        insights = result['trading_insights']
                        print(f"\n💡 Trading Insights:")
                        print(f"   Affected Cryptos: {insights.get('affected_cryptos', [])}")
                        print(f"   Affected Sectors: {insights.get('affected_sectors', [])}")
                        print(f"   High Impact News: {len(insights.get('high_impact_news', []))}")
                        
                        if insights.get('trading_recommendations'):
                            print(f"   Trading Recommendations:")
                            for rec, count in insights['trading_recommendations'].items():
                                print(f"     {rec}: {count}")
                    
                    # Display sample analysis
                    if result['impact_analyses']:
                        print(f"\n🔍 Sample Impact Analysis:")
                        sample = result['impact_analyses'][0]
                        print(f"   Title: {sample['title'][:80]}...")
                        print(f"   Market Impact: {sample['market_impact']}")
                        print(f"   Sentiment: {sample['sentiment']}")
                        print(f"   Confidence: {sample['confidence_score']:.1%}")
                        print(f"   Trading Recommendation: {sample['trading_recommendation']}")
                        print(f"   Risk Level: {sample['risk_level']}")
                        
                        if sample.get('affected_cryptos'):
                            print(f"   Affected Cryptos: {len(sample['affected_cryptos'])}")
                            for crypto in sample['affected_cryptos'][:3]:  # Show first 3
                                print(f"     {crypto['symbol']} ({crypto['name']}) - {crypto['impact_level']}")
                    
                else:
                    print(f"❌ Workflow failed: {data.get('error', 'Unknown error')}")
            else:
                print(f"❌ HTTP error: {response.status_code}")
                print(f"Response: {response.text}")
            
            # Step 4: Check workflow history
            print("\n4️⃣ Checking workflow history...")
            response = await client.get(f"{base_url}/news-impact/workflow/history")
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    print(f"✅ Found {data['total_workflows']} workflows in history")
                    if data['history']:
                        latest = data['history'][0]
                        print(f"   Latest workflow: {latest['workflow_id']}")
                        print(f"   Status: {latest['workflow_status']}")
                        print(f"   Timestamp: {latest['timestamp']}")
                else:
                    print(f"❌ Failed to get workflow history: {data.get('error')}")
            else:
                print(f"❌ HTTP error getting history: {response.status_code}")
            
            # Step 5: Test model switching
            print("\n5️⃣ Testing model switching...")
            response = await client.post(
                f"{base_url}/news-impact/agent/switch-model",
                json={"model_type": "deepseek"}
            )
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    print(f"✅ Successfully switched to {data['current_model']} model")
                else:
                    print(f"❌ Failed to switch model: {data.get('error')}")
            else:
                print(f"❌ HTTP error switching model: {response.status_code}")
            
            print("\n" + "=" * 60)
            print("🎉 News Impact Analysis Workflow Test Completed!")
            
        except Exception as e:
            print(f"❌ Error during testing: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_news_impact_workflow())
