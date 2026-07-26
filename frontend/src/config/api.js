// API Configuration for Bridgr Frontend

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// API call: GET /health
export const health = () =>
  fetch(`${API_BASE_URL}/health`, {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    }
  }).then(res => {
    if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
    return res.json();
  });

// API call: POST /api/readiness (multipart/form-data)
export const readiness = (formData) =>
  fetch(`${API_BASE_URL}/api/readiness`, {
    method: 'POST',
    body: formData,
    credentials: 'include',
  }).then(async res => {
    if (!res.ok) {
      let message = 'Could not generate readiness report.';
      try {
        const body = await res.json();
        message = body?.error || body?.detail || body?.explanations?.[0] || message;
      } catch (_) {}
      throw new Error(message);
    }
    return res.json();
  });

// API call: POST /api/user/sync
export const syncUser = (token) =>
  fetch(`${API_BASE_URL}/api/user/sync`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }
  }).then(async res => {
    if (!res.ok) {
      if (res.status === 401 || res.status === 403) {
        throw new Error('Authentication failed');
      }
      let message = 'Could not sync user data.';
      try {
        const body = await res.json();
        message = body?.error || body?.detail || message;
      } catch (_) {}
      throw new Error(message);
    }
    return res.json();
  });

// API call: POST /api/user/quiz  
export const saveQuiz = (quizData, token) =>
  fetch(`${API_BASE_URL}/api/user/quiz`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ quiz_data: quizData })
  }).then(async res => {
    if (!res.ok) {
      if (res.status === 401 || res.status === 403) {
        throw new Error('Authentication failed');
      }
      let message = 'Could not save quiz data.';
      try {
        const body = await res.json();
        message = body?.error || body?.detail || message;
      } catch (_) {}
      throw new Error(message);
    }
    return res.json();
  });

export default API_BASE_URL;
