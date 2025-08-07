/**
 * Agent Entity Implementation
 * Handles agent-specific data, validation, and key generation
 */

import { BaseEntity } from './base.entity';
import { AgentData, AgentType, AgentConfiguration, AgentMetrics, AgentHealth, EntityStatus } from '../schemas/table-schema';
import { CompositeKeyBuilder } from '../schemas/single-table-design';
import { ValidationError, Validator } from '../validation/validator';
import { v4 as uuidv4 } from 'uuid';

export class AgentEntity extends BaseEntity {
  private agentData: AgentData;

  constructor(data?: Partial<AgentData>) {
    super();
    
    this.EntityType = 'AGENT';
    this.EntityId = data?.agentId || uuidv4();
    
    // Initialize agent data with defaults
    this.agentData = {
      agentId: this.EntityId,
      name: data?.name || '',
      type: data?.type || AgentType.CUSTOM,
      version: data?.version || '1.0.0',
      description: data?.description,
      projectId: data?.projectId || '',
      configuration: data?.configuration || this.getDefaultConfiguration(),
      capabilities: data?.capabilities || [],
      dependencies: data?.dependencies || [],
      metrics: data?.metrics || this.getDefaultMetrics(),
      health: data?.health || this.getDefaultHealth()
    };

    if (data) {
      this.initialize();
    }
  }

  /**
   * Build composite keys for agent entity
   */
  protected buildKeys(): void {
    this.PK = CompositeKeyBuilder.buildPK('AGENT', this.EntityId);
    this.SK = 'CONFIG';
    
    // GSI1: For querying agents by project
    this.GSI1PK = `PROJECT#${this.agentData.projectId}`;
    this.GSI1SK = `AGENT#${this.EntityId}`;
    
    // GSI2: For querying agents by type
    this.GSI2PK = `AGENT_TYPE#${this.agentData.type}`;
    this.GSI2SK = `AGENT#${this.EntityId}`;
    
    // GSI3: For time-based queries
    this.GSI3PK = CompositeKeyBuilder.buildGSI3Keys('AGENT', this.CreatedAt).GSI3PK;
  }

  /**
   * Validate agent entity
   */
  protected validate(): ValidationError[] {
    const schema = {
      ...Validator.Schemas.BaseEntity,
      ...Validator.Schemas.Agent
    };

    // Add agent-specific validations
    const agentValidationSchema = {
      name: [
        ...Validator.Schemas.Agent.name,
        Validator.Rules.custom(
          async (value) => this.isAgentNameUnique(value, this.agentData.projectId),
          'Agent name already exists in this project',
          'uniqueAgentName'
        )
      ],
      capabilities: [
        Validator.Rules.array('Capabilities must be an array'),
        Validator.Rules.custom(
          (value) => this.validateCapabilities(value),
          'Invalid capabilities configuration'
        )
      ],
      dependencies: [
        Validator.Rules.array('Dependencies must be an array'),
        Validator.Rules.custom(
          (value) => this.validateDependencies(value),
          'Invalid dependencies configuration'
        )
      ]
    };

    // Merge validation data
    const validationData = {
      ...this,
      ...this.agentData
    };

    try {
      return Validator.validate(validationData, { ...schema, ...agentValidationSchema }) as ValidationError[];
    } catch (error) {
      return [new ValidationError(`Validation failed: ${error}`)];
    }
  }

  /**
   * Serialize agent data to JSON string
   */
  protected serializeData(): string {
    return JSON.stringify(this.agentData);
  }

  /**
   * Deserialize agent data from JSON string
   */
  protected deserializeData(data: string): void {
    try {
      this.agentData = JSON.parse(data);
    } catch (error) {
      throw new Error(`Failed to deserialize agent data: ${error}`);
    }
  }

  /**
   * Get default agent configuration
   */
  private getDefaultConfiguration(): AgentConfiguration {
    return {
      model: 'claude-3-sonnet',
      temperature: 0.7,
      maxTokens: 4000,
      timeout: 30000,
      retryPolicy: {
        maxRetries: 3,
        backoffMultiplier: 2
      },
      environment: {},
      resources: {
        cpu: 1,
        memory: 1024
      }
    };
  }

  /**
   * Get default agent metrics
   */
  private getDefaultMetrics(): AgentMetrics {
    return {
      totalExecutions: 0,
      successfulExecutions: 0,
      failedExecutions: 0,
      avgResponseTime: 0,
      p95ResponseTime: 0,
      p99ResponseTime: 0,
      lastExecutionAt: undefined,
      errorRate: 0,
      throughput: 0
    };
  }

  /**
   * Get default agent health
   */
  private getDefaultHealth(): AgentHealth {
    return {
      status: 'unknown',
      lastHealthCheck: new Date().toISOString(),
      issues: [],
      uptime: 0
    };
  }

  /**
   * Check if agent name is unique in project (mock implementation)
   */
  private async isAgentNameUnique(name: string, projectId: string): Promise<boolean> {
    // Mock implementation - in real app, query database
    return true;
  }

  /**
   * Validate agent capabilities
   */
  private validateCapabilities(capabilities: string[]): boolean {
    if (!Array.isArray(capabilities)) return false;
    
    const validCapabilities = [
      'natural_language_processing',
      'code_generation',
      'ui_design',
      'data_analysis',
      'file_operations',
      'api_integration',
      'testing',
      'deployment',
      'monitoring',
      'custom'
    ];

    return capabilities.every(cap => validCapabilities.includes(cap));
  }

  /**
   * Validate agent dependencies
   */
  private validateDependencies(dependencies: string[]): boolean {
    if (!Array.isArray(dependencies)) return false;
    
    // Check if all dependencies are valid agent IDs (UUID format)
    return dependencies.every(dep => 
      typeof dep === 'string' && 
      dep.length > 0 && 
      Validator.Rules.uuid().validator(dep)
    );
  }

  /**
   * Get agent data
   */
  public getAgentData(): AgentData {
    return { ...this.agentData };
  }

  /**
   * Update agent configuration
   */
  public updateAgent(updates: Partial<AgentData>, userId?: string): void {
    const sanitizedUpdates = this.sanitizeAgentUpdates(updates);
    
    // Update agent data
    Object.assign(this.agentData, sanitizedUpdates);
    
    // Update base entity
    this.update({}, userId);
  }

  /**
   * Sanitize agent data updates
   */
  private sanitizeAgentUpdates(updates: Partial<AgentData>): Partial<AgentData> {
    const sanitized: Partial<AgentData> = {};

    if (updates.name) {
      sanitized.name = Validator.sanitize.string(updates.name);
    }
    if (updates.description) {
      sanitized.description = Validator.sanitize.string(updates.description);
    }
    if (updates.version) {
      sanitized.version = Validator.sanitize.string(updates.version);
    }
    if (updates.type !== undefined) {
      sanitized.type = updates.type;
    }
    if (updates.configuration) {
      sanitized.configuration = updates.configuration;
    }
    if (updates.capabilities) {
      sanitized.capabilities = Validator.sanitize.array(updates.capabilities);
    }
    if (updates.dependencies) {
      sanitized.dependencies = Validator.sanitize.array(updates.dependencies);
    }

    return sanitized;
  }

  /**
   * Update agent configuration
   */
  public updateConfiguration(config: Partial<AgentConfiguration>): void {
    this.agentData.configuration = {
      ...this.agentData.configuration,
      ...config
    };
    this.update({});
  }

  /**
   * Add capability to agent
   */
  public addCapability(capability: string): void {
    const sanitizedCapability = Validator.sanitize.string(capability);
    if (sanitizedCapability && !this.agentData.capabilities.includes(sanitizedCapability)) {
      this.agentData.capabilities.push(sanitizedCapability);
      this.update({});
    }
  }

  /**
   * Remove capability from agent
   */
  public removeCapability(capability: string): void {
    const index = this.agentData.capabilities.indexOf(capability);
    if (index > -1) {
      this.agentData.capabilities.splice(index, 1);
      this.update({});
    }
  }

  /**
   * Add dependency to agent
   */
  public addDependency(agentId: string): void {
    if (agentId && !this.agentData.dependencies.includes(agentId)) {
      this.agentData.dependencies.push(agentId);
      this.update({});
    }
  }

  /**
   * Remove dependency from agent
   */
  public removeDependency(agentId: string): void {
    const index = this.agentData.dependencies.indexOf(agentId);
    if (index > -1) {
      this.agentData.dependencies.splice(index, 1);
      this.update({});
    }
  }

  /**
   * Update agent metrics after execution
   */
  public updateMetrics(executionResult: {
    success: boolean;
    responseTime: number;
    error?: string;
  }): void {
    const metrics = this.agentData.metrics;
    
    // Update execution counters
    metrics.totalExecutions++;
    if (executionResult.success) {
      metrics.successfulExecutions++;
    } else {
      metrics.failedExecutions++;
    }
    
    // Update error rate
    metrics.errorRate = (metrics.failedExecutions / metrics.totalExecutions) * 100;
    
    // Update response times
    const totalExecutions = metrics.totalExecutions;
    metrics.avgResponseTime = 
      ((metrics.avgResponseTime * (totalExecutions - 1)) + executionResult.responseTime) / totalExecutions;
    
    // Update percentiles (simplified calculation)
    if (executionResult.responseTime > metrics.p95ResponseTime) {
      metrics.p95ResponseTime = executionResult.responseTime;
    }
    if (executionResult.responseTime > metrics.p99ResponseTime) {
      metrics.p99ResponseTime = executionResult.responseTime;
    }
    
    // Update timestamps
    metrics.lastExecutionAt = new Date().toISOString();
    
    // Calculate throughput (executions per hour over last 24h)
    // This is simplified - in reality, you'd maintain a time window
    metrics.throughput = metrics.totalExecutions / 24; // rough estimate
    
    this.update({});
  }

  /**
   * Update agent health status
   */
  public updateHealth(health: Partial<AgentHealth>): void {
    this.agentData.health = {
      ...this.agentData.health,
      ...health,
      lastHealthCheck: new Date().toISOString()
    };
    this.update({});
  }

  /**
   * Mark agent as healthy
   */
  public markHealthy(): void {
    this.updateHealth({
      status: 'healthy',
      issues: []
    });
  }

  /**
   * Mark agent as unhealthy
   */
  public markUnhealthy(issues: string[]): void {
    this.updateHealth({
      status: 'unhealthy',
      issues
    });
  }

  /**
   * Mark agent as degraded
   */
  public markDegraded(issues: string[]): void {
    this.updateHealth({
      status: 'degraded',
      issues
    });
  }

  /**
   * Check if agent has capability
   */
  public hasCapability(capability: string): boolean {
    return this.agentData.capabilities.includes(capability);
  }

  /**
   * Check if agent depends on another agent
   */
  public dependsOn(agentId: string): boolean {
    return this.agentData.dependencies.includes(agentId);
  }

  /**
   * Check if agent is healthy
   */
  public isHealthy(): boolean {
    return this.agentData.health.status === 'healthy';
  }

  /**
   * Check if agent is ready for execution
   */
  public isReady(): boolean {
    return this.isHealthy() && this.Status === EntityStatus.ACTIVE;
  }

  /**
   * Get agent performance score (0-100)
   */
  public getPerformanceScore(): number {
    const metrics = this.agentData.metrics;
    
    if (metrics.totalExecutions === 0) return 50; // Neutral score for new agents
    
    let score = 0;
    
    // Success rate (40% weight)
    const successRate = (metrics.successfulExecutions / metrics.totalExecutions) * 100;
    score += (successRate * 0.4);
    
    // Response time (30% weight) - lower is better
    const avgResponseTime = metrics.avgResponseTime;
    const responseTimeScore = Math.max(0, 100 - (avgResponseTime / 1000) * 10); // Penalty after 1s
    score += (responseTimeScore * 0.3);
    
    // Health status (20% weight)
    const healthScore = this.agentData.health.status === 'healthy' ? 100 :
                       this.agentData.health.status === 'degraded' ? 60 :
                       this.agentData.health.status === 'unhealthy' ? 20 : 40;
    score += (healthScore * 0.2);
    
    // Uptime (10% weight)
    const uptimeScore = Math.min(100, this.agentData.health.uptime);
    score += (uptimeScore * 0.1);
    
    return Math.round(Math.max(0, Math.min(100, score)));
  }

  /**
   * Get agent utilization rate
   */
  public getUtilizationRate(): number {
    // Simplified calculation - in reality, you'd track active time
    const metrics = this.agentData.metrics;
    if (!metrics.lastExecutionAt) return 0;
    
    const hoursSinceLastExecution = 
      (Date.now() - new Date(metrics.lastExecutionAt).getTime()) / (1000 * 60 * 60);
    
    if (hoursSinceLastExecution > 24) return 0;
    
    return Math.max(0, 100 - (hoursSinceLastExecution * 4)); // Linear decay
  }

  /**
   * Get agent compatibility with task
   */
  public isCompatibleWithTask(requiredCapabilities: string[]): boolean {
    return requiredCapabilities.every(cap => this.hasCapability(cap));
  }

  /**
   * Create agent summary for dashboards
   */
  public createSummary(): {
    agentId: string;
    name: string;
    type: AgentType;
    version: string;
    status: EntityStatus;
    health: string;
    performanceScore: number;
    utilizationRate: number;
    lastExecution?: string;
    totalExecutions: number;
    successRate: number;
  } {
    const metrics = this.agentData.metrics;
    const successRate = metrics.totalExecutions > 0 
      ? (metrics.successfulExecutions / metrics.totalExecutions) * 100 
      : 0;

    return {
      agentId: this.agentData.agentId,
      name: this.agentData.name,
      type: this.agentData.type,
      version: this.agentData.version,
      status: this.Status,
      health: this.agentData.health.status,
      performanceScore: this.getPerformanceScore(),
      utilizationRate: this.getUtilizationRate(),
      lastExecution: metrics.lastExecutionAt,
      totalExecutions: metrics.totalExecutions,
      successRate: Math.round(successRate)
    };
  }

  /**
   * Create agent items for batch operations
   */
  public createAgentItems(): Array<any> {
    const items = [
      // Main agent configuration
      this.toDynamoDBItem()
    ];

    // Add project relationship item
    items.push({
      PK: `PROJECT#${this.agentData.projectId}`,
      SK: `AGENT#${this.EntityId}`,
      EntityType: 'PROJECT_AGENT',
      EntityId: `${this.agentData.projectId}#${this.EntityId}`,
      Status: this.Status,
      CreatedAt: this.CreatedAt,
      UpdatedAt: this.UpdatedAt,
      Data: JSON.stringify({
        agentId: this.EntityId,
        agentName: this.agentData.name,
        agentType: this.agentData.type
      }),
      GSI1PK: `AGENT#${this.EntityId}`,
      GSI1SK: `PROJECT#${this.agentData.projectId}`
    });

    // Add type-based lookup item
    items.push({
      PK: `AGENT_TYPE#${this.agentData.type}`,
      SK: `AGENT#${this.EntityId}`,
      EntityType: 'AGENT_TYPE_LOOKUP',
      EntityId: `${this.agentData.type}#${this.EntityId}`,
      Status: this.Status,
      CreatedAt: this.CreatedAt,
      UpdatedAt: this.UpdatedAt,
      Data: JSON.stringify({
        agentId: this.EntityId,
        agentName: this.agentData.name,
        projectId: this.agentData.projectId
      })
    });

    return items;
  }
}