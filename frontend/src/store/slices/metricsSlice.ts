import { createSlice, PayloadAction } from '@reduxjs/toolkit'

export interface Metric {
  timestamp: number
  value: number
  label: string
}

export interface MetricsData {
  docstringCoverage: Metric[]
  testCoverage: Metric[]
  codeComplexity: Metric[]
  performanceScore: Metric[]
  tasksCompleted: Metric[]
  evolutionCycles: Metric[]
}

interface MetricsState {
  data: MetricsData
  realTimeData: {
    cpuUsage: number
    memoryUsage: number
    requestsPerSecond: number
    avgResponseTime: number
  }
  summary: {
    totalTasks: number
    successRate: number
    codeImproved: number
    activeAgents: number
  }
}

const initialState: MetricsState = {
  data: {
    docstringCoverage: [],
    testCoverage: [],
    codeComplexity: [],
    performanceScore: [],
    tasksCompleted: [],
    evolutionCycles: [],
  },
  realTimeData: {
    cpuUsage: 0,
    memoryUsage: 0,
    requestsPerSecond: 0,
    avgResponseTime: 0,
  },
  summary: {
    totalTasks: 0,
    successRate: 0,
    codeImproved: 0,
    activeAgents: 0,
  }
}

const metricsSlice = createSlice({
  name: 'metrics',
  initialState,
  reducers: {
    updateMetrics: (state, action: PayloadAction<Partial<MetricsData>>) => {
      Object.entries(action.payload).forEach(([key, value]) => {
        if (key in state.data) {
          state.data[key as keyof MetricsData] = value as Metric[]
        }
      })
    },
    updateRealTimeData: (state, action: PayloadAction<Partial<MetricsState['realTimeData']>>) => {
      state.realTimeData = { ...state.realTimeData, ...action.payload }
    },
    updateSummary: (state, action: PayloadAction<Partial<MetricsState['summary']>>) => {
      state.summary = { ...state.summary, ...action.payload }
    },
    addMetricPoint: (state, action: PayloadAction<{ metric: keyof MetricsData; point: Metric }>) => {
      const metricArray = state.data[action.payload.metric]
      metricArray.push(action.payload.point)
      // Keep only last 100 points
      if (metricArray.length > 100) {
        metricArray.shift()
      }
    },
  },
})

export const { updateMetrics, updateRealTimeData, updateSummary, addMetricPoint } = metricsSlice.actions
export default metricsSlice.reducer
