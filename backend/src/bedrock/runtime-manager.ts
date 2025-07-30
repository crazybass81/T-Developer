import { AgentCoreClient } from './agentcore-client';

interface RuntimeSession {
  id: string;
  userId: string;
  createdAt: Date;
  lastActivity: Date;
}

export class RuntimeManager {
  private agentCore: AgentCoreClient;
  private sessions: Map<string, RuntimeSession> = new Map();
  
  constructor() {
    this.agentCore = new AgentCoreClient();
  }
  
  async initializeRuntime(): Promise<void> {
    await this.agentCore.createSession('system');
    console.log('✅ AgentCore runtime initialized');
  }
  
  async createAgentSession(userId: string): Promise<string> {
    const sessionId = `session_${userId}_${Date.now()}`;
    await this.agentCore.createSession(sessionId);
    
    this.sessions.set(sessionId, {
      id: sessionId,
      userId,
      createdAt: new Date(),
      lastActivity: new Date()
    });
    
    return sessionId;
  }
  
  async executeInSession(sessionId: string, input: any): Promise<any> {
    // Create Bedrock session if it doesn't exist
    if (!this.sessions.has(sessionId)) {
      await this.agentCore.createSession(sessionId);
      this.sessions.set(sessionId, {
        id: sessionId,
        userId: 'unknown',
        createdAt: new Date(),
        lastActivity: new Date()
      });
    }
    
    const session = this.sessions.get(sessionId)!;
    session.lastActivity = new Date();
    return await this.agentCore.executeAgent(sessionId, input);
  }
  
  async cleanupSessions(): Promise<void> {
    const now = new Date();
    const timeout = 8 * 60 * 60 * 1000; // 8 hours
    
    for (const [sessionId, session] of this.sessions) {
      if (now.getTime() - session.lastActivity.getTime() > timeout) {
        this.sessions.delete(sessionId);
      }
    }
  }
}