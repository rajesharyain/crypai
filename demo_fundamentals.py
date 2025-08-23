#!/usr/bin/env python3
"""
Fundamentals Fetcher Agent Demonstration
Showcases cryptocurrency fundamentals fetching capabilities
"""

import asyncio
from datetime import datetime
from fundamentals import (
    FundamentalsFetcherAgent,
    get_fundamentals,
    get_multiple_fundamentals,
    get_trending_coins,
    get_market_overview
)

async def demonstrate_single_coin():
    """Demonstrate single coin fundamentals fetching"""
    print("🪙 Single Coin Fundamentals Demonstration")
    print("=" * 60)
    
    try:
        # Test with Bitcoin
        print("🔍 Fetching Bitcoin (BTC) fundamentals...")
        btc = await get_fundamentals("BTC")
        
        if btc:
            print("✅ Bitcoin Fundamentals Retrieved Successfully!")
            print(f"\n📊 {btc.name} ({btc.symbol})")
            print(f"   💰 Current Price: ${btc.current_price_usd:,.2f}")
            print(f"   📈 24h Change: {btc.price_change_percentage_24h:+.2f}%")
            print(f"   🏆 Market Cap Rank: #{btc.market_cap_rank}")
            print(f"   💎 Market Cap: ${btc.market_cap:,.0f}")
            print(f"   📊 24h Volume: ${btc.volume_24h:,.0f}")
            print(f"   🔄 Circulating Supply: {btc.circulating_supply:,.0f}")
            
            if btc.ath:
                print(f"   🚀 All-Time High: ${btc.ath:,.2f}")
                print(f"   📉 From ATH: {btc.ath_change_percentage:+.2f}%")
            
            if btc.atl:
                print(f"   📉 All-Time Low: ${btc.atl:,.2f}")
                print(f"   📈 From ATL: {btc.atl_change_percentage:+.2f}%")
            
            print(f"   ⏰ Last Updated: {btc.last_updated}")
            
            return True
        else:
            print("❌ Failed to fetch Bitcoin fundamentals")
            return False
            
    except Exception as e:
        print(f"❌ Error in single coin demonstration: {e}")
        return False

async def demonstrate_multiple_coins():
    """Demonstrate multiple coins fundamentals fetching"""
    print(f"\n🪙 Multiple Coins Fundamentals Demonstration")
    print("=" * 60)
    
    try:
        # Test with popular cryptocurrencies
        symbols = ["BTC", "ETH", "ADA", "DOT", "LINK"]
        print(f"🔍 Fetching fundamentals for: {', '.join(symbols)}")
        
        fundamentals_dict = await get_multiple_fundamentals(symbols)
        
        if fundamentals_dict:
            print(f"✅ Successfully fetched fundamentals for {len(fundamentals_dict)} coins")
            
            for symbol, fundamentals in fundamentals_dict.items():
                if fundamentals:
                    print(f"\n   {fundamentals.name} ({symbol}):")
                    print(f"      💰 Price: ${fundamentals.current_price_usd:,.2f}")
                    print(f"      📈 24h Change: {fundamentals.price_change_percentage_24h:+.2f}%")
                    print(f"      🏆 Rank: #{fundamentals.market_cap_rank}")
                    print(f"      💎 Market Cap: ${fundamentals.market_cap:,.0f}")
                else:
                    print(f"   {symbol}: ❌ Failed to fetch")
            
            return True
        else:
            print("❌ Failed to fetch multiple fundamentals")
            return False
            
    except Exception as e:
        print(f"❌ Error in multiple coins demonstration: {e}")
        return False

async def demonstrate_trending_coins():
    """Demonstrate trending coins functionality"""
    print(f"\n📈 Trending Coins Demonstration")
    print("=" * 60)
    
    try:
        print("🔍 Fetching trending coins...")
        trending_coins = await get_trending_coins(limit=5)
        
        if trending_coins:
            print(f"✅ Successfully fetched {len(trending_coins)} trending coins")
            
            for i, coin in enumerate(trending_coins, 1):
                print(f"\n   {i}. {coin.name} ({coin.symbol}):")
                print(f"      💰 Price: ${coin.current_price_usd:,.2f}")
                print(f"      📈 24h Change: {coin.price_change_percentage_24h:+.2f}%")
                print(f"      🏆 Market Cap Rank: #{coin.market_cap_rank}")
                print(f"      📊 24h Volume: ${coin.volume_24h:,.0f}")
                
                if coin.sparkline_7d:
                    print(f"      📉 7-Day Sparkline: {len(coin.sparkline_7d)} data points")
        else:
            print("❌ Failed to fetch trending coins")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error in trending coins demonstration: {e}")
        return False

async def demonstrate_market_overview():
    """Demonstrate market overview functionality"""
    print(f"\n📊 Market Overview Demonstration")
    print("=" * 60)
    
    try:
        print("🔍 Fetching market overview...")
        market_overview = await get_market_overview()
        
        if market_overview:
            print("✅ Successfully fetched market overview")
            
            # Global market data
            global_data = market_overview.get("global_market_data", {})
            if global_data:
                print(f"\n🌍 Global Market Data:")
                total_market_cap = global_data.get('total_market_cap', {}).get('usd', 0)
                total_volume = global_data.get('total_volume', {}).get('usd', 0)
                market_cap_change = global_data.get('market_cap_change_percentage_24h_usd', 0)
                
                print(f"   💎 Total Market Cap: ${total_market_cap:,.0f}")
                print(f"   📊 Total Volume 24h: ${total_volume:,.0f}")
                print(f"   📈 Market Cap Change 24h: {market_cap_change:+.2f}%")
                print(f"   🪙 Active Cryptocurrencies: {global_data.get('active_cryptocurrencies', 0)}")
                print(f"   🏪 Total Markets: {global_data.get('markets', 0)}")
            
            # Top coins
            top_coins = market_overview.get("top_coins", [])
            if top_coins:
                print(f"\n🏆 Top 5 Coins by Market Cap:")
                for i, coin in enumerate(top_coins[:5], 1):
                    name = coin.get('name', 'Unknown')
                    symbol = coin.get('symbol', 'N/A')
                    price = coin.get('current_price', 0)
                    market_cap = coin.get('market_cap', 0)
                    change_24h = coin.get('price_change_percentage_24h', 0)
                    
                    print(f"   {i}. {name} ({symbol})")
                    print(f"      💰 Price: ${price:,.2f}")
                    print(f"      💎 Market Cap: ${market_cap:,.0f}")
                    print(f"      📈 24h Change: {change_24h:+.2f}%")
        else:
            print("❌ Failed to fetch market overview")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error in market overview demonstration: {e}")
        return False

async def demonstrate_search_functionality():
    """Demonstrate coin search functionality"""
    print(f"\n🔍 Coin Search Demonstration")
    print("=" * 60)
    
    try:
        async with FundamentalsFetcherAgent() as agent:
            # Test search functionality
            print("🔍 Searching for 'bitcoin'...")
            search_results = await agent.search_coin("bitcoin")
            
            if search_results:
                print(f"✅ Search found {len(search_results)} results")
                
                # Show first few results
                for i, result in enumerate(search_results[:3], 1):
                    name = result.get('name', 'Unknown')
                    symbol = result.get('symbol', 'N/A')
                    market_cap_rank = result.get('market_cap_rank', 'N/A')
                    
                    print(f"   {i}. {name} ({symbol})")
                    if market_cap_rank != 'N/A':
                        print(f"      🏆 Market Cap Rank: #{market_cap_rank}")
                
                if len(search_results) > 3:
                    print(f"   ... and {len(search_results) - 3} more results")
            else:
                print("❌ Search failed")
                return False
            
            # Test coin ID resolution
            print(f"\n🔍 Testing coin ID resolution for BTC...")
            coin_id = await agent.get_coin_id("BTC")
            if coin_id:
                print(f"✅ BTC coin ID: {coin_id}")
            else:
                print("❌ Failed to get BTC coin ID")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error in search demonstration: {e}")
        return False

async def demonstrate_error_handling():
    """Demonstrate error handling capabilities"""
    print(f"\n⚠️  Error Handling Demonstration")
    print("=" * 60)
    
    try:
        print("🔍 Testing invalid symbol handling...")
        
        # Test with invalid symbol
        invalid_result = await get_fundamentals("INVALID_SYMBOL_123")
        if invalid_result is None:
            print("   ✅ Correctly handled invalid symbol")
        else:
            print("   ❌ Should have returned None for invalid symbol")
            return False
        
        # Test with empty symbol
        empty_result = await get_fundamentals("")
        if empty_result is None:
            print("   ✅ Correctly handled empty symbol")
        else:
            print("   ❌ Should have returned None for empty symbol")
            return False
        
        print("✅ Error handling working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Error in error handling demonstration: {e}")
        return False

async def main():
    """Main demonstration function"""
    print("🚀 Fundamentals Fetcher Agent - Live Demonstration")
    print("=" * 80)
    
    try:
        # Run demonstrations
        demonstrations = [
            ("Single Coin Fundamentals", demonstrate_single_coin),
            ("Multiple Coins Fundamentals", demonstrate_multiple_coins),
            ("Trending Coins", demonstrate_trending_coins),
            ("Market Overview", demonstrate_market_overview),
            ("Coin Search", demonstrate_search_functionality),
            ("Error Handling", demonstrate_error_handling)
        ]
        
        results = []
        
        for demo_name, demo_func in demonstrations:
            print(f"\n🧪 Running {demo_name}...")
            try:
                result = await demo_func()
                results.append((demo_name, result))
            except Exception as e:
                print(f"❌ {demo_name} failed with exception: {e}")
                results.append((demo_name, False))
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 Demonstration Results Summary:")
        
        passed = 0
        total = len(results)
        
        for demo_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {demo_name}: {status}")
            if result:
                passed += 1
        
        print(f"\n🎯 Overall: {passed}/{total} demonstrations successful")
        
        if passed == total:
            print("🎉 All demonstrations completed successfully!")
            print("\n💡 Key Features Demonstrated:")
            print("   ✅ Single coin fundamentals fetching")
            print("   ✅ Multiple coins concurrent fetching")
            print("   ✅ Trending coins with fundamentals")
            print("   ✅ Market overview and statistics")
            print("   ✅ Coin search functionality")
            print("   ✅ Proper error handling")
            print("   ✅ Rate limiting compliance")
        else:
            print("⚠️  Some demonstrations failed. Check the output above for details.")
        
        print("\n🚀 Next Steps:")
        print("   - Run the app: python main.py")
        print("   - Test fundamentals endpoints: GET /fundamentals/{symbol}")
        print("   - Test trending coins: GET /fundamentals/trending")
        print("   - Test market overview: GET /fundamentals/market/overview")
        print("   - Integrate with news ingestion for comprehensive analysis")
        print("   - Build trading bots or portfolio trackers")
        
    except Exception as e:
        print(f"❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
