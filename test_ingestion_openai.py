#!/usr/bin/env python3
"""
Test script to verify OpenAI API calls in the News Ingestion Agent
"""

import asyncio
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging to see all details
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_ingestion_openai():
    """Test if the ingestion agent calls OpenAI API"""
    
    print("🧪 Testing News Ingestion Agent OpenAI Integration")
    print("=" * 60)
    
    # Check OpenAI API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found in .env file")
        return
    else:
        print(f"✅ OpenAI API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        # Import the ingestion agent
        from ingestion import NewsIngestionAgent
        
        print("\n🔧 Initializing News Ingestion Agent...")
        agent = NewsIngestionAgent()
        
        # Check if LLM is initialized
        if agent.llm:
            print("✅ LangChain ChatOpenAI initialized successfully")
            print(f"   Model: {agent.llm.model_name}")
            print(f"   Temperature: {agent.llm.temperature}")
        else:
            print("❌ LangChain ChatOpenAI not initialized")
            return
        
        # Create test news items
        test_news = [
            {
                'title': 'Bitcoin reaches new all-time high as institutional adoption grows',
                'summary': 'Bitcoin (BTC) has surged to a new record high of $75,000, driven by strong institutional demand and ETF inflows. Major companies are now considering Bitcoin as a treasury asset.',
                'source': 'Test Source',
                'published': '2025-08-23T12:00:00Z'
            },
            {
                'title': 'Ethereum 2.0 staking rewards increase as network upgrades continue',
                'summary': 'Ethereum (ETH) staking rewards have increased to 5.2% APY as the network continues its transition to proof-of-stake. Validators are earning more ETH through staking.',
                'source': 'Test Source',
                'published': '2025-08-23T12:00:00Z'
            },
            {
                'title': 'Sui Network launches new DeFi protocols and gaming applications',
                'summary': 'Sui (SUI) blockchain has launched several new DeFi protocols and gaming applications. The network is seeing increased activity and developer adoption.',
                'source': 'Test Source',
                'published': '2025-08-23T12:00:00Z'
            }
        ]
        
        print(f"\n📰 Testing with {len(test_news)} news items...")
        
        # Test AI-powered crypto extraction
        print("\n🤖 Testing AI-powered crypto symbol extraction...")
        try:
            enhanced_news = await agent.extract_crypto_symbols_with_ai(test_news)
            print(f"✅ AI extraction completed: {len(enhanced_news)} items processed")
            
            # Show results
            for i, item in enumerate(enhanced_news):
                print(f"\n📄 Item {i+1}: {item['title'][:50]}...")
                print(f"   Crypto Symbols: {len(item.get('crypto_symbols', []))}")
                print(f"   Primary Crypto: {item.get('primary_crypto', 'None')}")
                print(f"   AI Method: {item.get('analysis_method', 'Unknown')}")
                print(f"   Relevance Score: {item.get('crypto_relevance_score', 0)}")
                
                if item.get('crypto_symbols'):
                    for symbol_info in item['crypto_symbols']:
                        print(f"     - {symbol_info['symbol']}: {symbol_info['name']} (Score: {symbol_info['relevance_score']})")
        
        except Exception as e:
            print(f"❌ AI extraction failed: {e}")
            print("   This might be due to OpenAI API quota issues")
        
        # Test regex-based fallback
        print("\n🔍 Testing regex-based crypto symbol extraction (fallback)...")
        try:
            regex_enhanced = agent.analyze_news_with_crypto_context(test_news)
            print(f"✅ Regex extraction completed: {len(regex_enhanced)} items processed")
            
            # Show results
            for i, item in enumerate(regex_enhanced):
                print(f"\n📄 Item {i+1}: {item['title'][:50]}...")
                print(f"   Crypto Symbols: {len(item.get('crypto_symbols', []))}")
                print(f"   Primary Crypto: {item.get('primary_crypto', 'None')}")
                print(f"   Relevance Score: {item.get('crypto_relevance_score', 0)}")
                
                if item.get('crypto_symbols'):
                    for symbol_info in item['crypto_symbols']:
                        print(f"     - {symbol_info['symbol']}: {symbol_info['name']} (Score: {symbol_info['relevance_score']})")
        
        except Exception as e:
            print(f"❌ Regex extraction failed: {e}")
        
        # Test individual symbol extraction
        print("\n🎯 Testing individual crypto symbol extraction...")
        test_text = "Bitcoin and Ethereum are leading the market, while Solana and Cardano show strong momentum."
        symbols = agent.extract_crypto_symbols(test_text)
        print(f"✅ Extracted {len(symbols)} symbols from test text")
        
        for symbol_info in symbols:
            print(f"   - {symbol_info['symbol']}: {symbol_info['name']} (Score: {symbol_info['relevance_score']})")
        
        print("\n" + "=" * 60)
        print("🎉 Testing completed!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(test_ingestion_openai())
