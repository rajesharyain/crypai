# Observability Setup Guide for AI Finance Assistant

This guide explains how to set up comprehensive observability for your AI Finance Assistant using Langfuse, OpenTelemetry, and Prometheus.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in your project root with the following variables:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Langfuse Configuration (AI Operations Tracking)
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key_here
LANGFUSE_SECRET_KEY=your_langfuse_secret_key_here
LANGFUSE_HOST=https://cloud.langfuse.com
LANGFUSE_PROJECT_ID=your_langfuse_project_id_here

# OpenTelemetry Configuration (Distributed Tracing & Metrics)
OTEL_SERVICE_NAME=ai-finance-assistant
OTEL_SERVICE_VERSION=1.0.0
OTEL_ENVIRONMENT=development
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317

# Prometheus Configuration (Metrics Collection)
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090

# Jaeger Configuration (Optional - Distributed Tracing UI)
JAEGER_ENABLED=false
JAEGER_ENDPOINT=http://localhost:14268/api/traces

# Observability Features
METRICS_ENABLED=true
TRACES_ENABLED=true
LOGS_ENABLED=true
TRACE_SAMPLING_RATE=1.0
METRIC_INTERVAL=15
```

## 🔍 What You'll Get

### 1. **Langfuse Integration**
- **AI Operation Tracking**: Monitor every OpenAI API call with input/output, tokens used, and performance
- **News Ingestion Tracking**: Track RSS feed fetching, API calls, and crypto symbol extraction
- **Pipeline Execution Tracking**: Monitor complete pipeline runs from news ingestion to post creation
- **Performance Monitoring**: Track response times, success rates, and error patterns
- **Error Tracking**: Detailed error logging with context and stack traces

### 2. **OpenTelemetry Integration**
- **Distributed Tracing**: See the complete flow of requests across all components
- **Automatic Instrumentation**: FastAPI, HTTPX, Requests, and Feedparser are automatically instrumented
- **Metrics Collection**: Built-in metrics for HTTP requests, database operations, and custom business logic
- **Log Correlation**: Correlate logs with traces for better debugging

### 3. **Prometheus Metrics**
- **Custom Business Metrics**: News processing rates, AI operation success rates, pipeline performance
- **System Metrics**: Uptime, memory usage, CPU usage, active connections
- **Performance Metrics**: Response times, throughput, error rates
- **Real-time Monitoring**: Metrics are updated in real-time and available via `/metrics` endpoint

## 📊 Available Endpoints

### Observability Status
```bash
GET /observability/status
```
Get the current status of all observability components.

### Comprehensive Metrics
```bash
GET /observability/metrics
```
Get metrics from all observability components.

### Prometheus Metrics
```bash
GET /metrics
```
Get Prometheus-formatted metrics for monitoring systems.

### Metrics Summary
```bash
GET /observability/metrics/summary
```
Get key performance indicators and system health status.

### Traces Information
```bash
GET /observability/traces
```
Get information about available tracing capabilities.

### Reset Metrics
```bash
POST /observability/metrics/reset
```
Reset all collected metrics (useful for testing).

## 🎯 Key Metrics You'll See

### API Performance
- Total API calls by endpoint
- Response times (min, max, average)
- Success/failure rates
- Status code distribution

### News Processing
- News items fetched by provider
- Crypto symbols detected
- Processing rates and efficiency
- Cache hit ratios

### AI Operations
- OpenAI API calls by operation type
- Token usage tracking
- Model performance metrics
- Success rates and error patterns

### Pipeline Execution
- Pipeline completion rates
- Processing times
- Items processed per pipeline
- Error rates by pipeline type

### System Health
- Overall system status
- Performance recommendations
- Error rate monitoring
- Resource usage tracking

## 🛠️ Setup Instructions

### 1. **Langfuse Setup**
1. Go to [Langfuse Cloud](https://cloud.langfuse.com)
2. Create a new project
3. Get your public key, secret key, and project ID
4. Add them to your `.env` file

### 2. **OpenTelemetry Setup (Optional)**
1. Install OpenTelemetry Collector (optional)
2. Set `OTEL_EXPORTER_OTLP_ENDPOINT` to your collector URL
3. For local development, use `http://localhost:4317`

### 3. **Prometheus Setup (Optional)**
1. Install Prometheus server
2. Configure it to scrape `/metrics` endpoint
3. Set up Grafana for visualization

### 4. **Jaeger Setup (Optional)**
1. Install Jaeger for distributed tracing visualization
2. Set `JAEGER_ENABLED=true` and configure endpoint
3. Access Jaeger UI at `http://localhost:16686`

## 📈 Monitoring Dashboards

### Langfuse Dashboard
- AI operation performance
- Token usage trends
- Error analysis
- Cost tracking

### Prometheus + Grafana
- System performance metrics
- Business KPIs
- Error rate monitoring
- Resource utilization

### OpenTelemetry Jaeger
- Request flow visualization
- Performance bottlenecks
- Error tracing
- Service dependencies

## 🔧 Advanced Configuration

### Custom Metrics
You can add custom metrics in your code:

```python
from prometheus_metrics import get_prometheus_metrics

metrics = get_prometheus_metrics()
metrics.record_custom_metric("business_value", 100.0)
```

### Custom Traces
Add custom tracing to your operations:

```python
from langfuse_integration import get_pipeline_tracker

tracker = get_pipeline_tracker()
with tracker.track_pipeline("custom_operation") as trace_id:
    # Your operation here
    tracker.track_pipeline_step(trace_id, "step_name", {"data": "value"})
```

### Error Tracking
Automatically track errors:

```python
from observability import get_metrics_collector

metrics = get_metrics_collector()
metrics.record_error("api_error", "news_fetch", "high")
```

## 🚨 Troubleshooting

### Common Issues

1. **Langfuse not connecting**
   - Check your API keys
   - Verify project ID
   - Check network connectivity

2. **OpenTelemetry errors**
   - Verify collector endpoint
   - Check port availability
   - Review instrumentation setup

3. **Prometheus metrics not showing**
   - Check `/metrics` endpoint
   - Verify registry configuration
   - Check for import errors

### Debug Mode
Enable debug logging by setting:

```bash
LOG_LEVEL=DEBUG
```

### Health Checks
Use the observability endpoints to check component health:

```bash
curl http://localhost:8000/observability/status
curl http://localhost:8000/observability/metrics/summary
```

## 🎉 What You'll Achieve

With this observability setup, you'll have:

✅ **Complete visibility** into your AI Finance Assistant's operations
✅ **Real-time monitoring** of performance and health
✅ **Detailed tracing** of every operation from news ingestion to post creation
✅ **Performance optimization** insights based on metrics
✅ **Error tracking** with full context and stack traces
✅ **Cost monitoring** for AI operations
✅ **Business intelligence** from custom metrics
✅ **Professional monitoring** setup ready for production

## 🔗 Useful Links

- [Langfuse Documentation](https://langfuse.com/docs)
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [FastAPI Observability](https://fastapi.tiangolo.com/advanced/middleware/)

## 📞 Support

If you encounter issues:
1. Check the logs for detailed error messages
2. Verify all environment variables are set correctly
3. Test individual components using the health check endpoints
4. Review the troubleshooting section above

Happy monitoring! 🚀
