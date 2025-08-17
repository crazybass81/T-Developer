import axios from 'axios'
import { Agent } from '../store/slices/agentsSlice'
import { EvolutionCycle } from '../store/slices/evolutionSlice'

const API_BASE_URL = import.meta.env.VITE_API_ENDPOINT ||
  (import.meta.env.MODE === 'production'
    ? 'https://api.t-developer.io'
    : 'http://localhost:8000')

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for authentication
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const agentAPI = {
  getAgents: () => api.get<Agent[]>('/api/agents'),
  getAgent: (id: string) => api.get<Agent>(`/api/agents/${id}`),
  createAgent: (data: Partial<Agent>) => api.post<Agent>('/api/agents', data),
  updateAgent: (id: string, data: Partial<Agent>) => api.put<Agent>(`/api/agents/${id}`, data),
  deleteAgent: (id: string) => api.delete(`/api/agents/${id}`),
  startAgent: (id: string) => api.post<Agent>(`/api/agents/${id}/start`),
  stopAgent: (id: string) => api.post<Agent>(`/api/agents/${id}/stop`),
  restartAgent: (id: string) => api.post<Agent>(`/api/agents/${id}/restart`),
}

export const evolutionAPI = {
  startCycle: (config: any) => api.post<EvolutionCycle>('/api/evolution/start', config),
  stopCycle: () => api.post('/api/evolution/stop'),
  getCycles: () => api.get<EvolutionCycle[]>('/api/evolution/cycles'),
  getCycle: (id: string) => api.get<EvolutionCycle>(`/api/evolution/cycles/${id}`),
}

export const metricsAPI = {
  getMetrics: (range?: { start: Date; end: Date }) =>
    api.get('/api/metrics', { params: range }),
  getRealtimeMetrics: () => api.get('/api/metrics/realtime'),
  getSummary: () => api.get('/api/metrics/summary'),
}

export const logsAPI = {
  getLogs: (filters?: any) => api.get('/api/logs', { params: filters }),
  streamLogs: () => api.get('/api/logs/stream'),
}

export const workflowAPI = {
  runWorkflow: (data: {
    workflow: string
    target: string
    problem?: string
  }) => api.post('/api/workflow/run', data),
  getWorkflowStatus: (id: string) => api.get(`/api/workflow/${id}/status`),
  cancelWorkflow: (id: string) => api.post(`/api/workflow/${id}/cancel`),
}

export default api
