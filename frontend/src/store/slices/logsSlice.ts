import { createSlice, PayloadAction } from '@reduxjs/toolkit'

export interface LogEntry {
  id: string
  timestamp: string
  level: 'debug' | 'info' | 'warning' | 'error' | 'critical'
  source: string
  message: string
  details?: any
}

interface LogsState {
  entries: LogEntry[]
  filters: {
    level: string[]
    source: string[]
    search: string
  }
  maxEntries: number
  isPaused: boolean
}

const initialState: LogsState = {
  entries: [],
  filters: {
    level: [],
    source: [],
    search: '',
  },
  maxEntries: 1000,
  isPaused: false,
}

const logsSlice = createSlice({
  name: 'logs',
  initialState,
  reducers: {
    addLog: (state, action: PayloadAction<LogEntry>) => {
      if (!state.isPaused) {
        state.entries.unshift(action.payload)
        if (state.entries.length > state.maxEntries) {
          state.entries.pop()
        }
      }
    },
    addLogs: (state, action: PayloadAction<LogEntry[]>) => {
      if (!state.isPaused) {
        state.entries = [...action.payload, ...state.entries].slice(0, state.maxEntries)
      }
    },
    clearLogs: (state) => {
      state.entries = []
    },
    setFilter: (state, action: PayloadAction<{ key: keyof LogsState['filters']; value: any }>) => {
      state.filters[action.payload.key] = action.payload.value
    },
    togglePause: (state) => {
      state.isPaused = !state.isPaused
    },
  },
})

export const { addLog, addLogs, clearLogs, setFilter, togglePause } = logsSlice.actions
export default logsSlice.reducer
