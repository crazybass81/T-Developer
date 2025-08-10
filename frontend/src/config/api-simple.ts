/**
 * Simple API Configuration
 * Uses relative paths to work with any port forwarding setup
 */

// Use relative paths - will work with any port forwarding
export const API_URL = '';  // Empty string for relative URLs

// WebSocket URL - needs to be absolute
export const WS_URL = typeof window !== 'undefined' 
  ? `ws://${window.location.host}`
  : 'ws://localhost:8000';

// API Endpoints - using proxy paths
export const API_ENDPOINTS = {
  // Project endpoints - using proxy
  projects: '/api/proxy/projects',
  generate: '/api/proxy/generate',
  download: (projectId: string) => `/api/proxy/download/${projectId}`,
  preview: (projectId: string) => `/api/proxy/preview/${projectId}`,
  
  // Agent endpoints
  agents: '/api/proxy/agents',
  bedrock: {
    status: '/api/proxy/bedrock/status',
  },
  
  // Health check
  health: '/api/proxy/health',
  
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
};

// Helper function to build API URL
export function buildApiUrl(path: string): string {
  if (path.startsWith('http')) {
    return path;
  }
  
  return path; // Return as-is for relative paths
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