#!/usr/bin/env python3
"""
Test script for NewsImpact Orchestrator and User-Friendly Endpoints
"""

import requests
import json
from datetime import datetime

def test_newsimpact_workflow():
    """Test the complete NewsImpact Orchestrator workflow"""
    print("🧪 Testing NewsImpact Orchestrator Workflow...")
    
    # Test the workflow endpoint
    workflow_url = "http://localhost:8000/news-impact/workflow"
    workflow_data = {
        "sources": ["CoinDesk", "CoinTelegraph"],
        "news_limit": 3
    }
    
    try:
        response = requests.post(workflow_url, json=workflow_data)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ NewsImpact Workflow completed successfully!")
                print(f"   Workflow ID: {result['result']['workflow_id']}")
                print(f"   Fetched News: {result['result']['fetched_news_count']}")
                print(f"   Analyzed News: {result['result']['analyzed_news_count']}")
                print(f"   Execution Time: {result['result']['execution_time']:.3f}s")
                return True
            else:
                print(f"❌ Workflow failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing workflow: {e}")
        return False

def test_user_friendly_endpoints():
    """Test the user-friendly analysis endpoints"""
    print("\n🧪 Testing User-Friendly Endpoints...")
    
    # Test the main user-friendly analyses endpoint
    try:
        response = requests.get("http://localhost:8000/news-impact/user-friendly-analyses")
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                analyses = result['result']['analyses']
                print(f"✅ User-friendly analyses endpoint working!")
                print(f"   Total analyses: {result['result']['total_count']}")
                
                # Display the first analysis in user-friendly format
                if analyses:
                    first_analysis = analyses[0]
                    print("\n📊 Sample User-Friendly Analysis:")
                    print(f"   Date: {first_analysis['date']}")
                    print(f"   Category: {first_analysis['category']}")
                    print(f"   Headline: {first_analysis['headline']}")
                    print(f"   Expected Impact: {first_analysis['expected_impact']}")
                    print(f"   Affected Assets/Sectors: {first_analysis['affected_assets_sectors']}")
                    print(f"   How to Trade: {first_analysis['how_to_trade_it']}")
                    print(f"   Source: {first_analysis['source']}")
                    print(f"   Link: {first_analysis['link']}")
                    print(f"   Confidence: {first_analysis['confidence']}")
                    print(f"   Risk Level: {first_analysis['risk_level']}")
                    print(f"   Time Horizon: {first_analysis['time_horizon']}")
                
                return True
            else:
                print(f"❌ User-friendly endpoint failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing user-friendly endpoint: {e}")
        return False

def test_specific_analysis():
    """Test getting a specific analysis by ID"""
    print("\n🧪 Testing Specific Analysis Endpoint...")
    
    try:
        # First get all analyses to find an ID
        response = requests.get("http://localhost:8000/news-impact/user-friendly-analyses")
        if response.status_code == 200:
            result = response.json()
            if result.get("success") and result['result']['analyses']:
                # Get the first analysis ID
                first_analysis = result['result']['analyses'][0]
                headline = first_analysis['headline']
                analysis_id = headline[:20]  # Use first 20 chars as ID
                
                # Test the specific analysis endpoint
                specific_url = f"http://localhost:8000/news-impact/analyses/{analysis_id}"
                specific_response = requests.get(specific_url)
                
                if specific_response.status_code == 200:
                    specific_result = specific_response.json()
                    if specific_result.get("success"):
                        print(f"✅ Specific analysis endpoint working!")
                        print(f"   Retrieved analysis for ID: {analysis_id}")
                        return True
                    else:
                        print(f"❌ Specific analysis failed: {specific_result.get('error', 'Unknown error')}")
                        return False
                else:
                    print(f"❌ HTTP Error: {specific_response.status_code}")
                    return False
            else:
                print("❌ No analyses available to test specific endpoint")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing specific analysis endpoint: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing NewsImpact Orchestrator and User-Friendly Endpoints")
    print("=" * 70)
    
    # Test 1: Workflow
    workflow_success = test_newsimpact_workflow()
    
    # Test 2: User-friendly endpoints
    user_friendly_success = test_user_friendly_endpoints()
    
    # Test 3: Specific analysis
    specific_success = test_specific_analysis()
    
    # Summary
    print("\n" + "=" * 70)
    print("📋 Test Summary:")
    print(f"   NewsImpact Workflow: {'✅ PASS' if workflow_success else '❌ FAIL'}")
    print(f"   User-Friendly Endpoints: {'✅ PASS' if user_friendly_success else '❌ FAIL'}")
    print(f"   Specific Analysis: {'✅ PASS' if specific_success else '❌ FAIL'}")
    
    if all([workflow_success, user_friendly_success, specific_success]):
        print("\n🎉 All tests passed! The NewsImpact Orchestrator is working correctly.")
        print("   The system is now providing user-friendly analysis format for decision making.")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
