#!/usr/bin/env python3
"""
Test script for fundamentals agent fixes
"""

import asyncio
from fundamentals import FundamentalsFetcherAgent

async def test_fundamentals_fix():
    """Test the fundamentals agent fixes"""
    
    print("🧪 Testing Fundamentals Agent Fixes")
    print("=" * 40)
    
    try:
        async with FundamentalsFetcherAgent() as agent:
            
            # Test symbol validation
            print("\n🔍 Testing Symbol Validation")
            test_symbols = ['SUI', 'BTC', 'STABLECOIN', 'BINANCE']
            
            for symbol in test_symbols:
                is_valid = await agent.is_valid_symbol(symbol)
                print(f"  {symbol}: {'✅ Valid' if is_valid else '❌ Invalid'}")
            
            # Test fundamentals fetching for SUI
            print(f"\n💰 Testing Fundamentals for SUI")
            fundamentals = await agent.get_fundamentals('SUI')
            
            if fundamentals:
                print(f"✅ SUI fundamentals: ${fundamentals.current_price_usd}")
                print(f"   Market Cap Rank: {fundamentals.market_cap_rank}")
                print(f"   24h Change: {fundamentals.price_change_percentage_24h}%")
            else:
                print("❌ Failed to get SUI fundamentals")
        
        print("\n🎉 Fundamentals agent test completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_fundamentals_fix())
