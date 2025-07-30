import { BaseEntity } from './base.entity';

export interface UserPreferences {
  theme: 'light' | 'dark';
  language: string;
  notifications: boolean;
}

export class UserEntity extends BaseEntity {
  UserId: string;
  Email: string = '';
  Username: string = '';
  Role: 'admin' | 'developer' | 'viewer' = 'developer';
  Preferences: UserPreferences;
  LastLoginAt?: string;
  
  constructor(userId: string) {
    super();
    this.EntityType = 'USER';
    this.EntityId = userId;
    this.UserId = userId;
    this.PK = `USER#${userId}`;
    this.SK = 'METADATA';
    this.Preferences = {
      theme: 'light',
      language: 'en',
      notifications: true
    };
  }
  
  toDynamoDBItem(): Record<string, any> {
    return {
      PK: this.PK,
      SK: this.SK,
      EntityType: this.EntityType,
      EntityId: this.EntityId,
      UserId: this.UserId,
      Email: this.Email,
      Username: this.Username,
      Role: this.Role,
      Preferences: this.Preferences,
      LastLoginAt: this.LastLoginAt,
      CreatedAt: this.CreatedAt,
      UpdatedAt: this.UpdatedAt,
      Version: this.Version,
      GSI1PK: `EMAIL#${this.Email}`,
      GSI1SK: this.UserId
    };
  }
  
  fromDynamoDBItem(item: Record<string, any>): void {
    Object.assign(this, item);
  }
}