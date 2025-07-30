// SubTask 1.20.4: CI/CD Orchestrator
import { PipelineManager, PipelineConfig } from '../pipeline/pipeline-manager';
import { DeploymentManager, DeploymentConfig } from '../deployment/deployment-manager';
import { PipelineMonitor, PipelineMetrics } from '../monitoring/pipeline-monitor';

export class CICDOrchestrator {
  private pipelineManager: PipelineManager;
  private deploymentManager: DeploymentManager;
  private monitor: PipelineMonitor;
  private workflows: Map<string, WorkflowConfig> = new Map();

  constructor() {
    this.pipelineManager = new PipelineManager();
    this.deploymentManager = new DeploymentManager();
    this.monitor = new PipelineMonitor();
    
    this.setupDefaultPipelines();
    this.setupMonitoring();
  }

  // Setup default pipelines
  private setupDefaultPipelines(): void {
    // Build pipeline
    this.pipelineManager.register({
      name: 'build',
      stages: [
        {
          name: 'install',
          commands: ['npm ci'],
          timeout: 300000,
          retries: 2
        },
        {
          name: 'lint',
          commands: ['npm run lint'],
          timeout: 60000,
          retries: 1
        },
        {
          name: 'test',
          commands: ['npm run test'],
          timeout: 300000,
          retries: 1
        },
        {
          name: 'build',
          commands: ['npm run build'],
          timeout: 300000,
          retries: 1
        }
      ],
      environment: {
        NODE_ENV: 'test',
        CI: 'true'
      },
      notifications: ['team@company.com']
    });

    // Deploy pipeline
    this.pipelineManager.register({
      name: 'deploy',
      stages: [
        {
          name: 'package',
          commands: ['npm run package'],
          timeout: 120000,
          retries: 1
        },
        {
          name: 'upload',
          commands: ['aws s3 cp dist/ s3://artifacts/ --recursive'],
          timeout: 300000,
          retries: 2
        }
      ],
      environment: {
        NODE_ENV: 'production'
      },
      notifications: ['ops@company.com']
    });
  }

  // Setup monitoring
  private setupMonitoring(): void {
    // Failure alerts
    this.monitor.addAlert({
      name: 'pipeline-failure',
      type: 'failure',
      threshold: 0,
      message: 'Pipeline execution failed',
      severity: 'high',
      notifications: ['team@company.com']
    });

    // Duration alerts
    this.monitor.addAlert({
      name: 'slow-pipeline',
      type: 'duration',
      threshold: 600000, // 10 minutes
      message: 'Pipeline execution is taking too long',
      severity: 'medium',
      notifications: ['team@company.com']
    });

    // Success rate alerts
    this.monitor.addAlert({
      name: 'low-success-rate',
      type: 'success-rate',
      threshold: 0.8,
      window: 60, // 1 hour
      message: 'Pipeline success rate is below 80%',
      severity: 'critical',
      notifications: ['team@company.com', 'ops@company.com']
    });
  }

  // Execute full workflow
  async executeWorkflow(workflowName: string, trigger: WorkflowTrigger): Promise<WorkflowResult> {
    const workflow = this.workflows.get(workflowName);
    if (!workflow) throw new Error(`Workflow ${workflowName} not found`);

    const workflowId = `workflow_${Date.now()}`;
    const startTime = Date.now();
    const results: StepResult[] = [];

    try {
      for (const step of workflow.steps) {
        const stepResult = await this.executeWorkflowStep(step, trigger);
        results.push(stepResult);

        if (!stepResult.success && !step.continueOnFailure) {
          throw new Error(`Workflow step ${step.name} failed`);
        }
      }

      return {
        workflowId,
        success: true,
        duration: Date.now() - startTime,
        steps: results,
        trigger
      };

    } catch (error: any) {
      return {
        workflowId,
        success: false,
        duration: Date.now() - startTime,
        steps: results,
        trigger,
        error: error.message
      };
    }
  }

  // Execute workflow step
  private async executeWorkflowStep(
    step: WorkflowStep, 
    trigger: WorkflowTrigger
  ): Promise<StepResult> {
    const startTime = Date.now();

    try {
      switch (step.type) {
        case 'pipeline':
          const pipelineResult = await this.pipelineManager.execute(step.pipeline!);
          
          // Record metrics
          this.monitor.recordExecution({
            pipelineName: step.pipeline!,
            executionId: pipelineResult.executionId,
            duration: pipelineResult.duration,
            success: pipelineResult.success,
            timestamp: new Date(),
            stages: pipelineResult.stages.map(s => ({
              name: s.name,
              duration: s.duration,
              success: s.success,
              retries: s.attempt
            }))
          });

          return {
            name: step.name,
            type: 'pipeline',
            success: pipelineResult.success,
            duration: Date.now() - startTime,
            output: pipelineResult
          };

        case 'deployment':
          const deployResult = await this.deploymentManager.deploy(
            step.deployment!,
            trigger.artifact || 'latest'
          );

          return {
            name: step.name,
            type: 'deployment',
            success: deployResult.success,
            duration: Date.now() - startTime,
            output: deployResult
          };

        case 'approval':
          const approved = await this.requestApproval(step.approval!);
          
          return {
            name: step.name,
            type: 'approval',
            success: approved,
            duration: Date.now() - startTime,
            output: { approved }
          };

        default:
          throw new Error(`Unknown step type: ${step.type}`);
      }

    } catch (error: any) {
      return {
        name: step.name,
        type: step.type,
        success: false,
        duration: Date.now() - startTime,
        error: error.message
      };
    }
  }

  // Register workflow
  registerWorkflow(config: WorkflowConfig): void {
    this.workflows.set(config.name, config);
  }

  // Get default CI/CD workflow
  getDefaultWorkflow(): WorkflowConfig {
    return {
      name: 'ci-cd',
      description: 'Standard CI/CD workflow',
      triggers: ['push', 'pull-request'],
      steps: [
        {
          name: 'build-and-test',
          type: 'pipeline',
          pipeline: 'build',
          continueOnFailure: false
        },
        {
          name: 'deploy-staging',
          type: 'deployment',
          deployment: {
            name: 'staging-deploy',
            environment: 'staging',
            strategy: 'rolling',
            healthCheck: {
              endpoint: '/health',
              timeout: 30000,
              retries: 3,
              interval: 5000
            },
            rollback: {
              enabled: true,
              threshold: 0.95,
              autoRollback: true
            }
          },
          continueOnFailure: false
        },
        {
          name: 'approval',
          type: 'approval',
          approval: {
            required: true,
            approvers: ['team-lead@company.com'],
            timeout: 86400000 // 24 hours
          },
          continueOnFailure: false
        },
        {
          name: 'deploy-production',
          type: 'deployment',
          deployment: {
            name: 'prod-deploy',
            environment: 'prod',
            strategy: 'blue-green',
            healthCheck: {
              endpoint: '/health',
              timeout: 30000,
              retries: 5,
              interval: 10000
            },
            rollback: {
              enabled: true,
              threshold: 0.99,
              autoRollback: true
            }
          },
          continueOnFailure: false
        }
      ]
    };
  }

  // Mock approval request
  private async requestApproval(config: ApprovalConfig): Promise<boolean> {
    console.log(`📋 Approval requested from: ${config.approvers.join(', ')}`);
    
    // Mock approval (auto-approve for demo)
    await new Promise(resolve => setTimeout(resolve, 1000));
    return true;
  }

  // Get workflow status
  getWorkflowStatus(): WorkflowStatus {
    const stats = this.monitor.getStats();
    const health = this.monitor.getHealth();

    return {
      health: health.status,
      totalWorkflows: this.workflows.size,
      recentExecutions: stats.totalExecutions,
      successRate: stats.successRate,
      averageDuration: stats.averageDuration
    };
  }
}

export interface WorkflowConfig {
  name: string;
  description: string;
  triggers: string[];
  steps: WorkflowStep[];
}

export interface WorkflowStep {
  name: string;
  type: 'pipeline' | 'deployment' | 'approval';
  pipeline?: string;
  deployment?: DeploymentConfig;
  approval?: ApprovalConfig;
  continueOnFailure: boolean;
}

export interface ApprovalConfig {
  required: boolean;
  approvers: string[];
  timeout: number;
}

export interface WorkflowTrigger {
  type: string;
  source: string;
  artifact?: string;
  metadata?: Record<string, any>;
}

export interface WorkflowResult {
  workflowId: string;
  success: boolean;
  duration: number;
  steps: StepResult[];
  trigger: WorkflowTrigger;
  error?: string;
}

export interface StepResult {
  name: string;
  type: string;
  success: boolean;
  duration: number;
  output?: any;
  error?: string;
}

export interface WorkflowStatus {
  health: string;
  totalWorkflows: number;
  recentExecutions: number;
  successRate: number;
  averageDuration: number;
}