from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Finance Assistant MVP",
    description="Quick Lean MVP with LangChain + FastAPI for AI-powered financial insights",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    model: str = "gpt-3.5-turbo"

class ChatResponse(BaseModel):
    response: str
    model_used: str

# Health check endpoint
@app.get("/ping")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "AI Finance Assistant is running!"}

@app.get("/")
async def root():
    """Root endpoint with project information"""
    return {
        "message": "AI Finance Assistant MVP",
        "version": "1.0.0",
        "endpoints": {
            "health": "/ping",
            "chat": "/chat",
            "docs": "/docs"
        }
    }

# Chat endpoint using LangChain
@app.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """Chat with AI using LangChain and OpenAI"""
    try:
        # Get OpenAI API key
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        # Initialize LangChain chat model
        llm = ChatOpenAI(
            model=request.model,
            openai_api_key=openai_api_key,
            temperature=0.7
        )
        
        # Create message and get response
        messages = [HumanMessage(content=request.message)]
        response = llm.invoke(messages)
        
        logger.info(f"Chat request processed successfully with model: {request.model}")
        
        return ChatResponse(
            response=response.content,
            model_used=request.model
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")

# Additional utility endpoints
@app.get("/models")
async def get_available_models():
    """Get available OpenAI models"""
    return {
        "models": [
            "gpt-3.5-turbo",
            "gpt-4",
            "gpt-4-turbo-preview"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
