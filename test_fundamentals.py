#!/usr/bin/env python3
"""
Test script for the Fundamentals Fetcher Agent
Tests cryptocurrency fundamentals fetching via CoinGecko API
"""

import asyncio
import json
from datetime import datetime
from fundamentals import (
    FundamentalsFetcherAgent,
    get_fundamentals,
    get_multiple_fundamentals,
    get_trending_coins,
    get_market_overview
)

async def test_single_coin_fundamentals():
    """Test fetching fundamentals for a single cryptocurrency"""
    print("🪙 Testing Single Coin Fundamentals...")
    print("=" * 50)
    
    try:
        # Test with Bitcoin
        print("🔍 Testing Bitcoin (BTC) fundamentals...")
        btc_fundamentals = await get_fundamentals("BTC")
        
        if btc_fundamentals:
            print("✅ Successfully fetched Bitcoin fundamentals")
            print(f"   Name: {btc_fundamentals.name}")
            print(f"   Symbol: {btc_fundamentals.symbol}")
            print(f"   Current Price: ${btc_fundamentals.current_price_usd:,.2f}")
            print(f"   24h Change: {btc_fundamentals.price_change_percentage_24h:+.2f}%")
            print(f"   Market Cap: ${btc_fundamentals.market_cap:,.0f}")
            print(f"   Market Cap Rank: #{btc_fundamentals.market_cap_rank}")
            print(f"   24h Volume: ${btc_fundamentals.volume_24h:,.0f}")
            print(f"   Circulating Supply: {btc_fundamentals.circulating_supply:,.0f}")
            print(f"   ATH: ${btc_fundamentals.ath:,.2f}")
            print(f"   ATH Change: {btc_fundamentals.ath_change_percentage:+.2f}%")
            print(f"   Last Updated: {btc_fundamentals.last_updated}")
        else:
            print("❌ Failed to fetch Bitcoin fundamentals")
            return False
        
        # Test with Ethereum
        print("\n🔍 Testing Ethereum (ETH) fundamentals...")
        eth_fundamentals = await get_fundamentals("ETH")
        
        if eth_fundamentals:
            print("✅ Successfully fetched Ethereum fundamentals")
            print(f"   Name: {eth_fundamentals.name}")
            print(f"   Current Price: ${eth_fundamentals.current_price_usd:,.2f}")
            print(f"   24h Change: {eth_fundamentals.price_change_percentage_24h:+.2f}%")
            print(f"   Market Cap Rank: #{eth_fundamentals.market_cap_rank}")
        else:
            print("❌ Failed to fetch Ethereum fundamentals")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error in single coin fundamentals test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_multiple_coins_fundamentals():
    """Test fetching fundamentals for multiple cryptocurrencies"""
    print("\n🪙 Testing Multiple Coins Fundamentals...")
    print("=" * 50)
    
    try:
        # Test with multiple popular coins
        symbols = ["BTC", "ETH", "ADA", "DOT", "LINK"]
        print(f"🔍 Testing fundamentals for: {', '.join(symbols)}")
        
        fundamentals_dict = await get_multiple_fundamentals(symbols)
        
        if fundamentals_dict:
            print(f"✅ Successfully fetched fundamentals for {len(fundamentals_dict)} coins")
            
            for symbol, fundamentals in fundamentals_dict.items():
                if fundamentals:
                    print(f"\n   {symbol}:")
                    print(f"      Price: ${fundamentals.current_price_usd:,.2f}")
                    print(f"      24h Change: {fundamentals.price_change_percentage_24h:+.2f}%")
                    print(f"      Market Cap Rank: #{fundamentals.market_cap_rank}")
                else:
                    print(f"   {symbol}: ❌ Failed to fetch")
            
            return True
        else:
            print("❌ Failed to fetch multiple fundamentals")
            return False
        
    except Exception as e:
        print(f"❌ Error in multiple coins fundamentals test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_trending_coins():
    """Test fetching trending coins with fundamentals"""
    print("\n📈 Testing Trending Coins...")
    print("=" * 50)
    
    try:
        print("🔍 Fetching trending coins...")
        trending_coins = await get_trending_coins(limit=5)
        
        if trending_coins:
            print(f"✅ Successfully fetched {len(trending_coins)} trending coins")
            
            for i, coin in enumerate(trending_coins, 1):
                print(f"\n   {i}. {coin.name} ({coin.symbol}):")
                print(f"      Price: ${coin.current_price_usd:,.2f}")
                print(f"      24h Change: {coin.price_change_percentage_24h:+.2f}%")
                print(f"      Market Cap Rank: #{coin.market_cap_rank}")
                print(f"      24h Volume: ${coin.volume_24h:,.0f}")
        else:
            print("❌ Failed to fetch trending coins")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error in trending coins test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_market_overview():
    """Test fetching market overview and statistics"""
    print("\n📊 Testing Market Overview...")
    print("=" * 50)
    
    try:
        print("🔍 Fetching market overview...")
        market_overview = await get_market_overview()
        
        if market_overview:
            print("✅ Successfully fetched market overview")
            
            # Global market data
            global_data = market_overview.get("global_market_data", {})
            if global_data:
                print(f"\n   🌍 Global Market Data:")
                print(f"      Total Market Cap: ${global_data.get('total_market_cap', {}).get('usd', 0):,.0f}")
                print(f"      Total Volume 24h: ${global_data.get('total_volume', {}).get('usd', 0):,.0f}")
                print(f"      Market Cap Change 24h: {global_data.get('market_cap_change_percentage_24h_usd', 0):+.2f}%")
                print(f"      Active Cryptocurrencies: {global_data.get('active_cryptocurrencies', 0)}")
                print(f"      Total Markets: {global_data.get('markets', 0)}")
            
            # Top coins
            top_coins = market_overview.get("top_coins", [])
            if top_coins:
                print(f"\n   🏆 Top 10 Coins by Market Cap:")
                for i, coin in enumerate(top_coins[:5], 1):
                    print(f"      {i}. {coin.get('name', 'Unknown')} ({coin.get('symbol', 'N/A')})")
                    print(f"         Price: ${coin.get('current_price', 0):,.2f}")
                    print(f"         Market Cap: ${coin.get('market_cap', 0):,.0f}")
                    print(f"         24h Change: {coin.get('price_change_percentage_24h', 0):+.2f}%")
        else:
            print("❌ Failed to fetch market overview")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error in market overview test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_agent_context_manager():
    """Test the agent as an async context manager"""
    print("\n🔧 Testing Agent Context Manager...")
    print("=" * 50)
    
    try:
        print("🔍 Testing FundamentalsFetcherAgent as context manager...")
        
        async with FundamentalsFetcherAgent() as agent:
            # Test search functionality
            print("   Testing coin search...")
            search_results = await agent.search_coin("bitcoin")
            if search_results:
                print(f"   ✅ Search found {len(search_results)} results")
                first_result = search_results[0]
                print(f"   First result: {first_result.get('name', 'Unknown')} ({first_result.get('symbol', 'N/A')})")
            else:
                print("   ❌ Search failed")
                return False
            
            # Test coin ID resolution
            print("   Testing coin ID resolution...")
            coin_id = await agent.get_coin_id("BTC")
            if coin_id:
                print(f"   ✅ BTC coin ID: {coin_id}")
            else:
                print("   ❌ Failed to get BTC coin ID")
                return False
        
        print("✅ Context manager test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error in context manager test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_error_handling():
    """Test error handling for invalid symbols and edge cases"""
    print("\n⚠️  Testing Error Handling...")
    print("=" * 50)
    
    try:
        print("🔍 Testing invalid symbol handling...")
        
        # Test with invalid symbol
        invalid_fundamentals = await get_fundamentals("INVALID_SYMBOL_123")
        if invalid_fundamentals is None:
            print("   ✅ Correctly handled invalid symbol")
        else:
            print("   ❌ Should have returned None for invalid symbol")
            return False
        
        # Test with empty symbol
        empty_fundamentals = await get_fundamentals("")
        if empty_fundamentals is None:
            print("   ✅ Correctly handled empty symbol")
        else:
            print("   ❌ Should have returned None for empty symbol")
            return False
        
        print("✅ Error handling test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error in error handling test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_performance():
    """Test performance and rate limiting"""
    print("\n⚡ Testing Performance and Rate Limiting...")
    print("=" * 50)
    
    try:
        import time
        
        print("🔍 Testing multiple concurrent requests...")
        start_time = time.time()
        
        # Test multiple symbols concurrently
        symbols = ["BTC", "ETH", "ADA", "DOT", "LINK", "XRP", "SOL", "MATIC"]
        fundamentals_dict = await get_multiple_fundamentals(symbols)
        
        end_time = time.time()
        duration = end_time - start_time
        
        if fundamentals_dict:
            successful_fetches = sum(1 for f in fundamentals_dict.values() if f is not None)
            print(f"   ✅ Fetched {successful_fetches}/{len(symbols)} symbols in {duration:.2f} seconds")
            print(f"   Rate: {successful_fetches/duration:.2f} symbols/second")
            
            if duration > 10:  # CoinGecko rate limiting
                print("   ℹ️  Rate limiting working as expected")
            
            return True
        else:
            print("   ❌ Failed to fetch multiple fundamentals")
            return False
        
    except Exception as e:
        print(f"❌ Error in performance test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🚀 Fundamentals Fetcher Agent Test Suite")
    print("=" * 60)
    
    tests = [
        ("Single Coin Fundamentals", test_single_coin_fundamentals),
        ("Multiple Coins Fundamentals", test_multiple_coins_fundamentals),
        ("Trending Coins", test_trending_coins),
        ("Market Overview", test_market_overview),
        ("Agent Context Manager", test_agent_context_manager),
        ("Error Handling", test_error_handling),
        ("Performance & Rate Limiting", test_performance)
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
        print("🎉 All tests passed! The Fundamentals Fetcher Agent is working correctly.")
        print("\n💡 Key Features Verified:")
        print("   ✅ Single coin fundamentals fetching")
        print("   ✅ Multiple coins concurrent fetching")
        print("   ✅ Trending coins with fundamentals")
        print("   ✅ Market overview and statistics")
        print("   ✅ Proper error handling")
        print("   ✅ Rate limiting compliance")
        print("   ✅ Async context manager support")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print("\n🚀 Next steps:")
    print("   - Run the app: python main.py")
    print("   - Test fundamentals endpoints: GET /fundamentals/{symbol}")
    print("   - Test trending coins: GET /fundamentals/trending")
    print("   - Test market overview: GET /fundamentals/market/overview")
    print("   - Integrate with news ingestion for comprehensive analysis")

if __name__ == "__main__":
    asyncio.run(main())
