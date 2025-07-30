import { EventEmitter } from 'events';

export interface Task {
  id: string;
  name: string;
  execute: () => Promise<any>;
  dependencies: string[];
  timeout?: number;
}

export interface ExecutionResult {
  taskId: string;
  success: boolean;
  result?: any;
  error?: string;
  duration: number;
}

export class ParallelExecutor extends EventEmitter {
  private maxWorkers: number;
  private activeWorkers = 0;
  private taskQueue: Task[] = [];
  private results = new Map<string, ExecutionResult>();

  constructor(maxWorkers = 10) {
    super();
    this.maxWorkers = maxWorkers;
  }

  async executeParallel(tasks: Task[]): Promise<Map<string, ExecutionResult>> {
    // 의존성 그래프 생성
    const dependencyGraph = this.buildDependencyGraph(tasks);
    
    // 실행 순서 결정
    const executionOrder = this.topologicalSort(dependencyGraph);
    
    // 병렬 실행 그룹 생성
    const parallelGroups = this.createParallelGroups(executionOrder, dependencyGraph);
    
    // 그룹별 순차 실행
    for (const group of parallelGroups) {
      await this.executeGroup(group);
    }
    
    return this.results;
  }

  private buildDependencyGraph(tasks: Task[]): Map<string, string[]> {
    const graph = new Map<string, string[]>();
    
    for (const task of tasks) {
      graph.set(task.id, task.dependencies);
    }
    
    return graph;
  }

  private topologicalSort(graph: Map<string, string[]>): string[] {
    const visited = new Set<string>();
    const result: string[] = [];
    
    const visit = (nodeId: string) => {
      if (visited.has(nodeId)) return;
      
      visited.add(nodeId);
      const dependencies = graph.get(nodeId) || [];
      
      for (const dep of dependencies) {
        visit(dep);
      }
      
      result.push(nodeId);
    };
    
    for (const nodeId of graph.keys()) {
      visit(nodeId);
    }
    
    return result;
  }

  private createParallelGroups(order: string[], graph: Map<string, string[]>): string[][] {
    const groups: string[][] = [];
    const processed = new Set<string>();
    
    while (processed.size < order.length) {
      const currentGroup: string[] = [];
      
      for (const taskId of order) {
        if (processed.has(taskId)) continue;
        
        const dependencies = graph.get(taskId) || [];
        const canExecute = dependencies.every(dep => processed.has(dep));
        
        if (canExecute) {
          currentGroup.push(taskId);
        }
      }
      
      if (currentGroup.length === 0) {
        throw new Error('Circular dependency detected');
      }
      
      groups.push(currentGroup);
      currentGroup.forEach(id => processed.add(id));
    }
    
    return groups;
  }

  private async executeGroup(group: string[]): Promise<void> {
    const promises = group.map(taskId => this.executeTask(taskId));
    await Promise.all(promises);
  }

  private async executeTask(taskId: string): Promise<void> {
    const startTime = Date.now();
    
    try {
      // 워커 슬롯 대기
      await this.acquireWorker();
      
      this.emit('taskStart', taskId);
      
      // 태스크 실행 (실제로는 더미 실행)
      const result = await this.simulateTaskExecution(taskId);
      
      this.results.set(taskId, {
        taskId,
        success: true,
        result,
        duration: Date.now() - startTime
      });
      
      this.emit('taskComplete', taskId, result);
      
    } catch (error) {
      this.results.set(taskId, {
        taskId,
        success: false,
        error: error instanceof Error ? error.message : String(error),
        duration: Date.now() - startTime
      });
      
      this.emit('taskError', taskId, error instanceof Error ? error : new Error(String(error)));
    } finally {
      this.releaseWorker();
    }
  }

  private async acquireWorker(): Promise<void> {
    while (this.activeWorkers >= this.maxWorkers) {
      await new Promise(resolve => setTimeout(resolve, 10));
    }
    this.activeWorkers++;
  }

  private releaseWorker(): void {
    this.activeWorkers--;
  }

  private async simulateTaskExecution(taskId: string): Promise<any> {
    // 실제 태스크 실행 시뮬레이션
    const delay = Math.random() * 1000 + 500; // 500-1500ms
    await new Promise(resolve => setTimeout(resolve, delay));
    
    return {
      taskId,
      executedAt: new Date().toISOString(),
      result: `Task ${taskId} completed successfully`
    };
  }
}