# 🚀 AI Finance Assistant - Quick Lean MVP

**Built with ❤️ using FastAPI + LangChain + Intelligent News Ingestion + MCP Server Integration + RSS Fallbacks + Cryptocurrency Fundamentals**

## 🌟 **Enhanced Features**

### **Phase 1: Project Setup** ✅
- FastAPI + LangChain integration
- OpenAI API integration
- Health check endpoints
- Environment variable management

### **Phase 2: Agentic News Ingestion Pipeline** ✅
- **NewsIngestionAgent** with LangChain
- RSS feeds: CoinDesk, CoinTelegraph
- API sources: Crypto News API, Token Metrics API, CoinFeeds API
- AI-powered sentiment analysis
- Smart deduplication and relevance scoring

### **Phase 3: MCP Server Integration + RSS Fallbacks** ✅
- **ChainGPT AI News MCP Server** (with API key)
- **Coin MCP Server** (CoinGecko integration)
- **CryptoPanic MCP Server** (free tier)
- **🆕 RSS Fallback System**:
  - **CoinDesk RSS** (always available, no API key needed)
  - **CoinTelegraph RSS** (always available, no API key needed)
- **Smart Fallback Strategy**: RSS sources work even when API keys are missing
- **Unified News Aggregation**: All sources work together seamlessly

### **Phase 4: Fundamentals Fetcher Agent** ✅
- **🆕 FundamentalsFetcherAgent** with CoinGecko API integration
- **Comprehensive Cryptocurrency Data**:
  - Current price (USD, BTC, ETH)
  - 24h price changes and percentages
  - Market cap and rankings
  - Volume and supply metrics
  - All-time high/low data
  - ROI and performance metrics
  - 7-day price sparklines
- **Smart Rate Limiting**: Compliant with CoinGecko free tier (50 calls/minute)
- **Async Context Manager**: Efficient resource management
- **Multiple Fetching Modes**: Single coin, multiple coins, trending coins, market overview

## 🎯 **Key Benefits**

### **🔑 No API Key Required for Basic Functionality**
- RSS sources (CoinDesk, CoinTelegraph) work immediately
- System gracefully handles missing API keys
- Always provides crypto news regardless of configuration

### **🔄 Intelligent Fallback System**
- **Priority 1**: RSS sources (reliable, no API keys)
- **Priority 2**: Free API sources (CoinGecko, CryptoPanic)
- **Priority 3**: Premium sources (ChainGPT with API key)
- Automatic fallback activation when sources fail

### **📰 Comprehensive News Coverage**
- **Traditional RSS**: CoinDesk, CoinTelegraph
- **Market Data**: CoinGecko trending coins and market info
- **Community Sentiment**: CryptoPanic with voting system
- **AI Analysis**: ChainGPT AI-powered insights (when available)

### **💰 Rich Cryptocurrency Fundamentals**
- **Real-time Pricing**: Current prices in USD, BTC, and ETH
- **Market Metrics**: Market cap, volume, supply, rankings
- **Performance Data**: 1h, 24h, 7d, 30d, 1y price changes
- **Historical Data**: All-time highs/lows with dates
- **Trending Analysis**: Hot coins with fundamentals
- **Market Overview**: Global statistics and top performers

## 🚀 **Quick Start**

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2. Environment Setup**
```bash
# Copy and configure environment variables
cp env_example.txt .env

# Optional: Add API keys for enhanced functionality
OPENAI_API_KEY=your_openai_key_here
CHAINGPT_API_KEY=your_chaingpt_key_here
```

### **3. Run the Application**
```bash
python main.py
```

### **4. Test the System**
```bash
# Test basic functionality
python test_simple_mcp.py

# Test enhanced MCP integration with RSS fallbacks
python test_enhanced_mcp.py

# Test fundamentals fetcher agent
python test_fundamentals.py

# Test full MCP system
python test_mcp.py
```

## 📡 **API Endpoints**

### **Core Endpoints**
- `GET /ping` - Health check
- `GET /` - Root endpoint
- `GET /chat` - LangChain + OpenAI chat
- `GET /models` - Available models

### **News Ingestion**
- `GET /fetch_news` - Fetch news from traditional sources
- `GET /sources` - Get news source statistics
- `POST /add_source` - Add new RSS or API news source
- `GET /news/sources` - List configured news sources
- `GET /news/health` - News system health check

### **MCP Integration + RSS Fallbacks**
- `GET /mcp/news` - Fetch news from all MCP servers and RSS sources
- `GET /mcp/status` - Get status of all news sources
- `GET /mcp/health` - MCP system health check
- `POST /mcp/server/priority` - Change source priority
- `GET /mcp/servers` - List all available news sources

### **🆕 Cryptocurrency Fundamentals**
- `GET /fundamentals/{symbol}` - Get fundamentals for a specific cryptocurrency
- `POST /fundamentals/multiple` - Get fundamentals for multiple cryptocurrencies
- `GET /fundamentals/trending` - Get trending coins with fundamentals
- `GET /fundamentals/market/overview` - Get overall market overview and statistics
- `GET /fundamentals/search/{query}` - Search for coins by name or symbol

## 🏗️ **Architecture**

### **News Source Hierarchy**
```
📰 News Sources
├── 🔴 RSS Sources (High Priority - Always Available)
│   ├── CoinDesk RSS
│   └── CoinTelegraph RSS
├── 🟡 Free API Sources (Medium Priority)
│   ├── CoinGecko (trending coins, market data)
│   └── CryptoPanic (community sentiment)
└── 🟢 Premium API Sources (Low Priority - Requires API Key)
    └── ChainGPT AI News
```

### **🆕 Fundamentals Data Flow**
```
CoinGecko API → Rate Limiting → Data Fetching → Data Normalization → Fundamentals Object
     ↓
Multiple Endpoints → Concurrent Fetching → Error Handling → Unified Response Format
```

### **Fallback Strategy**
1. **Primary**: RSS sources (CoinDesk, CoinTelegraph)
2. **Secondary**: Free API sources (CoinGecko, CryptoPanic)
3. **Tertiary**: Premium sources (ChainGPT if API key available)
4. **Automatic**: Smart fallback activation when sources fail

### **Data Flow**
```
RSS Feeds → HTML Cleaning → Content Parsing → News Items
    ↓
API Sources → Data Normalization → Sentiment Analysis → News Items
    ↓
MCP Manager → Deduplication → Relevance Scoring → Unified Output
    ↓
🆕 Fundamentals Agent → Market Data → Price Analysis → Cryptocurrency Insights
```

## 🧪 **Testing**

### **Test Scripts**
- `test_setup.py` - Verify project setup
- `test_ingestion.py` - Test news ingestion pipeline
- `test_simple_mcp.py` - Basic MCP functionality
- `test_enhanced_mcp.py` - RSS fallbacks and enhanced features
- `test_mcp.py` - Full MCP integration testing
- **🆕 `test_fundamentals.py`** - Fundamentals Fetcher Agent testing

### **Test Scenarios**
1. **No API Keys**: Verify RSS fallbacks work
2. **Partial API Keys**: Test mixed source functionality
3. **Full API Keys**: Test complete system
4. **Source Failures**: Test fallback activation
5. **Performance**: Test concurrent news fetching
6. **🆕 Fundamentals**: Test cryptocurrency data fetching
7. **🆕 Rate Limiting**: Test CoinGecko API compliance

## 🔧 **Configuration**

### **News Sources**
```python
# RSS Sources (configured in MCPManager)
"coindesk": RSSNewsSource("CoinDesk", "https://www.coindesk.com/arc/outboundfeeds/rss/")
"cointelegraph": RSSNewsSource("CoinTelegraph", "https://cointelegraph.com/rss")

# API Sources
"chaingpt": ChainGPTAINewsMCPServer()  # Requires CHAINGPT_API_KEY
"coin": CoinMCPServer()                # Free, always available
"cryptopanic": CryptoPanicMCPServer()  # Free tier
```

### **🆕 Fundamentals Configuration**
```python
# Fundamentals Fetcher Agent
agent = FundamentalsFetcherAgent()
agent.rate_limit_delay = 1.2  # CoinGecko free tier: 50 calls/minute

# Available endpoints
GET /fundamentals/BTC          # Single coin
POST /fundamentals/multiple    # Multiple coins
GET /fundamentals/trending     # Trending coins
GET /fundamentals/market/overview  # Market overview
```

### **System Settings**
- **Health Check Interval**: 5 minutes
- **Concurrency**: Async fetching from multiple sources
- **Deduplication**: Similarity-based duplicate removal
- **Relevance Scoring**: Time-based + content-based scoring
- **🆕 Rate Limiting**: CoinGecko API compliance (1.2s between requests)

## 🚀 **Usage Examples**

### **Fetch News Without API Keys**
```bash
curl http://localhost:8000/mcp/news
# Returns news from RSS sources (CoinDesk, CoinTelegraph)
# + Free API sources (CoinGecko, CryptoPanic)
```

### **Check Source Status**
```bash
curl http://localhost:8000/mcp/status
# Shows active/fallback sources and their health
```

### **🆕 Get Cryptocurrency Fundamentals**
```bash
# Get Bitcoin fundamentals
curl http://localhost:8000/fundamentals/BTC

# Get multiple coins
curl -X POST "http://localhost:8000/fundamentals/multiple" \
  -H "Content-Type: application/json" \
  -d '["BTC", "ETH", "ADA", "DOT"]'

# Get trending coins
curl http://localhost:8000/fundamentals/trending?limit=10

# Get market overview
curl http://localhost:8000/fundamentals/market/overview

# Search for coins
curl http://localhost:8000/fundamentals/search/bitcoin
```

### **Add Custom RSS Source**
```bash
curl -X POST http://localhost:8000/add_source \
  -H "Content-Type: application/json" \
  -d '{"name": "Custom Crypto News", "url": "https://example.com/rss", "type": "rss"}'
```

## 🔒 **Security & Best Practices**

### **API Key Management**
- Store keys in `.env` file (not in code)
- Use environment variables for sensitive data
- Implement rate limiting for API calls
- Monitor API usage and costs

### **Data Validation**
- Pydantic models for request/response validation
- HTML sanitization for RSS content
- Input validation for all endpoints
- Error handling for malformed data

### **🆕 Rate Limiting**
- CoinGecko API compliance (50 calls/minute)
- Automatic rate limiting with configurable delays
- Graceful handling of rate limit errors
- Retry mechanisms for failed requests

## 📊 **Monitoring & Health**

### **Health Checks**
- **System Health**: `/ping` endpoint
- **News System**: `/news/health` endpoint
- **MCP System**: `/mcp/health` endpoint
- **Source Status**: `/mcp/status` endpoint

### **🆕 Fundamentals Monitoring**
- **API Health**: Automatic CoinGecko API health checking
- **Rate Limit Monitoring**: Request timing and compliance
- **Error Tracking**: Failed requests and retry attempts
- **Performance Metrics**: Response times and success rates

### **Logging**
- Structured logging with different levels
- Source health monitoring
- Error tracking and reporting
- Performance metrics

## 🔮 **Future Enhancements**

### **Planned Features**
- **WebSocket Support**: Real-time news updates
- **Caching Layer**: Redis integration for performance
- **Advanced Analytics**: News sentiment trends
- **Custom Alerts**: Price and news notifications
- **Mobile App**: React Native companion app

### **🆕 Fundamentals Enhancements**
- **Price Alerts**: Custom price threshold notifications
- **Portfolio Tracking**: Multi-coin portfolio management
- **Technical Analysis**: Moving averages, RSI, MACD indicators
- **Correlation Analysis**: News sentiment vs. price correlation
- **Predictive Models**: AI-powered price prediction

### **Extensibility**
- **Plugin System**: Easy addition of new news sources
- **Custom Parsers**: Support for new data formats
- **AI Models**: Integration with other LLM providers
- **Database**: Persistent storage for news history
- **🆕 Exchange Integration**: Multiple exchange APIs (Binance, Coinbase, etc.)

## 🤝 **Contributing**

### **Development Setup**
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### **Code Standards**
- Follow PEP 8 style guidelines
- Add type hints for all functions
- Include docstrings for classes and methods
- Write comprehensive tests

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 **Acknowledgments**

- **FastAPI** for the modern web framework
- **LangChain** for AI/LLM orchestration
- **CoinDesk & CoinTelegraph** for reliable RSS feeds
- **CoinGecko & CryptoPanic** for free API access
- **ChainGPT** for AI-powered news insights
- **🆕 CoinGecko** for comprehensive cryptocurrency data

---

**🎉 Ready to revolutionize crypto news ingestion and fundamentals analysis with AI-powered intelligence and reliable RSS fallbacks!**
