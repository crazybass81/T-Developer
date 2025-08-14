import { io, Socket } from 'socket.io-client';
import { WebSocketEvent, WebSocketEventType } from '@/types';

class SocketManager {
  private socket: Socket | null = null;
  private listeners: Map<string, Set<(data: any) => void>> = new Map();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  constructor() {
    if (typeof window !== 'undefined') {
      this.connect();
    }
  }

  connect() {
    const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';

    this.socket = io(WS_URL, {
      transports: ['websocket'],
      reconnection: true,
      reconnectionAttempts: this.maxReconnectAttempts,
      reconnectionDelay: this.reconnectDelay,
      reconnectionDelayMax: 10000,
    });

    this.setupEventHandlers();
  }

  private setupEventHandlers() {
    if (!this.socket) return;

    this.socket.on('connect', () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
      this.emit('system:connected', { timestamp: new Date().toISOString() });
    });

    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason);
      this.emit('system:disconnected', { reason, timestamp: new Date().toISOString() });
    });

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error);
      this.reconnectAttempts++;

      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        this.emit('system:error', {
          error: 'Max reconnection attempts reached',
          timestamp: new Date().toISOString()
        });
      }
    });

    // Evolution events
    this.socket.on('evolution:update', (data) => {
      this.emit('evolution:update', data);
    });

    this.socket.on('evolution:generation', (data) => {
      this.emit('evolution:generation', data);
    });

    this.socket.on('evolution:fitness', (data) => {
      this.emit('evolution:fitness', data);
    });

    this.socket.on('evolution:alert', (data) => {
      this.emit('evolution:alert', data);
    });

    // Agent events
    this.socket.on('agent:status', (data) => {
      this.emit('agent:status', data);
    });

    this.socket.on('agent:metrics', (data) => {
      this.emit('agent:metrics', data);
    });

    this.socket.on('agent:created', (data) => {
      this.emit('agent:created', data);
    });

    this.socket.on('agent:deleted', (data) => {
      this.emit('agent:deleted', data);
    });

    // Workflow events
    this.socket.on('workflow:started', (data) => {
      this.emit('workflow:started', data);
    });

    this.socket.on('workflow:progress', (data) => {
      this.emit('workflow:progress', data);
    });

    this.socket.on('workflow:completed', (data) => {
      this.emit('workflow:completed', data);
    });

    this.socket.on('workflow:failed', (data) => {
      this.emit('workflow:failed', data);
    });

    // Service events
    this.socket.on('service:analyzing', (data) => {
      this.emit('service:analyzing', data);
    });

    this.socket.on('service:building', (data) => {
      this.emit('service:building', data);
    });

    this.socket.on('service:improving', (data) => {
      this.emit('service:improving', data);
    });

    this.socket.on('service:completed', (data) => {
      this.emit('service:completed', data);
    });

    // System events
    this.socket.on('metrics:update', (data) => {
      this.emit('metrics:update', data);
    });

    this.socket.on('system:alert', (data) => {
      this.emit('system:alert', data);
    });

    this.socket.on('system:performance', (data) => {
      this.emit('system:performance', data);
    });

    this.socket.on('system:cost', (data) => {
      this.emit('system:cost', data);
    });
  }

  subscribe(event: WebSocketEventType | string, callback: (data: any) => void) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(callback);

    // Return unsubscribe function
    return () => {
      const callbacks = this.listeners.get(event);
      if (callbacks) {
        callbacks.delete(callback);
        if (callbacks.size === 0) {
          this.listeners.delete(event);
        }
      }
    };
  }

  unsubscribe(event: WebSocketEventType | string, callback?: (data: any) => void) {
    if (callback) {
      const callbacks = this.listeners.get(event);
      if (callbacks) {
        callbacks.delete(callback);
        if (callbacks.size === 0) {
          this.listeners.delete(event);
        }
      }
    } else {
      this.listeners.delete(event);
    }
  }

  private emit(event: string, data: any) {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      callbacks.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in WebSocket listener for ${event}:`, error);
        }
      });
    }
  }

  send(event: string, data: any) {
    if (this.socket && this.socket.connected) {
      this.socket.emit(event, data);
    } else {
      console.warn('WebSocket not connected, queuing message');
      // Could implement a queue here if needed
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
    this.listeners.clear();
  }

  isConnected(): boolean {
    return this.socket?.connected || false;
  }

  reconnect() {
    this.disconnect();
    this.connect();
  }
}

// Singleton instance
let socketManagerInstance: SocketManager | null = null;

export const getSocketManager = (): SocketManager => {
  if (!socketManagerInstance) {
    socketManagerInstance = new SocketManager();
  }
  return socketManagerInstance;
};

export default getSocketManager;
