// backend/src/llm/context-manager.ts
export interface ConversationContext {
  sessionId: string;
  userId?: string;
  messages: ContextMessage[];
  metadata: Record<string, any>;
  createdAt: Date;
  updatedAt: Date;
}

export interface ContextMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  tokens?: number;
  metadata?: Record<string, any>;
}

export class ContextManager {
  private contexts: Map<string, ConversationContext> = new Map();
  private maxContextLength: number = 8000; // tokens
  private maxMessages: number = 50;

  constructor(options?: { maxContextLength?: number; maxMessages?: number }) {
    if (options?.maxContextLength) this.maxContextLength = options.maxContextLength;
    if (options?.maxMessages) this.maxMessages = options.maxMessages;
  }

  createContext(sessionId: string, userId?: string): ConversationContext {
    const context: ConversationContext = {
      sessionId,
      userId,
      messages: [],
      metadata: {},
      createdAt: new Date(),
      updatedAt: new Date()
    };

    this.contexts.set(sessionId, context);
    return context;
  }

  getContext(sessionId: string): ConversationContext | undefined {
    return this.contexts.get(sessionId);
  }

  addMessage(
    sessionId: string,
    role: 'user' | 'assistant' | 'system',
    content: string,
    metadata?: Record<string, any>
  ): void {
    const context = this.contexts.get(sessionId);
    if (!context) {
      throw new Error(`Context not found: ${sessionId}`);
    }

    const message: ContextMessage = {
      id: this.generateMessageId(),
      role,
      content,
      timestamp: new Date(),
      tokens: this.estimateTokens(content),
      metadata
    };

    context.messages.push(message);
    context.updatedAt = new Date();

    // Trim context if needed
    this.trimContext(context);
  }

  getContextForPrompt(sessionId: string, includeSystem: boolean = true): string {
    const context = this.contexts.get(sessionId);
    if (!context) {
      return '';
    }

    const messages = includeSystem 
      ? context.messages 
      : context.messages.filter(m => m.role !== 'system');

    return messages
      .map(m => `${m.role}: ${m.content}`)
      .join('\n\n');
  }

  getRecentMessages(sessionId: string, count: number = 10): ContextMessage[] {
    const context = this.contexts.get(sessionId);
    if (!context) {
      return [];
    }

    return context.messages.slice(-count);
  }

  updateMetadata(sessionId: string, metadata: Record<string, any>): void {
    const context = this.contexts.get(sessionId);
    if (!context) {
      throw new Error(`Context not found: ${sessionId}`);
    }

    context.metadata = { ...context.metadata, ...metadata };
    context.updatedAt = new Date();
  }

  clearContext(sessionId: string): void {
    const context = this.contexts.get(sessionId);
    if (context) {
      context.messages = [];
      context.updatedAt = new Date();
    }
  }

  deleteContext(sessionId: string): boolean {
    return this.contexts.delete(sessionId);
  }

  private trimContext(context: ConversationContext): void {
    // Trim by message count
    if (context.messages.length > this.maxMessages) {
      const systemMessages = context.messages.filter(m => m.role === 'system');
      const otherMessages = context.messages.filter(m => m.role !== 'system');
      
      const trimmedOthers = otherMessages.slice(-(this.maxMessages - systemMessages.length));
      context.messages = [...systemMessages, ...trimmedOthers];
    }

    // Trim by token count
    let totalTokens = context.messages.reduce((sum, m) => sum + (m.tokens || 0), 0);
    
    while (totalTokens > this.maxContextLength && context.messages.length > 1) {
      // Remove oldest non-system message
      const nonSystemIndex = context.messages.findIndex(m => m.role !== 'system');
      if (nonSystemIndex !== -1) {
        const removed = context.messages.splice(nonSystemIndex, 1)[0];
        totalTokens -= (removed.tokens || 0);
      } else {
        break;
      }
    }
  }

  private estimateTokens(text: string): number {
    // Simple token estimation (roughly 4 characters per token)
    return Math.ceil(text.length / 4);
  }

  private generateMessageId(): string {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  // Context summarization for long conversations
  async summarizeContext(sessionId: string): Promise<string> {
    const context = this.contexts.get(sessionId);
    if (!context || context.messages.length === 0) {
      return '';
    }

    const messages = context.messages.slice(0, -5); // Keep last 5 messages
    const conversationText = messages
      .map(m => `${m.role}: ${m.content}`)
      .join('\n');

    // This would typically call an LLM to summarize
    // For now, return a simple summary
    return `Previous conversation summary: ${messages.length} messages exchanged about ${context.metadata.topic || 'various topics'}.`;
  }

  getContextStats(sessionId: string): {
    messageCount: number;
    totalTokens: number;
    duration: number;
    lastActivity: Date;
  } | null {
    const context = this.contexts.get(sessionId);
    if (!context) {
      return null;
    }

    return {
      messageCount: context.messages.length,
      totalTokens: context.messages.reduce((sum, m) => sum + (m.tokens || 0), 0),
      duration: context.updatedAt.getTime() - context.createdAt.getTime(),
      lastActivity: context.updatedAt
    };
  }
}