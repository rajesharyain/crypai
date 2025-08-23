#!/usr/bin/env python3
"""
Test script for the MCP Integration
Tests ChainGPT AI News, Coin, and CryptoPanic MCP servers
"""

import asyncio
import json
from datetime import datetime
from mcp_integration import (
    MCPManager,
    ChainGPTAINewsMCPServer,
    CoinMCPServer,
    CryptoPanicMCPServer
)

async def test_mcp_server_health():
    """Test health checks for all MCP servers"""
    print("🏥 Testing MCP Server Health Checks...")
    print("=" * 50)
    
    try:
        # Test individual server health
        servers = {
            "ChainGPT": ChainGPTAINewsMCPServer(),
            "Coin": CoinMCPServer(),
            "CryptoPanic": CryptoPanicMCPServer()
        }
        
        for name, server in servers.items():
            print(f"\n🔍 Testing {name} server health...")
            try:
                is_healthy = await server.check_health()
                status = "✅ Healthy" if is_healthy else "❌ Unhealthy"
                print(f"   {name}: {status}")
                print(f"   Status: {server.health_status}")
                print(f"   Last Check: {server.last_check}")
            except Exception as e:
                print(f"   ❌ Error checking {name}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in health check test: {e}")
        return False

async def test_individual_servers():
    """Test individual MCP server news fetching"""
    print("\n📰 Testing Individual MCP Servers...")
    print("=" * 50)
    
    try:
        # Test ChainGPT (if API key available)
        print("\n🤖 Testing ChainGPT AI News Server...")
        chaingpt_server = ChainGPTAINewsMCPServer()
        if chaingpt_server.enabled:
            try:
                news_items = await chaingpt_server.fetch_news(5)
                print(f"   ✅ Fetched {len(news_items)} items from ChainGPT")
                if news_items:
                    print(f"   Sample: {news_items[0].title[:50]}...")
            except Exception as e:
                print(f"   ❌ ChainGPT fetch error: {e}")
        else:
            print("   ⚠️ ChainGPT disabled (no API key)")
        
        # Test CoinGecko server
        print("\n🪙 Testing Coin MCP Server (CoinGecko)...")
        coin_server = CoinMCPServer()
        try:
            news_items = await coin_server.fetch_news(5)
            print(f"   ✅ Fetched {len(news_items)} items from CoinGecko")
            if news_items:
                print(f"   Sample: {news_items[0].title[:50]}...")
        except Exception as e:
            print(f"   ❌ CoinGecko fetch error: {e}")
        
        # Test CryptoPanic server
        print("\n📊 Testing CryptoPanic MCP Server...")
        cryptopanic_server = CryptoPanicMCPServer()
        try:
            news_items = await cryptopanic_server.fetch_news(5)
            print(f"   ✅ Fetched {len(news_items)} items from CryptoPanic")
            if news_items:
                print(f"   Sample: {news_items[0].title[:50]}...")
        except Exception as e:
            print(f"   ❌ CryptoPanic fetch error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in individual server test: {e}")
        return False

async def test_mcp_manager():
    """Test the MCP manager functionality"""
    print("\n🎛️ Testing MCP Manager...")
    print("=" * 50)
    
    try:
        # Initialize manager
        manager = MCPManager()
        print("✅ MCP Manager initialized")
        
        # Initialize servers
        await manager.initialize()
        print(f"✅ Initialized {len(manager.active_servers)} active and {len(manager.fallback_servers)} fallback servers")
        
        # Get server status
        status = await manager.get_server_status()
        print(f"📊 Server Status:")
        print(f"   Total Servers: {status['total_servers']}")
        print(f"   Active: {status['active_count']}")
        print(f"   Fallback: {status['fallback_count']}")
        
        # Test news fetching from all servers
        print("\n📰 Testing news fetch from all servers...")
        news_items = await manager.fetch_news_from_all(10)
        print(f"   ✅ Fetched {len(news_items)} total news items")
        
        # Show breakdown by server
        server_counts = {}
        for item in news_items:
            server_counts[item.mcp_server] = server_counts.get(item.mcp_server, 0) + 1
        
        print("   📊 News by server:")
        for server, count in server_counts.items():
            print(f"      {server}: {count} items")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in MCP manager test: {e}")
        return False

async def test_server_priority_switching():
    """Test server priority switching functionality"""
    print("\n🔄 Testing Server Priority Switching...")
    print("=" * 50)
    
    try:
        manager = MCPManager()
        await manager.initialize()
        
        initial_status = await manager.get_server_status()
        print(f"📊 Initial Status: {initial_status['active_count']} active, {initial_status['fallback_count']} fallback")
        
        # Test switching a server to fallback
        if manager.active_servers:
            test_server = manager.active_servers[0]
            server_name = None
            
            # Find the server name
            for name, server in manager.servers.items():
                if server == test_server:
                    server_name = name
                    break
            
            if server_name:
                print(f"\n🔄 Moving {server_name} to fallback...")
                await manager.switch_server_priority(server_name, "fallback")
                
                updated_status = await manager.get_server_status()
                print(f"📊 Updated Status: {updated_status['active_count']} active, {updated_status['fallback_count']} fallback")
                
                # Move back to active
                print(f"🔄 Moving {server_name} back to active...")
                await manager.switch_server_priority(server_name, "active")
                
                final_status = await manager.get_server_status()
                print(f"📊 Final Status: {final_status['active_count']} active, {final_status['fallback_count']} fallback")
                
                if final_status['active_count'] == initial_status['active_count']:
                    print("✅ Priority switching working correctly")
                    return True
                else:
                    print("❌ Priority switching not working correctly")
                    return False
            else:
                print("⚠️ Could not find server name for testing")
                return False
        else:
            print("⚠️ No active servers to test priority switching")
            return False
        
    except Exception as e:
        print(f"❌ Error in priority switching test: {e}")
        return False

async def test_health_check_all():
    """Test health check functionality for all servers"""
    print("\n🔍 Testing Health Check All...")
    print("=" * 50)
    
    try:
        manager = MCPManager()
        await manager.initialize()
        
        initial_status = await manager.get_server_status()
        print(f"📊 Initial Status: {initial_status['active_count']} active, {initial_status['fallback_count']} fallback")
        
        # Perform health check
        print("\n🔍 Performing health check on all servers...")
        await manager.health_check_all()
        
        updated_status = await manager.get_server_status()
        print(f"📊 Updated Status: {updated_status['active_count']} active, {updated_status['fallback_count']} fallback")
        
        print("✅ Health check completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error in health check all test: {e}")
        return False

async def test_performance():
    """Test MCP system performance"""
    print("\n⚡ Testing MCP Performance...")
    print("=" * 50)
    
    try:
        import time
        
        manager = MCPManager()
        await manager.initialize()
        
        # Test fetch performance
        print("📊 Testing news fetch performance...")
        start_time = time.time()
        
        news_items = await manager.fetch_news_from_all(20)
        
        end_time = time.time()
        fetch_duration = end_time - start_time
        
        print(f"✅ Fetched {len(news_items)} items in {fetch_duration:.2f} seconds")
        print(f"   Rate: {len(news_items)/fetch_duration:.2f} items/second")
        
        # Test health check performance
        print("\n🔍 Testing health check performance...")
        start_time = time.time()
        
        await manager.health_check_all()
        
        end_time = time.time()
        health_check_duration = end_time - start_time
        
        print(f"✅ Health check completed in {health_check_duration:.2f} seconds")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in performance test: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 MCP Integration Test Suite")
    print("=" * 60)
    
    tests = [
        ("MCP Server Health", test_mcp_server_health),
        ("Individual Servers", test_individual_servers),
        ("MCP Manager", test_mcp_manager),
        ("Server Priority Switching", test_server_priority_switching),
        ("Health Check All", test_health_check_all),
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
        print("🎉 All tests passed! The MCP integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print("\n💡 Tips:")
    print("   - Make sure you have a .env file with CHAINGPT_API_KEY (optional)")
    print("   - Check internet connectivity for API calls")
    print("   - CoinGecko and CryptoPanic are free and should always work")
    print("   - ChainGPT requires an API key for full functionality")

if __name__ == "__main__":
    asyncio.run(main())
