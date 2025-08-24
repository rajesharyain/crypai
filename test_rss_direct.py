#!/usr/bin/env python3
"""
Direct test of RSS parsing for CoinDesk
"""

import feedparser
from bs4 import BeautifulSoup

def test_coindesk_rss_direct():
    """Test CoinDesk RSS parsing directly"""
    print("Testing CoinDesk RSS parsing directly...")
    
    # Parse the RSS feed
    feed = feedparser.parse('https://www.coindesk.com/arc/outboundfeeds/rss/')
    
    if not feed.entries:
        print("No entries found in RSS feed")
        return
    
    print(f"Found {len(feed.entries)} entries")
    print("=" * 80)
    
    # Test first 3 entries
    for i, entry in enumerate(feed.entries[:3], 1):
        print(f"\n{i}. Title: {getattr(entry, 'title', 'No Title')}")
        
        # Check all available fields
        print(f"   Available fields: {[attr for attr in dir(entry) if not attr.startswith('_')]}")
        
        # Test our parsing logic
        title = getattr(entry, 'title', 'No Title')
        
        # Handle CoinDesk specifically - it uses 'content' field instead of 'summary'
        content = getattr(entry, 'content', [])
        if content and isinstance(content, list) and len(content) > 0:
            # Extract the HTML content from the first content item
            html_content = content[0].get('value', '')
            if html_content:
                soup = BeautifulSoup(html_content, 'html.parser')
                summary = soup.get_text()[:300]  # Limit summary length
                print(f"   ✅ Summary extracted: {summary[:100]}...")
            else:
                summary = 'No Summary'
                print(f"   ❌ No HTML content value")
        else:
            summary = 'No Summary'
            print(f"   ❌ No content field or empty content")
        
        print(f"   Link: {getattr(entry, 'link', '')}")
        print("-" * 80)

if __name__ == "__main__":
    test_coindesk_rss_direct()
