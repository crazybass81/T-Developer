import { createSlice, PayloadAction, createAsyncThunk } from '@reduxjs/toolkit'
import { evolutionAPI } from '../../services/api'

export interface EvolutionCycle {
  id: string
  startTime: string
  endTime?: string
  status: 'running' | 'completed' | 'failed'
  phase: 'research' | 'planning' | 'implementation' | 'evaluation'
  target: string
  improvements: {
    docstring: number
    coverage: number
    complexity: number
    security: number
  }
  changes: string[]
  learnings: string[]
}

interface EvolutionState {
  currentCycle: EvolutionCycle | null
  history: EvolutionCycle[]
  isRunning: boolean
  autoMode: boolean
  config: {
    targetPath: string
    maxCycles: number
    minImprovement: number
    safetyChecks: boolean
  }
}

const initialState: EvolutionState = {
  currentCycle: null,
  history: [],
  isRunning: false,
  autoMode: false,
  config: {
    targetPath: './packages',
    maxCycles: 10,
    minImprovement: 0.05,
    safetyChecks: true,
  },
}

export const startEvolution = createAsyncThunk(
  'evolution/start',
  async (config: Partial<EvolutionState['config']>) => {
    const response = await evolutionAPI.startCycle(config)
    return response.data
  }
)

export const stopEvolution = createAsyncThunk(
  'evolution/stop',
  async () => {
    const response = await evolutionAPI.stopCycle()
    return response.data
  }
)

const evolutionSlice = createSlice({
  name: 'evolution',
  initialState,
  reducers: {
    updateCurrentCycle: (state, action: PayloadAction<Partial<EvolutionCycle>>) => {
      if (state.currentCycle) {
        state.currentCycle = { ...state.currentCycle, ...action.payload }
      }
    },
    setPhase: (state, action: PayloadAction<EvolutionCycle['phase']>) => {
      if (state.currentCycle) {
        state.currentCycle.phase = action.payload
      }
    },
    setCycles: (state, action: PayloadAction<EvolutionCycle[]>) => {
      state.history = action.payload
    },
    setEvolutionStatus: (state, action: PayloadAction<'running' | 'completed' | 'failed' | 'idle'>) => {
      state.isRunning = action.payload === 'running'
      if (state.currentCycle && action.payload !== 'running') {
        state.currentCycle.status = action.payload === 'completed' ? 'completed' : 'failed'
      }
    },
    completeCycle: (state, action: PayloadAction<EvolutionCycle>) => {
      state.history.unshift(action.payload)
      state.currentCycle = null
      state.isRunning = false
    },
    toggleAutoMode: (state) => {
      state.autoMode = !state.autoMode
    },
    updateConfig: (state, action: PayloadAction<Partial<EvolutionState['config']>>) => {
      state.config = { ...state.config, ...action.payload }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(startEvolution.fulfilled, (state, action) => {
        state.currentCycle = action.payload
        state.isRunning = true
      })
      .addCase(stopEvolution.fulfilled, (state) => {
        state.isRunning = false
        if (state.currentCycle) {
          state.currentCycle.status = 'failed'
        }
      })
  },
})

export const { updateCurrentCycle, setPhase, setCycles, setEvolutionStatus, completeCycle, toggleAutoMode, updateConfig } = evolutionSlice.actions
export default evolutionSlice.reducer
