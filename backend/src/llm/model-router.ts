// backend/src/llm/model-router.ts
import { LLMModelManager, ModelResponse } from './model-manager';

export interface RoutingRule {
  condition: (prompt: string, context?: any) => boolean;
  modelName: string;
  priority: number;
}

export class ModelRouter {
  private modelManager: LLMModelManager;
  private routingRules: RoutingRule[] = [];

  constructor(modelManager: LLMModelManager) {
    this.modelManager = modelManager;
    this.initializeDefaultRules();
  }

  private initializeDefaultRules(): void {
    // Fast responses for simple queries
    this.addRule({
      condition: (prompt) => prompt.length < 100,
      modelName: 'gpt-3.5-turbo',
      priority: 1
    });

    // Complex analysis tasks
    this.addRule({
      condition: (prompt) => 
        prompt.includes('analyze') || 
        prompt.includes('complex') || 
        prompt.includes('detailed'),
      modelName: 'claude-3-sonnet-direct',
      priority: 2
    });

    // Code generation tasks
    this.addRule({
      condition: (prompt) => 
        prompt.includes('code') || 
        prompt.includes('implement') || 
        prompt.includes('function'),
      modelName: 'gpt-4',
      priority: 3
    });

    // Default fallback (use direct API models)
    this.addRule({
      condition: () => true,
      modelName: 'gpt-3.5-turbo',
      priority: 0
    });
  }

  addRule(rule: RoutingRule): void {
    this.routingRules.push(rule);
    this.routingRules.sort((a, b) => b.priority - a.priority);
  }

  async route(
    prompt: string,
    context?: any,
    preferredModel?: string
  ): Promise<ModelResponse> {
    let selectedModel = preferredModel;

    if (!selectedModel) {
      // Find matching rule
      const matchingRule = this.routingRules.find(rule => 
        rule.condition(prompt, context)
      );
      
      selectedModel = matchingRule?.modelName || 'claude-3-haiku';
    }

    return this.modelManager.invoke(selectedModel, prompt);
  }

  getRoutingRules(): RoutingRule[] {
    return [...this.routingRules];
  }
}