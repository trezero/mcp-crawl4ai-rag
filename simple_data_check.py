#!/usr/bin/env python3
"""
Simple data verification script that checks available tables and data
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    supabase_url = os.getenv("SUPABASE_URL", "http://localhost:8101")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_key:
        print("❌ SUPABASE_SERVICE_KEY not found")
        return
    
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        print(f"✅ Connected to Supabase at {supabase_url}")
        
        # Check crawled_pages table
        print("\n📊 CRAWLED PAGES DATA:")
        pages = supabase.table("crawled_pages").select("url, content, metadata, source_id, created_at, chunk_number").execute()
        
        if pages.data:
            print(f"   Total pages: {len(pages.data)}")
            
            # Show sample of recent pages
            print("\n   Recent pages:")
            for i, page in enumerate(pages.data[-5:]):  # Last 5 pages
                url = page.get('url', 'No URL')[:60]
                source_id = page.get('source_id', 'No Source')[:30]
                content_len = len(page.get('content', ''))
                chunk_num = page.get('chunk_number', 0)
                created = page.get('created_at', 'Unknown')[:19]
                print(f"   {i+1}. {url}")
                print(f"      Source: {source_id}")
                print(f"      Chunk: {chunk_num}, Content: {content_len} chars")
                print(f"      Created: {created}")
                print()
            
            # Content quality analysis
            content_lengths = [len(page.get('content', '')) for page in pages.data]
            avg_length = sum(content_lengths) / len(content_lengths)
            min_length = min(content_lengths)
            max_length = max(content_lengths)
            
            print(f"   Content Statistics:")
            print(f"     Average length: {avg_length:.0f} chars")
            print(f"     Range: {min_length} - {max_length} chars")
            
            # Check for quality issues
            empty_content = sum(1 for length in content_lengths if length == 0)
            short_content = sum(1 for length in content_lengths if 0 < length < 100)
            
            print(f"     Empty content: {empty_content}")
            print(f"     Short content (<100 chars): {short_content}")
            print(f"     Quality score: {((len(pages.data) - empty_content - short_content) / len(pages.data)) * 100:.1f}%")
            
        else:
            print("   No pages found")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
