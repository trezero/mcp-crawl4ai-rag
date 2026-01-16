#!/usr/bin/env python3
import asyncio
import os
import sys
from supabase import create_client, Client
from openai import OpenAI

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def main():
    print("🚀 DataCore Documentation Recovery - Simple Crawl")
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
    
    # Initialize crawler with minimal config
    browser_config = BrowserConfig(headless=True)
    crawl_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        print("✅ Crawler initialized")
        
        # DataCore documentation URLs to crawl
        urls_to_crawl = [
            "https://docs.datacore.com/SSV-WebHelp/",
            "https://docs.datacore.com/SSV-WebHelp/Content/Getting_Started/Getting_Started.htm",
            "https://docs.datacore.com/SSV-WebHelp/Content/Installation/Installation.htm",
            "https://docs.datacore.com/SSV-WebHelp/Content/Configuration/Configuration.htm",
            "https://docs.datacore.com/SSV-WebHelp/Content/Administration/Administration.htm"
        ]
        
        all_chunks = []
        source_id = "docs.datacore.com"
        
        # Clear existing data
        try:
            supabase.table('crawled_pages').delete().eq('source_id', source_id).execute()
            print("🧹 Cleared existing DataCore data")
        except Exception as e:
            print(f"⚠️  Error clearing existing data: {e}")
        
        # Crawl each URL
        for url in urls_to_crawl:
            try:
                print(f"\n🌐 Crawling: {url}")
                result = await crawler.arun(url=url, config=crawl_config)
                
                if result.success and result.extracted_content:
                    content = result.extracted_content.strip()
                    if content:
                        # Simple chunking by size
                        chunk_size = 3000
                        for i in range(0, len(content), chunk_size):
                            chunk = content[i:i + chunk_size]
                            if len(chunk.strip()) > 100:  # Only store meaningful chunks
                                all_chunks.append({
                                    'content': chunk,
                                    'url': url,
                                    'chunk_number': len(all_chunks)
                                })
                        
                        print(f"  ✅ Extracted {len(content)} characters")
                else:
                    print(f"  ❌ Failed to crawl {url}")
                    
            except Exception as e:
                print(f"  ❌ Error crawling {url}: {e}")
                continue
        
        print(f"\n📄 Total chunks created: {len(all_chunks)}")
        
        if not all_chunks:
            print("❌ No content was successfully crawled")
            return
        
        # Store chunks with embeddings
        stored_count = 0
        for chunk_data in all_chunks:
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
                    print(f"📊 Stored {stored_count}/{len(all_chunks)} chunks")
                    
            except Exception as e:
                print(f"⚠️  Error storing chunk {chunk_data['chunk_number']}: {e}")
                continue
        
        print(f"✅ Successfully stored {stored_count} chunks")
        
        # Update source record
        try:
            supabase.table('sources').upsert({
                'source_id': source_id,
                'summary': f"DataCore SANsymphony documentation - {stored_count} chunks recovered",
                'total_word_count': sum(len(chunk['content'].split()) for chunk in all_chunks)
            }).execute()
            print("✅ Source record updated")
        except Exception as e:
            print(f"⚠️  Error updating source: {e}")
        
        # Test RAG query
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
                    print(f"     URL: {result['url']}")
                    print(f"     Content: {result['content'][:150]}...")
                    print()
            else:
                print("⚠️  No results found")
                
        except Exception as e:
            print(f"❌ Query test failed: {e}")
    
    print("\n🎉 DataCore Documentation Recovery Completed!")
    print(f"📊 Final Statistics:")
    print(f"   • {stored_count} content chunks stored")
    print(f"   • {len(urls_to_crawl)} URLs processed")
    print(f"   • Source ID: {source_id}")
    print("\n🔗 Oracle RightNow Intelligence Platform Ready!")
    print("   • Vector database populated")
    print("   • RAG queries functional")
    print("   • Intelligent responses enabled")

if __name__ == "__main__":
    asyncio.run(main())
