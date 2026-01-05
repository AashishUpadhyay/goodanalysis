import React from 'react';
import './VideoTranscript.css';

function VideoTranscript({ video, onBack, loading }) {
  if (loading) {
    return (
      <div className="transcript-container">
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading transcript...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="transcript-container fade-in">
      <div className="transcript-header-card">
        <button onClick={onBack} className="back-button">
          ← Back to Videos
        </button>
        
        <div className="video-preview">
          <img
            src={video.thumbnail}
            alt={`Video ${video.id}`}
            className="video-preview-thumbnail"
            onError={(e) => {
              e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="112"%3E%3Crect fill="%23ddd" width="200" height="112"/%3E%3Ctext x="50%25" y="50%25" text-anchor="middle" dy=".3em" fill="%23999" font-family="Arial" font-size="12"%3ENo Thumbnail%3C/text%3E%3C/svg%3E';
            }}
          />
          <div className="video-preview-info">
            <h2>Video: {video.id}</h2>
            <p className="video-url">
              <a
                href={video.url}
                target="_blank"
                rel="noopener noreferrer"
                className="external-link"
              >
                {video.url}
              </a>
            </p>
            <a
              href={video.url}
              target="_blank"
              rel="noopener noreferrer"
              className="watch-button"
            >
              Watch on YouTube →
            </a>
          </div>
        </div>
      </div>

      <div className="transcript-card">
        <div className="transcript-header">
          <h2>📄 Transcript</h2>
          <div className="transcript-meta">
            {video.char_count.toLocaleString()} characters
          </div>
        </div>
        <div className="transcript-content">
          {video.transcript}
        </div>
      </div>
    </div>
  );
}

export default VideoTranscript;


