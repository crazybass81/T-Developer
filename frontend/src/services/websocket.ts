import { WebSocketMessage, WebSocketMessageType } from '../types/api'

export interface WebSocketConfig {
  url?: string
  reconnectionAttempts?: number
  reconnectionDelay?: number
  timeout?: number
  autoConnect?: boolean
}

export type MessageHandler = (data: any) => void
export type ConnectionHandler = () => void
export type ErrorHandler = (error: Error) => void

class WebSocketService {
  private socket: WebSocket | null = null
  private config: WebSocketConfig
  private messageHandlers: Map<string, Set<MessageHandler>> = new Map()
  private connectionHandlers: {
    connect: Set<ConnectionHandler>
    disconnect: Set<ConnectionHandler>
    error: Set<ErrorHandler>
  } = {
    connect: new Set(),
    disconnect: new Set(),
    error: new Set()
  }
  private reconnectAttempts: number = 0
  private reconnectTimer: NodeJS.Timeout | null = null
  private heartbeatTimer: NodeJS.Timeout | null = null
  private isIntentionalDisconnect: boolean = false
  private messageQueue: WebSocketMessage[] = []
  private connectionPromise: Promise<void> | null = null
  private connectionState: 'disconnected' | 'connecting' | 'connected' = 'disconnected'

  constructor(config?: WebSocketConfig) {
    this.config = {
      url: this.getWebSocketURL(),
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
      timeout: 30000,
      autoConnect: true,
      ...config
    }

    if (this.config.autoConnect) {
      this.connect()
    }
  }

  private getWebSocketURL(): string {
    return import.meta.env.MODE === 'production'
      ? 'wss://api.t-developer.io/ws'
      : 'ws://localhost:8000/ws'
  }

  /**
   * Connect to WebSocket server
   */
  async connect(): Promise<void> {
    if (this.connectionState === 'connected') {
      return Promise.resolve()
    }

    if (this.connectionPromise) {
      return this.connectionPromise
    }

    this.isIntentionalDisconnect = false
    this.connectionState = 'connecting'

    this.connectionPromise = new Promise((resolve, reject) => {
      const url = this.config.url || this.getWebSocketURL()

      console.log(`Connecting to WebSocket at ${url}`)

      try {
        this.socket = new WebSocket(url)

        const connectTimeout = setTimeout(() => {
          if (this.connectionState !== 'connected') {
            reject(new Error('Connection timeout'))
            this.handleConnectionError(new Error('Connection timeout'))
            this.socket?.close()
          }
        }, this.config.timeout!)

        this.socket.onopen = () => {
          clearTimeout(connectTimeout)
          console.log('WebSocket connected successfully')
          this.connectionState = 'connected'
          this.reconnectAttempts = 0
          this.connectionPromise = null

          // Start heartbeat
          this.startHeartbeat()

          // Process queued messages
          this.processMessageQueue()

          // Notify handlers
          this.connectionHandlers.connect.forEach(handler => handler())
          
          resolve()
        }

        this.socket.onerror = (event) => {
          clearTimeout(connectTimeout)
          const error = new Error('WebSocket error')
          console.error('WebSocket error:', error)
          this.connectionHandlers.error.forEach(handler => handler(error))
          
          if (this.connectionState === 'connecting') {
            reject(error)
          }
        }

        this.socket.onclose = (event) => {
          clearTimeout(connectTimeout)
          console.log('WebSocket disconnected', { code: event.code, reason: event.reason })
          this.connectionState = 'disconnected'
          this.stopHeartbeat()

          // Notify handlers
          this.connectionHandlers.disconnect.forEach(handler => handler())

          // Attempt reconnection if not intentional
          if (!this.isIntentionalDisconnect && this.reconnectAttempts < this.config.reconnectionAttempts!) {
            this.attemptReconnect()
          }
        }

        this.socket.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data)
            this.handleMessage(message)
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error)
          }
        }
      } catch (error) {
        reject(error as Error)
        this.handleConnectionError(error as Error)
      }
    })

    return this.connectionPromise
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    this.isIntentionalDisconnect = true
    this.stopHeartbeat()
    this.clearReconnectTimer()

    if (this.socket) {
      this.socket.close()
      this.socket = null
    }

    this.connectionState = 'disconnected'
    console.log('WebSocket disconnected intentionally')
  }

  /**
   * Send a message
   */
  send(event: string, data?: any): void {
    const message: WebSocketMessage = {
      id: this.generateMessageId(),
      type: event as WebSocketMessageType,
      payload: data,
      timestamp: new Date().toISOString()
    }

    if (this.connectionState === 'connected' && this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message))
    } else {
      // Queue message if not connected
      this.messageQueue.push(message)
      console.log('Message queued, will send when connected:', event)
    }
  }

  /**
   * Register a message handler
   */
  on(event: string | WebSocketMessageType, handler: MessageHandler): void {
    if (!this.messageHandlers.has(event)) {
      this.messageHandlers.set(event, new Set())
    }
    this.messageHandlers.get(event)!.add(handler)
  }

  /**
   * Unregister a message handler
   */
  off(event: string | WebSocketMessageType, handler: MessageHandler): void {
    const handlers = this.messageHandlers.get(event)
    if (handlers) {
      handlers.delete(handler)
      if (handlers.size === 0) {
        this.messageHandlers.delete(event)
      }
    }
  }

  /**
   * Register connection event handlers
   */
  onConnect(handler: ConnectionHandler): void {
    this.connectionHandlers.connect.add(handler)
  }

  onDisconnect(handler: ConnectionHandler): void {
    this.connectionHandlers.disconnect.add(handler)
  }

  onError(handler: ErrorHandler): void {
    this.connectionHandlers.error.add(handler)
  }

  /**
   * Remove connection event handlers
   */
  offConnect(handler: ConnectionHandler): void {
    this.connectionHandlers.connect.delete(handler)
  }

  offDisconnect(handler: ConnectionHandler): void {
    this.connectionHandlers.disconnect.delete(handler)
  }

  offError(handler: ErrorHandler): void {
    this.connectionHandlers.error.delete(handler)
  }

  /**
   * Handle incoming messages
   */
  private handleMessage(message: any): void {
    // Handle different message formats
    let type: string
    let payload: any

    if (message.type) {
      type = message.type
      payload = message.payload || message.data || message
    } else if (message.event) {
      type = message.event
      payload = message.data || message
    } else {
      // Fallback for unknown format
      type = 'message'
      payload = message
    }

    // Call registered handlers
    const handlers = this.messageHandlers.get(type)
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(payload)
        } catch (error) {
          console.error(`Error in message handler for ${type}:`, error)
        }
      })
    }

    // Also check for wildcard handlers
    const wildcardHandlers = this.messageHandlers.get('*')
    if (wildcardHandlers) {
      wildcardHandlers.forEach(handler => {
        try {
          handler({ type, payload })
        } catch (error) {
          console.error('Error in wildcard message handler:', error)
        }
      })
    }
  }

  /**
   * Handle connection errors
   */
  private handleConnectionError(error: Error): void {
    console.error('WebSocket connection error:', error)
    this.connectionPromise = null
    this.connectionState = 'disconnected'

    // Notify error handlers
    this.connectionHandlers.error.forEach(handler => handler(error))

    // Attempt reconnection
    if (!this.isIntentionalDisconnect && this.reconnectAttempts < this.config.reconnectionAttempts!) {
      this.attemptReconnect()
    }
  }

  /**
   * Attempt to reconnect
   */
  private attemptReconnect(): void {
    if (this.reconnectTimer) {
      return
    }

    this.reconnectAttempts++
    const delay = Math.min(
      this.config.reconnectionDelay! * Math.pow(2, this.reconnectAttempts - 1),
      30000
    )

    console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`)

    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null
      this.connect().catch(error => {
        console.error('Reconnection failed:', error)
      })
    }, delay)
  }

  /**
   * Clear reconnection timer
   */
  private clearReconnectTimer(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
  }

  /**
   * Start heartbeat
   */
  private startHeartbeat(): void {
    this.stopHeartbeat()

    // Send ping every 30 seconds
    this.heartbeatTimer = setInterval(() => {
      if (this.connectionState === 'connected' && this.socket?.readyState === WebSocket.OPEN) {
        this.send('ping')
      }
    }, 30000)
  }

  /**
   * Stop heartbeat
   */
  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
  }

  /**
   * Process queued messages
   */
  private processMessageQueue(): void {
    while (this.messageQueue.length > 0 && this.connectionState === 'connected') {
      const message = this.messageQueue.shift()!
      if (this.socket?.readyState === WebSocket.OPEN) {
        this.socket.send(JSON.stringify(message))
      }
    }
  }

  /**
   * Generate unique message ID
   */
  private generateMessageId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
  }

  /**
   * Get connection status
   */
  isConnected(): boolean {
    return this.connectionState === 'connected' && this.socket?.readyState === WebSocket.OPEN
  }

  /**
   * Get connection state
   */
  getState(): 'disconnected' | 'connecting' | 'connected' {
    return this.connectionState
  }

  /**
   * Get queue size
   */
  getQueueSize(): number {
    return this.messageQueue.length
  }

  /**
   * Clear message queue
   */
  clearQueue(): void {
    this.messageQueue = []
  }
}

// Create and export singleton instance
const websocketService = new WebSocketService({
  autoConnect: false // Will be connected via Redux middleware
})

export default websocketService