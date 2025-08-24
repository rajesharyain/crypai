#!/usr/bin/env python3
"""
Test script for DeepSeek AI integration in CategorizeAgent
"""

import asyncio
import os
from dotenv import load_dotenv
from categorize_agent import CategorizeAgent

# Load environment variables
load_dotenv()

async def test_deepseek_integration():
    """Test DeepSeek AI integration"""
    print("🧪 Testing DeepSeek AI Integration in CategorizeAgent")
    print("=" * 60)
    
    # Check environment variables
    deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
    deepseek_base_url = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1')
    
    print(f"🔑 DeepSeek API Key: {'✅ Configured' if deepseek_api_key else '❌ Not configured'}")
    print(f"🌐 DeepSeek Base URL: {deepseek_base_url}")
    print()
    
    if not deepseek_api_key:
        print("⚠️  Please set DEEPSEEK_API_KEY in your .env file")
        print("   Example: DEEPSEEK_API_KEY=your_api_key_here")
        return
    
    # Test CategorizeAgent initialization with DeepSeek
    try:
        print("🚀 Initializing CategorizeAgent with DeepSeek AI...")
        agent = CategorizeAgent(model_type="deepseek")
        print(f"✅ Agent initialized successfully")
        print(f"📊 Current model: {agent.get_current_model()}")
        print(f"🔧 Available models: {agent.get_available_models()}")
        print()
        
        # Test model switching
        print("🔄 Testing model switching...")
        success = agent.switch_model("openai")
        print(f"Switch to OpenAI: {'✅ Success' if success else '❌ Failed'}")
        
        success = agent.switch_model("deepseek")
        print(f"Switch to DeepSeek: {'✅ Success' if success else '❌ Failed'}")
        print()
        
        # Test categorization with sample news
        print("📰 Testing news categorization with DeepSeek AI...")
        sample_news = {
            "title": "Bitcoin Surges to New All-Time High as Institutional Adoption Grows",
            "summary": "Bitcoin has reached a new all-time high of $75,000 as major institutions continue to invest in cryptocurrency. The surge comes amid growing adoption by traditional financial companies and positive regulatory developments.",
            "link": "https://example.com/bitcoin-surge",
            "published": "2025-01-27 10:00:00",
            "source": "Test Source",
            "category": "crypto"
        }
        
        print(f"📝 Sample news: {sample_news['title']}")
        print("⏳ Processing with DeepSeek AI...")
        
        categorized_item = await agent.categorize_news_item(sample_news)
        
        print("✅ Categorization completed!")
        print(f"🔍 Is Crypto News: {categorized_item.is_crypto_news}")
        print(f"📊 Relevance Score: {categorized_item.crypto_relevance_score}/10")
        print(f"🪙 Crypto Symbols: {[s['symbol'] for s in categorized_item.crypto_symbols]}")
        print(f"📈 News Category: {categorized_item.news_category}")
        print(f"😊 Sentiment: {categorized_item.sentiment}")
        print(f"🏷️ Key Topics: {categorized_item.key_topics}")
        print(f"🤖 Analysis Method: {categorized_item.analysis_method}")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_deepseek_integration())
