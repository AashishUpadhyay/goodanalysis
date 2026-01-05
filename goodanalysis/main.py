#!/usr/bin/env python3
"""
Main application for YouTube Transcript RAG System
"""
import argparse
import sys
from typing import Optional
from goodanalysis.transcript_downloader import download_transcript, format_transcript, get_video_id_from_url
from goodanalysis.vector_store import VectorStore
from goodanalysis.rag_system import RAGSystem
from goodanalysis.web_ui import run_web_ui


def add_video(vector_store: VectorStore, video_url_or_id: str):
    """Add a YouTube video transcript to the vector store."""
    print(f"\n📥 Downloading transcript for: {video_url_or_id}")

    # Extract video ID
    video_id = get_video_id_from_url(video_url_or_id)
    print(f"Video ID: {video_id}")

    # Download transcript
    transcript = download_transcript(video_id)
    if not transcript:
        print("❌ Failed to download transcript. Make sure the video has captions enabled.")
        return False

    # Format transcript
    transcript_text = format_transcript(transcript)
    print(f"✅ Downloaded transcript ({len(transcript_text)} characters)")

    # Add to vector store
    print("💾 Storing in vector database...")
    vector_store.add_transcript(video_id, transcript_text)
    print("✅ Transcript stored successfully!")

    return True


def query_rag(rag_system: RAGSystem, question: str):
    """Query the RAG system with a question."""
    print(f"\n🔍 Searching for: {question}")
    print("-" * 60)

    result = rag_system.query(question)

    print("\n📝 Answer:")
    print(result['answer'])

    if result['sources']:
        print(f"\n📹 Sources: {', '.join(result['sources'])}")

    print("-" * 60)


def list_videos(vector_store: VectorStore):
    """List all videos in the vector store."""
    videos = vector_store.get_all_videos()
    if videos:
        print(f"\n📹 Videos in database ({len(videos)}):")
        for video_id in videos:
            print(f"  - {video_id}")
    else:
        print("\n📹 No videos in database yet.")


def view_transcript(vector_store: VectorStore, video_id: str, save_to_file: Optional[str] = None):
    """View the full transcript for a video."""
    print(f"\n📄 Retrieving transcript for video: {video_id}")

    transcript = vector_store.get_transcript(video_id)

    if not transcript:
        print(f"❌ No transcript found for video: {video_id}")
        print("   Make sure the video ID is correct and the video has been added to the database.")
        return False

    print(f"✅ Found transcript ({len(transcript)} characters)")
    print("-" * 60)
    print("\n📝 Transcript:")
    print(transcript)
    print("-" * 60)

    if save_to_file:
        try:
            with open(save_to_file, 'w', encoding='utf-8') as f:
                f.write(f"Transcript for video: {video_id}\n")
                f.write("=" * 60 + "\n\n")
                f.write(transcript)
            print(f"\n💾 Transcript saved to: {save_to_file}")
        except Exception as e:
            print(f"\n❌ Error saving transcript to file: {e}")
            return False

    return True


def main():
    parser = argparse.ArgumentParser(
        description="YouTube Transcript RAG System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add a video
  python main.py add "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  
  # Query the RAG system
  python main.py query "What is machine learning?"
  
  # List all videos
  python main.py list
  
  # View a transcript
  python main.py view "VIDEO_ID"
  python main.py view "VIDEO_ID" --save transcript.txt
  
  # Start web UI
  python main.py web
  python main.py web --port 8080
        """
    )

    subparsers = parser.add_subparsers(
        dest='command', help='Command to execute')

    # Add video command
    add_parser = subparsers.add_parser(
        'add', help='Add a YouTube video transcript')
    add_parser.add_argument('video_url', help='YouTube URL or video ID')

    # Query command
    query_parser = subparsers.add_parser('query', help='Query the RAG system')
    query_parser.add_argument('question', help='Question to ask')
    query_parser.add_argument('--llm', choices=['openai', 'none'], default='openai',
                              help='LLM provider to use (default: openai). Note: embeddings always use local model.')
    query_parser.add_argument(
        '--model', help='OpenAI model name (default: gpt-4o-mini)')

    # List command
    list_parser = subparsers.add_parser(
        'list', help='List all videos in database')

    # View transcript command
    view_parser = subparsers.add_parser(
        'view', help='View transcript for a video')
    view_parser.add_argument('video_id', help='YouTube video ID')
    view_parser.add_argument('--save', '-s', help='Save transcript to a file')

    # Web UI command
    web_parser = subparsers.add_parser(
        'web', help='Start web UI to browse videos and transcripts')
    web_parser.add_argument('--host', default='127.0.0.1',
                            help='Host to bind to (default: 127.0.0.1)')
    web_parser.add_argument('--port', type=int, default=5000,
                            help='Port to bind to (default: 5000)')
    web_parser.add_argument('--debug', action='store_true',
                            help='Enable debug mode')

    # API server command
    api_parser = subparsers.add_parser(
        'api', help='Start API server for React frontend')
    api_parser.add_argument('--host', default='127.0.0.1',
                            help='Host to bind to (default: 127.0.0.1)')
    api_parser.add_argument('--port', type=int, default=5000,
                            help='Port to bind to (default: 5000)')
    api_parser.add_argument('--debug', action='store_true',
                            help='Enable debug mode')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize vector store
    print("🚀 Initializing vector store...")
    vector_store = VectorStore()

    # Execute command
    if args.command == 'add':
        add_video(vector_store, args.video_url)
    elif args.command == 'query':
        # Initialize RAG system with LLM configuration
        llm_provider = getattr(args, 'llm', 'openai')
        model_name = getattr(args, 'model', None)
        rag_system = RAGSystem(
            vector_store, llm_provider=llm_provider, model_name=model_name)
        query_rag(rag_system, args.question)
    elif args.command == 'list':
        list_videos(vector_store)
    elif args.command == 'view':
        video_id = get_video_id_from_url(
            args.video_id)  # Support both URL and ID
        view_transcript(vector_store, video_id,
                        save_to_file=getattr(args, 'save', None))
    elif args.command == 'web':
        # Web UI doesn't need vector store initialization here
        # It will initialize it when needed
        run_web_ui(
            host=getattr(args, 'host', '127.0.0.1'),
            port=getattr(args, 'port', 5000),
            debug=getattr(args, 'debug', False)
        )
    elif args.command == 'api':
        # API server doesn't need vector store initialization here
        # It will initialize it when needed
        from goodanalysis.api_server import run_api_server
        run_api_server(
            host=getattr(args, 'host', '127.0.0.1'),
            port=getattr(args, 'port', 5000),
            debug=getattr(args, 'debug', False)
        )


if __name__ == "__main__":
    main()
