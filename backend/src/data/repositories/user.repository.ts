/**
 * User Repository Implementation
 * Provides user-specific data access methods and business logic
 */

import { BaseRepository, QueryResult, AdvancedQueryOptions } from './base.repository';
import { BaseModel } from '../models/base.model';
import { UserEntity } from '../entities/user.entity';
import { UserData, UserRole, EntityStatus } from '../schemas/table-schema';
import { SingleTableClient } from '../dynamodb/single-table';
import { ValidationError, Validator } from '../validation/validator';

/**
 * User-specific model implementation
 */
class UserModel extends BaseModel<UserEntity, UserData> {
  protected createEntity(data: UserData): UserEntity {
    return new UserEntity(data);
  }

  protected getEntityType(): string {
    return 'USER';
  }

  protected getDefaultSortKey(): string {
    return 'PROFILE';
  }

  protected getEntityClass(): new () => UserEntity {
    return UserEntity;
  }
}

export interface UserSearchOptions extends AdvancedQueryOptions {
  roles?: UserRole[];
  emailVerified?: boolean;
  twoFactorEnabled?: boolean;
  lastLoginRange?: {
    from: string;
    to: string;
  };
}

export interface UserActivitySummary {
  totalUsers: number;
  activeUsers: number;
  newUsersThisMonth: number;
  usersByRole: Record<UserRole, number>;
  averageSessionTime: number;
  topUsers: Array<{
    userId: string;
    username: string;
    activityScore: number;
  }>;
}

/**
 * User Repository with comprehensive user management functionality
 */
export class UserRepository extends BaseRepository<UserEntity, UserData> {
  constructor(client?: SingleTableClient) {
    const userModel = new UserModel(client);
    super(userModel, {
      enableCaching: true,
      cacheExpiration: 600, // 10 minutes for user data
      enableMetrics: true,
      enableAuditLog: true
    });
  }

  protected getRepositoryName(): string {
    return 'User';
  }

  /**
   * Find user by email address
   */
  public async findByEmail(email: string): Promise<UserEntity | null> {
    const startTime = Date.now();

    try {
      // Use GSI1 to query by email
      const result = await this.client.query({
        indexName: 'GSI1',
        gsi1pk: `EMAIL#${email.toLowerCase()}`,
        gsi1sk: 'USER#',
        limit: 1
      });

      if (result.items.length === 0) {
        return null;
      }

      const userEntity = BaseRepository.fromDynamoDBItem(
        result.items[0],
        UserEntity
      );

      // Cache the result
      this.setToCache(userEntity.EntityId, userEntity);
      this.logAudit('READ_BY_EMAIL', userEntity.EntityId, undefined, { email });

      return userEntity;
    } catch (error) {
      throw new Error(`Failed to find user by email: ${error}`);
    } finally {
      this.trackMetrics('query', Date.now() - startTime);
    }
  }

  /**
   * Find user by username
   */
  public async findByUsername(username: string): Promise<UserEntity | null> {
    const startTime = Date.now();

    try {
      // Use scan with filter (could be optimized with a dedicated GSI)
      const result = await this.client.scan({
        filter: 'contains(#data, :username)',
        expressionAttributeNames: {
          '#data': 'Data'
        },
        expressionAttributeValues: {
          ':username': `"username":"${username}"`
        },
        limit: 1
      });

      const userItems = result.items.filter(item => 
        item.EntityType === 'USER' && item.SK === 'PROFILE'
      );

      if (userItems.length === 0) {
        return null;
      }

      const userEntity = BaseRepository.fromDynamoDBItem(
        userItems[0],
        UserEntity
      );

      this.setToCache(userEntity.EntityId, userEntity);
      this.logAudit('READ_BY_USERNAME', userEntity.EntityId, undefined, { username });

      return userEntity;
    } catch (error) {
      throw new Error(`Failed to find user by username: ${error}`);
    } finally {
      this.trackMetrics('query', Date.now() - startTime);
    }
  }

  /**
   * Find users by role
   */
  public async findByRole(
    role: UserRole,
    options: UserSearchOptions = {}
  ): Promise<QueryResult<UserEntity>> {
    const startTime = Date.now();

    try {
      // Use GSI2 to query by role
      const result = await this.client.query({
        indexName: 'GSI2',
        gsi2pk: `ROLE#${role}`,
        limit: options.limit,
        lastEvaluatedKey: options.lastEvaluatedKey,
        scanIndexForward: options.scanIndexForward
      });

      const entities = result.items.map(item => 
        BaseRepository.fromDynamoDBItem(item, UserEntity)
      );

      // Apply additional filters
      let filteredEntities = entities;
      if (options.emailVerified !== undefined) {
        filteredEntities = filteredEntities.filter(user => {
          const userData = user.getUserData();
          return userData.emailVerified === options.emailVerified;
        });
      }

      if (options.twoFactorEnabled !== undefined) {
        filteredEntities = filteredEntities.filter(user => {
          const userData = user.getUserData();
          return userData.twoFactorEnabled === options.twoFactorEnabled;
        });
      }

      this.logAudit('LIST_BY_ROLE', '', undefined, { 
        role, 
        count: filteredEntities.length 
      });

      return {
        items: filteredEntities,
        lastEvaluatedKey: result.lastEvaluatedKey,
        count: filteredEntities.length
      };
    } catch (error) {
      throw new Error(`Failed to find users by role: ${error}`);
    } finally {
      this.trackMetrics('query', Date.now() - startTime);
    }
  }

  /**
   * Find users with advanced search capabilities
   */
  public async searchUsers(options: UserSearchOptions): Promise<QueryResult<UserEntity>> {
    const startTime = Date.now();

    try {
      // Start with all users
      let result = await this.findAll(options);

      // Apply user-specific filters
      let filteredUsers = result.items;

      if (options.roles && options.roles.length > 0) {
        filteredUsers = filteredUsers.filter(user => {
          const userData = user.getUserData();
          return options.roles!.includes(userData.role);
        });
      }

      if (options.emailVerified !== undefined) {
        filteredUsers = filteredUsers.filter(user => {
          const userData = user.getUserData();
          return userData.emailVerified === options.emailVerified;
        });
      }

      if (options.twoFactorEnabled !== undefined) {
        filteredUsers = filteredUsers.filter(user => {
          const userData = user.getUserData();
          return userData.twoFactorEnabled === options.twoFactorEnabled;
        });
      }

      if (options.lastLoginRange) {
        const fromDate = new Date(options.lastLoginRange.from);
        const toDate = new Date(options.lastLoginRange.to);
        
        filteredUsers = filteredUsers.filter(user => {
          const userData = user.getUserData();
          if (!userData.lastLoginAt) return false;
          
          const loginDate = new Date(userData.lastLoginAt);
          return loginDate >= fromDate && loginDate <= toDate;
        });
      }

      // Apply sorting if specified
      if (options.sort) {
        filteredUsers = this.applySort(filteredUsers, options.sort);
      }

      this.logAudit('SEARCH_USERS', '', undefined, { 
        options, 
        count: filteredUsers.length 
      });

      return {
        items: filteredUsers,
        lastEvaluatedKey: result.lastEvaluatedKey,
        count: filteredUsers.length
      };
    } catch (error) {
      throw new Error(`Failed to search users: ${error}`);
    } finally {
      this.trackMetrics('query', Date.now() - startTime);
    }
  }

  /**
   * Check if email is already taken
   */
  public async isEmailTaken(email: string, excludeUserId?: string): Promise<boolean> {
    const user = await this.findByEmail(email);
    
    if (!user) return false;
    
    // If excluding a specific user (for updates), check if it's a different user
    if (excludeUserId && user.EntityId === excludeUserId) {
      return false;
    }
    
    return true;
  }

  /**
   * Check if username is already taken
   */
  public async isUsernameTaken(username: string, excludeUserId?: string): Promise<boolean> {
    const user = await this.findByUsername(username);
    
    if (!user) return false;
    
    if (excludeUserId && user.EntityId === excludeUserId) {
      return false;
    }
    
    return true;
  }

  /**
   * Create user with validation
   */
  public async createUser(userData: UserData, createdBy?: string): Promise<UserEntity> {
    // Validate unique constraints
    const [emailTaken, usernameTaken] = await Promise.all([
      this.isEmailTaken(userData.email),
      this.isUsernameTaken(userData.username)
    ]);

    if (emailTaken) {
      throw new ValidationError('Email already exists', 'email', 'DUPLICATE_EMAIL');
    }

    if (usernameTaken) {
      throw new ValidationError('Username already exists', 'username', 'DUPLICATE_USERNAME');
    }

    return await this.create(userData, createdBy);
  }

  /**
   * Update user with validation
   */
  public async updateUser(
    userId: string,
    updates: Partial<UserData>,
    updatedBy?: string
  ): Promise<UserEntity | null> {
    // Check unique constraints if updating email or username
    if (updates.email) {
      const emailTaken = await this.isEmailTaken(updates.email, userId);
      if (emailTaken) {
        throw new ValidationError('Email already exists', 'email', 'DUPLICATE_EMAIL');
      }
    }

    if (updates.username) {
      const usernameTaken = await this.isUsernameTaken(updates.username, userId);
      if (usernameTaken) {
        throw new ValidationError('Username already exists', 'username', 'DUPLICATE_USERNAME');
      }
    }

    return await this.update(userId, updates, updatedBy);
  }

  /**
   * Get users by activity status
   */
  public async getUsersByActivity(
    activityStatus: 'active' | 'inactive' | 'new',
    options: UserSearchOptions = {}
  ): Promise<QueryResult<UserEntity>> {
    const allUsers = await this.findAll(options);
    
    const filteredUsers = allUsers.items.filter(user => {
      const userData = user.getUserData();
      
      if (activityStatus === 'new') {
        return !userData.lastLoginAt;
      }
      
      if (!userData.lastLoginAt) return false;
      
      const daysSinceLogin = (Date.now() - new Date(userData.lastLoginAt).getTime()) / (1000 * 60 * 60 * 24);
      
      if (activityStatus === 'active') {
        return daysSinceLogin <= 30;
      } else {
        return daysSinceLogin > 30;
      }
    });

    return {
      items: filteredUsers,
      lastEvaluatedKey: allUsers.lastEvaluatedKey,
      count: filteredUsers.length
    };
  }

  /**
   * Get user activity summary
   */
  public async getUserActivitySummary(): Promise<UserActivitySummary> {
    const [allUsers, stats] = await Promise.all([
      this.findAll({ limit: 1000 }),
      this.getStatistics()
    ]);

    const now = new Date();
    const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);

    let newUsersThisMonth = 0;
    const usersByRole: Record<UserRole, number> = {
      [UserRole.ADMIN]: 0,
      [UserRole.MANAGER]: 0,
      [UserRole.DEVELOPER]: 0,
      [UserRole.VIEWER]: 0
    };

    const topUsers: Array<{
      userId: string;
      username: string;
      activityScore: number;
    }> = [];

    for (const user of allUsers.items) {
      const userData = user.getUserData();
      
      // Count new users this month
      if (new Date(user.CreatedAt) >= startOfMonth) {
        newUsersThisMonth++;
      }

      // Count by role
      usersByRole[userData.role]++;

      // Calculate activity score (simplified)
      let activityScore = 0;
      if (userData.lastLoginAt) {
        const daysSinceLogin = (Date.now() - new Date(userData.lastLoginAt).getTime()) / (1000 * 60 * 60 * 24);
        activityScore = Math.max(0, 100 - daysSinceLogin);
      }

      topUsers.push({
        userId: user.EntityId,
        username: userData.username,
        activityScore
      });
    }

    // Sort top users by activity score
    topUsers.sort((a, b) => b.activityScore - a.activityScore);

    return {
      totalUsers: stats.total,
      activeUsers: stats.active,
      newUsersThisMonth,
      usersByRole,
      averageSessionTime: 0, // Would need session tracking
      topUsers: topUsers.slice(0, 10)
    };
  }

  /**
   * Get user security metrics
   */
  public async getUserSecurityMetrics(): Promise<{
    totalUsers: number;
    emailVerifiedCount: number;
    phoneVerifiedCount: number;
    twoFactorEnabledCount: number;
    averageSecurityScore: number;
  }> {
    const users = await this.findAll({ limit: 1000 });
    
    let emailVerifiedCount = 0;
    let phoneVerifiedCount = 0;
    let twoFactorEnabledCount = 0;
    let totalSecurityScore = 0;

    for (const user of users.items) {
      const userData = user.getUserData();
      
      if (userData.emailVerified) emailVerifiedCount++;
      if (userData.phoneVerified) phoneVerifiedCount++;
      if (userData.twoFactorEnabled) twoFactorEnabledCount++;
      
      totalSecurityScore += user.getSecurityScore();
    }

    return {
      totalUsers: users.count,
      emailVerifiedCount,
      phoneVerifiedCount,
      twoFactorEnabledCount,
      averageSecurityScore: users.count > 0 ? totalSecurityScore / users.count : 0
    };
  }

  /**
   * Bulk update user roles
   */
  public async bulkUpdateRoles(
    userIds: string[],
    newRole: UserRole,
    updatedBy?: string
  ): Promise<UserEntity[]> {
    const updatedUsers: UserEntity[] = [];

    // Process in batches to avoid overwhelming the database
    const batchSize = 10;
    for (let i = 0; i < userIds.length; i += batchSize) {
      const batch = userIds.slice(i, i + batchSize);
      
      const batchPromises = batch.map(async (userId) => {
        try {
          const updated = await this.updateUser(
            userId,
            { role: newRole } as any,
            updatedBy
          );
          if (updated) {
            updatedUsers.push(updated);
          }
        } catch (error) {
          // Log error but continue with other users
          console.error(`Failed to update role for user ${userId}:`, error);
        }
      });

      await Promise.all(batchPromises);
    }

    this.logAudit('BULK_UPDATE_ROLES', '', updatedBy, { 
      userIds, 
      newRole, 
      successCount: updatedUsers.length 
    });

    return updatedUsers;
  }

  /**
   * Clean up inactive users (soft delete users inactive for specified days)
   */
  public async cleanupInactiveUsers(
    inactiveDays: number = 365,
    performedBy?: string
  ): Promise<number> {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - inactiveDays);

    const allUsers = await this.findAll({ limit: 1000 });
    const inactiveUsers = allUsers.items.filter(user => {
      const userData = user.getUserData();
      
      // Consider users inactive if they never logged in or haven't logged in for the specified period
      if (!userData.lastLoginAt) {
        return new Date(user.CreatedAt) < cutoffDate;
      }
      
      return new Date(userData.lastLoginAt) < cutoffDate;
    });

    let cleanedCount = 0;
    for (const user of inactiveUsers) {
      try {
        await this.archive(user.EntityId, performedBy);
        cleanedCount++;
      } catch (error) {
        console.error(`Failed to archive inactive user ${user.EntityId}:`, error);
      }
    }

    this.logAudit('CLEANUP_INACTIVE', '', performedBy, { 
      inactiveDays,
      totalChecked: allUsers.count,
      cleanedCount 
    });

    return cleanedCount;
  }
}