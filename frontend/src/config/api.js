// API Configuration for Bridgr Frontend

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// API call: GET /health
export const health = () =>
  fetch(`${API_BASE_URL}/health`).then(res => {
    if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
    return res.json();
  });

// API call: POST /api/readiness (multipart/form-data)
export const readiness = (formData) =>
  fetch(`${API_BASE_URL}/api/readiness`, {
    method: 'POST',
    body: formData,
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

export default API_BASE_URL;
