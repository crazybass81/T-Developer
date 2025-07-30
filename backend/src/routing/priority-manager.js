const Priority = {
  CRITICAL: 1,
  HIGH: 2,
  NORMAL: 3,
  LOW: 4
};

class PriorityQueue {
  constructor() {
    this.queue = [];
    this.taskMap = new Map();
  }
  
  addTask(task) {
    const priorityScore = this.calculatePriorityScore(task);
    
    // 힙에 추가 (우선순위, 타임스탬프, 태스크)
    this.queue.push([priorityScore, task.createdAt, task]);
    this.taskMap.set(task.id, priorityScore);
    
    // 힙 정렬 유지
    this.heapifyUp(this.queue.length - 1);
  }
  
  getNextTask() {
    if (this.queue.length === 0) return null;
    
    // 최고 우선순위 태스크 추출
    const [, , task] = this.queue[0];
    
    // 힙에서 제거
    const lastItem = this.queue.pop();
    if (this.queue.length > 0) {
      this.queue[0] = lastItem;
      this.heapifyDown(0);
    }
    
    this.taskMap.delete(task.id);
    return task;
  }
  
  calculatePriorityScore(task) {
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
  
  heapifyUp(index) {
    if (index === 0) return;
    
    const parentIndex = Math.floor((index - 1) / 2);
    if (this.queue[index][0] < this.queue[parentIndex][0]) {
      [this.queue[index], this.queue[parentIndex]] = [this.queue[parentIndex], this.queue[index]];
      this.heapifyUp(parentIndex);
    }
  }
  
  heapifyDown(index) {
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
  
  size() {
    return this.queue.length;
  }
  
  isEmpty() {
    return this.queue.length === 0;
  }
  
  updatePriority(taskId, newPriority) {
    // 기존 태스크 찾기 및 제거
    const taskIndex = this.queue.findIndex(([, , task]) => task.id === taskId);
    if (taskIndex === -1) return false;
    
    const [, timestamp, task] = this.queue[taskIndex];
    
    // 제거
    const lastItem = this.queue.pop();
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

class PriorityManager {
  constructor() {
    this.queues = new Map();
    
    // 에이전트별 우선순위 큐 초기화
    this.queues.set('code-agent', new PriorityQueue());
    this.queues.set('test-agent', new PriorityQueue());
    this.queues.set('design-agent', new PriorityQueue());
  }
  
  addTask(agentName, task, priority = Priority.NORMAL) {
    const queue = this.queues.get(agentName);
    if (!queue) {
      throw new Error(`No queue found for agent: ${agentName}`);
    }
    
    const priorityTask = {
      id: task.id || `task-${Date.now()}`,
      priority,
      createdAt: Date.now(),
      data: task
    };
    
    queue.addTask(priorityTask);
  }
  
  getNextTask(agentName) {
    const queue = this.queues.get(agentName);
    if (!queue) return null;
    
    const priorityTask = queue.getNextTask();
    return priorityTask ? priorityTask.data : null;
  }
  
  getQueueStats() {
    const stats = {};
    
    for (const [agentName, queue] of this.queues) {
      stats[agentName] = queue.size();
    }
    
    return stats;
  }
  
  updateTaskPriority(agentName, taskId, newPriority) {
    const queue = this.queues.get(agentName);
    if (!queue) return false;
    
    return queue.updatePriority(taskId, newPriority);
  }
}

module.exports = { PriorityQueue, PriorityManager, Priority };