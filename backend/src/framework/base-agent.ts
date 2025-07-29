import { EventEmitter } from 'events';
import { Logger } from 'winston';

export interface AgentCapability {
  name: string;
  description: string;
  inputSchema: any;
  outputSchema: any;
  version: string;
}

export interface AgentMessage {
  id: string;
  type: string;
  payload: any;
  timestamp: Date;
  source?: string;
}

export abstract class BaseAgent extends EventEmitter {
  protected name: string;
  protected version: string;
  protected logger: Logger;
  protected capabilities: Map<string, AgentCapability> = new Map();
  protected isInitialized = false;

  constructor(name: string, version: string, logger: Logger) {
    super();
    this.name = name;
    this.version = version;
    this.logger = logger;
  }

  async start(): Promise<void> {
    if (this.isInitialized) {
      return;
    }

    try {
      await this.initialize();
      this.isInitialized = true;
      this.logger.info(`Agent ${this.name} started successfully`);
      this.emit('started');
    } catch (error) {
      this.logger.error(`Failed to start agent ${this.name}:`, error);
      throw error;
    }
  }

  async stop(): Promise<void> {
    if (!this.isInitialized) {
      return;
    }

    try {
      await this.cleanup();
      this.isInitialized = false;
      this.logger.info(`Agent ${this.name} stopped`);
      this.emit('stopped');
    } catch (error) {
      this.logger.error(`Error stopping agent ${this.name}:`, error);
      throw error;
    }
  }

  async execute(message: AgentMessage): Promise<any> {
    if (!this.isInitialized) {
      throw new Error(`Agent ${this.name} is not initialized`);
    }

    const startTime = Date.now();
    
    try {
      this.logger.debug(`Processing message in agent ${this.name}`, { 
        messageId: message.id,
        type: message.type 
      });

      const result = await this.process(message);
      
      const duration = Date.now() - startTime;
      this.logger.debug(`Message processed successfully`, { 
        messageId: message.id,
        duration 
      });

      this.emit('messageProcessed', { message, result, duration });
      
      return result;
    } catch (error) {
      const duration = Date.now() - startTime;
      this.logger.error(`Error processing message in agent ${this.name}:`, error);
      
      this.emit('messageError', { message, error, duration });
      throw error;
    }
  }

  protected registerCapability(capability: AgentCapability): void {
    this.capabilities.set(capability.name, capability);
    this.logger.debug(`Registered capability: ${capability.name}`);
  }

  getCapabilities(): AgentCapability[] {
    return Array.from(this.capabilities.values());
  }

  hasCapability(name: string): boolean {
    return this.capabilities.has(name);
  }

  getInfo(): any {
    return {
      name: this.name,
      version: this.version,
      capabilities: this.getCapabilities(),
      isInitialized: this.isInitialized
    };
  }

  protected abstract initialize(): Promise<void>;
  protected abstract process(message: AgentMessage): Promise<any>;
  
  protected async cleanup(): Promise<void> {
    // Default implementation - can be overridden
  }
}