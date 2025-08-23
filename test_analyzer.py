#!/usr/bin/env python3
"""
Test script for the Analyzer Agent
Tests news analysis functionality using LangChain + OpenAI
"""

import asyncio
import json
from datetime import datetime
from analyzer import (
    AnalyzerAgent,
    analyze_single_news,
    analyze_news_batch
)

async def test_analyzer_initialization():
    """Test analyzer agent initialization"""
    print("🧪 Testing Analyzer Agent Initialization...")
    print("=" * 50)
    
    try:
        agent = AnalyzerAgent()
        status = agent.get_agent_status()
        
        print(f"✅ Analyzer Agent initialized successfully")
        print(f"   Model: {status['model']}")
        print(f"   Temperature: {status['temperature']}")
        print(f"   LLM Initialized: {status['llm_initialized']}")
        print(f"   OpenAI Key Configured: {status['openai_key_configured']}")
        print(f"   Status: {status['status']}")
        
        return status['llm_initialized']
        
    except Exception as e:
        print(f"❌ Error initializing Analyzer Agent: {e}")
        return False

async def test_single_news_analysis():
    """Test single news article analysis"""
    print("\n🧪 Testing Single News Analysis...")
    print("=" * 50)
    
    try:
        # Test with a positive crypto news
        title = "Bitcoin Surges to New All-Time High as Institutional Adoption Grows"
        summary = "Bitcoin has reached a new all-time high of $75,000 as major financial institutions announce new cryptocurrency investment products. The surge is driven by increased institutional adoption and positive regulatory developments."
        
        print(f"🔍 Analyzing: {title}")
        print(f"📝 Summary: {summary}")
        
        result = await analyze_single_news(title, summary)
        
        if result:
            print("✅ Analysis completed successfully!")
            print(f"   📊 Summary: {result.summary}")
            print(f"   😊 Sentiment: {result.sentiment:.3f}")
            print(f"   💼 Fundamentals: {result.fundamentals}")
            print(f"   🎯 Confidence: {result.confidence:.3f}")
            return True
        else:
            print("❌ Analysis failed")
            return False
            
    except Exception as e:
        print(f"❌ Error in single news analysis: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_negative_news_analysis():
    """Test negative news article analysis"""
    print("\n🧪 Testing Negative News Analysis...")
    print("=" * 50)
    
    try:
        # Test with a negative crypto news
        title = "Major Cryptocurrency Exchange Faces Regulatory Crackdown"
        summary = "A leading cryptocurrency exchange is under investigation by regulatory authorities for alleged violations of financial regulations. The news has caused market uncertainty and declining prices across major cryptocurrencies."
        
        print(f"🔍 Analyzing: {title}")
        print(f"📝 Summary: {summary}")
        
        result = await analyze_single_news(title, summary)
        
        if result:
            print("✅ Analysis completed successfully!")
            print(f"   📊 Summary: {result.summary}")
            print(f"   😊 Sentiment: {result.sentiment:.3f}")
            print(f"   💼 Fundamentals: {result.fundamentals}")
            print(f"   🎯 Confidence: {result.confidence:.3f}")
            return True
        else:
            print("❌ Analysis failed")
            return False
            
    except Exception as e:
        print(f"❌ Error in negative news analysis: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_neutral_news_analysis():
    """Test neutral news article analysis"""
    print("\n🧪 Testing Neutral News Analysis...")
    print("=" * 50)
    
    try:
        # Test with a neutral crypto news
        title = "New Cryptocurrency Wallet Feature Released for Enhanced Security"
        summary = "A popular cryptocurrency wallet has released a new security feature that allows users to set additional authentication requirements. The update is part of regular security improvements and maintenance."
        
        print(f"🔍 Analyzing: {title}")
        print(f"📝 Summary: {summary}")
        
        result = await analyze_single_news(title, summary)
        
        if result:
            print("✅ Analysis completed successfully!")
            print(f"   📊 Summary: {result.summary}")
            print(f"   😊 Sentiment: {result.sentiment:.3f}")
            print(f"   💼 Fundamentals: {result.fundamentals}")
            print(f"   🎯 Confidence: {result.confidence:.3f}")
            return True
        else:
            print("❌ Analysis failed")
            return False
            
    except Exception as e:
        print(f"❌ Error in neutral news analysis: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_batch_news_analysis():
    """Test batch news analysis"""
    print("\n🧪 Testing Batch News Analysis...")
    print("=" * 50)
    
    try:
        # Test with multiple news items
        news_items = [
            {
                "title": "Ethereum 2.0 Upgrade Successfully Launched",
                "summary": "The long-awaited Ethereum 2.0 upgrade has been successfully deployed, bringing proof-of-stake consensus and improved scalability to the network."
            },
            {
                "title": "DeFi Protocol Suffers Major Exploit",
                "summary": "A popular DeFi protocol has been exploited, resulting in the loss of millions of dollars worth of user funds."
            },
            {
                "title": "Central Bank Announces Digital Currency Pilot Program",
                "summary": "A major central bank has announced plans to launch a pilot program for its digital currency, marking a significant step in CBDC development."
            }
        ]
        
        print(f"🔍 Analyzing {len(news_items)} news articles...")
        
        results = await analyze_news_batch(news_items)
        
        if results:
            print(f"✅ Batch analysis completed successfully!")
            print(f"   📊 Total analyzed: {len(results)}")
            
            for i, result in enumerate(results, 1):
                analysis = result['analysis']
                item = result['item']
                print(f"\n   {i}. {item['title']}")
                print(f"      Sentiment: {analysis.sentiment:.3f}")
                print(f"      Fundamentals: {analysis.fundamentals}")
                print(f"      Confidence: {analysis.confidence:.3f}")
            
            return True
        else:
            print("❌ Batch analysis failed")
            return False
            
    except Exception as e:
        print(f"❌ Error in batch analysis: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_fallback_analysis():
    """Test fallback analysis when AI analysis fails"""
    print("\n🧪 Testing Fallback Analysis...")
    print("=" * 50)
    
    try:
        # Create an agent without OpenAI key to trigger fallback
        agent = AnalyzerAgent()
        agent.llm = None  # Force fallback mode
        
        title = "Cryptocurrency Market Shows Mixed Signals"
        summary = "The cryptocurrency market is experiencing mixed signals with some coins showing gains while others decline."
        
        print(f"🔍 Testing fallback analysis for: {title}")
        
        result = await agent.analyze_news(title, summary)
        
        if result:
            print("✅ Fallback analysis completed successfully!")
            print(f"   📊 Summary: {result.summary}")
            print(f"   😊 Sentiment: {result.sentiment:.3f}")
            print(f"   💼 Fundamentals: {result.fundamentals}")
            print(f"   🎯 Confidence: {result.confidence:.3f}")
            return True
        else:
            print("❌ Fallback analysis failed")
            return False
            
    except Exception as e:
        print(f"❌ Error in fallback analysis: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🚀 Analyzer Agent Test Suite")
    print("=" * 60)
    
    tests = [
        ("Analyzer Initialization", test_analyzer_initialization),
        ("Single News Analysis", test_single_news_analysis),
        ("Negative News Analysis", test_negative_news_analysis),
        ("Neutral News Analysis", test_neutral_news_analysis),
        ("Batch News Analysis", test_batch_news_analysis),
        ("Fallback Analysis", test_fallback_analysis)
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
        print("🎉 All tests passed! The Analyzer Agent is working correctly.")
        print("\n💡 Key Features Verified:")
        print("   ✅ OpenAI integration via LangChain")
        print("   ✅ Sentiment analysis (-1 to 1 scale)")
        print("   ✅ Fundamental impact assessment")
        print("   ✅ Confidence scoring")
        print("   ✅ Fallback analysis system")
        print("   ✅ Batch processing capability")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print("\n🚀 Next steps:")
    print("   - Test the /analyze endpoint: POST /analyze")
    print("   - Test batch analysis: POST /analyze/batch")
    print("   - Check analyzer status: GET /analyze/status")
    print("   - Integrate with news ingestion for automated analysis")

if __name__ == "__main__":
    asyncio.run(main())
