from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
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

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="AI Finance Assistant MVP",
    description="AI-powered financial insights with news ingestion and MCP server integration",
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

# Initialize agents
news_agent = NewsIngestionAgent()
mcp_manager = MCPManager()

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
            "health": "/ping",
            "chat": "/chat",
            "news": "/fetch_news",
            "mcp_news": "/mcp/news",
            "fundamentals": "/fundamentals/{symbol}",
            "trending": "/fundamentals/trending",
            "market_overview": "/fundamentals/market/overview"
        }
    }

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
