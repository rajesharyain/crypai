"""
Analyzer Agent for News Analysis
Uses LangChain + OpenAI to analyze news articles for sentiment and fundamental impact
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from dotenv import load_dotenv

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, SystemMessage

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AnalysisResult:
    """Result of news analysis"""
    summary: str
    sentiment: float  # -1 to 1
    fundamentals: str  # "positive", "negative", "neutral"
    confidence: float  # 0 to 1
    crypto_impact: Dict[str, Any]  # Crypto-specific analysis
    analysis_timestamp: str
    model_used: str
    processing_time: float

# Pydantic models for API requests
from pydantic import BaseModel

class NewsAnalysisRequest(BaseModel):
    """Request model for news analysis"""
    title: str
    summary: str
    crypto_symbols: Optional[List[Dict[str, Any]]] = None

class NewsAnalysisResponse(BaseModel):
    """Response model for news analysis"""
    success: bool
    analysis: Optional[AnalysisResult] = None
    error: Optional[str] = None

class BatchAnalysisRequest(BaseModel):
    """Request model for batch news analysis"""
    news_items: List[Dict[str, Any]]

class BatchAnalysisResponse(BaseModel):
    """Response model for batch news analysis"""
    success: bool
    analyses: List[AnalysisResult]
    total_processed: int
    errors: List[str] = []

class AnalyzerAgent:
    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.1):
        """Initialize the Analyzer Agent with OpenAI model"""
        self.model_name = model_name
        self.temperature = temperature
        self.llm = None
        self.analysis_prompt = None
        
        # Initialize OpenAI connection
        self._initialize_llm()
        self._create_prompts()
        
        if self.llm:
            logger.info(f"✅ AnalyzerAgent initialized with {model_name}")
        else:
            logger.warning("⚠️ AnalyzerAgent initialized without OpenAI - will use fallback analysis")

    def _initialize_llm(self):
        """Initialize the OpenAI language model"""
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key and api_key.strip():
                self.llm = ChatOpenAI(
                    model_name=self.model_name,
                    temperature=self.temperature,
                    openai_api_key=api_key,
                    max_tokens=1000
                )
                logger.info(f"🔗 Connected to OpenAI {self.model_name}")
            else:
                logger.warning("⚠️ No OpenAI API key found - will use fallback analysis")
                self.llm = None
        except Exception as e:
            logger.error(f"❌ Error initializing OpenAI: {e}")
            self.llm = None

    def _create_prompts(self):
        """Create analysis prompts"""
        # Main analysis prompt for crypto news
        self.analysis_prompt = PromptTemplate(
            input_variables=["title", "summary", "crypto_symbols"],
            template="""
You are a professional cryptocurrency analyst and financial expert. Analyze the following crypto news article and provide a comprehensive analysis.

NEWS ARTICLE:
Title: {title}
Summary: {summary}
Cryptocurrencies Mentioned: {crypto_symbols}

Please provide your analysis in the following JSON format:
{{
    "summary": "A concise 2-3 sentence summary of the news",
    "sentiment": <sentiment_score>, // Number from -1.0 (very negative) to 1.0 (very positive)
    "fundamentals": "positive|negative|neutral", // Overall fundamental impact
    "confidence": <confidence_score>, // Number from 0.0 to 1.0 indicating analysis confidence
    "crypto_impact": {{
        "market_sentiment": "bullish|bearish|neutral",
        "price_impact": "positive|negative|neutral",
        "adoption_impact": "positive|negative|neutral",
        "regulatory_impact": "positive|negative|neutral",
        "technical_impact": "positive|negative|neutral",
        "key_insights": ["insight1", "insight2", "insight3"],
        "risk_factors": ["risk1", "risk2"],
        "opportunities": ["opportunity1", "opportunity2"]
    }},
    "analysis_notes": "Additional professional insights and context"
}}

Focus on:
1. Market sentiment and potential price impact
2. Fundamental analysis of the news
3. Regulatory and adoption implications
4. Technical and infrastructure impacts
5. Risk assessment and opportunities

Be objective, professional, and provide actionable insights for crypto investors and traders.
"""
        )

        # Crypto-specific analysis prompt
        self.crypto_analysis_prompt = PromptTemplate(
            input_variables=["crypto_symbol", "crypto_name", "news_context", "market_data"],
            template="""
You are a cryptocurrency analyst specializing in {crypto_name} ({crypto_symbol}). 

NEWS CONTEXT:
{news_context}

MARKET DATA:
{market_data}

Provide a detailed analysis of how this news affects {crypto_symbol} specifically:

{{
    "crypto_specific_analysis": {{
        "symbol": "{crypto_symbol}",
        "name": "{crypto_name}",
        "news_impact": "positive|negative|neutral",
        "price_outlook": "bullish|bearish|sideways",
        "short_term_impact": "high|medium|low",
        "long_term_impact": "high|medium|low",
        "key_drivers": ["driver1", "driver2", "driver3"],
        "technical_levels": {{
            "support": "key support levels",
            "resistance": "key resistance levels",
            "trend": "current trend analysis"
        }},
        "investment_recommendation": "buy|sell|hold|accumulate",
        "risk_level": "low|medium|high",
        "time_horizon": "immediate|short-term|long-term"
    }}
}}
"""
        )

    async def analyze_news(self, title: str, summary: str, crypto_symbols: List[Dict] = None) -> Optional[AnalysisResult]:
        """
        Analyze news using OpenAI GPT-3.5-turbo
        """
        start_time = datetime.now()
        
        try:
            if not self.llm:
                logger.warning("🔄 OpenAI not available, using fallback analysis")
                return self._create_fallback_analysis(title, summary, crypto_symbols)

            # Prepare crypto symbols string
            crypto_info = "None"
            if crypto_symbols:
                crypto_info = ", ".join([f"{s['symbol']} ({s['name']})" for s in crypto_symbols])

            # Create the prompt
            prompt = self.analysis_prompt.format(
                title=title,
                summary=summary,
                crypto_symbols=crypto_info
            )

            logger.info(f"🔍 Analyzing news: {title[:50]}...")

            # Get response from OpenAI
            messages = [
                SystemMessage(content="You are a professional cryptocurrency analyst. Always respond with valid JSON."),
                HumanMessage(content=prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            response_text = response.content

            # Parse JSON response
            try:
                analysis_data = json.loads(response_text)
                
                # Validate required fields
                required_fields = ['summary', 'sentiment', 'fundamentals', 'confidence', 'crypto_impact']
                if not all(field in analysis_data for field in required_fields):
                    raise ValueError("Missing required fields in analysis response")

                # Create analysis result
                result = AnalysisResult(
                    summary=analysis_data['summary'],
                    sentiment=float(analysis_data['sentiment']),
                    fundamentals=analysis_data['fundamentals'],
                    confidence=float(analysis_data['confidence']),
                    crypto_impact=analysis_data['crypto_impact'],
                    analysis_timestamp=datetime.utcnow().isoformat(),
                    model_used=self.model_name,
                    processing_time=(datetime.now() - start_time).total_seconds()
                )

                logger.info(f"✅ Analysis completed: {result.fundamentals} sentiment, confidence: {result.confidence:.2f}")
                return result

            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse JSON response: {e}")
                logger.error(f"Raw response: {response_text}")
                return self._create_fallback_analysis(title, summary, crypto_symbols)

        except Exception as e:
            logger.error(f"❌ Error during news analysis: {e}")
            return self._create_fallback_analysis(title, summary, crypto_symbols)

    async def analyze_crypto_specific_news(self, news_item: Dict[str, Any], market_data: Dict[str, Any] = None) -> Optional[AnalysisResult]:
        """
        Analyze news with specific focus on mentioned cryptocurrencies
        """
        try:
            # Get primary crypto symbol
            primary_crypto = news_item.get('primary_crypto')
            if not primary_crypto:
                return await self.analyze_news(
                    news_item.get('title', ''),
                    news_item.get('summary', ''),
                    news_item.get('crypto_symbols', [])
                )

            # Create crypto-specific context
            crypto_context = f"Title: {news_item.get('title', '')}\nSummary: {news_item.get('summary', '')}\nCrypto Symbols: {[s['symbol'] for s in news_item.get('crypto_symbols', [])]}"
            
            # Format market data
            market_info = "No market data available"
            if market_data:
                market_info = f"Price: ${market_data.get('current_price', 'N/A')}, 24h Change: {market_data.get('price_change_24h', 'N/A')}%, Market Cap Rank: #{market_data.get('market_cap_rank', 'N/A')}"

            # Create crypto-specific prompt
            prompt = self.crypto_analysis_prompt.format(
                crypto_symbol=primary_crypto['symbol'],
                crypto_name=primary_crypto['name'],
                news_context=crypto_context,
                market_data=market_info
            )

            if not self.llm:
                return self._create_fallback_analysis(
                    news_item.get('title', ''),
                    news_item.get('summary', ''),
                    news_item.get('crypto_symbols', [])
                )

            # Get response from OpenAI
            messages = [
                SystemMessage(content="You are a cryptocurrency analyst. Always respond with valid JSON."),
                HumanMessage(content=prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            response_text = response.content

            # Parse and enhance the analysis
            try:
                crypto_analysis = json.loads(response_text)
                
                # Create enhanced analysis result
                result = AnalysisResult(
                    summary=f"Analysis of {primary_crypto['symbol']} news: {crypto_analysis.get('crypto_specific_analysis', {}).get('news_impact', 'neutral')} impact detected",
                    sentiment=self._map_impact_to_sentiment(crypto_analysis.get('crypto_specific_analysis', {}).get('news_impact', 'neutral')),
                    fundamentals=crypto_analysis.get('crypto_specific_analysis', {}).get('news_impact', 'neutral'),
                    confidence=0.8,  # High confidence for crypto-specific analysis
                    crypto_impact={
                        **crypto_analysis.get('crypto_specific_analysis', {}),
                        'primary_crypto': primary_crypto
                    },
                    analysis_timestamp=datetime.utcnow().isoformat(),
                    model_used=self.model_name,
                    processing_time=0.0
                )

                logger.info(f"✅ Crypto-specific analysis completed for {primary_crypto['symbol']}")
                return result

            except json.JSONDecodeError:
                return await self.analyze_news(
                    news_item.get('title', ''),
                    news_item.get('summary', ''),
                    news_item.get('crypto_symbols', [])
                )

        except Exception as e:
            logger.error(f"❌ Error in crypto-specific analysis: {e}")
            return await self.analyze_news(
                news_item.get('title', ''),
                news_item.get('summary', ''),
                news_item.get('crypto_symbols', [])
            )

    def _map_impact_to_sentiment(self, impact: str) -> float:
        """Map impact string to sentiment score"""
        mapping = {
            'positive': 0.7,
            'negative': -0.7,
            'neutral': 0.0,
            'bullish': 0.8,
            'bearish': -0.8,
            'sideways': 0.0
        }
        return mapping.get(impact.lower(), 0.0)

    def _create_fallback_analysis(self, title: str, summary: str, crypto_symbols: List[Dict] = None) -> AnalysisResult:
        """
        Create fallback analysis when OpenAI is not available
        """
        logger.info("🔄 Using fallback analysis")
        
        # Simple keyword-based sentiment analysis
        text_lower = f"{title} {summary}".lower()
        
        # Sentiment keywords
        positive_words = ['bullish', 'surge', 'rally', 'gain', 'up', 'positive', 'growth', 'adoption', 'partnership', 'launch', 'upgrade']
        negative_words = ['bearish', 'crash', 'drop', 'down', 'negative', 'decline', 'hack', 'exploit', 'ban', 'regulation', 'sell-off']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = 0.3
            fundamentals = "positive"
        elif negative_count > positive_count:
            sentiment = -0.3
            fundamentals = "negative"
        else:
            sentiment = 0.0
            fundamentals = "neutral"

        # Extract crypto symbols for context
        crypto_context = []
        if crypto_symbols:
            for symbol_info in crypto_symbols:
                crypto_context.append({
                    'symbol': symbol_info['symbol'],
                    'name': symbol_info['name'],
                    'relevance': symbol_info['relevance_score']
                })

        return AnalysisResult(
            summary=f"News analysis: {title[:50]}...",
            sentiment=sentiment,
            fundamentals=fundamentals,
            confidence=0.3,  # Low confidence for fallback
            crypto_impact={
                'market_sentiment': 'neutral',
                'price_impact': fundamentals,
                'crypto_symbols': crypto_context,
                'fallback_analysis': True
            },
            analysis_timestamp=datetime.utcnow().isoformat(),
            model_used="fallback_keyword_analysis",
            processing_time=0.0
        )

    async def analyze_multiple_news(self, news_items: List[Dict[str, Any]]) -> List[AnalysisResult]:
        """
        Analyze multiple news items concurrently
        """
        logger.info(f"🔍 Starting batch analysis of {len(news_items)} news items")
        
        results = []
        for i, news_item in enumerate(news_items):
            try:
                # Use crypto-specific analysis if available
                if news_item.get('crypto_symbols'):
                    result = await self.analyze_crypto_specific_news(news_item)
                else:
                    result = await self.analyze_news(
                        news_item.get('title', ''),
                        news_item.get('summary', ''),
                        news_item.get('crypto_symbols', [])
                    )
                
                if result:
                    results.append(result)
                    logger.info(f"✅ Completed analysis {i+1}/{len(news_items)}")
                
            except Exception as e:
                logger.error(f"❌ Error analyzing news item {i+1}: {e}")
                # Create fallback result
                fallback = self._create_fallback_analysis(
                    news_item.get('title', ''),
                    news_item.get('summary', ''),
                    news_item.get('crypto_symbols', [])
                )
                results.append(fallback)

        logger.info(f"✅ Completed analysis of {len(results)} news items")
        return results

    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "model": self.model_name,
            "temperature": self.temperature,
            "llm_initialized": self.llm is not None,
            "openai_key_configured": bool(os.getenv('OPENAI_API_KEY')),
            "status": "ready" if self.llm else "fallback_mode"
        }
