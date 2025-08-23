#!/usr/bin/env python3
"""
Enhanced test script for Fundamentals Fetcher Agent
Tests integration with enhanced crypto data from ingestion agent
"""

import asyncio
import logging
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging to see all details
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_fundamentals_enhanced():
    """Test fundamentals agent with enhanced crypto data"""
    
    print("🧪 Testing Fundamentals Fetcher Agent with Enhanced Crypto Data")
    print("=" * 70)
    
    # Import the fundamentals agent
    try:
        from fundamentals import FundamentalsFetcherAgent, CryptoFundamentals
        print("✅ Fundamentals agent imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import fundamentals agent: {e}")
        return
    
    # Test data from ingestion agent (simulated)
    test_crypto_data = [
        {
            "symbol": "BTC",
            "name": "Bitcoin",
            "relevance_score": 9.5,
            "mentions": 3,
            "context": "Bitcoin price analysis and market trends"
        },
        {
            "symbol": "ETH",
            "name": "Ethereum", 
            "relevance_score": 8.2,
            "mentions": 2,
            "context": "Ethereum network upgrades and DeFi developments"
        },
        {
            "symbol": "SUI",
            "name": "Sui",
            "relevance_score": 7.8,
            "mentions": 1,
            "context": "Sui blockchain performance and ecosystem growth"
        },
        {
            "symbol": "STABLECOIN",  # This should fail - not a valid symbol
            "name": "Stablecoin",
            "relevance_score": 6.0,
            "mentions": 1,
            "context": "Stablecoin market dynamics"
        }
    ]
    
    print(f"\n📊 Testing with {len(test_crypto_data)} crypto symbols from ingestion agent")
    
    # Initialize the fundamentals agent
    async with FundamentalsFetcherAgent() as agent:
        print("✅ Fundamentals agent initialized")
        
        # Test 1: Fetch fundamentals for each crypto symbol
        print("\n🔍 Test 1: Fetching fundamentals for each crypto symbol")
        print("-" * 50)
        
        for crypto_data in test_crypto_data:
            symbol = crypto_data["symbol"]
            name = crypto_data["name"]
            relevance = crypto_data["relevance_score"]
            
            print(f"\n💰 Testing: {name} ({symbol}) - Relevance: {relevance}")
            
            try:
                # Test basic fundamentals fetch
                fundamentals = await agent.get_fundamentals(symbol)
                
                if fundamentals:
                    print(f"  ✅ Success: ${fundamentals.current_price_usd:,.2f}")
                    print(f"     24h Change: {fundamentals.price_change_percentage_24h:+.2f}%")
                    print(f"     Market Cap Rank: #{fundamentals.market_cap_rank}")
                    print(f"     Market Cap: ${fundamentals.market_cap:,.0f}")
                    
                    # Test enhanced data access
                    if hasattr(fundamentals, 'volume_24h') and fundamentals.volume_24h:
                        print(f"     24h Volume: ${fundamentals.volume_24h:,.0f}")
                    
                    if hasattr(fundamentals, 'ath') and fundamentals.ath:
                        print(f"     ATH: ${fundamentals.ath:,.2f}")
                        
                else:
                    print(f"  ❌ Failed to fetch fundamentals for {symbol}")
                    
            except Exception as e:
                print(f"  ❌ Error fetching {symbol}: {e}")
        
        # Test 2: Batch fundamentals fetch
        print("\n🔍 Test 2: Batch fundamentals fetch")
        print("-" * 50)
        
        try:
            symbols = [crypto["symbol"] for crypto in test_crypto_data[:3]]  # First 3 valid ones
            print(f"Fetching fundamentals for: {', '.join(symbols)}")
            
            batch_fundamentals = await agent.get_multiple_fundamentals(symbols)
            
            if batch_fundamentals:
                print(f"✅ Batch fetch successful: {len(batch_fundamentals)} results")
                for fund in batch_fundamentals:
                    print(f"  {fund.symbol}: ${fund.current_price_usd:,.2f}")
            else:
                print("❌ Batch fetch failed")
                
        except Exception as e:
            print(f"❌ Batch fetch error: {e}")
        
        # Test 3: Market data fetch
        print("\n🔍 Test 3: Market data fetch")
        print("-" * 50)
        
        try:
            market_data = await agent.get_market_data()
            if market_data:
                print(f"✅ Market data fetched: {len(market_data)} coins")
                # Show top 5 by market cap
                top_coins = sorted(market_data, key=lambda x: x.get('market_cap', 0), reverse=True)[:5]
                for coin in top_coins:
                    print(f"  {coin['symbol'].upper()}: ${coin['market_cap']:,.0f}")
            else:
                print("❌ Market data fetch failed")
                
        except Exception as e:
            print(f"❌ Market data error: {e}")
        
        # Test 4: Search functionality
        print("\n🔍 Test 4: Search functionality")
        print("-" * 50)
        
        search_terms = ["bitcoin", "ethereum", "sui", "stablecoin"]
        for term in search_terms:
            try:
                results = await agent.search_coins(term)
                if results:
                    print(f"✅ Search '{term}': {len(results)} results")
                    for result in results[:3]:  # Show first 3
                        print(f"    {result['symbol'].upper()}: {result['name']}")
                else:
                    print(f"❌ Search '{term}': No results")
            except Exception as e:
                print(f"❌ Search '{term}' error: {e}")
    
    print("\n🎉 Fundamentals agent testing completed!")

if __name__ == "__main__":
    asyncio.run(test_fundamentals_enhanced())
