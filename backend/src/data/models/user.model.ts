import { BaseModel } from './base.model';

export interface UserPreferences {
  theme: 'light' | 'dark';
  language: string;
  notifications: boolean;
  defaultFramework?: string;
}

export class User extends BaseModel {
  email: string;
  username: string;
  role: 'admin' | 'developer' | 'viewer';
  preferences: UserPreferences;
  lastLoginAt?: Date;
  isActive: boolean;

  constructor(data: Partial<User>) {
    super(data.id);
    this.email = data.email!;
    this.username = data.username!;
    this.role = data.role || 'developer';
    this.preferences = data.preferences || {
      theme: 'light',
      language: 'en',
      notifications: true
    };
    this.lastLoginAt = data.lastLoginAt;
    this.isActive = data.isActive ?? true;
  }

  protected getEntityPrefix(): string {
    return 'user';
  }

  protected serialize(): any {
    return {
      email: this.email,
      username: this.username,
      role: this.role,
      preferences: this.preferences,
      lastLoginAt: this.lastLoginAt?.toISOString(),
      isActive: this.isActive
    };
  }

  updateLastLogin(): void {
    this.lastLoginAt = new Date();
    this.updateVersion();
  }

  deactivate(): void {
    this.isActive = false;
    this.updateVersion();
  }
}