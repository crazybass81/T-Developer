import React from 'react'
import { Drawer, List, ListItem, ListItemIcon, ListItemText, ListItemButton, Toolbar, Divider, Box } from '@mui/material'
import {
  Dashboard as DashboardIcon,
  Memory as AgentsIcon,
  Analytics as MetricsIcon,
  Description as LogsIcon,
  Science as EvolutionIcon,
  Settings as SettingsIcon,
  PlayCircle as RunIcon,
} from '@mui/icons-material'
import { useNavigate, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useAppDispatch } from '../store/hooks'
import { startEvolution } from '../store/slices/evolutionSlice'

const drawerWidth = 240

interface MenuItem {
  text: string
  icon: React.ReactElement
  path: string
}

const menuItems: MenuItem[] = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
  { text: 'Agents', icon: <AgentsIcon />, path: '/agents' },
  { text: 'Metrics', icon: <MetricsIcon />, path: '/metrics' },
  { text: 'Logs', icon: <LogsIcon />, path: '/logs' },
  { text: 'Evolution', icon: <EvolutionIcon />, path: '/evolution' },
  { text: 'Settings', icon: <SettingsIcon />, path: '/settings' },
]

const Sidebar: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const dispatch = useAppDispatch()

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
          backgroundColor: 'background.paper',
          borderRight: '1px solid rgba(255, 255, 255, 0.12)',
        },
      }}
    >
      <Toolbar />
      <Box sx={{ overflow: 'auto' }}>
        <List>
          {menuItems.map((item) => (
            <ListItem key={item.text} disablePadding>
              <ListItemButton
                selected={location.pathname === item.path}
                onClick={() => navigate(item.path)}
                sx={{
                  '&.Mui-selected': {
                    backgroundColor: 'rgba(59, 130, 246, 0.15)',
                    borderLeft: '3px solid #3b82f6',
                  },
                }}
              >
                <ListItemIcon sx={{ color: location.pathname === item.path ? 'primary.main' : 'inherit' }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText primary={item.text} />
              </ListItemButton>
            </ListItem>
          ))}
        </List>

        <Divider sx={{ my: 2 }} />

        <Box sx={{ px: 2 }}>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            style={{
              width: '100%',
              padding: '12px',
              backgroundColor: '#8b5cf6',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              fontWeight: 600,
            }}
            onClick={() => {
              dispatch(startEvolution({
                targetPath: './backend/packages',
                maxCycles: 5,
                minImprovement: 0.05,
                safetyChecks: true,
                dryRun: false,
                autoMode: true,
                config: {
                  focusAreas: ['documentation', 'testing', 'performance']
                }
              }))
            }}
          >
            <RunIcon />
            Self-Improve
          </motion.button>
        </Box>
      </Box>
    </Drawer>
  )
}

export default Sidebar
