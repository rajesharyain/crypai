#!/usr/bin/env python3
"""
Test script for orchestrator fixes
"""

import asyncio
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_orchestrator_fix():
    """Test the orchestrator fixes"""
    
    print("🧪 Testing Orchestrator Fixes")
    print("=" * 40)
    
    try:
        from orchestrator import OrchestratorAgent
        from ingestion import NewsIngestionAgent
        from analyzer import AnalyzerAgent
        from fundamentals import FundamentalsFetcherAgent
        from post_creator import PostCreatorAgent
        
        print("\n🔧 Initializing agents...")
        
        # Initialize agents
        ingestion_agent = NewsIngestionAgent()
        analyzer_agent = AnalyzerAgent()
        fundamentals_agent = FundamentalsFetcherAgent()
        post_creator_agent = PostCreatorAgent()
        
        print("✅ All agents initialized")
        
        # Test each component individually
        print("\n📰 Testing News Ingestion...")
        news_items = await ingestion_agent.fetch_crypto_focused_news(2)
        if news_items:
            print(f"✅ News fetched: {len(news_items)} items")
            for i, news in enumerate(news_items):
                print(f"  {i+1}. {news['title'][:60]}...")
                if news.get('primary_crypto'):
                    print(f"     Crypto: {news['primary_crypto']['symbol']} ({news['primary_crypto']['name']})")
        else:
            print("❌ News ingestion failed")
            return
        
        print("\n🔍 Testing News Analysis...")
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
        
        print("\n💰 Testing Fundamentals...")
        async with fundamentals_agent as agent:
            fundamentals = await agent.get_fundamentals('SUI')
            if fundamentals:
                print(f"✅ SUI fundamentals: ${fundamentals.current_price_usd}")
            else:
                print("❌ Fundamentals failed")
                return
        
        print("\n📝 Testing Post Creation...")
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
                    if hasattr(post, 'content'):
                        # It's a SocialPost object
                        print(f"  {platform}: {post.content[:50]}...")
                    elif isinstance(post, dict) and 'content' in post:
                        # It's a dictionary
                        print(f"  {platform}: {post['content'][:50]}...")
                    else:
                        # Fallback
                        print(f"  {platform}: {str(post)[:50]}...")
            else:
                print("❌ Post creation failed")
                return
        
        print("\n🎉 All individual components working!")
        
        # Now test the orchestrator
        print("\n🚀 Testing Orchestrator...")
        orchestrator = OrchestratorAgent()
        
        # Test the pipeline
        from orchestrator import PipelineRequest
        request = PipelineRequest(symbol="SUI", news_limit=2, crypto_focus=True)
        
        result = await orchestrator.run_pipeline(request)
        
        if result.pipeline_status == "completed":
            print("🎉 Orchestrator pipeline completed successfully!")
            print(f"   Execution time: {result.execution_time:.2f} seconds")
            print(f"   News: {result.news_item.get('title', 'N/A')[:50]}...")
            print(f"   Analysis: {result.analysis.get('fundamentals', 'N/A')} sentiment")
            print(f"   Fundamentals: ${result.fundamentals.get('current_price_usd', 'N/A')}")
            print(f"   Posts: {len(result.posts)} platforms")
        else:
            print(f"❌ Orchestrator pipeline failed: {result.pipeline_status}")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_orchestrator_fix())
