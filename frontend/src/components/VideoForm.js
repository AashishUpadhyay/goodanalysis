import React, { useState } from 'react';
import './VideoForm.css';

function VideoForm({ onAddVideo, loading, error, message }) {
  const [videoUrl, setVideoUrl] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (videoUrl.trim()) {
      onAddVideo(videoUrl.trim());
      setVideoUrl('');
    }
  };

  return (
    <div className="video-form-container fade-in">
      <div className="video-form-card">
        <h2>➕ Add New Video</h2>
        <form onSubmit={handleSubmit} className="video-form">
          <div className="form-group">
            <input
              type="text"
              value={videoUrl}
              onChange={(e) => setVideoUrl(e.target.value)}
              placeholder="Enter YouTube URL or Video ID"
              className="form-input"
              disabled={loading}
              required
            />
            <button 
              type="submit" 
              className="form-submit-btn"
              disabled={loading || !videoUrl.trim()}
            >
              {loading ? (
                <>
                  <span className="loading-spinner"></span>
                  Processing...
                </>
              ) : (
                'Download Transcript'
              )}
            </button>
          </div>
          <p className="form-help">
            Supports: youtube.com/watch?v=..., youtu.be/..., or just the video ID
          </p>
        </form>
        
        {error && (
          <div className="alert alert-error">
            <span>❌</span>
            <span>{error}</span>
          </div>
        )}
        
        {message && (
          <div className="alert alert-success">
            <span>✅</span>
            <span>{message}</span>
          </div>
        )}
      </div>
    </div>
  );
}

export default VideoForm;

