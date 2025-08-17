import React, { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Paper,
  Button,
  TextField,
  Switch,
  FormControlLabel,
  Grid,
  Stepper,
  Step,
  StepLabel,
  Chip,
  LinearProgress,
  Alert,
  CircularProgress,
} from '@mui/material'
import {
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  AutoMode as AutoModeIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material'
import { useAppSelector, useAppDispatch } from '../store/hooks'
import { startEvolution, stopEvolution, toggleAutoMode, updateConfig } from '../store/slices/evolutionSlice'
import evolutionApi from '../services/evolutionApi'
import { EvolutionConfig } from '../types/api'
import toast from 'react-hot-toast'

const Evolution: React.FC = () => {
  const dispatch = useAppDispatch()
  const { currentCycle, history, isRunning, autoMode, config } = useAppSelector(state => state.evolution)
  const [localConfig, setLocalConfig] = useState<EvolutionConfig>({
    target_path: config.targetPath || './backend/packages',
    max_cycles: config.maxCycles || 5,
    focus_areas: config.focusAreas || ['docstring', 'type_hints', 'error_handling'],
    dry_run: config.dryRun ?? true,
    enable_code_modification: !config.dryRun,
    min_improvement: config.minImprovement || 0.05,
    safety_checks: config.safetyChecks ?? true
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const phases = ['research', 'planning', 'implementation', 'evaluation']
  const currentPhaseIndex = currentCycle ? phases.indexOf(currentCycle.phase) : -1

  const handleStart = async () => {
    setLoading(true)
    setError(null)
    try {
      // Update config in Redux
      await dispatch(updateConfig(localConfig))

      // Start evolution via API
      const response = await evolutionApi.start(localConfig)

      // Update Redux state
      await dispatch(startEvolution(localConfig)).unwrap()

      // Start polling for updates
      evolutionApi.pollEvolutionStatus(response.evolutionId)

      toast.success('Evolution cycle started')
    } catch (error: any) {
      const errorMessage = error.message || 'Failed to start evolution'
      setError(errorMessage)
      toast.error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const handleStop = async () => {
    setLoading(true)
    try {
      // Stop current evolution if exists
      if (currentCycle?.id) {
        await evolutionApi.stop(currentCycle.id)
      }

      await dispatch(stopEvolution()).unwrap()
      toast.success('Evolution cycle stopped')
    } catch (error: any) {
      const errorMessage = error.message || 'Failed to stop evolution'
      toast.error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const refreshHistory = async () => {
    try {
      const historyData = await evolutionApi.getHistory()
      // Dispatch action to update history in Redux
      // dispatch(setHistory(historyData))
    } catch (error) {
      console.error('Failed to fetch history:', error)
    }
  }

  useEffect(() => {
    // Load initial history on mount
    refreshHistory()
  }, [])

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        Self-Evolution System
      </Typography>

      <Grid container spacing={3}>
        {/* Control Panel */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Evolution Control
            </Typography>

            {error && (
              <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
                {error}
              </Alert>
            )}

            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <TextField
                label="Target Path"
                value={localConfig.target_path}
                onChange={(e) => setLocalConfig({ ...localConfig, target_path: e.target.value })}
                fullWidth
                placeholder="e.g., ./packages/agents"
                helperText="Path to the code you want to evolve"
              />

              <TextField
                label="Max Cycles"
                type="number"
                value={localConfig.max_cycles}
                onChange={(e) => setLocalConfig({ ...localConfig, max_cycles: parseInt(e.target.value) })}
                fullWidth
              />

              <TextField
                label="Min Improvement (%)"
                type="number"
                value={(localConfig.min_improvement || 0.05) * 100}
                onChange={(e) => setLocalConfig({ ...localConfig, min_improvement: parseFloat(e.target.value) / 100 })}
                fullWidth
              />

              <FormControlLabel
                control={
                  <Switch
                    checked={localConfig.safety_checks ?? true}
                    onChange={(e) => setLocalConfig({ ...localConfig, safety_checks: e.target.checked })}
                  />
                }
                label="Safety Checks"
              />

              <FormControlLabel
                control={
                  <Switch
                    checked={localConfig.dry_run ?? true}
                    onChange={(e) => setLocalConfig({ 
                      ...localConfig, 
                      dry_run: e.target.checked,
                      enable_code_modification: !e.target.checked
                    })}
                    color="warning"
                  />
                }
                label="Dry Run (Simulate changes)"
              />

              <FormControlLabel
                control={
                  <Switch
                    checked={autoMode}
                    onChange={() => dispatch(toggleAutoMode())}
                    color="secondary"
                  />
                }
                label="Auto Mode"
              />

              <Button
                variant="contained"
                color={isRunning ? 'error' : 'primary'}
                startIcon={loading ? <CircularProgress size={20} color="inherit" /> : (isRunning ? <StopIcon /> : <PlayIcon />)}
                onClick={isRunning ? handleStop : handleStart}
                disabled={loading}
                fullWidth
              >
                {loading ? 'Processing...' : (isRunning ? 'Stop Evolution' : 'Start Evolution')}
              </Button>

              {autoMode && (
                <Chip
                  icon={<AutoModeIcon />}
                  label="Auto Mode Active"
                  color="secondary"
                />
              )}
            </Box>
          </Paper>
        </Grid>

        {/* Current Cycle */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Current Evolution Cycle
            </Typography>

            {currentCycle ? (
              <Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Cycle ID: {currentCycle.id}
                  </Typography>
                  <Chip
                    label={currentCycle.status}
                    color={currentCycle.status === 'running' ? 'primary' :
                           currentCycle.status === 'completed' ? 'success' : 'error'}
                    size="small"
                  />
                </Box>

                <Stepper activeStep={currentPhaseIndex} sx={{ mb: 3 }}>
                  {phases.map((phase) => (
                    <Step key={phase}>
                      <StepLabel>{phase.charAt(0).toUpperCase() + phase.slice(1)}</StepLabel>
                    </Step>
                  ))}
                </Stepper>

                {currentCycle.status === 'running' && (
                  <LinearProgress sx={{ mb: 2 }} />
                )}

                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Target
                    </Typography>
                    <Typography variant="body1">
                      {currentCycle.target}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Started
                    </Typography>
                    <Typography variant="body1">
                      {new Date(currentCycle.startTime).toLocaleTimeString()}
                    </Typography>
                  </Grid>
                </Grid>

                <Box sx={{ mt: 3 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Improvements
                  </Typography>
                  <Grid container spacing={1}>
                    <Grid item xs={3}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h6">
                          +{currentCycle.improvements.docstring}%
                        </Typography>
                        <Typography variant="caption">Docstring</Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={3}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h6">
                          +{currentCycle.improvements.coverage}%
                        </Typography>
                        <Typography variant="caption">Coverage</Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={3}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h6">
                          +{currentCycle.improvements.complexity}
                        </Typography>
                        <Typography variant="caption">Complexity</Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={3}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h6">
                          +{currentCycle.improvements.security}
                        </Typography>
                        <Typography variant="caption">Security</Typography>
                      </Box>
                    </Grid>
                  </Grid>
                </Box>
              </Box>
            ) : (
              <Typography color="text.secondary">
                No evolution cycle in progress
              </Typography>
            )}
          </Paper>
        </Grid>

        {/* History */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                Evolution History
              </Typography>
              <Button
                size="small"
                startIcon={<RefreshIcon />}
                onClick={refreshHistory}
              >
                Refresh
              </Button>
            </Box>

            {history.length > 0 ? (
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {history.slice(0, 5).map((cycle) => (
                  <Box
                    key={cycle.id}
                    sx={{
                      p: 2,
                      borderRadius: 1,
                      backgroundColor: 'rgba(255,255,255,0.02)',
                      border: '1px solid rgba(255,255,255,0.1)',
                    }}
                  >
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body1">
                        {cycle.id}
                      </Typography>
                      <Chip
                        label={cycle.status}
                        color={cycle.status === 'completed' ? 'success' : 'error'}
                        size="small"
                      />
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      Target: {cycle.target} | Duration: {
                        cycle.endTime ?
                        `${Math.round((new Date(cycle.endTime).getTime() - new Date(cycle.startTime).getTime()) / 60000)}m` :
                        'N/A'
                      }
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 2, mt: 1 }}>
                      <Chip label={`Doc: +${cycle.improvements.docstring}%`} size="small" variant="outlined" />
                      <Chip label={`Test: +${cycle.improvements.coverage}%`} size="small" variant="outlined" />
                      <Chip label={`Complex: ${cycle.improvements.complexity}`} size="small" variant="outlined" />
                    </Box>
                  </Box>
                ))}
              </Box>
            ) : (
              <Typography color="text.secondary">
                No evolution history yet
              </Typography>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}

export default Evolution
