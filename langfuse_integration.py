"""
Langfuse Integration for AI Finance Assistant
Tracks AI operations, news ingestion, and pipeline executions
"""

import os
import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from contextlib import contextmanager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from langfuse import Langfuse
    from langfuse.model import CreateTrace, CreateSpan, CreateGeneration, CreateScore
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    logger.warning("Langfuse not available. Install with: pip install langfuse")

class LangfuseTracker:
    """Track AI operations and pipeline executions with Langfuse"""
    
    def __init__(self):
        if not LANGFUSE_AVAILABLE:
            self.client = None
            self.enabled = False
            logger.warning("Langfuse tracking disabled - package not available")
            return
        
        # Initialize Langfuse client
        try:
            self.client = Langfuse(
                public_key=os.getenv('LANGFUSE_PUBLIC_KEY'),
                secret_key=os.getenv('LANGFUSE_SECRET_KEY'),
                host=os.getenv('LANGFUSE_HOST', 'https://cloud.langfuse.com'),
                project_id=os.getenv('LANGFUSE_PROJECT_ID')
            )
            self.enabled = True
            logger.info("✅ Langfuse client initialized successfully")
        except Exception as e:
            self.client = None
            self.enabled = False
            logger.error(f"❌ Failed to initialize Langfuse: {e}")
    
    def is_enabled(self) -> bool:
        """Check if Langfuse tracking is enabled"""
        return self.enabled and self.client is not None
    
    def create_trace(self, name: str, metadata: Dict[str, Any] = None) -> Optional[str]:
        """Create a new trace and return trace ID"""
        if not self.is_enabled():
            return None
        
        try:
            trace_data = CreateTrace(
                name=name,
                metadata=metadata or {},
                tags=["ai-finance-assistant", "news-pipeline"]
            )
            trace = self.client.trace(trace_data)
            logger.debug(f"Created Langfuse trace: {trace.id}")
            return trace.id
        except Exception as e:
            logger.error(f"Error creating Langfuse trace: {e}")
            return None
    
    def create_span(self, trace_id: str, name: str, metadata: Dict[str, Any] = None) -> Optional[str]:
        """Create a span within a trace"""
        if not self.is_enabled() or not trace_id:
            return None
        
        try:
            span_data = CreateSpan(
                name=name,
                trace_id=trace_id,
                metadata=metadata or {},
                tags=["ai-finance-assistant"]
            )
            span = self.client.span(span_data)
            logger.debug(f"Created Langfuse span: {span.id}")
            return span.id
        except Exception as e:
            logger.error(f"Error creating Langfuse span: {e}")
            return None
    
    def create_generation(self, trace_id: str, name: str, model: str, input_data: Any, 
                         output_data: Any, metadata: Dict[str, Any] = None) -> Optional[str]:
        """Create a generation record for AI operations"""
        if not self.is_enabled() or not trace_id:
            return None
        
        try:
            generation_data = CreateGeneration(
                name=name,
                trace_id=trace_id,
                model=model,
                model_parameters={
                    "temperature": 0.1,
                    "max_tokens": 1000
                },
                input=input_data,
                output=output_data,
                metadata=metadata or {},
                tags=["ai-finance-assistant", "ai-operation"]
            )
            generation = self.client.generation(generation_data)
            logger.debug(f"Created Langfuse generation: {generation.id}")
            return generation.id
        except Exception as e:
            logger.error(f"Error creating Langfuse generation: {e}")
            return None
    
    def create_score(self, trace_id: str, name: str, value: float, 
                    comment: str = "", metadata: Dict[str, Any] = None) -> Optional[str]:
        """Create a score for evaluating operations"""
        if not self.is_enabled() or not trace_id:
            return None
        
        try:
            score_data = CreateScore(
                name=name,
                trace_id=trace_id,
                value=value,
                comment=comment,
                metadata=metadata or {},
                tags=["ai-finance-assistant", "evaluation"]
            )
            score = self.client.score(score_data)
            logger.debug(f"Created Langfuse score: {score.id}")
            return score.id
        except Exception as e:
            logger.error(f"Error creating Langfuse score: {e}")
            return None
    
    def update_trace(self, trace_id: str, metadata: Dict[str, Any] = None, 
                    tags: List[str] = None) -> bool:
        """Update an existing trace"""
        if not self.is_enabled() or not trace_id:
            return False
        
        try:
            self.client.update_trace(
                id=trace_id,
                metadata=metadata,
                tags=tags
            )
            return True
        except Exception as e:
            logger.error(f"Error updating Langfuse trace: {e}")
            return False
    
    def flush(self):
        """Flush pending data to Langfuse"""
        if not self.is_enabled():
            return
        
        try:
            self.client.flush()
            logger.debug("Flushed data to Langfuse")
        except Exception as e:
            logger.error(f"Error flushing to Langfuse: {e}")

class NewsIngestionTracker:
    """Track news ingestion operations with Langfuse"""
    
    def __init__(self, langfuse_tracker: LangfuseTracker):
        self.tracker = langfuse_tracker
    
    @contextmanager
    def track_news_fetch(self, source_name: str, source_type: str, expected_items: int = 0):
        """Track news fetching operation"""
        trace_id = None
        start_time = time.time()
        
        try:
            # Create trace for news fetch
            trace_id = self.tracker.create_trace(
                name=f"news_fetch_{source_name}",
                metadata={
                    "source_name": source_name,
                    "source_type": source_type,
                    "expected_items": expected_items,
                    "operation": "news_fetch"
                }
            )
            
            yield trace_id
            
        except Exception as e:
            # Record error
            if trace_id:
                self.tracker.create_score(
                    trace_id=trace_id,
                    name="fetch_success",
                    value=0.0,
                    comment=f"Fetch failed: {str(e)}",
                    metadata={"error": str(e), "error_type": "fetch_error"}
                )
            raise
        finally:
            # Record completion metrics
            if trace_id:
                duration = time.time() - start_time
                self.tracker.create_score(
                    trace_id=trace_id,
                    name="fetch_duration",
                    value=duration,
                    comment=f"Fetch completed in {duration:.2f}s",
                    metadata={"duration_seconds": duration}
                )
    
    @contextmanager
    def track_crypto_extraction(self, news_count: int, extraction_method: str):
        """Track crypto symbol extraction operation"""
        trace_id = None
        start_time = time.time()
        
        try:
            trace_id = self.tracker.create_trace(
                name="crypto_extraction",
                metadata={
                    "news_count": news_count,
                    "extraction_method": extraction_method,
                    "operation": "crypto_extraction"
                }
            )
            
            yield trace_id
            
        except Exception as e:
            if trace_id:
                self.tracker.create_score(
                    trace_id=trace_id,
                    name="extraction_success",
                    value=0.0,
                    comment=f"Extraction failed: {str(e)}",
                    metadata={"error": str(e), "error_type": "extraction_error"}
                )
            raise
        finally:
            if trace_id:
                duration = time.time() - start_time
                self.tracker.create_score(
                    trace_id=trace_id,
                    name="extraction_duration",
                    value=duration,
                    comment=f"Extraction completed in {duration:.2f}s",
                    metadata={"duration_seconds": duration}
                )

class AIOperationTracker:
    """Track AI operations with Langfuse"""
    
    def __init__(self, langfuse_tracker: LangfuseTracker):
        self.tracker = langfuse_tracker
    
    @contextmanager
    def track_ai_analysis(self, operation: str, model: str, input_text: str, 
                         expected_output: str = "json"):
        """Track AI analysis operation"""
        trace_id = None
        start_time = time.time()
        
        try:
            trace_id = self.tracker.create_trace(
                name=f"ai_analysis_{operation}",
                metadata={
                    "operation": operation,
                    "model": model,
                    "expected_output": expected_output,
                    "input_length": len(input_text),
                    "operation_type": "ai_analysis"
                }
            )
            
            # Create generation record
            generation_id = self.tracker.create_generation(
                trace_id=trace_id,
                name=f"{operation}_generation",
                model=model,
                input_data={"text": input_text[:500] + "..." if len(input_text) > 500 else input_text},
                output_data={"expected_format": expected_output},
                metadata={"operation": operation}
            )
            
            yield trace_id, generation_id
            
        except Exception as e:
            if trace_id:
                self.tracker.create_score(
                    trace_id=trace_id,
                    name="analysis_success",
                    value=0.0,
                    comment=f"Analysis failed: {str(e)}",
                    metadata={"error": str(e), "error_type": "analysis_error"}
                )
            raise
        finally:
            if trace_id:
                duration = time.time() - start_time
                self.tracker.create_score(
                    trace_id=trace_id,
                    name="analysis_duration",
                    value=duration,
                    comment=f"Analysis completed in {duration:.2f}s",
                    metadata={"duration_seconds": duration}
                )
    
    @contextmanager
    def track_post_creation(self, platform: str, analysis_summary: str, 
                           expected_length: int = 280):
        """Track social media post creation"""
        trace_id = None
        start_time = time.time()
        
        try:
            trace_id = self.tracker.create_trace(
                name=f"post_creation_{platform}",
                metadata={
                    "platform": platform,
                    "expected_length": expected_length,
                    "analysis_summary": analysis_summary[:200] + "..." if len(analysis_summary) > 200 else analysis_summary,
                    "operation_type": "post_creation"
                }
            )
            
            yield trace_id
            
        except Exception as e:
            if trace_id:
                self.tracker.create_score(
                    trace_id=trace_id,
                    name="creation_success",
                    value=0.0,
                    comment=f"Post creation failed: {str(e)}",
                    metadata={"error": str(e), "error_type": "creation_error"}
                )
            raise
        finally:
            if trace_id:
                duration = time.time() - start_time
                self.tracker.create_score(
                    trace_id=trace_id,
                    name="creation_duration",
                    value=duration,
                    comment=f"Post creation completed in {duration:.2f}s",
                    metadata={"duration_seconds": duration}
                )

class PipelineTracker:
    """Track pipeline executions with Langfuse"""
    
    def __init__(self, langfuse_tracker: LangfuseTracker):
        self.tracker = langfuse_tracker
    
    @contextmanager
    def track_pipeline(self, pipeline_type: str, crypto_symbol: str = None, 
                      news_limit: int = 0):
        """Track complete pipeline execution"""
        trace_id = None
        start_time = time.time()
        
        try:
            trace_id = self.tracker.create_trace(
                name=f"pipeline_{pipeline_type}",
                metadata={
                    "pipeline_type": pipeline_type,
                    "crypto_symbol": crypto_symbol,
                    "news_limit": news_limit,
                    "operation_type": "pipeline_execution"
                }
            )
            
            yield trace_id
            
        except Exception as e:
            if trace_id:
                self.tracker.create_score(
                    trace_id=trace_id,
                    name="pipeline_success",
                    value=0.0,
                    comment=f"Pipeline failed: {str(e)}",
                    metadata={"error": str(e), "error_type": "pipeline_error"}
                )
            raise
        finally:
            if trace_id:
                duration = time.time() - start_time
                self.tracker.create_score(
                    trace_id=trace_id,
                    name="pipeline_duration",
                    value=duration,
                    comment=f"Pipeline completed in {duration:.2f}s",
                    metadata={"duration_seconds": duration}
                )
    
    def track_pipeline_step(self, trace_id: str, step_name: str, step_data: Dict[str, Any]):
        """Track individual pipeline step"""
        if not trace_id:
            return None
        
        return self.tracker.create_span(
            trace_id=trace_id,
            name=f"pipeline_step_{step_name}",
            metadata={
                "step_name": step_name,
                "step_data": step_data,
                "step_type": "pipeline_step"
            }
        )

# Global instances
langfuse_tracker = LangfuseTracker()
news_tracker = NewsIngestionTracker(langfuse_tracker)
ai_tracker = AIOperationTracker(langfuse_tracker)
pipeline_tracker = PipelineTracker(langfuse_tracker)

def get_langfuse_tracker() -> LangfuseTracker:
    """Get Langfuse tracker instance"""
    return langfuse_tracker

def get_news_tracker() -> NewsIngestionTracker:
    """Get news ingestion tracker instance"""
    return news_tracker

def get_ai_tracker() -> AIOperationTracker:
    """Get AI operation tracker instance"""
    return ai_tracker

def get_pipeline_tracker() -> PipelineTracker:
    """Get pipeline tracker instance"""
    return pipeline_tracker
