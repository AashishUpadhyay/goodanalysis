import React, { useState, useEffect } from 'react';
import './App.css';
import VideoList from './components/VideoList';
import VideoForm from './components/VideoForm';
import VideoTranscript from './components/VideoTranscript';
import Header from './components/Header';

function App() {
  const [videos, setVideos] = useState([]);
  const [selectedVideo, setSelectedVideo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    loadVideos();
  }, []);

  const loadVideos = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://127.0.0.1:5000/api/videos');
      const data = await response.json();
      if (data.success) {
        setVideos(data.videos || []);
      } else {
        setError(data.error || 'Failed to load videos');
      }
    } catch (err) {
      setError('Failed to connect to server. Make sure the API server is running.');
      console.error('Error loading videos:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddVideo = async (videoUrl) => {
    try {
      setLoading(true);
      setError(null);
      setMessage(null);
      
      const response = await fetch('http://127.0.0.1:5000/api/videos', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ video_url: videoUrl }),
      });

      const data = await response.json();
      
      if (data.success) {
        if (data.exists) {
          setMessage(`Video ${data.video_id} already exists. Loading transcript...`);
        } else {
          setMessage(data.message || 'Video added successfully!');
        }
        // Reload videos and show the transcript
        await loadVideos();
        if (data.video_id) {
          handleVideoSelect(data.video_id);
        }
      } else {
        setError(data.error || 'Failed to add video');
      }
    } catch (err) {
      setError('Failed to connect to server. Make sure the API server is running.');
      console.error('Error adding video:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleVideoSelect = async (videoId) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`http://127.0.0.1:5000/api/videos/${videoId}`);
      const data = await response.json();
      
      if (data.success) {
        setSelectedVideo(data.video);
      } else {
        setError(data.error || 'Failed to load transcript');
      }
    } catch (err) {
      setError('Failed to connect to server.');
      console.error('Error loading video:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    setSelectedVideo(null);
    setError(null);
    setMessage(null);
  };

  return (
    <div className="App">
      <Header />
      <div className="container">
        {selectedVideo ? (
          <VideoTranscript 
            video={selectedVideo} 
            onBack={handleBack}
            loading={loading}
          />
        ) : (
          <>
            <VideoForm 
              onAddVideo={handleAddVideo} 
              loading={loading}
              error={error}
              message={message}
            />
            <VideoList 
              videos={videos} 
              onVideoSelect={handleVideoSelect}
              loading={loading}
            />
          </>
        )}
      </div>
    </div>
  );
}

export default App;

