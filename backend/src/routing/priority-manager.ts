enum Priority {
  CRITICAL = 1,
  HIGH = 2,
  NORMAL = 3,
  LOW = 4
}

interface PriorityTask {
  id: string;
  priority: Priority;
  createdAt: number;
  data: any;
}

export class PriorityQueue {
  private queue: Array<[number, number, PriorityTask]> = [];
  private taskMap: Map<string, number> = new Map();
  
  addTask(task: PriorityTask): void {
    const priorityScore = this.calculatePriorityScore(task);
    
    // 힙에 추가 (우선순위, 타임스탬프, 태스크)
    this.queue.push([priorityScore, task.createdAt, task]);
    this.taskMap.set(task.id, priorityScore);
    
    // 힙 정렬 유지
    this.heapifyUp(this.queue.length - 1);
  }
  
  getNextTask(): PriorityTask | null {
    if (this.queue.length === 0) return null;
    
    // 최고 우선순위 태스크 추출
    const [, , task] = this.queue[0];
    
    // 힙에서 제거
    const lastItem = this.queue.pop()!;
    if (this.queue.length > 0) {
      this.queue[0] = lastItem;
      this.heapifyDown(0);
    }
    
    this.taskMap.delete(task.id);
    return task;
  }
  
  private calculatePriorityScore(task: PriorityTask): number {
    let baseScore = task.priority;
    
    // 대기 시간 가중치
    const waitTime = Date.now() - task.createdAt;
    const waitWeight = Math.min(waitTime / 300000, 1.0); // 5분 이상 대기 시 최대 가중치
    
    // SLA 가중치
    let slaWeight = 0;
    if (task.data.slaDeadline) {
      const timeToDeadline = task.data.slaDeadline - Date.now();
      if (timeToDeadline < 300000) { // 5분 이내
        slaWeight = 2.0;
      }
    }
    
    // 우선순위 타입별 추가 가중치
    let typeWeight = 0;
    if (task.data.type === 'security') typeWeight = 1.0;
    if (task.data.type === 'critical-bug') typeWeight = 1.5;
    
    return baseScore - (waitWeight + slaWeight + typeWeight);
  }
  
  private heapifyUp(index: number): void {
    if (index === 0) return;
    
    const parentIndex = Math.floor((index - 1) / 2);
    if (this.queue[index][0] < this.queue[parentIndex][0]) {
      [this.queue[index], this.queue[parentIndex]] = [this.queue[parentIndex], this.queue[index]];
      this.heapifyUp(parentIndex);
    }
  }
  
  private heapifyDown(index: number): void {
    const leftChild = 2 * index + 1;
    const rightChild = 2 * index + 2;
    let smallest = index;
    
    if (leftChild < this.queue.length && 
        this.queue[leftChild][0] < this.queue[smallest][0]) {
      smallest = leftChild;
    }
    
    if (rightChild < this.queue.length && 
        this.queue[rightChild][0] < this.queue[smallest][0]) {
      smallest = rightChild;
    }
    
    if (smallest !== index) {
      [this.queue[index], this.queue[smallest]] = [this.queue[smallest], this.queue[index]];
      this.heapifyDown(smallest);
    }
  }
  
  size(): number {
    return this.queue.length;
  }
  
  isEmpty(): boolean {
    return this.queue.length === 0;
  }
  
  // 우선순위 업데이트
  updatePriority(taskId: string, newPriority: Priority): boolean {
    // 기존 태스크 찾기 및 제거
    const taskIndex = this.queue.findIndex(([, , task]) => task.id === taskId);
    if (taskIndex === -1) return false;
    
    const [, timestamp, task] = this.queue[taskIndex];
    
    // 제거
    const lastItem = this.queue.pop()!;
    if (taskIndex < this.queue.length) {
      this.queue[taskIndex] = lastItem;
      this.heapifyDown(taskIndex);
    }
    
    // 새 우선순위로 다시 추가
    task.priority = newPriority;
    this.addTask(task);
    
    return true;
  }
}

export class PriorityManager {
  private queues: Map<string, PriorityQueue> = new Map();
  
  constructor() {
    // 에이전트별 우선순위 큐 초기화
    this.queues.set('code-agent', new PriorityQueue());
    this.queues.set('test-agent', new PriorityQueue());
    this.queues.set('design-agent', new PriorityQueue());
  }
  
  addTask(agentName: string, task: any, priority: Priority = Priority.NORMAL): void {
    const queue = this.queues.get(agentName);
    if (!queue) {
      throw new Error(`No queue found for agent: ${agentName}`);
    }
    
    const priorityTask: PriorityTask = {
      id: task.id || `task-${Date.now()}`,
      priority,
      createdAt: Date.now(),
      data: task
    };
    
    queue.addTask(priorityTask);
  }
  
  getNextTask(agentName: string): any | null {
    const queue = this.queues.get(agentName);
    if (!queue) return null;
    
    const priorityTask = queue.getNextTask();
    return priorityTask ? priorityTask.data : null;
  }
  
  getQueueStats(): Record<string, number> {
    const stats: Record<string, number> = {};
    
    for (const [agentName, queue] of this.queues) {
      stats[agentName] = queue.size();
    }
    
    return stats;
  }
  
  updateTaskPriority(agentName: string, taskId: string, newPriority: Priority): boolean {
    const queue = this.queues.get(agentName);
    if (!queue) return false;
    
    return queue.updatePriority(taskId, newPriority);
  }
}