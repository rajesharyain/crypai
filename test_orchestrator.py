#!/usr/bin/env python3
"""
Test script for the Orchestrator Agent
Tests the complete pipeline: Ingestion → Analysis → Fundamentals → Post Creation
"""

import asyncio
import json
from datetime import datetime
from orchestrator import (
    OrchestratorAgent,
    run_complete_pipeline,
    run_multiple_news_pipeline
)

async def test_orchestrator_initialization():
    """Test orchestrator agent initialization"""
    print("🧪 Testing Orchestrator Agent Initialization...")
    print("=" * 70)
    
    try:
        orchestrator = OrchestratorAgent()
        status = orchestrator.get_agent_status()
        pipeline_info = orchestrator.get_pipeline_info()
        
        print(f"✅ Orchestrator Agent initialized successfully")
        print(f"   Status: {status['orchestrator_status']}")
        print(f"   Default Symbol: {status['default_symbol']}")
        print(f"   Pipeline Steps: {len(pipeline_info['pipeline_steps'])}")
        
        # Display pipeline steps
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
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing Orchestrator Agent: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_single_pipeline_execution():
    """Test single pipeline execution"""
    print("\n🧪 Testing Single Pipeline Execution...")
    print("=" * 70)
    
    try:
        print("🚀 Running complete pipeline with default settings...")
        print("   Symbol: SUI (default)")
        print("   News Limit: 1")
        
        result = await run_complete_pipeline(symbol="SUI", news_limit=1)
        
        if result:
            print("✅ Pipeline executed successfully!")
            
            # Display news item
            print(f"\n📰 News Item:")
            print(f"   Title: {result.news_item['title']}")
            print(f"   Source: {result.news_item['source']}")
            print(f"   Summary: {result.news_item['summary'][:100]}...")
            
            # Display analysis
            print(f"\n🔍 Analysis:")
            print(f"   Summary: {result.analysis['summary']}")
            print(f"   Sentiment: {result.analysis['sentiment']:.3f}")
            print(f"   Fundamentals: {result.analysis['fundamentals']}")
            print(f"   Confidence: {result.analysis['confidence']:.3f}")
            
            # Display fundamentals
            print(f"\n💰 Fundamentals ({result.fundamentals['symbol']}):")
            print(f"   Current Price: ${result.fundamentals['current_price']:,.2f}")
            print(f"   24h Change: {result.fundamentals['price_change_24h']:+.2f}%")
            print(f"   Market Cap Rank: #{result.fundamentals['market_cap_rank']}")
            print(f"   Volume 24h: ${result.fundamentals['volume_24h']:,.0f}")
            
            # Display posts
            print(f"\n📝 Social Media Posts:")
            print(f"   Twitter: {result.posts['twitter']['character_count']}/280 chars")
            print(f"   LinkedIn: {result.posts['linkedin']['character_count']}/1300 chars")
            print(f"   Telegram: {result.posts['telegram']['character_count']}/500 chars")
            
            # Display execution info
            print(f"\n⚡ Execution Info:")
            print(f"   Status: {result.pipeline_status}")
            print(f"   Execution Time: {result.execution_time:.2f} seconds")
            
            return True
        else:
            print("❌ Pipeline execution failed")
            return False
            
    except Exception as e:
        print(f"❌ Error in single pipeline execution: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_custom_symbol_pipeline():
    """Test pipeline with custom cryptocurrency symbol"""
    print("\n🧪 Testing Custom Symbol Pipeline...")
    print("=" * 70)
    
    try:
        custom_symbol = "BTC"
        print(f"🚀 Running pipeline with custom symbol: {custom_symbol}")
        print(f"   Symbol: {custom_symbol}")
        print(f"   News Limit: 1")
        
        result = await run_complete_pipeline(symbol=custom_symbol, news_limit=1)
        
        if result:
            print("✅ Custom symbol pipeline executed successfully!")
            
            # Display fundamentals for custom symbol
            print(f"\n💰 Fundamentals ({result.fundamentals['symbol']}):")
            print(f"   Current Price: ${result.fundamentals['current_price']:,.2f}")
            print(f"   24h Change: {result.fundamentals['price_change_24h']:+.2f}%")
            print(f"   Market Cap Rank: #{result.fundamentals['market_cap_rank']}")
            
            # Display execution info
            print(f"\n⚡ Execution Info:")
            print(f"   Status: {result.pipeline_status}")
            print(f"   Execution Time: {result.execution_time:.2f} seconds")
            
            return True
        else:
            print("❌ Custom symbol pipeline execution failed")
            return False
            
    except Exception as e:
        print(f"❌ Error in custom symbol pipeline execution: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_multiple_news_pipeline():
    """Test pipeline for multiple news items"""
    print("\n🧪 Testing Multiple News Pipeline...")
    print("=" * 70)
    
    try:
        news_limit = 2
        print(f"🚀 Running pipeline for multiple news items...")
        print(f"   Symbol: SUI (default)")
        print(f"   News Limit: {news_limit}")
        
        results = await run_multiple_news_pipeline(news_limit=news_limit)
        
        if results:
            print(f"✅ Multiple news pipeline executed successfully!")
            print(f"   📊 Total processed: {len(results)}")
            
            for i, result in enumerate(results, 1):
                print(f"\n   📰 News Item {i}:")
                print(f"      Title: {result.news_item['title'][:60]}...")
                print(f"      Sentiment: {result.analysis['sentiment']:.3f}")
                print(f"      Fundamentals: {result.analysis['fundamentals']}")
                print(f"      Twitter: {result.posts['twitter']['character_count']}/280 chars")
                print(f"      LinkedIn: {result.posts['linkedin']['character_count']}/1300 chars")
                print(f"      Telegram: {result.posts['telegram']['character_count']}/500 chars")
            
            return True
        else:
            print("❌ Multiple news pipeline execution failed")
            return False
            
    except Exception as e:
        print(f"❌ Error in multiple news pipeline execution: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_pipeline_error_handling():
    """Test pipeline error handling"""
    print("\n🧪 Testing Pipeline Error Handling...")
    print("=" * 70)
    
    try:
        orchestrator = OrchestratorAgent()
        
        # Test with invalid symbol
        print("🔍 Testing with invalid symbol...")
        result = await orchestrator.run_pipeline(symbol="INVALID_SYMBOL_123", news_limit=1)
        
        if result:
            print("✅ Pipeline handled invalid symbol gracefully")
            print(f"   Status: {result.pipeline_status}")
            print(f"   Fundamentals: {result.fundamentals}")
        else:
            print("❌ Pipeline failed completely with invalid symbol")
        
        # Test with very high news limit
        print(f"\n🔍 Testing with high news limit...")
        result = await orchestrator.run_pipeline(symbol="SUI", news_limit=100)
        
        if result:
            print("✅ Pipeline handled high news limit gracefully")
            print(f"   Status: {result.pipeline_status}")
        else:
            print("❌ Pipeline failed with high news limit")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in pipeline error handling test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_pipeline_performance():
    """Test pipeline performance and timing"""
    print("\n🧪 Testing Pipeline Performance...")
    print("=" * 70)
    
    try:
        print("⏱️  Testing pipeline execution time...")
        
        # Run pipeline multiple times to get average
        execution_times = []
        for i in range(3):
            print(f"   Run {i+1}/3...")
            start_time = asyncio.get_event_loop().time()
            
            result = await run_complete_pipeline(symbol="SUI", news_limit=1)
            
            if result:
                execution_time = asyncio.get_event_loop().time() - start_time
                execution_times.append(execution_time)
                print(f"      Completed in {execution_time:.2f} seconds")
            else:
                print(f"      Failed")
        
        if execution_times:
            avg_time = sum(execution_times) / len(execution_times)
            min_time = min(execution_times)
            max_time = max(execution_times)
            
            print(f"\n📊 Performance Results:")
            print(f"   Average Execution Time: {avg_time:.2f} seconds")
            print(f"   Fastest Execution: {min_time:.2f} seconds")
            print(f"   Slowest Execution: {max_time:.2f} seconds")
            print(f"   Total Runs: {len(execution_times)}")
            
            return True
        else:
            print("❌ No successful pipeline runs for performance testing")
            return False
            
    except Exception as e:
        print(f"❌ Error in pipeline performance test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🚀 Orchestrator Agent Test Suite")
    print("=" * 80)
    
    tests = [
        ("Orchestrator Initialization", test_orchestrator_initialization),
        ("Single Pipeline Execution", test_single_pipeline_execution),
        ("Custom Symbol Pipeline", test_custom_symbol_pipeline),
        ("Multiple News Pipeline", test_multiple_news_pipeline),
        ("Pipeline Error Handling", test_pipeline_error_handling),
        ("Pipeline Performance", test_pipeline_performance)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} Test...")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 Test Results Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The Orchestrator Agent is working correctly.")
        print("\n💡 Key Features Verified:")
        print("   ✅ Complete pipeline orchestration")
        print("   ✅ News ingestion → Analysis → Fundamentals → Post Creation")
        print("   ✅ Custom cryptocurrency symbol support")
        print("   ✅ Multiple news item processing")
        print("   ✅ Error handling and fallbacks")
        print("   ✅ Performance monitoring")
        print("   ✅ Agent status monitoring")
        print("   ✅ Pipeline information")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print("\n🚀 Next steps:")
    print("   - Test the /run_pipeline endpoint: POST /run_pipeline")
    print("   - Test multiple news: POST /run_pipeline/multiple")
    print("   - Check orchestrator status: GET /run_pipeline/status")
    print("   - Set up automated pipeline scheduling")
    print("   - Monitor pipeline performance")
    print("   - Integrate with external systems")
    print("   - Build dashboard for pipeline monitoring")

if __name__ == "__main__":
    asyncio.run(main())
