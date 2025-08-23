"""
Post Creator Agent for Social Media
Uses LangChain + OpenAI to create engaging social media posts based on news analysis and fundamentals
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from dotenv import load_dotenv

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, SystemMessage

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SocialPost:
    """Social media post structure"""
    content: str
    hashtags: List[str]
    emojis: List[str]
    character_count: int
    sentiment: str
    engagement_score: float
    platform: str
    created_at: str

# Pydantic models for API requests
from pydantic import BaseModel

class PostCreationRequest(BaseModel):
    """Request model for post creation"""
    analysis: Dict[str, Any]
    fundamentals: Optional[Dict[str, Any]] = None

class PostCreationResponse(BaseModel):
    """Response model for post creation"""
    success: bool
    posts: Optional[Dict[str, SocialPost]] = None
    error: Optional[str] = None

class BatchPostCreationRequest(BaseModel):
    """Request model for batch post creation"""
    news_items: List[Dict[str, Any]]
    fundamentals_data: Optional[List[Dict[str, Any]]] = None

class BatchPostCreationResponse(BaseModel):
    """Response model for batch post creation"""
    success: bool
    posts: List[Dict[str, SocialPost]]
    total_processed: int
    errors: List[str] = []

class PostCreatorAgent:
    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.7):
        """Initialize the Post Creator Agent with OpenAI model"""
        self.model_name = model_name
        self.temperature = temperature
        self.llm = None
        self.post_creation_prompt = None
        
        # Initialize OpenAI connection
        self._initialize_llm()
        self._create_prompts()
        
        if self.llm:
            logger.info(f"✅ PostCreatorAgent initialized with {model_name}")
        else:
            logger.warning("⚠️ PostCreatorAgent initialized without OpenAI - will use fallback post creation")

    def _initialize_llm(self):
        """Initialize the OpenAI language model"""
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key and api_key.strip():
                self.llm = ChatOpenAI(
                    model_name=self.model_name,
                    temperature=self.temperature,
                    openai_api_key=api_key,
                    max_tokens=800
                )
                logger.info(f"🔗 Connected to OpenAI {self.model_name}")
            else:
                logger.warning("⚠️ No OpenAI API key found - will use fallback post creation")
                self.llm = None
        except Exception as e:
            logger.error(f"❌ Error initializing OpenAI: {e}")
            self.llm = None

    def _create_prompts(self):
        """Create post creation prompts"""
        # Main post creation prompt
        self.post_creation_prompt = PromptTemplate(
            input_variables=["analysis", "fundamentals", "crypto_context"],
            template="""
You are a professional social media content creator specializing in cryptocurrency and financial content. Create engaging social media posts based on the provided analysis and market data.

ANALYSIS DATA:
{analysis}

MARKET FUNDAMENTALS:
{fundamentals}

CRYPTO CONTEXT:
{crypto_context}

Create social media posts for THREE platforms in the following JSON format:

{{
    "twitter": {{
        "content": "Twitter post content (max 280 characters, engaging and informative)",
        "hashtags": ["#crypto", "#bitcoin", "#trading", "#blockchain", "#defi"],
        "emojis": ["🚀", "📈", "💡"],
        "character_count": <exact_character_count>,
        "sentiment": "positive|negative|neutral",
        "engagement_score": <score_1_to_10>
    }},
    "linkedin": {{
        "content": "LinkedIn post content (professional, business-focused, can be longer)",
        "hashtags": ["#cryptocurrency", "#blockchain", "#investment", "#fintech", "#web3"],
        "emojis": ["💼", "📊", "🎯"],
        "character_count": <exact_character_count>,
        "sentiment": "positive|negative|neutral",
        "engagement_score": <score_1_to_10>
    }},
    "telegram": {{
        "content": "Telegram post content (community-focused, can include calls to action)",
        "hashtags": ["#crypto", "#community", "#trading", "#news"],
        "emojis": ["📱", "🔥", "💪"],
        "character_count": <exact_character_count>,
        "sentiment": "positive|negative|neutral",
        "engagement_score": <score_1_to_10>
    }}
}}

GUIDELINES:
1. Make content engaging and shareable
2. Use appropriate hashtags for each platform
3. Include relevant emojis to increase engagement
4. Ensure Twitter posts are under 280 characters
5. Make LinkedIn posts professional and business-oriented
6. Make Telegram posts community-focused
7. Match sentiment with the analysis
8. Include actionable insights when possible
9. Use platform-specific best practices

Be creative, informative, and engaging while maintaining professional credibility.
"""
        )

        # Crypto-specific post creation prompt
        self.crypto_post_prompt = PromptTemplate(
            input_variables=["crypto_symbol", "crypto_name", "news_analysis", "market_data", "sentiment"],
            template="""
You are a cryptocurrency social media expert. Create engaging posts about {crypto_name} ({crypto_symbol}) based on the latest news and market data.

CRYPTO: {crypto_symbol} ({crypto_name})
NEWS ANALYSIS: {news_analysis}
MARKET DATA: {market_data}
SENTIMENT: {sentiment}

Create platform-specific posts in this JSON format:

{{
    "twitter": {{
        "content": "Engaging Twitter post about {crypto_symbol} (max 280 chars)",
        "hashtags": ["#{crypto_symbol.lower()}", "#crypto", "#blockchain", "#trading"],
        "emojis": ["🚀", "📈", "💎"],
        "character_count": <exact_count>,
        "sentiment": "{sentiment}",
        "engagement_score": <1-10>
    }},
    "linkedin": {{
        "content": "Professional LinkedIn post about {crypto_symbol} market analysis",
        "hashtags": ["#{crypto_symbol.lower()}", "#cryptocurrency", "#investment", "#blockchain"],
        "emojis": ["💼", "📊", "🎯"],
        "character_count": <exact_count>,
        "sentiment": "{sentiment}",
        "engagement_score": <1-10>
    }},
    "telegram": {{
        "content": "Community-focused Telegram post about {crypto_symbol}",
        "hashtags": ["#{crypto_symbol.lower()}", "#crypto", "#community", "#news"],
        "emojis": ["📱", "🔥", "💪"],
        "character_count": <exact_count>,
        "sentiment": "{sentiment}",
        "engagement_score": <1-10>
    }}
}}

Focus on:
- Market insights and analysis
- Price action and trends
- Adoption and development news
- Community engagement
- Investment opportunities
- Risk awareness

Make each post platform-appropriate and engaging!
"""
        )

    async def create_social_posts(self, analysis: Dict[str, Any], fundamentals: Dict[str, Any] = None) -> Optional[Dict[str, SocialPost]]:
        """
        Create social media posts using OpenAI GPT-3.5-turbo
        """
        start_time = datetime.now()
        
        try:
            if not self.llm:
                logger.warning("🔄 OpenAI not available, using fallback post creation")
                return self._create_fallback_posts(analysis, fundamentals)

            # Extract crypto context from analysis
            crypto_context = self._extract_crypto_context(analysis)
            
            # Format fundamentals data
            fundamentals_text = self._format_fundamentals(fundamentals)
            
            # Create the prompt
            prompt = self.post_creation_prompt.format(
                analysis=json.dumps(analysis, indent=2),
                fundamentals=fundamentals_text,
                crypto_context=crypto_context
            )

            logger.info(f"📝 Creating social media posts for: {analysis.get('summary', 'Unknown news')[:50]}...")

            # Get response from OpenAI
            messages = [
                SystemMessage(content="You are a professional social media content creator. Always respond with valid JSON."),
                HumanMessage(content=prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            response_text = response.content

            # Parse JSON response
            try:
                posts_data = json.loads(response_text)
                
                # Validate required platforms
                required_platforms = ['twitter', 'linkedin', 'telegram']
                if not all(platform in posts_data for platform in required_platforms):
                    raise ValueError("Missing required platforms in response")

                # Create SocialPost objects
                created_posts = {}
                for platform in required_platforms:
                    platform_data = posts_data[platform]
                    
                    # Validate platform data
                    if not all(field in platform_data for field in ['content', 'hashtags', 'emojis']):
                        logger.warning(f"⚠️ Incomplete data for {platform}, using fallback")
                        platform_data = self._create_fallback_platform_post(platform, analysis, fundamentals)
                    
                    post = SocialPost(
                        content=platform_data['content'],
                        hashtags=platform_data.get('hashtags', []),
                        emojis=platform_data.get('emojis', []),
                        character_count=platform_data.get('character_count', len(platform_data['content'])),
                        sentiment=platform_data.get('sentiment', 'neutral'),
                        engagement_score=platform_data.get('engagement_score', 5.0),
                        platform=platform,
                        created_at=datetime.utcnow().isoformat()
                    )
                    
                    created_posts[platform] = post

                logger.info(f"✅ Social media posts created successfully")
                return created_posts

            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse JSON response: {e}")
                logger.error(f"Raw response: {response_text}")
                return self._create_fallback_posts(analysis, fundamentals)

        except Exception as e:
            logger.error(f"❌ Error during post creation: {e}")
            return self._create_fallback_posts(analysis, fundamentals)

    async def create_crypto_specific_posts(self, crypto_symbol: str, crypto_name: str, news_analysis: Dict[str, Any], market_data: Dict[str, Any] = None) -> Optional[Dict[str, SocialPost]]:
        """
        Create crypto-specific social media posts
        """
        try:
            if not self.llm:
                return self._create_fallback_posts(news_analysis, market_data)

            # Format market data
            market_text = self._format_market_data(market_data)
            
            # Create crypto-specific prompt
            prompt = self.crypto_post_prompt.format(
                crypto_symbol=crypto_symbol,
                crypto_name=crypto_name,
                news_analysis=json.dumps(news_analysis, indent=2),
                market_data=market_text,
                sentiment=news_analysis.get('sentiment', 'neutral')
            )

            logger.info(f"📝 Creating {crypto_symbol}-specific social media posts...")

            # Get response from OpenAI
            messages = [
                SystemMessage(content="You are a cryptocurrency social media expert. Always respond with valid JSON."),
                HumanMessage(content=prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            response_text = response.content

            # Parse and create posts
            try:
                posts_data = json.loads(response_text)
                
                created_posts = {}
                for platform in ['twitter', 'linkedin', 'telegram']:
                    if platform in posts_data:
                        platform_data = posts_data[platform]
                        
                        post = SocialPost(
                            content=platform_data['content'],
                            hashtags=platform_data.get('hashtags', []),
                            emojis=platform_data.get('emojis', []),
                            character_count=platform_data.get('character_count', len(platform_data['content'])),
                            sentiment=platform_data.get('sentiment', 'neutral'),
                            engagement_score=platform_data.get('engagement_score', 5.0),
                            platform=platform,
                            created_at=datetime.utcnow().isoformat()
                        )
                        
                        created_posts[platform] = post

                logger.info(f"✅ {crypto_symbol}-specific posts created successfully")
                return created_posts

            except json.JSONDecodeError:
                return await self.create_social_posts(news_analysis, market_data)

        except Exception as e:
            logger.error(f"❌ Error in crypto-specific post creation: {e}")
            return await self.create_social_posts(news_analysis, market_data)

    def _extract_crypto_context(self, analysis: Dict[str, Any]) -> str:
        """Extract crypto context from analysis"""
        crypto_context = []
        
        # Extract from crypto_impact if available
        if 'crypto_impact' in analysis:
            crypto_impact = analysis['crypto_impact']
            
            # Get crypto symbols
            if 'crypto_symbols' in crypto_impact:
                symbols = [f"{s['symbol']} ({s['name']})" for s in crypto_impact['crypto_symbols']]
                crypto_context.append(f"Cryptocurrencies: {', '.join(symbols)}")
            
            # Get market sentiment
            if 'market_sentiment' in crypto_impact:
                crypto_context.append(f"Market Sentiment: {crypto_impact['market_sentiment']}")
            
            # Get key insights
            if 'key_insights' in crypto_impact:
                insights = crypto_impact['key_insights'][:3]  # Limit to 3 insights
                crypto_context.append(f"Key Insights: {', '.join(insights)}")
        
        # Extract from primary crypto if available
        if 'primary_crypto' in analysis:
            primary = analysis['primary_crypto']
            crypto_context.append(f"Primary Focus: {primary['symbol']} ({primary['name']})")
        
        return "\n".join(crypto_context) if crypto_context else "General cryptocurrency news"

    def _format_fundamentals(self, fundamentals: Dict[str, Any]) -> str:
        """Format fundamentals data for prompt"""
        if not fundamentals:
            return "No market data available"
        
        try:
            return f"""
Current Price: ${fundamentals.get('current_price', 'N/A')}
24h Change: {fundamentals.get('price_change_24h', 'N/A')}%
Market Cap Rank: #{fundamentals.get('market_cap_rank', 'N/A')}
Volume 24h: ${fundamentals.get('volume_24h', 'N/A'):,.0f}
Market Cap: ${fundamentals.get('market_cap', 'N/A'):,.0f}
"""
        except:
            return "Market data available but formatting error"

    def _format_market_data(self, market_data: Dict[str, Any]) -> str:
        """Format market data for crypto-specific prompts"""
        if not market_data:
            return "No market data available"
        
        try:
            return f"""
Price: ${market_data.get('current_price', 'N/A')}
24h Change: {market_data.get('price_change_24h', 'N/A')}%
Market Cap Rank: #{market_data.get('market_cap_rank', 'N/A')}
Volume: ${market_data.get('volume_24h', 'N/A'):,.0f}
"""
        except:
            return "Market data available"

    def _create_fallback_posts(self, analysis: Dict[str, Any], fundamentals: Dict[str, Any] = None) -> Dict[str, SocialPost]:
        """Create fallback posts when OpenAI is not available"""
        logger.info("🔄 Using fallback post creation")
        
        # Extract basic info
        summary = analysis.get('summary', 'Cryptocurrency news analysis')
        sentiment = analysis.get('sentiment', 'neutral')
        
        # Create basic posts for each platform
        posts = {}
        
        # Twitter post
        twitter_content = f"📰 {summary[:200]}... #crypto #blockchain #trading"
        posts['twitter'] = SocialPost(
            content=twitter_content,
            hashtags=['#crypto', '#blockchain', '#trading', '#defi'],
            emojis=['📰', '🚀', '💡'],
            character_count=len(twitter_content),
            sentiment=sentiment,
            engagement_score=5.0,
            platform='twitter',
            created_at=datetime.utcnow().isoformat()
        )
        
        # LinkedIn post
        linkedin_content = f"💼 Market Analysis: {summary}\n\n📊 Cryptocurrency market insights and analysis.\n\n#cryptocurrency #blockchain #investment #fintech"
        posts['linkedin'] = SocialPost(
            content=linkedin_content,
            hashtags=['#cryptocurrency', '#blockchain', '#investment', '#fintech', '#web3'],
            emojis=['💼', '📊', '🎯'],
            character_count=len(linkedin_content),
            sentiment=sentiment,
            engagement_score=6.0,
            platform='linkedin',
            created_at=datetime.utcnow().isoformat()
        )
        
        # Telegram post
        telegram_content = f"📱 {summary}\n\n🔥 Join our community for more crypto insights!\n\n#crypto #community #trading #news"
        posts['telegram'] = SocialPost(
            content=telegram_content,
            hashtags=['#crypto', '#community', '#trading', '#news'],
            emojis=['📱', '🔥', '💪'],
            character_count=len(telegram_content),
            sentiment=sentiment,
            engagement_score=5.5,
            platform='telegram',
            created_at=datetime.utcnow().isoformat()
        )
        
        return posts

    def _create_fallback_platform_post(self, platform: str, analysis: Dict[str, Any], fundamentals: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create fallback post for a specific platform"""
        summary = analysis.get('summary', 'Cryptocurrency news')
        sentiment = analysis.get('sentiment', 'neutral')
        
        if platform == 'twitter':
            return {
                'content': f"📰 {summary[:200]}... #crypto #blockchain",
                'hashtags': ['#crypto', '#blockchain', '#trading'],
                'emojis': ['📰', '🚀'],
                'character_count': 200,
                'sentiment': sentiment,
                'engagement_score': 5.0
            }
        elif platform == 'linkedin':
            return {
                'content': f"💼 {summary}\n\n#cryptocurrency #blockchain #investment",
                'hashtags': ['#cryptocurrency', '#blockchain', '#investment'],
                'emojis': ['💼', '📊'],
                'character_count': len(summary) + 50,
                'sentiment': sentiment,
                'engagement_score': 6.0
            }
        else:  # telegram
            return {
                'content': f"📱 {summary}\n\n#crypto #community",
                'hashtags': ['#crypto', '#community'],
                'emojis': ['📱', '🔥'],
                'character_count': len(summary) + 30,
                'sentiment': sentiment,
                'engagement_score': 5.5
            }

    async def create_multiple_posts(self, news_items: List[Dict[str, Any]], fundamentals_data: List[Dict[str, Any]] = None) -> List[Dict[str, SocialPost]]:
        """
        Create posts for multiple news items
        """
        logger.info(f"📝 Starting batch post creation for {len(news_items)} news items")
        
        results = []
        for i, news_item in enumerate(news_items):
            try:
                # Get fundamentals for this news item if available
                fundamentals = None
                if fundamentals_data and i < len(fundamentals_data):
                    fundamentals = fundamentals_data[i]
                
                # Check if this is crypto-specific news
                if news_item.get('crypto_symbols') and news_item.get('primary_crypto'):
                    primary_crypto = news_item['primary_crypto']
                    posts = await self.create_crypto_specific_posts(
                        primary_crypto['symbol'],
                        primary_crypto['name'],
                        news_item,
                        fundamentals
                    )
                else:
                    posts = await self.create_social_posts(news_item, fundamentals)
                
                if posts:
                    results.append(posts)
                    logger.info(f"✅ Completed post creation {i+1}/{len(news_items)}")
                
            except Exception as e:
                logger.error(f"❌ Error creating posts for news item {i+1}: {e}")
                # Create fallback posts
                fallback_posts = self._create_fallback_posts(news_item, fundamentals)
                results.append(fallback_posts)

        logger.info(f"✅ Completed post creation for {len(results)} news items")
        return results

    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "model": self.model_name,
            "temperature": self.temperature,
            "llm_initialized": self.llm is not None,
            "openai_key_configured": bool(os.getenv('OPENAI_API_KEY')),
            "status": "ready" if self.llm else "fallback_mode"
        }
