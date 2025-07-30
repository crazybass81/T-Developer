import { Agent as AgnoAgent } from 'agno';
import { logger } from '../config/logger';

export abstract class BaseAgent extends AgnoAgent {
  protected agentName: string;
  protected agentType: string;

  constructor(name: string, type: string) {
    super({
      name,
      description: `T-Developer ${name} agent`,
      lightweight: true,
      skipValidation: true,
      useCache: true
    });
    
    this.agentName = name;
    this.agentType = type;
  }

  async initialize(): Promise<void> {
    logger.info(`Initializing ${this.agentName} agent`);
    await this.setup();
  }

  protected abstract setup(): Promise<void>;

  async execute(input: any): Promise<AgentResult> {
    const startTime = performance.now();
    
    try {
      logger.debug(`Executing ${this.agentName} agent`, { input });
      
      // Validate input
      this.validateInput(input);
      
      // Process
      const result = await this.process(input);
      
      const duration = performance.now() - startTime;
      
      logger.info(`${this.agentName} agent completed`, { 
        duration: `${duration.toFixed(2)}ms`,
        success: true 
      });

      return {
        success: true,
        data: result,
        metadata: {
          agentName: this.agentName,
          agentType: this.agentType,
          executionTime: duration,
          timestamp: new Date().toISOString()
        }
      };

    } catch (error) {
      const duration = performance.now() - startTime;
      
      logger.error(`${this.agentName} agent failed`, { 
        error: error.message,
        duration: `${duration.toFixed(2)}ms`
      });

      return {
        success: false,
        error: error.message,
        metadata: {
          agentName: this.agentName,
          agentType: this.agentType,
          executionTime: duration,
          timestamp: new Date().toISOString()
        }
      };
    }
  }

  protected abstract validateInput(input: any): void;
  protected abstract process(input: any): Promise<any>;
}

export interface AgentResult {
  success: boolean;
  data?: any;
  error?: string;
  metadata: {
    agentName: string;
    agentType: string;
    executionTime: number;
    timestamp: string;
  };
}