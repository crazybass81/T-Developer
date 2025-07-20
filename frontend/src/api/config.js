// API 설정
const getApiBaseUrl = () => {
  // If explicitly set in environment
  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }
  
  // Check if we're running on S3 website
  if (window.location.hostname.includes('s3-website')) {
    // Extract region from S3 website URL
    const hostnameparts = window.location.hostname.split('.');
    const region = hostnameparts[1];
    
    // Use API Gateway or CloudFront URL if available
    if (process.env.REACT_APP_API_GATEWAY_URL) {
      return process.env.REACT_APP_API_GATEWAY_URL;
    }
    
    // Fallback to EC2 public DNS if available
    if (process.env.REACT_APP_EC2_PUBLIC_DNS) {
      return `http://${process.env.REACT_APP_EC2_PUBLIC_DNS}:8000`;
    }
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
  return 'http://localhost:8000';
};

export const apiClient = {
  baseURL: getApiBaseUrl(),
  headers: {
    'Content-Type': 'application/json',
  }
};

export default apiClient;