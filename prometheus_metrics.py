"""
Prometheus Metrics for AI Finance Assistant
Provides custom metrics and Prometheus endpoint
"""

import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from prometheus_client import (
    Counter, Gauge, Histogram, Summary, 
    generate_latest, CONTENT_TYPE_LATEST,
    REGISTRY, CollectorRegistry
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PrometheusMetrics:
    """Custom Prometheus metrics for AI Finance Assistant"""
    
    def __init__(self):
        # Create a custom registry for our metrics
        self.registry = CollectorRegistry()
        
        # API Metrics
        self.api_requests_total = Counter(
            'ai_finance_api_requests_total',
            'Total number of API requests',
            ['endpoint', 'method', 'status_code'],
            registry=self.registry
        )
        
        self.api_request_duration_seconds = Histogram(
            'ai_finance_api_request_duration_seconds',
            'API request duration in seconds',
            ['endpoint', 'method'],
            registry=self.registry
        )
        
        # News Provider Metrics
        self.news_provider_requests_total = Counter(
            'ai_finance_news_provider_requests_total',
            'Total number of news provider requests',
            ['provider_name', 'provider_type', 'status'],
            registry=self.registry
        )
        
        self.news_provider_duration_seconds = Histogram(
            'ai_finance_news_provider_duration_seconds',
            'News provider request duration in seconds',
            ['provider_name', 'provider_type'],
            registry=self.registry
        )
        
        self.news_items_fetched_total = Counter(
            'ai_finance_news_items_fetched_total',
            'Total number of news items fetched',
            ['provider_name', 'source_type'],
            registry=self.registry
        )
        
        # AI Operation Metrics
        self.ai_operations_total = Counter(
            'ai_finance_ai_operations_total',
            'Total number of AI operations',
            ['operation_type', 'model', 'status'],
            registry=self.registry
        )
        
        self.ai_operation_duration_seconds = Histogram(
            'ai_finance_ai_operation_duration_seconds',
            'AI operation duration in seconds',
            ['operation_type', 'model'],
            registry=self.registry
        )
        
        self.ai_tokens_used_total = Counter(
            'ai_finance_ai_tokens_used_total',
            'Total number of AI tokens used',
            ['operation_type', 'model'],
            registry=self.registry
        )
        
        # Pipeline Metrics
        self.pipeline_executions_total = Counter(
            'ai_finance_pipeline_executions_total',
            'Total number of pipeline executions',
            ['pipeline_type', 'status'],
            registry=self.registry
        )
        
        self.pipeline_duration_seconds = Histogram(
            'ai_finance_pipeline_duration_seconds',
            'Pipeline execution duration in seconds',
            ['pipeline_type'],
            registry=self.registry
        )
        
        self.pipeline_items_processed_total = Counter(
            'ai_finance_pipeline_items_processed_total',
            'Total number of items processed by pipelines',
            ['pipeline_type', 'item_type'],
            registry=self.registry
        )
        
        # Crypto Symbol Metrics
        self.crypto_symbols_detected_total = Counter(
            'ai_finance_crypto_symbols_detected_total',
            'Total number of crypto symbols detected',
            ['symbol', 'extraction_method'],
            registry=self.registry
        )
        
        self.crypto_news_relevance_score = Histogram(
            'ai_finance_crypto_news_relevance_score',
            'Crypto news relevance scores',
            ['symbol', 'news_source'],
            registry=self.registry
        )
        
        # Error Metrics
        self.errors_total = Counter(
            'ai_finance_errors_total',
            'Total number of errors',
            ['error_type', 'component', 'severity'],
            registry=self.registry
        )
        
        # Performance Metrics
        self.cache_hit_ratio = Gauge(
            'ai_finance_cache_hit_ratio',
            'Cache hit ratio percentage',
            ['cache_type'],
            registry=self.registry
        )
        
        self.memory_usage_bytes = Gauge(
            'ai_finance_memory_usage_bytes',
            'Memory usage in bytes',
            ['component'],
            registry=self.registry
        )
        
        self.active_connections = Gauge(
            'ai_finance_active_connections',
            'Number of active connections',
            ['connection_type'],
            registry=self.registry
        )
        
        # Business Metrics
        self.news_processing_rate = Summary(
            'ai_finance_news_processing_rate',
            'News processing rate in items per second',
            ['processing_type'],
            registry=self.registry
        )
        
        self.ai_accuracy_score = Gauge(
            'ai_finance_ai_accuracy_score',
            'AI accuracy score (0-1)',
            ['operation_type', 'model'],
            registry=self.registry
        )
        
        # System Metrics
        self.system_uptime_seconds = Gauge(
            'ai_finance_system_uptime_seconds',
            'System uptime in seconds',
            registry=self.registry
        )
        
        self.system_cpu_usage_percent = Gauge(
            'ai_finance_system_cpu_usage_percent',
            'System CPU usage percentage',
            registry=self.registry
        )
        
        self.system_memory_usage_percent = Gauge(
            'ai_finance_system_memory_usage_percent',
            'System memory usage percentage',
            registry=self.registry
        )
        
        # Initialize system metrics
        self.start_time = time.time()
        self._update_system_metrics()
    
    def _update_system_metrics(self):
        """Update system metrics"""
        try:
            # Update uptime
            uptime = time.time() - self.start_time
            self.system_uptime_seconds.set(uptime)
            
            # Update CPU and memory (simplified - in production use psutil)
            # self.system_cpu_usage_percent.set(cpu_percent)
            # self.system_memory_usage_percent.set(memory_percent)
            
        except Exception as e:
            logger.error(f"Error updating system metrics: {e}")
    
    def record_api_request(self, endpoint: str, method: str, status_code: int, duration: float):
        """Record API request metrics"""
        try:
            self.api_requests_total.labels(
                endpoint=endpoint,
                method=method,
                status_code=str(status_code)
            ).inc()
            
            self.api_request_duration_seconds.labels(
                endpoint=endpoint,
                method=method
            ).observe(duration)
            
        except Exception as e:
            logger.error(f"Error recording API metrics: {e}")
    
    def record_news_provider_request(self, provider_name: str, provider_type: str, 
                                   success: bool, duration: float, items_fetched: int):
        """Record news provider request metrics"""
        try:
            status = "success" if success else "failure"
            
            self.news_provider_requests_total.labels(
                provider_name=provider_name,
                provider_type=provider_type,
                status=status
            ).inc()
            
            self.news_provider_duration_seconds.labels(
                provider_name=provider_name,
                provider_type=provider_type
            ).observe(duration)
            
            if items_fetched > 0:
                self.news_items_fetched_total.labels(
                    provider_name=provider_name,
                    source_type=provider_type
                ).inc(items_fetched)
                
        except Exception as e:
            logger.error(f"Error recording news provider metrics: {e}")
    
    def record_ai_operation(self, operation_type: str, model: str, success: bool, 
                           duration: float, tokens_used: int = 0):
        """Record AI operation metrics"""
        try:
            status = "success" if success else "failure"
            
            self.ai_operations_total.labels(
                operation_type=operation_type,
                model=model,
                status=status
            ).inc()
            
            self.ai_operation_duration_seconds.labels(
                operation_type=operation_type,
                model=model
            ).observe(duration)
            
            if tokens_used > 0:
                self.ai_tokens_used_total.labels(
                    operation_type=operation_type,
                    model=model
                ).inc(tokens_used)
                
        except Exception as e:
            logger.error(f"Error recording AI operation metrics: {e}")
    
    def record_pipeline_execution(self, pipeline_type: str, success: bool, 
                                duration: float, items_processed: int):
        """Record pipeline execution metrics"""
        try:
            status = "success" if success else "failure"
            
            self.pipeline_executions_total.labels(
                pipeline_type=pipeline_type,
                status=status
            ).inc()
            
            self.pipeline_duration_seconds.labels(
                pipeline_type=pipeline_type
            ).observe(duration)
            
            if items_processed > 0:
                self.pipeline_items_processed_total.labels(
                    pipeline_type=pipeline_type,
                    item_type="news"
                ).inc(items_processed)
                
        except Exception as e:
            logger.error(f"Error recording pipeline metrics: {e}")
    
    def record_crypto_symbol_detection(self, symbol: str, extraction_method: str, 
                                     relevance_score: float = 0.0):
        """Record crypto symbol detection metrics"""
        try:
            self.crypto_symbols_detected_total.labels(
                symbol=symbol,
                extraction_method=extraction_method
            ).inc()
            
            if relevance_score > 0:
                self.crypto_news_relevance_score.labels(
                    symbol=symbol,
                    news_source="unknown"
                ).observe(relevance_score)
                
        except Exception as e:
            logger.error(f"Error recording crypto symbol metrics: {e}")
    
    def record_error(self, error_type: str, component: str, severity: str = "medium"):
        """Record error metrics"""
        try:
            self.errors_total.labels(
                error_type=error_type,
                component=component,
                severity=severity
            ).inc()
            
        except Exception as e:
            logger.error(f"Error recording error metrics: {e}")
    
    def update_cache_metrics(self, cache_type: str, hit_ratio: float):
        """Update cache metrics"""
        try:
            self.cache_hit_ratio.labels(cache_type=cache_type).set(hit_ratio)
        except Exception as e:
            logger.error(f"Error updating cache metrics: {e}")
    
    def update_memory_usage(self, component: str, usage_bytes: int):
        """Update memory usage metrics"""
        try:
            self.memory_usage_bytes.labels(component=component).set(usage_bytes)
        except Exception as e:
            logger.error(f"Error updating memory metrics: {e}")
    
    def update_connection_count(self, connection_type: str, count: int):
        """Update connection count metrics"""
        try:
            self.active_connections.labels(connection_type=connection_type).set(count)
        except Exception as e:
            logger.error(f"Error updating connection metrics: {e}")
    
    def record_news_processing_rate(self, processing_type: str, rate: float):
        """Record news processing rate"""
        try:
            self.news_processing_rate.labels(processing_type=processing_type).observe(rate)
        except Exception as e:
            logger.error(f"Error recording processing rate: {e}")
    
    def update_ai_accuracy(self, operation_type: str, model: str, accuracy: float):
        """Update AI accuracy score"""
        try:
            self.ai_accuracy_score.labels(
                operation_type=operation_type,
                model=model
            ).set(accuracy)
        except Exception as e:
            logger.error(f"Error updating AI accuracy: {e}")
    
    def get_metrics(self) -> bytes:
        """Get Prometheus metrics in text format"""
        try:
            return generate_latest(self.registry)
        except Exception as e:
            logger.error(f"Error generating metrics: {e}")
            return b"# Error generating metrics\n"
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary for monitoring"""
        try:
            # Collect metrics from registry
            metrics_data = {}
            
            for metric in self.registry.collect():
                metric_name = metric.name
                if metric_name not in metrics_data:
                    metrics_data[metric_name] = []
                
                for sample in metric.samples:
                    metrics_data[metric_name].append({
                        'name': sample.name,
                        'labels': sample.labels,
                        'value': sample.value,
                        'timestamp': sample.timestamp
                    })
            
            return {
                'metrics_count': len(metrics_data),
                'metrics': metrics_data,
                'registry_info': {
                    'start_time': self.start_time,
                    'uptime_seconds': time.time() - self.start_time
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting metrics summary: {e}")
            return {'error': str(e)}

# Global instance
prometheus_metrics = PrometheusMetrics()

def get_prometheus_metrics() -> PrometheusMetrics:
    """Get Prometheus metrics instance"""
    return prometheus_metrics

def record_api_metrics(endpoint: str, method: str, status_code: int, duration: float):
    """Record API metrics (convenience function)"""
    prometheus_metrics.record_api_request(endpoint, method, status_code, duration)

def record_news_provider_metrics(provider_name: str, provider_type: str, 
                                success: bool, duration: float, items_fetched: int):
    """Record news provider metrics (convenience function)"""
    prometheus_metrics.record_news_provider_request(provider_name, provider_type, 
                                                  success, duration, items_fetched)

def record_ai_operation_metrics(operation_type: str, model: str, success: bool, 
                               duration: float, tokens_used: int = 0):
    """Record AI operation metrics (convenience function)"""
    prometheus_metrics.record_ai_operation(operation_type, model, success, 
                                         duration, tokens_used)

def record_pipeline_metrics(pipeline_type: str, success: bool, 
                           duration: float, items_processed: int):
    """Record pipeline metrics (convenience function)"""
    prometheus_metrics.record_pipeline_execution(pipeline_type, success, 
                                               duration, items_processed)
