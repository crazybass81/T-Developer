/**
 * Dynamic API Configuration
 * Handles both local and port-forwarded environments
 */

// Detect if we're in a port-forwarded environment
function getApiUrl(): string {
  if (typeof window === 'undefined') {
    // Server-side
    return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  }
  
  // Client-side
  const currentHost = window.location.hostname;
  const currentPort = window.location.port;
  
  // If running on a non-standard port (like 55635), assume port forwarding
  if (currentPort && parseInt(currentPort) > 10000) {
    // VSCode typically forwards ports sequentially
    // If frontend is on 55635, backend might be on 55636
    const frontendPort = parseInt(currentPort);
    const backendPort = frontendPort + 1; // Assume sequential forwarding
    
    // Try to detect the backend port
    console.log(`Detected port forwarding. Frontend: ${frontendPort}, trying backend on: ${backendPort}`);
    
    return `http://${currentHost}:${backendPort}`;
  }
  
  // Default to environment variable or localhost
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
}

// Get API URL dynamically
export const API_URL = getApiUrl();

// WebSocket URL (convert http to ws)
export const WS_URL = API_URL.replace(/^http/, 'ws');

// API Endpoints
export const API_ENDPOINTS = {
  // Project endpoints
  projects: `${API_URL}/api/v1/projects`,
  generate: `${API_URL}/api/v1/generate`,
  download: (projectId: string) => `${API_URL}/api/v1/download/${projectId}`,
  preview: (projectId: string) => `${API_URL}/api/v1/preview/${projectId}`,
  
  // Agent endpoints
  agents: `${API_URL}/api/v1/agents`,
  bedrock: {
    status: `${API_URL}/api/v1/bedrock/status`,
  },
  
  // Health check
  health: `${API_URL}/health`,
  
  // WebSocket endpoints
  ws: {
    project: (projectId: string) => `${WS_URL}/ws/${projectId}`,
  },
};

// Log configuration for debugging
if (typeof window !== 'undefined') {
  console.log('API Configuration:', {
    API_URL,
    WS_URL,
    location: window.location.href
  });
}

// Request configuration defaults
export const REQUEST_CONFIG = {
  headers: {
    'Content-Type': 'application/json',
  },
  // Remove credentials requirement for cross-port requests
  mode: 'cors' as RequestMode,
};

// Helper function to build API URL
export function buildApiUrl(path: string): string {
  if (path.startsWith('http')) {
    return path;
  }
  
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${API_URL}${cleanPath}`;
}

// Helper function for error handling
export async function handleApiResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorText = await response.text();
    let errorMessage = `API Error: ${response.status}`;
    
    try {
      const errorJson = JSON.parse(errorText);
      errorMessage = errorJson.error || errorJson.message || errorMessage;
    } catch {
      errorMessage = errorText || errorMessage;
    }
    
    throw new Error(errorMessage);
  }
  
  return response.json();
}