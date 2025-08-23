#!/usr/bin/env python3
"""
Demo script for the AI Finance Assistant Web UI
Shows how to use the orchestrator dashboard
"""

import webbrowser
import time
import subprocess
import sys
import os

def main():
    """Demo the web UI functionality"""
    print("🚀 AI Finance Assistant - Web UI Demo")
    print("=" * 60)
    
    # Check if the server is running
    try:
        import requests
        response = requests.get("http://localhost:8000/ping", timeout=3)
        if response.status_code != 200:
            raise Exception("Server not responding")
        print("✅ Server is running on http://localhost:8000")
    except Exception as e:
        print("❌ Server is not running. Please start it first:")
        print("   python main.py")
        return
    
    print("\n🎯 Available Features:")
    print("   📊 Real-time pipeline status tracking")
    print("   📰 Top 3 latest news processing (optimized for API limits)")
    print("   🔍 AI-powered sentiment analysis")
    print("   💰 SUI cryptocurrency fundamentals")
    print("   📱 Social media post generation (Twitter, LinkedIn, Telegram)")
    print("   📋 One-click copy buttons for each platform")
    
    print("\n🌐 Opening Web UI in your browser...")
    print("   URL: http://localhost:8000/ui")
    
    # Open the UI in the default browser
    try:
        webbrowser.open("http://localhost:8000/ui")
        print("✅ Web UI opened successfully!")
    except Exception as e:
        print(f"❌ Could not open browser: {e}")
        print("   Please manually open: http://localhost:8000/ui")
    
    print("\n📱 How to Use the Web UI:")
    print("   1. Click the '▶️ Start Orchestration' button")
    print("   2. Watch the real-time status of each agent:")
    print("      • 📰 News Ingestion (fetches top 3 latest news)")
    print("      • 🔍 News Analysis (AI sentiment analysis)")
    print("      • 💰 Fundamentals (SUI market data)")
    print("      • 📝 Post Creation (social media posts)")
    print("   3. Copy generated posts using the copy buttons")
    print("   4. Share them on your preferred platforms!")
    
    print("\n🔧 Additional API Endpoints:")
    print("   • API Documentation: http://localhost:8000/docs")
    print("   • Health Check: http://localhost:8000/ping")
    print("   • Root Info: http://localhost:8000/")
    
    print("\n💡 Pro Tips:")
    print("   • The system uses fallback analysis when OpenAI API is unavailable")
    print("   • Rate limiting is built-in to prevent API quota issues")
    print("   • News is limited to 3 items to optimize performance")
    print("   • All posts include hashtags, emojis, and engagement optimization")
    
    print("\n🎉 Enjoy using the AI Finance Assistant!")
    print("   Press Ctrl+C to stop the server when done.")

if __name__ == "__main__":
    main()
