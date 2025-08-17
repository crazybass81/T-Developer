import React from 'react'
import {
  Box,
  Typography,
  Paper,
  TextField,
  Switch,
  FormControlLabel,
  Button,
  Divider,
  Grid,
} from '@mui/material'
import { Save as SaveIcon } from '@mui/icons-material'
import toast from 'react-hot-toast'

const Settings: React.FC = () => {
  const handleSave = () => {
    toast.success('Settings saved successfully')
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        Settings
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              General Settings
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <TextField
                label="API Endpoint"
                defaultValue="http://localhost:8000"
                fullWidth
              />
              <TextField
                label="WebSocket URL"
                defaultValue="ws://localhost:8000"
                fullWidth
              />
              <FormControlLabel
                control={<Switch defaultChecked />}
                label="Auto-connect on startup"
              />
              <FormControlLabel
                control={<Switch defaultChecked />}
                label="Enable notifications"
              />
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Evolution Settings
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <TextField
                label="Default Target Path"
                defaultValue="./packages"
                fullWidth
              />
              <TextField
                label="Max Concurrent Agents"
                type="number"
                defaultValue="4"
                fullWidth
              />
              <TextField
                label="Evolution Timeout (minutes)"
                type="number"
                defaultValue="30"
                fullWidth
              />
              <FormControlLabel
                control={<Switch defaultChecked />}
                label="Enable safety checks"
              />
              <FormControlLabel
                control={<Switch />}
                label="Auto-commit changes"
              />
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Performance Settings
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <TextField
                label="Log Buffer Size"
                type="number"
                defaultValue="1000"
                fullWidth
              />
              <TextField
                label="Metrics Retention (hours)"
                type="number"
                defaultValue="24"
                fullWidth
              />
              <FormControlLabel
                control={<Switch defaultChecked />}
                label="Enable real-time updates"
              />
              <FormControlLabel
                control={<Switch />}
                label="Debug mode"
              />
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              variant="contained"
              startIcon={<SaveIcon />}
              onClick={handleSave}
              size="large"
            >
              Save Settings
            </Button>
          </Box>
        </Grid>
      </Grid>
    </Box>
  )
}

export default Settings
