"""
Orchestrator Agent for Complete Pipeline
Chains all agents together: Ingestion → Analysis → Fundamentals → Post Creation
"""

import asyncio
import logging
import os
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from pydantic import BaseModel

# Import agents
from ingestion import NewsIngestionAgent
from analyzer import AnalyzerAgent
from fundamentals import FundamentalsFetcherAgent
from post_creator import PostCreatorAgent

# Import observability components
from observability import get_metrics_collector
from prometheus_metrics import record_pipeline_metrics
from langfuse_integration import get_pipeline_tracker

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
    def __init__(self, news_agent=None, analyzer_agent=None, fundamentals_agent=None, post_creator_agent=None):
        """Initialize the Orchestrator Agent"""
        # Use provided agents or initialize new ones with model type from environment
        ai_model_type = os.getenv('AI_MODEL_TYPE', 'openai').lower()
        
        self.news_agent = news_agent or NewsIngestionAgent(model_type=ai_model_type)
        self.analyzer_agent = analyzer_agent or AnalyzerAgent(model_type=ai_model_type)
        self.fundamentals_agent = fundamentals_agent or FundamentalsFetcherAgent(model_type=ai_model_type)
        self.post_creator_agent = post_creator_agent or PostCreatorAgent(model_type=ai_model_type)
        self.default_symbol = "SUI"
        
        # Initialize observability components
        self.metrics_collector = get_metrics_collector()
        self.pipeline_tracker = get_pipeline_tracker()
        
        logger.info("🚀 OrchestratorAgent initialized successfully")

    async def run_pipeline(self, request: PipelineRequest = None) -> PipelineResult:
        """
        Run the complete pipeline: News → Analysis → Fundamentals → Posts
        """
        if not request:
            request = PipelineRequest()
        
        start_time = time.time()
        pipeline_type = "single_pipeline"
        logger.info("🚀 Starting complete pipeline execution...")
        
        # Start observability tracking
        trace_id = None
        if self.pipeline_tracker:
            try:
                with self.pipeline_tracker.track_pipeline(pipeline_type, request.symbol, request.news_limit) as trace_id:
                    return await self._execute_pipeline(request, start_time, trace_id)
            except Exception as e:
                logger.error(f"Pipeline tracking failed: {e}")
                return await self._execute_pipeline(request, start_time, None)
        else:
            return await self._execute_pipeline(request, start_time, None)

    async def _execute_pipeline(self, request: PipelineRequest, start_time: float, trace_id: str = None) -> PipelineResult:
        """Internal method to execute the pipeline with observability"""
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
            
            # Track pipeline step
            if trace_id and self.pipeline_tracker:
                self.pipeline_tracker.track_pipeline_step(trace_id, "news_ingestion", {
                    "items_fetched": len(news_items),
                    "crypto_symbols": len(primary_news.get('crypto_symbols', [])),
                    "primary_crypto": primary_news.get('primary_crypto', {})
                })
            
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
            
            # Track pipeline step
            if trace_id and self.pipeline_tracker:
                self.pipeline_tracker.track_pipeline_step(trace_id, "news_analysis", {
                    "sentiment": analysis_result.sentiment,
                    "fundamentals": analysis_result.fundamentals,
                    "model_used": getattr(analysis_result, 'model_used', 'unknown')
                })
            
            # Step 3: Get fundamentals for primary crypto or requested symbol
            logger.info(f"💰 Step 3: Fetching fundamentals for {request.symbol}...")
            
            # Use fundamentals agent as async context manager
            async with self.fundamentals_agent as fundamentals_agent:
                # Determine which crypto to get fundamentals for
                target_symbol = request.symbol
                if primary_news.get('primary_crypto'):
                    news_crypto = primary_news['primary_crypto']['symbol']
                    # Validate that the news crypto is a real cryptocurrency
                    if news_crypto and await fundamentals_agent.is_valid_symbol(news_crypto):
                        target_symbol = news_crypto
                        logger.info(f"🎯 Using primary crypto from news: {target_symbol}")
                    else:
                        logger.warning(f"⚠️ News contains invalid crypto symbol '{news_crypto}', using requested symbol: {target_symbol}")
                else:
                    logger.info(f"📰 No crypto symbols found in news, using requested symbol: {target_symbol}")
                
                # Try to get fundamentals for the target symbol
                fundamentals = await fundamentals_agent.get_fundamentals(target_symbol)
                if not fundamentals:
                    # If the target symbol fails, try the originally requested symbol first
                    if target_symbol != request.symbol:
                        logger.info(f"🔄 Target symbol {target_symbol} failed, trying requested symbol: {request.symbol}")
                        fundamentals = await fundamentals_agent.get_fundamentals(request.symbol)
                        if fundamentals:
                            target_symbol = request.symbol
                            logger.info(f"✅ Using requested symbol: {request.symbol}")
                    
                    # If still no success, try some common fallbacks
                    if not fundamentals:
                        fallback_symbols = ['BTC', 'ETH', 'USDT']
                        for fallback in fallback_symbols:
                            if fallback not in [target_symbol, request.symbol]:
                                logger.info(f"🔄 Trying fallback symbol: {fallback}")
                                fundamentals = await fundamentals_agent.get_fundamentals(fallback)
                                if fundamentals:
                                    target_symbol = fallback
                                    logger.info(f"✅ Using fallback symbol: {fallback}")
                                    break
                        
                        if not fundamentals:
                            raise Exception(f"Failed to fetch fundamentals for {target_symbol}, {request.symbol}, and all fallbacks")
                
                logger.info(f"✅ Fundamentals fetched for {target_symbol}: ${fundamentals.current_price_usd}")
                
                # Track pipeline step
                if trace_id and self.pipeline_tracker:
                    self.pipeline_tracker.track_pipeline_step(trace_id, "fundamentals_fetch", {
                        "symbol": target_symbol,
                        "price": getattr(fundamentals, 'current_price_usd', 0.0),
                        "market_cap_rank": getattr(fundamentals, 'market_cap_rank', 0)
                    })
                
                # Step 4: Create AI-powered social media posts
                logger.info("📝 Step 4: Creating social media posts...")
                
                # Use crypto-specific post creation if we have a valid crypto symbol
                if target_symbol and await fundamentals_agent.is_valid_symbol(target_symbol):
                    # Get crypto name for the target symbol
                    crypto_names = {
                        'BTC': 'Bitcoin', 'ETH': 'Ethereum', 'SUI': 'Sui Network',
                        'SOL': 'Solana', 'ADA': 'Cardano', 'DOT': 'Polkadot',
                        'USDT': 'Tether', 'USDC': 'USDC Coin', 'BNB': 'Binance Coin'
                    }
                    crypto_name = crypto_names.get(target_symbol, target_symbol)
                    
                    posts = await self.post_creator_agent.create_crypto_specific_posts(
                        target_symbol,
                        crypto_name,
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
                
                # Track pipeline step
                if trace_id and self.pipeline_tracker:
                    self.pipeline_tracker.track_pipeline_step(trace_id, "post_creation", {
                        "platforms": list(posts.keys()) if isinstance(posts, dict) else [],
                        "posts_count": len(posts) if isinstance(posts, dict) else 0
                    })
                
                # Calculate execution time
                execution_time = time.time() - start_time
                
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
                
                # Record successful pipeline metrics
                self._record_pipeline_metrics("single", True, execution_time, 1)
                
                logger.info(f"🎉 Pipeline completed successfully in {execution_time:.2f} seconds!")
                return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ Pipeline execution failed after {execution_time:.2f} seconds: {e}")
            
            # Record failed pipeline metrics
            self._record_pipeline_metrics("single", False, execution_time, 0)
            
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
            "pipeline_info": self.get_pipeline_info(),
            "agent_status": {
                "news_agent": self.news_agent.get_source_statistics(),
                "analyzer_agent": self.analyzer_agent.get_status(),
                "post_creator_agent": self.post_creator_agent.get_status(),
                "fundamentals_agent": {
                    "status": "operational",
                    "last_check": datetime.utcnow().isoformat()
                }
            },
            "observability": {
                "metrics_collector": self.metrics_collector is not None,
                "pipeline_tracker": self.pipeline_tracker is not None
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

    def _record_pipeline_metrics(self, pipeline_type: str, success: bool, duration: float, items_processed: int):
        """Record pipeline execution metrics"""
        try:
            # Record in our metrics collector
            if self.metrics_collector:
                self.metrics_collector.record_pipeline_execution(pipeline_type, success, duration, items_processed)
            
            # Record in Prometheus metrics
            record_pipeline_metrics(pipeline_type, success, duration, items_processed)
            
        except Exception as e:
            logger.error(f"Error recording pipeline metrics: {e}")
