import { ModelProviderFactory } from '../model-provider';
import { OpenAIProvider } from './openai-provider';
import { AnthropicProvider } from './anthropic-provider';
import { BedrockProvider } from './bedrock-provider';

// 모든 프로바이더 등록
export function registerAllProviders(): void {
  ModelProviderFactory.register('openai', OpenAIProvider);
  ModelProviderFactory.register('anthropic', AnthropicProvider);
  ModelProviderFactory.register('bedrock', BedrockProvider);
  
  console.log('✅ All LLM providers registered successfully');
}

// 프로바이더별 지원 모델 목록
export const SUPPORTED_MODELS = {
  openai: [
    'gpt-4',
    'gpt-4-turbo',
    'gpt-4-turbo-preview',
    'gpt-3.5-turbo',
    'gpt-3.5-turbo-16k'
  ],
  anthropic: [
    'claude-3-opus-20240229',
    'claude-3-sonnet-20240229',
    'claude-3-haiku-20240307',
    'claude-2.1',
    'claude-2.0'
  ],
  bedrock: [
    'anthropic.claude-3-opus-20240229-v1:0',
    'anthropic.claude-3-sonnet-20240229-v1:0',
    'anthropic.claude-3-haiku-20240307-v1:0',
    'anthropic.claude-v2:1',
    'anthropic.claude-v2',
    'amazon.titan-text-express-v1',
    'amazon.titan-text-lite-v1',
    'ai21.j2-ultra-v1',
    'ai21.j2-mid-v1',
    'cohere.command-text-v14',
    'cohere.command-light-text-v14',
    'meta.llama2-13b-chat-v1',
    'meta.llama2-70b-chat-v1'
  ]
};

export { OpenAIProvider, AnthropicProvider, BedrockProvider };