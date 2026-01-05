# YouTube Transcript RAG System

A working prototype that downloads YouTube transcripts, stores them in a vector database, and enables RAG (Retrieval Augmented Generation) queries.

## Features

- 📥 Download YouTube video transcripts automatically
- 💾 Store transcripts in ChromaDB vector database with embeddings
- 🔍 Query transcripts using semantic search (RAG)
- 🌐 Modern React web UI for browsing and viewing transcripts
- 🐳 Fully dockerized with Docker Compose
- 🚀 Fast setup and lightweight dependencies

## Demo

Watch a demo of the application in action:

![Demo](demo/TranscriptViewer-optimized.gif)

The demo shows:
- Adding a YouTube video URL
- Browsing downloaded videos
- Viewing full transcripts
- Modern, responsive UI

📹 **[Full Demo Video](demo/TranscriptViewer.webm)** (Click to download/view in your browser)

## Quick Start

### Option A: Docker (Recommended)

The easiest way to run the application is using Docker:

```bash
# Build and start all services
make build
make up

# View logs
make logs

# Stop services
make down
```

**Access Points:**
- Frontend UI: http://localhost:3000
- API Server: http://localhost:5001/api
- Health Check: http://localhost:5001/api/health

**Available Make Commands:**
- `make build` - Build all Docker images
- `make up` - Start all services in detached mode
- `make down` - Stop all services
- `make logs` - Follow logs from all services
- `make ps` - Show running containers
- `make restart` - Restart all services
- `make rebuild` - Clean, build, and start
- `make rebuild-backend` - Rebuild only backend
- `make rebuild-frontend` - Rebuild only frontend
- `make rebuild-backend-clean` - Rebuild backend without cache
- `make rebuild-frontend-clean` - Rebuild frontend without cache
- `make clean` - Remove local images
- `make clean-all` - Remove all images and volumes

For more Docker details, see [DOCKER.md](DOCKER.md).

### Option B: Local Development

### 1. Install uv (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Or with pip:

```bash
pip install uv
```

### 2. Install Dependencies

```bash
uv sync
```

This will create a virtual environment and install all dependencies automatically.

**Note for Intel macOS users:** If you encounter torch installation errors, PyTorch 2.8.0+ doesn't support Intel Macs. Install torch separately first:

```bash
uv pip install torch==2.2.2 torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
uv sync
```

### 3. Add a YouTube Video

```bash
uv run python -m goodanalysis.main add "https://www.youtube.com/watch?v=VIDEO_ID"
```

Or just use the video ID:

```bash
uv run python -m goodanalysis.main add "VIDEO_ID"
```

Alternatively, after `uv sync`, you can use the installed command:

```bash
goodanalysis add "VIDEO_ID"
```

### 4. Set Up OpenAI API Key (Required for Default)

The system uses OpenAI by default. Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys):

```bash
export OPENAI_API_KEY="your-api-key-here"
```

Or add it to your shell profile (`~/.zshrc` or `~/.bashrc`):

```bash
echo 'export OPENAI_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

### 5. Query the Transcripts

```bash
# Using OpenAI for answer generation (default)
uv run python -m goodanalysis.main query "What is the main topic discussed?"

# Using a specific OpenAI model
uv run python -m goodanalysis.main query "Your question" --model gpt-4o

# No LLM (simple retrieval only - embeddings still use local model)
uv run python -m goodanalysis.main query "Your question" --llm none
```

Or use the installed command:

```bash
goodanalysis query "What is the main topic discussed?"
```

### 6. List All Videos

```bash
uv run python -m goodanalysis.main list
```

Or use the installed command:

```bash
goodanalysis list
```

### 7. View Transcripts

View the full transcript for any video without using RAG:

```bash
# View transcript in terminal
uv run python -m goodanalysis.main view "VIDEO_ID"

# Save transcript to a file
uv run python -m goodanalysis.main view "VIDEO_ID" --save transcript.txt
```

Or use the installed command:

```bash
goodanalysis view "VIDEO_ID"
goodanalysis view "VIDEO_ID" --save transcript.txt
```

### 8. Web UI (Local Development)

Start the web UI to browse videos and transcripts in your browser:

```bash
# Start web UI (Flask templates)
uv run python -m goodanalysis.main web

# Start API server (for React frontend)
uv run python -m goodanalysis.main api
```

Then open http://127.0.0.1:5000 in your browser.

**Note:** For production, use Docker (see Option A above) which includes the React frontend.

## How It Works

1. **Transcript Download**: Uses `youtube-transcript-api` to fetch video transcripts
2. **Vector Storage**:
   - Chunks transcripts and stores them in ChromaDB
   - **Embeddings use local model** (`sentence-transformers` with `all-MiniLM-L6-v2`) - runs locally, no API calls
3. **RAG Query**:
   - **Retrieval**: Uses local embeddings to find relevant chunks via semantic search (cosine similarity)
   - **Generation**: Uses OpenAI to generate answers from retrieved context (requires API key)
   - Falls back to simple retrieval if OpenAI is not configured

## Project Structure

```
goodanalysis/
├── goodanalysis/           # Package directory
│   ├── __init__.py
│   ├── main.py            # Main CLI application
│   ├── api_server.py      # REST API server (for React frontend)
│   ├── web_ui.py          # Flask web UI (legacy)
│   ├── transcript_downloader.py # YouTube transcript download logic
│   ├── vector_store.py    # ChromaDB integration
│   └── rag_system.py      # RAG query system
├── frontend/              # React frontend
│   ├── src/              # React source code
│   ├── public/           # Static files
│   └── Dockerfile        # Frontend Docker image
├── pyproject.toml         # Project configuration and dependencies (uv)
├── Dockerfile             # Backend Docker image
├── docker-compose.yml     # Docker orchestration
├── Makefile              # Convenience commands
└── chroma_db/            # Vector database (created automatically)
```

## Example Usage

```bash
# Add a video about Python programming
uv run python -m goodanalysis.main add "https://www.youtube.com/watch?v=kqtD5dpn9C8"

# Query about what was discussed
uv run python -m goodanalysis.main query "What are the key concepts explained?"

# Add another video
uv run python -m goodanalysis.main add "https://www.youtube.com/watch?v=another_video_id"

# Query across all videos
uv run python -m goodanalysis.main query "What is machine learning?"
```

**Note:** After `uv sync`, you can also use the installed `goodanalysis` command directly:

```bash
goodanalysis add "VIDEO_ID"
goodanalysis query "Your question"
goodanalysis list
```

## Architecture

The system uses a **hybrid approach** for optimal performance and cost:

- **Embeddings (Local)**: Uses `sentence-transformers` with `all-MiniLM-L6-v2` model

  - Runs entirely locally, no API calls
  - Fast and free for semantic search
  - Used for finding relevant transcript chunks

- **Answer Generation (OpenAI)**: Uses OpenAI GPT models
  - Only called after relevant chunks are retrieved
  - Generates coherent answers from context
  - Requires API key (costs apply per query)

## LLM Configuration

1. **OpenAI** (Default, Recommended)

   - High-quality answers with GPT models
   - Requires API key (set `OPENAI_API_KEY` environment variable)
   - Get API key: https://platform.openai.com/api-keys
   - Default model: `gpt-4o-mini` (fast and cost-effective)
   - Supported models: `gpt-4o-mini`, `gpt-4o`, `gpt-3.5-turbo`, etc.
   - Usage: `uv run python -m goodanalysis.main query "question"` (default)
   - Usage with specific model: `uv run python -m goodanalysis.main query "question" --model gpt-4o`
   - Or: `goodanalysis query "question"` (after installation)

2. **None** (Simple Retrieval Only)
   - No LLM for answer generation, just returns relevant chunks
   - Embeddings still use local model
   - Usage: `uv run python -m goodanalysis.main query "question" --llm none`

## Notes

- **Embeddings**: Always uses local `all-MiniLM-L6-v2` model (no API calls, free, fast)
- **Answer Generation**: Uses OpenAI (requires API key, costs apply)
- **Chunking**: Transcripts are automatically chunked (500 chars, 50 char overlap) for better retrieval
- **Vector DB**: ChromaDB persists data in the `chroma_db/` directory
- **Cost**: Only OpenAI API calls cost money - embeddings are free and local

## Requirements

### For Docker:
- Docker and Docker Compose
- Internet connection for downloading transcripts

### For Local Development:
- Python 3.8+
- Node.js 18+ (for React frontend development)
- Internet connection for downloading transcripts
- YouTube videos must have captions/subtitles enabled
