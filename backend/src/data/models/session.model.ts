import { BaseModel } from './base.model';

export interface SessionContext {
  projectId?: string;
  currentStep?: string;
  agentStates: Record<string, any>;
  userPreferences: Record<string, any>;
}

export class Session extends BaseModel {
  userId: string;
  projectId?: string;
  status: 'active' | 'paused' | 'completed' | 'expired';
  context: SessionContext;
  expiresAt: Date;
  lastActivityAt: Date;

  constructor(data: Partial<Session>) {
    super(data.id);
    this.userId = data.userId!;
    this.projectId = data.projectId;
    this.status = data.status || 'active';
    this.context = data.context || {
      agentStates: {},
      userPreferences: {}
    };
    this.expiresAt = data.expiresAt || new Date(Date.now() + 8 * 60 * 60 * 1000); // 8 hours
    this.lastActivityAt = data.lastActivityAt || new Date();
  }

  protected getEntityPrefix(): string {
    return 'sess';
  }

  protected serialize(): any {
    return {
      userId: this.userId,
      projectId: this.projectId,
      status: this.status,
      context: this.context,
      expiresAt: this.expiresAt.toISOString(),
      lastActivityAt: this.lastActivityAt.toISOString()
    };
  }

  updateActivity(): void {
    this.lastActivityAt = new Date();
    this.updateVersion();
  }

  updateContext(context: Partial<SessionContext>): void {
    this.context = { ...this.context, ...context };
    this.updateActivity();
  }

  isExpired(): boolean {
    return new Date() > this.expiresAt;
  }

  extend(hours: number = 8): void {
    this.expiresAt = new Date(Date.now() + hours * 60 * 60 * 1000);
    this.updateVersion();
  }
}