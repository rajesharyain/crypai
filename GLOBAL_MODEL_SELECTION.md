# Global AI Model Selection for AI Finance Assistant

## Overview

The AI Finance Assistant now supports **global AI model selection** across all agents, allowing you to choose between **OpenAI GPT-3.5** and **DeepSeek AI** for consistent AI operations throughout the entire pipeline.

## Features

### 🎯 Global Model Control
- **Single Control Point**: Switch all agents to the same AI model from one location
- **Consistent Experience**: All agents use the same AI model for unified results
- **Real-time Updates**: See the current model status for each agent in real-time
- **Fallback Support**: Automatic fallback to keyword-based analysis when AI models are unavailable

### 🤖 Supported Agents
The following agents now support model switching:

1. **📰 News Ingestion Agent** (`NewsIngestionAgent`)
   - Crypto symbol extraction
   - News categorization and relevance scoring
   - Content analysis and enhancement

2. **🔍 News Analysis Agent** (`AnalyzerAgent`)
   - Sentiment analysis
   - Fundamental impact assessment
   - Market sentiment evaluation
   - Risk and opportunity identification

3. **💰 Fundamentals Agent** (`FundamentalsFetcherAgent`)
   - Market data analysis
   - Price trend evaluation
   - Technical indicator interpretation

4. **📝 Post Creation Agent** (`PostCreatorAgent`)
   - Social media content generation
   - Platform-specific post optimization
   - Engagement-focused content creation

5. **🏷️ News Categorization Agent** (`CategorizeAgent`)
   - Crypto relevance determination
   - News classification and tagging
   - Content filtering and prioritization

## 🚀 How to Use

### 1. Main Dashboard (`/ui`)
- **Location**: Top section above the pipeline controls
- **Features**: 
  - Global model dropdown selection
  - Real-time agent model status display
  - One-click model switching for all agents

### 2. Pipeline Control (`/pipeline-control`)
- **Location**: Dedicated "Global AI Model Configuration" section
- **Features**:
  - Global model selection with detailed status
  - Individual agent model status grid
  - Comprehensive model management controls

### 3. API Endpoints
- **`GET /agents/model-info`**: Get current model status for all agents
- **`POST /agents/switch-model`**: Switch a specific agent's model
- **`GET /news/categorization/model-info`**: Get categorization agent model info
- **`POST /news/categorization/switch-model`**: Switch categorization agent model

## 🔧 Configuration

### Environment Variables
```bash
# Global AI model for all agents (default: openai)
AI_MODEL_TYPE=openai

# Categorization agent model (can be different from global)
CATEGORIZATION_MODEL=openai

# OpenAI API configuration
OPENAI_API_KEY=your_openai_api_key_here

# DeepSeek AI configuration
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

### Model Initialization Priority
1. **Environment Variable**: `AI_MODEL_TYPE` sets the default for all agents
2. **Individual Override**: `CATEGORIZATION_MODEL` can override for categorization
3. **Runtime Switching**: Use UI or API to switch models at runtime

## 🎨 User Interface

### Main Dashboard
```
🤖 Global AI Model Configuration
├── Global AI Model: [OpenAI GPT-3.5 ▼]
├── Current: OPENAI
└── Agent Status Grid:
    ├── 📰 Ingestion: OPENAI
    ├── 🔍 Analysis: OPENAI
    ├── 💰 Fundamentals: OPENAI
    └── 📝 Posts: OPENAI
```

### Pipeline Control
```
🤖 Global AI Model Configuration
├── Global AI Model: [OpenAI GPT-3.5 ▼]
├── Current: OPENAI
└── Model Status Grid:
    ├── 📰 News Ingestion: OPENAI
    ├── 🔍 News Analysis: OPENAI
    ├── 💰 Fundamentals: OPENAI
    ├── 📝 Post Creation: OPENAI
    └── 🏷️ News Categorization: OPENAI
```

## 🔄 Model Switching Process

### 1. User Selection
- User selects new model from dropdown
- System validates API key availability
- UI shows loading state during switch

### 2. Agent Updates
- System iterates through all agents
- Calls `/agents/switch-model` for each agent
- Updates agent's internal model configuration
- Reinitializes LLM connections if needed

### 3. Status Verification
- System reloads model information
- Updates UI status displays
- Shows success/partial success messages
- Handles errors gracefully

### 4. Fallback Handling
- If model switch fails, agent falls back to previous model
- System continues operating with available models
- User is notified of partial success

## 🧪 Testing

### Test Script
Run the comprehensive test script to verify functionality:
```bash
python test_global_model_switching.py
```

### Manual Testing
1. **Start the server**: `python main.py`
2. **Open main UI**: Navigate to `http://localhost:8000/ui`
3. **Switch models**: Use the global model dropdown
4. **Verify status**: Check agent status displays update
5. **Test pipeline**: Run a pipeline to ensure models are working

## 🚨 Error Handling

### API Key Issues
- **Missing API Key**: Model option is disabled in UI
- **Invalid API Key**: Error message displayed to user
- **Rate Limit Exceeded**: Automatic fallback to keyword analysis

### Network Issues
- **Connection Timeout**: Retry mechanism with exponential backoff
- **Service Unavailable**: Graceful degradation to fallback methods
- **Partial Failures**: Continue with successfully switched agents

### Fallback Mechanisms
- **Keyword Analysis**: Rule-based content analysis
- **Regex Extraction**: Pattern-based crypto symbol detection
- **Template Generation**: Pre-defined content templates

## 📊 Monitoring and Observability

### Model Usage Tracking
- **Model Selection History**: Track which models were used when
- **Performance Metrics**: Compare response times between models
- **Error Rates**: Monitor failure rates for each model type
- **Cost Analysis**: Track API usage and costs per model

### Health Checks
- **API Availability**: Monitor OpenAI and DeepSeek API health
- **Response Quality**: Compare output quality between models
- **Fallback Usage**: Track when fallback mechanisms are activated

## 🔮 Future Enhancements

### Planned Features
1. **Model Performance Comparison**: Side-by-side output comparison
2. **Automatic Model Selection**: AI-powered model selection based on task
3. **Hybrid Model Usage**: Combine multiple models for optimal results
4. **Custom Model Integration**: Support for additional AI providers
5. **Model Fine-tuning**: Custom model training for specific use cases

### Integration Possibilities
1. **Anthropic Claude**: High-quality reasoning and analysis
2. **Google Gemini**: Multimodal content understanding
3. **Local Models**: Privacy-focused local AI processing
4. **Specialized Models**: Domain-specific AI models for finance

## 🛠️ Technical Implementation

### Code Structure
```
main.py
├── Global model endpoints
├── Agent initialization with model_type
└── Model switching logic

agents/
├── analyzer.py - Model switching methods
├── post_creator.py - Model switching methods
├── ingestion.py - Model switching methods
├── fundamentals.py - Model switching methods
└── categorize_agent.py - Model switching methods

templates/
├── index.html - Main UI with global model selection
└── pipeline_control.html - Pipeline control with model management
```

### Key Methods
- `switch_model(model_type)`: Switch agent to specified model
- `get_current_model()`: Get currently active model
- `get_available_models()`: Get list of available models
- `_initialize_llm()`: Initialize language model based on type

## 📝 Usage Examples

### Switch All Agents to DeepSeek AI
```bash
curl -X POST "http://localhost:8000/agents/switch-model" \
  -H "Content-Type: application/json" \
  -d '{"agent_type": "ingestion", "model_type": "deepseek"}'
```

### Get Current Model Status
```bash
curl "http://localhost:8000/agents/model-info"
```

### Switch Specific Agent
```bash
curl -X POST "http://localhost:8000/agents/switch-model" \
  -H "Content-Type: application/json" \
  -d '{"agent_type": "analysis", "model_type": "deepseek"}'
```

## 🎯 Best Practices

### Model Selection
1. **OpenAI GPT-3.5**: Best for general analysis and content generation
2. **DeepSeek AI**: Excellent for technical analysis and specialized tasks
3. **Fallback**: Use when API limits are reached or services are unavailable

### Performance Optimization
1. **Batch Operations**: Switch models during low-usage periods
2. **Cache Management**: Clear agent caches after model switches
3. **Error Handling**: Implement retry logic for failed switches
4. **Monitoring**: Track model performance and usage patterns

### Security Considerations
1. **API Key Management**: Secure storage and rotation of API keys
2. **Rate Limiting**: Implement proper rate limiting for model switches
3. **Access Control**: Restrict model switching to authorized users
4. **Audit Logging**: Log all model switches for compliance

## 🆘 Troubleshooting

### Common Issues
1. **Model Not Switching**: Check API key configuration and availability
2. **Partial Updates**: Verify all agents support the selected model
3. **UI Not Updating**: Refresh page or check browser console for errors
4. **Performance Degradation**: Monitor API response times and error rates

### Debug Commands
```bash
# Check server logs for model switching
tail -f server.log | grep "model"

# Verify API endpoints
curl "http://localhost:8000/agents/model-info"

# Test individual agent switching
curl -X POST "http://localhost:8000/agents/switch-model" \
  -H "Content-Type: application/json" \
  -d '{"agent_type": "categorization", "model_type": "deepseek"}'
```

---

## 🎉 Summary

The Global AI Model Selection feature provides:

✅ **Unified Control**: Single interface to manage all AI models  
✅ **Flexibility**: Choose between OpenAI and DeepSeek AI  
✅ **Real-time Status**: See current model for each agent  
✅ **Fallback Support**: Graceful degradation when AI services fail  
✅ **Easy Testing**: Comprehensive test scripts and documentation  
✅ **Future Ready**: Extensible architecture for new AI providers  

This enhancement makes the AI Finance Assistant more robust, flexible, and user-friendly while maintaining high-quality AI-powered analysis and content generation capabilities.
