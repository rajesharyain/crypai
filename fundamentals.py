"""
Fundamentals Fetcher Agent
Fetches comprehensive cryptocurrency fundamentals via CoinGecko API
Provides current price, market data, rankings, and detailed metrics
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from datetime import datetime, timezone
import httpx
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CryptoFundamentals:
    """Comprehensive cryptocurrency fundamentals data"""
    symbol: str
    name: str
    current_price_usd: Optional[float] = None
    current_price_btc: Optional[float] = None
    current_price_eth: Optional[float] = None
    price_change_24h: Optional[float] = None
    price_change_percentage_24h: Optional[float] = None
    market_cap: Optional[int] = None
    market_cap_rank: Optional[int] = None
    volume_24h: Optional[int] = None
    circulating_supply: Optional[int] = None
    total_supply: Optional[int] = None
    max_supply: Optional[int] = None
    ath: Optional[float] = None
    ath_change_percentage: Optional[float] = None
    ath_date: Optional[str] = None
    atl: Optional[float] = None
    atl_change_percentage: Optional[float] = None
    atl_date: Optional[str] = None
    roi: Optional[Dict[str, Any]] = None
    last_updated: Optional[str] = None
    sparkline_7d: Optional[List[float]] = None
    price_change_percentage_1h: Optional[float] = None
    price_change_percentage_7d: Optional[float] = None
    price_change_percentage_30d: Optional[float] = None
    price_change_percentage_1y: Optional[float] = None
    market_cap_change_24h: Optional[float] = None
    market_cap_change_percentage_24h: Optional[float] = None
    fully_diluted_valuation: Optional[int] = None
    total_volume: Optional[int] = None
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None
    price_change_24h_in_currency: Optional[Dict[str, float]] = None

class FundamentalsFetcherAgent:
    """Agent for fetching cryptocurrency fundamentals from CoinGecko API"""
    
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.session = None
        self.rate_limit_delay = 1.2  # CoinGecko free tier: 50 calls/minute
        self.last_request_time = 0
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Accept": "application/json",
                "User-Agent": "AI-Finance-Assistant/1.0"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.aclose()
    
    async def _rate_limit(self):
        """Implement rate limiting for CoinGecko API"""
        if self.last_request_time > 0:
            elapsed = asyncio.get_event_loop().time() - self.last_request_time
            if elapsed < self.rate_limit_delay:
                await asyncio.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = asyncio.get_event_loop().time()
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make rate-limited request to CoinGecko API"""
        await self._rate_limit()
        
        try:
            url = f"{self.base_url}/{endpoint}"
            response = await self.session.get(url, params=params)
            
            if response.status_code == 200:
                try:
                    json_data = response.json()
                    if json_data is None:
                        logger.warning(f"Empty JSON response from {endpoint}")
                        return {}
                    return json_data
                except Exception as json_error:
                    logger.error(f"Failed to parse JSON from {endpoint}: {json_error}")
                    return {}
            elif response.status_code == 429:
                logger.warning("Rate limit hit, waiting longer...")
                await asyncio.sleep(5)  # Wait longer on rate limit
                return await self._make_request(endpoint, params)
            else:
                logger.error(f"API request failed: {response.status_code} - {response.text}")
                return {}
                
        except Exception as e:
            logger.error(f"Error making request to {endpoint}: {e}")
            return {}
    
    async def search_coin(self, query: str) -> List[Dict[str, Any]]:
        """Search for a coin by name or symbol"""
        try:
            data = await self._make_request("search", {"query": query})
            if data and isinstance(data, dict):
                return data.get("coins", [])
            else:
                logger.warning(f"Invalid response format from search API for {query}")
                return []
        except Exception as e:
            logger.error(f"Error searching for coin {query}: {e}")
            return []
    
    async def get_coin_id(self, symbol: str) -> Optional[str]:
        """Get CoinGecko coin ID from symbol"""
        try:
            # Search for the coin
            search_results = await self.search_coin(symbol.upper())
            
            if search_results:
                # Find exact match by symbol
                for coin in search_results:
                    if coin.get("symbol", "").upper() == symbol.upper():
                        return coin.get("id")
                
                # If no exact match, return first result
                return search_results[0].get("id")
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting coin ID for {symbol}: {e}")
            return None
    
    async def is_valid_symbol(self, symbol: str) -> bool:
        """Check if a symbol is a valid cryptocurrency"""
        try:
            # List of known valid crypto symbols
            valid_symbols = {
                'BTC', 'ETH', 'SUI', 'SOL', 'ADA', 'DOT', 'LINK', 'MATIC', 'AVAX',
                'UNI', 'AAVE', 'COMP', 'MKR', 'YFI', 'CRV', 'BAL', 'SUSHI', '1INCH',
                'CAKE', 'BUNNY', 'ALPHA', 'BETA', 'PERP', 'DYDX', 'GMX', 'SNX',
                'REN', 'KNC', 'BAND', 'OCEAN', 'FET', 'AGIX', 'RLC', 'NMR', 'MLN',
                'ENJ', 'MANA', 'SAND', 'AXS', 'CHZ', 'FLOW', 'THETA', 'FTM', 'NEAR',
                'ALGO', 'ATOM', 'LUNA', 'UST', 'DOGE', 'SHIB', 'PEPE', 'BONK', 'WIF',
                'BOME', 'MYRO', 'POPCAT', 'TURBO', 'BOOK', 'XRP', 'LTC', 'BCH', 'BSV',
                'EOS', 'TRX', 'XLM', 'NEO', 'QTUM', 'ZEC', 'DASH', 'XMR', 'ZEN',
                'RVN', 'ERG', 'KAS', 'NEXA', 'XEC', 'BABYDOGE', 'FLOKI', 'SAFEMOON',
                'HOT', 'VET', 'ICX', 'ONT', 'ZIL', 'IOTA', 'NANO', 'BAN', 'XDC',
                'HBAR', 'ARB', 'PENGU', 'USDT', 'USDC', 'BNB'
            }
            
            # Check if symbol is in our known valid symbols
            if symbol.upper() in valid_symbols:
                return True
            
            # For unknown symbols, we'll assume they're valid and let the API decide
            # This avoids unnecessary API calls that might fail
            return True
            
        except Exception as e:
            logger.error(f"Error validating symbol {symbol}: {e}")
            return False

    async def get_fundamentals(self, symbol: str) -> Optional[CryptoFundamentals]:
        """Get comprehensive fundamentals for a cryptocurrency symbol"""
        try:
            # Get coin ID first
            coin_id = await self.get_coin_id(symbol)
            if not coin_id:
                logger.warning(f"Could not find coin ID for symbol: {symbol}")
                return None
            
            # Fetch detailed coin data
            coin_data = await self._make_request(
                "coins/markets",
                {
                    "ids": coin_id,
                    "vs_currency": "usd",
                    "order": "market_cap_desc",
                    "per_page": 1,
                    "page": 1,
                    "sparkline": True,
                    "price_change_percentage": "1h,24h,7d,30d,1y"
                }
            )
            
            if not coin_data:
                logger.warning(f"No market data found for {symbol}")
                return None
            
            market_data = coin_data[0]
            
            # Fetch additional detailed data
            detailed_data = await self._make_request(f"coins/{coin_id}")
            
            # Create fundamentals object
            fundamentals = CryptoFundamentals(
                symbol=symbol.upper(),
                name=market_data.get("name", symbol),
                current_price_usd=market_data.get("current_price"),
                current_price_btc=market_data.get("current_price_btc"),
                current_price_eth=market_data.get("current_price_eth"),
                price_change_24h=market_data.get("price_change_24h"),
                price_change_percentage_24h=market_data.get("price_change_percentage_24h"),
                market_cap=market_data.get("market_cap"),
                market_cap_rank=market_data.get("market_cap_rank"),
                volume_24h=market_data.get("total_volume"),
                circulating_supply=detailed_data.get("market_data", {}).get("circulating_supply"),
                total_supply=detailed_data.get("market_data", {}).get("total_supply"),
                max_supply=detailed_data.get("market_data", {}).get("max_supply"),
                ath=detailed_data.get("market_data", {}).get("ath", {}).get("usd"),
                ath_change_percentage=detailed_data.get("market_data", {}).get("ath_change_percentage", {}).get("usd"),
                ath_date=detailed_data.get("market_data", {}).get("ath_date", {}).get("usd"),
                atl=detailed_data.get("market_data", {}).get("atl", {}).get("usd"),
                atl_change_percentage=detailed_data.get("market_data", {}).get("atl_change_percentage", {}).get("usd"),
                atl_date=detailed_data.get("market_data", {}).get("atl_date", {}).get("usd"),
                roi=detailed_data.get("market_data", {}).get("roi"),
                last_updated=market_data.get("last_updated"),
                sparkline_7d=market_data.get("sparkline_in_7d", {}).get("price", []),
                price_change_percentage_1h=market_data.get("price_change_percentage_1h_in_currency"),
                price_change_percentage_7d=market_data.get("price_change_percentage_7d_in_currency"),
                price_change_percentage_30d=market_data.get("price_change_percentage_30d_in_currency"),
                price_change_percentage_1y=market_data.get("price_change_percentage_1y_in_currency"),
                market_cap_change_24h=detailed_data.get("market_data", {}).get("market_cap_change_24h"),
                market_cap_change_percentage_24h=detailed_data.get("market_data", {}).get("market_cap_change_percentage_24h"),
                fully_diluted_valuation=detailed_data.get("market_data", {}).get("fully_diluted_valuation", {}).get("usd"),
                total_volume=market_data.get("total_volume"),
                high_24h=detailed_data.get("market_data", {}).get("high_24h", {}).get("usd"),
                low_24h=detailed_data.get("market_data", {}).get("low_24h", {}).get("usd"),
                price_change_24h_in_currency=detailed_data.get("market_data", {}).get("price_change_24h_in_currency")
            )
            
            logger.info(f"Successfully fetched fundamentals for {symbol}")
            return fundamentals
            
        except Exception as e:
            logger.error(f"Error fetching fundamentals for {symbol}: {e}")
            return None
    
    async def get_multiple_fundamentals(self, symbols: List[str]) -> Dict[str, CryptoFundamentals]:
        """Get fundamentals for multiple symbols concurrently"""
        try:
            tasks = [self.get_fundamentals(symbol) for symbol in symbols]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            fundamentals_dict = {}
            for symbol, result in zip(symbols, results):
                if isinstance(result, Exception):
                    logger.error(f"Error fetching {symbol}: {result}")
                    fundamentals_dict[symbol] = None
                else:
                    fundamentals_dict[symbol] = result
            
            return fundamentals_dict
            
        except Exception as e:
            logger.error(f"Error fetching multiple fundamentals: {e}")
            return {}
    
    async def get_trending_coins(self, limit: int = 10) -> List[CryptoFundamentals]:
        """Get trending coins with fundamentals"""
        try:
            trending_data = await self._make_request("search/trending")
            trending_coins = trending_data.get("coins", [])[:limit]
            
            trending_fundamentals = []
            for coin in trending_coins:
                coin_data = coin.get("item", {})
                symbol = coin_data.get("symbol", "").upper()
                
                # Get fundamentals for trending coin
                fundamentals = await self.get_fundamentals(symbol)
                if fundamentals:
                    trending_fundamentals.append(fundamentals)
            
            return trending_fundamentals
            
        except Exception as e:
            logger.error(f"Error fetching trending coins: {e}")
            return []
    
    async def get_market_overview(self) -> Dict[str, Any]:
        """Get overall market overview and statistics"""
        try:
            # Get global market data
            global_data = await self._make_request("global")
            
            # Get top coins by market cap
            top_coins = await self._make_request(
                "coins/markets",
                {
                    "vs_currency": "usd",
                    "order": "market_cap_desc",
                    "per_page": 10,
                    "page": 1
                }
            )
            
            market_overview = {
                "global_market_data": global_data.get("data", {}),
                "top_coins": top_coins,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            return market_overview
            
        except Exception as e:
            logger.error(f"Error fetching market overview: {e}")
            return {}

# Pydantic models for API responses
class FundamentalsResponse(BaseModel):
    """API response model for fundamentals endpoint"""
    success: bool
    message: str
    symbol: str
    fundamentals: Optional[CryptoFundamentals] = None
    timestamp: str

class MultipleFundamentalsResponse(BaseModel):
    """API response model for multiple fundamentals endpoint"""
    success: bool
    message: str
    symbols: List[str]
    fundamentals: Dict[str, Optional[CryptoFundamentals]]
    timestamp: str

class TrendingCoinsResponse(BaseModel):
    """API response model for trending coins endpoint"""
    success: bool
    message: str
    trending_coins: List[CryptoFundamentals]
    count: int
    timestamp: str

class MarketOverviewResponse(BaseModel):
    """API response model for market overview endpoint"""
    success: bool
    message: str
    market_overview: Dict[str, Any]
    timestamp: str

# Utility functions for easy access
async def get_fundamentals(symbol: str) -> Optional[CryptoFundamentals]:
    """Convenience function to get fundamentals for a single symbol"""
    async with FundamentalsFetcherAgent() as agent:
        return await agent.get_fundamentals(symbol)

async def get_multiple_fundamentals(symbols: List[str]) -> Dict[str, CryptoFundamentals]:
    """Convenience function to get fundamentals for multiple symbols"""
    async with FundamentalsFetcherAgent() as agent:
        return await agent.get_multiple_fundamentals(symbols)

async def get_trending_coins(limit: int = 10) -> List[CryptoFundamentals]:
    """Convenience function to get trending coins"""
    async with FundamentalsFetcherAgent() as agent:
        return await agent.get_trending_coins(limit)

async def get_market_overview() -> Dict[str, Any]:
    """Convenience function to get market overview"""
    async with FundamentalsFetcherAgent() as agent:
        return await agent.get_market_overview()
