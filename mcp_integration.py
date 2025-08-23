"""
MCP (Model Context Protocol) Integration for Enhanced News Ingestion
Provides access to ChainGPT AI News, Coin, and CryptoPanic MCP servers
with fallback to free/open-source alternatives including RSS feeds
"""

import asyncio
import json
import logging
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod
import httpx
import feedparser
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from bs4 import BeautifulSoup
import re

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MCPNewsItem:
    """Standardized MCP news item structure"""
    title: str
    summary: str
    link: str
    published: str
    source: str
    category: str
    sentiment: Optional[str] = None
    relevance_score: Optional[float] = None
    mcp_server: str = "unknown"
    metadata: Dict[str, Any] = None

class MCPServer(ABC):
    """Abstract base class for MCP servers"""
    
    def __init__(self, name: str, base_url: str, api_key: str = None, enabled: bool = True):
        self.name = name
        self.base_url = base_url
        self.api_key = api_key
        self.enabled = enabled
        self.health_status = "unknown"
        self.last_check = None
    
    @abstractmethod
    async def check_health(self) -> bool:
        """Check if the MCP server is healthy"""
        pass
    
    @abstractmethod
    async def fetch_news(self, limit: int = 20) -> List[MCPNewsItem]:
        """Fetch news from the MCP server"""
        pass
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information and status"""
        # Convert datetime to string if it exists
        last_check_str = None
        if self.last_check:
            if isinstance(self.last_check, datetime):
                last_check_str = self.last_check.isoformat()
            else:
                last_check_str = str(self.last_check)
        
        return {
            "name": self.name,
            "base_url": self.base_url,
            "enabled": self.enabled,
            "health_status": self.health_status,
            "last_check": last_check_str
        }

class RSSNewsSource(MCPServer):
    """RSS-based news source (CoinDesk, CoinTelegraph, etc.)"""
    
    def __init__(self, name: str, rss_url: str, enabled: bool = True):
        super().__init__(name=name, base_url=rss_url, enabled=enabled)
        self.rss_url = rss_url
    
    async def check_health(self) -> bool:
        """Check RSS feed health by attempting to parse it"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.rss_url)
                
                if response.status_code == 200:
                    # Try to parse the RSS feed
                    feed = feedparser.parse(response.content)
                    if feed.entries:
                        self.health_status = "healthy"
                        self.last_check = datetime.now(timezone.utc)
                        return True
                    else:
                        self.health_status = "unhealthy"
                        return False
                else:
                    self.health_status = "unhealthy"
                    return False
                    
        except Exception as e:
            logger.warning(f"{self.name} RSS health check failed: {e}")
            self.health_status = "error"
            return False
    
    async def fetch_news(self, limit: int = 20) -> List[MCPNewsItem]:
        """Fetch news from RSS feed"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.rss_url)
                
                if response.status_code == 200:
                    feed = feedparser.parse(response.content)
                    news_items = []
                    
                    for entry in feed.entries[:limit]:
                        # Clean HTML from summary
                        summary = self._clean_html(entry.get('summary', ''))
                        if not summary and entry.get('description'):
                            summary = self._clean_html(entry.get('description', ''))
                        
                        # Parse published date
                        published = self._parse_date(entry.get('published', ''))
                        
                        # Calculate relevance score based on recency and source
                        relevance_score = self._calculate_relevance_score(entry, published)
                        
                        news_item = MCPNewsItem(
                            title=entry.get('title', 'No Title'),
                            summary=summary or "No summary available",
                            link=entry.get('link', ''),
                            published=published,
                            source=self.name,
                            category="crypto",
                            sentiment="neutral",  # RSS doesn't provide sentiment
                            relevance_score=relevance_score,
                            mcp_server=f"rss_{self.name.lower().replace(' ', '_')}",
                            metadata={
                                "author": entry.get('author', ''),
                                "tags": [tag.term for tag in entry.get('tags', [])],
                                "guid": entry.get('id', ''),
                                "feed_title": feed.feed.get('title', ''),
                                "feed_description": feed.feed.get('description', '')
                            }
                        )
                        news_items.append(news_item)
                    
                    logger.info(f"Successfully fetched {len(news_items)} news items from {self.name}")
                    return news_items
                else:
                    logger.warning(f"{self.name} RSS returned status {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching from {self.name}: {e}")
            return []
    
    def _clean_html(self, html_text: str) -> str:
        """Clean HTML tags from text"""
        if not html_text:
            return ""
        
        # Use BeautifulSoup to clean HTML
        try:
            soup = BeautifulSoup(html_text, 'html.parser')
            return soup.get_text(separator=' ', strip=True)
        except:
            # Fallback: simple regex cleanup
            clean_text = re.sub(r'<[^>]+>', '', html_text)
            clean_text = re.sub(r'\s+', ' ', clean_text)
            return clean_text.strip()
    
    def _parse_date(self, date_str: str) -> str:
        """Parse and standardize date format"""
        if not date_str:
            return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        
        try:
            # Try to parse various date formats
            parsed_date = feedparser._parse_date(date_str)
            if parsed_date:
                return parsed_date.strftime("%Y-%m-%d %H:%M:%S UTC")
        except:
            pass
        
        # Fallback to current time
        return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    def _calculate_relevance_score(self, entry, published_date: str) -> float:
        """Calculate relevance score for RSS entries"""
        base_score = 7.0  # Base score for RSS sources
        
        # Boost score for recent entries
        try:
            if published_date:
                parsed_date = datetime.strptime(published_date, "%Y-%m-%d %H:%M:%S UTC")
                hours_ago = (datetime.now(timezone.utc) - parsed_date).total_seconds() / 3600
                if hours_ago < 1:
                    base_score += 2.0  # Very recent
                elif hours_ago < 24:
                    base_score += 1.0  # Recent
                elif hours_ago < 72:
                    base_score += 0.5  # Somewhat recent
        except:
            pass
        
        # Boost score for entries with more content
        if entry.get('summary') and len(entry.get('summary', '')) > 100:
            base_score += 0.5
        
        return min(10.0, base_score)

class ChainGPTAINewsMCPServer(MCPServer):
    """ChainGPT AI News MCP Server integration"""
    
    def __init__(self, api_key: str = None):
        super().__init__(
            name="ChainGPT AI News",
            base_url="https://api.chain-gpt.com/v1",
            api_key=api_key or os.getenv("CHAINGPT_API_KEY"),
            enabled=bool(api_key or os.getenv("CHAINGPT_API_KEY"))
        )
    
    async def check_health(self) -> bool:
        """Check ChainGPT API health"""
        if not self.enabled or not self.api_key:
            return False
            
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                response = await client.get(f"{self.base_url}/health", headers=headers)
                
                if response.status_code == 200:
                    self.health_status = "healthy"
                    self.last_check = datetime.now(timezone.utc)
                    return True
                else:
                    self.health_status = "unhealthy"
                    return False
                    
        except Exception as e:
            logger.warning(f"ChainGPT health check failed: {e}")
            self.health_status = "error"
            return False
    
    async def fetch_news(self, limit: int = 20) -> List[MCPNewsItem]:
        """Fetch news from ChainGPT AI News API"""
        if not self.enabled or not self.api_key:
            return []
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Accept": "application/json"
                }
                
                # Fetch latest crypto news
                response = await client.get(
                    f"{self.base_url}/news",
                    headers=headers,
                    params={"limit": limit, "category": "crypto"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    news_items = []
                    
                    for article in data.get("articles", []):
                        news_item = MCPNewsItem(
                            title=article.get("title", "No Title"),
                            summary=article.get("summary", article.get("description", "No Summary")),
                            link=article.get("url", ""),
                            published=article.get("published_at", ""),
                            source="ChainGPT AI News",
                            category="crypto",
                            sentiment=article.get("sentiment", "neutral"),
                            relevance_score=article.get("relevance_score", 5.0),
                            mcp_server="chaingpt",
                            metadata={
                                "ai_generated": article.get("ai_generated", False),
                                "confidence": article.get("confidence", 0.0),
                                "entities": article.get("entities", [])
                            }
                        )
                        news_items.append(news_item)
                    
                    logger.info(f"Successfully fetched {len(news_items)} news items from ChainGPT")
                    return news_items
                else:
                    logger.warning(f"ChainGPT API returned status {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching from ChainGPT: {e}")
            return []

class CoinMCPServer(MCPServer):
    """Coin MCP Server integration (using CoinGecko as fallback)"""
    
    def __init__(self):
        super().__init__(
            name="Coin MCP Server",
            base_url="https://api.coingecko.com/api/v3",
            enabled=True  # CoinGecko is free
        )
    
    async def check_health(self) -> bool:
        """Check CoinGecko API health"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/ping")
                
                if response.status_code == 200:
                    self.health_status = "healthy"
                    self.last_check = datetime.now(timezone.utc)
                    return True
                else:
                    self.health_status = "unhealthy"
                    return False
                    
        except Exception as e:
            logger.warning(f"CoinGecko health check failed: {e}")
            self.health_status = "error"
            return False
    
    async def fetch_news(self, limit: int = 20) -> List[MCPNewsItem]:
        """Fetch crypto news from CoinGecko (free alternative)"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Get trending coins first
                trending_response = await client.get(f"{self.base_url}/search/trending")
                
                if trending_response.status_code == 200:
                    trending_data = trending_response.json()
                    trending_coins = trending_data.get("coins", [])[:5]
                    
                    news_items = []
                    
                    # Create news items from trending data
                    for coin in trending_coins:
                        coin_data = coin.get("item", {})
                        
                        news_item = MCPNewsItem(
                            title=f"{coin_data.get('name', 'Unknown')} Trending in Crypto",
                            summary=f"{coin_data.get('name', 'Unknown')} is currently trending with {coin_data.get('price_btc', 0)} BTC price and {coin_data.get('score', 0)} trend score.",
                            link=f"https://coingecko.com/en/coins/{coin_data.get('id', '')}",
                            published=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                            source="CoinGecko",
                            category="crypto",
                            sentiment="neutral",
                            relevance_score=8.0,
                            mcp_server="coin",
                            metadata={
                                "coin_id": coin_data.get("id"),
                                "symbol": coin_data.get("symbol"),
                                "market_cap_rank": coin_data.get("market_cap_rank"),
                                "trend_score": coin_data.get("score")
                            }
                        )
                        news_items.append(news_item)
                    
                    # Get market data for additional context
                    if trending_coins:
                        coin_ids = [coin["item"]["id"] for coin in trending_coins]
                        market_response = await client.get(
                            f"{self.base_url}/coins/markets",
                            params={
                                "vs_currency": "usd",
                                "ids": ",".join(coin_ids),
                                "order": "market_cap_desc",
                                "per_page": limit,
                                "page": 1
                            }
                        )
                        
                        if market_response.status_code == 200:
                            market_data = market_response.json()
                            
                            for i, market_info in enumerate(market_data):
                                if i < len(news_items):
                                    news_items[i].metadata.update({
                                        "current_price_usd": market_info.get("current_price"),
                                        "market_cap": market_info.get("market_cap"),
                                        "price_change_24h": market_info.get("price_change_percentage_24h")
                                    })
                    
                    logger.info(f"Successfully fetched {len(news_items)} trending items from CoinGecko")
                    return news_items
                else:
                    logger.warning(f"CoinGecko API returned status {trending_response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching from CoinGecko: {e}")
            return []

class CryptoPanicMCPServer(MCPServer):
    """CryptoPanic MCP Server integration (using free tier)"""
    
    def __init__(self):
        super().__init__(
            name="CryptoPanic MCP Server",
            base_url="https://cryptopanic.com/api/v1",
            enabled=True  # CryptoPanic has a free tier
        )
    
    async def check_health(self) -> bool:
        """Check CryptoPanic API health"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/posts/")
                
                if response.status_code == 200:
                    self.health_status = "healthy"
                    self.last_check = datetime.now(timezone.utc)
                    return True
                else:
                    self.health_status = "unhealthy"
                    return False
                    
        except Exception as e:
            logger.warning(f"CryptoPanic health check failed: {e}")
            self.health_status = "error"
            return False
    
    async def fetch_news(self, limit: int = 20) -> List[MCPNewsItem]:
        """Fetch news from CryptoPanic (free tier)"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/posts/",
                    params={"auth_token": "free", "filter": "hot", "public": True}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    news_items = []
                    
                    for post in data.get("results", [])[:limit]:
                        # Determine sentiment from votes
                        votes = post.get("votes", {})
                        positive_votes = votes.get("positive", 0)
                        negative_votes = votes.get("negative", 0)
                        
                        if positive_votes > negative_votes:
                            sentiment = "positive"
                        elif negative_votes > positive_votes:
                            sentiment = "negative"
                        else:
                            sentiment = "neutral"
                        
                        # Calculate relevance score based on votes and comments
                        total_votes = positive_votes + negative_votes
                        comments_count = post.get("comments_count", 0)
                        relevance_score = min(10.0, (total_votes + comments_count) / 2)
                        
                        news_item = MCPNewsItem(
                            title=post.get("title", "No Title"),
                            summary=post.get("currencies", []),
                            link=post.get("url", ""),
                            published=post.get("published_at", ""),
                            source="CryptoPanic",
                            category="crypto",
                            sentiment=sentiment,
                            relevance_score=relevance_score,
                            mcp_server="cryptopanic",
                            metadata={
                                "currencies": post.get("currencies", []),
                                "votes": votes,
                                "comments_count": comments_count,
                                "domain": post.get("domain")
                            }
                        )
                        news_items.append(news_item)
                    
                    logger.info(f"Successfully fetched {len(news_items)} news items from CryptoPanic")
                    return news_items
                else:
                    logger.warning(f"CryptoPanic API returned status {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching from CryptoPanic: {e}")
            return []

class MCPManager:
    """Manages multiple MCP servers with fallback strategies"""
    
    def __init__(self):
        # Initialize all available news sources
        self.servers = {
            # RSS-based sources (always available, no API keys needed)
            "coindesk": RSSNewsSource("CoinDesk", "https://www.coindesk.com/arc/outboundfeeds/rss/"),
            "cointelegraph": RSSNewsSource("CoinTelegraph", "https://cointelegraph.com/rss"),
            
            # API-based sources (may require API keys)
            "chaingpt": ChainGPTAINewsMCPServer(),
            "coin": CoinMCPServer(),
            "cryptopanic": CryptoPanicMCPServer(),
        }
        
        self.active_servers = []
        self.fallback_servers = []
        self.health_check_interval = 300  # 5 minutes
        
        # Priority order: RSS sources first (reliable), then API sources
        self.source_priority = [
            "coindesk",      # High priority: reliable RSS
            "cointelegraph", # High priority: reliable RSS
            "chaingpt",      # Medium priority: AI-powered if available
            "coin",          # Medium priority: free API
            "cryptopanic"    # Low priority: free API
        ]
    
    async def initialize(self):
        """Initialize and check health of all MCP servers"""
        logger.info("Initializing MCP servers and RSS sources...")
        
        # First, check RSS sources (these should always work)
        for source_name in ["coindesk", "cointelegraph"]:
            if source_name in self.servers:
                server = self.servers[source_name]
                try:
                    is_healthy = await server.check_health()
                    if is_healthy:
                        self.active_servers.append(server)
                        logger.info(f"✅ {server.name} RSS is healthy and active")
                    else:
                        self.fallback_servers.append(server)
                        logger.warning(f"⚠️ {server.name} RSS is unhealthy, moved to fallback")
                except Exception as e:
                    logger.error(f"❌ Error initializing {server.name}: {e}")
                    self.fallback_servers.append(server)
        
        # Then check API-based sources
        for source_name in ["chaingpt", "coin", "cryptopanic"]:
            if source_name in self.servers:
                server = self.servers[source_name]
                if server.enabled:
                    try:
                        is_healthy = await server.check_health()
                        if is_healthy:
                            self.active_servers.append(server)
                            logger.info(f"✅ {server.name} is healthy and active")
                        else:
                            self.fallback_servers.append(server)
                            logger.warning(f"⚠️ {server.name} is unhealthy, moved to fallback")
                    except Exception as e:
                        logger.error(f"❌ Error initializing {server.name}: {e}")
                        self.fallback_servers.append(server)
                else:
                    logger.info(f"ℹ️ {server.name} is disabled")
        
        logger.info(f"Initialized {len(self.active_servers)} active and {len(self.fallback_servers)} fallback sources")
        
        # Ensure we have at least some working sources
        if not self.active_servers:
            logger.warning("⚠️ No active sources found, trying to activate fallback sources...")
            await self._activate_fallback_sources()
    
    async def _activate_fallback_sources(self):
        """Activate fallback sources when no active sources are available"""
        for server in self.fallback_servers[:2]:  # Activate up to 2 fallback sources
            try:
                is_healthy = await server.check_health()
                if is_healthy:
                    self.fallback_servers.remove(server)
                    self.active_servers.append(server)
                    logger.info(f"✅ Activated fallback source: {server.name}")
            except Exception as e:
                logger.error(f"❌ Failed to activate fallback source {server.name}: {e}")
    
    async def fetch_news_from_all(self, limit: int = 20) -> List[MCPNewsItem]:
        """Fetch news from all active MCP servers and RSS sources"""
        all_news = []
        
        # Fetch from active servers
        for server in self.active_servers:
            try:
                news_items = await server.fetch_news(limit)
                all_news.extend(news_items)
            except Exception as e:
                logger.error(f"Error fetching from {server.name}: {e}")
                # Move to fallback if server fails
                if server in self.active_servers:
                    self.active_servers.remove(server)
                    self.fallback_servers.append(server)
        
        # If no active servers or insufficient news, try fallback servers
        if len(all_news) < limit and self.fallback_servers:
            logger.info("Using fallback sources to get more news")
            for server in self.fallback_servers[:3]:  # Try up to 3 fallback sources
                try:
                    news_items = await server.fetch_news(limit // 2)
                    all_news.extend(news_items)
                except Exception as e:
                    logger.error(f"Error fetching from fallback {server.name}: {e}")
        
        # Remove duplicates and sort by relevance
        unique_news = self._remove_duplicates(all_news)
        unique_news.sort(key=lambda x: x.relevance_score or 0, reverse=True)
        
        return unique_news[:limit]
    
    def _remove_duplicates(self, news_items: List[MCPNewsItem]) -> List[MCPNewsItem]:
        """Remove duplicate news items based on title similarity"""
        unique_items = []
        seen_titles = set()
        
        for item in news_items:
            normalized_title = item.title.lower().strip()
            
            is_duplicate = False
            for seen_title in seen_titles:
                if self._similarity_score(normalized_title, seen_title) > 0.8:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_items.append(item)
                seen_titles.add(normalized_title)
        
        return unique_items
    
    def _similarity_score(self, title1: str, title2: str) -> float:
        """Calculate similarity score between two titles"""
        words1 = set(title1.split())
        words2 = set(title2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    async def get_server_status(self) -> Dict[str, Any]:
        """Get status of all MCP servers and RSS sources"""
        status = {
            "active_servers": [server.get_server_info() for server in self.active_servers],
            "fallback_servers": [server.get_server_info() for server in self.fallback_servers],
            "total_servers": len(self.servers),
            "active_count": len(self.active_servers),
            "fallback_count": len(self.fallback_servers),
            "source_types": {
                "rss_sources": [name for name, server in self.servers.items() if isinstance(server, RSSNewsSource)],
                "api_sources": [name for name, server in self.servers.items() if not isinstance(server, RSSNewsSource)]
            }
        }
        return status
    
    async def switch_server_priority(self, server_name: str, priority: str):
        """Switch server between active and fallback"""
        if server_name in self.servers:
            server = self.servers[server_name]
            
            if priority == "active" and server in self.fallback_servers:
                self.fallback_servers.remove(server)
                self.active_servers.append(server)
                logger.info(f"Moved {server.name} to active sources")
            elif priority == "fallback" and server in self.active_servers:
                self.active_servers.remove(server)
                self.fallback_servers.append(server)
                logger.info(f"Moved {server.name} to fallback sources")
    
    async def health_check_all(self):
        """Perform health check on all servers and sources"""
        logger.info("Performing health check on all sources...")
        
        for server_name, server in self.servers.items():
            if server.enabled:
                try:
                    is_healthy = await server.check_health()
                    
                    if is_healthy and server in self.fallback_servers:
                        # Move back to active if healthy
                        self.fallback_servers.remove(server)
                        self.active_servers.append(server)
                        logger.info(f"✅ {server.name} recovered and moved to active")
                    elif not is_healthy and server in self.active_servers:
                        # Move to fallback if unhealthy
                        self.active_servers.remove(server)
                        self.fallback_servers.append(server)
                        logger.warning(f"⚠️ {server.name} became unhealthy and moved to fallback")
                        
                except Exception as e:
                    logger.error(f"Health check failed for {server.name}: {e}")
        
        # Ensure we have working sources
        if not self.active_servers:
            await self._activate_fallback_sources()

# Pydantic models for API responses
class MCPServerStatus(BaseModel):
    name: str
    base_url: str
    enabled: bool
    health_status: str
    last_check: Optional[str]

class MCPManagerStatus(BaseModel):
    active_servers: List[MCPServerStatus]
    fallback_servers: List[MCPServerStatus]
    total_servers: int
    active_count: int
    fallback_count: int
    source_types: Dict[str, List[str]]

class MCPNewsItemResponse(BaseModel):
    title: str
    summary: str
    link: str
    published: str
    source: str
    category: str
    sentiment: Optional[str]
    relevance_score: Optional[float]
    mcp_server: str
    metadata: Optional[Dict[str, Any]]

class MCPNewsResponse(BaseModel):
    success: bool
    message: str
    news_count: int
    news_items: List[MCPNewsItemResponse]
    server_status: MCPManagerStatus
    timestamp: str
