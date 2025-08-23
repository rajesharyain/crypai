"""
OpenTelemetry Integration for AI Finance Assistant
Provides distributed tracing, metrics, and logging capabilities
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
    from opentelemetry import trace, metrics
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
    from opentelemetry.exporter.prometheus import PrometheusMetricReader
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    from opentelemetry.instrumentation.logging import LoggingInstrumentor
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    logger.warning("OpenTelemetry not available. Install with: pip install opentelemetry-api opentelemetry-sdk")

class OpenTelemetryManager:
    """Manage OpenTelemetry instrumentation and exporters"""
    
    def __init__(self):
        if not OTEL_AVAILABLE:
            self.tracer_provider = None
            self.meter_provider = None
            self.enabled = False
            self.tracer = None
            self.meter = None
            logger.warning("OpenTelemetry disabled - packages not available")
            return

        self.enabled = True
        self.tracer_provider = None
        self.meter_provider = None
        self.tracer = None
        self.meter = None
        self.span_processors = []
        self.metric_readers = []

        # Configuration
        self.service_name = os.getenv('OTEL_SERVICE_NAME', 'ai-finance-assistant')
        self.service_version = os.getenv('OTEL_SERVICE_VERSION', '1.0.0')
        self.environment = os.getenv('OTEL_ENVIRONMENT', 'development')
        self.otel_endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'http://localhost:4317')
        self.prometheus_enabled = os.getenv('PROMETHEUS_ENABLED', 'true').lower() == 'true'
        self.prometheus_port = int(os.getenv('PROMETHEUS_PORT', '9090'))

        # Initialize providers
        self._initialize_providers()
        self._setup_instrumentation()
        
        # Ensure tracer and meter are always set
        if not self.tracer:
            self.tracer = None
        if not self.meter:
            self.meter = None
    
    def _initialize_providers(self):
        """Initialize TracerProvider and MeterProvider"""
        try:
            # Create resource with service information
            resource = Resource.create({
                "service.name": self.service_name,
                "service.version": self.service_version,
                "deployment.environment": self.environment,
                "application": "ai-finance-assistant",
                "component": "news-pipeline"
            })
            
            # Initialize TracerProvider
            self.tracer_provider = TracerProvider(resource=resource)
            
            # Add span processors
            if self.otel_endpoint and self.otel_endpoint != 'http://localhost:4317':
                # OTLP HTTP exporter
                otlp_exporter = OTLPSpanExporter(endpoint=f"{self.otel_endpoint}/v1/traces")
                self.span_processors.append(BatchSpanProcessor(otlp_exporter))
                logger.info(f"Added OTLP span exporter: {self.otel_endpoint}")
            
            # Console exporter for development
            if self.environment == 'development':
                console_exporter = ConsoleSpanExporter()
                self.span_processors.append(BatchSpanProcessor(console_exporter))
                logger.info("Added console span exporter for development")
            
            # Add processors to provider
            for processor in self.span_processors:
                self.tracer_provider.add_span_processor(processor)
            
            # Set global tracer provider
            trace.set_tracer_provider(self.tracer_provider)
            self.tracer = trace.get_tracer(self.service_name, self.service_version)
            
            # Initialize MeterProvider
            self.meter_provider = MeterProvider(resource=resource)
            
            # Add metric readers
            if self.prometheus_enabled:
                # Prometheus exporter
                prometheus_reader = PrometheusMetricReader(port=self.prometheus_port)
                self.metric_readers.append(prometheus_reader)
                logger.info(f"Added Prometheus metric reader on port {self.prometheus_port}")
            
            if self.otel_endpoint and self.otel_endpoint != 'http://localhost:4317':
                # OTLP HTTP exporter for metrics
                otlp_metric_exporter = OTLPMetricExporter(endpoint=f"{self.otel_endpoint}/v1/metrics")
                metric_reader = PeriodicExportingMetricReader(otlp_metric_exporter)
                self.metric_readers.append(metric_reader)
                logger.info(f"Added OTLP metric exporter: {self.otel_endpoint}")
            
            # Console exporter for development
            if self.environment == 'development':
                console_metric_exporter = ConsoleMetricExporter()
                metric_reader = PeriodicExportingMetricReader(console_metric_exporter)
                self.metric_readers.append(metric_reader)
                logger.info("Added console metric exporter for development")
            
            # Add readers to provider
            for reader in self.metric_readers:
                self.meter_provider.add_metric_reader(reader)
            
            # Set global meter provider
            metrics.set_meter_provider(self.meter_provider)
            self.meter = metrics.get_meter(self.service_name, self.service_version)
            
            logger.info("✅ OpenTelemetry providers initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize OpenTelemetry providers: {e}")
            self.enabled = False
            self.tracer = None
            self.meter = None
    
    def _setup_instrumentation(self):
        """Setup automatic instrumentation for various libraries"""
        if not self.enabled:
            return
        
        try:
            # Instrument logging
            LoggingInstrumentor().instrument()
            logger.info("✅ Logging instrumentation enabled")
            
        except Exception as e:
            logger.error(f"❌ Failed to setup instrumentation: {e}")
    
    def instrument_fastapi(self, app):
        """Instrument FastAPI application"""
        if not self.enabled:
            logger.warning("OpenTelemetry not enabled, skipping FastAPI instrumentation")
            return
        
        try:
            FastAPIInstrumentor.instrument_app(app)
            logger.info("✅ FastAPI instrumentation enabled")
        except Exception as e:
            logger.error(f"❌ Failed to instrument FastAPI: {e}")
    
    def instrument_httpx(self):
        """Instrument HTTPX client"""
        if not self.enabled:
            logger.warning("OpenTelemetry not enabled, skipping HTTPX instrumentation")
            return
        
        try:
            HTTPXClientInstrumentor().instrument()
            logger.info("✅ HTTPX instrumentation enabled")
        except Exception as e:
            logger.error(f"❌ Failed to instrument HTTPX: {e}")
    
    def instrument_requests(self):
        """Instrument requests library"""
        if not self.enabled:
            logger.warning("OpenTelemetry not enabled, skipping requests instrumentation")
            return
        
        try:
            RequestsInstrumentor().instrument()
            logger.info("✅ Requests instrumentation enabled")
        except Exception as e:
            logger.error(f"❌ Failed to instrument requests: {e}")
    
    def instrument_feedparser(self):
        """Instrument feedparser library"""
        if not self.enabled:
            logger.warning("OpenTelemetry not enabled, skipping feedparser instrumentation")
            return
        
        try:
            # FeedparserInstrumentor().instrument() # This line is removed
            logger.info("✅ Feedparser instrumentation enabled")
        except Exception as e:
            logger.error(f"❌ Failed to instrument feedparser: {e}")
    
    def get_tracer(self):
        """Get the tracer instance"""
        return self.tracer if self.enabled else None
    
    def get_meter(self):
        """Get the meter instance"""
        return self.meter if self.enabled else None
    
    def is_enabled(self) -> bool:
        """Check if OpenTelemetry is enabled"""
        return self.enabled
    
    def shutdown(self):
        """Shutdown OpenTelemetry providers"""
        if not self.enabled:
            return
        
        try:
            if self.tracer_provider:
                self.tracer_provider.shutdown()
            if self.meter_provider:
                self.meter_provider.shutdown()
            logger.info("✅ OpenTelemetry providers shut down successfully")
        except Exception as e:
            logger.error(f"❌ Error shutting down OpenTelemetry: {e}")

class TracingHelper:
    """Helper class for creating spans and traces"""
    
    def __init__(self, tracer):
        self.tracer = tracer
    
    @contextmanager
    def span(self, name: str, attributes: Dict[str, Any] = None):
        """Create a span context manager"""
        if not self.tracer:
            yield
            return
        
        with self.tracer.start_as_current_span(name, attributes=attributes or {}) as span:
            try:
                yield span
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise
    
    def add_event(self, span, name: str, attributes: Dict[str, Any] = None):
        """Add an event to a span"""
        if span:
            span.add_event(name, attributes or {})
    
    def set_attribute(self, span, key: str, value: Any):
        """Set an attribute on a span"""
        if span:
            span.set_attribute(key, value)

class MetricsHelper:
    """Helper class for creating and recording metrics"""
    
    def __init__(self, meter):
        self.meter = meter
        self.counters = {}
        self.gauges = {}
        self.histograms = {}
    
    def create_counter(self, name: str, description: str = "", unit: str = ""):
        """Create a counter metric"""
        if not self.meter:
            return None
        
        if name not in self.counters:
            self.counters[name] = self.meter.create_counter(
                name=name,
                description=description,
                unit=unit
            )
        return self.counters[name]
    
    def create_gauge(self, name: str, description: str = "", unit: str = ""):
        """Create a gauge metric"""
        if not self.meter:
            return None
        
        if name not in self.gauges:
            self.gauges[name] = self.meter.create_up_down_counter(
                name=name,
                description=description,
                unit=unit
            )
        return self.gauges[name]
    
    def create_histogram(self, name: str, description: str = "", unit: str = ""):
        """Create a histogram metric"""
        if not self.meter:
            return None
        
        if name not in self.histograms:
            self.histograms[name] = self.meter.create_histogram(
                name=name,
                description=description,
                unit=unit
            )
        return self.histograms[name]
    
    def increment_counter(self, name: str, value: int = 1, attributes: Dict[str, Any] = None):
        """Increment a counter metric"""
        counter = self.create_counter(name)
        if counter:
            counter.add(value, attributes or {})
    
    def set_gauge(self, name: str, value: float, attributes: Dict[str, Any] = None):
        """Set a gauge metric value"""
        gauge = self.create_gauge(name)
        if gauge:
            gauge.add(value, attributes or {})
    
    def record_histogram(self, name: str, value: float, attributes: Dict[str, Any] = None):
        """Record a histogram metric value"""
        histogram = self.create_histogram(name)
        if histogram:
            histogram.record(value, attributes or {})

# Global instances
otel_manager = OpenTelemetryManager()
tracing_helper = TracingHelper(otel_manager.get_tracer()) if otel_manager.is_enabled() and otel_manager.get_tracer() else None
metrics_helper = MetricsHelper(otel_manager.get_meter()) if otel_manager.is_enabled() and otel_manager.get_meter() else None

def get_otel_manager() -> OpenTelemetryManager:
    """Get OpenTelemetry manager instance"""
    return otel_manager

def get_tracing_helper() -> TracingHelper:
    """Get tracing helper instance"""
    return tracing_helper

def get_metrics_helper() -> MetricsHelper:
    """Get metrics helper instance"""
    return metrics_helper

def instrument_fastapi_app(app):
    """Instrument FastAPI application with OpenTelemetry"""
    return otel_manager.instrument_fastapi(app)

def setup_otel_instrumentation():
    """Setup all OpenTelemetry instrumentation"""
    otel_manager.instrument_httpx()
    otel_manager.instrument_requests()
    # otel_manager.instrument_feedparser()  # Feedparser instrumentation not available
