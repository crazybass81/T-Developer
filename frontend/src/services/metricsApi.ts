import apiClient from './apiClient'
import {
  ApiEndpoint,
  MetricData,
  MetricSummary,
  TimeSeriesData,
  EvolutionMetrics
} from '../types/api'

interface MetricRange {
  start: Date | string
  end: Date | string
}

interface MetricFilter {
  name?: string[]
  tags?: Record<string, string>
  aggregation?: 'sum' | 'avg' | 'min' | 'max' | 'count'
  interval?: '1m' | '5m' | '15m' | '1h' | '1d'
}

class MetricsAPI {
  private realtimeCallbacks: Set<(data: MetricData) => void> = new Set()
  private realtimeInterval: NodeJS.Timeout | null = null
  private isRealtimeActive: boolean = false

  /**
   * Get metrics within a time range
   */
  async getMetrics(range?: MetricRange, filter?: MetricFilter): Promise<MetricData[]> {
    const params = new URLSearchParams()

    if (range) {
      params.append('start', new Date(range.start).toISOString())
      params.append('end', new Date(range.end).toISOString())
    }

    if (filter) {
      if (filter.name) params.append('name', filter.name.join(','))
      if (filter.tags) params.append('tags', JSON.stringify(filter.tags))
      if (filter.aggregation) params.append('aggregation', filter.aggregation)
      if (filter.interval) params.append('interval', filter.interval)
    }

    const url = params.toString()
      ? `${ApiEndpoint.METRICS}?${params.toString()}`
      : ApiEndpoint.METRICS

    return await apiClient.get<MetricData[]>(url, {
      cache: {
        key: `metrics-${params.toString()}`,
        ttl: 10000 // Cache for 10 seconds
      }
    })
  }

  /**
   * Get realtime metrics
   */
  async getRealtimeMetrics(): Promise<MetricData[]> {
    return await apiClient.get<MetricData[]>(ApiEndpoint.METRICS_REALTIME, {
      cache: {
        key: 'metrics-realtime',
        ttl: 1000 // Cache for 1 second
      }
    })
  }

  /**
   * Get metrics summary
   */
  async getSummary(): Promise<MetricSummary> {
    return await apiClient.get<MetricSummary>(ApiEndpoint.METRICS_SUMMARY, {
      cache: {
        key: 'metrics-summary',
        ttl: 5000 // Cache for 5 seconds
      }
    })
  }

  /**
   * Get time series data for a specific metric
   */
  async getTimeSeries(
    metricName: string,
    range?: MetricRange,
    interval: string = '5m'
  ): Promise<TimeSeriesData> {
    const params = new URLSearchParams()
    params.append('name', metricName)
    params.append('interval', interval)

    if (range) {
      params.append('start', new Date(range.start).toISOString())
      params.append('end', new Date(range.end).toISOString())
    }

    const url = `${ApiEndpoint.METRICS_HISTORY}?${params.toString()}`

    return await apiClient.get<TimeSeriesData>(url, {
      cache: {
        key: `metrics-timeseries-${params.toString()}`,
        ttl: 30000 // Cache for 30 seconds
      }
    })
  }

  /**
   * Get evolution metrics comparison
   */
  async getEvolutionComparison(
    evolutionIds: string[]
  ): Promise<Record<string, EvolutionMetrics>> {
    const params = new URLSearchParams()
    params.append('ids', evolutionIds.join(','))

    const url = `${ApiEndpoint.METRICS}/evolution/compare?${params.toString()}`

    return await apiClient.get(url, {
      cache: {
        key: `metrics-evolution-compare-${evolutionIds.join('-')}`,
        ttl: 60000 // Cache for 1 minute
      }
    })
  }

  /**
   * Get system health metrics
   */
  async getSystemHealth(): Promise<{
    cpu: number
    memory: number
    disk: number
    network: number
    uptime: number
    status: 'healthy' | 'degraded' | 'critical'
  }> {
    return await apiClient.get('/api/metrics/health', {
      cache: {
        key: 'metrics-health',
        ttl: 3000 // Cache for 3 seconds
      }
    })
  }

  /**
   * Get agent performance metrics
   */
  async getAgentPerformance(agentId?: string): Promise<any> {
    const url = agentId
      ? `/api/metrics/agents/${agentId}`
      : '/api/metrics/agents'

    return await apiClient.get(url, {
      cache: {
        key: `metrics-agent-performance-${agentId || 'all'}`,
        ttl: 5000 // Cache for 5 seconds
      }
    })
  }

  /**
   * Start realtime metrics updates
   */
  startRealtimeUpdates(callback: (data: MetricData) => void, interval: number = 2000): void {
    this.realtimeCallbacks.add(callback)

    if (!this.isRealtimeActive) {
      this.isRealtimeActive = true
      this.realtimeInterval = setInterval(async () => {
        try {
          const metrics = await this.getRealtimeMetrics()

          // Notify all callbacks
          this.realtimeCallbacks.forEach(cb => {
            metrics.forEach(metric => cb(metric))
          })
        } catch (error) {
          console.error('Error fetching realtime metrics:', error)
        }
      }, interval)
    }
  }

  /**
   * Stop realtime metrics updates
   */
  stopRealtimeUpdates(callback?: (data: MetricData) => void): void {
    if (callback) {
      this.realtimeCallbacks.delete(callback)
    }

    if (this.realtimeCallbacks.size === 0 && this.realtimeInterval) {
      clearInterval(this.realtimeInterval)
      this.realtimeInterval = null
      this.isRealtimeActive = false
    }
  }

  /**
   * Calculate metric statistics
   */
  calculateStats(metrics: MetricData[]): {
    min: number
    max: number
    avg: number
    sum: number
    count: number
    stdDev: number
  } {
    if (metrics.length === 0) {
      return { min: 0, max: 0, avg: 0, sum: 0, count: 0, stdDev: 0 }
    }

    const values = metrics.map(m => m.value)
    const sum = values.reduce((a, b) => a + b, 0)
    const avg = sum / values.length
    const min = Math.min(...values)
    const max = Math.max(...values)

    // Calculate standard deviation
    const squaredDiffs = values.map(v => Math.pow(v - avg, 2))
    const avgSquaredDiff = squaredDiffs.reduce((a, b) => a + b, 0) / values.length
    const stdDev = Math.sqrt(avgSquaredDiff)

    return { min, max, avg, sum, count: values.length, stdDev }
  }

  /**
   * Get metric trends
   */
  async getMetricTrends(
    metricName: string,
    period: '1h' | '1d' | '1w' | '1m' = '1d'
  ): Promise<{
    current: number
    previous: number
    change: number
    changePercent: number
    trend: 'up' | 'down' | 'stable'
  }> {
    const now = new Date()
    const periodMs = {
      '1h': 3600000,
      '1d': 86400000,
      '1w': 604800000,
      '1m': 2592000000
    }[period]

    const currentRange = {
      start: new Date(now.getTime() - periodMs),
      end: now
    }

    const previousRange = {
      start: new Date(now.getTime() - (periodMs * 2)),
      end: new Date(now.getTime() - periodMs)
    }

    const [currentMetrics, previousMetrics] = await Promise.all([
      this.getMetrics(currentRange, { name: [metricName] }),
      this.getMetrics(previousRange, { name: [metricName] })
    ])

    const currentStats = this.calculateStats(currentMetrics)
    const previousStats = this.calculateStats(previousMetrics)

    const change = currentStats.avg - previousStats.avg
    const changePercent = previousStats.avg !== 0
      ? (change / previousStats.avg) * 100
      : 0

    const trend = Math.abs(changePercent) < 5
      ? 'stable'
      : change > 0
        ? 'up'
        : 'down'

    return {
      current: currentStats.avg,
      previous: previousStats.avg,
      change,
      changePercent,
      trend
    }
  }

  /**
   * Export metrics data
   */
  async exportMetrics(
    range?: MetricRange,
    format: 'json' | 'csv' = 'json'
  ): Promise<Blob> {
    const params = new URLSearchParams()
    params.append('format', format)

    if (range) {
      params.append('start', new Date(range.start).toISOString())
      params.append('end', new Date(range.end).toISOString())
    }

    const response = await apiClient.get(
      `/api/metrics/export?${params.toString()}`,
      {
        responseType: 'blob'
      }
    )

    return new Blob([response], {
      type: format === 'json' ? 'application/json' : 'text/csv'
    })
  }

  /**
   * Set metric alert
   */
  async setAlert(config: {
    metric: string
    threshold: number
    condition: 'above' | 'below'
    duration?: number
    webhook?: string
  }): Promise<{ id: string; active: boolean }> {
    return await apiClient.post('/api/metrics/alerts', config)
  }

  /**
   * Get active alerts
   */
  async getAlerts(): Promise<any[]> {
    return await apiClient.get('/api/metrics/alerts')
  }

  /**
   * Clean up resources
   */
  cleanup(): void {
    if (this.realtimeInterval) {
      clearInterval(this.realtimeInterval)
      this.realtimeInterval = null
    }
    this.realtimeCallbacks.clear()
    this.isRealtimeActive = false
  }
}

// Create and export singleton instance
const metricsAPI = new MetricsAPI()

export default metricsAPI
