import { EventEmitter } from 'events';
import Redis from 'ioredis';
import { AgentMessage } from './base-agent';

export interface MessageBus {
  publish(channel: string, message: AgentMessage): Promise<void>;
  subscribe(channel: string, handler: (message: AgentMessage) => void): void;
  unsubscribe(channel: string): void;
}

export class RedisMessageBus implements MessageBus {
  private publisher: Redis;
  private subscriber: Redis;
  private handlers: Map<string, Set<(message: AgentMessage) => void>> = new Map();
  
  constructor(redisUrl: string) {
    this.publisher = new Redis(redisUrl);
    this.subscriber = new Redis(redisUrl);
    
    this.subscriber.on('message', (channel, data) => {
      const message = JSON.parse(data) as AgentMessage;
      const channelHandlers = this.handlers.get(channel);
      
      if (channelHandlers) {
        channelHandlers.forEach(handler => handler(message));
      }
    });
  }
  
  async publish(channel: string, message: AgentMessage): Promise<void> {
    await this.publisher.publish(channel, JSON.stringify(message));
  }
  
  subscribe(channel: string, handler: (message: AgentMessage) => void): void {
    if (!this.handlers.has(channel)) {
      this.handlers.set(channel, new Set());
      this.subscriber.subscribe(channel);
    }
    
    this.handlers.get(channel)!.add(handler);
  }
  
  unsubscribe(channel: string): void {
    this.handlers.delete(channel);
    this.subscriber.unsubscribe(channel);
  }
}

export class AgentCommunicationManager {
  private messageBus: MessageBus;
  private agents: Map<string, any> = new Map();
  private routingTable: Map<string, string[]> = new Map();
  
  constructor(messageBus: MessageBus) {
    this.messageBus = messageBus;
  }
  
  registerAgent(agentId: string, agent: any, channels: string[]): void {
    this.agents.set(agentId, agent);
    
    channels.forEach(channel => {
      if (!this.routingTable.has(channel)) {
        this.routingTable.set(channel, []);
      }
      this.routingTable.get(channel)!.push(agentId);
      
      this.messageBus.subscribe(channel, async (message) => {
        if (message.target === agentId || message.target === 'broadcast') {
          const response = await agent.handleMessage(message);
          
          if (response && response.type === 'response') {
            await this.sendMessage(response);
          }
        }
      });
    });
  }
  
  async sendMessage(message: AgentMessage): Promise<void> {
    if (message.target && message.target !== 'broadcast') {
      await this.messageBus.publish(`agent:${message.target}`, message);
      return;
    }
    
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
}

export class AgentRPC {
  private communicationManager: AgentCommunicationManager;
  private pendingCalls: Map<string, {
    resolve: (value: any) => void;
    reject: (error: any) => void;
    timeout: NodeJS.Timeout;
  }> = new Map();
  
  constructor(communicationManager: AgentCommunicationManager) {
    this.communicationManager = communicationManager;
  }
  
  async call(
    targetAgent: string,
    method: string,
    params: any,
    timeout: number = 30000
  ): Promise<any> {
    const callId = `rpc-${Date.now()}-${Math.random()}`;
    
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
  
  handleResponse(message: AgentMessage): void {
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