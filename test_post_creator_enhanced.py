#!/usr/bin/env python3
"""
Enhanced test script for Post Creator Agent
Tests integration with enhanced crypto data from ingestion and analyzer agents
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

async def test_post_creator_enhanced():
    """Test post creator agent with enhanced crypto data"""
    
    print("🧪 Testing Post Creator Agent with Enhanced Crypto Data")
    print("=" * 70)
    
    # Import the post creator agent
    try:
        from post_creator import PostCreatorAgent, SocialPost
        print("✅ Post creator agent imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import post creator agent: {e}")
        return
    
    # Test data from ingestion and analyzer agents (simulated enhanced data)
    test_analysis_data = [
        {
            "title": "Bitcoin Surges Past $50,000 as Institutional Adoption Grows",
            "summary": "Bitcoin has reached a new milestone, crossing the $50,000 mark for the first time since 2021. Major financial institutions including BlackRock and Fidelity have increased their Bitcoin holdings, signaling growing institutional confidence in the cryptocurrency market.",
            "sentiment": 0.8,
            "fundamentals": "positive",
            "confidence": 0.85,
            "crypto_impact": {
                "market_sentiment": "bullish",
                "price_impact": "positive",
                "crypto_symbols": [
                    {
                        "symbol": "BTC",
                        "name": "Bitcoin",
                        "relevance_score": 9.8,
                        "mentions": 4,
                        "context": "Bitcoin price surge and institutional adoption"
                    }
                ],
                "market_trend": "institutional_inflow",
                "risk_level": "low"
            },
            "model_used": "gpt-3.5-turbo",
            "processing_time": 2.3
        },
        {
            "title": "Ethereum Layer 2 Solutions See Record Growth in TVL",
            "summary": "Ethereum's Layer 2 scaling solutions have achieved unprecedented growth, with total value locked (TVL) reaching new heights. Arbitrum, Optimism, and Polygon are leading the charge, offering faster and cheaper transactions.",
            "sentiment": 0.6,
            "fundamentals": "positive",
            "confidence": 0.78,
            "crypto_impact": {
                "market_sentiment": "bullish",
                "price_impact": "positive",
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
                "market_trend": "defi_growth",
                "risk_level": "medium"
            },
            "model_used": "gpt-3.5-turbo",
            "processing_time": 1.9
        },
        {
            "title": "Stablecoin Market Faces Regulatory Scrutiny",
            "summary": "Global regulators are intensifying their oversight of the stablecoin market, particularly focusing on USDT and USDC. Concerns about reserve backing and potential systemic risks have prompted calls for stricter regulations.",
            "sentiment": -0.4,
            "fundamentals": "negative",
            "confidence": 0.72,
            "crypto_impact": {
                "market_sentiment": "bearish",
                "price_impact": "negative",
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
                "market_trend": "regulatory_pressure",
                "risk_level": "high"
            },
            "model_used": "gpt-3.5-turbo",
            "processing_time": 2.1
        }
    ]
    
    # Test fundamentals data
    test_fundamentals_data = [
        {
            "symbol": "BTC",
            "name": "Bitcoin",
            "current_price_usd": 115257.00,
            "price_change_percentage_24h": -1.24,
            "market_cap_rank": 1,
            "market_cap": 2294885478039,
            "volume_24h": 25655625435,
            "ath": 124128.00
        },
        {
            "symbol": "ETH",
            "name": "Ethereum",
            "current_price_usd": 4790.79,
            "price_change_percentage_24h": -0.66,
            "market_cap_rank": 2,
            "market_cap": 578237485496,
            "volume_24h": 27477673800,
            "ath": 4878.26
        }
    ]
    
    print(f"\n📰 Testing with {len(test_analysis_data)} enhanced analysis items")
    print(f"💰 Testing with {len(test_fundamentals_data)} fundamentals data items")
    
    # Initialize the post creator agent
    post_creator = PostCreatorAgent()
    print(f"✅ Post creator agent initialized: {post_creator.get_status()}")
    
    # Test 1: Individual post creation with crypto analysis
    print("\n🔍 Test 1: Individual post creation with crypto analysis")
    print("-" * 60)
    
    for i, analysis in enumerate(test_analysis_data, 1):
        print(f"\n📱 Creating posts for analysis {i}: {analysis['title'][:50]}...")
        print(f"   Sentiment: {analysis['sentiment']:.2f}, Fundamentals: {analysis['fundamentals']}")
        print(f"   Crypto Symbols: {len(analysis['crypto_impact']['crypto_symbols'])} detected")
        
        try:
            # Test post creation with analysis only
            posts = await post_creator.create_social_posts(analysis)
            
            if posts:
                print(f"  ✅ Posts created successfully:")
                for platform, post in posts.items():
                    print(f"    {platform.upper()}:")
                    print(f"      Content: {post.content[:80]}...")
                    print(f"      Hashtags: {', '.join(post.hashtags[:3])}")
                    print(f"      Emojis: {', '.join(post.emojis[:3])}")
                    print(f"      Characters: {post.character_count}")
                    print(f"      Sentiment: {post.sentiment}")
                    print(f"      Engagement Score: {post.engagement_score:.2f}")
            else:
                print(f"  ❌ Post creation failed")
                
        except Exception as e:
            print(f"  ❌ Post creation error: {e}")
    
    # Test 2: Post creation with analysis + fundamentals
    print("\n🔍 Test 2: Post creation with analysis + fundamentals")
    print("-" * 60)
    
    for i, analysis in enumerate(test_analysis_data[:2], 1):  # Test first 2
        fundamentals = test_fundamentals_data[i-1] if i <= len(test_fundamentals_data) else None
        
        print(f"\n💰 Creating posts with fundamentals for {analysis['crypto_impact']['crypto_symbols'][0]['name']}")
        if fundamentals:
            print(f"   Price: ${fundamentals['current_price_usd']:,.2f}, 24h: {fundamentals['price_change_percentage_24h']:+.2f}%")
        
        try:
            # Test post creation with analysis + fundamentals
            posts = await post_creator.create_social_posts(analysis, fundamentals)
            
            if posts:
                print(f"  ✅ Posts with fundamentals created:")
                for platform, post in posts.items():
                    print(f"    {platform.upper()}: {post.content[:60]}...")
                    print(f"      Engagement: {post.engagement_score:.2f}")
            else:
                print(f"  ❌ Post creation with fundamentals failed")
                
        except Exception as e:
            print(f"  ❌ Post creation with fundamentals error: {e}")
    
    # Test 3: Crypto-specific post creation
    print("\n🔍 Test 3: Crypto-specific post creation")
    print("-" * 60)
    
    for i, analysis in enumerate(test_analysis_data[:2], 1):
        primary_crypto = analysis['crypto_impact']['crypto_symbols'][0]
        fundamentals = test_fundamentals_data[i-1] if i <= len(test_fundamentals_data) else None
        
        print(f"\n🎯 Crypto-specific posts for {primary_crypto['name']} ({primary_crypto['symbol']})")
        print(f"   Relevance: {primary_crypto['relevance_score']}, Context: {primary_crypto['context']}")
        
        try:
            # Test crypto-specific post creation
            posts = await post_creator.create_crypto_specific_posts(
                primary_crypto['symbol'],
                primary_crypto['name'],
                analysis,
                fundamentals
            )
            
            if posts:
                print(f"  ✅ Crypto-specific posts created:")
                for platform, post in posts.items():
                    print(f"    {platform.upper()}: {post.content[:70]}...")
                    print(f"      Hashtags: {', '.join(post.hashtags[:3])}")
                    print(f"      Engagement: {post.engagement_score:.2f}")
            else:
                print(f"  ❌ Crypto-specific post creation failed")
                
        except Exception as e:
            print(f"  ❌ Crypto-specific post creation error: {e}")
    
    # Test 4: Batch post creation
    print("\n🔍 Test 4: Batch post creation")
    print("-" * 60)
    
    try:
        print(f"Processing {len(test_analysis_data)} analysis items in batch...")
        
        # Test batch post creation
        batch_posts = await post_creator.create_multiple_posts(
            test_analysis_data,
            test_fundamentals_data
        )
        
        if batch_posts:
            print(f"✅ Batch post creation successful: {len(batch_posts)} results")
            
            # Show summary of each result
            for i, posts in enumerate(batch_posts, 1):
                if posts:
                    platforms = list(posts.keys())
                    print(f"  Result {i}: {len(platforms)} platforms ({', '.join(platforms)})")
                    for platform, post in posts.items():
                        print(f"    {platform}: {post.engagement_score:.2f} engagement")
                else:
                    print(f"  Result {i}: No posts created")
                    
        else:
            print("❌ Batch post creation failed")
            
    except Exception as e:
        print(f"❌ Batch post creation error: {e}")
    
    # Test 5: Fallback post creation (when OpenAI fails)
    print("\n🔍 Test 5: Fallback post creation testing")
    print("-" * 60)
    
    # Test with a simple analysis item
    test_analysis = {
        "title": "Crypto Market Shows Mixed Signals",
        "summary": "The cryptocurrency market is experiencing mixed signals with some coins gaining while others decline.",
        "sentiment": 0.0,
        "fundamentals": "neutral",
        "confidence": 0.5,
        "crypto_impact": {
            "market_sentiment": "neutral",
            "price_impact": "neutral",
            "crypto_symbols": []
        }
    }
    
    try:
        # This should trigger fallback if OpenAI is not available
        fallback_posts = await post_creator.create_social_posts(test_analysis)
        
        if fallback_posts:
            print(f"✅ Fallback post creation successful:")
            for platform, post in fallback_posts.items():
                print(f"    {platform.upper()}: {post.content[:60]}...")
                print(f"      Model Used: {getattr(post, 'model_used', 'fallback')}")
        else:
            print("❌ Fallback post creation failed")
            
    except Exception as e:
        print(f"❌ Fallback post creation error: {e}")
    
    print("\n🎉 Post creator agent testing completed!")

if __name__ == "__main__":
    asyncio.run(test_post_creator_enhanced())
