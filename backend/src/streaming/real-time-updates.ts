import { Server as SocketIOServer } from 'socket.io';
import { EventEmitter } from 'events';
import { StreamEvent } from './event-stream';

export interface RealtimeConfig {
  namespace?: string;
  authentication?: boolean;
  rateLimiting?: {
    maxConnections: number;
    windowMs: number;
  };
}

export class RealtimeUpdateService extends EventEmitter {
  private io: SocketIOServer;
  private connections: Map<string, Set<string>> = new Map(); // userId -> socketIds

  constructor(io: SocketIOServer, private config: RealtimeConfig = {}) {
    super();
    this.io = io;
    this.setupSocketHandlers();
  }

  private setupSocketHandlers(): void {
    const namespace = this.config.namespace || '/';
    const nsp = this.io.of(namespace);

    nsp.on('connection', (socket) => {
      this.handleConnection(socket);
    });
  }

  private handleConnection(socket: any): void {
    socket.on('authenticate', async (token: string) => {
      try {
        const userId = await this.authenticateUser(token);
        socket.userId = userId;
        
        // Track connection
        if (!this.connections.has(userId)) {
          this.connections.set(userId, new Set());
        }
        this.connections.get(userId)!.add(socket.id);

        socket.emit('authenticated', { userId });
        this.emit('user:connected', userId);
      } catch (error) {
        socket.emit('authentication:failed', { error: error.message });
        socket.disconnect();
      }
    });

    socket.on('subscribe', (channels: string[]) => {
      if (!socket.userId) return;
      
      channels.forEach(channel => {
        if (this.canSubscribeToChannel(socket.userId, channel)) {
          socket.join(channel);
        }
      });
    });

    socket.on('disconnect', () => {
      if (socket.userId) {
        const userSockets = this.connections.get(socket.userId);
        if (userSockets) {
          userSockets.delete(socket.id);
          if (userSockets.size === 0) {
            this.connections.delete(socket.userId);
            this.emit('user:disconnected', socket.userId);
          }
        }
      }
    });
  }

  async broadcastToUser(userId: string, event: string, data: any): Promise<void> {
    const userSockets = this.connections.get(userId);
    if (userSockets) {
      for (const socketId of userSockets) {
        this.io.to(socketId).emit(event, data);
      }
    }
  }

  async broadcastToChannel(channel: string, event: string, data: any): Promise<void> {
    this.io.to(channel).emit(event, data);
  }

  async broadcastProjectUpdate(projectId: string, update: any): Promise<void> {
    await this.broadcastToChannel(`project:${projectId}`, 'project:updated', update);
  }

  async broadcastAgentStatus(agentId: string, status: any): Promise<void> {
    await this.broadcastToChannel(`agent:${agentId}`, 'agent:status', status);
  }

  private async authenticateUser(token: string): Promise<string> {
    // JWT verification logic
    if (!token) throw new Error('No token provided');
    // Return userId from token
    return 'user123'; // Placeholder
  }

  private canSubscribeToChannel(userId: string, channel: string): boolean {
    // Authorization logic for channel subscription
    return true; // Placeholder
  }

  getConnectedUsers(): string[] {
    return Array.from(this.connections.keys());
  }

  getUserConnectionCount(userId: string): number {
    return this.connections.get(userId)?.size || 0;
  }
}

export class StreamToRealtimeAdapter {
  constructor(
    private realtimeService: RealtimeUpdateService
  ) {}

  async handleStreamEvent(event: StreamEvent): Promise<void> {
    switch (event.source) {
      case 'dynamodb':
        await this.handleDynamoDBEvent(event);
        break;
      case 'kinesis':
        await this.handleKinesisEvent(event);
        break;
    }
  }

  private async handleDynamoDBEvent(event: StreamEvent): Promise<void> {
    const tableName = event.metadata?.tableName;
    
    if (tableName?.includes('Project')) {
      await this.handleProjectEvent(event);
    } else if (tableName?.includes('Agent')) {
      await this.handleAgentEvent(event);
    }
  }

  private async handleProjectEvent(event: StreamEvent): Promise<void> {
    const projectId = event.data.keys?.ProjectId?.S;
    if (!projectId) return;

    const update = {
      type: event.type,
      projectId,
      timestamp: event.timestamp,
      data: event.data.newImage
    };

    await this.realtimeService.broadcastProjectUpdate(projectId, update);
  }

  private async handleAgentEvent(event: StreamEvent): Promise<void> {
    const agentId = event.data.keys?.AgentId?.S;
    if (!agentId) return;

    const status = {
      type: event.type,
      agentId,
      timestamp: event.timestamp,
      status: event.data.newImage?.Status?.S,
      data: event.data.newImage
    };

    await this.realtimeService.broadcastAgentStatus(agentId, status);
  }

  private async handleKinesisEvent(event: StreamEvent): Promise<void> {
    // Handle custom Kinesis events
    await this.realtimeService.broadcastToChannel(
      'system:events',
      'stream:event',
      event
    );
  }
}

export class RealtimeMetrics {
  private metrics = {
    connections: 0,
    messagesPerSecond: 0,
    channelSubscriptions: new Map<string, number>()
  };

  updateConnectionCount(count: number): void {
    this.metrics.connections = count;
  }

  incrementMessages(): void {
    this.metrics.messagesPerSecond++;
  }

  updateChannelSubscriptions(channel: string, count: number): void {
    this.metrics.channelSubscriptions.set(channel, count);
  }

  getMetrics(): any {
    return {
      ...this.metrics,
      channelSubscriptions: Object.fromEntries(this.metrics.channelSubscriptions)
    };
  }

  reset(): void {
    this.metrics.messagesPerSecond = 0;
  }
}