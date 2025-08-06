import { 
  BedrockAgentRuntimeClient,
  InvokeAgentCommand,
  RetrieveCommand
} from '@aws-sdk/client-bedrock-agent-runtime';
import { Logger } from 'winston';
import { BaseAgent, AgentMessage } from '../../agents/framework/base-agent';

export interface AgentCoreConfig {
  agentId: string;
  agentAliasId: string;
  region: string;
  knowledgeBaseId?: string;
  instructionTemplate?: string;
}

export class BedrockAgentCoreManager {
  private client: BedrockAgentRuntimeClient;
  private logger: Logger;
  private config: AgentCoreConfig;
  
  constructor(config: AgentCoreConfig, logger: Logger) {
    this.config = config;
    this.logger = logger;
    
    this.client = new BedrockAgentRuntimeClient({
      region: config.region
    });
  }
  
  async invokeAgent(
    sessionId: string,
    inputText: string,
    sessionAttributes?: Record<string, string>
  ): Promise<any> {
    try {
      const command = new InvokeAgentCommand({
        agentId: this.config.agentId,
        agentAliasId: this.config.agentAliasId,
        sessionId,
        inputText,
        sessionState: { sessionAttributes }
      });
      
      const response = await this.client.send(command);
      const chunks: any[] = [];
      
      if (response.completion) {
        for await (const chunk of response.completion) {
          chunks.push(chunk);
          if (chunk.chunk) {
            this.handleChunk(chunk.chunk);
          }
        }
      }
      
      return {
        sessionId,
        response: chunks,
        metadata: {
          agentId: this.config.agentId,
          timestamp: new Date()
        }
      };
      
    } catch (error) {
      this.logger.error('Bedrock AgentCore invocation failed', {
        error,
        sessionId,
        inputText
      });
      throw error;
    }
  }
  
  async retrieveFromKnowledgeBase(
    query: string,
    numberOfResults: number = 5
  ): Promise<any> {
    if (!this.config.knowledgeBaseId) {
      throw new Error('Knowledge base ID not configured');
    }
    
    try {
      const command = new RetrieveCommand({
        knowledgeBaseId: this.config.knowledgeBaseId,
        retrievalQuery: { text: query },
        retrievalConfiguration: {
          vectorSearchConfiguration: { numberOfResults }
        }
      });
      
      const response = await this.client.send(command);
      
      return {
        results: response.retrievalResults || [],
        metadata: {
          knowledgeBaseId: this.config.knowledgeBaseId,
          query,
          timestamp: new Date()
        }
      };
      
    } catch (error) {
      this.logger.error('Knowledge base retrieval failed', {
        error,
        query,
        knowledgeBaseId: this.config.knowledgeBaseId
      });
      throw error;
    }
  }
  
  private handleChunk(chunk: any): void {
    if (chunk.bytes) {
      const text = Buffer.from(chunk.bytes).toString('utf-8');
      this.logger.debug('Received text chunk', { text });
    }
    
    if (chunk.attribution) {
      this.logger.debug('Received attribution', {
        attribution: chunk.attribution
      });
    }
  }
  
  async createSession(userId: string, metadata?: any): Promise<string> {
    const sessionId = `${userId}-${Date.now()}`;
    
    this.logger.info('Created Bedrock session', {
      sessionId,
      userId,
      metadata
    });
    
    return sessionId;
  }
}

export abstract class BedrockAgent extends BaseAgent {
  protected bedrockManager: BedrockAgentCoreManager;
  protected version: string;
  protected context?: { userId?: string };
  
  constructor(
    name: string,
    version: string,
    logger: Logger,
    bedrockConfig: AgentCoreConfig
  ) {
    super(name, logger);
    this.version = version;
    
    this.bedrockManager = new BedrockAgentCoreManager(
      bedrockConfig,
      logger
    );
  }
  
  async process(message: AgentMessage): Promise<any> {
    return this.execute(message.payload);
  }
  
  abstract execute(input: any): Promise<any>;
  abstract healthCheck(): Promise<any>;
  
  protected async processWithBedrock(
    input: string,
    sessionId?: string
  ): Promise<any> {
    const session = sessionId || await this.bedrockManager.createSession(
      this.context?.userId || 'anonymous'
    );
    
    return this.bedrockManager.invokeAgent(session, input);
  }
  
  protected async searchKnowledgeBase(query: string): Promise<any> {
    return this.bedrockManager.retrieveFromKnowledgeBase(query);
  }
}