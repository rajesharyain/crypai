"""
Categorize Agent for Crypto Financial News
Analyzes news from selected providers to determine crypto relevance and extract data
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CategorizedNewsItem:
    """Categorized news item with crypto analysis"""
    title: str
    summary: str
    link: str
    published: str
    source: str
    category: str
    is_crypto_news: bool
    crypto_relevance_score: float
    crypto_symbols: List[Dict[str, Any]]
    primary_crypto: Optional[Dict[str, Any]]
    news_category: str
    sentiment: str
    key_topics: List[str]
    analysis_timestamp: str
    analysis_method: str

class CategorizeAgent:
    """Agent for categorizing news and determining crypto relevance"""
    
    def __init__(self):
        """Initialize the CategorizeAgent"""
        self.llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.1,
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        
        # Initialize crypto patterns for fallback analysis
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
            'ARB': r'\b(?:arbitrum|arb)\b',
            'PENGU': r'\b(?:pengu|pengu coin)\b',
            'USDT': r'\b(?:tether|usdt)\b',
            'USDC': r'\b(?:usd coin|usdc)\b',
            'BNB': r'\b(?:binance coin|bnb)\b'
        }
        
        # Crypto-related keywords for relevance scoring
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
        
        # Initialize categorization cache
        self.categorization_cache = {
            'categorized_news': [],
            'crypto_news_count': 0,
            'non_crypto_news_count': 0,
            'last_update': None,
            'cache_ttl': 600  # 10 minutes cache TTL
        }
        
        # Create AI prompt template for categorization
        self.categorization_prompt = PromptTemplate(
            input_variables=["news_text"],
            template="""Analyze the following news article and determine if it's related to cryptocurrency/blockchain:

News Article:
{news_text}

Provide your analysis in this exact JSON format:
{{
    "is_crypto_news": true/false,
    "crypto_relevance_score": 0-10,
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
    "news_category": "price analysis|adoption|regulation|technology|defi|nft|general",
    "sentiment": "positive|negative|neutral",
    "key_topics": ["bitcoin", "price", "adoption"],
    "reasoning": "Brief explanation of why this is/isn't crypto news"
}}

Only respond with valid JSON."""
        )
        
        logger.info("✅ CategorizeAgent initialized successfully")
    
    async def categorize_news_item(self, news_item: Dict[str, Any]) -> CategorizedNewsItem:
        """Categorize a single news item using AI analysis"""
        try:
            # Combine title and summary for analysis
            full_text = f"Title: {news_item.get('title', '')}\nSummary: {news_item.get('summary', '')}"
            
            # Use AI for categorization
            if self.llm:
                try:
                    # Create AI prompt
                    prompt = self.categorization_prompt.format(news_text=full_text)
                    
                    # Get AI response
                    response = await self.llm.ainvoke(prompt)
                    
                    # Parse AI response
                    try:
                        ai_analysis = json.loads(response.content)
                        
                        # Create categorized news item
                        categorized_item = CategorizedNewsItem(
                            title=news_item.get('title', ''),
                            summary=news_item.get('summary', ''),
                            link=news_item.get('link', ''),
                            published=news_item.get('published', ''),
                            source=news_item.get('source', ''),
                            category=news_item.get('category', 'general'),
                            is_crypto_news=ai_analysis.get('is_crypto_news', False),
                            crypto_relevance_score=ai_analysis.get('crypto_relevance_score', 0.0),
                            crypto_symbols=ai_analysis.get('crypto_symbols', []),
                            primary_crypto=ai_analysis.get('primary_crypto'),
                            news_category=ai_analysis.get('news_category', 'general'),
                            sentiment=ai_analysis.get('sentiment', 'neutral'),
                            key_topics=ai_analysis.get('key_topics', []),
                            analysis_timestamp=datetime.now(timezone.utc).isoformat(),
                            analysis_method='ai_enhanced'
                        )
                        
                        logger.info(f"✅ AI categorization successful for: {news_item.get('title', '')[:50]}...")
                        return categorized_item
                        
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse AI response for item: {news_item.get('title', '')[:50]}")
                        # Fallback to regex analysis
                        return self._categorize_with_regex_fallback(news_item)
                        
                except Exception as e:
                    logger.warning(f"AI categorization failed for item: {news_item.get('title', '')[:50]}, error: {e}")
                    # Fallback to regex analysis
                    return self._categorize_with_regex_fallback(news_item)
            else:
                # No AI available, use regex fallback
                logger.info("⚠️ OpenAI not available, using regex-based categorization")
                return self._categorize_with_regex_fallback(news_item)
                
        except Exception as e:
            logger.error(f"Error in categorize_news_item: {e}")
            # Return basic categorized item with minimal info
            return CategorizedNewsItem(
                title=news_item.get('title', ''),
                summary=news_item.get('summary', ''),
                link=news_item.get('link', ''),
                published=news_item.get('published', ''),
                source=news_item.get('source', ''),
                category=news_item.get('category', 'general'),
                is_crypto_news=False,
                crypto_relevance_score=0.0,
                crypto_symbols=[],
                primary_crypto=None,
                news_category='general',
                sentiment='neutral',
                key_topics=[],
                analysis_timestamp=datetime.now(timezone.utc).isoformat(),
                analysis_method='error_fallback'
            )
    
    def _categorize_with_regex_fallback(self, news_item: Dict[str, Any]) -> CategorizedNewsItem:
        """Fallback categorization using regex patterns when AI is unavailable"""
        try:
            # Combine title and summary for analysis
            full_text = f"{news_item.get('title', '')} {news_item.get('summary', '')}"
            text_lower = full_text.lower()
            
            # Extract crypto symbols
            crypto_symbols = self._extract_crypto_symbols_regex(text_lower)
            
            # Calculate crypto relevance score
            crypto_relevance_score = self._calculate_relevance_score(text_lower, crypto_symbols)
            
            # Determine if it's crypto news
            is_crypto_news = len(crypto_symbols) > 0 or crypto_relevance_score > 3
            
            # Determine news category based on content
            news_category = self._determine_news_category(text_lower, crypto_symbols)
            
            # Determine sentiment based on keywords
            sentiment = self._determine_sentiment(text_lower)
            
            # Extract key topics
            key_topics = self._extract_key_topics(text_lower)
            
            # Create categorized news item
            categorized_item = CategorizedNewsItem(
                title=news_item.get('title', ''),
                summary=news_item.get('summary', ''),
                link=news_item.get('link', ''),
                published=news_item.get('published', ''),
                source=news_item.get('source', ''),
                category=news_item.get('category', 'general'),
                is_crypto_news=is_crypto_news,
                crypto_relevance_score=crypto_relevance_score,
                crypto_symbols=crypto_symbols,
                primary_crypto=crypto_symbols[0] if crypto_symbols else None,
                news_category=news_category,
                sentiment=sentiment,
                key_topics=key_topics,
                analysis_timestamp=datetime.now(timezone.utc).isoformat(),
                analysis_method='regex_fallback'
            )
            
            logger.info(f"✅ Regex categorization completed for: {news_item.get('title', '')[:50]}...")
            return categorized_item
            
        except Exception as e:
            logger.error(f"Error in regex fallback categorization: {e}")
            # Return minimal categorized item
            return CategorizedNewsItem(
                title=news_item.get('title', ''),
                summary=news_item.get('summary', ''),
                link=news_item.get('link', ''),
                published=news_item.get('published', ''),
                source=news_item.get('source', ''),
                category=news_item.get('category', 'general'),
                is_crypto_news=False,
                crypto_relevance_score=0.0,
                crypto_symbols=[],
                primary_crypto=None,
                news_category='general',
                sentiment='neutral',
                key_topics=[],
                analysis_timestamp=datetime.now(timezone.utc).isoformat(),
                analysis_method='error_fallback'
            )
    
    def _extract_crypto_symbols_regex(self, text: str) -> List[Dict[str, Any]]:
        """Extract cryptocurrency symbols using regex patterns"""
        found_symbols = {}
        
        for symbol, pattern in self.crypto_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                mention_count = len(matches)
                relevance_score = min(mention_count * 2, 10)
                
                # Boost score if crypto keywords are nearby
                if any(keyword in text for keyword in self.crypto_keywords):
                    relevance_score += 2
                
                # Boost score for major cryptocurrencies
                if symbol in ['BTC', 'ETH', 'USDT', 'USDC', 'BNB']:
                    relevance_score += 1
                
                found_symbols[symbol] = {
                    'symbol': symbol,
                    'name': self._get_crypto_name(symbol),
                    'mentions': mention_count,
                    'context': self._extract_context(text, matches[0]),
                    'relevance': min(relevance_score, 10)
                }
        
        # Sort by relevance score (highest first)
        sorted_symbols = sorted(
            found_symbols.values(), 
            key=lambda x: x['relevance'], 
            reverse=True
        )
        
        return sorted_symbols
    
    def _calculate_relevance_score(self, text: str, crypto_symbols: List[Dict[str, Any]]) -> float:
        """Calculate overall crypto relevance score"""
        base_score = sum(symbol['relevance'] for symbol in crypto_symbols)
        
        # Boost score if crypto keywords are present
        crypto_keyword_matches = sum(1 for keyword in self.crypto_keywords if keyword in text)
        keyword_boost = min(crypto_keyword_matches * 0.5, 3)
        
        return min(base_score + keyword_boost, 10)
    
    def _determine_news_category(self, text: str, crypto_symbols: List[Dict[str, Any]]) -> str:
        """Determine the news category based on content"""
        text_lower = text.lower()
        
        # Check for specific categories
        if any(word in text_lower for word in ['price', 'market', 'trading', 'chart']):
            return 'price analysis'
        elif any(word in text_lower for word in ['adoption', 'partnership', 'enterprise', 'institutional']):
            return 'adoption'
        elif any(word in text_lower for word in ['regulation', 'legal', 'compliance', 'sec', 'government']):
            return 'regulation'
        elif any(word in text_lower for word in ['technology', 'upgrade', 'development', 'protocol']):
            return 'technology'
        elif any(word in text_lower for word in ['defi', 'yield', 'liquidity', 'amm', 'dex']):
            return 'defi'
        elif any(word in text_lower for word in ['nft', 'metaverse', 'gaming', 'collectibles']):
            return 'nft'
        elif crypto_symbols:
            return 'crypto general'
        else:
            return 'general'
    
    def _determine_sentiment(self, text: str) -> str:
        """Determine sentiment based on keywords"""
        text_lower = text.lower()
        
        positive_words = ['bullish', 'surge', 'rally', 'gain', 'positive', 'growth', 'adoption', 'partnership']
        negative_words = ['bearish', 'crash', 'drop', 'decline', 'negative', 'risk', 'concern', 'warning']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _extract_key_topics(self, text: str) -> List[str]:
        """Extract key topics from the text"""
        topics = []
        text_lower = text.lower()
        
        # Check for common crypto topics
        topic_keywords = [
            'bitcoin', 'ethereum', 'blockchain', 'defi', 'nft', 'mining', 'staking',
            'exchange', 'wallet', 'smart contract', 'governance', 'dao', 'metaverse'
        ]
        
        for topic in topic_keywords:
            if topic in text_lower:
                topics.append(topic)
        
        return topics[:5]  # Limit to 5 topics
    
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
            'USDC': 'USDC Coin', 'BNB': 'Binance Coin'
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
    
    async def categorize_multiple_news(self, news_items: List[Dict[str, Any]]) -> List[CategorizedNewsItem]:
        """Categorize multiple news items concurrently"""
        try:
            logger.info(f"🔄 Starting categorization of {len(news_items)} news items...")
            
            # Process items concurrently with rate limiting
            semaphore = asyncio.Semaphore(5)  # Limit concurrent AI calls
            
            async def categorize_with_semaphore(item):
                async with semaphore:
                    return await self.categorize_news_item(item)
            
            # Create tasks for all items
            tasks = [categorize_with_semaphore(item) for item in news_items]
            
            # Execute all categorizations concurrently
            categorized_items = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle any exceptions
            valid_items = []
            for i, result in enumerate(categorized_items):
                if isinstance(result, Exception):
                    logger.error(f"Error categorizing item {i}: {result}")
                    # Create basic categorized item for failed items
                    basic_item = CategorizedNewsItem(
                        title=news_items[i].get('title', ''),
                        summary=news_items[i].get('summary', ''),
                        link=news_items[i].get('link', ''),
                        published=news_items[i].get('published', ''),
                        source=news_items[i].get('source', ''),
                        category=news_items[i].get('category', 'general'),
                        is_crypto_news=False,
                        crypto_relevance_score=0.0,
                        crypto_symbols=[],
                        primary_crypto=None,
                        news_category='general',
                        sentiment='neutral',
                        key_topics=[],
                        analysis_timestamp=datetime.now(timezone.utc).isoformat(),
                        analysis_method='error_fallback'
                    )
                    valid_items.append(basic_item)
                else:
                    valid_items.append(result)
            
            # Update cache
            self._update_categorization_cache(valid_items)
            
            logger.info(f"✅ Successfully categorized {len(valid_items)} news items")
            return valid_items
            
        except Exception as e:
            logger.error(f"Error in categorize_multiple_news: {e}")
            return []
    
    def _update_categorization_cache(self, categorized_items: List[CategorizedNewsItem]):
        """Update the categorization cache"""
        self.categorization_cache['categorized_news'] = categorized_items
        self.categorization_cache['crypto_news_count'] = sum(1 for item in categorized_items if item.is_crypto_news)
        self.categorization_cache['non_crypto_news_count'] = sum(1 for item in categorized_items if not item.is_crypto_news)
        self.categorization_cache['last_update'] = datetime.now(timezone.utc)
        
        logger.info(f"📊 Cache updated: {self.categorization_cache['crypto_news_count']} crypto, {self.categorization_cache['non_crypto_news_count']} non-crypto")
    
    def get_categorization_stats(self) -> Dict[str, Any]:
        """Get statistics about categorized news"""
        return {
            'total_news': len(self.categorization_cache['categorized_news']),
            'crypto_news_count': self.categorization_cache['crypto_news_count'],
            'non_crypto_news_count': self.categorization_cache['non_crypto_news_count'],
            'crypto_percentage': (self.categorization_cache['crypto_news_count'] / max(len(self.categorization_cache['categorized_news']), 1)) * 100,
            'last_update': self.categorization_cache['last_update'],
            'cache_ttl': self.categorization_cache['cache_ttl']
        }
    
    def get_crypto_news(self, limit: Optional[int] = None) -> List[CategorizedNewsItem]:
        """Get only crypto-related news from cache"""
        crypto_news = [item for item in self.categorization_cache['categorized_news'] if item.is_crypto_news]
        
        if limit:
            return crypto_news[:limit]
        return crypto_news
    
    def get_news_by_category(self, category: str, limit: Optional[int] = None) -> List[CategorizedNewsItem]:
        """Get news by specific category"""
        category_news = [item for item in self.categorization_cache['categorized_news'] if item.news_category == category]
        
        if limit:
            return category_news[:limit]
        return category_news
    
    def get_news_by_sentiment(self, sentiment: str, limit: Optional[int] = None) -> List[CategorizedNewsItem]:
        """Get news by specific sentiment"""
        sentiment_news = [item for item in self.categorization_cache['categorized_news'] if item.sentiment == sentiment]
        
        if limit:
            return sentiment_news[:limit]
        return sentiment_news
    
    def clear_cache(self):
        """Clear the categorization cache"""
        self.categorization_cache = {
            'categorized_news': [],
            'crypto_news_count': 0,
            'non_crypto_news_count': 0,
            'last_update': None,
            'cache_ttl': 600
        }
        logger.info("🗑️ Categorization cache cleared")
    
    def is_cache_fresh(self) -> bool:
        """Check if the cache is still fresh"""
        if not self.categorization_cache['last_update']:
            return False
        
        cache_age = (datetime.now(timezone.utc) - self.categorization_cache['last_update']).total_seconds()
        return cache_age < self.categorization_cache['cache_ttl']
