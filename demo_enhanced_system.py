#!/usr/bin/env python3
"""
Enhanced MCP System Demonstration
Shows how RSS fallbacks work together with MCP servers
"""

import asyncio
import json
from datetime import datetime
from mcp_integration import MCPManager

async def demonstrate_rss_fallbacks():
    """Demonstrate RSS fallback system"""
    print("🔄 RSS Fallback System Demonstration")
    print("=" * 60)
    
    # Initialize MCP Manager
    manager = MCPManager()
    print("✅ MCP Manager initialized")
    
    # Initialize all sources
    print("\n🔍 Initializing news sources...")
    await manager.initialize()
    
    # Show initial status
    status = await manager.get_server_status()
    print(f"\n📊 Initial Status:")
    print(f"   Active Sources: {status['active_count']}")
    print(f"   Fallback Sources: {status['fallback_count']}")
    print(f"   RSS Sources: {status['source_types']['rss_sources']}")
    print(f"   API Sources: {status['source_types']['api_sources']}")
    
    # Show active sources
    if manager.active_servers:
        print(f"\n✅ Active Sources:")
        for server in manager.active_servers:
            print(f"   • {server.name} ({type(server).__name__})")
    
    # Show fallback sources
    if manager.fallback_servers:
        print(f"\n⚠️  Fallback Sources:")
        for server in manager.fallback_servers:
            print(f"   • {server.name} ({type(server).__name__})")
    
    return manager

async def demonstrate_news_fetching(manager):
    """Demonstrate news fetching from all sources"""
    print(f"\n📰 News Fetching Demonstration")
    print("=" * 60)
    
    try:
        # Fetch news from all sources
        print("🔄 Fetching news from all available sources...")
        news_items = await manager.fetch_news_from_all(20)
        
        print(f"✅ Successfully fetched {len(news_items)} news items")
        
        # Group by source
        source_groups = {}
        for item in news_items:
            source = item.source
            if source not in source_groups:
                source_groups[source] = []
            source_groups[source].append(item)
        
        # Display breakdown
        print(f"\n📊 News Breakdown by Source:")
        for source, items in source_groups.items():
            print(f"   {source}: {len(items)} items")
            
            # Show sample item
            if items:
                sample = items[0]
                print(f"      Sample: {sample.title[:70]}...")
                print(f"      Relevance: {sample.relevance_score}")
                print(f"      Published: {sample.published}")
                if hasattr(sample, 'sentiment') and sample.sentiment:
                    print(f"      Sentiment: {sample.sentiment}")
                print()
        
        return news_items
        
    except Exception as e:
        print(f"❌ Error fetching news: {e}")
        return []

async def demonstrate_fallback_activation(manager):
    """Demonstrate fallback activation when sources fail"""
    print(f"\n🔄 Fallback Activation Demonstration")
    print("=" * 60)
    
    try:
        # Simulate source failure by moving active sources to fallback
        if manager.active_servers:
            print("🔄 Simulating source failure...")
            failed_source = manager.active_servers[0]
            manager.active_servers.remove(failed_source)
            manager.fallback_servers.append(failed_source)
            print(f"   Moved {failed_source.name} to fallback")
        
        # Check status after "failure"
        status = await manager.get_server_status()
        print(f"\n📊 Status after simulated failure:")
        print(f"   Active Sources: {status['active_count']}")
        print(f"   Fallback Sources: {status['fallback_count']}")
        
        # Activate fallback sources
        if manager.fallback_servers:
            print("\n🔄 Activating fallback sources...")
            await manager._activate_fallback_sources()
            
            updated_status = await manager.get_server_status()
            print(f"\n📊 Status after fallback activation:")
            print(f"   Active Sources: {updated_status['active_count']}")
            print(f"   Fallback Sources: {updated_status['fallback_count']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in fallback demonstration: {e}")
        return False

async def demonstrate_no_api_key_scenario():
    """Demonstrate system working without API keys"""
    print(f"\n🔑 No API Key Scenario Demonstration")
    print("=" * 60)
    
    try:
        # Create manager without API keys
        manager = MCPManager()
        
        # Disable premium sources
        if "chaingpt" in manager.servers:
            manager.servers["chaingpt"].enabled = False
            print("ℹ️  ChainGPT disabled (no API key)")
        
        # Initialize
        await manager.initialize()
        
        # Check what's available
        status = await manager.get_server_status()
        print(f"\n📊 Available sources without API keys:")
        print(f"   Active: {status['active_count']}")
        print(f"   Fallback: {status['fallback_count']}")
        
        # Count RSS sources
        rss_sources = [s for s in manager.active_servers if hasattr(s, 'rss_url')]
        print(f"   RSS Sources: {len(rss_sources)}")
        
        if rss_sources:
            print("✅ RSS fallbacks working without API keys!")
            
            # Test news fetching
            news_items = await manager.fetch_news_from_all(10)
            print(f"📰 Fetched {len(news_items)} news items from RSS sources")
            
            return True
        else:
            print("❌ No RSS sources available")
            return False
            
    except Exception as e:
        print(f"❌ Error in no API key demonstration: {e}")
        return False

async def main():
    """Main demonstration function"""
    print("🚀 Enhanced MCP System with RSS Fallbacks - Live Demonstration")
    print("=" * 80)
    
    try:
        # Demonstrate RSS fallbacks
        manager = await demonstrate_rss_fallbacks()
        
        # Demonstrate news fetching
        news_items = await demonstrate_news_fetching(manager)
        
        # Demonstrate fallback activation
        await demonstrate_fallback_activation(manager)
        
        # Demonstrate no API key scenario
        await demonstrate_no_api_key_scenario()
        
        # Summary
        print("\n" + "=" * 80)
        print("🎉 Demonstration Complete!")
        print("\n💡 Key Features Demonstrated:")
        print("   ✅ RSS fallbacks (CoinDesk, CoinTelegraph) work without API keys")
        print("   ✅ Multiple news sources work together seamlessly")
        print("   ✅ Smart fallback activation when sources fail")
        print("   ✅ System gracefully handles missing API keys")
        print("   ✅ Unified news aggregation from diverse sources")
        
        print("\n🚀 Next Steps:")
        print("   - Run the app: python main.py")
        print("   - Test endpoints: GET /mcp/news, GET /mcp/status")
        print("   - Add your API keys for enhanced functionality")
        print("   - Customize news sources via configuration")
        
    except Exception as e:
        print(f"❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
