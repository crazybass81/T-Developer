import { ParallelExecutor, Task, ExecutionResult } from './parallel-executor';
import { DependencyManager, Dependency, TaskStatus } from './dependency-manager';
import { StateSynchronizer, WorkflowState } from './state-synchronizer';
import { RecoveryManager } from './recovery-manager';
import { EventEmitter } from 'events';

export interface WorkflowDefinition {
  id: string;
  name: string;
  tasks: WorkflowTask[];
  dependencies: Dependency[];
}

export interface WorkflowTask extends Task {
  type: string;
  retryStrategy?: string;
}

export class WorkflowCoordinator extends EventEmitter {
  private parallelExecutor: ParallelExecutor;
  private dependencyManager: DependencyManager;
  private stateSynchronizer: StateSynchronizer;
  private recoveryManager: RecoveryManager;

  constructor() {
    super();
    this.parallelExecutor = new ParallelExecutor();
    this.dependencyManager = new DependencyManager();
    this.stateSynchronizer = new StateSynchronizer();
    this.recoveryManager = new RecoveryManager();

    this.setupEventHandlers();
  }

  async executeWorkflow(definition: WorkflowDefinition): Promise<WorkflowState> {
    const workflowId = definition.id;
    
    try {
      // 워크플로우 초기화
      await this.initializeWorkflow(definition);
      
      // 의존성 설정
      this.setupDependencies(definition.dependencies);
      
      // 워크플로우 실행
      const results = await this.executeWithRecovery(definition.tasks);
      
      // 최종 상태 업데이트
      await this.stateSynchronizer.syncState(workflowId, {
        status: 'completed',
        metadata: { completedAt: new Date().toISOString() }
      });
      
      return this.stateSynchronizer.getState(workflowId);
      
    } catch (error) {
      await this.stateSynchronizer.syncState(workflowId, {
        status: 'failed',
        metadata: { 
          error: error instanceof Error ? error.message : 'Unknown error',
          failedAt: new Date().toISOString()
        }
      });
      
      throw error;
    }
  }

  private async initializeWorkflow(definition: WorkflowDefinition): Promise<void> {
    await this.stateSynchronizer.syncState(definition.id, {
      workflowId: definition.id,
      status: 'running',
      tasks: new Map(),
      metadata: {
        name: definition.name,
        startedAt: new Date().toISOString(),
        totalTasks: definition.tasks.length
      }
    });
  }

  private setupDependencies(dependencies: Dependency[]): void {
    for (const dependency of dependencies) {
      this.dependencyManager.addDependency(dependency);
    }
  }

  private async executeWithRecovery(tasks: WorkflowTask[]): Promise<Map<string, ExecutionResult>> {
    const enhancedTasks: Task[] = tasks.map(task => ({
      ...task,
      execute: async () => {
        return await this.recoveryManager.executeRecovery(
          task.id,
          { action: 'retry' },
          async () => {
            // 실제 태스크 실행 시뮬레이션
            await this.delay(Math.random() * 1000 + 500);
            
            // 10% 확률로 실패 시뮬레이션
            if (Math.random() < 0.1) {
              throw new Error(`Task ${task.id} failed randomly`);
            }
            
            return {
              taskId: task.id,
              result: `Task ${task.id} completed`,
              timestamp: new Date().toISOString()
            };
          }
        );
      }
    }));

    return await this.parallelExecutor.executeParallel(enhancedTasks);
  }

  private setupEventHandlers(): void {
    // 병렬 실행기 이벤트
    this.parallelExecutor.on('taskStart', (taskId) => {
      this.stateSynchronizer.updateTaskState(taskId, taskId, {
        status: 'running',
        startedAt: new Date().toISOString()
      });
      this.emit('taskStarted', taskId);
    });

    this.parallelExecutor.on('taskComplete', (taskId, result) => {
      this.stateSynchronizer.updateTaskState(taskId, taskId, {
        status: 'completed',
        result,
        completedAt: new Date().toISOString()
      });
      this.emit('taskCompleted', taskId, result);
    });

    this.parallelExecutor.on('taskError', (taskId, error) => {
      this.stateSynchronizer.updateTaskState(taskId, taskId, {
        status: 'failed',
        error: error.message,
        failedAt: new Date().toISOString()
      });
      this.emit('taskFailed', taskId, error);
    });

    // 상태 동기화 이벤트
    this.stateSynchronizer.on('stateChanged', (event) => {
      this.emit('workflowStateChanged', event);
    });
  }

  // 워크플로우 상태 조회
  getWorkflowState(workflowId: string): WorkflowState {
    return this.stateSynchronizer.getState(workflowId);
  }

  // 실행 중인 태스크 대기
  async waitForTask(workflowId: string, taskId: string): Promise<any> {
    return await this.stateSynchronizer.waitForTaskCompletion(workflowId, taskId);
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}