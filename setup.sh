#!/bin/bash

echo "=== MCP Crawl4AI RAG Setup ==="
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create one based on .env.example"
    exit 1
fi

# Check if required environment variables are set
source .env

if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
    echo "❌ Please set your OPENAI_API_KEY in .env file"
    echo "   Get your key from: https://platform.openai.com/api-keys"
    exit 1
fi

if [ -z "$SUPABASE_URL" ] || [ "$SUPABASE_URL" = "your_supabase_project_url" ]; then
    echo "⚠️  SUPABASE_URL not configured. You can either:"
    echo "   1. Set up Supabase at https://supabase.com/"
    echo "   2. Use local PostgreSQL with: docker-compose up -d"
    echo ""
    read -p "Use local PostgreSQL + Neo4j? (y/n): " use_local
    if [ "$use_local" = "y" ]; then
        echo "Starting local PostgreSQL + Neo4j..."
        docker-compose up -d
        echo "✅ Local services started:"
        echo "   - PostgreSQL on port 5433"
        echo "   - Neo4j on ports 7474 (HTTP) and 7687 (Bolt)"
        echo "   Update your .env with:"
        echo "   SUPABASE_URL=postgresql://postgres:postgres@localhost:5433/crawl4ai_rag"
        echo "   SUPABASE_SERVICE_KEY=postgres"
        echo ""
        echo "   Neo4j Browser: http://localhost:7474"
        echo "   Neo4j credentials: neo4j / crawl4ai_password"
    fi
fi

echo ""
echo "✅ Setup complete! You can now:"
echo "   1. Start the server: ./start-server.sh"
echo "   2. Or use it via Kiro CLI MCP integration"
echo ""
