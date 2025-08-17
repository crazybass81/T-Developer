import React from 'react'
import { Card, CardContent, Box, Typography, Chip } from '@mui/material'
import { motion } from 'framer-motion'

interface StatsCardProps {
  title: string
  value: string
  icon: React.ReactElement
  color: string
  change?: string
}

const StatsCard: React.FC<StatsCardProps> = ({ title, value, icon, color, change }) => {
  return (
    <Card
      component={motion.div}
      whileHover={{ scale: 1.02 }}
      sx={{
        height: '100%',
        background: 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255,255,255,0.1)',
      }}
    >
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box>
            <Typography color="text.secondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h4" component="div" sx={{ fontWeight: 600, my: 1 }}>
              {value}
            </Typography>
            {change && (
              <Chip
                label={change}
                size="small"
                color={change.startsWith('+') ? 'success' : change === '0' ? 'default' : 'error'}
                sx={{ mt: 1 }}
              />
            )}
          </Box>
          <Box
            sx={{
              p: 1.5,
              borderRadius: 2,
              backgroundColor: `${color}20`,
              color: color,
            }}
          >
            {React.cloneElement(icon, { fontSize: 'large' })}
          </Box>
        </Box>
      </CardContent>
    </Card>
  )
}

export default StatsCard
