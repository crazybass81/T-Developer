// backend/src/agno/memory/context-manager.ts
import { MemoryHierarchy, MemoryLevel } from './memory-hierarchy';

export interface ConversationContext {
  id: string;
  userId: string;
  sessionId: string;
  messages: Message[];
  metadata: Record<string, any>;
  createdAt: number;
  updatedAt: number;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: number;
  metadata?: Record<string, any>;
}

export class ContextManager {
  private memory: MemoryHierarchy;
  private maxContextLength = 4000; // tokens
  private maxMessages = 50;
  
  constructor() {
    this.memory = new MemoryHierarchy();
  }
  
  async getContext(sessionId: string): Promise<ConversationContext | null> {
    const context = await this.memory.get(`context:${sessionId}`);
    return context || null;
  }
  
  async updateContext(
    sessionId: string, 
    message: Message
  ): Promise<ConversationContext> {
    let context = await this.getContext(sessionId);
    
    if (!context) {
      context = {
        id: sessionId,
        userId: message.metadata?.userId || 'anonymous',
        sessionId,
        messages: [],
        metadata: {},
        createdAt: Date.now(),
        updatedAt: Date.now()
      };
    }
    
    context.messages.push(message);
    context.updatedAt = Date.now();
    
    // 컨텍스트 크기 관리
    context = this.trimContext(context);
    
    await this.memory.set(
      `context:${sessionId}`, 
      context, 
      MemoryLevel.L2_SESSION
    );
    
    return context;
  }
  
  private trimContext(context: ConversationContext): ConversationContext {
    // 메시지 수 제한
    if (context.messages.length > this.maxMessages) {
      context.messages = context.messages.slice(-this.maxMessages);
    }
    
    // 토큰 수 제한 (간단한 추정)
    let totalTokens = 0;
    const trimmedMessages: Message[] = [];
    
    for (let i = context.messages.length - 1; i >= 0; i--) {
      const message = context.messages[i];
      const tokens = this.estimateTokens(message.content);
      
      if (totalTokens + tokens > this.maxContextLength) {
        break;
      }
      
      totalTokens += tokens;
      trimmedMessages.unshift(message);
    }
    
    context.messages = trimmedMessages;
    return context;
  }
  
  private estimateTokens(text: string): number {
    // 간단한 토큰 추정 (실제로는 tokenizer 사용)
    return Math.ceil(text.length / 4);
  }
  
  async clearContext(sessionId: string): Promise<void> {
    await this.memory.set(`context:${sessionId}`, null);
  }
  
  async getContextSummary(sessionId: string): Promise<string> {
    const context = await this.getContext(sessionId);
    if (!context || context.messages.length === 0) {
      return '';
    }
    
    // 간단한 요약 생성
    const recentMessages = context.messages.slice(-5);
    return recentMessages
      .map(m => `${m.role}: ${m.content.substring(0, 100)}`)
      .join('\n');
  }
}