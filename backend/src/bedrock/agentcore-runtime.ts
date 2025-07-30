// backend/src/bedrock/agentcore-runtime.ts
import { BedrockAgentRuntimeClient, InvokeAgentCommand } from '@aws-sdk/client-bedrock-agent-runtime';

export interface AgentCoreConfig {
  region: string;
  agentId: string;
  agentAliasId: string;
  sessionId?: string;
}

export interface AgentCoreResponse {
  completion: string;
  sessionId: string;
  trace?: any;
  citations?: any[];
}

export class AgentCoreRuntime {
  private client: BedrockAgentRuntimeClient;
  private config: AgentCoreConfig;

  constructor(config: AgentCoreConfig) {
    this.config = config;
    this.client = new BedrockAgentRuntimeClient({
      region: config.region
    });
  }

  async invokeAgent(
    inputText: string,
    sessionId?: string
  ): Promise<AgentCoreResponse> {
    const command = new InvokeAgentCommand({
      agentId: this.config.agentId,
      agentAliasId: this.config.agentAliasId,
      sessionId: sessionId || this.config.sessionId || this.generateSessionId(),
      inputText,
      enableTrace: true
    });

    try {
      const response = await this.client.send(command);
      
      let completion = '';
      let trace = null;
      let citations: any[] = [];

      if (response.completion) {
        for await (const chunk of response.completion) {
          if (chunk.chunk?.bytes) {
            const text = new TextDecoder().decode(chunk.chunk.bytes);
            completion += text;
          }
          if (chunk.trace) {
            trace = chunk.trace;
          }
          if (chunk.chunk?.attribution?.citations) {
            citations.push(...chunk.chunk.attribution.citations);
          }
        }
      }

      return {
        completion,
        sessionId: response.sessionId || sessionId || '',
        trace,
        citations
      };
    } catch (error) {
      throw new Error(`AgentCore invocation failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  async endSession(sessionId: string): Promise<void> {
    // AgentCore sessions auto-expire, but we can track locally
    console.log(`Session ${sessionId} ended`);
  }

  private generateSessionId(): string {
    return `agentcore_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}