import { useEffect, useRef, useCallback } from 'react'
import { io, Socket } from 'socket.io-client'
import { useAppDispatch } from '../store/hooks'
import { updateAgentStatus, updateAgentMetrics } from '../store/slices/agentsSlice'
import { addLog } from '../store/slices/logsSlice'
import { updateRealTimeData, addMetricPoint } from '../store/slices/metricsSlice'
import { updateCurrentCycle, setPhase } from '../store/slices/evolutionSlice'
import toast from 'react-hot-toast'

const WS_URL = import.meta.env.MODE === 'production'
  ? 'wss://api.t-developer.io'
  : 'ws://localhost:8000'

export const useWebSocket = () => {
  const dispatch = useAppDispatch()
  const socketRef = useRef<Socket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()
  const reconnectAttemptsRef = useRef(0)

  const connect = useCallback(() => {
    if (socketRef.current?.connected) return

    const socket = io(WS_URL, {
      transports: ['websocket'],
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
    })

    socket.on('connect', () => {
      console.log('WebSocket connected')
      toast.success('Connected to server')
      reconnectAttemptsRef.current = 0
    })

    socket.on('disconnect', () => {
      console.log('WebSocket disconnected')
      // Don't show error toast on initial disconnect
      if (reconnectAttemptsRef.current > 0) {
        toast.error('Disconnected from server')
      }
    })

    socket.on('connect_error', (error) => {
      console.log('WebSocket connection error:', error.message)
      // Only show error after first attempt
      if (reconnectAttemptsRef.current === 0) {
        console.log('Backend server not available - running in offline mode')
      }
      reconnectAttemptsRef.current++
    })

    socket.on('agent:status', (data: any) => {
      dispatch(updateAgentStatus({ id: data.agentId, status: data.status }))
    })

    socket.on('agent:metrics', (data: any) => {
      dispatch(updateAgentMetrics({ id: data.agentId, metrics: data.metrics }))
    })

    socket.on('log:entry', (data: any) => {
      dispatch(addLog(data))
    })

    socket.on('metrics:realtime', (data: any) => {
      dispatch(updateRealTimeData(data))
    })

    socket.on('metrics:point', (data: any) => {
      dispatch(addMetricPoint({
        metric: data.metric,
        point: {
          timestamp: Date.now(),
          value: data.value,
          label: data.label,
        },
      }))
    })

    socket.on('evolution:update', (data: any) => {
      dispatch(updateCurrentCycle(data))
    })

    socket.on('evolution:phase', (data: any) => {
      dispatch(setPhase(data.phase))
      toast(`Evolution phase: ${data.phase}`, { icon: 'ℹ️' })
    })

    socket.on('notification', (data: any) => {
      const { type, message } = data
      switch (type) {
        case 'success':
          toast.success(message)
          break
        case 'error':
          toast.error(message)
          break
        case 'warning':
          toast(message, { icon: '⚠️' })
          break
        default:
          toast(message)
      }
    })

    socket.on('error', (error: any) => {
      console.error('WebSocket error:', error)
      toast.error(`Connection error: ${error.message}`)
    })

    socketRef.current = socket
  }, [dispatch])

  const disconnect = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.disconnect()
      socketRef.current = null
    }
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
  }, [])

  const emit = useCallback((event: string, data?: any) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit(event, data)
    } else {
      console.warn('WebSocket not connected, cannot emit event:', event)
    }
  }, [])

  const subscribe = useCallback((event: string, callback: (data: any) => void) => {
    if (socketRef.current) {
      socketRef.current.on(event, callback)
      return () => {
        socketRef.current?.off(event, callback)
      }
    }
  }, [])

  useEffect(() => {
    return () => {
      disconnect()
    }
  }, [disconnect])

  return {
    connect,
    disconnect,
    emit,
    subscribe,
    isConnected: socketRef.current?.connected ?? false,
  }
}
