import { createSlice, PayloadAction, createAsyncThunk } from '@reduxjs/toolkit'
import { agentAPI } from '../../services/api'

export interface Agent {
  id: string
  name: string
  type: 'research' | 'planner' | 'refactor' | 'evaluator' | 'service_creator'
  status: 'active' | 'idle' | 'error' | 'stopped'
  lastActivity: string
  metrics: {
    tasksCompleted: number
    successRate: number
    avgExecutionTime: number
  }
  currentTask?: string
  cpuUsage?: number
  memoryUsage?: number
}

interface AgentsState {
  agents: Agent[]
  loading: boolean
  error: string | null
}

const initialState: AgentsState = {
  agents: [],
  loading: false,
  error: null,
}

export const fetchAgents = createAsyncThunk(
  'agents/fetchAgents',
  async () => {
    const response = await agentAPI.getAgents()
    return response.data
  }
)

export const startAgent = createAsyncThunk(
  'agents/start',
  async (agentId: string) => {
    const response = await agentAPI.startAgent(agentId)
    return response.data
  }
)

export const stopAgent = createAsyncThunk(
  'agents/stop',
  async (agentId: string) => {
    const response = await agentAPI.stopAgent(agentId)
    return response.data
  }
)

const agentsSlice = createSlice({
  name: 'agents',
  initialState,
  reducers: {
    setAgents: (state, action: PayloadAction<Agent[]>) => {
      state.agents = action.payload
    },
    updateAgentStatus: (state, action: PayloadAction<{ id: string; status: Agent['status'] }>) => {
      const agent = state.agents.find(a => a.id === action.payload.id)
      if (agent) {
        agent.status = action.payload.status
      }
    },
    updateAgentMetrics: (state, action: PayloadAction<{ id: string; metrics: Partial<Agent['metrics']> }>) => {
      const agent = state.agents.find(a => a.id === action.payload.id)
      if (agent) {
        agent.metrics = { ...agent.metrics, ...action.payload.metrics }
      }
    },
    setAgentTask: (state, action: PayloadAction<{ id: string; task: string }>) => {
      const agent = state.agents.find(a => a.id === action.payload.id)
      if (agent) {
        agent.currentTask = action.payload.task
      }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchAgents.pending, (state) => {
        state.loading = true
      })
      .addCase(fetchAgents.fulfilled, (state, action) => {
        state.loading = false
        state.agents = action.payload
      })
      .addCase(fetchAgents.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || 'Failed to fetch agents'
      })
  },
})

export const { setAgents, updateAgentStatus, updateAgentMetrics, setAgentTask } = agentsSlice.actions
export default agentsSlice.reducer
