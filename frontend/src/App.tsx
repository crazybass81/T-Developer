import React, { useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Box } from '@mui/material'
import Navbar from './components/Navbar'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import Agents from './pages/Agents'
import Metrics from './pages/Metrics'
import Logs from './pages/Logs'
import Evolution from './pages/Evolution'
import Settings from './pages/Settings'
import { useAppDispatch } from './store/hooks'
import { connectWebSocket } from './store/middleware/websocket'

const App: React.FC = () => {
  const dispatch = useAppDispatch()

  useEffect(() => {
    // Connect to WebSocket on app mount using Redux middleware
    // Delay connection attempt to avoid blocking initial render
    const timer = setTimeout(() => {
      dispatch(connectWebSocket())
    }, 1000)
    return () => clearTimeout(timer)
  }, [dispatch])

  return (
    <Router>
      <Box sx={{ display: 'flex', minHeight: '100vh' }}>
        <Navbar />
        <Sidebar />
        <Box component="main" sx={{ flexGrow: 1, p: 3, mt: 8 }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/agents" element={<Agents />} />
            <Route path="/metrics" element={<Metrics />} />
            <Route path="/logs" element={<Logs />} />
            <Route path="/evolution" element={<Evolution />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </Box>
      </Box>
    </Router>
  )
}

export default App
