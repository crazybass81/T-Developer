/**
 * User Entity Implementation
 * Handles user-specific data, validation, and key generation
 */

import { BaseEntity } from './base.entity';
import { UserData, UserRole, UserPreferences, AuthProvider, EntityStatus } from '../schemas/table-schema';
import { CompositeKeyBuilder } from '../schemas/single-table-design';
import { ValidationError, Validator } from '../validation/validator';
import { v4 as uuidv4 } from 'uuid';

export class UserEntity extends BaseEntity {
  private userData: UserData;

  constructor(data?: Partial<UserData>) {
    super();
    
    this.EntityType = 'USER';
    this.EntityId = data?.userId || uuidv4();
    
    // Initialize user data with defaults
    this.userData = {
      userId: this.EntityId,
      username: data?.username || '',
      email: data?.email || '',
      fullName: data?.fullName,
      avatarUrl: data?.avatarUrl,
      role: data?.role || UserRole.DEVELOPER,
      permissions: data?.permissions || [],
      preferences: data?.preferences || this.getDefaultPreferences(),
      authProviders: data?.authProviders || [],
      lastLoginAt: data?.lastLoginAt,
      emailVerified: data?.emailVerified || false,
      phoneNumber: data?.phoneNumber,
      phoneVerified: data?.phoneVerified || false,
      twoFactorEnabled: data?.twoFactorEnabled || false
    };

    if (data) {
      this.initialize();
    }
  }

  /**
   * Build composite keys for user entity
   */
  protected buildKeys(): void {
    this.PK = CompositeKeyBuilder.buildPK('USER', this.EntityId);
    this.SK = 'PROFILE';
    
    // GSI1: For querying users by email
    this.GSI1PK = `EMAIL#${this.userData.email}`;
    this.GSI1SK = `USER#${this.EntityId}`;
    
    // GSI2: For querying users by role
    this.GSI2PK = `ROLE#${this.userData.role}`;
    this.GSI2SK = `USER#${this.EntityId}`;
    
    // GSI3: For time-based queries
    this.GSI3PK = CompositeKeyBuilder.buildGSI3Keys('USER', this.CreatedAt).GSI3PK;
  }

  /**
   * Validate user entity
   */
  protected validate(): ValidationError[] {
    const schema = {
      ...Validator.Schemas.BaseEntity,
      ...Validator.Schemas.User
    };

    // Add user-specific validations
    const userValidationSchema = {
      username: [
        ...Validator.Schemas.User.username,
        Validator.Rules.custom(
          async (value) => this.isUsernameUnique(value),
          'Username already exists',
          'uniqueUsername'
        )
      ],
      email: [
        ...Validator.Schemas.User.email,
        Validator.Rules.custom(
          async (value) => this.isEmailUnique(value),
          'Email already exists',
          'uniqueEmail'
        )
      ]
    };

    // Merge validation data
    const validationData = {
      ...this,
      ...this.userData
    };

    try {
      return Validator.validate(validationData, { ...schema, ...userValidationSchema }) as ValidationError[];
    } catch (error) {
      return [new ValidationError(`Validation failed: ${error}`)];
    }
  }

  /**
   * Serialize user data to JSON string
   */
  protected serializeData(): string {
    return JSON.stringify(this.userData);
  }

  /**
   * Deserialize user data from JSON string
   */
  protected deserializeData(data: string): void {
    try {
      this.userData = JSON.parse(data);
    } catch (error) {
      throw new Error(`Failed to deserialize user data: ${error}`);
    }
  }

  /**
   * Get default user preferences
   */
  private getDefaultPreferences(): UserPreferences {
    return {
      theme: 'auto',
      language: 'en',
      timezone: 'UTC',
      notifications: {
        email: true,
        push: true,
        sms: false
      }
    };
  }

  /**
   * Check if username is unique (mock implementation)
   * In real implementation, this would query the database
   */
  private async isUsernameUnique(username: string): Promise<boolean> {
    // Mock implementation - in real app, query database
    return true;
  }

  /**
   * Check if email is unique (mock implementation)
   * In real implementation, this would query the database
   */
  private async isEmailUnique(email: string): Promise<boolean> {
    // Mock implementation - in real app, query database
    return true;
  }

  /**
   * Get user data
   */
  public getUserData(): UserData {
    return { ...this.userData };
  }

  /**
   * Update user profile
   */
  public updateProfile(updates: Partial<UserData>, userId?: string): void {
    const sanitizedUpdates = this.sanitizeUserUpdates(updates);
    
    // Update user data
    Object.assign(this.userData, sanitizedUpdates);
    
    // Update base entity
    this.update({}, userId);
  }

  /**
   * Sanitize user data updates
   */
  private sanitizeUserUpdates(updates: Partial<UserData>): Partial<UserData> {
    const sanitized: Partial<UserData> = {};

    if (updates.username) {
      sanitized.username = Validator.sanitize.string(updates.username);
    }
    if (updates.email) {
      sanitized.email = Validator.sanitize.email(updates.email);
    }
    if (updates.fullName) {
      sanitized.fullName = Validator.sanitize.string(updates.fullName);
    }
    if (updates.phoneNumber) {
      sanitized.phoneNumber = Validator.sanitize.string(updates.phoneNumber);
    }
    if (updates.role !== undefined) {
      sanitized.role = updates.role;
    }
    if (updates.permissions) {
      sanitized.permissions = Validator.sanitize.array(updates.permissions);
    }
    if (updates.preferences) {
      sanitized.preferences = updates.preferences;
    }
    if (updates.emailVerified !== undefined) {
      sanitized.emailVerified = updates.emailVerified;
    }
    if (updates.phoneVerified !== undefined) {
      sanitized.phoneVerified = updates.phoneVerified;
    }
    if (updates.twoFactorEnabled !== undefined) {
      sanitized.twoFactorEnabled = updates.twoFactorEnabled;
    }

    return sanitized;
  }

  /**
   * Update user role
   */
  public updateRole(role: UserRole, userId?: string): void {
    this.userData.role = role;
    this.update({}, userId);
    
    // Rebuild keys since GSI2 depends on role
    this.buildKeys();
  }

  /**
   * Add permission to user
   */
  public addPermission(permission: string): void {
    if (!this.userData.permissions.includes(permission)) {
      this.userData.permissions.push(permission);
      this.update({});
    }
  }

  /**
   * Remove permission from user
   */
  public removePermission(permission: string): void {
    const index = this.userData.permissions.indexOf(permission);
    if (index > -1) {
      this.userData.permissions.splice(index, 1);
      this.update({});
    }
  }

  /**
   * Check if user has permission
   */
  public hasPermission(permission: string): boolean {
    return this.userData.permissions.includes(permission) || 
           this.userData.role === UserRole.ADMIN;
  }

  /**
   * Update user preferences
   */
  public updatePreferences(preferences: Partial<UserPreferences>): void {
    this.userData.preferences = {
      ...this.userData.preferences,
      ...preferences
    };
    this.update({});
  }

  /**
   * Add authentication provider
   */
  public addAuthProvider(provider: AuthProvider): void {
    // Remove existing provider of same type
    this.userData.authProviders = this.userData.authProviders.filter(
      p => p.provider !== provider.provider
    );
    
    // Add new provider
    this.userData.authProviders.push({
      ...provider,
      linkedAt: new Date().toISOString()
    });
    
    this.update({});
  }

  /**
   * Remove authentication provider
   */
  public removeAuthProvider(providerType: AuthProvider['provider']): void {
    this.userData.authProviders = this.userData.authProviders.filter(
      p => p.provider !== providerType
    );
    this.update({});
  }

  /**
   * Update last login timestamp
   */
  public updateLastLogin(): void {
    this.userData.lastLoginAt = new Date().toISOString();
    this.update({});
  }

  /**
   * Verify email
   */
  public verifyEmail(): void {
    this.userData.emailVerified = true;
    this.update({});
  }

  /**
   * Verify phone
   */
  public verifyPhone(): void {
    this.userData.phoneVerified = true;
    this.update({});
  }

  /**
   * Enable two-factor authentication
   */
  public enableTwoFactor(): void {
    this.userData.twoFactorEnabled = true;
    this.update({});
  }

  /**
   * Disable two-factor authentication
   */
  public disableTwoFactor(): void {
    this.userData.twoFactorEnabled = false;
    this.update({});
  }

  /**
   * Get user's full name or username
   */
  public getDisplayName(): string {
    return this.userData.fullName || this.userData.username;
  }

  /**
   * Check if user is admin
   */
  public isAdmin(): boolean {
    return this.userData.role === UserRole.ADMIN;
  }

  /**
   * Check if user can manage projects
   */
  public canManageProjects(): boolean {
    return this.userData.role === UserRole.ADMIN || 
           this.userData.role === UserRole.MANAGER ||
           this.hasPermission('project.manage');
  }

  /**
   * Check if user account is complete
   */
  public isAccountComplete(): boolean {
    return !!(
      this.userData.username &&
      this.userData.email &&
      this.userData.emailVerified &&
      this.userData.fullName
    );
  }

  /**
   * Get security score (0-100)
   */
  public getSecurityScore(): number {
    let score = 0;
    
    if (this.userData.emailVerified) score += 25;
    if (this.userData.phoneVerified) score += 15;
    if (this.userData.twoFactorEnabled) score += 30;
    if (this.userData.authProviders.length > 1) score += 20;
    if (this.userData.phoneNumber) score += 10;
    
    return Math.min(score, 100);
  }

  /**
   * Get user activity status
   */
  public getActivityStatus(): 'active' | 'inactive' | 'new' {
    if (!this.userData.lastLoginAt) {
      return 'new';
    }
    
    const daysSinceLogin = (Date.now() - new Date(this.userData.lastLoginAt).getTime()) / (1000 * 60 * 60 * 24);
    
    if (daysSinceLogin > 30) {
      return 'inactive';
    }
    
    return 'active';
  }

  /**
   * Create user session data for login
   */
  public createSessionData(): {
    userId: string;
    username: string;
    email: string;
    role: UserRole;
    permissions: string[];
  } {
    return {
      userId: this.userData.userId,
      username: this.userData.username,
      email: this.userData.email,
      role: this.userData.role,
      permissions: this.userData.permissions
    };
  }

  /**
   * Create user items for batch operations
   */
  public createUserItems(): Array<any> {
    const items = [
      // Main user profile
      this.toDynamoDBItem(),
      
      // Email index item for quick lookup
      {
        PK: `EMAIL#${this.userData.email}`,
        SK: 'LOOKUP',
        EntityType: 'USER_LOOKUP',
        EntityId: this.EntityId,
        Status: this.Status,
        CreatedAt: this.CreatedAt,
        UpdatedAt: this.UpdatedAt,
        Data: JSON.stringify({ userId: this.EntityId, username: this.userData.username })
      },
      
      // Username index item for quick lookup
      {
        PK: `USERNAME#${this.userData.username}`,
        SK: 'LOOKUP', 
        EntityType: 'USER_LOOKUP',
        EntityId: this.EntityId,
        Status: this.Status,
        CreatedAt: this.CreatedAt,
        UpdatedAt: this.UpdatedAt,
        Data: JSON.stringify({ userId: this.EntityId, email: this.userData.email })
      }
    ];

    return items;
  }
}