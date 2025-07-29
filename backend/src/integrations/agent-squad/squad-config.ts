import { EventEmitter } from 'events';

export interface SquadConfig {
  supervisorConfig: {
    name: string;
    role: 'orchestrator' | 'coordinator' | 'monitor';
    capabilities: string[];
  };
  workers: Array<{
    name: string;
    type: string;
    count: number;
    capabilities: string[];
  }>;
  communication: {
    protocol: 'redis' | 'sqs' | 'eventbridge';
    endpoint: string;
  };
}

export interface Task {
  id: string;
  type: string;
  capability: string;
  workerType?: string;
  payload: any;
  priority?: number;
  timeout?: number;
}

export class SupervisorAgent extends EventEmitter {
  private config: SquadConfig['supervisorConfig'];
  private workers: Map<string, WorkerAgent[]> = new Map();
  private taskQueue: TaskQueue;
  
  constructor(config: SquadConfig['supervisorConfig']) {
    super();
    this.config = config;
    this.taskQueue = new TaskQueue();
    
    this.initialize();
  }
  
  private initialize(): void {
    console.log('Supervisor Agent initialized', {
      name: this.config.name,
      role: this.config.role,
      capabilities: this.config.capabilities
    });
  }
  
  async addWorker(worker: WorkerAgent): Promise<void> {
    const type = worker.getType();
    
    if (!this.workers.has(type)) {
      this.workers.set(type, []);
    }
    
    this.workers.get(type)!.push(worker);
    
    console.log('Worker added to squad', {
      supervisorName: this.config.name,
      workerType: type,
      workerId: worker.getId()
    });
    
    worker.on('taskCompleted', (result) => {
      this.handleWorkerTaskCompletion(worker, result);
    });
    
    worker.on('error', (error) => {
      this.handleWorkerError(worker, error);
    });
  }
  
  async distributeTask(task: Task): Promise<void> {
    const workerType = this.selectWorkerType(task);
    const workers = this.workers.get(workerType);
    
    if (!workers || workers.length === 0) {
      throw new Error(`No workers available for type: ${workerType}`);
    }
    
    const selectedWorker = this.selectIdleWorker(workers);
    
    if (!selectedWorker) {
      await this.taskQueue.enqueue(task);
      return;
    }
    
    await selectedWorker.executeTask(task);
  }
  
  private selectWorkerType(task: Task): string {
    for (const [type, workers] of this.workers) {
      if (workers.some(w => w.canHandle(task))) {
        return type;
      }
    }
    
    throw new Error(`No suitable worker for task: ${task.type}`);
  }
  
  private selectIdleWorker(workers: WorkerAgent[]): WorkerAgent | null {
    return workers.find(w => w.getStatus() === 'idle') || null;
  }
  
  private handleWorkerTaskCompletion(worker: WorkerAgent, result: any): void {
    console.log('Worker task completed', {
      workerId: worker.getId(),
      result
    });
    
    this.emit('taskCompleted', {
      worker: worker.getId(),
      result
    });
    
    this.assignNextTask(worker);
  }
  
  private handleWorkerError(worker: WorkerAgent, error: Error): void {
    console.error('Worker error', {
      workerId: worker.getId(),
      error
    });
    
    this.emit('workerError', {
      worker: worker.getId(),
      error
    });
  }
  
  private async assignNextTask(worker: WorkerAgent): Promise<void> {
    const nextTask = await this.taskQueue.dequeue(worker.getType());
    
    if (nextTask) {
      await worker.executeTask(nextTask);
    }
  }
  
  getSquadStatus(): any {
    const status = {
      supervisor: {
        name: this.config.name,
        role: this.config.role
      },
      workers: {} as any,
      queueSize: this.taskQueue.size()
    };
    
    for (const [type, workers] of this.workers) {
      status.workers[type] = {
        count: workers.length,
        idle: workers.filter(w => w.getStatus() === 'idle').length,
        busy: workers.filter(w => w.getStatus() === 'busy').length
      };
    }
    
    return status;
  }
}

export abstract class WorkerAgent extends EventEmitter {
  protected id: string;
  protected type: string;
  protected status: 'idle' | 'busy' | 'error' = 'idle';
  protected capabilities: string[];
  
  constructor(type: string, capabilities: string[]) {
    super();
    this.id = `worker-${type}-${Date.now()}`;
    this.type = type;
    this.capabilities = capabilities;
  }
  
  getId(): string {
    return this.id;
  }
  
  getType(): string {
    return this.type;
  }
  
  getStatus(): string {
    return this.status;
  }
  
  canHandle(task: Task): boolean {
    return this.capabilities.includes(task.capability);
  }
  
  async executeTask(task: Task): Promise<void> {
    this.status = 'busy';
    
    try {
      const result = await this.process(task);
      
      this.emit('taskCompleted', result);
      this.status = 'idle';
      
    } catch (error) {
      this.status = 'error';
      this.emit('error', error);
      
      setTimeout(() => {
        this.status = 'idle';
      }, 5000);
    }
  }
  
  protected abstract process(task: Task): Promise<any>;
}

class TaskQueue {
  private queues: Map<string, Task[]> = new Map();
  
  async enqueue(task: Task): Promise<void> {
    const type = task.workerType || 'default';
    
    if (!this.queues.has(type)) {
      this.queues.set(type, []);
    }
    
    this.queues.get(type)!.push(task);
  }
  
  async dequeue(type: string): Promise<Task | null> {
    const queue = this.queues.get(type);
    
    if (!queue || queue.length === 0) {
      return null;
    }
    
    return queue.shift() || null;
  }
  
  size(): number {
    let total = 0;
    for (const queue of this.queues.values()) {
      total += queue.length;
    }
    return total;
  }
}