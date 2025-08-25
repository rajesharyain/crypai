#!/usr/bin/env python3
"""
News Impact Analysis Agent

This agent analyzes cryptocurrency news to determine:
- Market impact and sentiment
- Affected assets and trading implications
- Risk assessment and recommendations
- Expected price movements and volatility
"""

import os
import json
import logging
import httpx
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class NewsImpactAnalysis:
    """Data structure for news impact analysis results"""
    news_id: str
    title: str
    source: str
    published_date: str
    analysis_timestamp: str
    
    # Impact Analysis
    market_impact: str  # "High", "Medium", "Low"
    sentiment: str      # "Bullish", "Bearish", "Neutral"
    confidence_score: float  # 0.0 to 1.0
    
    # Affected Assets
    affected_cryptos: List[Dict[str, Any]]
    affected_sectors: List[str]
    
    # Trading Implications
    expected_price_movement: str  # "Up", "Down", "Sideways"
    volatility_impact: str       # "High", "Medium", "Low"
    time_horizon: str            # "Immediate", "Short-term", "Long-term"
    
    # Risk Assessment
    risk_level: str              # "High", "Medium", "Low"
    risk_factors: List[str]
    
    # Recommendations
    trading_recommendation: str
    position_sizing: str         # "Large", "Medium", "Small"
    stop_loss_considerations: str
    
    # Additional Context
    key_topics: List[str]
    market_context: str
    related_events: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

class NewsImpactAnalysisAgent:
    """Agent for analyzing news impact on cryptocurrency markets"""
    
    def __init__(self, model_type: str = "deepseek"):
        """Initialize the News Impact Analysis Agent"""
        self.model_type = model_type.lower()
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.deepseek_base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        
        # Initialize caches
        self.fetched_news_cache = []
        self.analysis_cache = {}
        
        # Validation
        if self.model_type == "deepseek" and not self.deepseek_api_key:
            logger.warning("DeepSeek API key not found. Falling back to OpenAI.")
            self.model_type = "openai"
        
        logger.info(f"🚀 NewsImpactAnalysisAgent initialized with {self.model_type} model")
    
    def add_fetched_news(self, news_items: List[Dict[str, Any]]) -> None:
        """Add fetched news to the cache for processing"""
        self.fetched_news_cache.extend(news_items)
        logger.info(f"Added {len(news_items)} news items to fetched_news_cache")
    
    def get_fetched_news_cache(self) -> List[Dict[str, Any]]:
        """Get the current fetched news cache"""
        return self.fetched_news_cache
    
    def clear_fetched_news_cache(self) -> None:
        """Clear the fetched news cache"""
        self.fetched_news_cache.clear()
        logger.info("Cleared fetched_news_cache")
    
    async def analyze_news_impact(self, news_item: Dict[str, Any]) -> NewsImpactAnalysis:
        """Analyze the impact of a single news item"""
        try:
            if self.model_type == "deepseek":
                return await self._analyze_with_deepseek(news_item)
            else:
                return await self._analyze_with_openai(news_item)
        except Exception as e:
            logger.error(f"Error analyzing news impact: {e}")
            return self._create_fallback_analysis(news_item)
    
    async def analyze_multiple_news_impact(self, news_items: Optional[List[Dict[str, Any]]] = None) -> List[NewsImpactAnalysis]:
        """Analyze impact of multiple news items"""
        if news_items is None:
            news_items = self.fetched_news_cache
        
        if not news_items:
            logger.warning("No news items to analyze")
            return []
        
        logger.info(f"Analyzing impact of {len(news_items)} news items")
        
        analysis_results = []
        for news_item in news_items:
            try:
                analysis = await self.analyze_news_impact(news_item)
                analysis_results.append(analysis)
                
                # Cache the analysis
                self.analysis_cache[news_item.get('title', 'unknown')] = analysis
                
            except Exception as e:
                logger.error(f"Error analyzing news item '{news_item.get('title', 'unknown')}': {e}")
                # Create fallback analysis
                fallback = self._create_fallback_analysis(news_item)
                analysis_results.append(fallback)
        
        logger.info(f"Completed impact analysis for {len(analysis_results)} news items")
        return analysis_results
    
    async def _analyze_with_deepseek(self, news_item: Dict[str, Any]) -> NewsImpactAnalysis:
        """Analyze news impact using DeepSeek AI"""
        try:
            # Prepare the prompt for DeepSeek
            prompt = self._create_analysis_prompt(news_item)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.deepseek_base_url}/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.deepseek_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are an expert cryptocurrency market analyst. Analyze news for market impact, sentiment, and trading implications. Return only valid JSON."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.3,
                        "max_tokens": 2000
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content']
                    
                    # Parse the JSON response
                    analysis_data = self._parse_deepseek_response(content)
                    return self._create_analysis_from_data(news_item, analysis_data)
                else:
                    logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                    raise Exception(f"DeepSeek API error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error in DeepSeek analysis: {e}")
            raise
    
    async def _analyze_with_openai(self, news_item: Dict[str, Any]) -> NewsImpactAnalysis:
        """Analyze news impact using OpenAI (fallback)"""
        # This would be implemented if OpenAI is available
        # For now, return fallback analysis
        logger.info("OpenAI analysis not implemented, using fallback")
        return self._create_fallback_analysis(news_item)
    
    def _create_analysis_prompt(self, news_item: Dict[str, Any]) -> str:
        """Create a detailed prompt for the AI model"""
        title = news_item.get('title', '')
        summary = news_item.get('summary', '')
        source = news_item.get('source', '')
        published = news_item.get('published', '')
        
        prompt = f"""
Analyze this cryptocurrency news for market impact and trading implications:

Title: {title}
Summary: {summary}
Source: {source}
Published: {published}

Provide analysis in the following JSON format:
{{
    "market_impact": "High/Medium/Low",
    "sentiment": "Bullish/Bearish/Neutral",
    "confidence_score": 0.0-1.0,
    "affected_cryptos": [
        {{
            "symbol": "BTC",
            "name": "Bitcoin",
            "impact_level": "High/Medium/Low",
            "expected_movement": "Up/Down/Sideways"
        }}
    ],
    "affected_sectors": ["DeFi", "Layer2", "NFTs"],
    "expected_price_movement": "Up/Down/Sideways",
    "volatility_impact": "High/Medium/Low",
    "time_horizon": "Immediate/Short-term/Long-term",
    "risk_level": "High/Medium/Low",
    "risk_factors": ["Regulatory uncertainty", "Market volatility"],
    "trading_recommendation": "Buy/Sell/Hold/Wait",
    "position_sizing": "Large/Medium/Small",
    "stop_loss_considerations": "Set tight stops due to high volatility",
    "key_topics": ["Regulation", "ETF approval", "Institutional adoption"],
    "market_context": "Current market conditions and how this news fits",
    "related_events": ["Upcoming SEC decisions", "Fed meetings"]
}}

Return only the JSON, no additional text.
"""
        return prompt
    
    def _parse_deepseek_response(self, content: str) -> Dict[str, Any]:
        """Parse the response from DeepSeek AI"""
        try:
            # Clean the content to extract JSON
            content = content.strip()
            
            # Find JSON content
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            
            content = content.strip()
            
            # Parse JSON
            analysis_data = json.loads(content)
            return analysis_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse DeepSeek response as JSON: {e}")
            logger.error(f"Raw response: {content}")
            
            # Try to extract JSON using regex or other methods
            return self._extract_json_from_text(content)
        except Exception as e:
            logger.error(f"Error parsing DeepSeek response: {e}")
            raise
    
    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """Extract JSON from text when direct parsing fails"""
        try:
            # Look for JSON-like structures
            import re
            
            # Find content between curly braces
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            matches = re.findall(json_pattern, text)
            
            if matches:
                # Try to parse the longest match
                longest_match = max(matches, key=len)
                return json.loads(longest_match)
            
            # If no JSON found, create a basic structure
            return self._create_basic_analysis_structure()
            
        except Exception as e:
            logger.error(f"Failed to extract JSON: {e}")
            return self._create_basic_analysis_structure()
    
    def _create_basic_analysis_structure(self) -> Dict[str, Any]:
        """Create a basic analysis structure when parsing fails"""
        return {
            "market_impact": "Medium",
            "sentiment": "Neutral",
            "confidence_score": 0.5,
            "affected_cryptos": [],
            "affected_sectors": [],
            "expected_price_movement": "Sideways",
            "volatility_impact": "Medium",
            "time_horizon": "Short-term",
            "risk_level": "Medium",
            "risk_factors": ["Analysis failed"],
            "trading_recommendation": "Wait",
            "position_sizing": "Small",
            "stop_loss_considerations": "Standard stops recommended",
            "key_topics": [],
            "market_context": "Analysis unavailable",
            "related_events": []
        }
    
    def _create_analysis_from_data(self, news_item: Dict[str, Any], analysis_data: Dict[str, Any]) -> NewsImpactAnalysis:
        """Create NewsImpactAnalysis object from parsed data"""
        return NewsImpactAnalysis(
            news_id=news_item.get('title', '')[:50],  # Use first 50 chars of title as ID
            title=news_item.get('title', ''),
            source=news_item.get('source', ''),
            published_date=news_item.get('published', ''),
            analysis_timestamp=datetime.now().isoformat(),
            
            market_impact=analysis_data.get('market_impact', 'Medium'),
            sentiment=analysis_data.get('sentiment', 'Neutral'),
            confidence_score=float(analysis_data.get('confidence_score', 0.5)),
            
            affected_cryptos=analysis_data.get('affected_cryptos', []),
            affected_sectors=analysis_data.get('affected_sectors', []),
            
            expected_price_movement=analysis_data.get('expected_price_movement', 'Sideways'),
            volatility_impact=analysis_data.get('volatility_impact', 'Medium'),
            time_horizon=analysis_data.get('time_horizon', 'Short-term'),
            
            risk_level=analysis_data.get('risk_level', 'Medium'),
            risk_factors=analysis_data.get('risk_factors', []),
            
            trading_recommendation=analysis_data.get('trading_recommendation', 'Wait'),
            position_sizing=analysis_data.get('position_sizing', 'Small'),
            stop_loss_considerations=analysis_data.get('stop_loss_considerations', ''),
            
            key_topics=analysis_data.get('key_topics', []),
            market_context=analysis_data.get('market_context', ''),
            related_events=analysis_data.get('related_events', [])
        )
    
    def _create_fallback_analysis(self, news_item: Dict[str, Any]) -> NewsImpactAnalysis:
        """Create a fallback analysis when AI analysis fails"""
        return NewsImpactAnalysis(
            news_id=news_item.get('title', '')[:50],
            title=news_item.get('title', ''),
            source=news_item.get('source', ''),
            published_date=news_item.get('published', ''),
            analysis_timestamp=datetime.now().isoformat(),
            
            market_impact="Medium",
            sentiment="Neutral",
            confidence_score=0.3,
            
            affected_cryptos=[],
            affected_sectors=[],
            
            expected_price_movement="Sideways",
            volatility_impact="Medium",
            time_horizon="Short-term",
            
            risk_level="Medium",
            risk_factors=["Analysis unavailable"],
            
            trading_recommendation="Wait",
            position_sizing="Small",
            stop_loss_considerations="Standard stops recommended",
            
            key_topics=[],
            market_context="Fallback analysis - AI analysis failed",
            related_events=[]
        )
    
    def get_analysis_cache(self) -> Dict[str, NewsImpactAnalysis]:
        """Get the current analysis cache"""
        return self.analysis_cache
    
    def clear_analysis_cache(self) -> None:
        """Clear the analysis cache"""
        self.analysis_cache.clear()
        logger.info("Cleared analysis_cache")
    
    def get_analysis_stats(self) -> Dict[str, Any]:
        """Get statistics about the analysis cache"""
        if not self.analysis_cache:
            return {
                "total_analyses": 0,
                "sentiment_distribution": {},
                "impact_distribution": {},
                "risk_distribution": {}
            }
        
        total = len(self.analysis_cache)
        sentiments = {}
        impacts = {}
        risks = {}
        
        for analysis in self.analysis_cache.values():
            # Count sentiments
            sentiment = analysis.sentiment
            sentiments[sentiment] = sentiments.get(sentiment, 0) + 1
            
            # Count impacts
            impact = analysis.market_impact
            impacts[impact] = impacts.get(impact, 0) + 1
            
            # Count risks
            risk = analysis.risk_level
            risks[risk] = risks.get(risk, 0) + 1
        
        return {
            "total_analyses": total,
            "sentiment_distribution": sentiments,
            "impact_distribution": impacts,
            "risk_distribution": risks,
            "cache_size": len(self.fetched_news_cache)
        }
    
    def switch_model(self, model_type: str) -> bool:
        """Switch between different AI models"""
        if model_type.lower() in ["deepseek", "openai"]:
            self.model_type = model_type.lower()
            logger.info(f"Switched to {model_type} model")
            return True
        else:
            logger.error(f"Invalid model type: {model_type}")
            return False
    
    def get_current_model(self) -> str:
        """Get the current AI model being used"""
        return self.model_type
    
    def get_available_models(self) -> List[str]:
        """Get available AI models"""
        models = ["deepseek"]
        
        # Check if OpenAI is available
        if os.getenv("OPENAI_API_KEY"):
            models.append("openai")
        
        return models
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get the current status of the agent"""
        return {
            "model_type": self.model_type,
            "fetched_news_cache_size": len(self.fetched_news_cache),
            "analysis_cache_size": len(self.analysis_cache),
            "last_analysis": datetime.now().isoformat(),
            "available_models": self.get_available_models()
        }
