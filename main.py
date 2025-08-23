from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv
import uvicorn
from datetime import datetime, timezone
import json

# Import our custom modules
from ingestion import NewsIngestionAgent, NewsItem
from mcp_integration import MCPManager, MCPNewsResponse, MCPManagerStatus
from fundamentals import (
    FundamentalsFetcherAgent, 
    CryptoFundamentals, 
    FundamentalsResponse,
    MultipleFundamentalsResponse,
    TrendingCoinsResponse,
    MarketOverviewResponse
)
from analyzer import (
    AnalyzerAgent,
    NewsAnalysisRequest,
    NewsAnalysisResponse,
    BatchAnalysisRequest,
    BatchAnalysisResponse
)
from post_creator import (
    PostCreatorAgent,
    PostCreationRequest,
    PostCreationResponse,
    BatchPostCreationRequest,
    BatchPostCreationResponse
)
from orchestrator import (
    OrchestratorAgent,
    PipelineRequest,
    PipelineResponse,
    MultiplePipelineRequest,
    MultiplePipelineResponse
)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="AI Finance Assistant MVP",
    description="AI-powered financial insights with news ingestion and MCP server integration",
    version="1.0.0"
)

# Configure templates
templates = Jinja2Templates(directory="templates")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
news_agent = NewsIngestionAgent()
mcp_manager = MCPManager()
analyzer_agent = AnalyzerAgent()
post_creator_agent = PostCreatorAgent()
orchestrator_agent = OrchestratorAgent()

# Pydantic models for API requests
class ChatRequest(BaseModel):
    message: str
    model: str = "gpt-3.5-turbo"

class AddSourceRequest(BaseModel):
    source_type: str  # "rss" or "api"
    url: str
    name: str
    category: str = "crypto"
    max_items: int = 20

class ServerPriorityRequest(BaseModel):
    server_name: str
    priority: str  # "active" or "fallback"

# Health check endpoint
@app.get("/ping")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "AI Finance Assistant MVP",
        "version": "1.0.0",
        "features": [
            "AI-powered financial insights",
            "News ingestion pipeline",
            "MCP server integration",
            "RSS fallback system",
            "Cryptocurrency fundamentals"
        ],
        "endpoints": {
            "dashboard_ui": "/ui",
            "health": "/ping",
            "chat": "/chat",
            "news": "/fetch_news",
            "mcp_news": "/mcp/news",
            "fundamentals": "/fundamentals/{symbol}",
            "trending": "/fundamentals/trending",
            "market_overview": "/fundamentals/market/overview",
            "analyzer": "/analyze",
            "batch_analyzer": "/analyze/batch",
            "analyzer_status": "/analyze/status",
            "post_creator": "/create_post",
            "batch_post_creator": "/create_post/batch",
            "post_creator_status": "/create_post/status",
            "orchestrator": "/run_pipeline",
            "multiple_pipeline": "/run_pipeline/multiple",
            "orchestrator_status": "/run_pipeline/status"
        }
    }

@app.get("/ui", response_class=HTMLResponse)
async def dashboard_ui(request: Request):
    """Serve the orchestrator dashboard UI"""
    return templates.TemplateResponse("index.html", {"request": request})

# Chat endpoint with LangChain + OpenAI
@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Get OpenAI API key
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        # Initialize LangChain with OpenAI
        from langchain_openai import ChatOpenAI
        from langchain.schema import HumanMessage
        
        llm = ChatOpenAI(
            openai_api_key=openai_api_key,
            model_name=request.model,
            temperature=0.7
        )
        
        # Get response from OpenAI
        messages = [HumanMessage(content=request.message)]
        response = llm.invoke(messages)
        
        return {
            "message": request.message,
            "response": response.content,
            "model": request.model,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

# Get available models
@app.get("/models")
async def get_models():
    return {
        "available_models": [
            "gpt-3.5-turbo",
            "gpt-4",
            "gpt-4-turbo-preview"
        ],
        "default_model": "gpt-3.5-turbo"
    }

# News ingestion endpoints
@app.get("/fetch_news")
async def fetch_news(
    limit: int = 20,
    include_sentiment: bool = False,
    sources: Optional[str] = None
):
    try:
        news_items = await news_agent.fetch_all_news(limit=limit)
        
        if include_sentiment:
            # Analyze sentiment for news items
            news_items = await news_agent.analyze_news_sentiment(news_items)
        
        return {
            "success": True,
            "news_count": len(news_items),
            "news_items": [
                {
                    "title": item.title,
                    "summary": item.summary,
                    "link": item.link,
                    "published": item.published,
                    "source": item.source,
                    "sentiment": getattr(item, 'sentiment', None)
                }
                for item in news_items
            ],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching news: {str(e)}")

@app.get("/sources")
async def get_sources():
    try:
        stats = news_agent.get_source_statistics()
        return {
            "success": True,
            "source_statistics": stats,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting sources: {str(e)}")

@app.post("/add_source")
async def add_source(request: AddSourceRequest):
    try:
        news_agent.add_news_source(
            source_type=request.source_type,
            url=request.url,
            name=request.name,
            category=request.category,
            max_items=request.max_items
        )
        return {
            "success": True,
            "message": f"Source {request.name} added successfully",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding source: {str(e)}")

@app.get("/news/sources")
async def list_news_sources():
    try:
        config = news_agent.config
        return {
            "success": True,
            "rss_sources": [
                {
                    "name": source.name,
                    "url": source.url,
                    "category": source.category,
                    "max_items": source.max_items
                }
                for source in config.rss_sources
            ],
            "api_sources": [
                {
                    "name": source.name,
                    "url": source.url,
                    "api_key_required": bool(source.api_key),
                    "category": source.category,
                    "max_items": source.max_items
                }
                for source in config.api_sources
            ],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing sources: {str(e)}")

@app.get("/news/health")
async def news_health():
    try:
        stats = news_agent.get_source_statistics()
        return {
            "success": True,
            "status": "healthy",
            "source_statistics": stats,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

# MCP Integration endpoints
@app.get("/mcp/news")
async def get_mcp_news(limit: int = 20):
    try:
        news_items = await mcp_manager.fetch_news_from_all(limit)
        server_status = await mcp_manager.get_server_status()
        
        return MCPNewsResponse(
            success=True,
            message=f"Successfully fetched {len(news_items)} news items",
            news_count=len(news_items),
            news_items=[
                {
                    "title": item.title,
                    "summary": item.summary,
                    "link": item.link,
                    "published": item.published,
                    "source": item.source,
                    "category": item.category,
                    "sentiment": item.sentiment,
                    "relevance_score": item.relevance_score,
                    "mcp_server": item.mcp_server,
                    "metadata": item.metadata
                }
                for item in news_items
            ],
            server_status=server_status,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching MCP news: {str(e)}")

@app.get("/mcp/status")
async def get_mcp_status():
    try:
        status = await mcp_manager.get_server_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting MCP status: {str(e)}")

@app.get("/mcp/health")
async def mcp_health():
    try:
        await mcp_manager.health_check_all()
        status = await mcp_manager.get_server_status()
        return {
            "success": True,
            "status": "healthy",
            "server_status": status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@app.post("/mcp/server/priority")
async def change_server_priority(request: ServerPriorityRequest):
    try:
        await mcp_manager.switch_server_priority(request.server_name, request.priority)
        return {
            "success": True,
            "message": f"Server {request.server_name} priority changed to {request.priority}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error changing server priority: {str(e)}")

@app.get("/mcp/servers")
async def list_mcp_servers():
    try:
        status = await mcp_manager.get_server_status()
        return {
            "success": True,
            "servers": status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing MCP servers: {str(e)}")

# Fundamentals endpoints
@app.get("/fundamentals/{symbol}")
async def get_fundamentals(symbol: str):
    """Get fundamentals for a specific cryptocurrency symbol"""
    try:
        async with FundamentalsFetcherAgent() as agent:
            fundamentals = await agent.get_fundamentals(symbol.upper())
            
            if fundamentals:
                return FundamentalsResponse(
                    success=True,
                    message=f"Successfully fetched fundamentals for {symbol.upper()}",
                    symbol=symbol.upper(),
                    fundamentals=fundamentals,
                    timestamp=datetime.now(timezone.utc).isoformat()
                )
            else:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Could not find fundamentals for symbol: {symbol.upper()}"
                )
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching fundamentals: {str(e)}")

@app.post("/fundamentals/multiple")
async def get_multiple_fundamentals(symbols: List[str]):
    """Get fundamentals for multiple cryptocurrency symbols"""
    try:
        async with FundamentalsFetcherAgent() as agent:
            fundamentals_dict = await agent.get_multiple_fundamentals(symbols)
            
            return MultipleFundamentalsResponse(
                success=True,
                message=f"Successfully fetched fundamentals for {len(symbols)} symbols",
                symbols=symbols,
                fundamentals=fundamentals_dict,
                timestamp=datetime.now(timezone.utc).isoformat()
            )
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching multiple fundamentals: {str(e)}")

@app.get("/fundamentals/trending")
async def get_trending_coins(limit: int = 10):
    """Get trending coins with fundamentals"""
    try:
        async with FundamentalsFetcherAgent() as agent:
            trending_coins = await agent.get_trending_coins(limit)
            
            return TrendingCoinsResponse(
                success=True,
                message=f"Successfully fetched {len(trending_coins)} trending coins",
                trending_coins=trending_coins,
                count=len(trending_coins),
                timestamp=datetime.now(timezone.utc).isoformat()
            )
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching trending coins: {str(e)}")

@app.get("/fundamentals/market/overview")
async def get_market_overview():
    """Get overall market overview and statistics"""
    try:
        async with FundamentalsFetcherAgent() as agent:
            market_overview = await agent.get_market_overview()
            
            return MarketOverviewResponse(
                success=True,
                message="Successfully fetched market overview",
                market_overview=market_overview,
                timestamp=datetime.now(timezone.utc).isoformat()
            )
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching market overview: {str(e)}")

@app.get("/fundamentals/search/{query}")
async def search_coins(query: str):
    """Search for coins by name or symbol"""
    try:
        async with FundamentalsFetcherAgent() as agent:
            search_results = await agent.search_coin(query)
            
            return {
                "success": True,
                "query": query,
                "results": search_results,
                "count": len(search_results),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching coins: {str(e)}")

# News Analysis endpoints
@app.post("/analyze")
async def analyze_news(request: NewsAnalysisRequest):
    """Analyze a single news article for sentiment and fundamental impact"""
    try:
        analysis_result = await analyzer_agent.analyze_news(
            title=request.title,
            summary=request.summary
        )
        
        if analysis_result:
            return NewsAnalysisResponse(
                success=True,
                message="News analysis completed successfully",
                analysis={
                    "summary": analysis_result.summary,
                    "sentiment": analysis_result.sentiment,
                    "fundamentals": analysis_result.fundamentals,
                    "confidence": analysis_result.confidence,
                    "analysis_timestamp": analysis_result.analysis_timestamp
                },
                agent_status=analyzer_agent.get_agent_status(),
                timestamp=datetime.now(timezone.utc).isoformat()
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to analyze news article"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing news: {str(e)}")

@app.post("/analyze/batch")
async def analyze_multiple_news(request: BatchAnalysisRequest):
    """Analyze multiple news articles for sentiment and fundamental impact"""
    try:
        analysis_results = await analyzer_agent.analyze_multiple_news(request.news_items)
        
        return BatchAnalysisResponse(
            success=True,
            message=f"Successfully analyzed {len(analysis_results)} news articles",
            analyses=analysis_results,
            total_analyzed=len(analysis_results),
            agent_status=analyzer_agent.get_agent_status(),
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in batch analysis: {str(e)}")

@app.get("/analyze/status")
async def get_analyzer_status():
    """Get the current status of the analyzer agent"""
    try:
        return {
            "success": True,
            "agent_status": analyzer_agent.get_agent_status(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting analyzer status: {str(e)}")

# Post Creation endpoints
@app.post("/create_post")
async def create_social_post(request: PostCreationRequest):
    """Create social media posts based on analysis and fundamentals"""
    try:
        post_result = await post_creator_agent.create_social_posts(
            analysis=request.analysis,
            fundamentals=request.fundamentals,
            news_title=request.news_title
        )
        
        if post_result:
            # Validate post lengths
            validation = post_creator_agent.validate_post_lengths(post_result)
            
            return PostCreationResponse(
                success=True,
                message="Social media posts created successfully",
                posts={
                    "twitter": {
                        "platform": post_result.twitter_post.platform,
                        "content": post_result.twitter_post.content,
                        "hashtags": post_result.twitter_post.hashtags,
                        "emojis": post_result.twitter_post.emojis,
                        "character_count": post_result.twitter_post.character_count,
                        "sentiment": post_result.twitter_post.sentiment,
                        "engagement_score": post_result.twitter_post.engagement_score
                    },
                    "linkedin": {
                        "platform": post_result.linkedin_post.platform,
                        "content": post_result.linkedin_post.content,
                        "hashtags": post_result.linkedin_post.hashtags,
                        "emojis": post_result.linkedin_post.emojis,
                        "character_count": post_result.linkedin_post.character_count,
                        "sentiment": post_result.linkedin_post.sentiment,
                        "engagement_score": post_result.linkedin_post.engagement_score
                    },
                    "telegram": {
                        "platform": post_result.telegram_post.platform,
                        "content": post_result.telegram_post.content,
                        "hashtags": post_result.telegram_post.hashtags,
                        "emojis": post_result.telegram_post.emojis,
                        "character_count": post_result.telegram_post.character_count,
                        "sentiment": post_result.telegram_post.sentiment,
                        "engagement_score": post_result.telegram_post.engagement_score
                    }
                },
                validation=validation,
                agent_status=post_creator_agent.get_agent_status(),
                timestamp=datetime.now(timezone.utc).isoformat()
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to create social media posts"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating posts: {str(e)}")

@app.post("/create_post/batch")
async def create_multiple_posts(request: BatchPostCreationRequest):
    """Create social media posts for multiple analysis results"""
    try:
        post_results = await post_creator_agent.create_multiple_posts(request.posts_data)
        
        return BatchPostCreationResponse(
            success=True,
            message=f"Successfully created posts for {len(post_results)} analysis results",
            created_posts=post_results,
            total_created=len(post_results),
            agent_status=post_creator_agent.get_agent_status(),
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in batch post creation: {str(e)}")

@app.get("/create_post/status")
async def get_post_creator_status():
    """Get the current status of the post creator agent"""
    try:
        return {
            "success": True,
            "agent_status": post_creator_agent.get_agent_status(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting post creator status: {str(e)}")

# Orchestrator Pipeline endpoints
@app.post("/run_pipeline")
async def run_complete_pipeline(request: PipelineRequest):
    """Run the complete pipeline: Ingestion → Analysis → Fundamentals → Post Creation"""
    try:
        pipeline_result = await orchestrator_agent.run_pipeline(
            symbol=request.symbol,
            news_limit=request.news_limit
        )
        
        if pipeline_result:
            return PipelineResponse(
                success=True,
                message="Pipeline executed successfully",
                pipeline_result={
                    "news_item": pipeline_result.news_item,
                    "analysis": pipeline_result.analysis,
                    "fundamentals": pipeline_result.fundamentals,
                    "posts": pipeline_result.posts,
                    "pipeline_status": pipeline_result.pipeline_status,
                    "execution_time": pipeline_result.execution_time,
                    "timestamp": pipeline_result.timestamp
                },
                agent_status=orchestrator_agent.get_agent_status(),
                pipeline_info=orchestrator_agent.get_pipeline_info(),
                timestamp=datetime.now(timezone.utc).isoformat()
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Pipeline execution failed"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running pipeline: {str(e)}")

@app.post("/run_pipeline/multiple")
async def run_multiple_news_pipeline(request: MultiplePipelineRequest):
    """Run pipeline for multiple news items"""
    try:
        pipeline_results = await orchestrator_agent.run_pipeline_with_multiple_news(
            news_limit=request.news_limit
        )
        
        return MultiplePipelineResponse(
            success=True,
            message=f"Pipeline executed for {len(pipeline_results)} news items",
            pipeline_results=[
                {
                    "news_item": result.news_item,
                    "analysis": result.analysis,
                    "fundamentals": result.fundamentals,
                    "posts": result.posts,
                    "pipeline_status": result.pipeline_status,
                    "timestamp": result.timestamp
                }
                for result in pipeline_results
            ],
            total_processed=len(pipeline_results),
            agent_status=orchestrator_agent.get_agent_status(),
            pipeline_info=orchestrator_agent.get_pipeline_info(),
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running multiple news pipeline: {str(e)}")

@app.get("/run_pipeline/status")
async def get_orchestrator_status():
    """Get the current status of the orchestrator agent"""
    try:
        return {
            "success": True,
            "agent_status": orchestrator_agent.get_agent_status(),
            "pipeline_info": orchestrator_agent.get_pipeline_info(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting orchestrator status: {str(e)}")

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize MCP manager on startup"""
    try:
        await mcp_manager.initialize()
        print("✅ MCP Manager initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing MCP Manager: {e}")

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
