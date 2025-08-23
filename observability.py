"""
Observability Configuration for AI Finance Assistant
Integrates Langfuse and OpenTelemetry for comprehensive monitoring
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ObservabilityConfig:
    """Configuration for observability and monitoring"""
    
    def __init__(self):
        # Langfuse Configuration
        self.langfuse_public_key = os.getenv('LANGFUSE_PUBLIC_KEY')
        self.langfuse_secret_key = os.getenv('LANGFUSE_SECRET_KEY')
        self.langfuse_host = os.getenv('LANGFUSE_HOST', 'https://cloud.langfuse.com')
        self.langfuse_project_id = os.getenv('LANGFUSE_PROJECT_ID')
        
        # OpenTelemetry Configuration
        self.otel_endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'http://localhost:4317')
        self.otel_service_name = os.getenv('OTEL_SERVICE_NAME', 'ai-finance-assistant')
        self.otel_service_version = os.getenv('OTEL_SERVICE_VERSION', '1.0.0')
        self.otel_environment = os.getenv('OTEL_ENVIRONMENT', 'development')
        
        # Prometheus Configuration
        self.prometheus_enabled = os.getenv('PROMETHEUS_ENABLED', 'true').lower() == 'true'
        self.prometheus_port = int(os.getenv('PROMETHEUS_PORT', '9090'))
        
        # Jaeger Configuration (optional)
        self.jaeger_enabled = os.getenv('JAEGER_ENABLED', 'false').lower() == 'true'
        self.jaeger_endpoint = os.getenv('JAEGER_ENDPOINT', 'http://localhost:14268/api/traces')
        
        # Metrics Configuration
        self.metrics_enabled = os.getenv('METRICS_ENABLED', 'true').lower() == 'true'
        self.traces_enabled = os.getenv('TRACES_ENABLED', 'true').lower() == 'true'
        self.logs_enabled = os.getenv('LOGS_ENABLED', 'true').lower() == 'true'
        
        # Sampling Configuration
        self.trace_sampling_rate = float(os.getenv('TRACE_SAMPLING_RATE', '1.0'))
        self.metric_interval = int(os.getenv('METRIC_INTERVAL', '15'))
        
        # Custom Dimensions
        self.custom_dimensions = {
            'application': 'ai-finance-assistant',
            'component': 'news-pipeline',
            'deployment': self.otel_environment,
            'version': self.otel_service_version
        }
    
    def is_langfuse_configured(self) -> bool:
        """Check if Langfuse is properly configured"""
        return all([
            self.langfuse_public_key,
            self.langfuse_secret_key,
            self.langfuse_project_id
        ])
    
    def is_otel_configured(self) -> bool:
        """Check if OpenTelemetry is properly configured"""
        return bool(self.otel_endpoint)
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary for monitoring"""
        return {
            'langfuse_configured': self.is_langfuse_configured(),
            'opentelemetry_configured': self.is_otel_configured(),
            'prometheus_enabled': self.prometheus_enabled,
            'jaeger_enabled': self.jaeger_enabled,
            'metrics_enabled': self.metrics_enabled,
            'traces_enabled': self.traces_enabled,
            'logs_enabled': self.logs_enabled,
            'service_name': self.otel_service_name,
            'environment': self.otel_environment,
            'custom_dimensions': self.custom_dimensions
        }

class MetricsCollector:
    """Collect and track application metrics"""
    
    def __init__(self):
        self.metrics = {
            'api_calls': {},
            'news_providers': {},
            'ai_operations': {},
            'pipeline_executions': {},
            'errors': {},
            'performance': {}
        }
        self.start_time = datetime.now(timezone.utc)
    
    def record_api_call(self, endpoint: str, method: str, status_code: int, duration: float):
        """Record API call metrics"""
        if endpoint not in self.metrics['api_calls']:
            self.metrics['api_calls'][endpoint] = {
                'total_calls': 0,
                'successful_calls': 0,
                'failed_calls': 0,
                'total_duration': 0.0,
                'avg_duration': 0.0,
                'min_duration': float('inf'),
                'max_duration': 0.0,
                'status_codes': {},
                'methods': {}
            }
        
        metric = self.metrics['api_calls'][endpoint]
        metric['total_calls'] += 1
        metric['total_duration'] += duration
        
        if 200 <= status_code < 400:
            metric['successful_calls'] += 1
        else:
            metric['failed_calls'] += 1
        
        # Update duration stats
        if duration < metric['min_duration']:
            metric['min_duration'] = duration
        if duration > metric['max_duration']:
            metric['max_duration'] = duration
        
        metric['avg_duration'] = metric['total_duration'] / metric['total_calls']
        
        # Track status codes
        status_str = str(status_code)
        metric['status_codes'][status_str] = metric['status_codes'].get(status_str, 0) + 1
        
        # Track methods
        metric['methods'][method] = metric['methods'].get(method, 0) + 1
    
    def record_news_provider_call(self, provider: str, success: bool, duration: float, items_fetched: int):
        """Record news provider metrics"""
        if provider not in self.metrics['news_providers']:
            self.metrics['news_providers'][provider] = {
                'total_calls': 0,
                'successful_calls': 0,
                'failed_calls': 0,
                'total_items_fetched': 0,
                'avg_items_per_call': 0.0,
                'total_duration': 0.0,
                'avg_duration': 0.0,
                'success_rate': 0.0
            }
        
        metric = self.metrics['news_providers'][provider]
        metric['total_calls'] += 1
        metric['total_duration'] += duration
        metric['total_items_fetched'] += items_fetched
        
        if success:
            metric['successful_calls'] += 1
        else:
            metric['failed_calls'] += 1
        
        metric['avg_duration'] = metric['total_duration'] / metric['total_calls']
        metric['avg_items_per_call'] = metric['total_items_fetched'] / metric['total_calls']
        metric['success_rate'] = (metric['successful_calls'] / metric['total_calls']) * 100
    
    def record_ai_operation(self, operation: str, model: str, success: bool, duration: float, tokens_used: int = 0):
        """Record AI operation metrics"""
        if operation not in self.metrics['ai_operations']:
            self.metrics['ai_operations'][operation] = {
                'total_calls': 0,
                'successful_calls': 0,
                'failed_calls': 0,
                'total_duration': 0.0,
                'avg_duration': 0.0,
                'total_tokens': 0,
                'avg_tokens_per_call': 0.0,
                'models_used': {},
                'success_rate': 0.0
            }
        
        metric = self.metrics['ai_operations'][operation]
        metric['total_calls'] += 1
        metric['total_duration'] += duration
        metric['total_tokens'] += tokens_used
        
        if success:
            metric['successful_calls'] += 1
        else:
            metric['failed_calls'] += 1
        
        metric['avg_duration'] = metric['total_duration'] / metric['total_calls']
        metric['avg_tokens_per_call'] = metric['total_tokens'] / metric['total_calls']
        metric['success_rate'] = (metric['successful_calls'] / metric['total_calls']) * 100
        
        # Track model usage
        metric['models_used'][model] = metric['models_used'].get(model, 0) + 1
    
    def record_pipeline_execution(self, pipeline_type: str, success: bool, duration: float, items_processed: int):
        """Record pipeline execution metrics"""
        if pipeline_type not in self.metrics['pipeline_executions']:
            self.metrics['pipeline_executions'][pipeline_type] = {
                'total_executions': 0,
                'successful_executions': 0,
                'failed_executions': 0,
                'total_items_processed': 0,
                'avg_items_per_execution': 0.0,
                'total_duration': 0.0,
                'avg_duration': 0.0,
                'success_rate': 0.0
            }
        
        metric = self.metrics['pipeline_executions'][pipeline_type]
        metric['total_executions'] += 1
        metric['total_duration'] += duration
        metric['total_items_processed'] += items_processed
        
        if success:
            metric['successful_executions'] += 1
        else:
            metric['failed_executions'] += 1
        
        metric['avg_duration'] = metric['total_duration'] / metric['total_executions']
        metric['avg_items_per_execution'] = metric['total_items_processed'] / metric['total_executions']
        metric['success_rate'] = (metric['successful_executions'] / metric['total_executions']) * 100
    
    def record_error(self, error_type: str, component: str, error_message: str):
        """Record error metrics"""
        if error_type not in self.metrics['errors']:
            self.metrics['errors'][error_type] = {
                'total_errors': 0,
                'components': {},
                'error_messages': {},
                'last_occurrence': None
            }
        
        metric = self.metrics['errors'][error_type]
        metric['total_errors'] += 1
        metric['last_occurrence'] = datetime.now(timezone.utc).isoformat()
        
        # Track component errors
        metric['components'][component] = metric['components'].get(component, 0) + 1
        
        # Track error messages (truncated for privacy)
        truncated_message = error_message[:100] + "..." if len(error_message) > 100 else error_message
        metric['error_messages'][truncated_message] = metric['error_messages'].get(truncated_message, 0) + 1
    
    def record_performance_metric(self, metric_name: str, value: float, unit: str = ""):
        """Record custom performance metrics"""
        if metric_name not in self.metrics['performance']:
            self.metrics['performance'][metric_name] = {
                'values': [],
                'count': 0,
                'sum': 0.0,
                'min': float('inf'),
                'max': 0.0,
                'avg': 0.0,
                'unit': unit
            }
        
        metric = self.metrics['performance'][metric_name]
        metric['values'].append(value)
        metric['count'] += 1
        metric['sum'] += value
        
        if value < metric['min']:
            metric['min'] = value
        if value > metric['max']:
            metric['max'] = value
        
        metric['avg'] = metric['sum'] / metric['count']
        
        # Keep only last 1000 values to prevent memory issues
        if len(metric['values']) > 1000:
            metric['values'] = metric['values'][-1000:]
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        uptime = (datetime.now(timezone.utc) - self.start_time).total_seconds()
        
        return {
            'uptime_seconds': uptime,
            'uptime_formatted': str(datetime.now(timezone.utc) - self.start_time),
            'start_time': self.start_time.isoformat(),
            'current_time': datetime.now(timezone.utc).isoformat(),
            'metrics': self.metrics,
            'summary': {
                'total_api_calls': sum(m['total_calls'] for m in self.metrics['api_calls'].values()),
                'total_news_provider_calls': sum(m['total_calls'] for m in self.metrics['news_providers'].values()),
                'total_ai_operations': sum(m['total_calls'] for m in self.metrics['ai_operations'].values()),
                'total_pipeline_executions': sum(m['total_executions'] for m in self.metrics['pipeline_executions'].values()),
                'total_errors': sum(m['total_errors'] for m in self.metrics['errors'].values())
            }
        }
    
    def reset_metrics(self):
        """Reset all metrics (useful for testing)"""
        self.metrics = {
            'api_calls': {},
            'news_providers': {},
            'ai_operations': {},
            'pipeline_executions': {},
            'errors': {},
            'performance': {}
        }
        self.start_time = datetime.now(timezone.utc)

# Global instances
observability_config = ObservabilityConfig()
metrics_collector = MetricsCollector()

def get_observability_config() -> ObservabilityConfig:
    """Get observability configuration instance"""
    return observability_config

def get_metrics_collector() -> MetricsCollector:
    """Get metrics collector instance"""
    return metrics_collector
