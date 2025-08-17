import React, { useState, useRef, useEffect } from 'react'
import {
  Box,
  Typography,
  Paper,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  IconButton,
  Chip,
  Stack,
} from '@mui/material'
import {
  Pause as PauseIcon,
  PlayArrow as PlayIcon,
  Clear as ClearIcon,
  Download as DownloadIcon,
} from '@mui/icons-material'
import { useAppSelector, useAppDispatch } from '../store/hooks'
import { togglePause, clearLogs, setFilter } from '../store/slices/logsSlice'

const Logs: React.FC = () => {
  const dispatch = useAppDispatch()
  const { entries, filters, isPaused } = useAppSelector(state => state.logs)
  const logContainerRef = useRef<HTMLDivElement>(null)
  const [autoScroll, setAutoScroll] = useState(true)

  useEffect(() => {
    if (autoScroll && logContainerRef.current && !isPaused) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight
    }
  }, [entries, autoScroll, isPaused])

  const getLogColor = (level: string) => {
    switch (level) {
      case 'error': return 'error.main'
      case 'warning': return 'warning.main'
      case 'info': return 'info.main'
      case 'debug': return 'text.secondary'
      case 'critical': return 'error.dark'
      default: return 'text.primary'
    }
  }

  const getLevelChipColor = (level: string) => {
    switch (level) {
      case 'error': return 'error'
      case 'warning': return 'warning'
      case 'info': return 'info'
      case 'debug': return 'default'
      case 'critical': return 'error'
      default: return 'default' as const
    }
  }

  const filteredLogs = entries.filter(log => {
    if (filters.level.length > 0 && !filters.level.includes(log.level)) {
      return false
    }
    if (filters.source.length > 0 && !filters.source.includes(log.source)) {
      return false
    }
    if (filters.search && !log.message.toLowerCase().includes(filters.search.toLowerCase())) {
      return false
    }
    return true
  })

  const exportLogs = () => {
    const data = JSON.stringify(filteredLogs, null, 2)
    const blob = new Blob([data], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `logs-${new Date().toISOString()}.json`
    a.click()
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        System Logs
      </Typography>

      <Paper sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <TextField
            label="Search"
            variant="outlined"
            size="small"
            value={filters.search}
            onChange={(e) => dispatch(setFilter({ key: 'search', value: e.target.value }))}
            sx={{ flexGrow: 1 }}
          />

          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Level</InputLabel>
            <Select
              multiple
              value={filters.level}
              label="Level"
              onChange={(e) => dispatch(setFilter({ key: 'level', value: e.target.value }))}
            >
              <MenuItem value="debug">Debug</MenuItem>
              <MenuItem value="info">Info</MenuItem>
              <MenuItem value="warning">Warning</MenuItem>
              <MenuItem value="error">Error</MenuItem>
              <MenuItem value="critical">Critical</MenuItem>
            </Select>
          </FormControl>

          <Stack direction="row" spacing={1}>
            <IconButton
              onClick={() => dispatch(togglePause())}
              color={isPaused ? 'error' : 'primary'}
            >
              {isPaused ? <PlayIcon /> : <PauseIcon />}
            </IconButton>
            <IconButton onClick={() => dispatch(clearLogs())}>
              <ClearIcon />
            </IconButton>
            <IconButton onClick={exportLogs}>
              <DownloadIcon />
            </IconButton>
          </Stack>
        </Box>
      </Paper>

      <Paper
        ref={logContainerRef}
        sx={{
          p: 2,
          height: 'calc(100vh - 300px)',
          overflow: 'auto',
          backgroundColor: '#0a0a0a',
          fontFamily: 'monospace',
        }}
      >
        {filteredLogs.map((log) => (
          <Box
            key={log.id}
            sx={{
              py: 0.5,
              borderBottom: '1px solid rgba(255,255,255,0.05)',
              '&:hover': {
                backgroundColor: 'rgba(255,255,255,0.02)',
              },
            }}
          >
            <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-start' }}>
              <Typography variant="caption" sx={{ color: 'text.secondary', minWidth: 150 }}>
                {log.timestamp}
              </Typography>
              <Chip
                label={log.level.toUpperCase()}
                size="small"
                color={getLevelChipColor(log.level)}
                sx={{ minWidth: 80 }}
              />
              <Typography variant="caption" sx={{ color: 'primary.main', minWidth: 120 }}>
                [{log.source}]
              </Typography>
              <Typography
                variant="body2"
                sx={{
                  color: getLogColor(log.level),
                  flexGrow: 1,
                  wordBreak: 'break-word',
                }}
              >
                {log.message}
              </Typography>
            </Box>
            {log.details && (
              <Box sx={{ ml: '380px', mt: 0.5 }}>
                <Typography variant="caption" sx={{ color: 'text.secondary', fontFamily: 'monospace' }}>
                  {JSON.stringify(log.details, null, 2)}
                </Typography>
              </Box>
            )}
          </Box>
        ))}
        {isPaused && (
          <Box sx={{ textAlign: 'center', py: 2 }}>
            <Chip label="PAUSED" color="error" />
          </Box>
        )}
      </Paper>
    </Box>
  )
}

export default Logs
