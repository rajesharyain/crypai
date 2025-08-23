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
import re

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
    
    def get_source_name(self) -> str:
        return self.source_name

class NewsIngestionAgent:
    """Main news ingestion agent using LangChain"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.1,
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        
        # Create LangChain tools (temporarily disabled for compatibility)
        # self.tools = self._create_tools()
        
        # Create agent (temporarily disabled for compatibility)
        # self.agent = self._create_agent()
        
        # Initialize news cache for enhanced crypto news
        self.news_cache = {
            'enhanced_news': [],
            'crypto_symbols_index': {},
            'last_update': None,
            'cache_ttl': 300  # 5 minutes cache TTL
        }
        
        # Get configuration
        self.config = get_news_config()
        
        # Initialize news sources from configuration
        self.news_sources = self._initialize_news_sources()
        
        # Add crypto symbol extraction patterns
        self.crypto_patterns = {
            'BTC': r'\b(?:bitcoin|btc|₿)\b',
            'ETH': r'\b(?:ethereum|eth|Ξ)\b',
            'SUI': r'\b(?:sui|sui network)\b',
            'SOL': r'\b(?:solana|sol)\b',
            'ADA': r'\b(?:cardano|ada)\b',
            'DOT': r'\b(?:polkadot|dot)\b',
            'LINK': r'\b(?:chainlink|link)\b',
            'MATIC': r'\b(?:polygon|matic)\b',
            'AVAX': r'\b(?:avalanche|avax)\b',
            'UNI': r'\b(?:uniswap|uni)\b',
            'AAVE': r'\b(?:aave)\b',
            'COMP': r'\b(?:compound|comp)\b',
            'MKR': r'\b(?:maker|mkr)\b',
            'YFI': r'\b(?:yearn|yfi)\b',
            'CRV': r'\b(?:curve|crv)\b',
            'BAL': r'\b(?:balancer|bal)\b',
            'SUSHI': r'\b(?:sushiswap|sushi)\b',
            '1INCH': r'\b(?:1inch|1inch network)\b',
            'CAKE': r'\b(?:pancakeswap|cake)\b',
            'BUNNY': r'\b(?:pancake bunny|bunny)\b',
            'ALPHA': r'\b(?:alpha finance|alpha)\b',
            'BETA': r'\b(?:beta finance|beta)\b',
            'PERP': r'\b(?:perpetual protocol|perp)\b',
            'DYDX': r'\b(?:dydx)\b',
            'GMX': r'\b(?:gmx)\b',
            'SNX': r'\b(?:synthetix|snx)\b',
            'REN': r'\b(?:ren|renvm)\b',
            'KNC': r'\b(?:kyber network|knc)\b',
            'BAND': r'\b(?:band protocol|band)\b',
            'OCEAN': r'\b(?:ocean protocol|ocean)\b',
            'FET': r'\b(?:fetch|fetch.ai|fet)\b',
            'AGIX': r'\b(?:singularitynet|agix)\b',
            'RLC': r'\b(?:iexec|rlc)\b',
            'NMR': r'\b(?:numerai|nmr)\b',
            'MLN': r'\b(?:melon|mln)\b',
            'ENJ': r'\b(?:enjin|enj)\b',
            'MANA': r'\b(?:decentraland|mana)\b',
            'SAND': r'\b(?:sandbox|sand)\b',
            'AXS': r'\b(?:axie infinity|axs)\b',
            'CHZ': r'\b(?:chiliz|chz)\b',
            'FLOW': r'\b(?:flow|dapper labs)\b',
            'THETA': r'\b(?:theta|theta network)\b',
            'FTM': r'\b(?:fantom|ftm)\b',
            'NEAR': r'\b(?:near protocol|near)\b',
            'ALGO': r'\b(?:algorand|algo)\b',
            'ATOM': r'\b(?:cosmos|atom)\b',
            'LUNA': r'\b(?:terra|terra luna|luna)\b',
            'UST': r'\b(?:terrausd|ust)\b',
            'DOGE': r'\b(?:dogecoin|doge|🐕)\b',
            'SHIB': r'\b(?:shiba inu|shib|🐕)\b',
            'PEPE': r'\b(?:pepe|pepe coin|🐸)\b',
            'BONK': r'\b(?:bonk|bonk inu)\b',
            'WIF': r'\b(?:dogwifhat|wif|🐕)\b',
            'BOME': r'\b(?:book of meme|bome)\b',
            'MYRO': r'\b(?:myro|myro inu)\b',
            'POPCAT': r'\b(?:popcat|popcat inu)\b',
            'TURBO': r'\b(?:turbo|turbo inu)\b',
            'BOOK': r'\b(?:book|book of meme)\b',
            'XRP': r'\b(?:ripple|xrp)\b',
            'LTC': r'\b(?:litecoin|ltc)\b',
            'BCH': r'\b(?:bitcoin cash|bch)\b',
            'BSV': r'\b(?:bitcoin sv|bsv)\b',
            'EOS': r'\b(?:eos)\b',
            'TRX': r'\b(?:tron|trx)\b',
            'XLM': r'\b(?:stellar|xlm)\b',
            'NEO': r'\b(?:neo)\b',
            'QTUM': r'\b(?:qtum)\b',
            'ZEC': r'\b(?:zcash|zec)\b',
            'DASH': r'\b(?:dash)\b',
            'XMR': r'\b(?:monero|xmr)\b',
            'ZEN': r'\b(?:horizen|zen)\b',
            'RVN': r'\b(?:ravencoin|rvn)\b',
            'ERG': r'\b(?:ergo|erg)\b',
            'KAS': r'\b(?:kaspa|kas)\b',
            'NEXA': r'\b(?:nexa|nexa coin)\b',
            'XEC': r'\b(?:ecash|xec)\b',
            'BABYDOGE': r'\b(?:babydoge|baby doge)\b',
            'FLOKI': r'\b(?:floki|floki inu)\b',
            'SAFEMOON': r'\b(?:safemoon|safe moon)\b',
            'HOT': r'\b(?:holochain|holo|hot)\b',
            'VET': r'\b(?:vechain|vet)\b',
            'ICX': r'\b(?:icon|icx)\b',
            'ONT': r'\b(?:ontology|ont)\b',
            'ZIL': r'\b(?:zilliqa|zil)\b',
            'IOTA': r'\b(?:iota|miota)\b',
            'NANO': r'\b(?:nano|nano coin)\b',
            'BAN': r'\b(?:banano|ban)\b',
            'XDC': r'\b(?:xdc network|xdc)\b',
            'HBAR': r'\b(?:hedera|hbar)\b',
            # Add new patterns from recent news
            'ARB': r'\b(?:arbitrum|arb)\b',
            'PENGU': r'\b(?:pengu|pengu coin)\b',
            'USDT': r'\b(?:tether|usdt)\b',
            'USDC': r'\b(?:usd coin|usdc)\b',
            'BNB': r'\b(?:binance coin|bnb)\b',
            'STABLECOIN': r'\b(?:stablecoin|stable coin)\b',
            'BINANCE': r'\b(?:binance)\b',
            'META': r'\b(?:meta|metaplanet)\b',
            'TRUMP': r'\b(?:trump|american bitcoin)\b'
        }
        
        # Common crypto-related keywords for relevance scoring
        self.crypto_keywords = [
            'cryptocurrency', 'crypto', 'blockchain', 'defi', 'nft', 'web3',
            'smart contract', 'wallet', 'exchange', 'mining', 'staking', 'yield',
            'liquidity', 'governance', 'dao', 'metaverse', 'gamefi', 'play2earn',
            'tokenomics', 'airdrops', 'ico', 'ido', 'launchpad', 'dex', 'amm',
            'lending', 'borrowing', 'flash loans', 'oracles', 'bridges', 'rollups',
            'layer 2', 'sidechains', 'cross-chain', 'interoperability', 'scalability',
            'consensus', 'proof of stake', 'proof of work', 'proof of authority',
            'validator', 'node', 'masternode', 'supernode', 'delegator', 'nominator'
        ]

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
                self._llm = llm
                super().__init__()
            
            @property
            def llm(self):
                return self._llm
            
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
    
    async def fetch_all_news(self, limit: Optional[int] = None) -> List[NewsItem]:
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
            
            # Apply limit if specified
            if limit and limit > 0:
                unique_news = unique_news[:limit]
            
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
                    
                    # Use the agent to analyze (temporarily disabled)
                    # analysis_result = await self.agent.arun(
                    #     f"Analyze this news: {analysis_text}"
                    # )
                    
                    # Parse the analysis result (temporarily disabled)
                    # try:
                    #     analysis_data = json.loads(analysis_result)
                    #     item.sentiment = analysis_data.get("sentiment", "neutral")
                    #     item.relevance_score = analysis_data.get("relevance_score", 5.0)
                    # except json.JSONDecodeError:
                    #     # Fallback if JSON parsing fails
                    #     item.sentiment = "neutral"
                    #     item.relevance_score = 5.0
                    
                    # Temporary fallback
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

    def extract_crypto_symbols(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract cryptocurrency symbols and their relevance from text
        Returns list of dicts with symbol, name, relevance_score, and mentions
        """
        if not text:
            return []
            
        text_lower = text.lower()
        found_symbols = {}
        
        # Check each crypto pattern
        for symbol, pattern in self.crypto_patterns.items():
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            if matches:
                # Calculate relevance score based on mentions and context
                mention_count = len(matches)
                relevance_score = min(mention_count * 2, 10)  # Max 10
                
                # Boost score if mentioned in title or has crypto keywords nearby
                if any(keyword in text_lower for keyword in self.crypto_keywords):
                    relevance_score += 2
                
                # Boost score for major cryptocurrencies
                if symbol in ['BTC', 'ETH', 'USDT', 'USDC', 'BNB']:
                    relevance_score += 1
                
                found_symbols[symbol] = {
                    'symbol': symbol,
                    'name': self._get_crypto_name(symbol),
                    'relevance_score': min(relevance_score, 10),
                    'mentions': mention_count,
                    'context': self._extract_context(text, matches[0])
                }
        
        # Sort by relevance score (highest first)
        sorted_symbols = sorted(
            found_symbols.values(), 
            key=lambda x: x['relevance_score'], 
            reverse=True
        )
        
        return sorted_symbols

    def _get_crypto_name(self, symbol: str) -> str:
        """Get full name for crypto symbol"""
        names = {
            'BTC': 'Bitcoin', 'ETH': 'Ethereum', 'SUI': 'Sui Network',
            'SOL': 'Solana', 'ADA': 'Cardano', 'DOT': 'Polkadot',
            'LINK': 'Chainlink', 'MATIC': 'Polygon', 'AVAX': 'Avalanche',
            'UNI': 'Uniswap', 'AAVE': 'Aave', 'COMP': 'Compound',
            'MKR': 'Maker', 'YFI': 'Yearn Finance', 'CRV': 'Curve',
            'BAL': 'Balancer', 'SUSHI': 'SushiSwap', '1INCH': '1inch Network',
            'CAKE': 'PancakeSwap', 'BUNNY': 'Pancake Bunny', 'ALPHA': 'Alpha Finance',
            'BETA': 'Beta Finance', 'PERP': 'Perpetual Protocol', 'DYDX': 'dYdX',
            'GMX': 'GMX', 'SNX': 'Synthetix', 'REN': 'RenVM', 'KNC': 'Kyber Network',
            'BAND': 'Band Protocol', 'OCEAN': 'Ocean Protocol', 'FET': 'Fetch.ai',
            'AGIX': 'SingularityNET', 'RLC': 'iExec', 'NMR': 'Numerai',
            'MLN': 'Melon', 'ENJ': 'Enjin', 'MANA': 'Decentraland',
            'SAND': 'The Sandbox', 'AXS': 'Axie Infinity', 'CHZ': 'Chiliz',
            'FLOW': 'Flow', 'THETA': 'Theta Network', 'FTM': 'Fantom',
            'NEAR': 'NEAR Protocol', 'ALGO': 'Algorand', 'ATOM': 'Cosmos',
            'LUNA': 'Terra Luna', 'UST': 'TerraUSD', 'DOGE': 'Dogecoin',
            'SHIB': 'Shiba Inu', 'PEPE': 'Pepe Coin', 'BONK': 'Bonk Inu',
            'WIF': 'Dogwifhat', 'BOME': 'Book of Meme', 'MYRO': 'Myro Inu',
            'POPCAT': 'Popcat Inu', 'TURBO': 'Turbo Inu', 'BOOK': 'Book of Meme',
            'XRP': 'Ripple', 'LTC': 'Litecoin', 'BCH': 'Bitcoin Cash',
            'BSV': 'Bitcoin SV', 'EOS': 'EOS', 'TRX': 'TRON',
            'XLM': 'Stellar', 'NEO': 'NEO', 'QTUM': 'Qtum',
            'ZEC': 'Zcash', 'DASH': 'Dash', 'XMR': 'Monero',
            'ZEN': 'Horizen', 'RVN': 'Ravencoin', 'ERG': 'Ergo',
            'KAS': 'Kaspa', 'NEXA': 'Nexa', 'XEC': 'eCash',
            'BABYDOGE': 'Baby Doge', 'FLOKI': 'Floki Inu',
            'SAFEMOON': 'SafeMoon', 'HOT': 'Holo', 'VET': 'VeChain',
            'ICX': 'ICON', 'ONT': 'Ontology', 'ZIL': 'Zilliqa',
            'IOTA': 'IOTA', 'NANO': 'Nano', 'BAN': 'Banano',
            'XDC': 'XDC Network', 'HBAR': 'Hedera',
            'ARB': 'Arbitrum', 'PENGU': 'Pengu Coin', 'USDT': 'Tether',
            'USDC': 'USDC Coin', 'BNB': 'Binance Coin', 'STABLECOIN': 'Stablecoin',
            'BINANCE': 'Binance', 'META': 'Meta', 'TRUMP': 'Trump'
        }
        return names.get(symbol, symbol)

    def _extract_context(self, text: str, match: str) -> str:
        """Extract context around a crypto mention"""
        try:
            start = max(0, text.lower().find(match.lower()) - 50)
            end = min(len(text), text.lower().find(match.lower()) + len(match) + 50)
            context = text[start:end].strip()
            if start > 0:
                context = "..." + context
            if end < len(text):
                context = context + "..."
            return context
        except:
            return match

    async def extract_crypto_symbols_with_ai(self, news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Use LangChain + OpenAI to intelligently extract crypto symbols and categorize news
        """
        if not self.llm:
            logger.warning("⚠️ OpenAI not available, using regex-based extraction")
            return self.analyze_news_with_crypto_context(news_items)
        
        enhanced_items = []
        
        for item in news_items:
            try:
                # Combine title and summary for AI analysis
                full_text = f"Title: {item.get('title', '')}\nSummary: {item.get('summary', '')}"
                
                # Create AI prompt for crypto analysis
                ai_prompt = f"""
                Analyze the following cryptocurrency news article and extract:
                1. All cryptocurrency symbols mentioned (BTC, ETH, XRP, etc.)
                2. The primary cryptocurrency if any
                3. News category (price analysis, adoption, regulation, technology, etc.)
                4. Sentiment (positive, negative, neutral)
                5. Relevance score (1-10, where 10 is highly relevant to crypto markets)

                News Article:
                {full_text}

                Respond in this exact JSON format:
                {{
                    "crypto_symbols": [
                        {{
                            "symbol": "BTC",
                            "name": "Bitcoin",
                            "mentions": 2,
                            "context": "brief context of mention"
                        }}
                    ],
                    "primary_crypto": {{
                        "symbol": "BTC",
                        "name": "Bitcoin",
                        "relevance": 8
                    }},
                    "news_category": "price analysis",
                    "sentiment": "positive",
                    "relevance_score": 8,
                    "is_crypto_news": true,
                    "key_topics": ["bitcoin", "price", "adoption"]
                }}
                """
                
                # Use LangChain to get AI analysis
                from langchain.schema import HumanMessage, SystemMessage
                
                messages = [
                    SystemMessage(content="You are a cryptocurrency news analyst. Extract crypto symbols and categorize news accurately."),
                    HumanMessage(content=ai_prompt)
                ]
                
                response = await self.llm.ainvoke(messages)
                
                # Parse AI response
                try:
                    ai_analysis = json.loads(response.content)
                    
                    # Enhanced news item with AI analysis
                    enhanced_item = {
                        **item,
                        'crypto_symbols': ai_analysis.get('crypto_symbols', []),
                        'primary_crypto': ai_analysis.get('primary_crypto'),
                        'news_category': ai_analysis.get('news_category', 'general'),
                        'sentiment': ai_analysis.get('sentiment', 'neutral'),
                        'crypto_relevance_score': ai_analysis.get('relevance_score', 0),
                        'is_crypto_news': ai_analysis.get('is_crypto_news', False),
                        'key_topics': ai_analysis.get('key_topics', []),
                        'ai_analysis_timestamp': datetime.utcnow().isoformat(),
                        'analysis_method': 'ai_enhanced'
                    }
                    
                    enhanced_items.append(enhanced_item)
                    
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse AI response for item: {item.get('title', '')[:50]}")
                    # Fallback to regex extraction
                    enhanced_item = self._extract_crypto_symbols_fallback(item)
                    enhanced_items.append(enhanced_item)
                    
            except Exception as e:
                logger.error(f"Error in AI crypto extraction: {e}")
                # Fallback to regex extraction
                enhanced_item = self._extract_crypto_symbols_fallback(item)
                enhanced_items.append(enhanced_item)
        
        # Sort by AI relevance score
        enhanced_items.sort(key=lambda x: x.get('crypto_relevance_score', 0), reverse=True)
        
        return enhanced_items

    def _extract_crypto_symbols_fallback(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback method using regex extraction when AI fails"""
        full_text = f"{item.get('title', '')} {item.get('summary', '')}"
        crypto_symbols = self.extract_crypto_symbols(full_text)
        
        return {
            **item,
            'crypto_symbols': crypto_symbols,
            'crypto_relevance_score': sum(symbol['relevance_score'] for symbol in crypto_symbols),
            'is_crypto_news': len(crypto_symbols) > 0,
            'primary_crypto': crypto_symbols[0] if crypto_symbols else None,
            'news_category': 'general',
            'sentiment': 'neutral',
            'key_topics': [],
            'ai_analysis_timestamp': datetime.utcnow().isoformat(),
            'analysis_method': 'regex_fallback'
        }

    def _update_news_cache(self, enhanced_news: List[Dict[str, Any]]):
        """Update the news cache with enhanced crypto news"""
        self.news_cache['enhanced_news'] = enhanced_news
        self.news_cache['last_update'] = datetime.utcnow()
        
        # Build crypto symbols index for quick lookup
        symbols_index = {}
        for item in enhanced_news:
            if item.get('crypto_symbols'):
                for crypto_info in item['crypto_symbols']:
                    symbol = crypto_info['symbol']
                    if symbol not in symbols_index:
                        symbols_index[symbol] = {
                            'name': crypto_info.get('name', symbol),
                            'news_items': [],
                            'total_mentions': 0,
                            'latest_news': []
                        }
                    
                    symbols_index[symbol]['news_items'].append(item)
                    symbols_index[symbol]['total_mentions'] += crypto_info.get('mentions', 1)
                    
                    # Add to latest news (keep only 3)
                    news_summary = {
                        'title': item.get('title', '')[:100],
                        'source': item.get('source', ''),
                        'published': item.get('published', ''),
                        'relevance_score': item.get('crypto_relevance_score', 0),
                        'sentiment': item.get('sentiment', 'neutral')
                    }
                    symbols_index[symbol]['latest_news'].append(news_summary)
                    symbols_index[symbol]['latest_news'] = symbols_index[symbol]['latest_news'][:3]
        
        self.news_cache['crypto_symbols_index'] = symbols_index

    def get_cached_enhanced_news(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get enhanced news from cache if available and fresh"""
        if not self.news_cache['enhanced_news']:
            return []
        
        # Check if cache is still valid
        if self.news_cache['last_update']:
            cache_age = (datetime.utcnow() - self.news_cache['last_update']).total_seconds()
            if cache_age > self.news_cache['cache_ttl']:
                logger.info("Cache expired, will refresh on next fetch")
                return []
        
        return self.news_cache['enhanced_news'][:limit]

    def get_crypto_symbols_from_cache(self) -> Dict[str, Any]:
        """Get all detected crypto symbols from cache"""
        return self.news_cache.get('crypto_symbols_index', {})

    def get_news_by_crypto_symbol(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get news items for a specific crypto symbol from cache"""
        symbols_index = self.news_cache.get('crypto_symbols_index', {})
        if symbol.upper() in symbols_index:
            return symbols_index[symbol.upper()]['news_items'][:limit]
        return []

    async def refresh_news_cache(self, limit: int = 20):
        """Refresh the news cache with fresh enhanced news"""
        try:
            logger.info("🔄 Refreshing news cache...")
            
            # Fetch fresh news
            all_news = await self.fetch_all_news(limit=limit * 2)
            
            # Convert to dict format
            news_dicts = []
            for item in all_news:
                news_dict = {
                    'title': item.title,
                    'summary': item.summary,
                    'link': item.link,
                    'published': item.published.isoformat() if hasattr(item.published, 'isoformat') else str(item.published),
                    'source': item.source,
                    'category': getattr(item, 'category', None),
                    'sentiment': getattr(item, 'sentiment', None)
                }
                news_dicts.append(news_dict)
            
            # Enhance with AI crypto extraction
            enhanced_news = await self.extract_crypto_symbols_with_ai(news_dicts)
            
            # Update cache
            self._update_news_cache(enhanced_news)
            
            logger.info(f"✅ News cache refreshed with {len(enhanced_news)} enhanced items")
            return enhanced_news
            
        except Exception as e:
            logger.error(f"❌ Error refreshing news cache: {e}")
            return []

    def analyze_news_with_crypto_context(self, news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze news items and extract crypto symbols with context
        """
        enhanced_items = []
        
        for item in news_items:
            # Combine title and summary for analysis
            full_text = f"{item.get('title', '')} {item.get('summary', '')}"
            
            # Extract crypto symbols
            crypto_symbols = self.extract_crypto_symbols(full_text)
            
            # Calculate overall crypto relevance
            crypto_relevance = sum(symbol['relevance_score'] for symbol in crypto_symbols)
            
            # Enhanced news item
            enhanced_item = {
                **item,
                'crypto_symbols': crypto_symbols,
                'crypto_relevance_score': crypto_relevance,
                'is_crypto_news': len(crypto_symbols) > 0,
                'primary_crypto': crypto_symbols[0] if crypto_symbols else None,
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
            enhanced_items.append(enhanced_item)
        
        # Sort by crypto relevance (highest first)
        enhanced_items.sort(key=lambda x: x['crypto_relevance_score'], reverse=True)
        
        return enhanced_items

    async def fetch_crypto_focused_news(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch news and focus on crypto-related content with AI enhancement
        """
        try:
            # First check cache for fresh enhanced news
            cached_news = self.get_cached_enhanced_news(limit=limit)
            if cached_news:
                logger.info(f"✅ Using cached enhanced news ({len(cached_news)} items)")
                return cached_news[:limit]
            
            # If no cache or expired, refresh and enhance
            logger.info("🔄 No fresh cache available, fetching and enhancing news...")
            enhanced_news = await self.refresh_news_cache(limit=limit * 2)
            
            if not enhanced_news:
                logger.warning("⚠️ No enhanced news available, falling back to basic extraction")
                # Fallback to basic regex extraction
                all_news = await self.fetch_all_news(limit=limit * 2)
                news_dicts = []
                for item in all_news:
                    news_dict = {
                        'title': item.title,
                        'summary': item.summary,
                        'link': item.link,
                        'published': item.published.isoformat() if hasattr(item.published, 'isoformat') else str(item.published),
                        'source': item.source,
                        'category': getattr(item, 'category', None),
                        'sentiment': getattr(item, 'sentiment', None)
                    }
                    news_dicts.append(news_dict)
                
                enhanced_news = self.analyze_news_with_crypto_context(news_dicts)
            
            # Filter to crypto-relevant news and limit results
            crypto_news = [
                item for item in enhanced_news 
                if item.get('is_crypto_news', False) and item.get('crypto_relevance_score', 0) > 3
            ][:limit]
            
            # If not enough crypto news, include some general crypto news
            if len(crypto_news) < limit:
                general_crypto = [
                    item for item in enhanced_news 
                    if item.get('is_crypto_news', False) and item.get('crypto_relevance_score', 0) <= 3
                ][:limit - len(crypto_news)]
                crypto_news.extend(general_crypto)
            
            # Ensure we have the requested limit
            result = crypto_news[:limit]
            
            logger.info(f"✅ Fetched {len(result)} crypto-focused news items with AI enhancement")
            return result
            
        except Exception as e:
            logger.error(f"Error fetching crypto-focused news: {e}")
            return []

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
