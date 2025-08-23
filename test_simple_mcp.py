#!/usr/bin/env python3
"""
Simple test script for MCP Integration
Tests basic functionality without complex dependencies
"""

import asyncio
from mcp_integration import MCPManager, CoinMCPServer

async def test_basic_mcp():
    """Test basic MCP functionality"""
    print("🧪 Testing Basic MCP Integration...")
    print("=" * 50)
    
    try:
        # Test CoinGecko server (should always work)
        print("🪙 Testing CoinGecko MCP Server...")
        coin_server = CoinMCPServer()
        
        # Check health
        is_healthy = await coin_server.check_health()
        print(f"   Health Status: {'✅ Healthy' if is_healthy else '❌ Unhealthy'}")
        
        if is_healthy:
            # Fetch some news
            print("   Fetching news...")
            news_items = await coin_server.fetch_news(3)
            print(f"   ✅ Fetched {len(news_items)} news items")
            
            if news_items:
                print("   📋 Sample news:")
                for i, item in enumerate(news_items[:2]):
                    print(f"      {i+1}. {item.title[:60]}...")
                    print(f"         Source: {item.source}")
                    print(f"         Relevance: {item.relevance_score}")
        else:
            print("   ⚠️ Server unhealthy, skipping news fetch")
        
        # Test MCP Manager
        print("\n🎛️ Testing MCP Manager...")
        manager = MCPManager()
        await manager.initialize()
        
        status = await manager.get_server_status()
        print(f"   Total Servers: {status['total_servers']}")
        print(f"   Active: {status['active_count']}")
        print(f"   Fallback: {status['fallback_count']}")
        
        print("\n✅ Basic MCP test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error in basic MCP test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🚀 Simple MCP Integration Test")
    print("=" * 40)
    
    try:
        result = await test_basic_mcp()
        
        if result:
            print("\n🎉 MCP integration is working correctly!")
            print("\n💡 Next steps:")
            print("   - Test with: python test_mcp.py")
            print("   - Run the app: python main.py")
            print("   - Access MCP endpoints: GET /mcp/news")
        else:
            print("\n⚠️ MCP integration has issues. Check the error above.")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
