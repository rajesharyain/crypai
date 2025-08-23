"""
Orchestrator Agent for Complete Pipeline
Chains all agents together: Ingestion → Analysis → Fundamentals → Post Creation
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Import our agent modules
from ingestion import NewsIngestionAgent
from analyzer import AnalyzerAgent
from fundamentals import FundamentalsFetcherAgent
from post_creator import PostCreatorAgent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PipelineResult:
    """Complete result of the orchestrated pipeline"""
    news_item: Dict[str, Any]
    analysis: Dict[str, Any]
    fundamentals: Dict[str, Any]
    posts: Dict[str, Any]
    pipeline_status: str
    execution_time: float
    timestamp: str

class OrchestratorAgent:
    """Orchestrates the complete pipeline from news ingestion to social media posts"""
    
    def __init__(self):
        """Initialize all agents"""
        try:
            self.news_agent = NewsIngestionAgent()
            self.analyzer_agent = AnalyzerAgent()
            self.post_creator_agent = PostCreatorAgent()
            
            # Default symbol for fundamentals
            self.default_symbol = "SUI"
            
            logger.info("✅ OrchestratorAgent initialized with all agents")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize OrchestratorAgent: {e}")
            raise
    
    async def run_pipeline(self, symbol: str = None, news_limit: int = 1) -> Optional[PipelineResult]:
        """Run the complete pipeline: Ingestion → Analysis → Fundamentals → Post Creation"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            logger.info("🚀 Starting complete pipeline execution...")
            
            # Step 1: Ingest latest news
            logger.info("📰 Step 1: Ingesting latest news...")
            news_items = await self.news_agent.fetch_all_news(limit=news_limit)
            
            if not news_items:
                logger.error("❌ No news items fetched. Pipeline cannot continue.")
                return None
            
            # Take the first news item
            news_item = news_items[0]
            logger.info(f"✅ News ingested: {news_item.title[:50]}...")
            
            # Step 2: Analyze the news
            logger.info("🔍 Step 2: Analyzing news sentiment and fundamentals...")
            analysis_result = await self.analyzer_agent.analyze_news(
                title=news_item.title,
                summary=news_item.summary
            )
            
            if not analysis_result:
                logger.error("❌ News analysis failed. Pipeline cannot continue.")
                return None
            
            logger.info(f"✅ Analysis completed: {analysis_result.fundamentals} sentiment")
            
            # Step 3: Get fundamentals for the symbol
            symbol = symbol or self.default_symbol
            logger.info(f"💰 Step 3: Fetching fundamentals for {symbol}...")
            
            async with FundamentalsFetcherAgent() as fundamentals_agent:
                fundamentals = await fundamentals_agent.get_fundamentals(symbol.upper())
                
                if not fundamentals:
                    logger.warning(f"⚠️ Could not fetch fundamentals for {symbol}, using default data")
                    fundamentals = {
                        "symbol": symbol.upper(),
                        "current_price": 0.0,
                        "price_change_24h": 0.0,
                        "market_cap_rank": 0,
                        "volume_24h": 0.0,
                        "market_cap": 0.0,
                        "status": "unavailable"
                    }
                else:
                    logger.info(f"✅ Fundamentals fetched: ${fundamentals.current_price_usd:,.2f}")
            
            # Step 4: Generate social media posts
            logger.info("📝 Step 4: Creating social media posts...")
            
            # Prepare data for post creation
            analysis_data = {
                "summary": analysis_result.summary,
                "sentiment": analysis_result.sentiment,
                "fundamentals": analysis_result.fundamentals,
                "confidence": analysis_result.confidence
            }
            
            fundamentals_data = {
                "current_price": getattr(fundamentals, 'current_price_usd', 0.0),
                "price_change_24h": getattr(fundamentals, 'price_change_percentage_24h', 0.0),
                "market_cap_rank": getattr(fundamentals, 'market_cap_rank', 0),
                "volume_24h": getattr(fundamentals, 'volume_24h', 0.0),
                "market_cap": getattr(fundamentals, 'market_cap', 0.0)
            }
            
            posts_result = await self.post_creator_agent.create_social_posts(
                analysis=analysis_data,
                fundamentals=fundamentals_data,
                news_title=news_item.title
            )
            
            if not posts_result:
                logger.error("❌ Post creation failed. Pipeline cannot complete.")
                return None
            
            logger.info("✅ Social media posts created successfully")
            
            # Calculate execution time
            execution_time = asyncio.get_event_loop().time() - start_time
            
            # Create pipeline result
            result = PipelineResult(
                news_item={
                    "title": news_item.title,
                    "summary": news_item.summary,
                    "link": news_item.link,
                    "published": news_item.published,
                    "source": news_item.source
                },
                analysis={
                    "summary": analysis_result.summary,
                    "sentiment": analysis_result.sentiment,
                    "fundamentals": analysis_result.fundamentals,
                    "confidence": analysis_result.confidence,
                    "analysis_timestamp": analysis_result.analysis_timestamp
                },
                fundamentals={
                    "symbol": symbol.upper(),
                    "current_price": getattr(fundamentals, 'current_price_usd', 0.0),
                    "price_change_24h": getattr(fundamentals, 'price_change_percentage_24h', 0.0),
                    "market_cap_rank": getattr(fundamentals, 'market_cap_rank', 0),
                    "volume_24h": getattr(fundamentals, 'volume_24h', 0.0),
                    "market_cap": getattr(fundamentals, 'market_cap', 0.0)
                },
                posts={
                    "twitter": {
                        "content": posts_result.twitter_post.content,
                        "hashtags": posts_result.twitter_post.hashtags,
                        "emojis": posts_result.twitter_post.emojis,
                        "character_count": posts_result.twitter_post.character_count,
                        "sentiment": posts_result.twitter_post.sentiment,
                        "engagement_score": posts_result.twitter_post.engagement_score
                    },
                    "linkedin": {
                        "content": posts_result.linkedin_post.content,
                        "hashtags": posts_result.linkedin_post.hashtags,
                        "emojis": posts_result.linkedin_post.emojis,
                        "character_count": posts_result.linkedin_post.character_count,
                        "sentiment": posts_result.linkedin_post.sentiment,
                        "engagement_score": posts_result.linkedin_post.engagement_score
                    },
                    "telegram": {
                        "content": posts_result.telegram_post.content,
                        "hashtags": posts_result.telegram_post.hashtags,
                        "emojis": posts_result.telegram_post.emojis,
                        "character_count": posts_result.telegram_post.character_count,
                        "sentiment": posts_result.telegram_post.sentiment,
                        "engagement_score": posts_result.telegram_post.engagement_score
                    }
                },
                pipeline_status="completed",
                execution_time=execution_time,
                timestamp=asyncio.get_event_loop().time()
            )
            
            logger.info(f"🎉 Pipeline completed successfully in {execution_time:.2f} seconds!")
            return result
            
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"❌ Pipeline execution failed after {execution_time:.2f} seconds: {e}")
            
            # Return partial result if possible
            try:
                return PipelineResult(
                    news_item={},
                    analysis={},
                    fundamentals={},
                    posts={},
                    pipeline_status="failed",
                    execution_time=execution_time,
                    timestamp=asyncio.get_event_loop().time()
                )
            except:
                return None
    
    async def run_pipeline_with_custom_symbol(self, symbol: str, news_limit: int = 1) -> Optional[PipelineResult]:
        """Run pipeline with a specific cryptocurrency symbol"""
        return await self.run_pipeline(symbol=symbol, news_limit=news_limit)
    
    async def run_pipeline_with_multiple_news(self, news_limit: int = 3) -> List[PipelineResult]:
        """Run pipeline for multiple news items"""
        try:
            logger.info(f"🚀 Starting pipeline for {news_limit} news items...")
            
            # Fetch multiple news items
            news_items = await self.news_agent.fetch_all_news(limit=news_limit)
            
            if not news_items:
                logger.error("❌ No news items fetched.")
                return []
            
            # Process each news item
            results = []
            for i, news_item in enumerate(news_items):
                logger.info(f"📰 Processing news item {i+1}/{len(news_items)}: {news_item.title[:50]}...")
                
                try:
                    # Create a temporary pipeline result for this item
                    analysis_result = await self.analyzer_agent.analyze_news(
                        title=news_item.title,
                        summary=news_item.summary
                    )
                    
                    if not analysis_result:
                        logger.warning(f"⚠️ Skipping news item {i+1} due to analysis failure")
                        continue
                    
                    # Get fundamentals (using default symbol)
                    async with FundamentalsFetcherAgent() as fundamentals_agent:
                        fundamentals = await fundamentals_agent.get_fundamentals(self.default_symbol.upper())
                        
                        if not fundamentals:
                            fundamentals = {
                                "symbol": self.default_symbol.upper(),
                                "current_price": 0.0,
                                "price_change_24h": 0.0,
                                "market_cap_rank": 0,
                                "volume_24h": 0.0,
                                "market_cap": 0.0,
                                "status": "unavailable"
                            }
                    
                    # Create posts
                    analysis_data = {
                        "summary": analysis_result.summary,
                        "sentiment": analysis_result.sentiment,
                        "fundamentals": analysis_result.fundamentals,
                        "confidence": analysis_result.confidence
                    }
                    
                    fundamentals_data = {
                        "current_price": getattr(fundamentals, 'current_price_usd', 0.0),
                        "price_change_24h": getattr(fundamentals, 'price_change_percentage_24h', 0.0),
                        "market_cap_rank": getattr(fundamentals, 'market_cap_rank', 0),
                        "volume_24h": getattr(fundamentals, 'volume_24h', 0.0),
                        "market_cap": getattr(fundamentals, 'market_cap', 0.0)
                    }
                    
                    posts_result = await self.post_creator_agent.create_social_posts(
                        analysis=analysis_data,
                        fundamentals=fundamentals_data,
                        news_title=news_item.title
                    )
                    
                    if posts_result:
                        result = PipelineResult(
                            news_item={
                                "title": news_item.title,
                                "summary": news_item.summary,
                                "link": news_item.link,
                                "published": news_item.published,
                                "source": news_item.source
                            },
                            analysis={
                                "summary": analysis_result.summary,
                                "sentiment": analysis_result.sentiment,
                                "fundamentals": analysis_result.fundamentals,
                                "confidence": analysis_result.confidence,
                                "analysis_timestamp": analysis_result.analysis_timestamp
                            },
                            fundamentals={
                                "symbol": self.default_symbol.upper(),
                                "current_price": getattr(fundamentals, 'current_price_usd', 0.0),
                                "price_change_24h": getattr(fundamentals, 'price_change_percentage_24h', 0.0),
                                "market_cap_rank": getattr(fundamentals, 'market_cap_rank', 0),
                                "volume_24h": getattr(fundamentals, 'volume_24h', 0.0),
                                "market_cap": getattr(fundamentals, 'market_cap', 0.0)
                            },
                            posts={
                                "twitter": {
                                    "content": posts_result.twitter_post.content,
                                    "hashtags": posts_result.twitter_post.hashtags,
                                    "emojis": posts_result.twitter_post.emojis,
                                    "character_count": posts_result.twitter_post.character_count,
                                    "sentiment": posts_result.twitter_post.sentiment,
                                    "engagement_score": posts_result.twitter_post.engagement_score
                                },
                                "linkedin": {
                                    "content": posts_result.linkedin_post.content,
                                    "hashtags": posts_result.linkedin_post.hashtags,
                                    "emojis": posts_result.linkedin_post.emojis,
                                    "character_count": posts_result.linkedin_post.character_count,
                                    "sentiment": posts_result.linkedin_post.sentiment,
                                    "engagement_score": posts_result.linkedin_post.engagement_score
                                },
                                "telegram": {
                                    "content": posts_result.telegram_post.content,
                                    "hashtags": posts_result.telegram_post.hashtags,
                                    "emojis": posts_result.telegram_post.emojis,
                                    "character_count": posts_result.telegram_post.character_count,
                                    "sentiment": posts_result.telegram_post.sentiment,
                                    "engagement_score": posts_result.telegram_post.engagement_score
                                }
                            },
                            pipeline_status="completed",
                            execution_time=0.0,  # Individual execution time not tracked here
                            timestamp=asyncio.get_event_loop().time()
                        )
                        
                        results.append(result)
                        logger.info(f"✅ News item {i+1} processed successfully")
                    
                except Exception as e:
                    logger.error(f"❌ Error processing news item {i+1}: {e}")
                    continue
            
            logger.info(f"🎉 Pipeline completed for {len(results)}/{len(news_items)} news items")
            return results
            
        except Exception as e:
            logger.error(f"❌ Multiple news pipeline failed: {e}")
            return []
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get the status of all agents in the orchestrator"""
        return {
            "orchestrator_status": "ready",
            "default_symbol": self.default_symbol,
            "agents": {
                "news_agent": self.news_agent.get_source_statistics() if hasattr(self.news_agent, 'get_source_statistics') else "available",
                "analyzer_agent": self.analyzer_agent.get_agent_status(),
                "post_creator_agent": self.post_creator_agent.get_agent_status()
            }
        }
    
    def get_pipeline_info(self) -> Dict[str, Any]:
        """Get information about the pipeline structure"""
        return {
            "pipeline_steps": [
                {
                    "step": 1,
                    "name": "News Ingestion",
                    "agent": "NewsIngestionAgent",
                    "description": "Fetch latest news from configured sources"
                },
                {
                    "step": 2,
                    "name": "News Analysis",
                    "agent": "AnalyzerAgent",
                    "description": "Analyze sentiment and fundamental impact"
                },
                {
                    "step": 3,
                    "name": "Fundamentals Fetching",
                    "agent": "FundamentalsFetcherAgent",
                    "description": "Get cryptocurrency market data"
                },
                {
                    "step": 4,
                    "name": "Post Creation",
                    "agent": "PostCreatorAgent",
                    "description": "Generate social media posts"
                }
            ],
            "default_symbol": self.default_symbol,
            "supported_operations": [
                "run_pipeline",
                "run_pipeline_with_custom_symbol",
                "run_pipeline_with_multiple_news"
            ]
        }

# Pydantic models for API requests and responses
class PipelineRequest(BaseModel):
    """Request model for pipeline execution"""
    symbol: Optional[str] = "SUI"
    news_limit: Optional[int] = 3

class PipelineResponse(BaseModel):
    """Response model for pipeline execution"""
    success: bool
    message: str
    pipeline_result: Optional[Dict[str, Any]] = None
    agent_status: Dict[str, Any]
    pipeline_info: Dict[str, Any]
    timestamp: str

class MultiplePipelineRequest(BaseModel):
    """Request model for multiple news pipeline execution"""
    symbol: Optional[str] = "ETH"
    news_limit: Optional[int] = 3

class MultiplePipelineResponse(BaseModel):
    """Response model for multiple news pipeline execution"""
    success: bool
    message: str
    pipeline_results: List[Dict[str, Any]]
    total_processed: int
    agent_status: Dict[str, Any]
    pipeline_info: Dict[str, Any]
    timestamp: str

# Utility functions for easy access
async def run_complete_pipeline(symbol: str = "ETH", news_limit: int = 1) -> Optional[PipelineResult]:
    """Convenience function to run the complete pipeline"""
    orchestrator = OrchestratorAgent()
    return await orchestrator.run_pipeline(symbol=symbol, news_limit=news_limit)

async def run_multiple_news_pipeline(symbol: str = "ETH", news_limit: int = 3) -> List[PipelineResult]:
    """Convenience function to run pipeline for multiple news items"""
    orchestrator = OrchestratorAgent()
    return await orchestrator.run_pipeline_with_multiple_news(news_limit=news_limit)
