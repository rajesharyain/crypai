# AI Finance Assistant MVP

A Quick Lean MVP built with **FastAPI + LangChain** for AI-powered financial insights and assistance.

## 🚀 Features

- **FastAPI Backend**: Modern, fast web framework for building APIs
- **LangChain Integration**: AI/LLM orchestration framework
- **OpenAI Integration**: GPT models for intelligent responses
- **Health Monitoring**: Built-in health check endpoints
- **API Documentation**: Automatic OpenAPI/Swagger docs
- **CORS Support**: Cross-origin resource sharing enabled

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key
- pip (Python package manager)

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

# Edit .env and add your OpenAI API key
OPENAI_API_KEY=your_actual_openai_api_key_here
```

### 4. Run the Application
```bash
# Option 1: Direct Python execution
python main.py

# Option 2: Using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🌐 API Endpoints

### Health Check
- **GET** `/ping` - Health status endpoint
- **GET** `/` - Root endpoint with project info

### AI Chat
- **POST** `/chat` - Chat with AI using LangChain
- **GET** `/models` - List available OpenAI models

### Documentation
- **GET** `/docs` - Interactive API documentation (Swagger UI)
- **GET** `/redoc` - Alternative API documentation

## 📱 Usage Examples

### Health Check
```bash
curl http://localhost:8000/ping
```
Response:
```json
{
  "status": "ok",
  "message": "AI Finance Assistant is running!"
}
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

### Get Available Models
```bash
curl http://localhost:8000/models
```

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENAI_MODEL`: Default model to use (optional, default: gpt-3.5-turbo)
- `TEMPERATURE`: AI response creativity (optional, default: 0.7)

### Customization
You can modify the following in `main.py`:
- Model parameters (temperature, max_tokens)
- CORS settings
- Logging configuration
- Additional endpoints

## 🏗️ Project Structure

```
ai-proj/
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
├── env_example.txt     # Environment variables template
├── README.md           # This file
└── .env                # Your environment variables (create this)
```

## 🚀 Development

### Running in Development Mode
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Adding New Features
1. Add new endpoints in `main.py`
2. Update requirements.txt if adding new packages
3. Test endpoints using the interactive docs at `/docs`

## 🔒 Security Notes

- Never commit your `.env` file to version control
- Keep your OpenAI API key secure
- Consider implementing rate limiting for production use
- Add authentication for production deployments

## 📊 Monitoring

The application includes:
- Health check endpoint for monitoring
- Structured logging
- Error handling with proper HTTP status codes

## 🤝 Contributing

This is an MVP - feel free to extend with:
- Database integration
- User authentication
- Rate limiting
- More sophisticated LangChain chains
- Financial data APIs integration
- WebSocket support for real-time chat

## 📄 License

This project is for educational and MVP purposes.

---

**Built with ❤️ using FastAPI + LangChain**
