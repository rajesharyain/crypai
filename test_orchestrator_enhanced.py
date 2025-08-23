#!/usr/bin/env python3
"""
Enhanced test script for Orchestrator Agent
Tests complete pipeline execution: Ingestion → Analysis → Fundamentals → Post Creation
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
    format='%(asctime)s - %(name)s - %(levelname)s - %(name)s - %(message)s'
)

async def test_orchestrator_enhanced():
    """Test orchestrator agent with complete pipeline execution"""
    
    print("🧪 Testing Orchestrator Agent - Complete Pipeline Execution")
    print("=" * 70)
    
    # Import the orchestrator agent
    try:
        from orchestrator import OrchestratorAgent, PipelineRequest, MultiplePipelineRequest
        print("✅ Orchestrator agent imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import orchestrator agent: {e}")
        return
    
    # Initialize the orchestrator agent
    orchestrator = OrchestratorAgent()
    print("✅ Orchestrator agent initialized")
    
    # Test 1: Single pipeline execution with crypto focus
    print("\n🔍 Test 1: Single pipeline execution with crypto focus")
    print("-" * 60)
    
    try:
        # Test single pipeline with SUI focus
        request = PipelineRequest(
            symbol="SUI",
            news_limit=2,
            crypto_focus=True
        )
        
        print(f"🚀 Running pipeline with crypto focus: {request.symbol}, limit: {request.news_limit}")
        
        result = await orchestrator.run_pipeline(request)
        
        if result and result.pipeline_status == "completed":
            print(f"✅ Pipeline completed successfully!")
            print(f"   Execution time: {result.execution_time:.2f} seconds")
            print(f"   News title: {result.news_item.get('title', 'Unknown')[:60]}...")
            print(f"   Analysis sentiment: {result.analysis.get('sentiment', 'Unknown')}")
            print(f"   Fundamentals symbol: {result.fundamentals.get('symbol', 'Unknown')}")
            print(f"   Posts created: {len(result.posts) if isinstance(result.posts, dict) else 0} platforms")
            
            # Show post details
            if result.posts and isinstance(result.posts, dict):
                print(f"   Post platforms:")
                for platform, post in result.posts.items():
                    if hasattr(post, 'content'):
                        print(f"     {platform.upper()}: {post.content[:50]}...")
                        print(f"       Engagement: {getattr(post, 'engagement_score', 'N/A')}")
                    else:
                        print(f"     {platform.upper()}: {str(post)[:50]}...")
            
        else:
            print(f"❌ Pipeline failed or incomplete")
            if result:
                print(f"   Status: {result.pipeline_status}")
                print(f"   Execution time: {result.execution_time:.2f} seconds")
                if result.pipeline_status == "failed":
                    print(f"   Error details: {result.analysis or 'No error details'}")
            
    except Exception as e:
        print(f"❌ Single pipeline execution error: {e}")
    
    # Test 2: Multiple pipeline execution
    print("\n🔍 Test 2: Multiple pipeline execution")
    print("-" * 60)
    
    try:
        # Test multiple pipeline execution
        multi_request = MultiplePipelineRequest(
            symbol="SUI",
            news_limit=2,
            crypto_focus=True
        )
        
        print(f"🚀 Running multiple pipelines with crypto focus: {multi_request.symbol}, limit: {multi_request.news_limit}")
        
        results = await orchestrator.run_multiple_pipelines(multi_request)
        
        if results and results.success:
            print(f"✅ Multiple pipelines completed successfully!")
            print(f"   Total executed: {results.total_executed}")
            print(f"   Results count: {len(results.pipeline_results)}")
            
            # Show summary of each result
            for i, result in enumerate(results.pipeline_results, 1):
                if result.pipeline_status == "completed":
                    print(f"   Pipeline {i}: ✅ Completed in {result.execution_time:.2f}s")
                    print(f"     News: {result.news_item.get('title', 'Unknown')[:40]}...")
                    print(f"     Sentiment: {result.analysis.get('sentiment', 'Unknown')}")
                    print(f"     Posts: {len(result.posts) if isinstance(result.posts, dict) else 0} platforms")
                else:
                    print(f"   Pipeline {i}: ❌ Failed - {result.pipeline_status}")
            
            if results.errors:
                print(f"   Errors encountered: {len(results.errors)}")
                for error in results.errors[:3]:  # Show first 3 errors
                    print(f"     - {error}")
                    
        else:
            print(f"❌ Multiple pipelines failed")
            if results:
                print(f"   Success: {results.success}")
                print(f"   Total executed: {results.total_executed}")
                print(f"   Errors: {len(results.errors)}")
            
    except Exception as e:
        print(f"❌ Multiple pipeline execution error: {e}")
    
    # Test 3: Pipeline with different crypto symbols
    print("\n🔍 Test 3: Pipeline with different crypto symbols")
    print("-" * 60)
    
    test_symbols = ["BTC", "ETH", "SUI"]
    
    for symbol in test_symbols:
        try:
            print(f"\n🎯 Testing pipeline with {symbol}...")
            
            request = PipelineRequest(
                symbol=symbol,
                news_limit=1,
                crypto_focus=True
            )
            
            result = await orchestrator.run_pipeline(request)
            
            if result and result.pipeline_status == "completed":
                print(f"  ✅ {symbol} pipeline completed in {result.execution_time:.2f}s")
                print(f"     News: {result.news_item.get('title', 'Unknown')[:40]}...")
                print(f"     Fundamentals: {result.fundamentals.get('symbol', 'Unknown')} - ${result.fundamentals.get('current_price_usd', 0):,.2f}")
                print(f"     Posts: {len(result.posts) if isinstance(result.posts, dict) else 0} platforms")
            else:
                print(f"  ❌ {symbol} pipeline failed")
                if result:
                    print(f"     Status: {result.pipeline_status}")
                    print(f"     Time: {result.execution_time:.2f}s")
                    
        except Exception as e:
            print(f"  ❌ {symbol} pipeline error: {e}")
    
    # Test 4: Pipeline error handling
    print("\n🔍 Test 4: Pipeline error handling")
    print("-" * 60)
    
    try:
        # Test with invalid symbol that should fail
        print("🧪 Testing error handling with invalid symbol...")
        
        request = PipelineRequest(
            symbol="INVALID_SYMBOL_123",
            news_limit=1,
            crypto_focus=True
        )
        
        result = await orchestrator.run_pipeline(request)
        
        if result:
            if result.pipeline_status == "failed":
                print(f"✅ Error handling working correctly")
                print(f"   Status: {result.pipeline_status}")
                print(f"   Execution time: {result.execution_time:.2f} seconds")
            else:
                print(f"⚠️ Unexpected success with invalid symbol")
                print(f"   Status: {result.pipeline_status}")
        else:
            print(f"❌ No result returned for error case")
            
    except Exception as e:
        print(f"✅ Exception caught as expected: {e}")
    
    # Test 5: Pipeline performance metrics
    print("\n🔍 Test 5: Pipeline performance metrics")
    print("-" * 60)
    
    try:
        # Run a quick pipeline to measure performance
        print("📊 Measuring pipeline performance...")
        
        request = PipelineRequest(
            symbol="SUI",
            news_limit=1,
            crypto_focus=True
        )
        
        start_time = asyncio.get_event_loop().time()
        result = await orchestrator.run_pipeline(request)
        end_time = asyncio.get_event_loop().time()
        
        if result:
            actual_time = result.execution_time
            measured_time = end_time - start_time
            
            print(f"✅ Performance metrics:")
            print(f"   Pipeline execution time: {actual_time:.2f}s")
            print(f"   Measured time: {measured_time:.2f}s")
            print(f"   Time difference: {abs(actual_time - measured_time):.2f}s")
            
            if actual_time < 30:  # Should complete within 30 seconds
                print(f"   Performance: 🚀 Fast (< 30s)")
            elif actual_time < 60:
                print(f"   Performance: ⚡ Moderate (< 60s)")
            else:
                print(f"   Performance: 🐌 Slow (> 60s)")
        else:
            print(f"❌ No result for performance measurement")
            
    except Exception as e:
        print(f"❌ Performance measurement error: {e}")
    
    print("\n🎉 Orchestrator agent testing completed!")

if __name__ == "__main__":
    asyncio.run(test_orchestrator_enhanced())
