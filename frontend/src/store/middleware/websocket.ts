import { Middleware } from '@reduxjs/toolkit'
import websocketService from '../../services/websocket'
import { WebSocketMessageType } from '../../types/api'
import {
  updateAgentStatus,
  updateAgentMetrics,
  setAgents
} from '../slices/agentsSlice'
import {
  addLog,
  setLogs
} from '../slices/logsSlice'
import {
  updateRealTimeData,
  addMetricPoint,
  setMetrics
} from '../slices/metricsSlice'
import {
  updateCurrentCycle,
  setPhase,
  setCycles,
  setEvolutionStatus
} from '../slices/evolutionSlice'
import toast from 'react-hot-toast'

// WebSocket action types
const WS_CONNECT = 'websocket/connect'
const WS_DISCONNECT = 'websocket/disconnect'
const WS_SEND = 'websocket/send'
const WS_SUBSCRIBE = 'websocket/subscribe'
const WS_UNSUBSCRIBE = 'websocket/unsubscribe'

// WebSocket action creators
export const wsConnect = (config?: any) => ({
  type: WS_CONNECT,
  payload: config
})

export const wsDisconnect = () => ({
  type: WS_DISCONNECT
})

export const wsSend = (event: string, data?: any) => ({
  type: WS_SEND,
  payload: { event, data }
})

export const wsSubscribe = (event: string) => ({
  type: WS_SUBSCRIBE,
  payload: event
})

export const wsUnsubscribe = (event: string) => ({
  type: WS_UNSUBSCRIBE,
  payload: event
})

// WebSocket middleware
export const websocketMiddleware: Middleware = (store) => {
  // Setup message handlers
  const setupMessageHandlers = () => {
    // Connection handlers
    websocketService.onConnect(() => {
      console.log('WebSocket connected via middleware')
      toast.success('Connected to server')
      store.dispatch({ type: 'websocket/connected' })
    })

    websocketService.onDisconnect(() => {
      console.log('WebSocket disconnected via middleware')
      toast.error('Disconnected from server')
      store.dispatch({ type: 'websocket/disconnected' })
    })

    websocketService.onError((error) => {
      console.error('WebSocket error via middleware:', error)
      store.dispatch({ type: 'websocket/error', payload: error.message })
    })

    // Agent events
    websocketService.on(WebSocketMessageType.AGENT_STARTED, (data) => {
      store.dispatch(updateAgentStatus({
        id: data.agentId,
        status: 'running'
      }))
      toast.success(`Agent ${data.agentName || data.agentId} started`)
    })

    websocketService.on(WebSocketMessageType.AGENT_COMPLETED, (data) => {
      store.dispatch(updateAgentStatus({
        id: data.agentId,
        status: 'completed'
      }))
      toast.success(`Agent ${data.agentName || data.agentId} completed`)
    })

    websocketService.on(WebSocketMessageType.AGENT_FAILED, (data) => {
      store.dispatch(updateAgentStatus({
        id: data.agentId,
        status: 'failed'
      }))
      toast.error(`Agent ${data.agentName || data.agentId} failed: ${data.error}`)
    })

    websocketService.on(WebSocketMessageType.AGENT_STATUS_CHANGED, (data) => {
      store.dispatch(updateAgentStatus({
        id: data.agentId,
        status: data.status
      }))
    })

    // Evolution events
    websocketService.on(WebSocketMessageType.EVOLUTION_STARTED, (data) => {
      store.dispatch(setEvolutionStatus('running'))
      store.dispatch(updateCurrentCycle(data.cycle))
      toast.success('Evolution started')
    })

    websocketService.on(WebSocketMessageType.EVOLUTION_PHASE_CHANGED, (data) => {
      store.dispatch(setPhase(data.phase))
      toast(`Evolution phase: ${data.phase}`, { icon: 'ℹ️' })
    })

    websocketService.on(WebSocketMessageType.EVOLUTION_PROGRESS, (data) => {
      store.dispatch(updateCurrentCycle({
        ...data.cycle,
        progress: data.progress
      }))
    })

    websocketService.on(WebSocketMessageType.EVOLUTION_COMPLETED, (data) => {
      store.dispatch(setEvolutionStatus('completed'))
      store.dispatch(updateCurrentCycle(data.cycle))

      const improvement = data.improvement || 0
      if (improvement > 0) {
        toast.success(`Evolution completed! ${improvement.toFixed(1)}% improvement`)
      } else {
        toast.success('Evolution completed')
      }
    })

    websocketService.on(WebSocketMessageType.EVOLUTION_FAILED, (data) => {
      store.dispatch(setEvolutionStatus('failed'))
      toast.error(`Evolution failed: ${data.error}`)
    })

    // Metrics events
    websocketService.on(WebSocketMessageType.METRICS_UPDATE, (data) => {
      store.dispatch(updateRealTimeData(data))
    })

    websocketService.on('metrics:point', (data) => {
      store.dispatch(addMetricPoint({
        metric: data.metric,
        point: {
          timestamp: Date.now(),
          value: data.value,
          label: data.label
        }
      }))
    })

    // Log events
    websocketService.on(WebSocketMessageType.LOG_ENTRY, (data) => {
      store.dispatch(addLog(data))
    })

    // System events
    websocketService.on(WebSocketMessageType.SYSTEM_STATUS, (data) => {
      store.dispatch({
        type: 'system/updateStatus',
        payload: data
      })
    })

    websocketService.on(WebSocketMessageType.SYSTEM_ERROR, (data) => {
      toast.error(`System error: ${data.message}`)
      store.dispatch({
        type: 'system/addError',
        payload: data
      })
    })

    websocketService.on(WebSocketMessageType.SYSTEM_WARNING, (data) => {
      toast(data.message, { icon: '⚠️' })
      store.dispatch({
        type: 'system/addWarning',
        payload: data
      })
    })

    // Generic notification handler
    websocketService.on('notification', (data) => {
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
        case 'info':
          toast(message, { icon: 'ℹ️' })
          break
        default:
          toast(message)
      }
    })
  }

  // Initialize handlers
  setupMessageHandlers()

  return (next) => (action) => {
    switch (action.type) {
      case WS_CONNECT:
        websocketService.connect().catch((error) => {
          console.error('Failed to connect WebSocket:', error)
          toast.error('Failed to connect to server')
        })
        break

      case WS_DISCONNECT:
        websocketService.disconnect()
        break

      case WS_SEND:
        const { event, data } = action.payload
        websocketService.send(event, data)
        break

      case WS_SUBSCRIBE:
        // Handle dynamic subscription if needed
        break

      case WS_UNSUBSCRIBE:
        // Handle dynamic unsubscription if needed
        break

      // Action to WebSocket message mapping
      case 'evolution/start':
        websocketService.send('evolution:start', action.payload)
        break

      case 'evolution/stop':
        websocketService.send('evolution:stop')
        break

      case 'agent/start':
        websocketService.send('agent:start', action.payload)
        break

      case 'agent/stop':
        websocketService.send('agent:stop', action.payload)
        break

      case 'agent/execute':
        websocketService.send('agent:execute', action.payload)
        break

      case 'workflow/run':
        websocketService.send('workflow:run', action.payload)
        break

      case 'workflow/cancel':
        websocketService.send('workflow:cancel', action.payload)
        break

      default:
        break
    }

    return next(action)
  }
}

// Helper functions for components to dispatch WebSocket actions
export const connectWebSocket = () => wsConnect()
export const disconnectWebSocket = () => wsDisconnect()
export const sendWebSocketMessage = (event: string, data?: any) => wsSend(event, data)

// WebSocket state selectors
export const selectWebSocketState = (state: any) => ({
  isConnected: websocketService.isConnected(),
  connectionState: websocketService.getState(),
  queueSize: websocketService.getQueueSize()
})

export default websocketMiddleware
