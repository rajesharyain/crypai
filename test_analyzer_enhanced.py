#!/usr/bin/env python3
"""
Enhanced test script for Analyzer Agent
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

async def test_analyzer_enhanced():
    """Test analyzer agent with enhanced crypto data"""
    
    print("🧪 Testing Analyzer Agent with Enhanced Crypto Data")
    print("=" * 70)
    
    # Import the analyzer agent
    try:
        from analyzer import AnalyzerAgent, AnalysisResult
        print("✅ Analyzer agent imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import analyzer agent: {e}")
        return
    
    # Test data from ingestion agent (simulated enhanced news)
    test_news_data = [
        {
            "title": "Bitcoin Surges Past $50,000 as Institutional Adoption Grows",
            "summary": "Bitcoin has reached a new milestone, crossing the $50,000 mark for the first time since 2021. Major financial institutions including BlackRock and Fidelity have increased their Bitcoin holdings, signaling growing institutional confidence in the cryptocurrency market. Analysts attribute this surge to improved regulatory clarity and the upcoming halving event.",
            "crypto_symbols": [
                {
                    "symbol": "BTC",
                    "name": "Bitcoin",
                    "relevance_score": 9.8,
                    "mentions": 4,
                    "context": "Bitcoin price surge and institutional adoption"
                }
            ],
            "is_crypto_news": True,
            "crypto_relevance_score": 9.8
        },
        {
            "title": "Ethereum Layer 2 Solutions See Record Growth in TVL",
            "summary": "Ethereum's Layer 2 scaling solutions have achieved unprecedented growth, with total value locked (TVL) reaching new heights. Arbitrum, Optimism, and Polygon are leading the charge, offering faster and cheaper transactions. This development addresses Ethereum's scalability challenges and improves user experience for DeFi applications.",
            "crypto_symbols": [
                {
                    "symbol": "ETH",
                    "name": "Ethereum",
                    "relevance_score": 8.5,
                    "mentions": 3,
                    "context": "Ethereum L2 scaling and DeFi growth"
                },
                {
                    "symbol": "ARB",
                    "name": "Arbitrum",
                    "relevance_score": 7.2,
                    "mentions": 1,
                    "context": "Arbitrum L2 solution performance"
                }
            ],
            "is_crypto_news": True,
            "crypto_relevance_score": 8.5
        },
        {
            "title": "Sui Blockchain Achieves 100,000 TPS in Latest Testnet",
            "summary": "The Sui blockchain has demonstrated exceptional performance in its latest testnet, achieving over 100,000 transactions per second. This milestone showcases Sui's potential to handle enterprise-grade applications and compete with traditional payment systems. The testnet also revealed improved smart contract execution and reduced gas fees.",
            "crypto_symbols": [
                {
                    "symbol": "SUI",
                    "name": "Sui",
                    "relevance_score": 8.9,
                    "mentions": 2,
                    "context": "Sui blockchain performance and scalability"
                }
            ],
            "is_crypto_news": True,
            "crypto_relevance_score": 8.9
        },
        {
            "title": "Stablecoin Market Faces Regulatory Scrutiny",
            "summary": "Global regulators are intensifying their oversight of the stablecoin market, particularly focusing on USDT and USDC. Concerns about reserve backing and potential systemic risks have prompted calls for stricter regulations. This regulatory pressure could reshape the stablecoin landscape and impact DeFi protocols that rely heavily on stable assets.",
            "crypto_symbols": [
                {
                    "symbol": "USDT",
                    "name": "Tether",
                    "relevance_score": 7.8,
                    "mentions": 2,
                    "context": "USDT regulatory scrutiny and market impact"
                },
                {
                    "symbol": "USDC",
                    "name": "USD Coin",
                    "relevance_score": 7.5,
                    "mentions": 1,
                    "context": "USDC regulatory compliance"
                }
            ],
            "is_crypto_news": True,
            "crypto_relevance_score": 7.8
        }
    ]
    
    print(f"\n📰 Testing with {len(test_news_data)} enhanced news items from ingestion agent")
    
    # Initialize the analyzer agent
    analyzer = AnalyzerAgent()
    print(f"✅ Analyzer agent initialized: {analyzer.get_status()}")
    
    # Test 1: Individual news analysis with crypto symbols
    print("\n🔍 Test 1: Individual news analysis with crypto symbols")
    print("-" * 60)
    
    for i, news_item in enumerate(test_news_data, 1):
        title = news_item["title"]
        summary = news_item["summary"]
        crypto_symbols = news_item.get("crypto_symbols", [])
        
        print(f"\n📰 News {i}: {title[:60]}...")
        print(f"   Crypto Symbols: {len(crypto_symbols)} detected")
        
        try:
            # Test analysis with crypto symbols
            analysis = await analyzer.analyze_news(title, summary, crypto_symbols)
            
            if analysis:
                print(f"  ✅ Analysis successful:")
                print(f"     Summary: {analysis.summary}")
                print(f"     Sentiment: {analysis.sentiment:.2f}")
                print(f"     Fundamentals: {analysis.fundamentals}")
                print(f"     Confidence: {analysis.confidence:.2f}")
                print(f"     Model Used: {analysis.model_used}")
                
                # Check crypto impact data
                if hasattr(analysis, 'crypto_impact') and analysis.crypto_impact:
                    print(f"     Crypto Impact: {len(analysis.crypto_impact)} fields")
                    for key, value in list(analysis.crypto_impact.items())[:3]:  # Show first 3
                        print(f"       {key}: {value}")
                else:
                    print(f"     Crypto Impact: No data")
                    
            else:
                print(f"  ❌ Analysis failed")
                
        except Exception as e:
            print(f"  ❌ Analysis error: {e}")
    
    # Test 2: Crypto-specific analysis
    print("\n🔍 Test 2: Crypto-specific analysis")
    print("-" * 60)
    
    for news_item in test_news_data[:2]:  # Test first 2 items
        title = news_item["title"]
        summary = news_item["summary"]
        crypto_symbols = news_item.get("crypto_symbols", [])
        
        if crypto_symbols:
            primary_crypto = crypto_symbols[0]
            print(f"\n🎯 Crypto-specific analysis for {primary_crypto['name']} ({primary_crypto['symbol']})")
            
            try:
                # Test crypto-specific analysis
                analysis = await analyzer.analyze_crypto_specific_news(news_item)
                
                if analysis:
                    print(f"  ✅ Crypto analysis successful:")
                    print(f"     Summary: {analysis.summary}")
                    print(f"     Sentiment: {analysis.sentiment:.2f}")
                    print(f"     Fundamentals: {analysis.fundamentals}")
                    print(f"     Confidence: {analysis.confidence:.2f}")
                    
                    # Check crypto impact data
                    if hasattr(analysis, 'crypto_impact') and analysis.crypto_impact:
                        print(f"     Crypto Impact: {len(analysis.crypto_impact)} fields")
                        for key, value in list(analysis.crypto_impact.items())[:3]:
                            print(f"       {key}: {value}")
                else:
                    print(f"  ❌ Crypto analysis failed")
                    
            except Exception as e:
                print(f"  ❌ Crypto analysis error: {e}")
    
    # Test 3: Batch analysis
    print("\n🔍 Test 3: Batch analysis")
    print("-" * 60)
    
    try:
        # Prepare news items for batch analysis
        batch_items = []
        for news_item in test_news_data:
            batch_items.append({
                "title": news_item["title"],
                "summary": news_item["summary"],
                "crypto_symbols": news_item.get("crypto_symbols", [])
            })
        
        print(f"Processing {len(batch_items)} news items in batch...")
        
        # Test batch analysis
        batch_results = await analyzer.analyze_multiple_news(batch_items)
        
        if batch_results:
            print(f"✅ Batch analysis successful: {len(batch_results)} results")
            
            # Show summary of each result
            for i, result in enumerate(batch_results, 1):
                print(f"  Result {i}: {result.sentiment:.2f} sentiment, {result.fundamentals} fundamentals")
                
        else:
            print("❌ Batch analysis failed")
            
    except Exception as e:
        print(f"❌ Batch analysis error: {e}")
    
    # Test 4: Fallback analysis (when OpenAI fails)
    print("\n🔍 Test 4: Fallback analysis testing")
    print("-" * 60)
    
    # Test with a simple news item
    test_title = "Crypto Market Shows Mixed Signals"
    test_summary = "The cryptocurrency market is experiencing mixed signals with some coins gaining while others decline."
    
    try:
        # This should trigger fallback if OpenAI is not available
        fallback_analysis = await analyzer.analyze_news(test_title, test_summary)
        
        if fallback_analysis:
            print(f"✅ Fallback analysis successful:")
            print(f"     Summary: {fallback_analysis.summary}")
            print(f"     Sentiment: {fallback_analysis.sentiment:.2f}")
            print(f"     Fundamentals: {fallback_analysis.fundamentals}")
            print(f"     Model Used: {fallback_analysis.model_used}")
        else:
            print("❌ Fallback analysis failed")
            
    except Exception as e:
        print(f"❌ Fallback analysis error: {e}")
    
    print("\n🎉 Analyzer agent testing completed!")

if __name__ == "__main__":
    asyncio.run(test_analyzer_enhanced())
