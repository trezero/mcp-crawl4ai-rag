#!/usr/bin/env python3
import asyncio
import os
import sys
from urllib.parse import urlparse
from supabase import create_client, Client
from openai import OpenAI
import json

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def main():
    print("🚀 DataCore Documentation Recovery - Direct Crawl")
    print("=" * 50)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Initialize clients
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not all([supabase_url, supabase_key, openai_key]):
        print("❌ Missing required environment variables")
        return
    
    supabase: Client = create_client(supabase_url, supabase_key)
    openai_client = OpenAI(api_key=openai_key)
    
    print("✅ Clients initialized")
    
    # Import crawl4ai components
    try:
        from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
        print("✅ Crawl4AI imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import crawl4ai: {e}")
        return
    
    # Initialize crawler
    browser_config = BrowserConfig(
        headless=True,
        verbose=False
    )
    
    crawl_config = CrawlerRunConfig(
        word_count_threshold=10,
        cache_mode=CacheMode.BYPASS,
        chunking_strategy="by_headers"
    )
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        print("✅ Crawler initialized")
        
        # Crawl the DataCore documentation main page first
        url = "https://docs.datacore.com/SSV-WebHelp/"
        print(f"\n🌐 Crawling main page: {url}")
        
        try:
            result = await crawler.arun(
                url=url,
                config=crawl_config
            )
            
            if result.success:
                print(f"✅ Successfully crawled main page: {len(result.extracted_content)} characters")
                
                # Process and store content
                content = result.extracted_content
                if not content:
                    content = result.cleaned_html
                
                # Create chunks
                chunks = []
                chunk_size = 3000
                for i in range(0, len(content), chunk_size):
                    chunk = content[i:i + chunk_size]
                    if chunk.strip():
                        chunks.append({
                            'content': chunk,
                            'chunk_number': len(chunks),
                            'url': url
                        })
                
                print(f"📄 Created {len(chunks)} chunks from main page")
                
                # Try to find additional pages by looking for common documentation patterns
                additional_urls = [
                    "https://docs.datacore.com/SSV-WebHelp/Content/Getting_Started/Getting_Started.htm",
                    "https://docs.datacore.com/SSV-WebHelp/Content/Installation/Installation.htm",
                    "https://docs.datacore.com/SSV-WebHelp/Content/Configuration/Configuration.htm",
                    "https://docs.datacore.com/SSV-WebHelp/Content/Administration/Administration.htm",
                    "https://docs.datacore.com/SSV-WebHelp/Content/Troubleshooting/Troubleshooting.htm"
                ]
                
                # Crawl additional pages
                for add_url in additional_urls:
                    try:
                        print(f"🌐 Crawling: {add_url}")
                        add_result = await crawler.arun(
                            url=add_url,
                            config=crawl_config
                        )
                        
                        if add_result.success and add_result.extracted_content:
                            add_content = add_result.extracted_content
                            for i in range(0, len(add_content), chunk_size):
                                chunk = add_content[i:i + chunk_size]
                                if chunk.strip():
                                    chunks.append({
                                        'content': chunk,
                                        'chunk_number': len(chunks),
                                        'url': add_url
                                    })
                            print(f"  ✅ Added content from {add_url}")
                        else:
                            print(f"  ⚠️  No content from {add_url}")
                    except Exception as e:
                        print(f"  ❌ Error crawling {add_url}: {e}")
                        continue
                
                print(f"📄 Total chunks created: {len(chunks)}")
                
                # Generate embeddings and store
                source_id = "docs.datacore.com"
                stored_count = 0
                
                # Clear existing data for this source
                try:
                    supabase.table('crawled_pages').delete().eq('source_id', source_id).execute()
                    print("🧹 Cleared existing DataCore data")
                except Exception as e:
                    print(f"⚠️  Error clearing existing data: {e}")
                
                for chunk_data in chunks:
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
                                'description': 'DataCore SANsymphony storage management documentation',
                                'word_count': len(chunk_data['content'].split())
                            }
                        }).execute()
                        
                        stored_count += 1
                        if stored_count % 5 == 0:
                            print(f"📊 Stored {stored_count}/{len(chunks)} chunks")
                            
                    except Exception as e:
                        print(f"⚠️  Error storing chunk {chunk_data['chunk_number']}: {e}")
                        continue
                
                print(f"✅ Successfully stored {stored_count} chunks")
                
                # Update or create source record
                try:
                    supabase.table('sources').upsert({
                        'source_id': source_id,
                        'summary': f"DataCore SANsymphony documentation - {stored_count} chunks recovered",
                        'total_word_count': sum(len(chunk['content'].split()) for chunk in chunks)
                    }).execute()
                    print("✅ Source record updated")
                except Exception as e:
                    print(f"⚠️  Error updating source: {e}")
                
                # Test query
                print("\n🔍 Testing RAG query...")
                try:
                    query = "DataCore SANsymphony storage management"
                    query_embedding = openai_client.embeddings.create(
                        model="text-embedding-ada-002",
                        input=query
                    ).data[0].embedding
                    
                    results = supabase.rpc('match_crawled_pages', {
                        'query_embedding': query_embedding,
                        'match_count': 3,
                        'source_filter': source_id
                    }).execute()
                    
                    if results.data:
                        print(f"✅ Query successful - found {len(results.data)} results")
                        for i, result in enumerate(results.data[:2]):
                            print(f"  {i+1}. Similarity: {result['similarity']:.3f}")
                            print(f"     Content: {result['content'][:100]}...")
                    else:
                        print("⚠️  No results found")
                        
                except Exception as e:
                    print(f"❌ Query test failed: {e}")
                
            else:
                print(f"❌ Crawl failed: {result.error_message}")
                
        except Exception as e:
            print(f"❌ Crawl error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n🎉 DataCore documentation recovery completed!")
    print(f"📊 Final stats: {stored_count} chunks stored")
    print("🔗 Oracle RightNow platform ready for intelligent responses")

if __name__ == "__main__":
    asyncio.run(main())
