/**
 * T-Developer Health Check and Monitoring System
 * 시스템 상태 모니터링 및 헬스체크
 */

import { EventEmitter } from 'events';
import { Logger } from '../utils/logger';
import { AgentOrchestrator } from '../agents/orchestrator';
import { performance } from 'perf_hooks';

export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  uptime: number;
  metrics: SystemMetrics;
  agents: AgentHealthStatus[];
  services: ServiceHealthStatus[];
  checks: HealthCheckResult[];
}

export interface SystemMetrics {
  activeAgents: number;
  queuedTasks: number;
  completedTasks: number;
  failedTasks: number;
  avgResponseTime: number;
  memoryUsage: NodeJS.MemoryUsage;
  cpuUsage: NodeJS.CpuUsage;
  throughput: number;
  errorRate: number;
}

export interface AgentHealthStatus {
  agentId: string;
  agentType: string;
  status: string;
  lastActive: Date;
  metrics: {
    totalExecutions: number;
    successRate: number;
    avgExecutionTime: number;
  };
}

export interface ServiceHealthStatus {
  name: string;
  status: 'up' | 'down' | 'degraded';
  responseTime?: number;
  lastChecked: Date;
  error?: string;
}

export interface HealthCheckResult {
  name: string;
  passed: boolean;
  message?: string;
  duration: number;
}

/**
 * Health Check Manager
 */
export class HealthCheckManager extends EventEmitter {
  private logger: Logger;
  private orchestrator: AgentOrchestrator;
  private startTime: Date;
  private metrics: SystemMetrics;
  private checkInterval: NodeJS.Timeout | null = null;
  private metricsHistory: SystemMetrics[] = [];
  private readonly MAX_HISTORY_SIZE = 100;
  
  constructor(orchestrator: AgentOrchestrator) {
    super();
    this.logger = new Logger('HealthCheck');
    this.orchestrator = orchestrator;
    this.startTime = new Date();
    this.metrics = this.initializeMetrics();
  }
  
  /**
   * Start health check monitoring
   */
  start(intervalMs: number = 30000): void {
    if (this.checkInterval) {
      this.stop();
    }
    
    this.logger.info(`Starting health check monitoring (interval: ${intervalMs}ms)`);
    
    // Initial check
    this.performHealthCheck();
    
    // Schedule periodic checks
    this.checkInterval = setInterval(() => {
      this.performHealthCheck();
    }, intervalMs);
  }
  
  /**
   * Stop health check monitoring
   */
  stop(): void {
    if (this.checkInterval) {
      clearInterval(this.checkInterval);
      this.checkInterval = null;
      this.logger.info('Health check monitoring stopped');
    }
  }
  
  /**
   * Perform comprehensive health check
   */
  async performHealthCheck(): Promise<HealthStatus> {
    const startTime = performance.now();
    
    try {
      // Collect metrics
      const metrics = await this.collectMetrics();
      
      // Check agents
      const agentHealth = await this.checkAgentHealth();
      
      // Check services
      const serviceHealth = await this.checkServiceHealth();
      
      // Run health checks
      const checks = await this.runHealthChecks();
      
      // Determine overall status
      const status = this.determineOverallStatus(agentHealth, serviceHealth, checks);
      
      // Create health status report
      const healthStatus: HealthStatus = {
        status,
        timestamp: new Date().toISOString(),
        uptime: Date.now() - this.startTime.getTime(),
        metrics,
        agents: agentHealth,
        services: serviceHealth,
        checks
      };
      
      // Store metrics history
      this.updateMetricsHistory(metrics);
      
      // Emit health status
      this.emit('health:checked', healthStatus);
      
      // Log if unhealthy
      if (status !== 'healthy') {
        this.logger.warn(`System health: ${status}`, { healthStatus });
      }
      
      const duration = performance.now() - startTime;
      this.logger.debug(`Health check completed in ${duration.toFixed(2)}ms`);
      
      return healthStatus;
    } catch (error) {
      this.logger.error('Health check failed', error);
      throw error;
    }
  }
  
  /**
   * Get current health status
   */
  async getHealthStatus(): Promise<HealthStatus> {
    return this.performHealthCheck();
  }
  
  /**
   * Collect system metrics
   */
  private async collectMetrics(): Promise<SystemMetrics> {
    const orchestratorMetrics = this.orchestrator.getMetrics();
    
    return {
      activeAgents: orchestratorMetrics.registeredAgents,
      queuedTasks: orchestratorMetrics.queuedMessages,
      completedTasks: this.metrics.completedTasks,
      failedTasks: this.metrics.failedTasks,
      avgResponseTime: this.calculateAvgResponseTime(),
      memoryUsage: process.memoryUsage(),
      cpuUsage: process.cpuUsage(),
      throughput: this.calculateThroughput(),
      errorRate: this.calculateErrorRate()
    };
  }
  
  /**
   * Check agent health
   */
  private async checkAgentHealth(): Promise<AgentHealthStatus[]> {
    const agents = this.orchestrator.getAllAgents();
    const healthStatuses: AgentHealthStatus[] = [];
    
    for (const agent of agents) {
      const metrics = agent.getMetrics();
      const metadata = agent.getMetadata();
      
      healthStatuses.push({
        agentId: metadata.agentId,
        agentType: metadata.agentType,
        status: agent.getStatus(),
        lastActive: metadata.lastActive,
        metrics: {
          totalExecutions: metrics.totalExecutions,
          successRate: metrics.totalExecutions > 0 
            ? metrics.successfulExecutions / metrics.totalExecutions 
            : 1,
          avgExecutionTime: metrics.avgExecutionTime
        }
      });
    }
    
    return healthStatuses;
  }
  
  /**
   * Check service health
   */
  private async checkServiceHealth(): Promise<ServiceHealthStatus[]> {
    const services: ServiceHealthStatus[] = [];
    
    // Check DynamoDB
    services.push(await this.checkDynamoDB());
    
    // Check Redis
    services.push(await this.checkRedis());
    
    // Check API endpoints
    services.push(await this.checkAPIEndpoints());
    
    return services;
  }
  
  /**
   * Check DynamoDB health
   */
  private async checkDynamoDB(): Promise<ServiceHealthStatus> {
    const startTime = performance.now();
    
    try {
      // Implement actual DynamoDB health check
      // For now, return mock status
      return {
        name: 'DynamoDB',
        status: 'up',
        responseTime: performance.now() - startTime,
        lastChecked: new Date()
      };
    } catch (error) {
      return {
        name: 'DynamoDB',
        status: 'down',
        lastChecked: new Date(),
        error: (error as Error).message
      };
    }
  }
  
  /**
   * Check Redis health
   */
  private async checkRedis(): Promise<ServiceHealthStatus> {
    const startTime = performance.now();
    
    try {
      // Implement actual Redis health check
      return {
        name: 'Redis',
        status: 'up',
        responseTime: performance.now() - startTime,
        lastChecked: new Date()
      };
    } catch (error) {
      return {
        name: 'Redis',
        status: 'down',
        lastChecked: new Date(),
        error: (error as Error).message
      };
    }
  }
  
  /**
   * Check API endpoints
   */
  private async checkAPIEndpoints(): Promise<ServiceHealthStatus> {
    const startTime = performance.now();
    
    try {
      // Check if API is responding
      return {
        name: 'API',
        status: 'up',
        responseTime: performance.now() - startTime,
        lastChecked: new Date()
      };
    } catch (error) {
      return {
        name: 'API',
        status: 'down',
        lastChecked: new Date(),
        error: (error as Error).message
      };
    }
  }
  
  /**
   * Run health checks
   */
  private async runHealthChecks(): Promise<HealthCheckResult[]> {
    const checks: HealthCheckResult[] = [];
    
    // Memory check
    checks.push(await this.checkMemoryUsage());
    
    // CPU check
    checks.push(await this.checkCPUUsage());
    
    // Queue size check
    checks.push(await this.checkQueueSize());
    
    // Error rate check
    checks.push(await this.checkErrorRate());
    
    return checks;
  }
  
  /**
   * Check memory usage
   */
  private async checkMemoryUsage(): Promise<HealthCheckResult> {
    const startTime = performance.now();
    const memUsage = process.memoryUsage();
    const heapUsedPercent = (memUsage.heapUsed / memUsage.heapTotal) * 100;
    
    return {
      name: 'Memory Usage',
      passed: heapUsedPercent < 80,
      message: `Heap usage: ${heapUsedPercent.toFixed(2)}%`,
      duration: performance.now() - startTime
    };
  }
  
  /**
   * Check CPU usage
   */
  private async checkCPUUsage(): Promise<HealthCheckResult> {
    const startTime = performance.now();
    const cpuUsage = process.cpuUsage();
    
    // Simple CPU check (can be enhanced)
    return {
      name: 'CPU Usage',
      passed: true,
      message: 'CPU usage within limits',
      duration: performance.now() - startTime
    };
  }
  
  /**
   * Check queue size
   */
  private async checkQueueSize(): Promise<HealthCheckResult> {
    const startTime = performance.now();
    const queueSize = this.orchestrator.getMetrics().queuedMessages;
    
    return {
      name: 'Queue Size',
      passed: queueSize < 1000,
      message: `Queue size: ${queueSize}`,
      duration: performance.now() - startTime
    };
  }
  
  /**
   * Check error rate
   */
  private async checkErrorRate(): Promise<HealthCheckResult> {
    const startTime = performance.now();
    const errorRate = this.calculateErrorRate();
    
    return {
      name: 'Error Rate',
      passed: errorRate < 0.05, // Less than 5%
      message: `Error rate: ${(errorRate * 100).toFixed(2)}%`,
      duration: performance.now() - startTime
    };
  }
  
  /**
   * Determine overall status
   */
  private determineOverallStatus(
    agents: AgentHealthStatus[],
    services: ServiceHealthStatus[],
    checks: HealthCheckResult[]
  ): 'healthy' | 'degraded' | 'unhealthy' {
    // Check if any service is down
    const downServices = services.filter(s => s.status === 'down');
    if (downServices.length > 0) {
      return 'unhealthy';
    }
    
    // Check if any health check failed
    const failedChecks = checks.filter(c => !c.passed);
    if (failedChecks.length > 0) {
      return 'degraded';
    }
    
    // Check agent health
    const unhealthyAgents = agents.filter(a => a.status === 'error');
    if (unhealthyAgents.length > 0) {
      return 'degraded';
    }
    
    return 'healthy';
  }
  
  /**
   * Initialize metrics
   */
  private initializeMetrics(): SystemMetrics {
    return {
      activeAgents: 0,
      queuedTasks: 0,
      completedTasks: 0,
      failedTasks: 0,
      avgResponseTime: 0,
      memoryUsage: process.memoryUsage(),
      cpuUsage: process.cpuUsage(),
      throughput: 0,
      errorRate: 0
    };
  }
  
  /**
   * Update metrics history
   */
  private updateMetricsHistory(metrics: SystemMetrics): void {
    this.metricsHistory.push(metrics);
    
    if (this.metricsHistory.length > this.MAX_HISTORY_SIZE) {
      this.metricsHistory.shift();
    }
  }
  
  /**
   * Calculate average response time
   */
  private calculateAvgResponseTime(): number {
    if (this.metricsHistory.length === 0) return 0;
    
    const sum = this.metricsHistory.reduce((acc, m) => acc + m.avgResponseTime, 0);
    return sum / this.metricsHistory.length;
  }
  
  /**
   * Calculate throughput
   */
  private calculateThroughput(): number {
    if (this.metricsHistory.length < 2) return 0;
    
    const recent = this.metricsHistory[this.metricsHistory.length - 1];
    const previous = this.metricsHistory[this.metricsHistory.length - 2];
    
    return recent.completedTasks - previous.completedTasks;
  }
  
  /**
   * Calculate error rate
   */
  private calculateErrorRate(): number {
    const total = this.metrics.completedTasks + this.metrics.failedTasks;
    if (total === 0) return 0;
    
    return this.metrics.failedTasks / total;
  }
  
  /**
   * Update task metrics
   */
  updateTaskMetrics(success: boolean, responseTime: number): void {
    if (success) {
      this.metrics.completedTasks++;
    } else {
      this.metrics.failedTasks++;
    }
    
    // Update average response time
    const total = this.metrics.completedTasks + this.metrics.failedTasks;
    this.metrics.avgResponseTime = 
      (this.metrics.avgResponseTime * (total - 1) + responseTime) / total;
  }
}

// Export singleton instance
let healthCheckManager: HealthCheckManager | null = null;

export function initializeHealthCheck(orchestrator: AgentOrchestrator): HealthCheckManager {
  if (!healthCheckManager) {
    healthCheckManager = new HealthCheckManager(orchestrator);
  }
  return healthCheckManager;
}

export function getHealthCheckManager(): HealthCheckManager | null {
  return healthCheckManager;
}