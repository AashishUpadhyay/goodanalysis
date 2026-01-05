import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:5001/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const videoService = {
  // Get all videos
  getVideos: async () => {
    const response = await api.get('/videos');
    return response.data;
  },

  // Add a new video
  addVideo: async (videoUrl) => {
    const response = await api.post('/videos', { video_url: videoUrl });
    return response.data;
  },

  // Get a specific video transcript
  getVideo: async (videoId) => {
    const response = await api.get(`/videos/${videoId}`);
    return response.data;
  },

  // Health check
  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;


