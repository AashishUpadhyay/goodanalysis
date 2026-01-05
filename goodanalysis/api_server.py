"""
API Server for YouTube Transcript Viewer
RESTful API endpoints for the React frontend
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from goodanalysis.vector_store import VectorStore
from goodanalysis.transcript_downloader import download_transcript, format_transcript, get_video_id_from_url
import os
import io
import sys
import traceback
from contextlib import redirect_stdout, redirect_stderr

app = Flask(__name__)
# Enable CORS for React frontend
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Cache the vector store instance to avoid reloading the embedding model
_vector_store_instance = None


def get_vector_store():
    """Get initialized vector store instance (cached)."""
    global _vector_store_instance
    if _vector_store_instance is None:
        try:
            # Suppress print statements during initialization for web UI
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                _vector_store_instance = VectorStore()
            print("VectorStore initialized successfully", file=sys.stderr)
        except Exception as e:
            error_msg = f"Failed to initialize VectorStore: {str(e)}"
            print(f"ERROR: {error_msg}", file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)
            app.logger.error(
                f"VectorStore initialization error: {traceback.format_exc()}")
            raise
    return _vector_store_instance


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "message": "API server is running"}), 200


@app.route('/api/videos', methods=['GET'])
def get_videos():
    """Get list of all videos."""
    try:
        vector_store = get_vector_store()
        videos = vector_store.get_all_videos()

        video_data = []
        for video_id in videos:
            video_data.append({
                'id': video_id,
                'url': f'https://www.youtube.com/watch?v={video_id}',
                'thumbnail': f'https://img.youtube.com/vi/{video_id}/mqdefault.jpg'
            })

        return jsonify({
            'success': True,
            'videos': video_data,
            'count': len(video_data)
        }), 200
    except Exception as e:
        app.logger.error(f"Error getting videos: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/videos', methods=['POST'])
def add_video():
    """Add a new video transcript."""
    try:
        data = request.get_json()
        if not data or 'video_url' not in data:
            return jsonify({
                'success': False,
                'error': 'video_url is required'
            }), 400

        video_url = data['video_url'].strip()
        if not video_url:
            return jsonify({
                'success': False,
                'error': 'video_url cannot be empty'
            }), 400

        # Extract video ID
        video_id = get_video_id_from_url(video_url)

        # Check if video already exists
        vector_store = get_vector_store()
        existing_videos = vector_store.get_all_videos()

        if video_id in existing_videos:
            return jsonify({
                'success': True,
                'message': f'Video {video_id} already exists',
                'video_id': video_id,
                'exists': True
            }), 200

        # Download transcript
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            transcript = download_transcript(video_id)

        if not transcript:
            return jsonify({
                'success': False,
                'error': f'Failed to download transcript for video {video_id}. Make sure the video has captions enabled.'
            }), 400

        # Format transcript
        transcript_text = format_transcript(transcript)

        # Add to vector store
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            vector_store.add_transcript(video_id, transcript_text)

        return jsonify({
            'success': True,
            'message': f'Successfully downloaded and stored transcript for video {video_id}',
            'video_id': video_id,
            'char_count': len(transcript_text)
        }), 201

    except Exception as e:
        app.logger.error(f"Error adding video: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/videos/<video_id>', methods=['GET'])
def get_video(video_id):
    """Get transcript for a specific video."""
    try:
        vector_store = get_vector_store()
        transcript = vector_store.get_transcript(video_id)

        if not transcript:
            return jsonify({
                'success': False,
                'error': f'No transcript found for video: {video_id}'
            }), 404

        return jsonify({
            'success': True,
            'video': {
                'id': video_id,
                'url': f'https://www.youtube.com/watch?v={video_id}',
                'thumbnail': f'https://img.youtube.com/vi/{video_id}/mqdefault.jpg',
                'transcript': transcript,
                'char_count': len(transcript)
            }
        }), 200

    except Exception as e:
        app.logger.error(f"Error getting video: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/videos/<video_id>', methods=['DELETE'])
def delete_video(video_id):
    """Delete a video transcript."""
    # Note: This would require implementing delete functionality in VectorStore
    return jsonify({
        'success': False,
        'error': 'Delete functionality not yet implemented'
    }), 501


def run_api_server(host='127.0.0.1', port=5000, debug=False):
    """Run the API server."""
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    print(f"\n🚀 Starting API server...")
    print(f"📡 API base URL: http://{host}:{port}/api")
    print(f"🔍 Health check: http://{host}:{port}/api/health")
    print(f"Press Ctrl+C to stop the server\n")
    if debug:
        print("🐛 Debug mode enabled\n")

    try:
        app.run(host=host, port=port, debug=debug)
    except Exception as e:
        print(f"ERROR starting server: {e}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        raise
