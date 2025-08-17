import React, { useEffect, useRef } from 'react'
import { Box } from '@mui/material'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'
import { Line } from 'react-chartjs-2'
import { useAppSelector } from '../store/hooks'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const MetricsChart: React.FC = () => {
  const metrics = useAppSelector(state => state.metrics.data)

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          color: 'white',
        },
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
      },
    },
    scales: {
      x: {
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
        ticks: {
          color: 'rgba(255, 255, 255, 0.7)',
        },
      },
      y: {
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
        ticks: {
          color: 'rgba(255, 255, 255, 0.7)',
        },
      },
    },
  }

  // Generate sample data for now
  const labels = Array.from({ length: 24 }, (_, i) => {
    const hour = new Date()
    hour.setHours(hour.getHours() - (23 - i))
    return hour.toLocaleTimeString('en-US', { hour: '2-digit' })
  })

  const data = {
    labels,
    datasets: [
      {
        label: 'Tasks Completed',
        data: Array.from({ length: 24 }, () => Math.floor(Math.random() * 50 + 20)),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
        fill: true,
      },
      {
        label: 'Code Quality',
        data: Array.from({ length: 24 }, () => Math.floor(Math.random() * 20 + 70)),
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        tension: 0.4,
        fill: true,
      },
      {
        label: 'Test Coverage',
        data: Array.from({ length: 24 }, () => Math.floor(Math.random() * 15 + 75)),
        borderColor: 'rgb(139, 92, 246)',
        backgroundColor: 'rgba(139, 92, 246, 0.1)',
        tension: 0.4,
        fill: true,
      },
    ],
  }

  return (
    <Box sx={{ height: 400, position: 'relative' }}>
      <Line options={options} data={data} />
    </Box>
  )
}

export default MetricsChart
