import React from 'react'
import { Box, Typography, Chip, LinearProgress, IconButton } from '@mui/material'
import {
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Refresh as RestartIcon,
} from '@mui/icons-material'
import { Agent } from '../store/slices/agentsSlice'
import { useAppDispatch } from '../store/hooks'
import { startAgent, stopAgent } from '../store/slices/agentsSlice'
import toast from 'react-hot-toast'

interface AgentStatusCardProps {
  agent: Agent
}

const AgentStatusCard: React.FC<AgentStatusCardProps> = ({ agent }) => {
  const dispatch = useAppDispatch()

  const getStatusColor = (status: Agent['status']) => {
    switch (status) {
      case 'active': return 'success'
      case 'idle': return 'info'
      case 'error': return 'error'
      case 'stopped': return 'default'
      default: return 'default'
    }
  }

  const getAgentIcon = (type: Agent['type']) => {
    const icons: Record<Agent['type'], string> = {
      research: '🔍',
      planner: '📋',
      refactor: '🔧',
      evaluator: '📊',
      service_creator: '🏗️',
    }
    return icons[type] || '🤖'
  }

  const handleStart = async () => {
    try {
      await dispatch(startAgent(agent.id)).unwrap()
      toast.success(`${agent.name} started`)
    } catch (error) {
      toast.error(`Failed to start ${agent.name}`)
    }
  }

  const handleStop = async () => {
    try {
      await dispatch(stopAgent(agent.id)).unwrap()
      toast.success(`${agent.name} stopped`)
    } catch (error) {
      toast.error(`Failed to stop ${agent.name}`)
    }
  }

  return (
    <Box
      sx={{
        p: 2,
        borderRadius: 2,
        backgroundColor: 'rgba(255,255,255,0.05)',
        border: '1px solid rgba(255,255,255,0.1)',
      }}
    >
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="h6">{getAgentIcon(agent.type)}</Typography>
          <Typography variant="subtitle1" fontWeight={500}>
            {agent.name}
          </Typography>
        </Box>
        <Chip
          label={agent.status}
          color={getStatusColor(agent.status)}
          size="small"
        />
      </Box>

      {agent.currentTask && (
        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
          {agent.currentTask}
        </Typography>
      )}

      {agent.status === 'active' && (
        <Box sx={{ mb: 1 }}>
          <LinearProgress
            variant="determinate"
            value={Math.random() * 100}
            sx={{ height: 4, borderRadius: 2 }}
          />
        </Box>
      )}

      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="caption" color="text.secondary">
            Tasks: {agent.metrics.tasksCompleted} | Success: {agent.metrics.successRate}%
          </Typography>
        </Box>
        <Box>
          {agent.status === 'stopped' || agent.status === 'idle' ? (
            <IconButton size="small" onClick={handleStart} color="primary">
              <PlayIcon />
            </IconButton>
          ) : (
            <IconButton size="small" onClick={handleStop} color="error">
              <StopIcon />
            </IconButton>
          )}
          <IconButton size="small" color="default">
            <RestartIcon />
          </IconButton>
        </Box>
      </Box>
    </Box>
  )
}

export default AgentStatusCard
