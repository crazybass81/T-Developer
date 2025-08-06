export enum Priority {
  CRITICAL = 1,
  HIGH = 2,
  NORMAL = 3,
  LOW = 4
}

export interface Task {
  id: string;
  type: string;
  createdAt: number;
  slaDeadline?: number;
  priority: Priority;
  data: any;
}

export class PriorityQueue {
  private queue: Array<{ score: number; timestamp: number; task: Task }> = [];
  private taskMap: Map<string, number> = new Map();

  addTask(task: Task, priority: Priority): void {
    const priorityScore = this.calculatePriorityScore(task, priority);
    
    const item = {
      score: priorityScore,
      timestamp: Date.now(),
      task: { ...task, priority }
    };

    this.queue.push(item);
    this.queue.sort((a, b) => a.score - b.score);
    this.taskMap.set(task.id, priorityScore);
  }

  getNextTask(): Task | null {
    while (this.queue.length > 0) {
      const item = this.queue.shift()!;
      if (this.taskMap.has(item.task.id)) {
        this.taskMap.delete(item.task.id);
        return item.task;
      }
    }
    return null;
  }

  removeTask(taskId: string): boolean {
    if (!this.taskMap.has(taskId)) return false;
    
    this.taskMap.delete(taskId);
    this.queue = this.queue.filter(item => item.task.id !== taskId);
    return true;
  }

  private calculatePriorityScore(task: Task, priority: Priority): number {
    const baseScore = priority;
    const now = Date.now();
    
    // 대기 시간 가중치 (5분 이상 대기 시 최대 가중치)
    const waitTime = (now - task.createdAt) / 1000;
    const waitWeight = Math.min(waitTime / 300, 1.0);
    
    // SLA 가중치
    let slaWeight = 0;
    if (task.slaDeadline) {
      const timeToDeadline = (task.slaDeadline - now) / 1000;
      if (timeToDeadline < 300) { // 5분 이내
        slaWeight = 2.0;
      }
    }
    
    return baseScore - (waitWeight + slaWeight);
  }

  getQueueStatus() {
    const priorityCounts = { CRITICAL: 0, HIGH: 0, NORMAL: 0, LOW: 0 };
    
    this.queue.forEach(item => {
      const priority = Priority[item.task.priority] as keyof typeof priorityCounts;
      priorityCounts[priority]++;
    });

    return {
      totalTasks: this.queue.length,
      priorityCounts,
      oldestTask: this.queue.length > 0 ? this.queue[0].task.createdAt : null
    };
  }
}

export class TaskScheduler {
  private priorityQueue = new PriorityQueue();
  private processing = false;
  private processingCallback?: (task: Task) => Promise<void>;

  constructor(processingCallback?: (task: Task) => Promise<void>) {
    this.processingCallback = processingCallback;
  }

  scheduleTask(task: Task, priority: Priority = Priority.NORMAL): void {
    this.priorityQueue.addTask(task, priority);
    
    if (!this.processing) {
      this.startProcessing();
    }
  }

  private async startProcessing(): Promise<void> {
    this.processing = true;

    while (true) {
      const task = this.priorityQueue.getNextTask();
      if (!task) {
        this.processing = false;
        break;
      }

      try {
        if (this.processingCallback) {
          await this.processingCallback(task);
        }
      } catch (error) {
        console.error(`Task ${task.id} processing failed:`, error);
      }
    }
  }

  getSchedulerStatus() {
    return {
      isProcessing: this.processing,
      queueStatus: this.priorityQueue.getQueueStatus()
    };
  }

  cancelTask(taskId: string): boolean {
    return this.priorityQueue.removeTask(taskId);
  }
}