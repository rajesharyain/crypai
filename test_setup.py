#!/usr/bin/env python3
"""
Test script to verify the project setup and dependencies.
Run this to check if everything is configured correctly.
"""

def test_imports():
    """Test if all required packages can be imported"""
    try:
        print("Testing imports...")
        
        import fastapi
        print(f"✅ FastAPI imported successfully (version: {fastapi.__version__})")
        
        import uvicorn
        print(f"✅ Uvicorn imported successfully")
        
        import langchain
        print(f"✅ LangChain imported successfully (version: {langchain.__version__})")
        
        import langchain_openai
        print(f"✅ LangChain OpenAI imported successfully")
        
        import feedparser
        print(f"✅ Feedparser imported successfully")
        
        import requests
        print(f"✅ Requests imported successfully (version: {requests.__version__})")
        
        import dotenv
        print(f"✅ Python-dotenv imported successfully")
        
        import pydantic
        print(f"✅ Pydantic imported successfully (version: {pydantic.__version__})")
        
        print("\n🎉 All imports successful! Your environment is ready.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install missing dependencies with: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_env_loading():
    """Test environment variable loading"""
    try:
        from dotenv import load_dotenv
        import os
        
        print("\nTesting environment loading...")
        load_dotenv()
        
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            print("✅ OpenAI API key found in environment")
        else:
            print("⚠️  OpenAI API key not found. Please create a .env file with OPENAI_API_KEY")
            print("   Copy env_example.txt to .env and add your actual API key")
        
        return True
        
    except Exception as e:
        print(f"❌ Environment loading error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing AI Finance Assistant MVP Setup")
    print("=" * 50)
    
    imports_ok = test_imports()
    env_ok = test_env_loading()
    
    print("\n" + "=" * 50)
    if imports_ok and env_ok:
        print("🎯 Setup looks good! You can now run the application with:")
        print("   python main.py")
        print("   or")
        print("   uvicorn main:app --reload")
    else:
        print("⚠️  Some issues found. Please resolve them before running the application.")
    
    print("\n📚 Check README.md for detailed setup instructions.")

if __name__ == "__main__":
    main()
