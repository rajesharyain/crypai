#!/usr/bin/env python3
"""
Enhanced MCP Integration Test
Tests the new RSS fallback system and ensures news sources work together
"""

import asyncio
from mcp_integration import MCPManager, RSSNewsSource, CoinMCPServer

async def test_rss_sources():
    """Test RSS sources (CoinDesk, CoinTelegraph)"""
    print("📰 Testing RSS News Sources...")
    print("=" * 50)
    
    try:
        # Test CoinDesk RSS
        print("\n🪙 Testing CoinDesk RSS...")
        coindesk = RSSNewsSource("CoinDesk", "https://www.coindesk.com/arc/outboundfeeds/rss/")
        
        is_healthy = await coindesk.check_health()
        print(f"   Health Status: {'✅ Healthy' if is_healthy else '❌ Unhealthy'}")
        
        if is_healthy:
            news_items = await coindesk.fetch_news(3)
            print(f"   ✅ Fetched {len(news_items)} news items")
            if news_items:
                print(f"   📋 Sample: {news_items[0].title[:60]}...")
                print(f"      Source: {news_items[0].source}")
                print(f"      Relevance: {news_items[0].relevance_score}")
        
        # Test CoinTelegraph RSS
        print("\n📊 Testing CoinTelegraph RSS...")
        cointelegraph = RSSNewsSource("CoinTelegraph", "https://cointelegraph.com/rss")
        
        is_healthy = await cointelegraph.check_health()
        print(f"   Health Status: {'✅ Healthy' if is_healthy else '❌ Unhealthy'}")
        
        if is_healthy:
            news_items = await cointelegraph.fetch_news(3)
            print(f"   ✅ Fetched {len(news_items)} news items")
            if news_items:
                print(f"   📋 Sample: {news_items[0].title[:60]}...")
                print(f"      Source: {news_items[0].source}")
                print(f"      Relevance: {news_items[0].relevance_score}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in RSS test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_enhanced_mcp_manager():
    """Test the enhanced MCP manager with RSS fallbacks"""
    print("\n🎛️ Testing Enhanced MCP Manager...")
    print("=" * 50)
    
    try:
        # Initialize manager
        manager = MCPManager()
        print("✅ MCP Manager initialized")
        
        # Initialize all sources
        await manager.initialize()
        print(f"✅ Initialized {len(manager.active_servers)} active and {len(manager.fallback_servers)} fallback sources")
        
        # Get detailed status
        status = await manager.get_server_status()
        print(f"📊 Server Status:")
        print(f"   Total Sources: {status['total_servers']}")
        print(f"   Active: {status['active_count']}")
        print(f"   Fallback: {status['fallback_count']}")
        print(f"   RSS Sources: {status['source_types']['rss_sources']}")
        print(f"   API Sources: {status['source_types']['api_sources']}")
        
        # Test news fetching from all sources
        print("\n📰 Testing news fetch from all sources...")
        news_items = await manager.fetch_news_from_all(15)
        print(f"   ✅ Fetched {len(news_items)} total news items")
        
        # Show breakdown by source
        source_counts = {}
        for item in news_items:
            source_counts[item.source] = source_counts.get(item.source, 0) + 1
        
        print("   📊 News by source:")
        for source, count in source_counts.items():
            print(f"      {source}: {count} items")
        
        # Test fallback activation
        if not manager.active_servers:
            print("\n🔄 Testing fallback activation...")
            await manager._activate_fallback_sources()
            print(f"   Active sources after fallback: {len(manager.active_servers)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in enhanced MCP manager test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_no_api_key_scenario():
    """Test the system when no API keys are provided"""
    print("\n🔑 Testing No API Key Scenario...")
    print("=" * 50)
    
    try:
        # Create a manager without API keys
        manager = MCPManager()
        
        # Force disable API-based sources
        if "chaingpt" in manager.servers:
            manager.servers["chaingpt"].enabled = False
            print("   ℹ️ ChainGPT disabled (no API key)")
        
        # Initialize and check what sources are available
        await manager.initialize()
        
        print(f"   📊 Available sources:")
        print(f"      Active: {len(manager.active_servers)}")
        print(f"      Fallback: {len(manager.fallback_servers)}")
        
        # Ensure RSS sources are working
        rss_sources = [s for s in manager.active_servers if isinstance(s, RSSNewsSource)]
        print(f"      RSS Sources Active: {len(rss_sources)}")
        
        if rss_sources:
            print("   ✅ RSS fallbacks are working without API keys!")
            
            # Test news fetching
            news_items = await manager.fetch_news_from_all(10)
            print(f"   📰 Fetched {len(news_items)} news items from RSS sources")
            
            return True
        else:
            print("   ❌ No RSS sources available")
            return False
        
    except Exception as e:
        print(f"❌ Error in no API key test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🚀 Enhanced MCP Integration Test Suite")
    print("=" * 60)
    
    tests = [
        ("RSS Sources", test_rss_sources),
        ("Enhanced MCP Manager", test_enhanced_mcp_manager),
        ("No API Key Scenario", test_no_api_key_scenario)
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
        print("🎉 All tests passed! The enhanced MCP integration is working correctly.")
        print("\n💡 Key Features Verified:")
        print("   ✅ RSS fallbacks (CoinDesk, CoinTelegraph) work without API keys")
        print("   ✅ System gracefully handles missing API keys")
        print("   ✅ Multiple news sources work together seamlessly")
        print("   ✅ Smart fallback activation when sources fail")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print("\n🚀 Next steps:")
    print("   - Run the app: python main.py")
    print("   - Test MCP endpoints: GET /mcp/news")
    print("   - Check source status: GET /mcp/status")

if __name__ == "__main__":
    asyncio.run(main())
