export interface Dependency {
  taskId: string;
  dependsOn: string[];
  type: 'hard' | 'soft';
  condition?: string;
}

export interface TaskStatus {
  id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  result?: any;
  error?: string;
}

export class DependencyManager {
  private dependencies = new Map<string, Dependency>();
  private taskStatuses = new Map<string, TaskStatus>();
  private graph = new Map<string, Set<string>>();

  addDependency(dependency: Dependency): void {
    this.dependencies.set(dependency.taskId, dependency);
    
    // 그래프에 노드 추가
    if (!this.graph.has(dependency.taskId)) {
      this.graph.set(dependency.taskId, new Set());
    }
    
    // 의존성 엣지 추가
    for (const dep of dependency.dependsOn) {
      if (!this.graph.has(dep)) {
        this.graph.set(dep, new Set());
      }
      this.graph.get(dep)!.add(dependency.taskId);
    }
    
    // 순환 의존성 검사
    if (this.hasCycle()) {
      this.dependencies.delete(dependency.taskId);
      throw new Error(`Circular dependency detected for task: ${dependency.taskId}`);
    }
  }

  async canExecute(taskId: string): Promise<boolean> {
    const dependency = this.dependencies.get(taskId);
    if (!dependency) return true;
    
    // 모든 의존성 확인
    for (const depId of dependency.dependsOn) {
      const depStatus = this.getTaskStatus(depId);
      
      if (dependency.type === 'hard' && depStatus.status !== 'completed') {
        return false;
      }
      
      if (dependency.type === 'soft' && depStatus.status === 'failed') {
        console.warn(`Soft dependency ${depId} failed for ${taskId}`);
      }
    }
    
    // 조건부 의존성 평가
    if (dependency.condition) {
      return this.evaluateCondition(dependency.condition);
    }
    
    return true;
  }

  getExecutionOrder(): string[] {
    const visited = new Set<string>();
    const result: string[] = [];
    
    const visit = (taskId: string) => {
      if (visited.has(taskId)) return;
      
      visited.add(taskId);
      const dependency = this.dependencies.get(taskId);
      
      if (dependency) {
        for (const dep of dependency.dependsOn) {
          visit(dep);
        }
      }
      
      result.push(taskId);
    };
    
    for (const taskId of this.dependencies.keys()) {
      visit(taskId);
    }
    
    return result;
  }

  updateTaskStatus(taskId: string, status: TaskStatus): void {
    this.taskStatuses.set(taskId, status);
  }

  getTaskStatus(taskId: string): TaskStatus {
    return this.taskStatuses.get(taskId) || {
      id: taskId,
      status: 'pending'
    };
  }

  getDependents(taskId: string): string[] {
    return Array.from(this.graph.get(taskId) || []);
  }

  getReadyTasks(): string[] {
    const ready: string[] = [];
    
    for (const taskId of this.dependencies.keys()) {
      const status = this.getTaskStatus(taskId);
      if (status.status === 'pending') {
        const dependency = this.dependencies.get(taskId)!;
        const canRun = dependency.dependsOn.every(depId => {
          const depStatus = this.getTaskStatus(depId);
          return depStatus.status === 'completed';
        });
        
        if (canRun) {
          ready.push(taskId);
        }
      }
    }
    
    return ready;
  }

  private hasCycle(): boolean {
    const visited = new Set<string>();
    const recStack = new Set<string>();
    
    const hasCycleUtil = (taskId: string): boolean => {
      visited.add(taskId);
      recStack.add(taskId);
      
      const neighbors = this.graph.get(taskId) || new Set();
      for (const neighbor of neighbors) {
        if (!visited.has(neighbor)) {
          if (hasCycleUtil(neighbor)) return true;
        } else if (recStack.has(neighbor)) {
          return true;
        }
      }
      
      recStack.delete(taskId);
      return false;
    };
    
    for (const taskId of this.graph.keys()) {
      if (!visited.has(taskId)) {
        if (hasCycleUtil(taskId)) return true;
      }
    }
    
    return false;
  }

  private evaluateCondition(condition: string): boolean {
    // 간단한 조건 평가 (실제로는 더 복잡한 표현식 파서 필요)
    try {
      return eval(condition);
    } catch {
      return false;
    }
  }
}