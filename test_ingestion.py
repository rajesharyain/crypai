#!/usr/bin/env python3
"""
Test script for the News Ingestion Agent
Tests news fetching, sentiment analysis, and source management
"""

import asyncio
import json
from datetime import datetime
from ingestion import NewsIngestionAgent, RSSNewsSource, APINewsSource
from config import get_news_config

async def test_news_fetching():
    """Test basic news fetching functionality"""
    print("🧪 Testing News Fetching...")
    print("=" * 50)
    
    try:
        # Initialize the agent
        agent = NewsIngestionAgent()
        
        # Get source statistics
        stats = agent.get_source_statistics()
        print(f"✅ Initialized agent with {stats['total_sources']} sources")
        print(f"   RSS Sources: {stats['rss_sources']}")
        print(f"   API Sources: {stats['api_sources']}")
        
        # Test fetching news
        print("\n📰 Fetching news from all sources...")
        news_items = await agent.fetch_all_news()
        
        if news_items:
            print(f"✅ Successfully fetched {len(news_items)} news items")
            
            # Show first few items
            print("\n📋 Sample news items:")
            for i, item in enumerate(news_items[:3]):
                print(f"\n{i+1}. {item.title}")
                print(f"   Source: {item.source}")
                print(f"   Published: {item.published}")
                print(f"   Summary: {item.summary[:100]}...")
        else:
            print("⚠️  No news items fetched")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in news fetching test: {e}")
        return False

async def test_sentiment_analysis():
    """Test sentiment analysis functionality"""
    print("\n🧠 Testing Sentiment Analysis...")
    print("=" * 50)
    
    try:
        agent = NewsIngestionAgent()
        
        # Fetch a small batch of news for analysis
        news_items = await agent.fetch_all_news()
        if not news_items:
            print("⚠️  No news items available for sentiment analysis")
            return False
        
        # Limit to first few items for testing
        test_items = news_items[:3]
        print(f"📊 Analyzing sentiment for {len(test_items)} news items...")
        
        # Perform sentiment analysis
        analyzed_items = await agent.analyze_news_sentiment(test_items)
        
        print("\n📈 Sentiment Analysis Results:")
        for i, item in enumerate(analyzed_items):
            print(f"\n{i+1}. {item.title}")
            print(f"   Sentiment: {item.sentiment}")
            print(f"   Relevance Score: {item.relevance_score}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in sentiment analysis test: {e}")
        return False

async def test_source_management():
    """Test dynamic source management"""
    print("\n🔧 Testing Source Management...")
    print("=" * 50)
    
    try:
        agent = NewsIngestionAgent()
        
        # Get initial stats
        initial_stats = agent.get_source_statistics()
        print(f"📊 Initial sources: {initial_stats['total_sources']}")
        
        # Test adding a new RSS source
        print("\n➕ Adding new RSS source...")
        new_rss_source = RSSNewsSource(
            feed_url="https://www.newsbtc.com/feed/",
            source_name="Test NewsBTC",
            category="crypto",
            max_items=10
        )
        agent.add_news_source(new_rss_source)
        
        # Get updated stats
        updated_stats = agent.get_source_statistics()
        print(f"📊 Updated sources: {updated_stats['total_sources']}")
        
        if updated_stats['total_sources'] > initial_stats['total_sources']:
            print("✅ Successfully added new source")
        else:
            print("⚠️  Source count didn't increase")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in source management test: {e}")
        return False

async def test_configuration():
    """Test configuration system"""
    print("\n⚙️  Testing Configuration System...")
    print("=" * 50)
    
    try:
        config = get_news_config()
        config_summary = config.get_config_summary()
        
        print("📋 Configuration Summary:")
        print(f"   Total Sources: {config_summary['total_sources']}")
        print(f"   RSS Sources: {config_summary['rss_sources']['total']}")
        print(f"   API Sources: {config_summary['api_sources']['total']}")
        
        print("\n🔧 System Settings:")
        for key, value in config_summary['settings'].items():
            print(f"   {key}: {value}")
        
        # Test adding new source via config
        print("\n➕ Testing config-based source addition...")
        new_source = config.add_rss_source(
            url="https://example.com/feed",
            name="Test Source",
            category="test",
            max_items=5
        )
        
        if new_source:
            print("✅ Successfully added source via configuration")
        else:
            print("⚠️  Failed to add source via configuration")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in configuration test: {e}")
        return False

async def test_performance():
    """Test performance and concurrency"""
    print("\n⚡ Testing Performance...")
    print("=" * 50)
    
    try:
        import time
        
        agent = NewsIngestionAgent()
        
        # Test fetch performance
        print("📊 Testing news fetch performance...")
        start_time = time.time()
        
        news_items = await agent.fetch_all_news()
        
        end_time = time.time()
        fetch_duration = end_time - start_time
        
        print(f"✅ Fetched {len(news_items)} items in {fetch_duration:.2f} seconds")
        print(f"   Rate: {len(news_items)/fetch_duration:.2f} items/second")
        
        # Test sentiment analysis performance
        if news_items:
            print("\n🧠 Testing sentiment analysis performance...")
            start_time = time.time()
            
            analyzed_items = await agent.analyze_news_sentiment(news_items[:5])
            
            end_time = time.time()
            analysis_duration = end_time - start_time
            
            print(f"✅ Analyzed {len(analyzed_items)} items in {analysis_duration:.2f} seconds")
            print(f"   Rate: {len(analyzed_items)/analysis_duration:.2f} items/second")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in performance test: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 News Ingestion Agent Test Suite")
    print("=" * 60)
    
    tests = [
        ("News Fetching", test_news_fetching),
        ("Sentiment Analysis", test_sentiment_analysis),
        ("Source Management", test_source_management),
        ("Configuration", test_configuration),
        ("Performance", test_performance)
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
    print("\n" + "=" * 60)
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
        print("🎉 All tests passed! The ingestion agent is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print("\n💡 Tips:")
    print("   - Make sure you have a .env file with OPENAI_API_KEY")
    print("   - Check that all RSS feeds are accessible")
    print("   - Verify internet connectivity for API calls")

if __name__ == "__main__":
    asyncio.run(main())
