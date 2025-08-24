#!/usr/bin/env python3
"""
Debug script to test pipeline step by step
"""

import asyncio
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_pipeline():
    """Debug the pipeline step by step"""
    
    print("🔍 Debugging Pipeline Step by Step")
    print("=" * 50)
    
    try:
        # Step 1: Test ingestion
        print("\n📰 Step 1: Testing News Ingestion")
        from ingestion import NewsIngestionAgent
        
        ingestion_agent = NewsIngestionAgent()
        news_items = await ingestion_agent.fetch_crypto_focused_news(2)
        
        if news_items:
            print(f"✅ News fetched: {len(news_items)} items")
            for i, news in enumerate(news_items):
                print(f"  {i+1}. {news['title'][:60]}...")
                if news.get('primary_crypto'):
                    print(f"     Crypto: {news['primary_crypto']['symbol']} ({news['primary_crypto']['name']})")
                else:
                    print("     Crypto: None")
        else:
            print("❌ No news fetched")
            return
        
        # Step 2: Test fundamentals validation
        print("\n💰 Step 2: Testing Fundamentals Validation")
        from fundamentals import FundamentalsFetcherAgent
        
        fundamentals_agent = FundamentalsFetcherAgent()
        
        # Test symbol validation
        test_symbols = ['SUI', 'BTC', 'STABLECOIN', 'BINANCE']
        for symbol in test_symbols:
            is_valid = await fundamentals_agent.is_valid_symbol(symbol)
            print(f"  {symbol}: {'✅ Valid' if is_valid else '❌ Invalid'}")
        
        # Test fundamentals fetching for SUI
        print(f"\n🔍 Testing fundamentals for SUI...")
        fundamentals = await fundamentals_agent.get_fundamentals('SUI')
        if fundamentals:
            print(f"✅ SUI fundamentals: ${fundamentals.current_price_usd}")
        else:
            print("❌ Failed to get SUI fundamentals")
            return
        
        # Step 3: Test analyzer
        print("\n🔍 Step 3: Testing News Analyzer")
        from analyzer import AnalyzerAgent
        
        analyzer_agent = AnalyzerAgent()
        
        if news_items:
            primary_news = news_items[0]
            analysis = await analyzer_agent.analyze_news(
                primary_news['title'],
                primary_news['summary']
            )
            
            if analysis:
                print(f"✅ Analysis completed: {analysis.fundamentals} sentiment")
            else:
                print("❌ Analysis failed")
                return
        
        # Step 4: Test post creator
        print("\n📝 Step 4: Testing Post Creator")
        from post_creator import PostCreatorAgent
        
        post_creator_agent = PostCreatorAgent()
        
        if 'analysis' in locals() and 'fundamentals' in locals():
            posts = await post_creator_agent.create_crypto_specific_posts(
                'SUI',
                'Sui Network',
                analysis.__dict__,
                fundamentals.__dict__
            )
            
            if posts:
                print(f"✅ Posts created for {len(posts)} platforms")
                for platform, post in posts.items():
                    print(f"  {platform}: {post[:50]}...")
            else:
                print("❌ Post creation failed")
                return
        
        print("\n🎉 All pipeline steps completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Pipeline debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_pipeline())
