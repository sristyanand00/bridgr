// API Configuration for Bridgr Frontend

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// API endpoints
export const API_ENDPOINTS = {
  // Base
  ROOT: '/',
  HEALTH: '/health',
  
  // Main features
  ANALYZE: '/api/analyze',
  CHAT: '/api/chat',
  ROADMAP: '/api/roadmap',
  MARKET_PULSE: '/api/market-pulse',
  INTERVIEW: '/api/interview',
};

// Generic API request function
export const apiRequest = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status} - ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API Request failed:', error);
    throw error;
  }
};

// Specific API methods
export const api = {
  // Health check
  health: () => apiRequest(API_ENDPOINTS.HEALTH),
  
  // Resume analysis
  analyzeResume: (formData) => {
    return apiRequest(API_ENDPOINTS.ANALYZE, {
      method: 'POST',
      body: formData,
      headers: {}, // Let browser set Content-Type for FormData
    });
  },
  
  // Chat with AI
  chat: (message, conversationHistory = []) => {
    return apiRequest(API_ENDPOINTS.CHAT, {
      method: 'POST',
      body: JSON.stringify({
        message,
        conversation_history: conversationHistory,
      }),
    });
  },
  
  // Get career roadmap
  getRoadmap: (profile) => {
    return apiRequest(API_ENDPOINTS.ROADMAP, {
      method: 'POST',
      body: JSON.stringify({ profile }),
    });
  },
  
  // Get market insights
  getMarketPulse: (role, location) => {
    return apiRequest(API_ENDPOINTS.MARKET_PULSE, {
      method: 'POST',
      body: JSON.stringify({ role, location }),
    });
  },
  
  // Interview preparation
  getInterviewPrep: (role, experience_level) => {
    return apiRequest(API_ENDPOINTS.INTERVIEW, {
      method: 'POST',
      body: JSON.stringify({ role, experience_level }),
    });
  },
};

export default API_BASE_URL;
