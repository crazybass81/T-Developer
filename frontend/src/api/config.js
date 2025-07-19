// API 설정
const getApiBaseUrl = () => {
  // If explicitly set in environment
  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }
  
  // Try to detect if we're running through SSH port forwarding
  const hostname = window.location.hostname;
  const port = window.location.port;
  
  // If we're accessing through a non-standard React port, assume SSH forwarding
  if (port && port !== '3000' && port !== '3001') {
    // Use the same hostname but with backend port 8000
    return `${window.location.protocol}//${hostname}:8000`;
  }
  
  // Default fallback
  return 'http://172.31.21.41:8000';
};

export const apiClient = {
  baseURL: getApiBaseUrl(),
  headers: {
    'Content-Type': 'application/json',
  }
};

export default apiClient;