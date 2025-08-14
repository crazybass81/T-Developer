import axios, { AxiosInstance, AxiosError } from 'axios';
import { ApiResponse } from '@/types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      if (typeof window !== 'undefined') {
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
    }

    // Format error response
    const errorResponse: ApiResponse<null> = {
      success: false,
      error: error.response?.data?.error || error.message || 'An error occurred',
      message: error.response?.data?.message,
      timestamp: new Date().toISOString(),
    };

    return Promise.reject(errorResponse);
  }
);

// Helper functions
export const get = <T>(url: string, params?: any): Promise<ApiResponse<T>> =>
  apiClient.get(url, { params }).then(res => res.data);

export const post = <T>(url: string, data?: any): Promise<ApiResponse<T>> =>
  apiClient.post(url, data).then(res => res.data);

export const put = <T>(url: string, data?: any): Promise<ApiResponse<T>> =>
  apiClient.put(url, data).then(res => res.data);

export const del = <T>(url: string): Promise<ApiResponse<T>> =>
  apiClient.delete(url).then(res => res.data);

export default apiClient;
