import Anthropic from '@anthropic-ai/sdk';
import { ModelProvider, ModelConfig, ModelResponse, StreamChunk } from '../model-provider';

export class AnthropicProvider extends ModelProvider {
  private client: Anthropic;
  
  constructor(config: ModelConfig) {
    super(config);
  }
  
  async initialize(): Promise<void> {
    this.client = new Anthropic({
      apiKey: this.config.apiKey || process.env.ANTHROPIC_API_KEY
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
      const response = await this.client.messages.create({
        model: config.name,
        max_tokens: config.maxTokens,
        temperature: config.temperature,
        top_p: config.topP,
        messages: [{ role: 'user', content: prompt }],
        stop_sequences: config.stopSequences.length > 0 ? config.stopSequences : undefined
      });
      
      const content = response.content[0];
      const text = content.type === 'text' ? content.text : '';
      
      return {
        text,
        tokensUsed: response.usage.input_tokens + response.usage.output_tokens,
        finishReason: response.stop_reason || 'stop',
        metadata: {
          model: response.model,
          latency: Date.now() - startTime,
          inputTokens: response.usage.input_tokens,
          outputTokens: response.usage.output_tokens,
          stopSequence: response.stop_sequence
        },
        cost: this.getCostEstimate(
          response.usage.input_tokens,
          response.usage.output_tokens
        )
      };
      
    } catch (error: any) {
      throw new Error(`Anthropic API error: ${error.message}`);
    }
  }
  
  async *streamGenerate(
    prompt: string,
    options?: Partial<ModelConfig>
  ): AsyncIterableIterator<StreamChunk> {
    this.validateInput(prompt);
    const config = this.mergeConfig(options);
    
    try {
      const stream = await this.client.messages.create({
        model: config.name,
        max_tokens: config.maxTokens,
        temperature: config.temperature,
        top_p: config.topP,
        messages: [{ role: 'user', content: prompt }],
        stop_sequences: config.stopSequences.length > 0 ? config.stopSequences : undefined,
        stream: true
      });
      
      for await (const chunk of stream) {
        if (chunk.type === 'content_block_delta' && chunk.delta.type === 'text_delta') {
          yield {
            text: chunk.delta.text,
            isComplete: false
          };
        } else if (chunk.type === 'message_stop') {
          yield {
            text: '',
            isComplete: true,
            metadata: {
              finishReason: 'stop'
            }
          };
          break;
        }
      }
      
    } catch (error: any) {
      throw new Error(`Anthropic streaming error: ${error.message}`);
    }
  }
  
  async embed(texts: string[]): Promise<number[][]> {
    // Anthropic doesn't provide embedding API, use a fallback or throw error
    throw new Error('Anthropic does not provide embedding API. Use OpenAI or other providers for embeddings.');
  }
  
  estimateTokens(text: string): number {
    // Anthropic의 토큰 계산 (대략적)
    // Claude는 대략 1 토큰당 3.5-4 문자
    return Math.ceil(text.length / 3.5);
  }
  
  getCostEstimate(inputTokens: number, outputTokens: number): number {
    // Anthropic 가격표 (2024년 기준)
    const pricing: Record<string, { input: number; output: number }> = {
      'claude-3-opus-20240229': { input: 0.000015, output: 0.000075 },
      'claude-3-sonnet-20240229': { input: 0.000003, output: 0.000015 },
      'claude-3-haiku-20240307': { input: 0.00000025, output: 0.00000125 },
      'claude-2.1': { input: 0.000008, output: 0.000024 },
      'claude-2.0': { input: 0.000008, output: 0.000024 }
    };
    
    const modelPricing = pricing[this.config.name] || pricing['claude-3-sonnet-20240229'];
    
    return (inputTokens * modelPricing.input) + (outputTokens * modelPricing.output);
  }
}