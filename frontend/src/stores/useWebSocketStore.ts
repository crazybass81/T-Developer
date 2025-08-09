import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { WSMessage, AgentStatusUpdate, CodeGenerationUpdate, BuildProgressUpdate } from '@/types'

type ConnectionStatus = 'disconnected' | 'connecting' | 'connected' | 'error'

interface WebSocketState {
  ws: WebSocket | null
  status: ConnectionStatus
  error: string | null
  reconnectCount: number
  maxReconnectAttempts: number
  
  // Message handlers
  messageHandlers: Map<string, Set<(data: any) => void>>
  
  // Actions
  connect: (projectId?: string) => void
  disconnect: () => void
  reconnect: () => void
  send: (message: any) => void
  
  // Subscribe/Unsubscribe
  subscribe: (eventType: string, handler: (data: any) => void) => () => void
  unsubscribe: (eventType: string, handler: (data: any) => void) => void
  
  // Internal actions
  setStatus: (status: ConnectionStatus) => void
  setError: (error: string | null) => void
  incrementReconnectCount: () => void
  resetReconnectCount: () => void
}

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'

export const useWebSocketStore = create<WebSocketState>()(
  devtools(
    (set, get) => ({
      ws: null,
      status: 'disconnected',
      error: null,
      reconnectCount: 0,
      maxReconnectAttempts: 5,
      messageHandlers: new Map(),

      connect: (projectId) => {
        const { status, reconnectCount, maxReconnectAttempts } = get()
        
        if (status === 'connected' || status === 'connecting') {
          return
        }
        
        if (reconnectCount >= maxReconnectAttempts) {
          set({ error: 'Max reconnection attempts reached' })
          return
        }

        try {
          set({ status: 'connecting', error: null })
          
          const wsUrl = projectId ? `${WS_URL}/ws/${projectId}` : `${WS_URL}/ws`
          const ws = new WebSocket(wsUrl)

          ws.onopen = () => {
            console.log('WebSocket connected')
            set({ 
              ws, 
              status: 'connected', 
              error: null 
            })
            get().resetReconnectCount()
          }

          ws.onmessage = (event) => {
            try {
              const message: WSMessage = JSON.parse(event.data)
              const handlers = get().messageHandlers.get(message.type)
              
              if (handlers) {
                handlers.forEach(handler => {
                  try {
                    handler(message.data)
                  } catch (error) {
                    console.error('Error in message handler:', error)
                  }
                })
              }
              
              // Debug logging
              console.log('WebSocket message:', message)
            } catch (error) {
              console.error('Failed to parse WebSocket message:', error)
            }
          }

          ws.onerror = (event) => {
            console.error('WebSocket error:', event)
            set({ 
              status: 'error', 
              error: 'WebSocket connection error' 
            })
          }

          ws.onclose = (event) => {
            console.log('WebSocket closed:', event.code, event.reason)
            set({ 
              ws: null, 
              status: 'disconnected' 
            })

            // Auto-reconnect if not a clean close
            if (!event.wasClean && reconnectCount < maxReconnectAttempts) {
              get().incrementReconnectCount()
              setTimeout(() => {
                get().reconnect()
              }, Math.min(1000 * Math.pow(2, reconnectCount), 30000)) // Exponential backoff
            }
          }

        } catch (error) {
          console.error('Failed to create WebSocket connection:', error)
          set({ 
            status: 'error', 
            error: 'Failed to create WebSocket connection' 
          })
        }
      },

      disconnect: () => {
        const { ws } = get()
        if (ws) {
          ws.close(1000, 'User initiated disconnect')
        }
        set({ 
          ws: null, 
          status: 'disconnected', 
          error: null 
        })
        get().resetReconnectCount()
      },

      reconnect: () => {
        get().disconnect()
        setTimeout(() => {
          get().connect()
        }, 100)
      },

      send: (message) => {
        const { ws, status } = get()
        if (ws && status === 'connected') {
          try {
            ws.send(JSON.stringify(message))
          } catch (error) {
            console.error('Failed to send WebSocket message:', error)
          }
        } else {
          console.warn('WebSocket not connected, cannot send message')
        }
      },

      subscribe: (eventType, handler) => {
        const { messageHandlers } = get()
        
        if (!messageHandlers.has(eventType)) {
          messageHandlers.set(eventType, new Set())
        }
        
        messageHandlers.get(eventType)!.add(handler)
        
        // Return unsubscribe function
        return () => {
          get().unsubscribe(eventType, handler)
        }
      },

      unsubscribe: (eventType, handler) => {
        const { messageHandlers } = get()
        const handlers = messageHandlers.get(eventType)
        
        if (handlers) {
          handlers.delete(handler)
          if (handlers.size === 0) {
            messageHandlers.delete(eventType)
          }
        }
      },

      // Internal actions
      setStatus: (status) => set({ status }),
      setError: (error) => set({ error }),
      incrementReconnectCount: () => set((state) => ({ 
        reconnectCount: state.reconnectCount + 1 
      })),
      resetReconnectCount: () => set({ reconnectCount: 0 }),
    }),
    {
      name: 'websocket-store',
    }
  )
)

// Auto-connect on store creation (client-side only)
if (typeof window !== 'undefined') {
  // useWebSocketStore.getState().connect()
}