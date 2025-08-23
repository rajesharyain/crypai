"""
Post Creator Agent for Social Media
Uses LangChain + OpenAI to create engaging social media posts based on news analysis and fundamentals
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Import LangChain components
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from langchain.prompts import PromptTemplate

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SocialPost:
    """Individual social media post"""
    platform: str
    content: str
    hashtags: List[str]
    emojis: List[str]
    character_count: int
    sentiment: str
    engagement_score: float

@dataclass
class PostCreationResult:
    """Result of post creation"""
    twitter_post: SocialPost
    linkedin_post: SocialPost
    telegram_post: SocialPost
    creation_timestamp: str
    analysis_summary: str

class PostCreatorAgent:
    """AI-powered social media post creator using LangChain + OpenAI"""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.7):
        self.model_name = model_name
        self.temperature = temperature
        self.llm = None
        self._initialize_llm()
        
        # Define the post creation prompt
        self.post_creation_prompt = PromptTemplate(
            input_variables=["analysis", "fundamentals", "news_title"],
            template="""You are a financial social media expert. Create engaging social media posts based on this crypto/financial news analysis:

News Title: {news_title}

Analysis Summary: {analysis}

Fundamentals Data: {fundamentals}

Create 3 social media posts in the following JSON format:
{{
    "twitter": {{
        "content": "Engaging tweet with key insights, max 280 characters including hashtags and emojis",
        "hashtags": ["#crypto", "#bitcoin", "#finance"],
        "emojis": ["🚀", "📈", "💡"],
        "sentiment": "positive|negative|neutral",
        "engagement_score": 0.85
    }},
    "linkedin": {{
        "content": "Professional LinkedIn post with business insights, max 1300 characters",
        "hashtags": ["#cryptocurrency", "#blockchain", "#investment"],
        "emojis": ["📊", "💼", "🎯"],
        "sentiment": "positive|negative|neutral",
        "engagement_score": 0.90
    }},
    "telegram": {{
        "content": "Informative Telegram message with community focus, max 500 characters",
        "hashtags": ["#crypto", "#trading", "#community"],
        "emojis": ["🔥", "📱", "👥"],
        "sentiment": "positive|negative|neutral",
        "engagement_score": 0.88
    }}
}}

Guidelines:
1. Twitter: Concise, trending hashtags, viral potential
2. LinkedIn: Professional tone, business insights, industry hashtags
3. Telegram: Community-focused, informative, engaging

Focus on:
- Key market insights
- Actionable information
- Platform-appropriate tone
- Relevant hashtags and emojis
- Engagement optimization

Return ONLY valid JSON, no additional text."""
        )
    
    def _initialize_llm(self):
        """Initialize the OpenAI LLM via LangChain"""
        try:
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                logger.warning("OpenAI API key not found. Post Creator will not function properly.")
                return
            
            self.llm = ChatOpenAI(
                model_name=self.model_name,
                temperature=self.temperature,
                openai_api_key=openai_api_key
            )
            logger.info(f"✅ PostCreatorAgent initialized with {self.model_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize PostCreatorAgent: {e}")
            self.llm = None
    
    async def create_social_posts(
        self, 
        analysis: Dict[str, Any], 
        fundamentals: Dict[str, Any],
        news_title: str = ""
    ) -> Optional[PostCreationResult]:
        """Create social media posts based on analysis and fundamentals"""
        if not self.llm:
            logger.error("LLM not initialized. Cannot create posts.")
            return None
        
        try:
            # Format the prompt with the data
            formatted_prompt = self.post_creation_prompt.format(
                analysis=json.dumps(analysis, indent=2),
                fundamentals=json.dumps(fundamentals, indent=2),
                news_title=news_title or "Crypto Market Update"
            )
            
            # Create the message for LangChain
            message = HumanMessage(content=formatted_prompt)
            
            # Get response from OpenAI
            logger.info(f"📝 Creating social media posts for: {news_title[:50]}...")
            response = await self.llm.ainvoke([message])
            
            # Parse the JSON response
            try:
                posts_data = json.loads(response.content.strip())
                
                # Validate the response structure
                required_platforms = ["twitter", "linkedin", "telegram"]
                if not all(platform in posts_data for platform in required_platforms):
                    logger.warning("Incomplete posts response, using fallback")
                    return self._create_fallback_posts(analysis, fundamentals, news_title)
                
                # Create social post objects
                twitter_post = self._create_social_post_object("twitter", posts_data["twitter"])
                linkedin_post = self._create_social_post_object("linkedin", posts_data["linkedin"])
                telegram_post = self._create_social_post_object("telegram", posts_data["telegram"])
                
                # Create result
                result = PostCreationResult(
                    twitter_post=twitter_post,
                    linkedin_post=linkedin_post,
                    telegram_post=telegram_post,
                    creation_timestamp=asyncio.get_event_loop().time(),
                    analysis_summary=analysis.get("summary", "Market analysis available")
                )
                
                logger.info(f"✅ Social posts created successfully")
                return result
                
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON response: {e}")
                logger.debug(f"Raw response: {response.content}")
                return self._create_fallback_posts(analysis, fundamentals, news_title)
                
        except Exception as e:
            logger.error(f"❌ Error during post creation: {e}")
            return self._create_fallback_posts(analysis, fundamentals, news_title)
    
    def _create_social_post_object(self, platform: str, post_data: Dict[str, Any]) -> SocialPost:
        """Create a SocialPost object from post data"""
        content = post_data.get("content", "")
        hashtags = post_data.get("hashtags", [])
        emojis = post_data.get("emojis", [])
        sentiment = post_data.get("sentiment", "neutral")
        engagement_score = float(post_data.get("engagement_score", 0.7))
        
        # Calculate character count
        char_count = len(content)
        
        return SocialPost(
            platform=platform,
            content=content,
            hashtags=hashtags,
            emojis=emojis,
            character_count=char_count,
            sentiment=sentiment,
            engagement_score=engagement_score
        )
    
    def _create_fallback_posts(
        self, 
        analysis: Dict[str, Any], 
        fundamentals: Dict[str, Any],
        news_title: str
    ) -> PostCreationResult:
        """Create fallback posts when AI creation fails"""
        logger.info("🔄 Using fallback post creation")
        
        # Extract key information
        sentiment = analysis.get("sentiment", 0)
        fundamentals_status = analysis.get("fundamentals", "neutral")
        summary = analysis.get("summary", "Market update available")
        
        # Determine emojis and hashtags based on sentiment
        if sentiment > 0.3:
            emojis = ["🚀", "📈", "💎", "🔥"]
            sentiment_text = "positive"
        elif sentiment < -0.3:
            emojis = ["⚠️", "📉", "🔻", "💸"]
            sentiment_text = "negative"
        else:
            emojis = ["📊", "💡", "🔍", "📱"]
            sentiment_text = "neutral"
        
        # Create fallback posts
        twitter_content = f"{emojis[0]} {summary[:200]}... {emojis[1]} #crypto #finance #trading"
        linkedin_content = f"📊 Market Analysis: {summary}\n\n💼 Fundamentals: {fundamentals_status}\n\n#cryptocurrency #blockchain #investment #trading"
        telegram_content = f"🔥 {summary[:300]}...\n\n📱 Join our community for more insights!\n\n#crypto #community #trading"
        
        twitter_post = SocialPost(
            platform="twitter",
            content=twitter_content,
            hashtags=["#crypto", "#finance", "#trading"],
            emojis=emojis[:2],
            character_count=len(twitter_content),
            sentiment=sentiment_text,
            engagement_score=0.6
        )
        
        linkedin_post = SocialPost(
            platform="linkedin",
            content=linkedin_content,
            hashtags=["#cryptocurrency", "#blockchain", "#investment", "#trading"],
            emojis=["📊", "💼", "📱"],
            character_count=len(linkedin_content),
            sentiment=sentiment_text,
            engagement_score=0.7
        )
        
        telegram_post = SocialPost(
            platform="telegram",
            content=telegram_content,
            hashtags=["#crypto", "#community", "#trading"],
            emojis=["🔥", "📱", "👥"],
            character_count=len(telegram_content),
            sentiment=sentiment_text,
            engagement_score=0.65
        )
        
        return PostCreationResult(
            twitter_post=twitter_post,
            linkedin_post=linkedin_post,
            telegram_post=telegram_post,
            creation_timestamp=asyncio.get_event_loop().time(),
            analysis_summary=summary
        )
    
    async def create_multiple_posts(self, posts_data: List[Dict[str, Any]]) -> List[PostCreationResult]:
        """Create posts for multiple analysis results"""
        if not posts_data:
            return []
        
        try:
            # Create post creation tasks
            tasks = []
            for data in posts_data:
                analysis = data.get("analysis", {})
                fundamentals = data.get("fundamentals", {})
                news_title = data.get("news_title", "")
                
                if analysis and fundamentals:
                    task = self.create_social_posts(analysis, fundamentals, news_title)
                    tasks.append((data, task))
            
            # Execute all post creations concurrently
            results = []
            for data, task in tasks:
                try:
                    post_result = await task
                    if post_result:
                        results.append({
                            "original_data": data,
                            "posts": post_result
                        })
                except Exception as e:
                    logger.error(f"Error creating posts for data: {e}")
                    continue
            
            logger.info(f"✅ Created posts for {len(results)} analysis results")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error in batch post creation: {e}")
            return []
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get the current status of the post creator agent"""
        return {
            "model": self.model_name,
            "temperature": self.temperature,
            "llm_initialized": self.llm is not None,
            "openai_key_configured": bool(os.getenv("OPENAI_API_KEY")),
            "status": "ready" if self.llm else "not_initialized"
        }
    
    def validate_post_lengths(self, posts: PostCreationResult) -> Dict[str, bool]:
        """Validate post lengths for different platforms"""
        return {
            "twitter": posts.twitter_post.character_count <= 280,
            "linkedin": posts.linkedin_post.character_count <= 1300,
            "telegram": posts.telegram_post.character_count <= 500
        }

# Pydantic models for API requests and responses
class PostCreationRequest(BaseModel):
    """Request model for post creation"""
    analysis: Dict[str, Any]
    fundamentals: Dict[str, Any]
    news_title: Optional[str] = ""

class SocialPostResponse(BaseModel):
    """Response model for individual social post"""
    platform: str
    content: str
    hashtags: List[str]
    emojis: List[str]
    character_count: int
    sentiment: str
    engagement_score: float

class PostCreationResponse(BaseModel):
    """Response model for post creation"""
    success: bool
    message: str
    posts: Optional[Dict[str, SocialPostResponse]] = None
    validation: Optional[Dict[str, bool]] = None
    agent_status: Dict[str, Any]
    timestamp: str

class BatchPostCreationRequest(BaseModel):
    """Request model for batch post creation"""
    posts_data: List[Dict[str, Any]]

class BatchPostCreationResponse(BaseModel):
    """Response model for batch post creation"""
    success: bool
    message: str
    created_posts: List[Dict[str, Any]]
    total_created: int
    agent_status: Dict[str, Any]
    timestamp: str

# Utility functions for easy access
async def create_single_posts(
    analysis: Dict[str, Any], 
    fundamentals: Dict[str, Any], 
    news_title: str = ""
) -> Optional[PostCreationResult]:
    """Convenience function to create social media posts"""
    agent = PostCreatorAgent()
    return await agent.create_social_posts(analysis, fundamentals, news_title)

async def create_multiple_posts_batch(posts_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convenience function to create multiple sets of posts"""
    agent = PostCreatorAgent()
    return await agent.create_multiple_posts(posts_data)
