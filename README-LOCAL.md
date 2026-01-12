# MCP Crawl4AI RAG - Local Installation

This is a local installation of the mcp-crawl4ai-rag application within the Oracle RightNow Testing project.

## Quick Start

1. **Configure Environment**:
   ```bash
   cd mcp-crawl4ai-rag
   cp .env.example .env
   # Edit .env with your API keys
   ```

2. **Required Configuration**:
   - `OPENAI_API_KEY`: Get from https://platform.openai.com/api-keys
   - `SUPABASE_URL` and `SUPABASE_SERVICE_KEY`: Either use Supabase or local PostgreSQL

3. **Setup**:
   ```bash
   ./setup.sh
   ```

4. **Start Server**:
   ```bash
   ./start-server.sh
   ```

## Database Options

### Option 1: Supabase (Cloud)
1. Create account at https://supabase.com/
2. Create new project
3. Get URL and service key from project settings
4. Run the SQL from `crawled_pages.sql` in Supabase SQL editor

### Option 2: Local PostgreSQL + Neo4j (Full Setup)
1. Start local services:
   ```bash
   docker compose up -d
   ```
2. Update .env:
   ```
   SUPABASE_URL=postgresql://postgres:postgres@localhost:5433/crawl4ai_rag
   SUPABASE_SERVICE_KEY=postgres
   ```
3. Neo4j Browser: http://localhost:7474 (neo4j / crawl4ai_password)

## Features Enabled

- ✅ Advanced web crawling and RAG
- ✅ Contextual embeddings for enhanced retrieval
- ✅ Hybrid search (vector + keyword)
- ✅ Agentic RAG for code examples
- ✅ Result reranking with cross-encoder
- ✅ **Neo4j knowledge graph functionality**
- ✅ **AI hallucination detection**
- ✅ **GitHub repository analysis**

## Integration with Kiro CLI

The MCP server is already configured in `.kiro/settings/mcp.json`. After setup, you can use it directly in Kiro CLI:

```bash
kiro-cli
> crawl_single_page https://example.com
> perform_rag_query "search for information about..."
```

## Troubleshooting

- **Port conflicts**: The server uses port 8051. Check if it's available.
- **Database connection**: Ensure PostgreSQL is running and accessible.
- **API keys**: Verify OpenAI API key is valid and has credits.

## Files

- `start-server.sh`: Start the MCP server
- `setup.sh`: Initial setup and configuration check
- `docker-compose.yml`: Local PostgreSQL with pgvector
- `.env`: Configuration (create from .env.example)
