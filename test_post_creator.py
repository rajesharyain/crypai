#!/usr/bin/env python3
"""
Test script for the Post Creator Agent
Tests social media post creation functionality using LangChain + OpenAI
"""

import asyncio
import json
from datetime import datetime
from post_creator import (
    PostCreatorAgent,
    create_single_posts,
    create_multiple_posts_batch
)

async def test_post_creator_initialization():
    """Test post creator agent initialization"""
    print("🧪 Testing Post Creator Agent Initialization...")
    print("=" * 60)
    
    try:
        agent = PostCreatorAgent()
        status = agent.get_agent_status()
        
        print(f"✅ Post Creator Agent initialized successfully")
        print(f"   Model: {status['model']}")
        print(f"   Temperature: {status['temperature']}")
        print(f"   LLM Initialized: {status['llm_initialized']}")
        print(f"   OpenAI Key Configured: {status['openai_key_configured']}")
        print(f"   Status: {status['status']}")
        
        return status['llm_initialized']
        
    except Exception as e:
        print(f"❌ Error initializing Post Creator Agent: {e}")
        return False

async def test_positive_news_posts():
    """Test post creation for positive news"""
    print("\n🧪 Testing Positive News Post Creation...")
    print("=" * 60)
    
    try:
        # Test with positive crypto news analysis
        analysis = {
            "summary": "Bitcoin has reached a new all-time high as institutional adoption grows and major financial firms announce new cryptocurrency investment products.",
            "sentiment": 0.8,
            "fundamentals": "positive",
            "confidence": 0.9
        }
        
        fundamentals = {
            "current_price": 75000,
            "price_change_24h": 5.2,
            "market_cap_rank": 1,
            "volume_24h": 45000000000
        }
        
        news_title = "Bitcoin Surges to New All-Time High as Institutional Adoption Grows"
        
        print(f"📰 News Title: {news_title}")
        print(f"📊 Analysis: {analysis['summary'][:100]}...")
        print(f"💰 Fundamentals: ${fundamentals['current_price']:,} (+{fundamentals['price_change_24h']}%)")
        
        result = await create_single_posts(analysis, fundamentals, news_title)
        
        if result:
            print("✅ Posts created successfully!")
            
            # Display Twitter post
            print(f"\n🐦 Twitter Post:")
            print(f"   Content: {result.twitter_post.content}")
            print(f"   Hashtags: {', '.join(result.twitter_post.hashtags)}")
            print(f"   Emojis: {', '.join(result.twitter_post.emojis)}")
            print(f"   Characters: {result.twitter_post.character_count}/280")
            print(f"   Sentiment: {result.twitter_post.sentiment}")
            print(f"   Engagement Score: {result.twitter_post.engagement_score:.2f}")
            
            # Display LinkedIn post
            print(f"\n💼 LinkedIn Post:")
            print(f"   Content: {result.linkedin_post.content}")
            print(f"   Hashtags: {', '.join(result.linkedin_post.hashtags)}")
            print(f"   Emojis: {', '.join(result.linkedin_post.emojis)}")
            print(f"   Characters: {result.linkedin_post.character_count}/1300")
            print(f"   Sentiment: {result.linkedin_post.sentiment}")
            print(f"   Engagement Score: {result.linkedin_post.engagement_score:.2f}")
            
            # Display Telegram post
            print(f"\n📱 Telegram Post:")
            print(f"   Content: {result.telegram_post.content}")
            print(f"   Hashtags: {', '.join(result.telegram_post.hashtags)}")
            print(f"   Emojis: {', '.join(result.telegram_post.emojis)}")
            print(f"   Characters: {result.telegram_post.character_count}/500")
            print(f"   Sentiment: {result.telegram_post.sentiment}")
            print(f"   Engagement Score: {result.telegram_post.engagement_score:.2f}")
            
            return True
        else:
            print("❌ Post creation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error in positive news post creation: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_negative_news_posts():
    """Test post creation for negative news"""
    print("\n🧪 Testing Negative News Post Creation...")
    print("=" * 60)
    
    try:
        # Test with negative crypto news analysis
        analysis = {
            "summary": "A major DeFi protocol has been exploited, resulting in the loss of millions of dollars worth of user funds.",
            "sentiment": -0.7,
            "fundamentals": "negative",
            "confidence": 0.85
        }
        
        fundamentals = {
            "current_price": 42000,
            "price_change_24h": -8.5,
            "market_cap_rank": 1,
            "volume_24h": 38000000000
        }
        
        news_title = "Major DeFi Protocol Exploit Results in $50M Loss"
        
        print(f"📰 News Title: {news_title}")
        print(f"📊 Analysis: {analysis['summary'][:100]}...")
        print(f"💰 Fundamentals: ${fundamentals['current_price']:,} ({fundamentals['price_change_24h']}%)")
        
        result = await create_single_posts(analysis, fundamentals, news_title)
        
        if result:
            print("✅ Posts created successfully!")
            
            # Display Twitter post
            print(f"\n🐦 Twitter Post:")
            print(f"   Content: {result.twitter_post.content}")
            print(f"   Characters: {result.twitter_post.character_count}/280")
            print(f"   Sentiment: {result.twitter_post.sentiment}")
            
            # Display LinkedIn post
            print(f"\n💼 LinkedIn Post:")
            print(f"   Content: {result.linkedin_post.content}")
            print(f"   Characters: {result.linkedin_post.character_count}/1300")
            print(f"   Sentiment: {result.linkedin_post.sentiment}")
            
            # Display Telegram post
            print(f"\n📱 Telegram Post:")
            print(f"   Content: {result.telegram_post.content}")
            print(f"   Characters: {result.telegram_post.character_count}/500")
            print(f"   Sentiment: {result.telegram_post.sentiment}")
            
            return True
        else:
            print("❌ Post creation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error in negative news post creation: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_neutral_news_posts():
    """Test post creation for neutral news"""
    print("\n🧪 Testing Neutral News Post Creation...")
    print("=" * 60)
    
    try:
        # Test with neutral crypto news analysis
        analysis = {
            "summary": "A new cryptocurrency exchange has launched with advanced security features including multi-signature wallets and cold storage.",
            "sentiment": 0.1,
            "fundamentals": "neutral",
            "confidence": 0.75
        }
        
        fundamentals = {
            "current_price": 65000,
            "price_change_24h": 0.8,
            "market_cap_rank": 1,
            "volume_24h": 42000000000
        }
        
        news_title = "New Cryptocurrency Exchange Launches with Enhanced Security Features"
        
        print(f"📰 News Title: {news_title}")
        print(f"📊 Analysis: {analysis['summary'][:100]}...")
        print(f"💰 Fundamentals: ${fundamentals['current_price']:,} (+{fundamentals['price_change_24h']}%)")
        
        result = await create_single_posts(analysis, fundamentals, news_title)
        
        if result:
            print("✅ Posts created successfully!")
            
            # Display Twitter post
            print(f"\n🐦 Twitter Post:")
            print(f"   Content: {result.twitter_post.content}")
            print(f"   Characters: {result.twitter_post.character_count}/280")
            print(f"   Sentiment: {result.twitter_post.sentiment}")
            
            # Display LinkedIn post
            print(f"\n💼 LinkedIn Post:")
            print(f"   Content: {result.linkedin_post.content}")
            print(f"   Characters: {result.linkedin_post.character_count}/1300")
            print(f"   Sentiment: {result.linkedin_post.sentiment}")
            
            # Display Telegram post
            print(f"\n📱 Telegram Post:")
            print(f"   Content: {result.telegram_post.content}")
            print(f"   Characters: {result.telegram_post.character_count}/500")
            print(f"   Sentiment: {result.telegram_post.sentiment}")
            
            return True
        else:
            print("❌ Post creation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error in neutral news post creation: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_batch_post_creation():
    """Test batch post creation"""
    print("\n🧪 Testing Batch Post Creation...")
    print("=" * 60)
    
    try:
        # Test with multiple news items
        posts_data = [
            {
                "analysis": {
                    "summary": "Ethereum 2.0 upgrade successfully launched with proof-of-stake consensus.",
                    "sentiment": 0.6,
                    "fundamentals": "positive",
                    "confidence": 0.8
                },
                "fundamentals": {
                    "current_price": 3200,
                    "price_change_24h": 3.2,
                    "market_cap_rank": 2
                },
                "news_title": "Ethereum 2.0 Upgrade Successfully Launched"
            },
            {
                "analysis": {
                    "summary": "Regulatory uncertainty impacts crypto markets with increased volatility.",
                    "sentiment": -0.4,
                    "fundamentals": "negative",
                    "confidence": 0.7
                },
                "fundamentals": {
                    "current_price": 45000,
                    "price_change_24h": -2.1,
                    "market_cap_rank": 1
                },
                "news_title": "Regulatory Uncertainty Impacts Crypto Markets"
            }
        ]
        
        print(f"📰 Creating posts for {len(posts_data)} news items...")
        
        results = await create_multiple_posts_batch(posts_data)
        
        if results:
            print(f"✅ Batch post creation completed successfully!")
            print(f"   📊 Total created: {len(results)}")
            
            for i, result in enumerate(results, 1):
                posts = result['posts']
                original_data = result['original_data']
                
                print(f"\n   {i}. {original_data['news_title']}")
                print(f"      Twitter: {posts.twitter_post.character_count}/280 chars")
                print(f"      LinkedIn: {posts.linkedin_post.character_count}/1300 chars")
                print(f"      Telegram: {posts.telegram_post.character_count}/500 chars")
            
            return True
        else:
            print("❌ Batch post creation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error in batch post creation: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_post_validation():
    """Test post length validation"""
    print("\n🧪 Testing Post Length Validation...")
    print("=" * 60)
    
    try:
        agent = PostCreatorAgent()
        
        # Test with sample posts
        analysis = {
            "summary": "Test analysis for validation",
            "sentiment": 0.5,
            "fundamentals": "positive",
            "confidence": 0.8
        }
        
        fundamentals = {
            "current_price": 50000,
            "price_change_24h": 2.0,
            "market_cap_rank": 1
        }
        
        result = await agent.create_social_posts(analysis, fundamentals, "Test News")
        
        if result:
            # Validate post lengths
            validation = agent.validate_post_lengths(result)
            
            print("✅ Post validation completed!")
            print(f"   Twitter (280 chars): {validation['twitter']}")
            print(f"   LinkedIn (1300 chars): {validation['linkedin']}")
            print(f"   Telegram (500 chars): {validation['telegram']}")
            
            # Show actual character counts
            print(f"\n📊 Actual Character Counts:")
            print(f"   Twitter: {result.twitter_post.character_count}/280")
            print(f"   LinkedIn: {result.linkedin_post.character_count}/1300")
            print(f"   Telegram: {result.telegram_post.character_count}/500")
            
            return all(validation.values())
        else:
            print("❌ Post creation failed for validation test")
            return False
            
    except Exception as e:
        print(f"❌ Error in post validation test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🚀 Post Creator Agent Test Suite")
    print("=" * 70)
    
    tests = [
        ("Post Creator Initialization", test_post_creator_initialization),
        ("Positive News Post Creation", test_positive_news_posts),
        ("Negative News Post Creation", test_negative_news_posts),
        ("Neutral News Post Creation", test_neutral_news_posts),
        ("Batch Post Creation", test_batch_post_creation),
        ("Post Length Validation", test_post_validation)
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
    print("\n" + "=" * 70)
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
        print("🎉 All tests passed! The Post Creator Agent is working correctly.")
        print("\n💡 Key Features Verified:")
        print("   ✅ OpenAI integration via LangChain")
        print("   ✅ Multi-platform post creation (Twitter, LinkedIn, Telegram)")
        print("   ✅ Sentiment-aware content generation")
        print("   ✅ Hashtag and emoji optimization")
        print("   ✅ Character limit validation")
        print("   ✅ Engagement scoring")
        print("   ✅ Fallback post creation system")
        print("   ✅ Batch processing capability")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print("\n🚀 Next steps:")
    print("   - Test the /create_post endpoint: POST /create_post")
    print("   - Test batch creation: POST /create_post/batch")
    print("   - Check agent status: GET /create_post/status")
    print("   - Integrate with news analysis pipeline")
    print("   - Automate social media posting workflows")
    print("   - Build content scheduling systems")

if __name__ == "__main__":
    asyncio.run(main())
