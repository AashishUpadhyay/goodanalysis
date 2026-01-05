import React, { useState, useEffect } from 'react';
import './App.css';
import VideoList from './components/VideoList';
import VideoForm from './components/VideoForm';
import VideoTranscript from './components/VideoTranscript';
import Header from './components/Header';
import { videoService } from './services/api';

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
      const data = await videoService.getVideos();
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
      
      const data = await videoService.addVideo(videoUrl);
      
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
      setError(err.response?.data?.error || 'Failed to connect to server. Make sure the API server is running.');
      console.error('Error adding video:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleVideoSelect = async (videoId) => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await videoService.getVideo(videoId);
      
      if (data.success) {
        setSelectedVideo(data.video);
      } else {
        setError(data.error || 'Failed to load transcript');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to connect to server.');
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

