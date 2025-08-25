#!/usr/bin/env python3
"""
Test script for the new user-friendly analysis format
"""

import asyncio
import httpx
import json
from datetime import datetime

async def test_user_friendly_analysis():
    """Test the new user-friendly analysis endpoints"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing User-Friendly Analysis Format")
    print("=" * 50)
    
    # Test 1: Check if the endpoint exists
    print("\n1. Testing endpoint availability...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/news-impact/user-friendly-analyses")
            print(f"✅ Endpoint accessible: {response.status_code}")
            data = response.json()
            print(f"   Current analyses: {data['total_count']}")
    except Exception as e:
        print(f"❌ Error accessing endpoint: {e}")
        return
    
    # Test 2: Check the NewsImpact Orchestrator workflow
    print("\n2. Testing NewsImpact Orchestrator workflow...")
    try:
        async with httpx.AsyncClient() as client:
            # First, fetch some news
            print("   Fetching news...")
            news_response = await client.post(f"{base_url}/news/fetch", json={
                "sources": ["coindesk", "cointelegraph"],
                "limit": 3
            })
            
            if news_response.status_code == 200:
                news_data = news_response.json()
                print(f"   ✅ Fetched {len(news_data.get('news', []))} news items")
                
                # Now run the news impact workflow
                print("   Running news impact workflow...")
                workflow_response = await client.post(f"{base_url}/news-impact/workflow", json={
                    "sources": ["coindesk", "cointelegraph"],
                    "news_limit": 3,
                    "crypto_focus": True
                })
                
                if workflow_response.status_code == 200:
                    workflow_data = workflow_response.json()
                    print(f"   ✅ Workflow started: {workflow_data.get('workflow_id', 'N/A')}")
                    
                    # Wait a bit for processing
                    await asyncio.sleep(5)
                    
                    # Check workflow status
                    status_response = await client.get(f"{base_url}/news-impact/workflow/status")
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        print(f"   ✅ Workflow status: {status_data.get('status', {}).get('current_phase', 'Unknown')}")
                        
                        # Get user-friendly analyses
                        analyses_response = await client.get(f"{base_url}/news-impact/user-friendly-analyses")
                        if analyses_response.status_code == 200:
                            analyses_data = analyses_response.json()
                            print(f"   ✅ User-friendly analyses: {analyses_data['total_count']}")
                            
                            if analyses_data['total_count'] > 0:
                                print("\n   📊 Sample Analysis Structure:")
                                sample = analyses_data['analyses'][0]
                                for key, value in sample.items():
                                    print(f"      {key}: {value}")
                            else:
                                print("   ⏳ No analyses available yet (workflow may still be running)")
                        else:
                            print(f"   ❌ Failed to get analyses: {analyses_response.status_code}")
                    else:
                        print(f"   ❌ Failed to get workflow status: {status_response.status_code}")
                else:
                    print(f"   ❌ Failed to start workflow: {workflow_response.status_code}")
                    print(f"   Error: {workflow_response.text}")
            else:
                print(f"   ❌ Failed to fetch news: {news_response.status_code}")
                
    except Exception as e:
        print(f"❌ Error testing workflow: {e}")
    
    # Test 3: Check the new data structure
    print("\n3. Testing new data structure...")
    try:
        from news_impact_analysis import NewsImpactAnalysis
        
        # Create a sample analysis with the new structure
        sample_analysis = NewsImpactAnalysis(
            date="2025-08-26",
            category="Macro / Fed",
            headline="Powell hints rate cuts may be needed; markets price Sept cut",
            source="Reuters",
            link="https://example.com/article",
            expected_impact="Bullish BTC/ETH & risk assets (lower discount rates); watch USD DXY down",
            affected_assets_sectors="BTC, ETH, high-beta alts; USD; yields",
            how_to_trade_it="Fade spikes; scale into strength on dovish follow-through; reduce if USD rebounds",
            sentiment="Bullish",
            confidence_score=0.85,
            market_impact="High",
            volatility_impact="Medium",
            time_horizon="Short-term",
            risk_level="Medium",
            risk_factors=["Fed policy uncertainty", "Market volatility"],
            trading_recommendation="Buy",
            position_sizing="Medium",
            stop_loss_considerations="Set stops below key support levels",
            analysis_timestamp=datetime.now().isoformat(),
            key_topics=["Fed policy", "Rate cuts", "Market pricing"],
            market_context="Current dovish Fed stance supporting risk assets",
            related_events=["September FOMC meeting", "Jackson Hole symposium"]
        )
        
        # Test the user-friendly format
        user_friendly = sample_analysis.to_user_friendly_dict()
        print("   ✅ Sample analysis created successfully")
        print("   📋 User-friendly format:")
        for key, value in user_friendly.items():
            print(f"      {key}: {value}")
            
    except Exception as e:
        print(f"❌ Error testing data structure: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Testing completed!")

if __name__ == "__main__":
    asyncio.run(test_user_friendly_analysis())
