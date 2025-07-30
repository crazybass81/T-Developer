class ContextManager {
  constructor() {
    this.contexts = new Map();
    this.maxMessages = 100;
    this.maxTokens = 4096;
  }

  async addMessage(sessionId, message) {
    if (!this.contexts.has(sessionId)) {
      this.contexts.set(sessionId, {
        messages: [],
        tokenCount: 0,
        createdAt: new Date(),
        updatedAt: new Date()
      });
    }

    const context = this.contexts.get(sessionId);
    context.messages.push({
      ...message,
      timestamp: new Date()
    });
    
    context.tokenCount += this.estimateTokens(message.content);
    context.updatedAt = new Date();

    if (context.messages.length > this.maxMessages || context.tokenCount > this.maxTokens) {
      await this.trimContext(sessionId);
    }

    return context;
  }

  async getContext(sessionId) {
    return this.contexts.get(sessionId) || null;
  }

  async trimContext(sessionId) {
    const context = this.contexts.get(sessionId);
    if (!context) return;

    while (context.messages.length > this.maxMessages * 0.8) {
      const removed = context.messages.shift();
      context.tokenCount -= this.estimateTokens(removed.content);
    }

    while (context.tokenCount > this.maxTokens * 0.8 && context.messages.length > 1) {
      const removed = context.messages.shift();
      context.tokenCount -= this.estimateTokens(removed.content);
    }
  }

  estimateTokens(text) {
    return Math.ceil(text.length / 4);
  }

  async clearContext(sessionId) {
    return this.contexts.delete(sessionId);
  }

  getStats() {
    return {
      totalSessions: this.contexts.size,
      totalMessages: Array.from(this.contexts.values())
        .reduce((sum, ctx) => sum + ctx.messages.length, 0)
    };
  }
}

module.exports = { ContextManager };