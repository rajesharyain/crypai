"""
Analyzer Agent for News Analysis
Uses LangChain + OpenAI to analyze news articles for sentiment and fundamental impact
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Import LangChain components
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from langchain.prompts import PromptTemplate

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
    fundamentals: str  # "positive", "negative", or "neutral"
    confidence: float  # 0 to 1
    analysis_timestamp: str

class AnalyzerAgent:
    """AI-powered news analyzer using LangChain + OpenAI"""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.1):
        self.model_name = model_name
        self.temperature = temperature
        self.llm = None
        self._initialize_llm()
        
        # Define the analysis prompt
        self.analysis_prompt = PromptTemplate(
            input_variables=["title", "summary"],
            template="""You are a financial news analyst. Analyze the following crypto/financial news article:

Title: {title}
Summary: {summary}

Please provide a comprehensive analysis in the following JSON format:
{{
    "summary": "Summarize this news in exactly 2 sentences",
    "sentiment": <float between -1.0 and 1.0, where -1.0 is extremely negative, 0 is neutral, and 1.0 is extremely positive>,
    "fundamentals": "positive|negative|neutral",
    "confidence": <float between 0.0 and 1.0 indicating your confidence in the analysis>,
    "reasoning": "Brief explanation of your sentiment and fundamentals assessment"
}}

Focus on:
1. Financial market impact
2. Investor sentiment
3. Fundamental business/economic implications
4. Regulatory or technological significance

Return ONLY valid JSON, no additional text."""
        )
    
    def _initialize_llm(self):
        """Initialize the OpenAI LLM via LangChain"""
        try:
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                logger.warning("OpenAI API key not found. Analyzer will not function properly.")
                return
            
            self.llm = ChatOpenAI(
                model_name=self.model_name,
                temperature=self.temperature,
                openai_api_key=openai_api_key
            )
            logger.info(f"✅ AnalyzerAgent initialized with {self.model_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize AnalyzerAgent: {e}")
            self.llm = None
    
    async def analyze_news(self, title: str, summary: str) -> Optional[AnalysisResult]:
        """Analyze a news article for sentiment and fundamental impact"""
        if not self.llm:
            logger.error("LLM not initialized. Cannot perform analysis.")
            return None
        
        try:
            # Format the prompt with the news content
            formatted_prompt = self.analysis_prompt.format(
                title=title.strip(),
                summary=summary.strip()
            )
            
            # Create the message for LangChain
            message = HumanMessage(content=formatted_prompt)
            
            # Get response from OpenAI
            logger.info(f"🔍 Analyzing news: {title[:50]}...")
            response = await self.llm.ainvoke([message])
            
            # Parse the JSON response
            try:
                analysis_data = json.loads(response.content.strip())
                
                # Validate the response structure
                required_fields = ["summary", "sentiment", "fundamentals", "confidence"]
                if not all(field in analysis_data for field in required_fields):
                    logger.warning("Incomplete analysis response, using fallback")
                    return self._create_fallback_analysis(title, summary)
                
                # Validate sentiment range
                sentiment = float(analysis_data["sentiment"])
                if not -1.0 <= sentiment <= 1.0:
                    sentiment = max(-1.0, min(1.0, sentiment))  # Clamp to valid range
                
                # Validate confidence range
                confidence = float(analysis_data["confidence"])
                if not 0.0 <= confidence <= 1.0:
                    confidence = max(0.0, min(1.0, confidence))  # Clamp to valid range
                
                # Validate fundamentals
                fundamentals = analysis_data["fundamentals"].lower()
                if fundamentals not in ["positive", "negative", "neutral"]:
                    fundamentals = "neutral"
                
                # Create analysis result
                result = AnalysisResult(
                    summary=analysis_data["summary"],
                    sentiment=sentiment,
                    fundamentals=fundamentals,
                    confidence=confidence,
                    analysis_timestamp=asyncio.get_event_loop().time()
                )
                
                logger.info(f"✅ Analysis completed successfully (confidence: {confidence:.2f})")
                return result
                
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON response: {e}")
                logger.debug(f"Raw response: {response.content}")
                return self._create_fallback_analysis(title, summary)
                
        except Exception as e:
            logger.error(f"❌ Error during news analysis: {e}")
            return self._create_fallback_analysis(title, summary)
    
    def _create_fallback_analysis(self, title: str, summary: str) -> AnalysisResult:
        """Create a fallback analysis when AI analysis fails"""
        logger.info("🔄 Using fallback analysis")
        
        # Simple keyword-based fallback analysis
        text = f"{title} {summary}".lower()
        
        # Basic sentiment keywords
        positive_words = ["bullish", "surge", "rally", "gain", "profit", "growth", "adoption", "partnership", "launch"]
        negative_words = ["bearish", "crash", "drop", "loss", "decline", "ban", "hack", "scam", "regulation"]
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        # Calculate basic sentiment
        if positive_count > negative_count:
            sentiment = 0.3
            fundamentals = "positive"
        elif negative_count > positive_count:
            sentiment = -0.3
            fundamentals = "negative"
        else:
            sentiment = 0.0
            fundamentals = "neutral"
        
        # Create fallback summary
        summary_text = f"News about {title.split()[0]} with mixed market implications. Requires further analysis for accurate assessment."
        
        return AnalysisResult(
            summary=summary_text,
            sentiment=sentiment,
            fundamentals=fundamentals,
            confidence=0.3,  # Low confidence for fallback
            analysis_timestamp=asyncio.get_event_loop().time()
        )
    
    async def analyze_multiple_news(self, news_items: list) -> list:
        """Analyze multiple news items concurrently"""
        if not news_items:
            return []
        
        try:
            # Create analysis tasks
            tasks = []
            for item in news_items:
                if isinstance(item, dict):
                    title = item.get("title", "")
                    summary = item.get("summary", "")
                else:
                    title = getattr(item, "title", "")
                    summary = getattr(item, "summary", "")
                
                if title and summary:
                    task = self.analyze_news(title, summary)
                    tasks.append((item, task))
            
            # Execute all analyses concurrently
            results = []
            for item, task in tasks:
                try:
                    analysis_result = await task
                    if analysis_result:
                        results.append({
                            "item": item,
                            "analysis": analysis_result
                        })
                except Exception as e:
                    logger.error(f"Error analyzing item: {e}")
                    continue
            
            logger.info(f"✅ Completed analysis of {len(results)} news items")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error in batch analysis: {e}")
            return []
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get the current status of the analyzer agent"""
        return {
            "model": self.model_name,
            "temperature": self.temperature,
            "llm_initialized": self.llm is not None,
            "openai_key_configured": bool(os.getenv("OPENAI_API_KEY")),
            "status": "ready" if self.llm else "not_initialized"
        }

# Pydantic models for API requests and responses
class NewsAnalysisRequest(BaseModel):
    """Request model for news analysis"""
    title: str
    summary: str

class NewsAnalysisResponse(BaseModel):
    """Response model for news analysis"""
    success: bool
    message: str
    analysis: Optional[Dict[str, Any]] = None
    agent_status: Dict[str, Any]
    timestamp: str

class BatchAnalysisRequest(BaseModel):
    """Request model for batch news analysis"""
    news_items: list

class BatchAnalysisResponse(BaseModel):
    """Response model for batch news analysis"""
    success: bool
    message: str
    analyses: list
    total_analyzed: int
    agent_status: Dict[str, Any]
    timestamp: str

# Utility functions for easy access
async def analyze_single_news(title: str, summary: str) -> Optional[AnalysisResult]:
    """Convenience function to analyze a single news article"""
    agent = AnalyzerAgent()
    return await agent.analyze_news(title, summary)

async def analyze_news_batch(news_items: list) -> list:
    """Convenience function to analyze multiple news articles"""
    agent = AnalyzerAgent()
    return await agent.analyze_multiple_news(news_items)
