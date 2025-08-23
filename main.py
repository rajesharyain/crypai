from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
import logging
from datetime import datetime, timezone
import asyncio

# Import our ingestion agent
from ingestion import (
    NewsIngestionAgent, 
    NewsItemResponse, 
    NewsFetchResponse, 
    SourceStatsResponse,
    RSSNewsSource,
    APINewsSource
)

# Import MCP integration
from mcp_integration import (
    MCPManager,
    MCPNewsResponse,
    MCPNewsItemResponse,
    MCPManagerStatus
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Finance Assistant MVP",
    description="Quick Lean MVP with LangChain + FastAPI for AI-powered financial insights, news ingestion, and MCP server integration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the news ingestion agent
news_agent = NewsIngestionAgent()

# Initialize the MCP manager
mcp_manager = MCPManager()

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    model: str = "gpt-3.5-turbo"

class ChatResponse(BaseModel):
    response: str
    model_used: str

class AddSourceRequest(BaseModel):
    source_type: str  # "rss" or "api"
    url: str
    name: str
    category: str = "crypto"
    api_key: str = None

class ServerPriorityRequest(BaseModel):
    server_name: str  # "chaingpt", "coin", "cryptopanic"
    priority: str  # "active" or "fallback"

# Health check endpoint
@app.get("/ping")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "AI Finance Assistant is running!"}

@app.get("/")
async def root():
    """Root endpoint with project information"""
    return {
        "message": "AI Finance Assistant MVP",
        "version": "1.0.0",
        "endpoints": {
            "health": "/ping",
            "chat": "/chat",
            "news": "/fetch_news",
            "mcp_news": "/mcp/news",
            "sources": "/sources",
            "add_source": "/add_source",
            "mcp_status": "/mcp/status",
            "mcp_health": "/mcp/health",
            "docs": "/docs"
        }
    }

# Chat endpoint using LangChain
@app.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """Chat with AI using LangChain and OpenAI"""
    try:
        # Get OpenAI API key
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        # Initialize LangChain chat model
        llm = ChatOpenAI(
            model=request.model,
            openai_api_key=openai_api_key,
            temperature=0.7
        )
        
        # Create message and get response
        messages = [HumanMessage(content=request.message)]
        response = llm.invoke(messages)
        
        logger.info(f"Chat request processed successfully with model: {request.model}")
        
        return ChatResponse(
            response=response.content,
            model_used=request.model
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")

# News ingestion endpoints
@app.get("/fetch_news", response_model=NewsFetchResponse)
async def fetch_news(include_sentiment: bool = False, limit: int = 50):
    """Fetch latest news from all configured sources"""
    try:
        logger.info("Starting news fetch operation")
        
        # Fetch news from all sources
        news_items = await news_agent.fetch_all_news()
        
        # Limit the number of items
        if limit and limit > 0:
            news_items = news_items[:limit]
        
        # Perform sentiment analysis if requested
        if include_sentiment:
            logger.info("Performing sentiment analysis on news items")
            news_items = await news_agent.analyze_news_sentiment(news_items)
        
        # Convert to response format
        news_responses = []
        for item in news_items:
            news_responses.append(NewsItemResponse(
                title=item.title,
                summary=item.summary,
                link=item.link,
                published=item.published,
                source=item.source,
                category=item.category,
                sentiment=item.sentiment,
                relevance_score=item.relevance_score
            ))
        
        # Get source statistics
        source_stats = news_agent.get_source_statistics()
        
        return NewsFetchResponse(
            success=True,
            message=f"Successfully fetched {len(news_responses)} news items",
            news_count=len(news_responses),
            news_items=news_responses,
            source_stats=source_stats,
            timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        )
        
    except Exception as e:
        logger.error(f"Error in fetch_news endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching news: {str(e)}")

# MCP News endpoints
@app.get("/mcp/news", response_model=MCPNewsResponse)
async def fetch_mcp_news(limit: int = 20, include_fallback: bool = True):
    """Fetch news from MCP servers (ChainGPT, Coin, CryptoPanic)"""
    try:
        logger.info("Starting MCP news fetch operation")
        
        # Initialize MCP manager if not already done
        if not mcp_manager.active_servers and not mcp_manager.fallback_servers:
            await mcp_manager.initialize()
        
        # Fetch news from MCP servers
        news_items = await mcp_manager.fetch_news_from_all(limit)
        
        # Convert to response format
        news_responses = []
        for item in news_items:
            news_responses.append(MCPNewsItemResponse(
                title=item.title,
                summary=item.summary,
                link=item.link,
                published=item.published,
                source=item.source,
                category=item.category,
                sentiment=item.sentiment,
                relevance_score=item.relevance_score,
                mcp_server=item.mcp_server,
                metadata=item.metadata
            ))
        
        # Get server status
        server_status = await mcp_manager.get_server_status()
        
        return MCPNewsResponse(
            success=True,
            message=f"Successfully fetched {len(news_responses)} news items from MCP servers",
            news_count=len(news_responses),
            news_items=news_responses,
            server_status=MCPManagerStatus(**server_status),
            timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        )
        
    except Exception as e:
        logger.error(f"Error in MCP news fetch endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching MCP news: {str(e)}")

@app.get("/mcp/status", response_model=MCPManagerStatus)
async def get_mcp_status():
    """Get status of all MCP servers"""
    try:
        # Initialize if needed
        if not mcp_manager.active_servers and not mcp_manager.fallback_servers:
            await mcp_manager.initialize()
        
        status = await mcp_manager.get_server_status()
        return MCPManagerStatus(**status)
        
    except Exception as e:
        logger.error(f"Error getting MCP status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting MCP status: {str(e)}")

@app.get("/mcp/health")
async def mcp_health_check():
    """Health check for MCP servers"""
    try:
        # Perform health check on all servers
        await mcp_manager.health_check_all()
        
        # Get updated status
        status = await mcp_manager.get_server_status()
        
        return {
            "status": "healthy" if status["active_count"] > 0 else "degraded",
            "message": f"MCP system operational with {status['active_count']} active servers",
            "active_servers": status["active_count"],
            "fallback_servers": status["fallback_count"],
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        }
        
    except Exception as e:
        logger.error(f"MCP health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "message": f"MCP system error: {str(e)}",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        }

@app.post("/mcp/server/priority")
async def change_server_priority(request: ServerPriorityRequest):
    """Change MCP server priority between active and fallback"""
    try:
        await mcp_manager.switch_server_priority(request.server_name, request.priority)
        
        return {
            "success": True,
            "message": f"Successfully moved {request.server_name} to {request.priority} priority",
            "server_name": request.server_name,
            "new_priority": request.priority
        }
        
    except Exception as e:
        logger.error(f"Error changing server priority: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error changing server priority: {str(e)}")

@app.get("/mcp/servers")
async def list_mcp_servers():
    """List all available MCP servers with their details"""
    try:
        servers_info = {}
        for server_name, server in mcp_manager.servers.items():
            servers_info[server_name] = {
                "name": server.name,
                "base_url": server.base_url,
                "enabled": server.enabled,
                "health_status": server.health_status,
                "last_check": server.last_check,
                "priority": "active" if server in mcp_manager.active_servers else "fallback"
            }
        
        return {
            "success": True,
            "servers": servers_info,
            "total_count": len(servers_info)
        }
        
    except Exception as e:
        logger.error(f"Error listing MCP servers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing MCP servers: {str(e)}")

# Traditional news endpoints
@app.get("/sources", response_model=SourceStatsResponse)
async def get_source_statistics():
    """Get statistics about configured news sources"""
    try:
        stats = news_agent.get_source_statistics()
        
        return SourceStatsResponse(
            success=True,
            message="Source statistics retrieved successfully",
            statistics=stats
        )
        
    except Exception as e:
        logger.error(f"Error in sources endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving source statistics: {str(e)}")

@app.post("/add_source")
async def add_news_source(request: AddSourceRequest):
    """Add a new news source dynamically"""
    try:
        if request.source_type.lower() == "rss":
            # Add RSS source
            new_source = RSSNewsSource(
                feed_url=request.url,
                source_name=request.name,
                category=request.category
            )
            news_agent.add_news_source(new_source)
            
            return {
                "success": True,
                "message": f"RSS source '{request.name}' added successfully",
                "source_type": "RSS",
                "source_name": request.name
            }
            
        elif request.source_type.lower() == "api":
            # Add API source
            if not request.api_key:
                raise HTTPException(status_code=400, detail="API key required for API sources")
            
            new_source = APINewsSource(
                api_url=request.url,
                api_key=request.api_key,
                source_name=request.name
            )
            news_agent.add_news_source(new_source)
            
            return {
                "success": True,
                "message": f"API source '{request.name}' added successfully",
                "source_type": "API",
                "source_name": request.name
            }
            
        else:
            raise HTTPException(status_code=400, detail="Invalid source type. Use 'rss' or 'api'")
            
    except Exception as e:
        logger.error(f"Error adding news source: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error adding news source: {str(e)}")

@app.get("/news/sources")
async def list_news_sources():
    """List all configured news sources with their details"""
    try:
        sources = []
        for source in news_agent.news_sources:
            source_info = {
                "name": source.get_source_name(),
                "type": "RSS" if hasattr(source, 'feed_url') else "API",
                "url": getattr(source, 'feed_url', getattr(source, 'api_url', 'N/A')),
                "category": getattr(source, 'category', 'N/A')
            }
            sources.append(source_info)
        
        return {
            "success": True,
            "sources": sources,
            "total_count": len(sources)
        }
        
    except Exception as e:
        logger.error(f"Error listing news sources: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing news sources: {str(e)}")

@app.get("/news/health")
async def news_health_check():
    """Health check for news ingestion system"""
    try:
        # Test fetching from one source to verify system health
        source_stats = news_agent.get_source_statistics()
        
        return {
            "status": "healthy",
            "message": "News ingestion system is operational",
            "active_sources": source_stats["total_sources"],
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        }
        
    except Exception as e:
        logger.error(f"News health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "message": f"News ingestion system error: {str(e)}",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        }

# Additional utility endpoints
@app.get("/models")
async def get_available_models():
    """Get available OpenAI models"""
    return {
        "models": [
            "gpt-3.5-turbo",
            "gpt-4",
            "gpt-4-turbo-preview"
        ]
    }

# Startup event to initialize MCP servers
@app.on_event("startup")
async def startup_event():
    """Initialize MCP servers on startup"""
    try:
        logger.info("Initializing MCP servers on startup...")
        await mcp_manager.initialize()
        logger.info("MCP servers initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize MCP servers: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
