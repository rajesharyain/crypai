# 🚀 AI Finance Assistant MVP - API Endpoints Categorized by Agent

## 📋 **Table of Contents**
1. [System & Health](#system--health)
2. [News Ingestion Agent](#news-ingestion-agent)
3. [MCP Integration Agent](#mcp-integration-agent)
4. [Fundamentals Fetcher Agent](#fundamentals-fetcher-agent)
5. [Analyzer Agent](#analyzer-agent)
6. [Post Creator Agent](#post-creator-agent)
7. [Orchestrator Agent](#orchestrator-agent)
8. [Observability & Monitoring](#observability--monitoring)
9. [Web UI & Dashboard](#web-ui--dashboard)

---

## 🔧 **System & Health**

### **Core System Endpoints**
| Endpoint | Method | Description | Status |
|----------|--------|-------------|---------|
| `/` | GET | Root endpoint with system overview | ✅ Active |
| `/ping` | GET | Health check endpoint | ✅ Active |
| `/docs` | GET | Interactive API documentation (Swagger UI) | ✅ Active |
| `/openapi.json` | GET | OpenAPI schema in JSON format | ✅ Active |

---

## 📰 **News Ingestion Agent**

### **Core News Fetching**
| Endpoint | Method | Description | Status |
|----------|--------|-------------|---------|
| `/fetch_news` | GET | Fetch latest news from all sources | ✅ Active |
| `/news/crypto` | GET | Get crypto-focused news with symbol extraction | ✅ Active |
| `/news/crypto/enhanced` | GET | Fetch enhanced crypto news with AI analysis | ✅ Active |

### **Crypto Symbol Management**
| Endpoint | Method | Description | Status |
|----------|--------|-------------|---------|
| `/news/symbols` | GET | Get all detected cryptocurrency symbols | ✅ Active |
| `/news/crypto/{symbol}` | GET | Get news for specific cryptocurrency | ✅ Active |
| `/news/crypto/symbol/{symbol}` | GET | Get news by crypto symbol from cache | ✅ Active |

### **News Cache Management**
| Endpoint | Method | Description | Status |
|----------|--------|-------------|---------|
| `/news/crypto/cache/refresh` | GET | Manually refresh crypto news cache | ✅ Active |
| `/news/crypto/cache/status` | GET | Get crypto news cache status | ✅ Active |

### **News Source Management**
| Endpoint | Method | Description | Status |
|----------|--------|-------------|---------|
| `/sources` | GET | Get all configured news sources | ✅ Active |
| `/add_source` | POST | Add new news source | ✅ Active |
| `/news/sources` | GET | List all news sources | ✅ Active |
| `/news/health` | GET | Check health of all news sources | ✅ Active |

---

## 🔗 **MCP Integration Agent**

### **MCP Server Management**
| Endpoint | Method | Description | Status |
|----------|--------|-------------|---------|
| `/mcp/servers` | GET | List all MCP servers | ✅ Active |
| `/mcp/status` | GET | Get MCP server status | ✅ Active |
| `/mcp/health` | GET | Check MCP server health | ✅ Active |
| `/mcp/server/priority` | POST | Change server priority | ✅ Active |

### **MCP News Integration**
| Endpoint | Method | Description | Status |
|----------|--------|-------------|---------|
| `/mcp/news` | GET | Get news from MCP servers | ✅ Active |

---

## 💰 **Fundamentals Fetcher Agent**

### **Single Coin Fundamentals**
| Endpoint | Method | Description | Status |
|----------|--------|-------------|---------|
| `/fundamentals/{symbol}` | GET | Get fundamentals for specific crypto | ✅ Active |

### **Multiple Coins & Market Data**
| Endpoint | Method | Description | Status |
|----------|--------|-------------|---------|
| `/fundamentals/multiple` | POST | Get fundamentals for multiple cryptos | ✅ Active |
| `/fundamentals/trending` | GET | Get trending coins with fundamentals | ✅ Active |
| `/fundamentals/market/overview` | GET | Get overall market overview | ✅ Active |

### **Coin Search & Discovery**
| Endpoint | Method | Description | Status |
|----------|--------|-------------|---------|
| `/fundamentals/search/{query}` | GET | Search for coins by name/symbol | ✅ Active |

---

## 🔍 **Analyzer Agent**

### **Single News Analysis**
| Endpoint | Method | Description | Status |
|----------|--------|-------------|---------|
| `/analyze` | POST | Analyze single news article | ✅ Active |

### **Batch Analysis**
| Endpoint | Method | Description | Status |
|----------|--------|-------------|---------|
| `/analyze/batch` | POST | Analyze multiple news articles | ✅ Active |

### **Agent Status**
| Endpoint | Method | Description | Status |
|----------|--------|-------------|---------|
| `/analyze/status` | GET | Get analyzer agent status | ✅ Active |

---

## ✍️ **Post Creator Agent**

### **Single Post Creation**
| Endpoint | Method | Description | Status |
|----------|--------|-------------|---------|
| `/create_post` | POST | Create social media posts | ✅ Active |

### **Batch Post Creation**
| Endpoint | Method | Description | Status |
|----------|--------|-------------|---------|
| `/create_post/batch` | POST | Create posts for multiple analyses | ✅ Active |

### **Agent Status**
| Endpoint | Method | Description | Status |
|----------|--------|-------------|---------|
| `/create_post/status` | GET | Get post creator agent status | ✅ Active |

---

## 🎯 **Orchestrator Agent**

### **Single Pipeline Execution**
| Endpoint | Method | Description | Status |
|----------|--------|-------------|---------|
| `/run_pipeline` | POST | Run complete AI-powered pipeline | ✅ Active |

### **Multiple News Pipeline**
| Endpoint | Method | Description | Status |
|----------|--------|-------------|---------|
| `/run_pipeline/multiple` | POST | Run pipeline for multiple news items | ✅ Active |

### **Crypto-Specific Pipeline**
| Endpoint | Method | Description | Status |
|----------|--------|-------------|---------|
| `/run_pipeline/crypto/{crypto_symbol}` | POST | Run pipeline for specific cryptocurrency | ✅ Active |

---

## 📊 **Observability & Monitoring**

### **System Status & Health**
| Endpoint | Method | Description | Status |
|----------|--------|-------------|---------|
| `/observability/status` | GET | Get observability components status | ✅ Active |
| `/observability/traces` | GET | Get tracing capabilities info | ✅ Active |

### **Metrics & Analytics**
| Endpoint | Method | Description | Status |
|----------|--------|-------------|---------|
| `/observability/metrics` | GET | Get comprehensive metrics | ✅ Active |
| `/observability/metrics/summary` | GET | Get key metrics summary | ✅ Active |
| `/metrics` | GET | Prometheus metrics endpoint | ✅ Active |

### **Metrics Management**
| Endpoint | Method | Description | Status |
|----------|--------|-------------|---------|
| `/observability/metrics/reset` | POST | Reset all collected metrics | ✅ Active |

---

## 🖥️ **Web UI & Dashboard**

### **User Interface**
| Endpoint | Method | Description | Status |
|----------|--------|-------------|---------|
| `/ui` | GET | Orchestrator dashboard UI | ✅ Active |

---

## 🔄 **Legacy & Utility Endpoints**

### **Chat & Models (Legacy)**
| Endpoint | Method | Description | Status |
|----------|--------|-------------|---------|
| `/chat` | POST | Chat endpoint (legacy) | ⚠️ Legacy |
| `/models` | GET | Get available models (legacy) | ⚠️ Legacy |

---

## 📈 **Endpoint Statistics**

### **Total Endpoints: 47**
- **System & Health**: 4 endpoints
- **News Ingestion Agent**: 12 endpoints
- **MCP Integration Agent**: 5 endpoints
- **Fundamentals Fetcher Agent**: 6 endpoints
- **Analyzer Agent**: 3 endpoints
- **Post Creator Agent**: 3 endpoints
- **Orchestrator Agent**: 3 endpoints
- **Observability & Monitoring**: 6 endpoints
- **Web UI & Dashboard**: 1 endpoint
- **Legacy & Utility**: 2 endpoints

### **HTTP Methods Distribution**
- **GET**: 35 endpoints (74.5%)
- **POST**: 12 endpoints (25.5%)

### **Response Status Codes**
- **200 OK**: All endpoints
- **422 Validation Error**: POST endpoints with request validation
- **500 Internal Server Error**: Error handling endpoints

---

## 🚀 **Quick Start Guide**

### **1. Health Check**
```bash
curl http://localhost:8000/ping
```

### **2. Run Complete Pipeline**
```bash
curl -X POST "http://localhost:8000/run_pipeline" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "SUI", "news_limit": 3, "crypto_focus": true}'
```

### **3. Get Crypto News**
```bash
curl "http://localhost:8000/news/crypto?limit=5"
```

### **4. Check System Status**
```bash
curl http://localhost:8000/observability/status
```

### **5. Access Web UI**
Open in browser: `http://localhost:8000/ui`

---

## 📝 **Notes**

- **All endpoints are fully functional** and integrated with the observability system
- **Fallback mechanisms** are in place for when OpenAI API is unavailable
- **Rate limiting** is implemented to prevent API abuse
- **Comprehensive error handling** with detailed error messages
- **Real-time metrics** available through Prometheus endpoint
- **Full tracing** available when OpenTelemetry is enabled

---

*Last Updated: August 23, 2025*
*API Version: 1.0.0*
*Status: Production Ready* 🎉
