/**
 * Project Entity Implementation
 * Handles project-specific data, validation, and key generation
 */

import { BaseEntity } from './base.entity';
import { ProjectData, ProjectSettings, ProjectMetrics, EntityStatus } from '../schemas/table-schema';
import { CompositeKeyBuilder } from '../schemas/single-table-design';
import { ValidationError, Validator } from '../validation/validator';
import { v4 as uuidv4 } from 'uuid';

export class ProjectEntity extends BaseEntity {
  private projectData: ProjectData;

  constructor(data?: Partial<ProjectData>) {
    super();
    
    this.EntityType = 'PROJECT';
    this.EntityId = data?.projectId || uuidv4();
    
    // Initialize project data with defaults
    this.projectData = {
      projectId: this.EntityId,
      name: data?.name || '',
      description: data?.description,
      ownerId: data?.ownerId || '',
      organizationId: data?.organizationId,
      visibility: data?.visibility || 'private',
      repository: data?.repository,
      settings: data?.settings || this.getDefaultSettings(),
      tags: data?.tags || [],
      metrics: data?.metrics || this.getDefaultMetrics()
    };

    if (data) {
      this.initialize();
    }
  }

  /**
   * Build composite keys for project entity
   */
  protected buildKeys(): void {
    this.PK = CompositeKeyBuilder.buildPK('PROJECT', this.EntityId);
    this.SK = 'METADATA';
    
    // GSI1: For querying projects by owner
    this.GSI1PK = `USER#${this.projectData.ownerId}`;
    this.GSI1SK = `PROJECT#${this.EntityId}`;
    
    // GSI2: For querying projects by organization
    if (this.projectData.organizationId) {
      this.GSI2PK = `ORG#${this.projectData.organizationId}`;
      this.GSI2SK = `PROJECT#${this.EntityId}`;
    }
    
    // GSI3: For time-based queries
    this.GSI3PK = CompositeKeyBuilder.buildGSI3Keys('PROJECT', this.CreatedAt).GSI3PK;
  }

  /**
   * Validate project entity
   */
  protected validate(): ValidationError[] {
    const schema = {
      ...Validator.Schemas.BaseEntity,
      ...Validator.Schemas.Project
    };

    // Add project-specific validations
    const projectValidationSchema = {
      name: [
        ...Validator.Schemas.Project.name,
        Validator.Rules.custom(
          async (value) => this.isProjectNameUnique(value, this.projectData.ownerId),
          'Project name already exists for this owner',
          'uniqueProjectName'
        )
      ],
      repository: [
        Validator.Rules.custom(
          (value) => this.validateRepository(value),
          'Invalid repository configuration'
        )
      ]
    };

    // Merge validation data
    const validationData = {
      ...this,
      ...this.projectData
    };

    try {
      return Validator.validate(validationData, { ...schema, ...projectValidationSchema }) as ValidationError[];
    } catch (error) {
      return [new ValidationError(`Validation failed: ${error}`)];
    }
  }

  /**
   * Serialize project data to JSON string
   */
  protected serializeData(): string {
    return JSON.stringify(this.projectData);
  }

  /**
   * Deserialize project data from JSON string
   */
  protected deserializeData(data: string): void {
    try {
      this.projectData = JSON.parse(data);
    } catch (error) {
      throw new Error(`Failed to deserialize project data: ${error}`);
    }
  }

  /**
   * Get default project settings
   */
  private getDefaultSettings(): ProjectSettings {
    return {
      autoDeployEnabled: false,
      cicdEnabled: false,
      monitoringEnabled: true,
      alertingEnabled: true,
      backupEnabled: true,
      maxAgents: 10,
      maxTasks: 100,
      resourceLimits: {
        cpu: 2,
        memory: 4096,
        storage: 10240
      }
    };
  }

  /**
   * Get default project metrics
   */
  private getDefaultMetrics(): ProjectMetrics {
    return {
      totalTasks: 0,
      completedTasks: 0,
      failedTasks: 0,
      avgExecutionTime: 0,
      lastActivityAt: new Date().toISOString(),
      storageUsed: 0,
      computeHours: 0
    };
  }

  /**
   * Check if project name is unique for owner (mock implementation)
   */
  private async isProjectNameUnique(name: string, ownerId: string): Promise<boolean> {
    // Mock implementation - in real app, query database
    return true;
  }

  /**
   * Validate repository configuration
   */
  private validateRepository(repository?: ProjectData['repository']): boolean {
    if (!repository) return true;
    
    return !!(
      repository.type &&
      ['github', 'gitlab', 'bitbucket', 'codecommit'].includes(repository.type) &&
      repository.url &&
      repository.branch
    );
  }

  /**
   * Get project data
   */
  public getProjectData(): ProjectData {
    return { ...this.projectData };
  }

  /**
   * Update project information
   */
  public updateProject(updates: Partial<ProjectData>, userId?: string): void {
    const sanitizedUpdates = this.sanitizeProjectUpdates(updates);
    
    // Update project data
    Object.assign(this.projectData, sanitizedUpdates);
    
    // Update metrics if needed
    this.projectData.metrics.lastActivityAt = new Date().toISOString();
    
    // Update base entity
    this.update({}, userId);
  }

  /**
   * Sanitize project data updates
   */
  private sanitizeProjectUpdates(updates: Partial<ProjectData>): Partial<ProjectData> {
    const sanitized: Partial<ProjectData> = {};

    if (updates.name) {
      sanitized.name = Validator.sanitize.string(updates.name);
    }
    if (updates.description) {
      sanitized.description = Validator.sanitize.string(updates.description);
    }
    if (updates.visibility !== undefined) {
      sanitized.visibility = updates.visibility;
    }
    if (updates.repository) {
      sanitized.repository = updates.repository;
    }
    if (updates.settings) {
      sanitized.settings = updates.settings;
    }
    if (updates.tags) {
      sanitized.tags = Validator.sanitize.array(updates.tags);
    }

    return sanitized;
  }

  /**
   * Update project settings
   */
  public updateSettings(settings: Partial<ProjectSettings>): void {
    this.projectData.settings = {
      ...this.projectData.settings,
      ...settings
    };
    this.update({});
  }

  /**
   * Add tag to project
   */
  public addTag(tag: string): void {
    const sanitizedTag = Validator.sanitize.string(tag).toLowerCase();
    if (sanitizedTag && !this.projectData.tags.includes(sanitizedTag)) {
      this.projectData.tags.push(sanitizedTag);
      this.update({});
    }
  }

  /**
   * Remove tag from project
   */
  public removeTag(tag: string): void {
    const index = this.projectData.tags.indexOf(tag.toLowerCase());
    if (index > -1) {
      this.projectData.tags.splice(index, 1);
      this.update({});
    }
  }

  /**
   * Set repository configuration
   */
  public setRepository(repository: ProjectData['repository']): void {
    this.projectData.repository = repository;
    this.update({});
  }

  /**
   * Remove repository configuration
   */
  public removeRepository(): void {
    this.projectData.repository = undefined;
    this.update({});
  }

  /**
   * Transfer project ownership
   */
  public transferOwnership(newOwnerId: string, userId?: string): void {
    this.projectData.ownerId = newOwnerId;
    this.update({}, userId);
    
    // Rebuild keys since GSI1 depends on owner
    this.buildKeys();
  }

  /**
   * Update project metrics
   */
  public updateMetrics(metrics: Partial<ProjectMetrics>): void {
    this.projectData.metrics = {
      ...this.projectData.metrics,
      ...metrics,
      lastActivityAt: new Date().toISOString()
    };
    this.update({});
  }

  /**
   * Increment task counters
   */
  public incrementTaskCount(type: 'total' | 'completed' | 'failed' = 'total'): void {
    switch (type) {
      case 'total':
        this.projectData.metrics.totalTasks++;
        break;
      case 'completed':
        this.projectData.metrics.completedTasks++;
        break;
      case 'failed':
        this.projectData.metrics.failedTasks++;
        break;
    }
    
    this.projectData.metrics.lastActivityAt = new Date().toISOString();
    this.update({});
  }

  /**
   * Update average execution time
   */
  public updateAvgExecutionTime(newExecutionTime: number): void {
    const currentAvg = this.projectData.metrics.avgExecutionTime;
    const totalTasks = this.projectData.metrics.totalTasks;
    
    if (totalTasks === 0) {
      this.projectData.metrics.avgExecutionTime = newExecutionTime;
    } else {
      this.projectData.metrics.avgExecutionTime = 
        ((currentAvg * totalTasks) + newExecutionTime) / (totalTasks + 1);
    }
    
    this.update({});
  }

  /**
   * Add storage usage
   */
  public addStorageUsage(bytes: number): void {
    this.projectData.metrics.storageUsed += bytes;
    this.update({});
  }

  /**
   * Add compute hours
   */
  public addComputeHours(hours: number): void {
    this.projectData.metrics.computeHours += hours;
    this.update({});
  }

  /**
   * Check if user is project owner
   */
  public isOwner(userId: string): boolean {
    return this.projectData.ownerId === userId;
  }

  /**
   * Check if project has repository configured
   */
  public hasRepository(): boolean {
    return !!this.projectData.repository;
  }

  /**
   * Check if project is public
   */
  public isPublic(): boolean {
    return this.projectData.visibility === 'public';
  }

  /**
   * Check if project belongs to organization
   */
  public isOrganizationProject(): boolean {
    return !!this.projectData.organizationId;
  }

  /**
   * Get project completion percentage
   */
  public getCompletionRate(): number {
    const { totalTasks, completedTasks } = this.projectData.metrics;
    if (totalTasks === 0) return 0;
    return Math.round((completedTasks / totalTasks) * 100);
  }

  /**
   * Get project success rate (excluding failed tasks)
   */
  public getSuccessRate(): number {
    const { totalTasks, failedTasks } = this.projectData.metrics;
    if (totalTasks === 0) return 100;
    return Math.round(((totalTasks - failedTasks) / totalTasks) * 100);
  }

  /**
   * Get project activity status
   */
  public getActivityStatus(): 'active' | 'inactive' | 'stale' {
    const daysSinceActivity = (Date.now() - new Date(this.projectData.metrics.lastActivityAt).getTime()) / (1000 * 60 * 60 * 24);
    
    if (daysSinceActivity <= 7) return 'active';
    if (daysSinceActivity <= 30) return 'inactive';
    return 'stale';
  }

  /**
   * Check if project has reached limits
   */
  public hasReachedLimits(): {
    agents: boolean;
    tasks: boolean;
    storage: boolean;
  } {
    return {
      agents: false, // Would need agent count from repository
      tasks: this.projectData.metrics.totalTasks >= this.projectData.settings.maxTasks,
      storage: this.projectData.metrics.storageUsed >= this.projectData.settings.resourceLimits.storage * 1024 * 1024
    };
  }

  /**
   * Get project resource usage
   */
  public getResourceUsage(): {
    storageUsed: number;
    storageLimit: number;
    storagePercentage: number;
    computeHours: number;
    tasksUsed: number;
    tasksLimit: number;
    tasksPercentage: number;
  } {
    const storageLimit = this.projectData.settings.resourceLimits.storage * 1024 * 1024;
    const storagePercentage = (this.projectData.metrics.storageUsed / storageLimit) * 100;
    const tasksPercentage = (this.projectData.metrics.totalTasks / this.projectData.settings.maxTasks) * 100;

    return {
      storageUsed: this.projectData.metrics.storageUsed,
      storageLimit,
      storagePercentage: Math.min(storagePercentage, 100),
      computeHours: this.projectData.metrics.computeHours,
      tasksUsed: this.projectData.metrics.totalTasks,
      tasksLimit: this.projectData.settings.maxTasks,
      tasksPercentage: Math.min(tasksPercentage, 100)
    };
  }

  /**
   * Create project summary for dashboards
   */
  public createSummary(): {
    projectId: string;
    name: string;
    description?: string;
    visibility: string;
    tags: string[];
    completionRate: number;
    successRate: number;
    activityStatus: string;
    lastActivity: string;
    totalTasks: number;
  } {
    return {
      projectId: this.projectData.projectId,
      name: this.projectData.name,
      description: this.projectData.description,
      visibility: this.projectData.visibility,
      tags: this.projectData.tags,
      completionRate: this.getCompletionRate(),
      successRate: this.getSuccessRate(),
      activityStatus: this.getActivityStatus(),
      lastActivity: this.projectData.metrics.lastActivityAt,
      totalTasks: this.projectData.metrics.totalTasks
    };
  }

  /**
   * Create project items for batch operations
   */
  public createProjectItems(): Array<any> {
    const items = [
      // Main project metadata
      this.toDynamoDBItem()
    ];

    // Add owner relationship item
    items.push({
      PK: `USER#${this.projectData.ownerId}`,
      SK: `PROJECT#${this.EntityId}`,
      EntityType: 'USER_PROJECT',
      EntityId: `${this.projectData.ownerId}#${this.EntityId}`,
      Status: this.Status,
      CreatedAt: this.CreatedAt,
      UpdatedAt: this.UpdatedAt,
      Data: JSON.stringify({
        projectId: this.EntityId,
        projectName: this.projectData.name,
        role: 'owner'
      }),
      GSI1PK: `PROJECT#${this.EntityId}`,
      GSI1SK: `USER#${this.projectData.ownerId}`
    });

    // Add organization relationship if applicable
    if (this.projectData.organizationId) {
      items.push({
        PK: `ORG#${this.projectData.organizationId}`,
        SK: `PROJECT#${this.EntityId}`,
        EntityType: 'ORG_PROJECT',
        EntityId: `${this.projectData.organizationId}#${this.EntityId}`,
        Status: this.Status,
        CreatedAt: this.CreatedAt,
        UpdatedAt: this.UpdatedAt,
        Data: JSON.stringify({
          projectId: this.EntityId,
          projectName: this.projectData.name
        })
      });
    }

    return items;
  }
}