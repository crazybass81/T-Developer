import { EventEmitter } from 'events';
import { Logger } from 'winston';

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

// Supervisor Agent 구현
export class SupervisorAgent extends EventEmitter {
  private config: SquadConfig['supervisorConfig'];
  private logger: Logger;
  private workers: Map<string, WorkerAgent[]> = new Map();
  private taskQueue: TaskQueue;
  
  constructor(
    config: SquadConfig['supervisorConfig'],
    logger: Logger
  ) {
    super();
    this.config = config;
    this.logger = logger;
    this.taskQueue = new TaskQueue();
    
    this.initialize();
  }
  
  private initialize(): void {
    this.logger.info('Supervisor Agent initialized', {
      name: this.config.name,
      role: this.config.role,
      capabilities: this.config.capabilities
    });
  }
  
  // Worker 관리
  async addWorker(worker: WorkerAgent): Promise<void> {
    const type = worker.getType();
    
    if (!this.workers.has(type)) {
      this.workers.set(type, []);
    }
    
    this.workers.get(type)!.push(worker);
    
    this.logger.info('Worker added to squad', {
      supervisorName: this.config.name,
      workerType: type,
      workerId: worker.getId()
    });
    
    // Worker 이벤트 구독
    worker.on('taskCompleted', (result) => {
      this.handleWorkerTaskCompletion(worker, result);
    });
    
    worker.on('error', (error) => {
      this.handleWorkerError(worker, error);
    });
  }
  
  // 작업 분배
  async distributeTask(task: Task): Promise<void> {
    const workerType = this.selectWorkerType(task);
    const workers = this.workers.get(workerType);
    
    if (!workers || workers.length === 0) {
      throw new Error(`No workers available for type: ${workerType}`);
    }
    
    // 로드 밸런싱: 가장 idle한 worker 선택
    const selectedWorker = this.selectIdleWorker(workers);
    
    if (!selectedWorker) {
      // 모든 worker가 busy하면 큐에 추가
      await this.taskQueue.enqueue(task);
      return;
    }
    
    await selectedWorker.executeTask(task);
  }
  
  // Worker 선택 로직
  private selectWorkerType(task: Task): string {
    // 작업 타입과 capability 매칭
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
  
  // 이벤트 핸들러
  private handleWorkerTaskCompletion(
    worker: WorkerAgent,
    result: any
  ): void {
    this.logger.info('Worker task completed', {
      workerId: worker.getId(),
      result
    });
    
    this.emit('taskCompleted', {
      worker: worker.getId(),
      result
    });
    
    // 큐에서 다음 작업 할당
    this.assignNextTask(worker);
  }
  
  private handleWorkerError(
    worker: WorkerAgent,
    error: Error
  ): void {
    this.logger.error('Worker error', {
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
  
  // 상태 모니터링
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

// Worker Agent 기본 클래스
export abstract class WorkerAgent extends EventEmitter {
  protected id: string;
  protected type: string;
  protected status: 'idle' | 'busy' | 'error' = 'idle';
  protected capabilities: string[];
  protected logger: Logger;
  
  constructor(
    type: string,
    capabilities: string[],
    logger: Logger
  ) {
    super();
    this.id = `worker-${type}-${Date.now()}`;
    this.type = type;
    this.capabilities = capabilities;
    this.logger = logger;
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
      }, 5000); // 5초 후 복구
    }
  }
  
  protected abstract process(task: Task): Promise<any>;
}

// 작업 큐 구현
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

// 타입 정의
interface Task {
  id: string;
  type: string;
  capability: string;
  workerType?: string;
  payload: any;
  priority?: number;
  timeout?: number;
}