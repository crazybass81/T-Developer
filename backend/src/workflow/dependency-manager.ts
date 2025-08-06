export interface Dependency {
  taskId: string;
  dependsOn: string[];
  type: 'hard' | 'soft';
  condition?: string;
}

export interface TaskStatus {
  id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped';
  result?: any;
  error?: string;
  startTime?: number;
  endTime?: number;
}

export class DirectedGraph<T> {
  private nodes = new Set<T>();
  private edges = new Map<T, Set<T>>();

  addNode(node: T): void {
    this.nodes.add(node);
    if (!this.edges.has(node)) {
      this.edges.set(node, new Set());
    }
  }

  addEdge(from: T, to: T): void {
    this.addNode(from);
    this.addNode(to);
    this.edges.get(from)!.add(to);
  }

  hasCycle(): boolean {
    const visited = new Set<T>();
    const recursionStack = new Set<T>();

    const dfs = (node: T): boolean => {
      if (recursionStack.has(node)) return true;
      if (visited.has(node)) return false;

      visited.add(node);
      recursionStack.add(node);

      const neighbors = this.edges.get(node) || new Set();
      for (const neighbor of neighbors) {
        if (dfs(neighbor)) return true;
      }

      recursionStack.delete(node);
      return false;
    };

    for (const node of this.nodes) {
      if (dfs(node)) return true;
    }

    return false;
  }

  topologicalSort(): T[] {
    const inDegree = new Map<T, number>();
    const result: T[] = [];
    const queue: T[] = [];

    // 진입 차수 계산
    for (const node of this.nodes) {
      inDegree.set(node, 0);
    }

    for (const [from, neighbors] of this.edges) {
      for (const to of neighbors) {
        inDegree.set(to, (inDegree.get(to) || 0) + 1);
      }
    }

    // 진입 차수가 0인 노드를 큐에 추가
    for (const [node, degree] of inDegree) {
      if (degree === 0) {
        queue.push(node);
      }
    }

    // 위상 정렬
    while (queue.length > 0) {
      const current = queue.shift()!;
      result.push(current);

      const neighbors = this.edges.get(current) || new Set();
      for (const neighbor of neighbors) {
        const newDegree = inDegree.get(neighbor)! - 1;
        inDegree.set(neighbor, newDegree);
        
        if (newDegree === 0) {
          queue.push(neighbor);
        }
      }
    }

    return result;
  }

  getNodes(): Set<T> {
    return new Set(this.nodes);
  }

  getDependents(node: T): Set<T> {
    return new Set(this.edges.get(node) || []);
  }
}

export class DependencyManager {
  private dependencies = new Map<string, Dependency>();
  private graph = new DirectedGraph<string>();
  private taskStatuses = new Map<string, TaskStatus>();

  addDependency(dependency: Dependency): void {
    this.dependencies.set(dependency.taskId, dependency);

    // 그래프에 노드 추가
    this.graph.addNode(dependency.taskId);

    // 의존성 엣지 추가
    for (const dep of dependency.dependsOn) {
      this.graph.addEdge(dep, dependency.taskId);
    }

    // 순환 의존성 검사
    if (this.graph.hasCycle()) {
      throw new Error(
        `Circular dependency detected for task: ${dependency.taskId}`
      );
    }
  }

  async canExecute(taskId: string): Promise<boolean> {
    const dependency = this.dependencies.get(taskId);
    if (!dependency) return true;

    // 모든 의존성 확인
    for (const depId of dependency.dependsOn) {
      const depStatus = await this.getTaskStatus(depId);

      if (dependency.type === 'hard' && depStatus !== 'completed') {
        return false;
      }

      if (dependency.type === 'soft' && depStatus === 'failed') {
        // Soft 의존성은 실패해도 진행 가능
        console.warn(`Soft dependency ${depId} failed for ${taskId}`);
      }
    }

    // 조건부 의존성 평가
    if (dependency.condition) {
      return await this.evaluateCondition(dependency.condition);
    }

    return true;
  }

  getExecutionOrder(): string[] {
    // 위상 정렬로 실행 순서 결정
    return this.graph.topologicalSort();
  }

  updateTaskStatus(taskId: string, status: TaskStatus): void {
    this.taskStatuses.set(taskId, status);
  }

  private async getTaskStatus(taskId: string): Promise<string> {
    const status = this.taskStatuses.get(taskId);
    return status?.status || 'pending';
  }

  private async evaluateCondition(condition: string): Promise<boolean> {
    // 간단한 조건 평가 (실제로는 더 복잡한 표현식 파서 필요)
    try {
      // 안전한 조건 평가를 위한 기본 구현
      const allowedOperators = ['==', '!=', '>', '<', '>=', '<=', '&&', '||'];
      const hasUnsafeCode = /[(){}[\];]/.test(condition);
      
      if (hasUnsafeCode) {
        console.warn(`Unsafe condition detected: ${condition}`);
        return false;
      }

      // 기본적인 불린 값 처리
      if (condition === 'true') return true;
      if (condition === 'false') return false;

      // 더 복잡한 조건은 별도 파서 필요
      return true;
    } catch (error) {
      console.error(`Error evaluating condition: ${condition}`, error);
      return false;
    }
  }

  getDependencies(taskId: string): string[] {
    const dependency = this.dependencies.get(taskId);
    return dependency?.dependsOn || [];
  }

  getDependents(taskId: string): string[] {
    return Array.from(this.graph.getDependents(taskId));
  }

  getAllTasks(): string[] {
    return Array.from(this.graph.getNodes());
  }

  getReadyTasks(): string[] {
    const allTasks = this.getAllTasks();
    const readyTasks: string[] = [];

    for (const taskId of allTasks) {
      const currentStatus = this.taskStatuses.get(taskId)?.status || 'pending';
      
      if (currentStatus === 'pending') {
        const dependencies = this.getDependencies(taskId);
        const allDepsCompleted = dependencies.every(depId => {
          const depStatus = this.taskStatuses.get(depId)?.status;
          return depStatus === 'completed';
        });

        if (allDepsCompleted) {
          readyTasks.push(taskId);
        }
      }
    }

    return readyTasks;
  }

  validateDependencies(): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];

    // 순환 의존성 검사
    if (this.graph.hasCycle()) {
      errors.push('Circular dependency detected in task graph');
    }

    // 존재하지 않는 의존성 검사
    const allTasks = this.getAllTasks();
    for (const [taskId, dependency] of this.dependencies) {
      for (const depId of dependency.dependsOn) {
        if (!allTasks.includes(depId)) {
          errors.push(`Task ${taskId} depends on non-existent task: ${depId}`);
        }
      }
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  reset(): void {
    this.dependencies.clear();
    this.graph = new DirectedGraph<string>();
    this.taskStatuses.clear();
  }

  getStats() {
    const allTasks = this.getAllTasks();
    const statusCounts = {
      pending: 0,
      running: 0,
      completed: 0,
      failed: 0,
      skipped: 0
    };

    for (const taskId of allTasks) {
      const status = this.taskStatuses.get(taskId)?.status || 'pending';
      statusCounts[status]++;
    }

    return {
      totalTasks: allTasks.length,
      totalDependencies: this.dependencies.size,
      statusCounts,
      readyTasks: this.getReadyTasks().length
    };
  }
}