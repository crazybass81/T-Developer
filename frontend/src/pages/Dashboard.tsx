import React, { useEffect } from 'react'
import { Grid, Paper, Box, Typography, Card, CardContent } from '@mui/material'
import {
  TrendingUp as TrendingUpIcon,
  CheckCircle as CheckCircleIcon,
  Code as CodeIcon,
  Memory as MemoryIcon,
} from '@mui/icons-material'
import { motion } from 'framer-motion'
import StatsCard from '../components/StatsCard'
import AgentStatusCard from '../components/AgentStatusCard'
import MetricsChart from '../components/MetricsChart'
import RecentTasks from '../components/RecentTasks'
import { useAppSelector, useAppDispatch } from '../store/hooks'
import { fetchAgents } from '../store/slices/agentsSlice'

const Dashboard: React.FC = () => {
  const dispatch = useAppDispatch()
  const agents = useAppSelector(state => state.agents.agents)
  const metrics = useAppSelector(state => state.metrics.summary)

  useEffect(() => {
    // Fetch initial data
    dispatch(fetchAgents())
  }, [dispatch])

  const stats = [
    {
      title: 'Total Tasks',
      value: metrics.totalTasks.toString(),
      icon: <TrendingUpIcon />,
      color: '#3b82f6',
      change: '+12%',
    },
    {
      title: 'Success Rate',
      value: `${metrics.successRate}%`,
      icon: <CheckCircleIcon />,
      color: '#10b981',
      change: '+5%',
    },
    {
      title: 'Code Improved',
      value: `${(metrics.codeImproved / 1000).toFixed(1)}K`,
      icon: <CodeIcon />,
      color: '#8b5cf6',
      change: '+18%',
    },
    {
      title: 'Active Agents',
      value: metrics.activeAgents.toString(),
      icon: <MemoryIcon />,
      color: '#f59e0b',
      change: '0',
    },
  ]

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        Dashboard
      </Typography>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {stats.map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <StatsCard {...stat} />
            </motion.div>
          </Grid>
        ))}
      </Grid>

      {/* Main Content */}
      <Grid container spacing={3}>
        {/* Agents Status */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Agent Status
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {agents.map((agent) => (
                <AgentStatusCard key={agent.id} agent={agent} />
              ))}
            </Box>
          </Paper>
        </Grid>

        {/* Metrics Chart */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Performance Metrics
            </Typography>
            <MetricsChart />
          </Paper>
        </Grid>

        {/* Recent Tasks */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Tasks
            </Typography>
            <RecentTasks />
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}

export default Dashboard
