import React from 'react';
import './VideoList.css';

function VideoList({ videos, onVideoSelect, loading }) {
  if (loading && videos.length === 0) {
    return (
      <div className="video-list-container">
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading videos...</p>
        </div>
      </div>
    );
  }

  if (videos.length === 0) {
    return (
      <div className="video-list-container">
        <div className="empty-state">
          <div className="empty-icon">📹</div>
          <h2>No videos found</h2>
          <p>You haven't downloaded any video transcripts yet.</p>
          <p>Use the form above to add your first video!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="video-list-container fade-in">
      <h2 className="section-title">Downloaded Videos ({videos.length})</h2>
      <div className="video-grid">
        {videos.map((video) => (
          <div
            key={video.id}
            className="video-card"
            onClick={() => onVideoSelect(video.id)}
          >
            <div className="video-thumbnail-container">
              <img
                src={video.thumbnail}
                alt={`Video ${video.id}`}
                className="video-thumbnail"
                onError={(e) => {
                  e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="320" height="180"%3E%3Crect fill="%23ddd" width="320" height="180"/%3E%3Ctext x="50%25" y="50%25" text-anchor="middle" dy=".3em" fill="%23999" font-family="Arial" font-size="14"%3ENo Thumbnail%3C/text%3E%3C/svg%3E';
                }}
              />
              <div className="video-overlay">
                <span className="play-icon">▶</span>
              </div>
            </div>
            <div className="video-info">
              <div className="video-id">{video.id}</div>
              <a
                href={video.url}
                target="_blank"
                rel="noopener noreferrer"
                className="video-link"
                onClick={(e) => e.stopPropagation()}
              >
                Watch on YouTube →
              </a>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default VideoList;

