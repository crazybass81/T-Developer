// Workflow 모듈 인덱스
export { RecoveryManager } from './recovery-manager';

// 타입 정의
export interface WorkflowTask {
  id: string;
  type: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  dependencies: string[];
  retryCount: number;
  maxRetries: number;
  data?: any;
}

export interface WorkflowExecution {
  id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  tasks: Map<string, WorkflowTask>;
  startedAt?: Date;
  completedAt?: Date;
  error?: string;
}

export interface DependencyGraph {
  nodes: Set<string>;
  edges: Map<string, Set<string>>;
  
  addNode(nodeId: string): void;
  addEdge(from: string, to: string): void;
  hasCycle(): boolean;
  topologicalSort(): string[];
}

// 기본 구현체들
export class SimpleDependencyGraph implements DependencyGraph {
  nodes = new Set<string>();
  edges = new Map<string, Set<string>>();

  addNode(nodeId: string): void {
    this.nodes.add(nodeId);
    if (!this.edges.has(nodeId)) {
      this.edges.set(nodeId, new Set());
    }
  }

  addEdge(from: string, to: string): void {
    this.addNode(from);
    this.addNode(to);
    this.edges.get(from)!.add(to);
  }

  hasCycle(): boolean {
    const visited = new Set<string>();
    const recursionStack = new Set<string>();

    const hasCycleUtil = (node: string): boolean => {
      visited.add(node);
      recursionStack.add(node);

      const neighbors = this.edges.get(node) || new Set();
      for (const neighbor of neighbors) {
        if (!visited.has(neighbor)) {
          if (hasCycleUtil(neighbor)) {
            return true;
          }
        } else if (recursionStack.has(neighbor)) {
          return true;
        }
      }

      recursionStack.delete(node);
      return false;
    };

    for (const node of this.nodes) {
      if (!visited.has(node)) {
        if (hasCycleUtil(node)) {
          return true;
        }
      }
    }

    return false;
  }

  topologicalSort(): string[] {
    const inDegree = new Map<string, number>();
    const result: string[] = [];
    const queue: string[] = [];

    // 진입 차수 계산
    for (const node of this.nodes) {
      inDegree.set(node, 0);
    }

    for (const [from, neighbors] of this.edges) {
      for (const to of neighbors) {
        inDegree.set(to, (inDegree.get(to) || 0) + 1);
      }
    }

    // 진입 차수가 0인 노드들을 큐에 추가
    for (const [node, degree] of inDegree) {
      if (degree === 0) {
        queue.push(node);
      }
    }

    // 위상 정렬 수행
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
}

// 유틸리티 함수들
export function createWorkflowTask(
  id: string,
  type: string,
  dependencies: string[] = []
): WorkflowTask {
  return {
    id,
    type,
    status: 'pending',
    dependencies,
    retryCount: 0,
    maxRetries: 3
  };
}

export function createWorkflowExecution(id: string): WorkflowExecution {
  return {
    id,
    status: 'pending',
    tasks: new Map()
  };
}