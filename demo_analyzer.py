#!/usr/bin/env python3
"""
Analyzer Agent Demonstration
Showcases AI-powered news analysis capabilities
"""

import asyncio
import json
from datetime import datetime
from analyzer import (
    AnalyzerAgent,
    analyze_single_news,
    analyze_news_batch
)

async def demonstrate_single_analysis():
    """Demonstrate single news analysis"""
    print("🔍 Single News Analysis Demonstration")
    print("=" * 60)
    
    try:
        # Example 1: Positive news
        print("📰 Example 1: Positive Crypto News")
        print("-" * 40)
        
        title1 = "Bitcoin ETF Approval Drives Institutional Investment Surge"
        summary1 = "The recent approval of Bitcoin ETFs has led to unprecedented institutional investment, with major financial firms allocating billions to cryptocurrency assets. This development signals mainstream acceptance and could drive significant price appreciation."
        
        print(f"Title: {title1}")
        print(f"Summary: {summary1}")
        
        result1 = await analyze_single_news(title1, summary1)
        
        if result1:
            print(f"\n✅ Analysis Results:")
            print(f"   📊 Summary: {result1.summary}")
            print(f"   😊 Sentiment: {result1.sentiment:.3f}")
            print(f"   💼 Fundamentals: {result1.fundamentals}")
            print(f"   🎯 Confidence: {result1.confidence:.3f}")
        else:
            print("❌ Analysis failed")
            return False
        
        # Example 2: Negative news
        print(f"\n📰 Example 2: Negative Crypto News")
        print("-" * 40)
        
        title2 = "Major DeFi Protocol Exploit Results in $50M Loss"
        summary2 = "A critical vulnerability in a popular DeFi protocol has been exploited, resulting in the theft of $50 million in user funds. The incident has shaken investor confidence and led to calls for improved security standards."
        
        print(f"Title: {title2}")
        print(f"Summary: {summary2}")
        
        result2 = await analyze_single_news(title2, summary2)
        
        if result2:
            print(f"\n✅ Analysis Results:")
            print(f"   📊 Summary: {result2.summary}")
            print(f"   😊 Sentiment: {result2.sentiment:.3f}")
            print(f"   💼 Fundamentals: {result2.fundamentals}")
            print(f"   🎯 Confidence: {result2.confidence:.3f}")
        else:
            print("❌ Analysis failed")
            return False
        
        # Example 3: Neutral news
        print(f"\n📰 Example 3: Neutral Crypto News")
        print("-" * 40)
        
        title3 = "New Cryptocurrency Exchange Launches with Enhanced Security Features"
        summary3 = "A new cryptocurrency exchange has launched with advanced security features including multi-signature wallets and cold storage. The platform aims to provide a secure trading environment for digital assets."
        
        print(f"Title: {title3}")
        print(f"Summary: {summary3}")
        
        result3 = await analyze_single_news(title3, summary3)
        
        if result3:
            print(f"\n✅ Analysis Results:")
            print(f"   📊 Summary: {result3.summary}")
            print(f"   😊 Sentiment: {result3.sentiment:.3f}")
            print(f"   💼 Fundamentals: {result3.fundamentals}")
            print(f"   🎯 Confidence: {result3.confidence:.3f}")
        else:
            print("❌ Analysis failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error in single analysis demonstration: {e}")
        import traceback
        traceback.print_exc()
        return False

async def demonstrate_batch_analysis():
    """Demonstrate batch news analysis"""
    print(f"\n🔍 Batch News Analysis Demonstration")
    print("=" * 60)
    
    try:
        # Create a diverse set of news items
        news_items = [
            {
                "title": "Ethereum 2.0 Staking Reaches 20 Million ETH",
                "summary": "The Ethereum 2.0 staking contract has reached a milestone with 20 million ETH now locked in the proof-of-stake system, demonstrating strong community support for the network upgrade."
            },
            {
                "title": "Regulatory Uncertainty Impacts Crypto Markets",
                "summary": "Recent regulatory announcements have created uncertainty in cryptocurrency markets, leading to increased volatility and cautious trading behavior among investors."
            },
            {
                "title": "DeFi Lending Protocol Achieves $1B TVL",
                "summary": "A decentralized lending protocol has achieved $1 billion in total value locked, marking a significant milestone in the growth of decentralized finance."
            },
            {
                "title": "Cryptocurrency Mining Faces Environmental Scrutiny",
                "summary": "Environmental concerns about cryptocurrency mining energy consumption have led to increased scrutiny and potential regulatory changes in several jurisdictions."
            },
            {
                "title": "Central Bank Digital Currency Pilot Program Launched",
                "summary": "A major central bank has launched a pilot program for its digital currency, exploring the potential benefits and challenges of CBDC implementation."
            }
        ]
        
        print(f"📰 Analyzing {len(news_items)} diverse news articles...")
        print("-" * 40)
        
        for i, item in enumerate(news_items, 1):
            print(f"{i}. {item['title']}")
        
        print(f"\n🔍 Processing batch analysis...")
        results = await analyze_news_batch(news_items)
        
        if results:
            print(f"✅ Batch analysis completed successfully!")
            print(f"   📊 Total analyzed: {len(results)}")
            
            # Group by sentiment category
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            total_sentiment = 0
            
            print(f"\n📊 Analysis Summary:")
            print("-" * 40)
            
            for i, result in enumerate(results, 1):
                analysis = result['analysis']
                item = result['item']
                
                # Count sentiment categories
                if analysis.fundamentals == "positive":
                    positive_count += 1
                elif analysis.fundamentals == "negative":
                    negative_count += 1
                else:
                    neutral_count += 1
                
                total_sentiment += analysis.sentiment
                
                print(f"\n   {i}. {item['title']}")
                print(f"      😊 Sentiment: {analysis.sentiment:.3f}")
                print(f"      💼 Fundamentals: {analysis.fundamentals}")
                print(f"      🎯 Confidence: {analysis.confidence:.3f}")
                print(f"      📝 Summary: {analysis.summary}")
            
            # Calculate averages
            avg_sentiment = total_sentiment / len(results) if results else 0
            
            print(f"\n📈 Batch Analysis Statistics:")
            print("-" * 40)
            print(f"   📊 Total Articles: {len(results)}")
            print(f"   😊 Positive: {positive_count}")
            print(f"   😔 Negative: {negative_count}")
            print(f"   😐 Neutral: {neutral_count}")
            print(f"   📊 Average Sentiment: {avg_sentiment:.3f}")
            
            return True
        else:
            print("❌ Batch analysis failed")
            return False
            
    except Exception as e:
        print(f"❌ Error in batch analysis demonstration: {e}")
        import traceback
        traceback.print_exc()
        return False

async def demonstrate_agent_capabilities():
    """Demonstrate various agent capabilities"""
    print(f"\n🔧 Agent Capabilities Demonstration")
    print("=" * 60)
    
    try:
        agent = AnalyzerAgent()
        
        # Show agent status
        print("📊 Agent Status:")
        print("-" * 40)
        status = agent.get_agent_status()
        for key, value in status.items():
            print(f"   {key}: {value}")
        
        # Test different model configurations
        print(f"\n🧪 Testing Different Configurations:")
        print("-" * 40)
        
        # Test with different temperature settings
        for temp in [0.1, 0.5, 0.9]:
            print(f"\n   Testing with temperature {temp}:")
            test_agent = AnalyzerAgent(temperature=temp)
            test_status = test_agent.get_agent_status()
            print(f"      Temperature: {test_status['temperature']}")
            print(f"      Model: {test_status['model']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in capabilities demonstration: {e}")
        import traceback
        traceback.print_exc()
        return False

async def demonstrate_error_handling():
    """Demonstrate error handling and fallback mechanisms"""
    print(f"\n⚠️  Error Handling Demonstration")
    print("=" * 60)
    
    try:
        # Test with empty content
        print("🔍 Testing with empty content:")
        print("-" * 40)
        
        result1 = await analyze_single_news("", "")
        if result1:
            print(f"   ✅ Fallback analysis worked for empty content")
            print(f"      Sentiment: {result1.sentiment:.3f}")
            print(f"      Fundamentals: {result1.fundamentals}")
        else:
            print("   ❌ Failed to handle empty content")
        
        # Test with very long content
        print(f"\n🔍 Testing with very long content:")
        print("-" * 40)
        
        long_title = "A" * 1000
        long_summary = "B" * 2000
        
        result2 = await analyze_single_news(long_title, long_summary)
        if result2:
            print(f"   ✅ Analysis worked with long content")
            print(f"      Sentiment: {result2.sentiment:.3f}")
            print(f"      Fundamentals: {result2.fundamentals}")
        else:
            print("   ❌ Failed to handle long content")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in error handling demonstration: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main demonstration function"""
    print("🚀 Analyzer Agent - Live Demonstration")
    print("=" * 80)
    
    try:
        # Run demonstrations
        demonstrations = [
            ("Single News Analysis", demonstrate_single_analysis),
            ("Batch News Analysis", demonstrate_batch_analysis),
            ("Agent Capabilities", demonstrate_agent_capabilities),
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
            print("   ✅ AI-powered sentiment analysis (-1 to 1 scale)")
            print("   ✅ Fundamental impact assessment")
            print("   ✅ Confidence scoring")
            print("   ✅ Intelligent summarization")
            print("   ✅ Batch processing capability")
            print("   ✅ Robust error handling")
            print("   ✅ Fallback analysis system")
        else:
            print("⚠️  Some demonstrations failed. Check the output above for details.")
        
        print("\n🚀 Next Steps:")
        print("   - Test the API endpoints: POST /analyze")
        print("   - Test batch analysis: POST /analyze/batch")
        print("   - Check analyzer status: GET /analyze/status")
        print("   - Integrate with news ingestion pipeline")
        print("   - Build trading signals based on sentiment analysis")
        print("   - Create automated news monitoring systems")
        
    except Exception as e:
        print(f"❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
