import { 
  BedrockAgentRuntimeClient,
  InvokeAgentCommand,
  RetrieveCommand
} from '@aws-sdk/client-bedrock-agent-runtime';

export interface AgentCoreConfig {
  agentId: string;
  agentAliasId: string;
  region: string;
  knowledgeBaseId?: string;
  instructionTemplate?: string;
}

export class BedrockAgentCoreManager {
  private client: BedrockAgentRuntimeClient;
  private config: AgentCoreConfig;
  
  constructor(config: AgentCoreConfig) {
    this.config = config;
    
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
        sessionState: {
          sessionAttributes
        }
      });
      
      const response = await this.client.send(command);
      
      // Process streaming response
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
      console.error('Bedrock AgentCore invocation failed', {
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
        retrievalQuery: {
          text: query
        },
        retrievalConfiguration: {
          vectorSearchConfiguration: {
            numberOfResults
          }
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
      console.error('Knowledge base retrieval failed', {
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
      console.log('Received text chunk:', text);
    }
    
    if (chunk.attribution) {
      console.log('Received attribution:', chunk.attribution);
    }
  }
  
  async createSession(userId: string, metadata?: any): Promise<string> {
    const sessionId = `${userId}-${Date.now()}`;
    
    console.log('Created Bedrock session', {
      sessionId,
      userId,
      metadata
    });
    
    return sessionId;
  }
}