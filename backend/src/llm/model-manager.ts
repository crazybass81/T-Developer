// backend/src/llm/model-manager.ts
import { BedrockRuntimeClient, InvokeModelCommand } from '@aws-sdk/client-bedrock-runtime';

export interface ModelConfig {
  provider: 'openai' | 'anthropic' | 'bedrock';
  modelId: string;
  maxTokens?: number;
  temperature?: number;
  topP?: number;
}

export interface ModelResponse {
  content: string;
  usage: {
    inputTokens: number;
    outputTokens: number;
    totalTokens: number;
  };
  model: string;
  finishReason: string;
}

export class LLMModelManager {
  private bedrockClient: BedrockRuntimeClient;
  private modelConfigs: Map<string, ModelConfig> = new Map();

  constructor() {
    this.bedrockClient = new BedrockRuntimeClient({
      region: process.env.AWS_BEDROCK_REGION || 'us-east-1'
    });
    
    this.initializeDefaultModels();
  }

  private initializeDefaultModels(): void {
    // Claude models
    this.modelConfigs.set('claude-3-sonnet', {
      provider: 'bedrock',
      modelId: 'anthropic.claude-3-sonnet-20240229-v1:0',
      maxTokens: 4096,
      temperature: 0.7
    });

    this.modelConfigs.set('claude-3-haiku', {
      provider: 'bedrock',
      modelId: 'anthropic.claude-3-haiku-20240307-v1:0',
      maxTokens: 4096,
      temperature: 0.7
    });

    // Nova models
    this.modelConfigs.set('nova-pro', {
      provider: 'bedrock',
      modelId: 'amazon.nova-pro-v1:0',
      maxTokens: 4096,
      temperature: 0.7
    });

    this.modelConfigs.set('nova-lite', {
      provider: 'bedrock',
      modelId: 'amazon.nova-lite-v1:0',
      maxTokens: 4096,
      temperature: 0.7
    });

    // OpenAI models (direct API)
    this.modelConfigs.set('gpt-4', {
      provider: 'openai',
      modelId: 'gpt-4',
      maxTokens: 4096,
      temperature: 0.7
    });

    this.modelConfigs.set('gpt-3.5-turbo', {
      provider: 'openai',
      modelId: 'gpt-3.5-turbo',
      maxTokens: 4096,
      temperature: 0.7
    });

    // Anthropic models (direct API)
    this.modelConfigs.set('claude-3-opus-direct', {
      provider: 'anthropic',
      modelId: 'claude-3-opus-20240229',
      maxTokens: 4096,
      temperature: 0.7
    });

    this.modelConfigs.set('claude-3-sonnet-direct', {
      provider: 'anthropic',
      modelId: 'claude-3-sonnet-20240229',
      maxTokens: 4096,
      temperature: 0.7
    });
  }

  async invoke(
    modelName: string,
    prompt: string,
    options?: Partial<ModelConfig>
  ): Promise<ModelResponse> {
    const config = this.modelConfigs.get(modelName);
    if (!config) {
      throw new Error(`Model not found: ${modelName}`);
    }

    const mergedConfig = { ...config, ...options };

    switch (config.provider) {
      case 'bedrock':
        return this.invokeBedrock(mergedConfig, prompt);
      case 'openai':
        return this.invokeOpenAI(mergedConfig, prompt);
      case 'anthropic':
        return this.invokeAnthropic(mergedConfig, prompt);
      default:
        throw new Error(`Unsupported provider: ${config.provider}`);
    }
  }

  private async invokeBedrock(
    config: ModelConfig,
    prompt: string
  ): Promise<ModelResponse> {
    const body = JSON.stringify({
      anthropic_version: 'bedrock-2023-05-31',
      max_tokens: config.maxTokens || 4096,
      temperature: config.temperature || 0.7,
      top_p: config.topP || 0.9,
      messages: [
        {
          role: 'user',
          content: prompt
        }
      ]
    });

    const command = new InvokeModelCommand({
      modelId: config.modelId,
      body,
      contentType: 'application/json',
      accept: 'application/json'
    });

    const response = await this.bedrockClient.send(command);
    const responseBody = JSON.parse(new TextDecoder().decode(response.body));

    return {
      content: responseBody.content[0].text,
      usage: {
        inputTokens: responseBody.usage.input_tokens,
        outputTokens: responseBody.usage.output_tokens,
        totalTokens: responseBody.usage.input_tokens + responseBody.usage.output_tokens
      },
      model: config.modelId,
      finishReason: responseBody.stop_reason
    };
  }

  private async invokeOpenAI(
    config: ModelConfig,
    prompt: string
  ): Promise<ModelResponse> {
    const { OpenAI } = await import('openai');
    const openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY
    });

    const response = await openai.chat.completions.create({
      model: config.modelId,
      messages: [{ role: 'user', content: prompt }],
      max_tokens: config.maxTokens || 4096,
      temperature: config.temperature || 0.7,
      top_p: config.topP || 0.9
    });

    const choice = response.choices[0];
    return {
      content: choice.message.content || '',
      usage: {
        inputTokens: response.usage?.prompt_tokens || 0,
        outputTokens: response.usage?.completion_tokens || 0,
        totalTokens: response.usage?.total_tokens || 0
      },
      model: config.modelId,
      finishReason: choice.finish_reason || 'stop'
    };
  }

  private async invokeAnthropic(
    config: ModelConfig,
    prompt: string
  ): Promise<ModelResponse> {
    const { Anthropic } = await import('@anthropic-ai/sdk');
    const anthropic = new Anthropic({
      apiKey: process.env.ANTHROPIC_API_KEY
    });

    const response = await anthropic.messages.create({
      model: config.modelId,
      max_tokens: config.maxTokens || 4096,
      temperature: config.temperature || 0.7,
      messages: [{ role: 'user', content: prompt }]
    });

    const content = response.content[0];
    return {
      content: content.type === 'text' ? content.text : '',
      usage: {
        inputTokens: response.usage.input_tokens,
        outputTokens: response.usage.output_tokens,
        totalTokens: response.usage.input_tokens + response.usage.output_tokens
      },
      model: config.modelId,
      finishReason: response.stop_reason || 'end_turn'
    };
  }

  getAvailableModels(): string[] {
    return Array.from(this.modelConfigs.keys());
  }

  getModelConfig(modelName: string): ModelConfig | undefined {
    return this.modelConfigs.get(modelName);
  }

  registerModel(name: string, config: ModelConfig): void {
    this.modelConfigs.set(name, config);
  }
}