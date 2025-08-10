/**
 * API Configuration
 * Centralized configuration for API endpoints
 */

// Get API URL from environment variable or use default
// Support both Vite and Next.js environment variables
export const API_URL = 
  typeof window !== 'undefined' 
    ? (process.env.NEXT_PUBLIC_API_URL || import.meta.env?.VITE_API_URL || 'http://localhost:8000')
    : (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000');

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

// Request configuration defaults
export const REQUEST_CONFIG = {
  headers: {
    'Content-Type': 'application/json',
  },
  credentials: 'include' as RequestCredentials,
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