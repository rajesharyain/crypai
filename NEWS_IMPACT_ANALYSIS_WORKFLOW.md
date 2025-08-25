# News Impact Analysis Workflow

## Overview

The News Impact Analysis Workflow is a new orchestration system that provides comprehensive analysis of cryptocurrency news for trading decision-making. It uses DeepSeek AI (with OpenAI fallback) to analyze news impact, sentiment, and trading implications.

## Workflow Architecture

### 1. **Fetch News & Cache** 📰
- Fetches news from selected sources (RSS feeds, APIs)
- Stores news in `fetched_news_cache` for further processing
- Supports source selection and crypto-focused filtering

### 2. **Analyze News Impact** 🔍
- Uses DeepSeek AI to analyze each news item
- Determines market impact, sentiment, and trading implications
- Extracts affected cryptocurrencies and sectors
- Assesses risk levels and provides recommendations

### 3. **Generate Insights** 📊
- Creates structured JSON output for human decision making
- Provides trading insights and recommendations
- Generates summary statistics and risk assessments

## Key Components

### NewsImpactAnalysisAgent
- **Purpose**: Analyzes news for market impact and trading implications
- **AI Models**: DeepSeek AI (primary), OpenAI (fallback)
- **Output**: Structured analysis with confidence scores

### NewsImpactOrchestrator
- **Purpose**: Manages the complete workflow execution
- **Features**: Workflow history, status tracking, error handling
- **Integration**: Works with existing news ingestion agents

## API Endpoints

### Core Workflow
- `POST /news-impact/workflow` - Run the complete workflow
- `GET /news-impact/workflow/status` - Get workflow status
- `GET /news-impact/workflow/history` - Get workflow history
- `POST /news-impact/workflow/clear-history` - Clear workflow history

### Agent Management
- `GET /news-impact/agent/status` - Get agent status
- `POST /news-impact/agent/switch-model` - Switch AI model

### Global Model Management
- `POST /agents/switch-model` - Switch model for any agent (including news_impact)
- `GET /agents/model-info` - Get model information for all agents

## Data Structures

### NewsImpactAnalysis
```json
{
  "news_id": "string",
  "title": "string",
  "source": "string",
  "published_date": "string",
  "analysis_timestamp": "string",
  
  "market_impact": "High|Medium|Low",
  "sentiment": "Bullish|Bearish|Neutral",
  "confidence_score": 0.0-1.0,
  
  "affected_cryptos": [
    {
      "symbol": "BTC",
      "name": "Bitcoin",
      "impact_level": "High|Medium|Low",
      "expected_movement": "Up|Down|Sideways"
    }
  ],
  "affected_sectors": ["DeFi", "Layer2", "NFTs"],
  
  "expected_price_movement": "Up|Down|Sideways",
  "volatility_impact": "High|Medium|Low",
  "time_horizon": "Immediate|Short-term|Long-term",
  
  "risk_level": "High|Medium|Low",
  "risk_factors": ["Regulatory uncertainty", "Market volatility"],
  
  "trading_recommendation": "Buy|Sell|Hold|Wait",
  "position_sizing": "Large|Medium|Small",
  "stop_loss_considerations": "string",
  
  "key_topics": ["Regulation", "ETF approval"],
  "market_context": "string",
  "related_events": ["Upcoming SEC decisions"]
}
```

### Workflow Result
```json
{
  "workflow_id": "string",
  "workflow_status": "completed|failed",
  "execution_time": 0.0,
  "timestamp": "string",
  
  "fetched_news_count": 0,
  "analyzed_news_count": 0,
  "fetched_news_cache": [...],
  "impact_analyses": [...],
  
  "sentiment_summary": {"Bullish": 3, "Bearish": 1, "Neutral": 1},
  "impact_summary": {"High": 2, "Medium": 2, "Low": 1},
  "risk_summary": {"High": 1, "Medium": 3, "Low": 1},
  
  "trading_insights": {
    "trading_recommendations": {"Buy": 2, "Hold": 2, "Wait": 1},
    "position_sizing_distribution": {"Medium": 3, "Small": 2},
    "affected_cryptos": ["BTC", "ETH", "SUI"],
    "affected_sectors": ["DeFi", "Layer2"],
    "high_impact_news": [...]
  }
}
```

## Usage Examples

### Running the Workflow
```bash
curl -X POST "http://localhost:8000/news-impact/workflow" \
  -H "Content-Type: application/json" \
  -d '{
    "sources": ["coindesk", "cointelegraph"],
    "news_limit": 10,
    "crypto_focus": true
  }'
```

### Switching AI Model
```bash
curl -X POST "http://localhost:8000/news-impact/agent/switch-model" \
  -H "Content-Type: application/json" \
  -d '{"model_type": "deepseek"}'
```

### Getting Workflow Status
```bash
curl "http://localhost:8000/news-impact/workflow/status"
```

## UI Integration

### Pipeline Control Interface
- New "News Impact Analysis" section in `/pipeline-control`
- Visual workflow steps with 3-step process
- Purple-themed UI elements for distinction
- Real-time status updates and results display

### Results Display
- **Summary Cards**: Workflow ID, news counts, execution time
- **Statistics Grid**: Sentiment, impact, and risk distributions
- **Trading Insights**: Affected assets, recommendations, high-impact news
- **Detailed Analyses**: Individual news item analysis with structured data

## Configuration

### Environment Variables
```bash
# DeepSeek AI Configuration
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com

# AI Model Selection
AI_MODEL_TYPE=deepseek  # or openai
```

### Model Selection
- **Global**: Set `AI_MODEL_TYPE` environment variable
- **Per-Agent**: Use `/agents/switch-model` endpoint
- **Runtime**: Switch models during operation

## Benefits

### For Traders
- **Actionable Insights**: Clear buy/sell/hold recommendations
- **Risk Assessment**: Comprehensive risk factor analysis
- **Market Context**: Understanding of news impact on specific assets
- **Confidence Scoring**: AI-powered confidence in analysis

### For Developers
- **Structured Output**: Consistent JSON format for integration
- **Caching System**: Efficient news storage and retrieval
- **Error Handling**: Robust fallback mechanisms
- **Extensible Architecture**: Easy to add new analysis types

## Testing

### Test Script
Run the comprehensive test script:
```bash
python test_news_impact_workflow.py
```

### Manual Testing
1. Start the server: `python main.py`
2. Navigate to `/pipeline-control`
3. Select news sources
4. Click "Run Impact Analysis"
5. Review results and insights

## Future Enhancements

### Planned Features
- **Real-time Updates**: Live news monitoring and analysis
- **Portfolio Integration**: Connect to trading platforms
- **Advanced Analytics**: Historical impact analysis and trends
- **Custom Models**: User-defined analysis criteria

### Integration Opportunities
- **Trading Bots**: Automated trading based on news analysis
- **Risk Management**: Portfolio risk assessment tools
- **Research Platforms**: Academic and institutional research
- **Media Monitoring**: Brand and market sentiment tracking

## Troubleshooting

### Common Issues
1. **DeepSeek API Errors**: Check API key and base URL
2. **Model Switching Failures**: Verify environment variables
3. **Workflow Timeouts**: Increase timeout for large news batches
4. **Memory Issues**: Monitor cache sizes and clear if needed

### Debug Information
- Check `/news-impact/agent/status` for agent health
- Review `/news-impact/workflow/history` for execution logs
- Monitor server logs for detailed error information

## Support

For issues or questions:
1. Check the server logs for error details
2. Verify environment variable configuration
3. Test individual endpoints for specific failures
4. Review the test script for working examples
