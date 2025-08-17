import React from 'react'
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Box,
  Typography,
} from '@mui/material'
import { format } from 'date-fns'

interface Task {
  id: string
  type: string
  target: string
  status: 'completed' | 'running' | 'failed' | 'pending'
  startTime: Date
  endTime?: Date
  agent: string
  improvement?: number
}

const RecentTasks: React.FC = () => {
  // Sample data - replace with real data from store
  const tasks: Task[] = [
    {
      id: 'task-001',
      type: 'Refactor',
      target: './packages/agents',
      status: 'completed',
      startTime: new Date(Date.now() - 3600000),
      endTime: new Date(Date.now() - 1800000),
      agent: 'RefactorAgent',
      improvement: 12.5,
    },
    {
      id: 'task-002',
      type: 'Research',
      target: './src/services',
      status: 'running',
      startTime: new Date(Date.now() - 600000),
      agent: 'ResearchAgent',
    },
    {
      id: 'task-003',
      type: 'Evaluate',
      target: './tests',
      status: 'failed',
      startTime: new Date(Date.now() - 7200000),
      endTime: new Date(Date.now() - 6000000),
      agent: 'EvaluatorAgent',
      improvement: -2.3,
    },
    {
      id: 'task-004',
      type: 'Plan',
      target: './docs',
      status: 'pending',
      startTime: new Date(Date.now() - 300000),
      agent: 'PlannerAgent',
    },
  ]

  const getStatusColor = (status: Task['status']) => {
    switch (status) {
      case 'completed': return 'success'
      case 'running': return 'info'
      case 'failed': return 'error'
      case 'pending': return 'default'
      default: return 'default'
    }
  }

  const getDuration = (start: Date, end?: Date) => {
    const endTime = end || new Date()
    const diff = endTime.getTime() - start.getTime()
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(minutes / 60)

    if (hours > 0) {
      return `${hours}h ${minutes % 60}m`
    }
    return `${minutes}m`
  }

  return (
    <TableContainer>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Task ID</TableCell>
            <TableCell>Type</TableCell>
            <TableCell>Target</TableCell>
            <TableCell>Agent</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Duration</TableCell>
            <TableCell>Improvement</TableCell>
            <TableCell>Started</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {tasks.map((task) => (
            <TableRow key={task.id} hover>
              <TableCell>
                <Typography variant="body2" fontFamily="monospace">
                  {task.id}
                </Typography>
              </TableCell>
              <TableCell>{task.type}</TableCell>
              <TableCell>
                <Typography variant="body2" fontFamily="monospace">
                  {task.target}
                </Typography>
              </TableCell>
              <TableCell>{task.agent}</TableCell>
              <TableCell>
                <Chip
                  label={task.status}
                  color={getStatusColor(task.status)}
                  size="small"
                />
              </TableCell>
              <TableCell>{getDuration(task.startTime, task.endTime)}</TableCell>
              <TableCell>
                {task.improvement !== undefined && (
                  <Chip
                    label={`${task.improvement > 0 ? '+' : ''}${task.improvement}%`}
                    color={task.improvement > 0 ? 'success' : 'error'}
                    size="small"
                    variant="outlined"
                  />
                )}
              </TableCell>
              <TableCell>{format(task.startTime, 'HH:mm:ss')}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  )
}

export default RecentTasks
