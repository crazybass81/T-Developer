import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'

// API Response Types
export interface ApiResponse<T = any> {
  data: T
  success: boolean
  message?: string
  error?: string
  timestamp: string
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  pageSize: number
  hasNext: boolean
  hasPrevious: boolean
}

// Error Types
export class ApiError extends Error {
  constructor(
    public statusCode: number,
    public message: string,
    public details?: any
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

// Retry Configuration
interface RetryConfig {
  maxRetries: number
  retryDelay: number
  retryCondition?: (error: any) => boolean
}

// Cache Configuration
interface CacheConfig {
  ttl: number // Time to live in milliseconds
  key: string
}

class ApiClient {
  private instance: AxiosInstance
  private cache: Map<string, { data: any; timestamp: number }> = new Map()
  private requestQueue: Map<string, Promise<any>> = new Map()

  private defaultRetryConfig: RetryConfig = {
    maxRetries: 3,
    retryDelay: 1000,
    retryCondition: (error) => {
      // Retry on network errors or 5xx status codes
      return !error.response || (error.response.status >= 500 && error.response.status < 600)
    }
  }

  constructor(baseURL?: string) {
    const apiBaseUrl = baseURL || this.getBaseURL()

    this.instance = axios.create({
      baseURL: apiBaseUrl,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.setupInterceptors()
  }

  private getBaseURL(): string {
    return import.meta.env.VITE_API_ENDPOINT ||
      (import.meta.env.MODE === 'production'
        ? 'https://api.t-developer.io'
        : 'http://localhost:8000')
  }

  private setupInterceptors(): void {
    // Request interceptor
    this.instance.interceptors.request.use(
      (config) => {
        // Add authentication token
        const token = localStorage.getItem('token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }

        // Add request ID for tracing
        config.headers['X-Request-ID'] = this.generateRequestId()

        // Add timestamp
        config.headers['X-Request-Timestamp'] = new Date().toISOString()

        return config
      },
      (error) => {
        console.error('Request error:', error)
        return Promise.reject(error)
      }
    )

    // Response interceptor
    this.instance.interceptors.response.use(
      (response) => {
        // Log response time
        const requestTime = response.config.headers['X-Request-Timestamp']
        if (requestTime) {
          const duration = Date.now() - new Date(requestTime).getTime()
          console.debug(`API call took ${duration}ms`, {
            url: response.config.url,
            method: response.config.method,
            duration
          })
        }
        return response
      },
      async (error) => {
        // Handle specific error codes
        if (error.response) {
          switch (error.response.status) {
            case 401:
              // Unauthorized - clear token and redirect to login
              localStorage.removeItem('token')
              window.location.href = '/login'
              break
            case 403:
              // Forbidden
              console.error('Access denied:', error.response.data)
              break
            case 429:
              // Rate limited - could implement retry with backoff
              console.warn('Rate limited:', error.response.data)
              break
            case 500:
            case 502:
            case 503:
            case 504:
              // Server errors - could retry
              console.error('Server error:', error.response.status)
              break
          }
        }

        return Promise.reject(this.transformError(error))
      }
    )
  }

  private generateRequestId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
  }

  private transformError(error: any): ApiError {
    if (error.response) {
      return new ApiError(
        error.response.status,
        error.response.data?.message || error.message,
        error.response.data
      )
    } else if (error.request) {
      return new ApiError(0, 'Network error - no response received', error.request)
    } else {
      return new ApiError(0, error.message || 'Unknown error', error)
    }
  }

  // Exponential backoff retry logic
  private async retryWithBackoff<T>(
    fn: () => Promise<T>,
    config: RetryConfig = this.defaultRetryConfig
  ): Promise<T> {
    let lastError: any

    for (let i = 0; i < config.maxRetries; i++) {
      try {
        return await fn()
      } catch (error) {
        lastError = error

        if (!config.retryCondition || !config.retryCondition(error)) {
          throw error
        }

        if (i < config.maxRetries - 1) {
          // Exponential backoff with jitter
          const delay = config.retryDelay * Math.pow(2, i) + Math.random() * 1000
          console.log(`Retrying after ${delay}ms (attempt ${i + 1}/${config.maxRetries})`)
          await new Promise(resolve => setTimeout(resolve, delay))
        }
      }
    }

    throw lastError
  }

  // Cache management
  private getCachedData(key: string, ttl: number): any | null {
    const cached = this.cache.get(key)
    if (cached && Date.now() - cached.timestamp < ttl) {
      console.debug(`Cache hit for ${key}`)
      return cached.data
    }
    return null
  }

  private setCachedData(key: string, data: any): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    })
  }

  private clearCache(pattern?: string): void {
    if (pattern) {
      // Clear specific cache entries matching pattern
      for (const key of this.cache.keys()) {
        if (key.includes(pattern)) {
          this.cache.delete(key)
        }
      }
    } else {
      // Clear all cache
      this.cache.clear()
    }
  }

  // Request deduplication
  private async deduplicateRequest<T>(
    key: string,
    fn: () => Promise<T>
  ): Promise<T> {
    // Check if there's already a pending request
    const pending = this.requestQueue.get(key)
    if (pending) {
      console.debug(`Deduplicating request for ${key}`)
      return pending
    }

    // Create new request
    const request = fn().finally(() => {
      this.requestQueue.delete(key)
    })

    this.requestQueue.set(key, request)
    return request
  }

  // Public methods
  async get<T = any>(
    url: string,
    config?: AxiosRequestConfig & { cache?: CacheConfig; retry?: RetryConfig }
  ): Promise<T> {
    // Check cache if configured
    if (config?.cache) {
      const cached = this.getCachedData(config.cache.key, config.cache.ttl)
      if (cached !== null) {
        return cached
      }
    }

    // Deduplicate if caching is enabled
    const requestKey = config?.cache ? config.cache.key : `GET:${url}`

    const request = async () => {
      const fn = () => this.instance.get<T>(url, config)
      const response = config?.retry
        ? await this.retryWithBackoff(fn, config.retry)
        : await fn()

      const data = response.data

      // Cache the response if configured
      if (config?.cache) {
        this.setCachedData(config.cache.key, data)
      }

      return data
    }

    return config?.cache
      ? this.deduplicateRequest(requestKey, request)
      : request()
  }

  async post<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig & { retry?: RetryConfig }
  ): Promise<T> {
    const fn = () => this.instance.post<T>(url, data, config)
    const response = config?.retry
      ? await this.retryWithBackoff(fn, config.retry)
      : await fn()

    // Invalidate related cache on POST
    this.clearCache(url.split('/')[1])

    return response.data
  }

  async put<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig & { retry?: RetryConfig }
  ): Promise<T> {
    const fn = () => this.instance.put<T>(url, data, config)
    const response = config?.retry
      ? await this.retryWithBackoff(fn, config.retry)
      : await fn()

    // Invalidate related cache on PUT
    this.clearCache(url.split('/')[1])

    return response.data
  }

  async delete<T = any>(
    url: string,
    config?: AxiosRequestConfig & { retry?: RetryConfig }
  ): Promise<T> {
    const fn = () => this.instance.delete<T>(url, config)
    const response = config?.retry
      ? await this.retryWithBackoff(fn, config.retry)
      : await fn()

    // Invalidate related cache on DELETE
    this.clearCache(url.split('/')[1])

    return response.data
  }

  async patch<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig & { retry?: RetryConfig }
  ): Promise<T> {
    const fn = () => this.instance.patch<T>(url, data, config)
    const response = config?.retry
      ? await this.retryWithBackoff(fn, config.retry)
      : await fn()

    // Invalidate related cache on PATCH
    this.clearCache(url.split('/')[1])

    return response.data
  }

  // Utility methods
  setAuthToken(token: string): void {
    localStorage.setItem('token', token)
  }

  clearAuthToken(): void {
    localStorage.removeItem('token')
  }

  getRequestQueue(): Map<string, Promise<any>> {
    return this.requestQueue
  }

  getCacheSize(): number {
    return this.cache.size
  }

  clearAllCache(): void {
    this.clearCache()
  }
}

// Create and export singleton instance
const apiClient = new ApiClient()

export default apiClient
