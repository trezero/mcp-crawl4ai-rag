#!/usr/bin/env python3
import asyncio
import os
import sys
from supabase import create_client, Client
from openai import OpenAI

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def main():
    print("🔍 DataCore Documentation Debug Crawl")
    print("=" * 40)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Initialize clients
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    supabase: Client = create_client(supabase_url, supabase_key)
    openai_client = OpenAI(api_key=openai_key)
    
    # Import crawl4ai components
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
    
    # Initialize crawler
    browser_config = BrowserConfig(headless=True)
    crawl_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        # Test with main page
        url = "https://docs.datacore.com/SSV-WebHelp/"
        print(f"🌐 Testing crawl: {url}")
        
        result = await crawler.arun(url=url, config=crawl_config)
        
        print(f"Success: {result.success}")
        print(f"Status Code: {result.status_code}")
        print(f"Error: {result.error_message}")
        print(f"Extracted Content Length: {len(result.extracted_content) if result.extracted_content else 0}")
        print(f"Cleaned HTML Length: {len(result.cleaned_html) if result.cleaned_html else 0}")
        print(f"Raw HTML Length: {len(result.html) if result.html else 0}")
        
        # Try to use any available content
        content = None
        if result.extracted_content:
            content = result.extracted_content
            print("Using extracted_content")
        elif result.cleaned_html:
            content = result.cleaned_html
            print("Using cleaned_html")
        elif result.html:
            content = result.html
            print("Using raw html")
        
        if content:
            print(f"Content preview (first 500 chars):")
            print("-" * 50)
            print(content[:500])
            print("-" * 50)
            
            # If we have content, let's store it
            if len(content.strip()) > 100:
                print("\n📄 Processing content for storage...")
                
                # Simple chunking
                chunks = []
                chunk_size = 3000
                for i in range(0, len(content), chunk_size):
                    chunk = content[i:i + chunk_size]
                    if len(chunk.strip()) > 100:
                        chunks.append({
                            'content': chunk,
                            'url': url,
                            'chunk_number': len(chunks)
                        })
                
                print(f"Created {len(chunks)} chunks")
                
                # Store first few chunks as test
                source_id = "docs.datacore.com"
                stored_count = 0
                
                # Clear existing data
                try:
                    supabase.table('crawled_pages').delete().eq('source_id', source_id).execute()
                    print("🧹 Cleared existing data")
                except:
                    pass
                
                # Store up to 5 chunks for testing
                for chunk_data in chunks[:5]:
                    try:
                        # Generate embedding
                        embedding_response = openai_client.embeddings.create(
                            model="text-embedding-ada-002",
                            input=chunk_data['content']
                        )
                        embedding = embedding_response.data[0].embedding
                        
                        # Store in Supabase
                        supabase.table('crawled_pages').insert({
                            'url': chunk_data['url'],
                            'chunk_number': chunk_data['chunk_number'],
                            'content': chunk_data['content'],
                            'source_id': source_id,
                            'embedding': embedding,
                            'metadata': {
                                'title': 'DataCore SANsymphony Documentation',
                                'description': 'DataCore documentation test',
                                'word_count': len(chunk_data['content'].split())
                            }
                        }).execute()
                        
                        stored_count += 1
                        print(f"✅ Stored chunk {stored_count}")
                        
                    except Exception as e:
                        print(f"❌ Error storing chunk: {e}")
                        continue
                
                # Update source
                try:
                    supabase.table('sources').upsert({
                        'source_id': source_id,
                        'summary': f"DataCore SANsymphony documentation - {stored_count} test chunks",
                        'total_word_count': sum(len(chunk['content'].split()) for chunk in chunks[:5])
                    }).execute()
                    print("✅ Source record updated")
                except Exception as e:
                    print(f"⚠️  Error updating source: {e}")
                
                # Test query
                print("\n🔍 Testing RAG query...")
                try:
                    query = "DataCore storage"
                    query_embedding = openai_client.embeddings.create(
                        model="text-embedding-ada-002",
                        input=query
                    ).data[0].embedding
                    
                    results = supabase.rpc('match_crawled_pages', {
                        'query_embedding': query_embedding,
                        'match_count': 2,
                        'source_filter': source_id
                    }).execute()
                    
                    if results.data:
                        print(f"✅ Found {len(results.data)} results")
                        for i, result in enumerate(results.data):
                            print(f"  {i+1}. Similarity: {result['similarity']:.3f}")
                            print(f"     Content: {result['content'][:100]}...")
                    else:
                        print("⚠️  No results found")
                        
                except Exception as e:
                    print(f"❌ Query failed: {e}")
                
                print(f"\n🎉 Debug crawl completed! Stored {stored_count} chunks")
            else:
                print("❌ Content too short to process")
        else:
            print("❌ No content found")

if __name__ == "__main__":
    asyncio.run(main())
