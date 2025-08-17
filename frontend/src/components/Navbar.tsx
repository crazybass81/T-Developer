import React from 'react'
import { AppBar, Toolbar, Typography, IconButton, Badge, Box, Chip } from '@mui/material'
import {
  Notifications as NotificationsIcon,
  Settings as SettingsIcon,
  WifiTethering as ConnectionIcon,
  WifiTetheringOff as DisconnectedIcon,
} from '@mui/icons-material'
import { useNavigate } from 'react-router-dom'
import { useAppSelector } from '../store/hooks'

const Navbar: React.FC = () => {
  const navigate = useNavigate()
  const isConnected = useAppSelector(state => state.websocket.connected)
  const activeAgents = useAppSelector(state =>
    state.agents.agents.filter(a => a.status === 'active').length
  )

  return (
    <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
      <Toolbar>
        <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
          <Typography variant="h6" noWrap component="div" sx={{ mr: 2 }}>
            T-Developer v2.0
          </Typography>
          <Typography variant="caption" sx={{ color: 'text.secondary' }}>
            Autonomous Code Evolution System
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Chip
            icon={isConnected ? <ConnectionIcon /> : <DisconnectedIcon />}
            label={isConnected ? 'Connected' : 'Disconnected'}
            color={isConnected ? 'success' : 'error'}
            size="small"
          />

          <Chip
            label={`${activeAgents} Agents Active`}
            color="primary"
            size="small"
          />

          <IconButton color="inherit">
            <Badge badgeContent={3} color="error">
              <NotificationsIcon />
            </Badge>
          </IconButton>

          <IconButton color="inherit" onClick={() => navigate('/settings')}>
            <SettingsIcon />
          </IconButton>
        </Box>
      </Toolbar>
    </AppBar>
  )
}

export default Navbar
