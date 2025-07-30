import { BedrockRuntimeClient, InvokeModelCommand, InvokeModelWithResponseStreamCommand } from '@aws-sdk/client-bedrock-runtime';
import { ModelProvider, ModelConfig, ModelResponse, StreamChunk } from '../model-provider';

export class BedrockProvider extends ModelProvider {
  private client: BedrockRuntimeClient;
  
  constructor(config: ModelConfig) {
    super(config);
  }
  
  async initialize(): Promise<void> {
    this.client = new BedrockRuntimeClient({
      region: process.env.AWS_BEDROCK_REGION || process.env.AWS_REGION || 'us-east-1'
    });
  }
  
  async generate(
    prompt: string,
    options?: Partial<ModelConfig>
  ): Promise<ModelResponse> {
    this.validateInput(prompt);
    const config = this.mergeConfig(options);
    
    const startTime = Date.now();
    
    try {
      const body = this.buildRequestBody(prompt, config);
      
      const command = new InvokeModelCommand({
        modelId: config.name,
        body: JSON.stringify(body),
        accept: 'application/json',
        contentType: 'application/json'
      });
      
      const response = await this.client.send(command);
      const responseBody = JSON.parse(new TextDecoder().decode(response.body));
      
      const result = this.parseResponse(responseBody, config.name);
      
      return {
        ...result,
        metadata: {
          ...result.metadata,
          latency: Date.now() - startTime,
          modelId: config.name
        },
        cost: this.getCostEstimate(
          result.metadata.inputTokens || 0,
          result.metadata.outputTokens || 0
        )
      };
      
    } catch (error: any) {
      throw new Error(`Bedrock API error: ${error.message}`);
    }
  }
  
  async *streamGenerate(
    prompt: string,
    options?: Partial<ModelConfig>
  ): AsyncIterableIterator<StreamChunk> {
    this.validateInput(prompt);
    const config = this.mergeConfig(options);
    
    try {
      const body = this.buildRequestBody(prompt, config);
      
      const command = new InvokeModelWithResponseStreamCommand({
        modelId: config.name,
        body: JSON.stringify(body),
        accept: 'application/json',
        contentType: 'application/json'
      });
      
      const response = await this.client.send(command);
      
      if (response.body) {
        for await (const chunk of response.body) {
          if (chunk.chunk?.bytes) {
            const chunkData = JSON.parse(new TextDecoder().decode(chunk.chunk.bytes));
            const parsed = this.parseStreamChunk(chunkData, config.name);
            
            if (parsed) {
              yield parsed;
            }
          }
        }
      }
      
    } catch (error: any) {
      throw new Error(`Bedrock streaming error: ${error.message}`);
    }
  }
  
  async embed(texts: string[]): Promise<number[][]> {
    // Bedrock의 Titan Embeddings 모델 사용
    const embeddings: number[][] = [];
    
    for (const text of texts) {
      try {
        const command = new InvokeModelCommand({
          modelId: 'amazon.titan-embed-text-v1',
          body: JSON.stringify({ inputText: text }),
          accept: 'application/json',
          contentType: 'application/json'
        });
        
        const response = await this.client.send(command);
        const responseBody = JSON.parse(new TextDecoder().decode(response.body));
        
        embeddings.push(responseBody.embedding);
        
      } catch (error: any) {
        throw new Error(`Bedrock embedding error: ${error.message}`);
      }
    }
    
    return embeddings;
  }
  
  private buildRequestBody(prompt: string, config: ModelConfig): any {
    // 모델별 요청 형식
    if (config.name.includes('anthropic.claude')) {
      return {
        prompt: `\n\nHuman: ${prompt}\n\nAssistant:`,
        max_tokens_to_sample: config.maxTokens,
        temperature: config.temperature,
        top_p: config.topP,
        stop_sequences: config.stopSequences
      };
    } else if (config.name.includes('amazon.titan')) {
      return {
        inputText: prompt,
        textGenerationConfig: {
          maxTokenCount: config.maxTokens,
          temperature: config.temperature,
          topP: config.topP,
          stopSequences: config.stopSequences
        }
      };
    } else if (config.name.includes('ai21.j2')) {
      return {
        prompt,
        maxTokens: config.maxTokens,
        temperature: config.temperature,
        topP: config.topP,
        stopSequences: config.stopSequences
      };
    } else if (config.name.includes('cohere.command')) {
      return {
        prompt,
        max_tokens: config.maxTokens,
        temperature: config.temperature,
        p: config.topP,
        stop_sequences: config.stopSequences
      };
    }
    
    // 기본 형식
    return {
      prompt,
      max_tokens: config.maxTokens,
      temperature: config.temperature,
      top_p: config.topP
    };
  }
  
  private parseResponse(responseBody: any, modelId: string): Omit<ModelResponse, 'metadata' | 'cost'> & { metadata: any } {
    if (modelId.includes('anthropic.claude')) {
      return {
        text: responseBody.completion || '',
        tokensUsed: (responseBody.usage?.input_tokens || 0) + (responseBody.usage?.output_tokens || 0),
        finishReason: responseBody.stop_reason || 'stop',
        metadata: {
          inputTokens: responseBody.usage?.input_tokens,
          outputTokens: responseBody.usage?.output_tokens
        }
      };
    } else if (modelId.includes('amazon.titan')) {
      return {
        text: responseBody.results?.[0]?.outputText || '',
        tokensUsed: responseBody.inputTextTokenCount + responseBody.results?.[0]?.tokenCount || 0,
        finishReason: responseBody.results?.[0]?.completionReason || 'stop',
        metadata: {
          inputTokens: responseBody.inputTextTokenCount,
          outputTokens: responseBody.results?.[0]?.tokenCount
        }
      };
    } else if (modelId.includes('ai21.j2')) {
      return {
        text: responseBody.completions?.[0]?.data?.text || '',
        tokensUsed: responseBody.prompt?.tokens?.length + responseBody.completions?.[0]?.data?.tokens?.length || 0,
        finishReason: responseBody.completions?.[0]?.finishReason?.reason || 'stop',
        metadata: {
          inputTokens: responseBody.prompt?.tokens?.length,
          outputTokens: responseBody.completions?.[0]?.data?.tokens?.length
        }
      };
    }
    
    // 기본 파싱
    return {
      text: responseBody.text || responseBody.completion || '',
      tokensUsed: responseBody.tokens_used || 0,
      finishReason: responseBody.finish_reason || 'stop',
      metadata: {}
    };
  }
  
  private parseStreamChunk(chunkData: any, modelId: string): StreamChunk | null {
    if (modelId.includes('anthropic.claude')) {
      if (chunkData.completion) {
        return {
          text: chunkData.completion,
          isComplete: chunkData.stop_reason !== null,
          metadata: {
            finishReason: chunkData.stop_reason
          }
        };
      }
    } else if (modelId.includes('amazon.titan')) {
      if (chunkData.outputText) {
        return {
          text: chunkData.outputText,
          isComplete: chunkData.completionReason !== null,
          metadata: {
            finishReason: chunkData.completionReason
          }
        };
      }
    }
    
    return null;
  }
  
  estimateTokens(text: string): number {
    // Bedrock 모델별 토큰 추정
    return Math.ceil(text.length / 4);
  }
  
  getCostEstimate(inputTokens: number, outputTokens: number): number {
    // Bedrock 가격표 (2024년 기준)
    const pricing: Record<string, { input: number; output: number }> = {
      'anthropic.claude-3-opus-20240229-v1:0': { input: 0.000015, output: 0.000075 },
      'anthropic.claude-3-sonnet-20240229-v1:0': { input: 0.000003, output: 0.000015 },
      'anthropic.claude-3-haiku-20240307-v1:0': { input: 0.00000025, output: 0.00000125 },
      'amazon.titan-text-express-v1': { input: 0.0000008, output: 0.0000016 },
      'ai21.j2-ultra-v1': { input: 0.0000188, output: 0.0000188 },
      'cohere.command-text-v14': { input: 0.0000015, output: 0.000002 }
    };
    
    const modelPricing = pricing[this.config.name] || { input: 0.000001, output: 0.000002 };
    
    return (inputTokens * modelPricing.input) + (outputTokens * modelPricing.output);
  }
}