export interface Task {
  id: string;
  type: string;
  payload: any;
  dependencies?: string[];
  timeout?: number;
  retryCount?: number;
}

export interface TaskResult {
  taskId: string;
  status: 'completed' | 'failed' | 'timeout';
  result?: any;
  error?: string;
  executionTime: number;
  startTime: number;
  endTime: number;
}

export interface ExecutionGroup {
  level: number;
  tasks: Task[];
  canRunInParallel: boolean;
}

export class ParallelExecutor {
  private maxWorkers: number;
  private semaphore: any;
  private activeTaskCount = 0;
  private taskResults = new Map<string, TaskResult>();

  constructor(maxWorkers: number = 50) {
    this.maxWorkers = maxWorkers;
    this.semaphore = this.createSemaphore(maxWorkers);
  }

  private createSemaphore(limit: number) {
    let count = 0;
    const waiting: (() => void)[] = [];

    return {
      async acquire(): Promise<void> {
        return new Promise<void>((resolve) => {
          if (count < limit) {
            count++;
            resolve();
          } else {
            waiting.push(resolve);
          }
        });
      },

      release(): void {
        count--;
        if (waiting.length > 0) {
          const next = waiting.shift()!;
          count++;
          next();
        }
      }
    };
  }

  async executeParallel(tasks: Task[]): Promise<TaskResult[]> {
    // 의존성 그래프 생성 및 실행 그룹 생성
    const executionGroups = this.createExecutionGroups(tasks);
    const results: TaskResult[] = [];

    // 각 그룹을 순차적으로 실행 (그룹 내에서는 병렬)
    for (const group of executionGroups) {
      const groupResults = await this.executeGroup(group);
      results.push(...groupResults);

      // 실패한 태스크가 있으면 의존성 체크
      const failedTasks = groupResults.filter(r => r.status === 'failed');
      if (failedTasks.length > 0) {
        await this.handleGroupFailures(failedTasks, tasks);
      }
    }

    return results;
  }

  private createExecutionGroups(tasks: Task[]): ExecutionGroup[] {
    const taskMap = new Map(tasks.map(t => [t.id, t]));
    const inDegree = new Map<string, number>();
    const dependents = new Map<string, string[]>();

    // 의존성 그래프 구성
    for (const task of tasks) {
      inDegree.set(task.id, 0);
      dependents.set(task.id, []);
    }

    for (const task of tasks) {
      if (task.dependencies) {
        inDegree.set(task.id, task.dependencies.length);
        
        for (const depId of task.dependencies) {
          if (!dependents.has(depId)) {
            dependents.set(depId, []);
          }
          dependents.get(depId)!.push(task.id);
        }
      }
    }

    // 위상 정렬로 실행 그룹 생성
    const groups: ExecutionGroup[] = [];
    const processed = new Set<string>();
    let level = 0;

    while (processed.size < tasks.length) {
      const currentLevel: Task[] = [];

      // 현재 레벨에서 실행 가능한 태스크 찾기
      for (const task of tasks) {
        if (!processed.has(task.id) && (inDegree.get(task.id) || 0) === 0) {
          currentLevel.push(task);
        }
      }

      if (currentLevel.length === 0) {
        throw new Error('Circular dependency detected or invalid task graph');
      }

      // 현재 레벨 태스크들을 처리됨으로 표시
      for (const task of currentLevel) {
        processed.add(task.id);
        
        // 의존성 업데이트
        const deps = dependents.get(task.id) || [];
        for (const depId of deps) {
          const currentInDegree = inDegree.get(depId) || 0;
          inDegree.set(depId, currentInDegree - 1);
        }
      }

      groups.push({
        level,
        tasks: currentLevel,
        canRunInParallel: currentLevel.length > 1
      });

      level++;
    }

    return groups;
  }

  private async executeGroup(group: ExecutionGroup): Promise<TaskResult[]> {
    if (group.canRunInParallel) {
      // 병렬 실행
      const promises = group.tasks.map(task => this.executeSingleTask(task));
      return await Promise.all(promises);
    } else {
      // 순차 실행
      const results: TaskResult[] = [];
      for (const task of group.tasks) {
        const result = await this.executeSingleTask(task);
        results.push(result);
      }
      return results;
    }
  }

  private async executeSingleTask(task: Task): Promise<TaskResult> {
    await this.semaphore.acquire();
    this.activeTaskCount++;

    const startTime = Date.now();
    let result: TaskResult;

    try {
      // 태스크 실행 시뮬레이션
      const executionResult = await this.runTaskWithTimeout(task);
      
      result = {
        taskId: task.id,
        status: 'completed',
        result: executionResult,
        executionTime: Date.now() - startTime,
        startTime,
        endTime: Date.now()
      };

    } catch (error: any) {
      result = {
        taskId: task.id,
        status: error.name === 'TimeoutError' ? 'timeout' : 'failed',
        error: error.message,
        executionTime: Date.now() - startTime,
        startTime,
        endTime: Date.now()
      };
    } finally {
      this.activeTaskCount--;
      this.semaphore.release();
    }

    this.taskResults.set(task.id, result);
    return result;
  }

  private async runTaskWithTimeout(task: Task): Promise<any> {
    const timeout = task.timeout || 30000; // 기본 30초

    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        const error = new Error(`Task ${task.id} timed out after ${timeout}ms`);
        error.name = 'TimeoutError';
        reject(error);
      }, timeout);

      // 실제 태스크 실행 시뮬레이션
      this.simulateTaskExecution(task)
        .then(result => {
          clearTimeout(timer);
          resolve(result);
        })
        .catch(error => {
          clearTimeout(timer);
          reject(error);
        });
    });
  }

  private async simulateTaskExecution(task: Task): Promise<any> {
    // 태스크 타입별 실행 시뮬레이션
    const executionTime = Math.random() * 1000 + 100; // 100-1100ms
    
    await new Promise(resolve => setTimeout(resolve, executionTime));

    // 10% 확률로 실패 시뮬레이션
    if (Math.random() < 0.1) {
      throw new Error(`Task ${task.id} failed during execution`);
    }

    return {
      taskId: task.id,
      type: task.type,
      processedAt: new Date().toISOString(),
      payload: task.payload,
      simulatedResult: `Result for ${task.id}`
    };
  }

  private async handleGroupFailures(failedTasks: TaskResult[], allTasks: Task[]): Promise<void> {
    // 실패한 태스크의 의존성을 가진 태스크들을 찾아서 스킵 처리
    const failedTaskIds = new Set(failedTasks.map(t => t.taskId));
    
    for (const task of allTasks) {
      if (task.dependencies) {
        const hasFailedDependency = task.dependencies.some(depId => failedTaskIds.has(depId));
        if (hasFailedDependency) {
          // 의존성 실패로 인한 스킵 처리
          console.warn(`Task ${task.id} skipped due to failed dependencies`);
        }
      }
    }
  }

  // 통계 및 모니터링
  getExecutionStats() {
    const results = Array.from(this.taskResults.values());
    const completed = results.filter(r => r.status === 'completed').length;
    const failed = results.filter(r => r.status === 'failed').length;
    const timeout = results.filter(r => r.status === 'timeout').length;
    
    const executionTimes = results.map(r => r.executionTime);
    const avgExecutionTime = executionTimes.length > 0 
      ? executionTimes.reduce((a, b) => a + b, 0) / executionTimes.length 
      : 0;

    return {
      totalTasks: results.length,
      completed,
      failed,
      timeout,
      successRate: results.length > 0 ? completed / results.length : 0,
      averageExecutionTime: Math.round(avgExecutionTime),
      activeTaskCount: this.activeTaskCount,
      maxWorkers: this.maxWorkers
    };
  }

  // 실행 중인 태스크 정보
  getActiveTasks(): string[] {
    return Array.from(this.taskResults.entries())
      .filter(([_, result]) => !result.endTime)
      .map(([taskId, _]) => taskId);
  }

  // 태스크 결과 조회
  getTaskResult(taskId: string): TaskResult | undefined {
    return this.taskResults.get(taskId);
  }

  // 모든 결과 초기화
  reset(): void {
    this.taskResults.clear();
    this.activeTaskCount = 0;
  }
}