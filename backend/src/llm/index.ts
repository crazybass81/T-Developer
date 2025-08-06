export { ModelFallbackManager } from './fallback-manager';

// LLM Integration Types
export interface ModelConfig {
  name: string;
  provider: string;
  apiKey?: string;
  endpoint?: string;
  maxTokens?: number;
  temperature?: number;
  timeout?: number;
}

export interface ModelResponse {
  content: string;
  model: string;
  usage?: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
  };
  metadata?: any;
}

export interface ModelProvider {
  name: string;
  initialize(): Promise<void>;
  generate(prompt: string, options?: any): Promise<ModelResponse>;
  isHealthy(): Promise<boolean>;
}

// Re-export for convenience
export * from './fallback-manager';