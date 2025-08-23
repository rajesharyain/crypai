"""
News Ingestion Agent for Crypto Financial News
Fetches and normalizes news from multiple sources using LangChain agents
"""

import asyncio
import feedparser
import requests
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
import logging
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
from langchain.schema import AgentAction, AgentFinish
from langchain_openai import ChatOpenAI
from langchain.prompts import StringPromptTemplate
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv

# Import configuration
from config import get_news_config

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class NewsItem:
    """Standardized news item structure"""
    title: str
    summary: str
    link: str
    published: str
    source: str
    category: Optional[str] = None
    sentiment: Optional[str] = None
    relevance_score: Optional[float] = None

class NewsSource(ABC):
    """Abstract base class for news sources"""
    
    @abstractmethod
    async def fetch_news(self) -> List[NewsItem]:
        """Fetch news from the source"""
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        """Get the name of the news source"""
        pass

class RSSNewsSource(NewsSource):
    """RSS feed news source"""
    
    def __init__(self, feed_url: str, source_name: str, category: str = "crypto", max_items: int = 20):
        self.feed_url = feed_url
        self.source_name = source_name
        self.category = category
        self.max_items = max_items
    
    async def fetch_news(self) -> List[NewsItem]:
        """Fetch news from RSS feed"""
        try:
            # Use feedparser to parse RSS
            feed = feedparser.parse(self.feed_url)
            news_items = []
            
            for entry in feed.entries[:self.max_items]:
                try:
                    # Normalize the data
                    title = getattr(entry, 'title', 'No Title')
                    summary = getattr(entry, 'summary', getattr(entry, 'description', 'No Summary'))
                    
                    # Clean HTML tags from summary
                    if summary:
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(summary, 'html.parser')
                        summary = soup.get_text()[:300]  # Limit summary length
                    
                    link = getattr(entry, 'link', '')
                    published = getattr(entry, 'published', '')
                    
                    # Parse and standardize date
                    if published:
                        try:
                            # Try to parse various date formats
                            parsed_date = feedparser._parse_date(published)
                            if parsed_date:
                                published = parsed_date.strftime("%Y-%m-%d %H:%M:%S UTC")
                        except:
                            published = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                    else:
                        published = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                    
                    news_item = NewsItem(
                        title=title,
                        summary=summary,
                        link=link,
                        published=published,
                        source=self.source_name,
                        category=self.category
                    )
                    news_items.append(news_item)
                    
                except Exception as e:
                    logger.warning(f"Error processing RSS entry from {self.source_name}: {e}")
                    continue
            
            logger.info(f"Successfully fetched {len(news_items)} news items from {self.source_name}")
            return news_items
            
        except Exception as e:
            logger.error(f"Error fetching RSS from {self.source_name}: {e}")
            return []
    
    def get_source_name(self) -> str:
        return self.source_name

class APINewsSource(NewsSource):
    """API-based news source"""
    
    def __init__(self, api_url: str, api_key: str, source_name: str, headers: Dict = None, max_items: int = 20):
        self.api_url = api_url
        self.api_key = api_key
        self.source_name = source_name
        self.headers = headers or {}
        self.max_items = max_items
        if api_key:
            self.headers['Authorization'] = f'Bearer {api_key}'
    
    async def fetch_news(self) -> List[NewsItem]:
        """Fetch news from API"""
        try:
            response = requests.get(
                self.api_url,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            news_items = []
            
            # Handle different API response structures
            articles = data.get('articles', data.get('data', data.get('results', [])))
            
            for article in articles[:self.max_items]:
                try:
                    title = article.get('title', 'No Title')
                    summary = article.get('summary', article.get('description', 'No Summary'))
                    link = article.get('link', article.get('url', ''))
                    published = article.get('published', article.get('date', ''))
                    
                    # Standardize date format
                    if published:
                        try:
                            # Try to parse various date formats
                            if isinstance(published, str):
                                # Handle ISO format
                                parsed_date = datetime.fromisoformat(published.replace('Z', '+00:00'))
                                published = parsed_date.strftime("%Y-%m-%d %H:%M:%S UTC")
                        except:
                            published = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                    else:
                        published = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                    
                    news_item = NewsItem(
                        title=title,
                        summary=summary,
                        link=link,
                        published=published,
                        source=self.source_name
                    )
                    news_items.append(news_item)
                    
                except Exception as e:
                    logger.warning(f"Error processing API article from {self.source_name}: {e}")
                    continue
            
            logger.info(f"Successfully fetched {len(news_items)} news items from {self.source_name}")
            return news_items
            
        except Exception as e:
            logger.error(f"Error fetching API from {self.source_name}: {e}")
            return []

class NewsIngestionAgent:
    """Main news ingestion agent using LangChain"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.1,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Get configuration
        self.config = get_news_config()
        
        # Initialize news sources from configuration
        self.news_sources = self._initialize_news_sources()
        
        # Create LangChain tools
        self.tools = self._create_tools()
        
        # Create agent
        self.agent = self._create_agent()
    
    def _initialize_news_sources(self) -> List[NewsSource]:
        """Initialize all news sources from configuration"""
        sources = []
        
        # Add RSS sources from configuration
        for rss_config in self.config.get_enabled_rss_sources():
            source = RSSNewsSource(
                feed_url=rss_config.url,
                source_name=rss_config.name,
                category=rss_config.category,
                max_items=rss_config.max_items
            )
            sources.append(source)
        
        # Add API sources from configuration
        for api_config in self.config.get_enabled_api_sources():
            api_key = os.getenv(api_config.api_key_env)
            if api_key:
                source = APINewsSource(
                    api_url=api_config.url,
                    api_key=api_key,
                    source_name=api_config.name,
                    headers=api_config.headers,
                    max_items=api_config.max_items
                )
                sources.append(source)
        
        logger.info(f"Initialized {len(sources)} news sources from configuration")
        return sources
    
    def _create_tools(self) -> List[BaseTool]:
        """Create LangChain tools for news processing"""
        
        class NewsAnalysisTool(BaseTool):
            name = "news_analysis"
            description = "Analyze news sentiment and relevance for financial markets"
            
            def __init__(self, llm):
                super().__init__()
                self.llm = llm
            
            def _run(self, news_text: str) -> str:
                """Analyze news sentiment and relevance"""
                try:
                    # Use LangChain LLM for analysis
                    prompt = f"""
                    Analyze the following crypto news for sentiment and financial relevance:
                    
                    {news_text}
                    
                    Provide a brief analysis including:
                    1. Sentiment (Positive/Negative/Neutral)
                    2. Financial relevance score (0-10)
                    3. Key entities mentioned
                    4. Potential market impact
                    
                    Format as JSON:
                    {{
                        "sentiment": "sentiment",
                        "relevance_score": score,
                        "entities": ["entity1", "entity2"],
                        "market_impact": "description"
                    }}
                    """
                    
                    response = self.llm.invoke(prompt)
                    return response.content
                    
                except Exception as e:
                    logger.error(f"Error in news analysis: {e}")
                    return json.dumps({
                        "sentiment": "neutral",
                        "relevance_score": 5.0,
                        "entities": [],
                        "market_impact": "Unable to analyze"
                    })
            
            async def _arun(self, news_text: str) -> str:
                return self._run(news_text)
        
        return [NewsAnalysisTool(self.llm)]
    
    def _create_agent(self) -> AgentExecutor:
        """Create the LangChain agent"""
        
        class NewsPromptTemplate(StringPromptTemplate):
            template = """You are a financial news ingestion agent. Your task is to:
            1. Fetch news from multiple sources
            2. Normalize and clean the data
            3. Analyze sentiment and relevance
            4. Return structured news items
            
            Available tools: {tools}
            
            Current task: {input}
            
            Think through this step by step:
            1. What news sources should I check?
            2. How should I process the data?
            3. What analysis should I perform?
            
            {agent_scratchpad}"""
            
            def format(self, **kwargs) -> str:
                return self.template.format(**kwargs)
        
        prompt = NewsPromptTemplate(
            input_variables=["tools", "input", "agent_scratchpad"],
            tools=self.tools
        )
        
        agent = LLMSingleActionAgent(
            llm_chain=self.llm,
            output_parser=None,
            stop=["\nObservation:"],
            allowed_tools=[tool.name for tool in self.tools]
        )
        
        return AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=self.tools,
            verbose=True
        )
    
    async def fetch_all_news(self) -> List[NewsItem]:
        """Fetch news from all sources concurrently"""
        try:
            # Get configuration settings
            max_concurrent = self.config.settings["max_concurrent_fetches"]
            timeout = self.config.settings["request_timeout"]
            
            # Fetch from all sources with concurrency limit
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def fetch_with_semaphore(source):
                async with semaphore:
                    return await source.fetch_news()
            
            tasks = [fetch_with_semaphore(source) for source in self.news_sources]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            all_news = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error fetching from source {i}: {result}")
                else:
                    all_news.extend(result)
            
            # Remove duplicates if enabled
            if self.config.settings["enable_duplicate_removal"]:
                unique_news = self._remove_duplicates(all_news)
            else:
                unique_news = all_news
            
            # Sort by published date (newest first)
            unique_news.sort(key=lambda x: x.published, reverse=True)
            
            logger.info(f"Successfully fetched {len(unique_news)} unique news items")
            return unique_news
            
        except Exception as e:
            logger.error(f"Error in fetch_all_news: {e}")
            return []
    
    def _remove_duplicates(self, news_items: List[NewsItem]) -> List[NewsItem]:
        """Remove duplicate news items based on title similarity"""
        threshold = self.config.settings["duplicate_similarity_threshold"]
        unique_items = []
        seen_titles = set()
        
        for item in news_items:
            # Normalize title for comparison
            normalized_title = item.title.lower().strip()
            
            # Check if similar title already exists
            is_duplicate = False
            for seen_title in seen_titles:
                if self._similarity_score(normalized_title, seen_title) > threshold:
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
    
    async def analyze_news_sentiment(self, news_items: List[NewsItem]) -> List[NewsItem]:
        """Analyze sentiment for news items using LangChain"""
        if not self.config.settings["enable_sentiment_analysis"]:
            return news_items
            
        try:
            batch_size = self.config.settings["sentiment_analysis_batch_size"]
            rate_limit_delay = self.config.settings["rate_limit_delay"]
            
            for item in news_items[:batch_size]:
                try:
                    # Create analysis text
                    analysis_text = f"Title: {item.title}\nSummary: {item.summary}"
                    
                    # Use the agent to analyze
                    analysis_result = await self.agent.arun(
                        f"Analyze this news: {analysis_text}"
                    )
                    
                    # Parse the analysis result
                    try:
                        analysis_data = json.loads(analysis_result)
                        item.sentiment = analysis_data.get("sentiment", "neutral")
                        item.relevance_score = analysis_data.get("relevance_score", 5.0)
                    except json.JSONDecodeError:
                        # Fallback if JSON parsing fails
                        item.sentiment = "neutral"
                        item.relevance_score = 5.0
                    
                except Exception as e:
                    logger.warning(f"Error analyzing sentiment for item: {e}")
                    item.sentiment = "neutral"
                    item.relevance_score = 5.0
                
                # Add delay to avoid rate limits
                await asyncio.sleep(rate_limit_delay)
            
            logger.info("Completed sentiment analysis for news items")
            return news_items
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return news_items
    
    def add_news_source(self, source: NewsSource):
        """Add a new news source dynamically"""
        self.news_sources.append(source)
        logger.info(f"Added new news source: {source.get_source_name()}")
    
    def get_source_statistics(self) -> Dict[str, Any]:
        """Get statistics about news sources"""
        stats = {
            "total_sources": len(self.news_sources),
            "rss_sources": len([s for s in self.news_sources if isinstance(s, RSSNewsSource)]),
            "api_sources": len([s for s in self.news_sources if isinstance(s, APINewsSource)]),
            "source_names": [s.get_source_name() for s in self.news_sources],
            "configuration": self.config.get_config_summary()
        }
        return stats

# Pydantic models for API responses
class NewsItemResponse(BaseModel):
    title: str
    summary: str
    link: str
    published: str
    source: str
    category: Optional[str] = None
    sentiment: Optional[str] = None
    relevance_score: Optional[float] = None

class NewsFetchResponse(BaseModel):
    success: bool
    message: str
    news_count: int
    news_items: List[NewsItemResponse]
    source_stats: Dict[str, Any]
    timestamp: str

class SourceStatsResponse(BaseModel):
    success: bool
    message: str
    statistics: Dict[str, Any]
