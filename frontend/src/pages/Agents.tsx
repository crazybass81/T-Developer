import React, { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Grid,
  Paper,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  CircularProgress,
  IconButton,
  Tooltip,
} from '@mui/material'
import {
  Add as AddIcon,
  Refresh as RefreshIcon,
  Delete as DeleteIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
} from '@mui/icons-material'
import AgentStatusCard from '../components/AgentStatusCard'
import { useAppSelector, useAppDispatch } from '../store/hooks'
import { setAgents, updateAgentStatus } from '../store/slices/agentsSlice'
import agentApi from '../services/agentApi'
import toast from 'react-hot-toast'

const Agents: React.FC = () => {
  const dispatch = useAppDispatch()
  const agents = useAppSelector(state => state.agents.agents)
  const [openDialog, setOpenDialog] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [newAgent, setNewAgent] = useState({
    name: '',
    type: 'research' as const,
    config: {},
  })

  const loadAgents = async () => {
    setLoading(true)
    try {
      const agentsList = await agentApi.getAll()
      dispatch(setAgents(agentsList))
    } catch (error: any) {
      console.error('Failed to load agents:', error)
      setError(error.message || 'Failed to load agents')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateAgent = async () => {
    setLoading(true)
    try {
      const createdAgent = await agentApi.create({
        name: newAgent.name,
        type: newAgent.type,
        config: newAgent.config,
      })

      // Reload agents list
      await loadAgents()

      toast.success(`Agent ${newAgent.name} created successfully`)
      setOpenDialog(false)
      setNewAgent({ name: '', type: 'research', config: {} })
    } catch (error: any) {
      toast.error(error.message || 'Failed to create agent')
    } finally {
      setLoading(false)
    }
  }

  const handleStartAgent = async (agentId: string) => {
    try {
      await agentApi.execute(agentId, {})
      dispatch(updateAgentStatus({ id: agentId, status: 'running' }))
      toast.success('Agent started')
    } catch (error: any) {
      toast.error(error.message || 'Failed to start agent')
    }
  }

  const handleStopAgent = async (agentId: string) => {
    try {
      await agentApi.stop(agentId)
      dispatch(updateAgentStatus({ id: agentId, status: 'idle' }))
      toast.success('Agent stopped')
    } catch (error: any) {
      toast.error(error.message || 'Failed to stop agent')
    }
  }

  const handleDeleteAgent = async (agentId: string) => {
    if (!window.confirm('Are you sure you want to delete this agent?')) return

    try {
      await agentApi.delete(agentId)
      await loadAgents()
      toast.success('Agent deleted')
    } catch (error: any) {
      toast.error(error.message || 'Failed to delete agent')
    }
  }

  useEffect(() => {
    loadAgents()
  }, [])

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Agents Management</Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadAgents}
            disabled={loading}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpenDialog(true)}
          >
            Create Agent
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
        </Box>
      )}

      <Grid container spacing={3}>
        {agents.map((agent) => (
          <Grid item xs={12} md={6} lg={4} key={agent.id}>
            <Paper sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                <Box sx={{ flex: 1 }}>
                  <AgentStatusCard agent={agent} />
                </Box>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Tooltip title={agent.status === 'running' ? 'Stop' : 'Start'}>
                    <IconButton
                      size="small"
                      onClick={() => agent.status === 'running' ? handleStopAgent(agent.id) : handleStartAgent(agent.id)}
                      color={agent.status === 'running' ? 'error' : 'primary'}
                    >
                      {agent.status === 'running' ? <StopIcon /> : <PlayIcon />}
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Delete">
                    <IconButton
                      size="small"
                      onClick={() => handleDeleteAgent(agent.id)}
                      color="error"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Tooltip>
                </Box>
              </Box>
              <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid rgba(255,255,255,0.1)' }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Performance Metrics
                </Typography>
                <Grid container spacing={1}>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      Avg Execution
                    </Typography>
                    <Typography variant="body1">
                      {agent.metrics.avgExecutionTime}s
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      CPU Usage
                    </Typography>
                    <Typography variant="body1">
                      {agent.cpuUsage || 0}%
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      Memory
                    </Typography>
                    <Typography variant="body1">
                      {agent.memoryUsage || 0}MB
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      Last Active
                    </Typography>
                    <Typography variant="body1">
                      {agent.lastActivity}
                    </Typography>
                  </Grid>
                </Grid>
              </Box>
            </Paper>
          </Grid>
        ))}
      </Grid>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Agent</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <TextField
              label="Agent Name"
              value={newAgent.name}
              onChange={(e) => setNewAgent({ ...newAgent, name: e.target.value })}
              fullWidth
            />
            <FormControl fullWidth>
              <InputLabel>Agent Type</InputLabel>
              <Select
                value={newAgent.type}
                label="Agent Type"
                onChange={(e) => setNewAgent({ ...newAgent, type: e.target.value as any })}
              >
                <MenuItem value="research">Research Agent</MenuItem>
                <MenuItem value="planner">Planner Agent</MenuItem>
                <MenuItem value="refactor">Refactor Agent</MenuItem>
                <MenuItem value="evaluator">Evaluator Agent</MenuItem>
                <MenuItem value="service_creator">Service Creator</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)} disabled={loading}>Cancel</Button>
          <Button
            onClick={handleCreateAgent}
            variant="contained"
            disabled={loading || !newAgent.name}
            startIcon={loading && <CircularProgress size={20} />}
          >
            {loading ? 'Creating...' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default Agents
