"""
Orchestrator Agent for Complete Pipeline
Chains all agents together: Ingestion → Analysis → Fundamentals → Post Creation
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from pydantic import BaseModel

# Import agents
from ingestion import NewsIngestionAgent
from analyzer import AnalyzerAgent
from fundamentals import FundamentalsFetcherAgent
from post_creator import PostCreatorAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PipelineResult:
    """Result of pipeline execution"""
    news_item: Dict[str, Any]
    analysis: Dict[str, Any]
    fundamentals: Dict[str, Any]
    posts: Dict[str, Any]
    pipeline_status: str
    execution_time: float
    timestamp: str

class PipelineRequest(BaseModel):
    """Request model for pipeline execution"""
    symbol: Optional[str] = "SUI"
    news_limit: Optional[int] = 5  # Increased to get more crypto news
    crypto_focus: Optional[bool] = True  # Focus on crypto-relevant news

class PipelineResponse(BaseModel):
    """Response model for pipeline execution"""
    success: bool
    pipeline_result: Optional[PipelineResult] = None
    error: Optional[str] = None

class MultiplePipelineRequest(BaseModel):
    """Request model for multiple pipeline execution"""
    symbol: Optional[str] = "SUI"
    news_limit: Optional[int] = 3
    crypto_focus: Optional[bool] = True

class MultiplePipelineResponse(BaseModel):
    """Response model for multiple pipeline execution"""
    success: bool
    pipeline_results: List[PipelineResult]
    total_executed: int
    errors: List[str] = []

class OrchestratorAgent:
    def __init__(self):
        """Initialize the Orchestrator Agent"""
        self.news_agent = NewsIngestionAgent()
        self.analyzer_agent = AnalyzerAgent()
        self.fundamentals_agent = FundamentalsFetcherAgent()
        self.post_creator_agent = PostCreatorAgent()
        self.default_symbol = "SUI"
        
        logger.info("🚀 OrchestratorAgent initialized successfully")

    async def run_pipeline(self, request: PipelineRequest = None) -> PipelineResult:
        """
        Run the complete pipeline: News → Analysis → Fundamentals → Posts
        """
        if not request:
            request = PipelineRequest()
        
        start_time = datetime.now()
        logger.info("🚀 Starting complete pipeline execution...")
        
        try:
            # Step 1: Ingest crypto-focused news
            logger.info("📰 Step 1: Ingesting latest crypto news...")
            if request.crypto_focus:
                news_items = await self.news_agent.fetch_crypto_focused_news(request.news_limit)
            else:
                news_items = await self.news_agent.fetch_all_news(request.news_limit)
            
            if not news_items:
                raise Exception("No news items fetched")
            
            # Get the most relevant crypto news item
            primary_news = news_items[0]
            logger.info(f"✅ News ingested: {primary_news.get('title', 'Unknown')[:50]}...")
            
            # Log crypto symbols found
            if primary_news.get('crypto_symbols'):
                symbols = [f"{s['symbol']} ({s['relevance_score']})" for s in primary_news['crypto_symbols'][:3]]
                logger.info(f"🔍 Crypto symbols detected: {', '.join(symbols)}")
            
            # Step 2: Analyze news with AI
            logger.info("🔍 Step 2: Analyzing news sentiment and fundamentals...")
            if primary_news.get('crypto_symbols'):
                # Use crypto-specific analysis
                analysis_result = await self.analyzer_agent.analyze_crypto_specific_news(
                    primary_news, 
                    None  # Will get fundamentals in next step
                )
            else:
                # Use general analysis
                analysis_result = await self.analyzer_agent.analyze_news(
                    primary_news.get('title', ''),
                    primary_news.get('summary', ''),
                    primary_news.get('crypto_symbols', [])
                )
            
            if not analysis_result:
                raise Exception("News analysis failed")
            
            logger.info(f"✅ Analysis completed: {analysis_result.fundamentals} sentiment")
            
            # Step 3: Get fundamentals for primary crypto or requested symbol
            logger.info(f"💰 Step 3: Fetching fundamentals for {request.symbol}...")
            
            # Determine which crypto to get fundamentals for
            target_symbol = request.symbol
            if primary_news.get('primary_crypto'):
                target_symbol = primary_news['primary_crypto']['symbol']
                logger.info(f"🎯 Using primary crypto from news: {target_symbol}")
            
            fundamentals = await self.fundamentals_agent.get_fundamentals(target_symbol)
            if not fundamentals:
                raise Exception(f"Failed to fetch fundamentals for {target_symbol}")
            
            logger.info(f"✅ Fundamentals fetched: ${fundamentals.current_price}")
            
            # Step 4: Create AI-powered social media posts
            logger.info("📝 Step 4: Creating social media posts...")
            
            # Use crypto-specific post creation if available
            if primary_news.get('primary_crypto'):
                primary_crypto = primary_news['primary_crypto']
                posts = await self.post_creator_agent.create_crypto_specific_posts(
                    primary_crypto['symbol'],
                    primary_crypto['name'],
                    analysis_result.__dict__,
                    fundamentals.__dict__
                )
            else:
                posts = await self.post_creator_agent.create_social_posts(
                    analysis_result.__dict__,
                    fundamentals.__dict__
                )
            
            if not posts:
                raise Exception("Social media post creation failed")
            
            logger.info("✅ Social media posts created successfully")
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Create pipeline result
            result = PipelineResult(
                news_item=primary_news,
                analysis=analysis_result.__dict__,
                fundamentals=fundamentals.__dict__,
                posts=posts,
                pipeline_status="completed",
                execution_time=execution_time,
                timestamp=datetime.utcnow().isoformat()
            )
            
            logger.info(f"🎉 Pipeline completed successfully in {execution_time:.2f} seconds!")
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Pipeline execution failed after {execution_time:.2f} seconds: {e}")
            
            # Return error result
            return PipelineResult(
                news_item={},
                analysis={},
                fundamentals={},
                posts={},
                pipeline_status="failed",
                execution_time=execution_time,
                timestamp=datetime.utcnow().isoformat()
            )

    async def run_multiple_news_pipeline(self, request: PipelineRequest = None) -> List[PipelineResult]:
        """
        Run pipeline for multiple news items to get comprehensive crypto coverage
        """
        if not request:
            request = PipelineRequest()
        
        start_time = datetime.now()
        logger.info(f"🚀 Starting multi-news pipeline execution for {request.news_limit} items...")
        
        try:
            # Step 1: Get crypto-focused news
            logger.info("📰 Step 1: Fetching crypto-focused news...")
            news_items = await self.news_agent.fetch_crypto_focused_news(request.news_limit * 2)  # Get more to filter
            
            if not news_items:
                raise Exception("No news items fetched")
            
            # Filter to top crypto-relevant news
            top_news = news_items[:request.news_limit]
            logger.info(f"✅ Selected {len(top_news)} top crypto news items")
            
            # Step 2: Analyze all news items
            logger.info("🔍 Step 2: Analyzing all news items...")
            analysis_results = await self.analyzer_agent.analyze_multiple_news(top_news)
            
            if not analysis_results:
                raise Exception("News analysis failed")
            
            logger.info(f"✅ Completed analysis of {len(analysis_results)} news items")
            
            # Step 3: Get fundamentals for each crypto mentioned
            logger.info("💰 Step 3: Fetching fundamentals for mentioned cryptocurrencies...")
            fundamentals_map = {}
            
            for news_item in top_news:
                if news_item.get('primary_crypto'):
                    crypto_symbol = news_item['primary_crypto']['symbol']
                    if crypto_symbol not in fundamentals_map:
                        try:
                            fundamentals = await self.fundamentals_agent.get_fundamentals(crypto_symbol)
                            if fundamentals:
                                fundamentals_map[crypto_symbol] = fundamentals.__dict__
                                logger.info(f"✅ Got fundamentals for {crypto_symbol}: ${fundamentals.current_price}")
                        except Exception as e:
                            logger.warning(f"⚠️ Failed to get fundamentals for {crypto_symbol}: {e}")
                            fundamentals_map[crypto_symbol] = {}
            
            # Step 4: Create posts for each news item
            logger.info("📝 Step 4: Creating social media posts for all news items...")
            all_posts = await self.post_creator_agent.create_multiple_posts(top_news, list(fundamentals_map.values()))
            
            if not all_posts:
                raise Exception("Social media post creation failed")
            
            logger.info(f"✅ Created posts for {len(all_posts)} news items")
            
            # Create pipeline results for each news item
            results = []
            for i, news_item in enumerate(top_news):
                analysis = analysis_results[i] if i < len(analysis_results) else {}
                fundamentals = fundamentals_map.get(news_item.get('primary_crypto', {}).get('symbol', ''), {})
                posts = all_posts[i] if i < len(all_posts) else {}
                
                result = PipelineResult(
                    news_item=news_item,
                    analysis=analysis.__dict__ if hasattr(analysis, '__dict__') else analysis,
                    fundamentals=fundamentals,
                    posts=posts,
                    pipeline_status="completed",
                    execution_time=(datetime.now() - start_time).total_seconds(),
                    timestamp=datetime.utcnow().isoformat()
                )
                results.append(result)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"🎉 Multi-news pipeline completed successfully in {execution_time:.2f} seconds!")
            
            return results
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Multi-news pipeline failed after {execution_time:.2f} seconds: {e}")
            return []

    async def run_crypto_specific_pipeline(self, crypto_symbol: str, news_limit: int = 3) -> PipelineResult:
        """
        Run pipeline specifically for a given cryptocurrency
        """
        start_time = datetime.now()
        logger.info(f"🚀 Starting {crypto_symbol}-specific pipeline execution...")
        
        try:
            # Step 1: Get news specifically about this crypto
            logger.info(f"📰 Step 1: Fetching {crypto_symbol} news...")
            all_news = await self.news_agent.fetch_crypto_focused_news(news_limit * 3)  # Get more to filter
            
            # Filter to news about the specific crypto
            crypto_news = []
            for news in all_news:
                if news.get('crypto_symbols'):
                    for crypto_info in news['crypto_symbols']:
                        if crypto_info['symbol'].upper() == crypto_symbol.upper():
                            crypto_news.append(news)
                            break
                        if len(crypto_news) >= news_limit:
                            break
                if len(crypto_news) >= news_limit:
                    break
            
            if not crypto_news:
                raise Exception(f"No news found for {crypto_symbol}")
            
            # Use the most relevant news
            primary_news = crypto_news[0]
            logger.info(f"✅ {crypto_symbol} news found: {primary_news.get('title', 'Unknown')[:50]}...")
            
            # Step 2: Analyze with crypto focus
            logger.info(f"🔍 Step 2: Analyzing {crypto_symbol} news...")
            analysis_result = await self.analyzer_agent.analyze_crypto_specific_news(primary_news)
            
            if not analysis_result:
                raise Exception(f"News analysis failed for {crypto_symbol}")
            
            logger.info(f"✅ {crypto_symbol} analysis completed")
            
            # Step 3: Get fundamentals
            logger.info(f"💰 Step 3: Fetching {crypto_symbol} fundamentals...")
            fundamentals = await self.fundamentals_agent.get_fundamentals(crypto_symbol)
            
            if not fundamentals:
                raise Exception(f"Failed to fetch fundamentals for {crypto_symbol}")
            
            logger.info(f"✅ {crypto_symbol} fundamentals: ${fundamentals.current_price}")
            
            # Step 4: Create crypto-specific posts
            logger.info(f"📝 Step 4: Creating {crypto_symbol} social media posts...")
            posts = await self.post_creator_agent.create_crypto_specific_posts(
                crypto_symbol,
                fundamentals.name if hasattr(fundamentals, 'name') else crypto_symbol,
                analysis_result.__dict__,
                fundamentals.__dict__
            )
            
            if not posts:
                raise Exception(f"Social media post creation failed for {crypto_symbol}")
            
            logger.info(f"✅ {crypto_symbol} posts created successfully")
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Create result
            result = PipelineResult(
                news_item=primary_news,
                analysis=analysis_result.__dict__,
                fundamentals=fundamentals.__dict__,
                posts=posts,
                pipeline_status="completed",
                execution_time=execution_time,
                timestamp=datetime.utcnow().isoformat()
            )
            
            logger.info(f"🎉 {crypto_symbol} pipeline completed successfully in {execution_time:.2f} seconds!")
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ {crypto_symbol} pipeline failed after {execution_time:.2f} seconds: {e}")
            
            return PipelineResult(
                news_item={},
                analysis={},
                fundamentals={},
                posts={},
                pipeline_status="failed",
                execution_time=execution_time,
                timestamp=datetime.utcnow().isoformat()
            )

    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        return {
            "orchestrator_status": "ready",
            "default_symbol": self.default_symbol,
            "agents": {
                "news_agent": self.news_agent.get_source_statistics(),
                "analyzer_agent": self.analyzer_agent.get_status(),
                "post_creator_agent": self.post_creator_agent.get_status()
            }
        }

    def get_pipeline_info(self) -> Dict[str, Any]:
        """Get pipeline information"""
        return {
            "pipeline_steps": [
                {
                    "step": 1,
                    "name": "News Ingestion",
                    "agent": "NewsIngestionAgent",
                    "description": "Fetch latest crypto news from configured sources"
                },
                {
                    "step": 2,
                    "name": "News Analysis",
                    "agent": "AnalyzerAgent",
                    "description": "Analyze sentiment and fundamental impact using AI"
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
                    "description": "Generate AI-powered social media posts"
                }
            ],
            "default_symbol": self.default_symbol,
            "supported_operations": [
                "run_pipeline",
                "run_pipeline_with_custom_symbol",
                "run_pipeline_with_multiple_news"
            ]
        }
