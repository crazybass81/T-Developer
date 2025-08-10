/**
 * API Client using Next.js rewrites for proxying
 * Works with VSCode port forwarding automatically
 */

// Use relative URL with /backend prefix that will be proxied by Next.js
export const API_BASE_URL = '';

export const apiClient = {
  async post(endpoint: string, data: any) {
    const url = `/backend/api/v1${endpoint}`;
    console.log('API Request:', url, data);
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('API Error:', response.status, errorText);
        throw new Error(`API Error: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Fetch error:', error);
      throw error;
    }
  },
  
  async get(endpoint: string) {
    const url = `/backend/api/v1${endpoint}`;
    console.log('API Request:', url);
    
    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('API Error:', response.status, errorText);
        throw new Error(`API Error: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Fetch error:', error);
      throw error;
    }
  }
};