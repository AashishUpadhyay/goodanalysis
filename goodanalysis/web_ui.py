"""
Web UI for YouTube Transcript Viewer
Provides a web interface to list videos and view transcripts
"""
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from goodanalysis.vector_store import VectorStore
from goodanalysis.transcript_downloader import download_transcript, format_transcript, get_video_id_from_url
import os
import io
import sys
import traceback
from contextlib import redirect_stdout, redirect_stderr

# Get the directory where this file is located
template_dir = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=template_dir)
app.secret_key = os.urandom(24)  # For flash messages

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


@app.route('/health')
def health():
    """Simple health check endpoint."""
    return jsonify({"status": "ok", "message": "Server is running"}), 200


@app.route('/', methods=['GET', 'POST'])
def index():
    """Home page - list all videos and handle video URL submission."""
    if request.method == 'POST':
        # Force output to stderr (unbuffered) and stdout

        def log_debug(msg):
            sys.stderr.write(str(msg) + "\n")
            sys.stderr.flush()
            print(msg, flush=True)
            app.logger.info(str(msg))

        # Comprehensive logging for debugging - use stderr (unbuffered)
        log_debug("\n" + "="*60)
        log_debug("🔍 POST REQUEST DEBUG INFO")
        log_debug("="*60)
        log_debug(f"Method: {request.method}")
        log_debug(f"URL: {request.url}")
        log_debug(f"Content-Type: {request.content_type}")
        log_debug(f"Content-Length: {request.content_length}")

        # Log form data in detail
        form_dict = dict(request.form)
        log_debug(f"\n📋 Form data (ImmutableMultiDict): {form_dict}")
        log_debug(f"Form keys: {list(request.form.keys())}")
        for key in request.form.keys():
            value = request.form.get(key)
            log_debug(
                f"  • '{key}' = '{value}' (type: {type(value).__name__}, len: {len(str(value))})")

        # Log JSON if present
        json_data = request.get_json(silent=True)
        log_debug(f"\n📦 JSON data: {json_data}")
        log_debug(f"Is JSON: {request.is_json}")

        # Log raw request data
        raw_data = request.get_data(as_text=True)
        log_debug(f"\n📄 Raw request data (first 500 chars):")
        log_debug(raw_data[:500] if raw_data else "None")
        log_debug(f"Raw data length: {len(raw_data) if raw_data else 0}")

        # Try to manually parse form data if Flask didn't parse it
        if not form_dict and raw_data:
            log_debug(
                "\n⚠️  Flask didn't parse form data, trying manual parse...")
            try:
                from urllib.parse import unquote_plus, parse_qs
                parsed_data = parse_qs(raw_data)
                log_debug(f"Manually parsed data: {parsed_data}")
                if 'video_url' in parsed_data:
                    video_url_manual = parsed_data['video_url'][0] if parsed_data['video_url'] else ''
                    log_debug(
                        f"Found video_url in manual parse: '{video_url_manual}'")
            except Exception as parse_error:
                log_debug(f"Manual parse error: {parse_error}")
                import traceback
                log_debug(traceback.format_exc())

        # Try multiple methods to get video_url
        video_url = None
        source = None

        # Method 1: Form data
        if 'video_url' in request.form:
            video_url = request.form.get('video_url', '').strip()
            source = "form"
            log_debug(f"\n✅ Found video_url in FORM: '{video_url}'")

        # Method 2: Manual parse from raw data (if Flask didn't parse it)
        if not video_url and raw_data:
            try:
                from urllib.parse import unquote_plus, parse_qs
                parsed_data = parse_qs(raw_data)
                log_debug(f"Manual parse result: {parsed_data}")
                if 'video_url' in parsed_data and parsed_data['video_url']:
                    video_url = parsed_data['video_url'][0].strip()
                    source = "manual_parse"
                    log_debug(
                        f"\n✅ Found video_url in MANUAL PARSE: '{video_url}'")
            except Exception as parse_error:
                log_debug(f"Manual parse error: {parse_error}")
                import traceback
                log_debug(traceback.format_exc())

        # Method 3: JSON
        if not video_url and request.is_json:
            json_data = request.get_json(silent=True) or {}
            video_url = json_data.get('video_url', '').strip()
            source = "json"
            log_debug(f"\n✅ Found video_url in JSON: '{video_url}'")

        # Method 4: Query args (just in case)
        if not video_url and 'video_url' in request.args:
            video_url = request.args.get('video_url', '').strip()
            source = "args"
            log_debug(f"\n✅ Found video_url in ARGS: '{video_url}'")

        # Final result
        if not video_url:
            video_url = ''
            log_debug(f"\n❌ NO video_url found in any source!")
            log_debug(f"   Available form keys: {list(request.form.keys())}")
            log_debug(f"   Available args keys: {list(request.args.keys())}")
            log_debug(f"   Raw data: {raw_data[:200] if raw_data else 'None'}")
        else:
            log_debug(
                f"\n✓ Final video_url from {source}: '{video_url}' (length: {len(video_url)})")

        log_debug("="*60 + "\n")

        if not video_url:
            error_details = (
                f"Form keys: {list(request.form.keys())}, "
                f"Args keys: {list(request.args.keys())}, "
                f"Content-Type: {request.content_type}, "
                f"Raw data length: {len(raw_data) if raw_data else 0}, "
                f"Raw data preview: {raw_data[:100] if raw_data else 'None'}"
            )
            error_msg = f'Please enter a YouTube video URL or video ID. Debug: {error_details}'
            log_debug(f"ERROR: Empty video_url - {error_details}")
            flash(error_msg, 'error')
            return redirect(url_for('index'))

        try:
            app.logger.info(f"Processing video URL: {video_url}")

            # Extract video ID
            video_id = get_video_id_from_url(video_url)
            app.logger.info(f"Extracted video ID: {video_id}")

            # Check if video already exists
            app.logger.info("Checking if video already exists in database...")
            vector_store = get_vector_store()
            existing_videos = vector_store.get_all_videos()
            app.logger.info(
                f"Found {len(existing_videos)} existing videos in database")

            if video_id in existing_videos:
                app.logger.info(
                    f"Video {video_id} already exists, redirecting to transcript")
                flash(
                    f'Video {video_id} is already in the database. Redirecting to transcript...', 'info')
                return redirect(url_for('view_transcript', video_id=video_id))

            # Download transcript (suppress print statements)
            app.logger.info(f"Downloading transcript for video {video_id}...")
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                transcript = download_transcript(video_id)

            if not transcript:
                app.logger.error(
                    f"Failed to download transcript for video {video_id}")
                flash(
                    f'Failed to download transcript for video {video_id}. Make sure the video has captions enabled.', 'error')
                return redirect(url_for('index'))

            app.logger.info(
                f"Successfully downloaded transcript ({len(transcript)} entries)")

            # Format transcript
            transcript_text = format_transcript(transcript)
            app.logger.info(
                f"Formatted transcript ({len(transcript_text)} characters)")

            # Add to vector store (suppress print statements)
            app.logger.info(f"Storing transcript in vector database...")
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                vector_store.add_transcript(video_id, transcript_text)

            app.logger.info(
                f"Successfully stored transcript for video {video_id}")
            flash(
                f'Successfully downloaded and stored transcript for video {video_id}!', 'success')
            return redirect(url_for('view_transcript', video_id=video_id))

        except Exception as e:
            # Log the full error for debugging
            error_details = traceback.format_exc()
            app.logger.error(
                f"Error processing video '{video_url}': {error_details}")
            flash(
                f'Error processing video: {str(e)}. Check server logs for details.', 'error')
            return redirect(url_for('index'))

    # GET request - show video list
    try:
        vector_store = get_vector_store()
        videos = vector_store.get_all_videos()

        # Create video data with YouTube URLs
        video_data = []
        for video_id in videos:
            video_data.append({
                'id': video_id,
                'url': f'https://www.youtube.com/watch?v={video_id}',
                'thumbnail': f'https://img.youtube.com/vi/{video_id}/mqdefault.jpg'
            })

        return render_template('index.html', videos=video_data)
    except Exception as e:
        error_msg = f"Error loading page: {str(e)}"
        app.logger.error(f"Error in index: {traceback.format_exc()}")
        print(f"ERROR in index: {error_msg}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        try:
            return render_template('error.html', message=error_msg), 500
        except:
            return f"<h1>Error</h1><p>{error_msg}</p>", 500


@app.route('/video/<video_id>')
def view_transcript(video_id):
    """View transcript for a specific video."""
    vector_store = get_vector_store()
    transcript = vector_store.get_transcript(video_id)

    if not transcript:
        return render_template('error.html',
                               message=f"No transcript found for video: {video_id}",
                               video_id=video_id), 404

    video_data = {
        'id': video_id,
        'url': f'https://www.youtube.com/watch?v={video_id}',
        'thumbnail': f'https://img.youtube.com/vi/{video_id}/mqdefault.jpg',
        'transcript': transcript,
        'char_count': len(transcript)
    }

    return render_template('transcript.html', video=video_data)


@app.route('/api/videos')
def api_videos():
    """API endpoint to get list of videos."""
    vector_store = get_vector_store()
    videos = vector_store.get_all_videos()

    video_data = []
    for video_id in videos:
        video_data.append({
            'id': video_id,
            'url': f'https://www.youtube.com/watch?v={video_id}',
            'thumbnail': f'https://img.youtube.com/vi/{video_id}/mqdefault.jpg'
        })

    return jsonify(video_data)


@app.route('/api/video/<video_id>/transcript')
def api_transcript(video_id):
    """API endpoint to get transcript for a video."""
    vector_store = get_vector_store()
    transcript = vector_store.get_transcript(video_id)

    if not transcript:
        return jsonify({'error': f'No transcript found for video: {video_id}'}), 404

    return jsonify({
        'video_id': video_id,
        'transcript': transcript,
        'char_count': len(transcript)
    })


def run_web_ui(host='127.0.0.1', port=5000, debug=False):
    """Run the web UI server."""
    # Configure logging
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Test template directory
    if not os.path.exists(template_dir):
        print(
            f"ERROR: Template directory not found: {template_dir}", file=sys.stderr)
        raise FileNotFoundError(
            f"Template directory not found: {template_dir}")

    print(f"Template directory: {template_dir}", file=sys.stderr)
    print(f"Templates found: {os.listdir(template_dir)}", file=sys.stderr)

    print(f"\n🌐 Starting web UI server...")
    print(f"📱 Open your browser to: http://{host}:{port}")
    print(f"🔍 Health check: http://{host}:{port}/health")
    print(f"Press Ctrl+C to stop the server\n")
    if debug:
        print("🐛 Debug mode enabled - detailed logging active\n")

    try:
        app.run(host=host, port=port, debug=debug)
    except Exception as e:
        print(f"ERROR starting server: {e}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        raise
