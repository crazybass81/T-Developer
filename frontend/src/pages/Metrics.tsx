import React from 'react'
import { Box, Typography, Grid, Paper } from '@mui/material'
import MetricsChart from '../components/MetricsChart'
import { useAppSelector } from '../store/hooks'

const Metrics: React.FC = () => {
  const metrics = useAppSelector(state => state.metrics)

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        Performance Metrics
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              System Overview
            </Typography>
            <MetricsChart />
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Real-time Metrics
            </Typography>
            <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
              <Box>
                <Typography variant="caption" color="text.secondary">
                  CPU Usage
                </Typography>
                <Typography variant="h4">
                  {metrics.realTimeData.cpuUsage}%
                </Typography>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Memory Usage
                </Typography>
                <Typography variant="h4">
                  {metrics.realTimeData.memoryUsage}%
                </Typography>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Requests/sec
                </Typography>
                <Typography variant="h4">
                  {metrics.realTimeData.requestsPerSecond}
                </Typography>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Avg Response Time
                </Typography>
                <Typography variant="h4">
                  {metrics.realTimeData.avgResponseTime}ms
                </Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Quality Metrics
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Docstring Coverage
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Box sx={{ flexGrow: 1, height: 8, bgcolor: 'background.default', borderRadius: 1 }}>
                    <Box sx={{ width: '85%', height: '100%', bgcolor: 'success.main', borderRadius: 1 }} />
                  </Box>
                  <Typography variant="body2">85%</Typography>
                </Box>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Test Coverage
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Box sx={{ flexGrow: 1, height: 8, bgcolor: 'background.default', borderRadius: 1 }}>
                    <Box sx={{ width: '78%', height: '100%', bgcolor: 'warning.main', borderRadius: 1 }} />
                  </Box>
                  <Typography variant="body2">78%</Typography>
                </Box>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Code Complexity (MI)
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Box sx={{ flexGrow: 1, height: 8, bgcolor: 'background.default', borderRadius: 1 }}>
                    <Box sx={{ width: '72%', height: '100%', bgcolor: 'info.main', borderRadius: 1 }} />
                  </Box>
                  <Typography variant="body2">72</Typography>
                </Box>
              </Box>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}

export default Metrics
