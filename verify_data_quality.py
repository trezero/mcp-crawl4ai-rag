#!/usr/bin/env python3
"""
Data Quality Verification Script for Crawl4AI MCP Server
Checks the integrity and quality of scraped website data
"""

import asyncio
import os
from datetime import datetime, timedelta
from supabase import create_client, Client
import json

async def verify_data_quality():
    """Verify the quality and integrity of scraped data"""
    
    # Load environment variables
    supabase_url = os.getenv("SUPABASE_URL", "http://localhost:8101")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_key:
        print("❌ SUPABASE_SERVICE_KEY not found in environment")
        return
    
    try:
        # Initialize Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        print(f"✅ Connected to Supabase at {supabase_url}")
        
        # Check recent data (last 24 hours)
        yesterday = datetime.now() - timedelta(days=1)
        
        print("\n🔍 DATA QUALITY VERIFICATION")
        print("=" * 50)
        
        # 1. Check crawled_pages table
        print("\n📄 CRAWLED PAGES ANALYSIS:")
        pages_response = supabase.table("crawled_pages").select("*").execute()
        
        if pages_response.data:
            total_pages = len(pages_response.data)
            print(f"   Total pages: {total_pages}")
            
            # Analyze content quality
            empty_content = 0
            short_content = 0
            good_content = 0
            
            for page in pages_response.data:
                content_length = len(page.get('content', ''))
                if content_length == 0:
                    empty_content += 1
                elif content_length < 100:
                    short_content += 1
                else:
                    good_content += 1
            
            print(f"   Empty content: {empty_content}")
            print(f"   Short content (<100 chars): {short_content}")
            print(f"   Good content (≥100 chars): {good_content}")
            print(f"   Quality score: {(good_content/total_pages)*100:.1f}%")
            
            # Show recent pages
            recent_pages = [p for p in pages_response.data if p.get('created_at')]
            if recent_pages:
                print(f"   Most recent page: {recent_pages[-1].get('url', 'Unknown')}")
        else:
            print("   No pages found in database")
        
        # 2. Check page_chunks table
        print("\n🧩 PAGE CHUNKS ANALYSIS:")
        chunks_response = supabase.table("page_chunks").select("*").execute()
        
        if chunks_response.data:
            total_chunks = len(chunks_response.data)
            print(f"   Total chunks: {total_chunks}")
            
            # Analyze chunk quality
            chunk_sizes = [len(chunk.get('content', '')) for chunk in chunks_response.data]
            if chunk_sizes:
                avg_size = sum(chunk_sizes) / len(chunk_sizes)
                min_size = min(chunk_sizes)
                max_size = max(chunk_sizes)
                
                print(f"   Average chunk size: {avg_size:.0f} chars")
                print(f"   Size range: {min_size} - {max_size} chars")
                
                # Check for embeddings
                with_embeddings = sum(1 for chunk in chunks_response.data if chunk.get('embedding'))
                print(f"   Chunks with embeddings: {with_embeddings}/{total_chunks}")
                print(f"   Embedding coverage: {(with_embeddings/total_chunks)*100:.1f}%")
        else:
            print("   No chunks found in database")
        
        # 3. Check code_examples table (if agentic RAG is enabled)
        print("\n💻 CODE EXAMPLES ANALYSIS:")
        try:
            code_response = supabase.table("code_examples").select("*").execute()
            if code_response.data:
                total_examples = len(code_response.data)
                print(f"   Total code examples: {total_examples}")
                
                # Analyze code quality
                with_summaries = sum(1 for ex in code_response.data if ex.get('summary'))
                print(f"   Examples with summaries: {with_summaries}/{total_examples}")
                
                # Language distribution
                languages = {}
                for ex in code_response.data:
                    lang = ex.get('language', 'unknown')
                    languages[lang] = languages.get(lang, 0) + 1
                
                print("   Language distribution:")
                for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True):
                    print(f"     {lang}: {count}")
            else:
                print("   No code examples found")
        except Exception as e:
            print(f"   Code examples table not accessible: {str(e)}")
        
        # 4. Data integrity checks
        print("\n🔒 DATA INTEGRITY CHECKS:")
        
        # Check for duplicate URLs
        if pages_response.data:
            urls = [page.get('url') for page in pages_response.data]
            unique_urls = set(urls)
            duplicates = len(urls) - len(unique_urls)
            print(f"   Duplicate URLs: {duplicates}")
            
            # Check for missing required fields
            missing_title = sum(1 for page in pages_response.data if not page.get('title'))
            missing_content = sum(1 for page in pages_response.data if not page.get('content'))
            
            print(f"   Pages missing title: {missing_title}")
            print(f"   Pages missing content: {missing_content}")
        
        # 5. Recent activity summary
        print("\n📊 RECENT ACTIVITY SUMMARY:")
        if pages_response.data:
            # Try to parse timestamps and find recent activity
            recent_count = 0
            for page in pages_response.data:
                created_at = page.get('created_at')
                if created_at:
                    try:
                        # Parse ISO timestamp
                        page_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        if page_time > yesterday:
                            recent_count += 1
                    except:
                        pass
            
            print(f"   Pages crawled in last 24h: {recent_count}")
        
        print("\n✅ Data quality verification completed!")
        
    except Exception as e:
        print(f"❌ Error connecting to database: {str(e)}")
        print("   Make sure Supabase is running and accessible")

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    asyncio.run(verify_data_quality())
