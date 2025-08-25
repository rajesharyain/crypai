#!/usr/bin/env python3
"""
News Impact Analysis Orchestrator

This orchestrator manages the workflow:
1. Fetch news and store in fetched_news_cache
2. Analyze news impact using NewsImpactAnalysisAgent
3. Return structured JSON for human decision making
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

from news_impact_analysis import NewsImpactAnalysisAgent, NewsImpactAnalysis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class NewsImpactWorkflowResult:
    """Result of the news impact analysis workflow"""
    workflow_id: str
    workflow_status: str
    execution_time: float
    timestamp: str
    
    # Workflow data
    fetched_news_count: int
    analyzed_news_count: int
    fetched_news_cache: List[Dict[str, Any]]
    impact_analyses: List[Dict[str, Any]]
    
    # Summary statistics
    sentiment_summary: Dict[str, int]
    impact_summary: Dict[str, int]
    risk_summary: Dict[str, int]
    
    # Trading insights
    trading_insights: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

class NewsImpactOrchestrator:
    """Orchestrator for news impact analysis workflow"""
    
    def __init__(self, news_agent, impact_analysis_agent):
        """Initialize the orchestrator with required agents"""
        self.news_agent = news_agent
        self.impact_analysis_agent = impact_analysis_agent
        
        # Workflow state
        self.workflow_history = []
        self.current_workflow_id = None
        
        logger.info("🚀 NewsImpactOrchestrator initialized successfully")
    
    async def run_news_impact_workflow(self, 
                                     sources: List[str] = None,
                                     news_limit: int = 10,
                                     crypto_focus: bool = True) -> NewsImpactWorkflowResult:
        """Run the complete news impact analysis workflow"""
        start_time = datetime.now()
        workflow_id = f"news_impact_{int(start_time.timestamp())}"
        self.current_workflow_id = workflow_id
        
        logger.info(f"🚀 Starting News Impact Workflow: {workflow_id}")
        
        try:
            # Step 1: Fetch news and store in fetched_news_cache
            logger.info("📰 Step 1: Fetching news and storing in fetched_news_cache")
            fetched_news = await self._fetch_and_cache_news(sources, news_limit, crypto_focus)
            
            # Step 2: Analyze news impact
            logger.info("🔍 Step 2: Analyzing news impact")
            impact_analyses = await self._analyze_news_impact(fetched_news)
            
            # Step 3: Generate workflow result
            logger.info("📊 Step 3: Generating workflow result")
            result = await self._generate_workflow_result(
                workflow_id, start_time, fetched_news, impact_analyses
            )
            
            # Store workflow in history
            self.workflow_history.append(result)
            
            logger.info(f"✅ News Impact Workflow completed successfully: {workflow_id}")
            return result
            
        except Exception as e:
            logger.error(f"❌ News Impact Workflow failed: {e}")
            # Return error result
            return await self._create_error_result(workflow_id, start_time, str(e))
    
    async def _fetch_and_cache_news(self, 
                                   sources: List[str] = None,
                                   news_limit: int = 10,
                                   crypto_focus: bool = True) -> List[Dict[str, Any]]:
        """Fetch news and store in the fetched_news_cache"""
        try:
            if sources:
                # Fetch from specific sources
                news_items = await self.news_agent.fetch_news_from_sources(sources, limit=news_limit)
            elif crypto_focus:
                # Fetch crypto-focused news
                news_items = await self.news_agent.fetch_crypto_focused_news(limit=news_limit)
            else:
                # Fetch general news
                news_items = await self.news_agent.fetch_news(limit=news_limit)
            
            # Store in the impact analysis agent's fetched_news_cache
            self.impact_analysis_agent.add_fetched_news(news_items)
            
            logger.info(f"📰 Fetched and cached {len(news_items)} news items")
            return news_items
            
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            raise
    
    async def _analyze_news_impact(self, news_items: List[Dict[str, Any]]) -> List[NewsImpactAnalysis]:
        """Analyze the impact of fetched news items"""
        try:
            # Use the impact analysis agent to analyze the news
            impact_analyses = await self.impact_analysis_agent.analyze_multiple_news_impact(news_items)
            
            logger.info(f"🔍 Completed impact analysis for {len(impact_analyses)} news items")
            return impact_analyses
            
        except Exception as e:
            logger.error(f"Error analyzing news impact: {e}")
            raise
    
    async def _generate_workflow_result(self, 
                                      workflow_id: str,
                                      start_time: datetime,
                                      fetched_news: List[Dict[str, Any]],
                                      impact_analyses: List[NewsImpactAnalysis]) -> NewsImpactWorkflowResult:
        """Generate the complete workflow result"""
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # Convert analyses to dictionaries
        analyses_dicts = [analysis.to_dict() for analysis in impact_analyses]
        
        # Generate summary statistics
        sentiment_summary = self._generate_sentiment_summary(impact_analyses)
        impact_summary = self._generate_impact_summary(impact_analyses)
        risk_summary = self._generate_risk_summary(impact_analyses)
        
        # Generate trading insights
        trading_insights = self._generate_trading_insights(impact_analyses)
        
        return NewsImpactWorkflowResult(
            workflow_id=workflow_id,
            workflow_status="completed",
            execution_time=execution_time,
            timestamp=end_time.isoformat(),
            
            fetched_news_count=len(fetched_news),
            analyzed_news_count=len(impact_analyses),
            fetched_news_cache=fetched_news,
            impact_analyses=analyses_dicts,
            
            sentiment_summary=sentiment_summary,
            impact_summary=impact_summary,
            risk_summary=risk_summary,
            
            trading_insights=trading_insights
        )
    
    def _generate_sentiment_summary(self, analyses: List[NewsImpactAnalysis]) -> Dict[str, int]:
        """Generate summary of sentiment distribution"""
        summary = {}
        for analysis in analyses:
            sentiment = analysis.sentiment
            summary[sentiment] = summary.get(sentiment, 0) + 1
        return summary
    
    def _generate_impact_summary(self, analyses: List[NewsImpactAnalysis]) -> Dict[str, int]:
        """Generate summary of market impact distribution"""
        summary = {}
        for analysis in analyses:
            impact = analysis.market_impact
            summary[impact] = summary.get(impact, 0) + 1
        return summary
    
    def _generate_risk_summary(self, analyses: List[NewsImpactAnalysis]) -> Dict[str, int]:
        """Generate summary of risk level distribution"""
        summary = {}
        for analysis in analyses:
            risk = analysis.risk_level
            summary[risk] = summary.get(risk, 0) + 1
        return summary
    
    def _generate_trading_insights(self, analyses: List[NewsImpactAnalysis]) -> Dict[str, Any]:
        """Generate actionable trading insights from analyses"""
        if not analyses:
            return {"message": "No analyses available"}
        
        # Count trading recommendations
        recommendations = {}
        position_sizes = {}
        affected_cryptos = set()
        affected_sectors = set()
        
        for analysis in analyses:
            # Count recommendations
            rec = analysis.trading_recommendation
            recommendations[rec] = recommendations.get(rec, 0) + 1
            
            # Count position sizes
            pos = analysis.position_sizing
            position_sizes[pos] = position_sizes.get(pos, 0) + 1
            
            # Collect affected cryptos and sectors
            for crypto in analysis.affected_cryptos:
                affected_cryptos.add(crypto.get('symbol', 'Unknown'))
            
            affected_sectors.update(analysis.affected_sectors)
        
        # Find high-impact news
        high_impact_news = [
            {
                "title": analysis.title,
                "sentiment": analysis.sentiment,
                "market_impact": analysis.market_impact,
                "trading_recommendation": analysis.trading_recommendation,
                "confidence_score": analysis.confidence_score
            }
            for analysis in analyses
            if analysis.market_impact == "High" and analysis.confidence_score > 0.7
        ]
        
        # Sort by confidence score
        high_impact_news.sort(key=lambda x: x['confidence_score'], reverse=True)
        
        return {
            "trading_recommendations": recommendations,
            "position_sizing_distribution": position_sizes,
            "affected_cryptos": list(affected_cryptos),
            "affected_sectors": list(affected_sectors),
            "high_impact_news": high_impact_news[:5],  # Top 5
            "total_analyses": len(analyses),
            "insights_generated": datetime.now().isoformat()
        }
    
    async def _create_error_result(self, workflow_id: str, start_time: datetime, error_message: str) -> NewsImpactWorkflowResult:
        """Create an error result when workflow fails"""
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        return NewsImpactWorkflowResult(
            workflow_id=workflow_id,
            workflow_status="failed",
            execution_time=execution_time,
            timestamp=end_time.isoformat(),
            
            fetched_news_count=0,
            analyzed_news_count=0,
            fetched_news_cache=[],
            impact_analyses=[],
            
            sentiment_summary={},
            impact_summary={},
            risk_summary={},
            
            trading_insights={"error": error_message}
        )
    
    def get_workflow_history(self) -> List[NewsImpactWorkflowResult]:
        """Get the history of all workflows"""
        return self.workflow_history
    
    def get_current_workflow_id(self) -> Optional[str]:
        """Get the current workflow ID"""
        return self.current_workflow_id
    
    def clear_workflow_history(self) -> None:
        """Clear the workflow history"""
        self.workflow_history.clear()
        logger.info("Cleared workflow history")
    
    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get the current status of the orchestrator"""
        return {
            "total_workflows": len(self.workflow_history),
            "current_workflow_id": self.current_workflow_id,
            "last_workflow": self.workflow_history[-1].timestamp if self.workflow_history else None,
            "impact_analysis_agent_status": self.impact_analysis_agent.get_agent_status(),
            "news_agent_status": getattr(self.news_agent, 'get_agent_status', lambda: {})()
        }
