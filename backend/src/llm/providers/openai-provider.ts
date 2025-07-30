import OpenAI from 'openai';
import { ModelProvider, ModelConfig, ModelResponse, StreamChunk } from '../model-provider';
import tiktoken from 'tiktoken';

export class OpenAIProvider extends ModelProvider {
  private client: OpenAI;
  private tokenizer: any;
  
  constructor(config: ModelConfig) {
    super(config);
  }
  
  async initialize(): Promise<void> {
    this.client = new OpenAI({
      apiKey: this.config.apiKey || process.env.OPENAI_API_KEY
    });
    
    // 토크나이저 초기화
    try {
      this.tokenizer = tiktoken.encoding_for_model(this.config.name as any);
    } catch {
      this.tokenizer = tiktoken.encoding_for_model('gpt-4');
    }
  }
  
  async generate(
    prompt: string,
    options?: Partial<ModelConfig>
  ): Promise<ModelResponse> {
    this.validateInput(prompt);
    const config = this.mergeConfig(options);
    
    const startTime = Date.now();
    
    try {
      const response = await this.client.chat.completions.create({
        model: config.name,
        messages: [{ role: 'user', content: prompt }],
        max_tokens: config.maxTokens,
        temperature: config.temperature,
        top_p: config.topP,
        frequency_penalty: config.frequencyPenalty,
        presence_penalty: config.presencePenalty,
        stop: config.stopSequences.length > 0 ? config.stopSequences : undefined
      });
      
      const choice = response.choices[0];
      const tokensUsed = response.usage?.total_tokens || 0;
      
      return {
        text: choice.message.content || '',
        tokensUsed,
        finishReason: choice.finish_reason || 'stop',
        metadata: {
          model: response.model,
          created: response.created,
          latency: Date.now() - startTime,
          promptTokens: response.usage?.prompt_tokens,
          completionTokens: response.usage?.completion_tokens
        },
        cost: this.getCostEstimate(
          response.usage?.prompt_tokens || 0,
          response.usage?.completion_tokens || 0
        )
      };
      
    } catch (error: any) {
      throw new Error(`OpenAI API error: ${error.message}`);
    }
  }
  
  async *streamGenerate(
    prompt: string,
    options?: Partial<ModelConfig>
  ): AsyncIterableIterator<StreamChunk> {
    this.validateInput(prompt);
    const config = this.mergeConfig(options);
    
    try {
      const stream = await this.client.chat.completions.create({
        model: config.name,
        messages: [{ role: 'user', content: prompt }],
        max_tokens: config.maxTokens,
        temperature: config.temperature,
        top_p: config.topP,
        frequency_penalty: config.frequencyPenalty,
        presence_penalty: config.presencePenalty,
        stop: config.stopSequences.length > 0 ? config.stopSequences : undefined,
        stream: true
      });
      
      for await (const chunk of stream) {
        const choice = chunk.choices[0];
        const content = choice?.delta?.content || '';
        
        yield {
          text: content,
          isComplete: choice?.finish_reason !== null,
          metadata: {
            finishReason: choice?.finish_reason
          }
        };
        
        if (choice?.finish_reason) {
          break;
        }
      }
      
    } catch (error: any) {
      throw new Error(`OpenAI streaming error: ${error.message}`);
    }
  }
  
  async embed(texts: string[]): Promise<number[][]> {
    try {
      const response = await this.client.embeddings.create({
        model: 'text-embedding-ada-002',
        input: texts
      });
      
      return response.data.map(item => item.embedding);
      
    } catch (error: any) {
      throw new Error(`OpenAI embedding error: ${error.message}`);
    }
  }
  
  estimateTokens(text: string): number {
    if (!this.tokenizer) {
      // 대략적인 추정 (1 토큰 ≈ 4 문자)
      return Math.ceil(text.length / 4);
    }
    
    return this.tokenizer.encode(text).length;
  }
  
  getCostEstimate(inputTokens: number, outputTokens: number): number {
    // OpenAI 가격표 (2024년 기준, 실제로는 동적으로 가져와야 함)
    const pricing: Record<string, { input: number; output: number }> = {
      'gpt-4': { input: 0.00003, output: 0.00006 },
      'gpt-4-turbo': { input: 0.00001, output: 0.00003 },
      'gpt-3.5-turbo': { input: 0.0000015, output: 0.000002 }
    };
    
    const modelPricing = pricing[this.config.name] || pricing['gpt-4'];
    
    return (inputTokens * modelPricing.input) + (outputTokens * modelPricing.output);
  }
}