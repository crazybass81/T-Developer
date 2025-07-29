import { EventEmitter } from 'events';
import { AgentMessage } from './base-agent';

export interface MessageBus {
  publish(channel: string, message: AgentMessage): Promise<void>;
  subscribe(channel: string, handler: (message: AgentMessage) => void): void;
  unsubscribe(channel: string): void;
}

// In-memory message bus for development
export class InMemoryMessageBus implements MessageBus {
  private handlers: Map<string, Set<(message: AgentMessage) => void>> = new Map();
  
  async publish(channel: string, message: AgentMessage): Promise<void> {
    const channelHandlers = this.handlers.get(channel);
    if (channelHandlers) {
      channelHandlers.forEach(handler => {
        // Async execution to avoid blocking
        setImmediate(() => handler(message));
      });
    }
  }
  
  subscribe(channel: string, handler: (message: AgentMessage) => void): void {
    if (!this.handlers.has(channel)) {
      this.handlers.set(channel, new Set());
    }
    this.handlers.get(channel)!.add(handler);
  }
  
  unsubscribe(channel: string): void {
    this.handlers.delete(channel);
  }
}

// Redis message bus for production
export class RedisMessageBus implements MessageBus {
  private publisher: any;
  private subscriber: any;
  private handlers: Map<string, Set<(message: AgentMessage) => void>> = new Map();
  
  constructor(redisUrl: string) {
    // Lazy load Redis to avoid dependency issues in development
    try {
      const Redis = require('ioredis');
      this.publisher = new Redis(redisUrl);
      this.subscriber = new Redis(redisUrl);
      
      this.subscriber.on('message', (channel: string, data: string) => {
        const message = JSON.parse(data) as AgentMessage;
        const channelHandlers = this.handlers.get(channel);
        
        if (channelHandlers) {
          channelHandlers.forEach(handler => handler(message));
        }
      });
    } catch (error) {
      console.warn('Redis not available, falling back to in-memory bus');
      const fallback = new InMemoryMessageBus();
      this.publisher = fallback;
      this.subscriber = fallback;
    }
  }
  
  async publish(channel: string, message: AgentMessage): Promise<void> {
    if (this.publisher.publish) {
      await this.publisher.publish(channel, JSON.stringify(message));
    } else {
      await this.publisher.publish(channel, message);
    }
  }
  
  subscribe(channel: string, handler: (message: AgentMessage) => void): void {
    if (!this.handlers.has(channel)) {
      this.handlers.set(channel, new Set());
      if (this.subscriber.subscribe) {
        this.subscriber.subscribe(channel);
      } else {
        this.subscriber.subscribe(channel, handler);
      }
    }
    
    this.handlers.get(channel)!.add(handler);
  }
  
  unsubscribe(channel: string): void {
    this.handlers.delete(channel);
    if (this.subscriber.unsubscribe) {
      this.subscriber.unsubscribe(channel);
    }
  }
}

// Agent communication manager
export class AgentCommunicationManager extends EventEmitter {
  private messageBus: MessageBus;
  private agents: Map<string, any> = new Map();
  private routingTable: Map<string, string[]> = new Map();
  
  constructor(messageBus?: MessageBus) {
    super();
    this.messageBus = messageBus || new InMemoryMessageBus();
  }
  
  registerAgent(agentId: string, agent: any, channels: string[] = [`agent:${agentId}`]): void {
    this.agents.set(agentId, agent);
    
    channels.forEach(channel => {
      if (!this.routingTable.has(channel)) {
        this.routingTable.set(channel, []);
      }
      this.routingTable.get(channel)!.push(agentId);
      
      // Subscribe to channel
      this.messageBus.subscribe(channel, async (message) => {
        if (message.target === agentId || message.target === 'broadcast') {
          try {
            const response = await agent.handleMessage(message);
            
            if (response && response.type === 'response') {
              await this.sendMessage(response);
            }
          } catch (error) {
            console.error(`Error handling message for agent ${agentId}:`, error);
          }
        }
      });
    });
    
    console.log(`Agent ${agentId} registered for channels:`, channels);
  }
  
  async sendMessage(message: AgentMessage): Promise<void> {
    // Direct messaging
    if (message.target && message.target !== 'broadcast') {
      await this.messageBus.publish(`agent:${message.target}`, message);
      return;
    }
    
    // Broadcast messaging
    if (message.target === 'broadcast') {
      await this.messageBus.publish('agent:broadcast', message);
    }
  }
  
  getRoutingInfo(): Map<string, string[]> {
    return new Map(this.routingTable);
  }
  
  getAgentStatus(agentId: string): any {
    const agent = this.agents.get(agentId);
    return agent ? agent.getStatus() : null;
  }
  
  unregisterAgent(agentId: string): void {
    this.agents.delete(agentId);
    
    // Remove from routing table
    for (const [channel, agents] of this.routingTable.entries()) {
      const index = agents.indexOf(agentId);
      if (index > -1) {
        agents.splice(index, 1);
        if (agents.length === 0) {
          this.routingTable.delete(channel);
          this.messageBus.unsubscribe(channel);
        }
      }
    }
    
    console.log(`Agent ${agentId} unregistered`);
  }
}

// Simple RPC implementation
export class AgentRPC {
  private communicationManager: AgentCommunicationManager;
  private pendingCalls: Map<string, {
    resolve: (value: any) => void;
    reject: (error: any) => void;
    timeout: NodeJS.Timeout;
  }> = new Map();
  
  constructor(communicationManager: AgentCommunicationManager) {
    this.communicationManager = communicationManager;
    
    // Listen for responses
    this.communicationManager.on('message', (message: AgentMessage) => {
      if (message.type === 'response' || message.type === 'error') {
        this.handleResponse(message);
      }
    });
  }
  
  async call(
    targetAgent: string,
    method: string,
    params: any,
    timeout: number = 30000
  ): Promise<any> {
    const callId = `rpc-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    const message: AgentMessage = {
      id: callId,
      type: 'request',
      source: 'rpc-client',
      target: targetAgent,
      payload: {
        method,
        params
      },
      timestamp: new Date()
    };
    
    return new Promise((resolve, reject) => {
      const timeoutHandle = setTimeout(() => {
        this.pendingCalls.delete(callId);
        reject(new Error(`RPC call timeout: ${method}`));
      }, timeout);
      
      this.pendingCalls.set(callId, {
        resolve,
        reject,
        timeout: timeoutHandle
      });
      
      this.communicationManager.sendMessage(message);
    });
  }
  
  private handleResponse(message: AgentMessage): void {
    if (message.correlationId && this.pendingCalls.has(message.correlationId)) {
      const call = this.pendingCalls.get(message.correlationId)!;
      clearTimeout(call.timeout);
      
      if (message.type === 'response') {
        call.resolve(message.payload);
      } else if (message.type === 'error') {
        call.reject(new Error(message.payload.error));
      }
      
      this.pendingCalls.delete(message.correlationId);
    }
  }
}