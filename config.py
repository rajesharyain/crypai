"""
Configuration file for news sources and system settings
Makes it easy to add new news providers and customize the system
"""

import os
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class RSSSourceConfig:
    """Configuration for RSS news sources"""
    url: str
    name: str
    category: str
    enabled: bool = True
    max_items: int = 20
    update_interval: int = 300  # seconds

@dataclass
class APISourceConfig:
    """Configuration for API news sources"""
    url: str
    name: str
    api_key_env: str
    headers: Dict[str, str] = None
    enabled: bool = True
    max_items: int = 20
    update_interval: int = 300  # seconds

class NewsConfig:
    """Central configuration for news sources"""
    
    def __init__(self):
        self.rss_sources = self._get_rss_sources()
        self.api_sources = self._get_api_sources()
        self.settings = self._get_settings()
    
    def _get_rss_sources(self) -> List[RSSSourceConfig]:
        """Get configured RSS sources"""
        return [
            RSSSourceConfig(
                url="https://www.coindesk.com/arc/outboundfeeds/rss/",
                name="CoinDesk",
                category="crypto",
                enabled=True,
                max_items=20
            ),
            RSSSourceConfig(
                url="https://cointelegraph.com/rss",
                name="CoinTelegraph",
                category="crypto",
                enabled=True,
                max_items=20
            ),
            RSSSourceConfig(
                url="https://cryptonews.com/news/feed/",
                name="CryptoNews",
                category="crypto",
                enabled=True,
                max_items=20
            ),
            RSSSourceConfig(
                url="https://bitcoinmagazine.com/.rss/full/",
                name="Bitcoin Magazine",
                category="crypto",
                enabled=True,
                max_items=20
            ),
            RSSSourceConfig(
                url="https://decrypt.co/feed",
                name="Decrypt",
                category="crypto",
                enabled=True,
                max_items=20
            ),
            # Add more RSS sources here
            RSSSourceConfig(
                url="https://www.newsbtc.com/feed/",
                name="NewsBTC",
                category="crypto",
                enabled=True,
                max_items=15
            ),
            RSSSourceConfig(
                url="https://ambcrypto.com/feed/",
                name="AMBCrypto",
                category="crypto",
                enabled=True,
                max_items=15
            )
        ]
    
    def _get_api_sources(self) -> List[APISourceConfig]:
        """Get configured API sources"""
        api_sources = []
        
        # Crypto News API
        if os.getenv("CRYPTO_NEWS_API_KEY"):
            api_sources.append(APISourceConfig(
                url="https://cryptonews-api.com/api/v1/news",
                name="Crypto News API",
                api_key_env="CRYPTO_NEWS_API_KEY",
                headers={"Accept": "application/json"},
                enabled=True
            ))
        
        # Token Metrics API
        if os.getenv("TOKEN_METRICS_API_KEY"):
            api_sources.append(APISourceConfig(
                url="https://api.tokenmetrics.com/v1/news",
                name="Token Metrics API",
                api_key_env="TOKEN_METRICS_API_KEY",
                headers={"Accept": "application/json"},
                enabled=True
            ))
        
        # CoinFeeds API
        if os.getenv("COINFEEDS_API_KEY"):
            api_sources.append(APISourceConfig(
                url="https://api.coinfeeds.io/v1/news",
                name="CoinFeeds API",
                api_key_env="COINFEEDS_API_KEY",
                headers={"Accept": "application/json"},
                enabled=True
            ))
        
        # Add more API sources here as they become available
        # Example for future integration:
        # if os.getenv("NEWS_API_KEY"):
        #     api_sources.append(APISourceConfig(
        #         url="https://api.newssource.com/v1/news",
        #         name="New News Source",
        #         api_key_env="NEWS_API_KEY",
        #         headers={"Accept": "application/json"},
        #         enabled=True
        #     ))
        
        return api_sources
    
    def _get_settings(self) -> Dict[str, Any]:
        """Get system settings"""
        return {
            "max_concurrent_fetches": 10,
            "request_timeout": 30,
            "retry_attempts": 3,
            "retry_delay": 5,
            "duplicate_similarity_threshold": 0.8,
            "sentiment_analysis_batch_size": 10,
            "rate_limit_delay": 0.1,  # seconds between API calls
            "cache_duration": 300,  # seconds
            "max_news_items_per_source": 50,
            "enable_sentiment_analysis": True,
            "enable_duplicate_removal": True,
            "enable_source_health_check": True
        }
    
    def get_enabled_rss_sources(self) -> List[RSSSourceConfig]:
        """Get only enabled RSS sources"""
        return [source for source in self.rss_sources if source.enabled]
    
    def get_enabled_api_sources(self) -> List[APISourceConfig]:
        """Get only enabled API sources"""
        return [source for source in self.api_sources if source.enabled]
    
    def add_rss_source(self, url: str, name: str, category: str = "crypto", 
                      max_items: int = 20, enabled: bool = True):
        """Add a new RSS source dynamically"""
        new_source = RSSSourceConfig(
            url=url,
            name=name,
            category=category,
            enabled=enabled,
            max_items=max_items
        )
        self.rss_sources.append(new_source)
        return new_source
    
    def add_api_source(self, url: str, name: str, api_key_env: str,
                      headers: Dict[str, str] = None, enabled: bool = True):
        """Add a new API source dynamically"""
        new_source = APISourceConfig(
            url=url,
            name=name,
            api_key_env=api_key_env,
            headers=headers,
            enabled=enabled
        )
        self.api_sources.append(new_source)
        return new_source
    
    def get_source_by_name(self, name: str) -> RSSSourceConfig | APISourceConfig | None:
        """Get a source configuration by name"""
        for source in self.rss_sources + self.api_sources:
            if source.name == name:
                return source
        return None
    
    def update_source_config(self, name: str, **kwargs):
        """Update source configuration"""
        source = self.get_source_by_name(name)
        if source:
            for key, value in kwargs.items():
                if hasattr(source, key):
                    setattr(source, key, value)
            return True
        return False
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of the current configuration"""
        return {
            "total_sources": len(self.rss_sources) + len(self.api_sources),
            "rss_sources": {
                "total": len(self.rss_sources),
                "enabled": len(self.get_enabled_rss_sources()),
                "names": [s.name for s in self.rss_sources]
            },
            "api_sources": {
                "total": len(self.api_sources),
                "enabled": len(self.get_enabled_api_sources()),
                "names": [s.name for s in self.api_sources]
            },
            "settings": self.settings
        }

# Global configuration instance
news_config = NewsConfig()

def get_news_config() -> NewsConfig:
    """Get the global news configuration instance"""
    return news_config
