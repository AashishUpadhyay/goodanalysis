"""
YouTube Transcript Downloader
Downloads transcripts from YouTube videos using youtube-transcript-api
"""
try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    raise ImportError("youtube-transcript-api is not installed. Run: uv sync")

from typing import Optional, List, Dict


def download_transcript(video_id: str, languages: List[str] = ['en'], use_auto_generated: bool = True) -> Optional[List[Dict]]:
    """
    Download transcript for a YouTube video.
    Tries manually created captions first, then falls back to auto-generated captions.

    Args:
        video_id: YouTube video ID (from URL: youtube.com/watch?v=VIDEO_ID)
        languages: List of language codes to try (default: ['en'])
        use_auto_generated: If True, will try auto-generated captions if manual ones aren't available

    Returns:
        List of transcript entries with 'text', 'start', and 'duration' keys
        None if transcript not available
    """
    try:
        # Try new API first (instance-based with fetch method)
        try:
            yt_api = YouTubeTranscriptApi()
            transcript_data = yt_api.fetch(video_id, languages=languages)
            return transcript_data.to_raw_data()
        except (AttributeError, TypeError):
            # Fall back to old static method API (if it exists)
            if hasattr(YouTubeTranscriptApi, 'get_transcript'):
                return YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
            else:
                raise AttributeError(
                    "Neither fetch() nor get_transcript() methods are available")
    except Exception as e:
        error_msg = str(e)
        # If manual transcripts fail and auto-generated is enabled, try fallback strategies
        if use_auto_generated:
            # Strategy 1: Try without language restriction (may get auto-generated)
            try:
                try:
                    yt_api = YouTubeTranscriptApi()
                    transcript_data = yt_api.fetch(video_id)
                    print(f"⚠️  Using available captions (may be auto-generated)")
                    return transcript_data.to_raw_data()
                except (AttributeError, TypeError):
                    if hasattr(YouTubeTranscriptApi, 'get_transcript'):
                        transcript = YouTubeTranscriptApi.get_transcript(
                            video_id)
                        print(f"⚠️  Using available captions (may be auto-generated)")
                        return transcript
                    else:
                        raise
            except Exception as e2:
                # Strategy 2: Try with translate parameter (sometimes helps with auto-generated)
                try:
                    try:
                        yt_api = YouTubeTranscriptApi()
                        transcript_data = yt_api.fetch(
                            video_id, languages=languages, translate=True)
                        print(f"⚠️  Using translated/auto-generated captions")
                        return transcript_data.to_raw_data()
                    except (AttributeError, TypeError):
                        if hasattr(YouTubeTranscriptApi, 'get_transcript'):
                            transcript = YouTubeTranscriptApi.get_transcript(
                                video_id, languages=languages, translate=True)
                            print(f"⚠️  Using translated/auto-generated captions")
                            return transcript
                        else:
                            raise
                except Exception as final_error:
                    print(
                        f"Error downloading transcript (including auto-generated): {final_error}")
                    print(f"Original error: {error_msg}")
                    return None
        else:
            print(f"Error downloading transcript: {error_msg}")
            return None


def format_transcript(transcript: List[Dict]) -> str:
    """
    Format transcript list into a single text string.

    Args:
        transcript: List of transcript entries

    Returns:
        Formatted text string
    """
    return " ".join([entry['text'] for entry in transcript])


def get_video_id_from_url(url: str) -> str:
    """
    Extract video ID from YouTube URL.

    Supports formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - VIDEO_ID (if already just the ID)
    """
    if 'youtube.com/watch?v=' in url:
        return url.split('watch?v=')[1].split('&')[0]
    elif 'youtu.be/' in url:
        return url.split('youtu.be/')[1].split('?')[0]
    else:
        # Assume it's already a video ID
        return url
