# AI Finance Assistant MVP

A Quick Lean MVP built with **FastAPI + LangChain** for AI-powered financial insights, **automated news ingestion**, and **MCP server integration**.

## 🚀 Features

- **FastAPI Backend**: Modern, fast web framework for building APIs
- **LangChain Integration**: AI/LLM orchestration framework with intelligent agents
- **OpenAI Integration**: GPT models for intelligent responses and sentiment analysis
- **News Ingestion Agent**: Automated crypto news collection from multiple sources
- **MCP Server Integration**: ChainGPT AI News, Coin, and CryptoPanic MCP servers
- **Multi-Source Support**: RSS feeds + API integrations + MCP servers
- **Sentiment Analysis**: AI-powered news sentiment and relevance scoring
- **Health Monitoring**: Built-in health check endpoints for all systems
- **API Documentation**: Automatic OpenAPI/Swagger docs
- **CORS Support**: Cross-origin resource sharing enabled
- **Extensible Architecture**: Easy to add new news sources, MCP servers, and providers

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key
- pip (Python package manager)
- Optional: ChainGPT API key for enhanced MCP functionality

## 🛠️ Installation & Setup

### 1. Clone and Navigate to Project
```bash
cd ai-proj
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the project root:
```bash
# Copy the example file
cp env_example.txt .env

# Edit .env and add your API keys
OPENAI_API_KEY=your_actual_openai_api_key_here

# Optional: Crypto News API Keys (for enhanced news sources)
CRYPTO_NEWS_API_KEY=your_crypto_news_api_key_here
TOKEN_METRICS_API_KEY=your_token_metrics_api_key_here
COINFEEDS_API_KEY=your_coinfeeds_api_key_here

# Optional: MCP Server API Keys (for enhanced MCP integration)
CHAINGPT_API_KEY=your_chaingpt_api_key_here
```

### 4. Run the Application
```bash
# Option 1: Direct Python execution
python main.py

# Option 2: Using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🌐 API Endpoints

### Core Endpoints
- **GET** `/ping` - Health status endpoint
- **GET** `/` - Root endpoint with project info
- **POST** `/chat` - Chat with AI using LangChain
- **GET** `/models` - List available OpenAI models

### News Ingestion Endpoints
- **GET** `/fetch_news` - Fetch latest news from traditional sources
- **GET** `/sources` - Get news source statistics
- **POST** `/add_source` - Add new news source dynamically
- **GET** `/news/sources` - List all configured news sources
- **GET** `/news/health` - Health check for news ingestion system

### MCP Server Endpoints
- **GET** `/mcp/news` - Fetch news from MCP servers (ChainGPT, Coin, CryptoPanic)
- **GET** `/mcp/status` - Get status of all MCP servers
- **GET** `/mcp/health` - Health check for MCP server system
- **POST** `/mcp/server/priority` - Change server priority between active/fallback
- **GET** `/mcp/servers` - List all available MCP servers with details

### Documentation
- **GET** `/docs` - Interactive API documentation (Swagger UI)
- **GET** `/redoc` - Alternative API documentation

## 📰 News Ingestion Systems

### 🔍 **Traditional News Sources**
- **RSS Feeds**: CoinDesk, CoinTelegraph, CryptoNews, Bitcoin Magazine, Decrypt, NewsBTC, AMBCrypto
- **API Sources**: Crypto News API, Token Metrics API, CoinFeeds API (when keys provided)
- **Extensible**: Easy to add new sources via configuration or API

### 🤖 **MCP Server Integration**
The system includes **Model Context Protocol (MCP)** servers for enhanced news intelligence:

#### **ChainGPT AI News MCP Server**
- **AI-Generated News**: Intelligent crypto news analysis and generation
- **Sentiment Analysis**: Built-in sentiment classification
- **Entity Recognition**: Automatic identification of key crypto entities
- **Requires**: API key (optional - falls back to other sources)

#### **Coin MCP Server (CoinGecko Integration)**
- **Trending Coins**: Real-time trending cryptocurrency data
- **Market Data**: Current prices, market cap, 24h changes
- **Free Tier**: Always available, no API key required
- **Fallback**: Primary source when other MCP servers are unavailable

#### **CryptoPanic MCP Server**
- **Community-Driven**: User-voted crypto news and sentiment
- **Vote-Based Sentiment**: Positive/negative sentiment from community votes
- **Free Tier**: Available without API key
- **Real-Time**: Live updates from crypto community

### 🧠 **AI-Powered Analysis**
- **Sentiment Analysis**: Positive/Negative/Neutral classification
- **Relevance Scoring**: 0-10 scale for financial market impact
- **Entity Recognition**: Key companies, cryptocurrencies, and events
- **Market Impact Assessment**: Potential effects on trading

### ⚡ **Performance Features**
- **Concurrent Fetching**: Multiple sources processed simultaneously
- **Smart Fallback**: Automatic switching between active and fallback servers
- **Duplicate Detection**: Smart similarity-based deduplication
- **Rate Limiting**: Respects API limits and RSS feed constraints
- **Health Monitoring**: Continuous server health checks

## 📱 Usage Examples

### Health Check
```bash
curl http://localhost:8000/ping
```

### Fetch Traditional News
```bash
# Basic news fetch
curl http://localhost:8000/fetch_news

# With sentiment analysis
curl "http://localhost:8000/fetch_news?include_sentiment=true&limit=20"
```

### Fetch MCP News
```bash
# Fetch from all MCP servers
curl http://localhost:8000/mcp/news

# Limit results
curl "http://localhost:8000/mcp/news?limit=10"
```

### MCP Server Management
```bash
# Get MCP server status
curl http://localhost:8000/mcp/status

# Health check MCP servers
curl http://localhost:8000/mcp/health

# List all MCP servers
curl http://localhost:8000/mcp/servers

# Change server priority
curl -X POST "http://localhost:8000/mcp/server/priority" \
     -H "Content-Type: application/json" \
     -d '{
       "server_name": "chaingpt",
       "priority": "fallback"
     }'
```

### Add New News Source
```bash
# Add RSS source
curl -X POST "http://localhost:8000/add_source" \
     -H "Content-Type: application/json" \
     -d '{
       "source_type": "rss",
       "url": "https://example.com/feed",
       "name": "New Source",
       "category": "crypto"
     }'
```

### Get Source Statistics
```bash
curl http://localhost:8000/sources
```

### Chat with AI
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "What are the key principles of value investing?",
       "model": "gpt-3.5-turbo"
     }'
```

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `CRYPTO_NEWS_API_KEY`: Crypto News API key (optional)
- `TOKEN_METRICS_API_KEY`: Token Metrics API key (optional)
- `COINFEEDS_API_KEY`: CoinFeeds API key (optional)
- `CHAINGPT_API_KEY`: ChainGPT API key (optional)

### System Settings
The system is highly configurable via `config.py`:
- **Concurrency**: Control simultaneous source fetching
- **Rate Limiting**: Adjust delays between API calls
- **Duplicate Detection**: Configure similarity thresholds
- **Batch Processing**: Set sentiment analysis batch sizes
- **Caching**: Configure cache durations and behavior

### MCP Server Configuration
MCP servers are automatically configured with intelligent fallback:
- **Active Servers**: Primary sources for news fetching
- **Fallback Servers**: Secondary sources when primary servers fail
- **Health Monitoring**: Automatic server status checking
- **Priority Switching**: Dynamic server priority management

### Adding New Sources
```python
# Via configuration file
from config import get_news_config

config = get_news_config()
config.add_rss_source(
    url="https://newsource.com/feed",
    name="New Source",
    category="crypto",
    max_items=25
)

# Via API endpoint
POST /add_source
```

## 🏗️ Project Structure

```
ai-proj/
├── main.py              # FastAPI application with news and MCP endpoints
├── ingestion.py         # News ingestion agent and source classes
├── mcp_integration.py   # MCP server integration and management
├── config.py            # Configuration management for news sources
├── requirements.txt     # Python dependencies
├── env_example.txt      # Environment variables template
├── test_ingestion.py    # Test suite for ingestion agent
├── test_mcp.py          # Test suite for MCP integration
├── README.md            # This file
└── .env                 # Your environment variables (create this)
```

## 🧪 Testing

### Test the Ingestion Agent
```bash
python test_ingestion.py
```

### Test the MCP Integration
```bash
python test_mcp.py
```

### Test the API
```bash
# Test setup
python test_setup.py

# Test individual endpoints
curl http://localhost:8000/fetch_news
curl http://localhost:8000/mcp/news
curl http://localhost:8000/sources
```

## 🚀 Development

### Running in Development Mode
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Adding New Features
1. **New News Sources**: Add to `config.py` or use the `/add_source` endpoint
2. **New MCP Servers**: Extend the `MCPServer` class in `mcp_integration.py`
3. **Custom Analysis**: Extend the LangChain tools in `ingestion.py`
4. **New Endpoints**: Add to `main.py` following the existing pattern
5. **Configuration**: Modify `config.py` for system-wide settings

### Architecture Highlights
- **Modular Design**: Separate concerns for ingestion, MCP, configuration, and API
- **Async Processing**: Non-blocking news fetching and analysis
- **Intelligent Fallback**: Automatic switching between active and fallback servers
- **Error Handling**: Graceful degradation when sources are unavailable
- **Extensibility**: Easy to add new news providers, MCP servers, and analysis tools

## 🔒 Security Notes

- Never commit your `.env` file to version control
- Keep your API keys secure
- Consider implementing rate limiting for production use
- Add authentication for production deployments
- Validate RSS feed URLs before adding them
- MCP servers use secure HTTPS connections

## 📊 Monitoring

The application includes comprehensive monitoring:
- **Health Checks**: `/ping`, `/news/health`, and `/mcp/health` endpoints
- **Source Statistics**: Detailed metrics on all news sources
- **MCP Server Status**: Real-time status of all MCP servers
- **Performance Metrics**: Fetch times and success rates
- **Error Logging**: Structured logging for debugging
- **Source Health**: Individual source availability monitoring

## 🤝 Contributing

This MVP is designed for easy extension:

### **Immediate Enhancements**
- Database integration for news storage
- User authentication and personalization
- Advanced sentiment analysis chains
- Real-time news alerts via WebSockets
- Additional MCP server integrations

### **Future Integrations**
- More crypto news APIs and MCP servers
- Social media sentiment analysis
- Price correlation analysis with news
- Automated trading signals
- News impact prediction models
- Advanced MCP server orchestration

## 📄 License

This project is for educational and MVP purposes.

---

**Built with ❤️ using FastAPI + LangChain + Intelligent News Ingestion + MCP Server Integration**
