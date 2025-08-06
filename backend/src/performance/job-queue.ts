import Bull, { Queue, Job, JobOptions } from 'bull';
import Redis from 'ioredis';

export enum JobType {
  AGENT_EXECUTION = 'agent_execution',
  PROJECT_BUILD = 'project_build',
  COMPONENT_GENERATION = 'component_generation',
  EMAIL_NOTIFICATION = 'email_notification'
}

export enum JobPriority {
  CRITICAL = 1,
  HIGH = 2,
  NORMAL = 3,
  LOW = 4
}

interface BaseJobData {
  type: JobType;
  userId?: string;
  projectId?: string;
  timestamp: number;
}

export type JobData = BaseJobData & Record<string, any>;

export class QueueManager {
  private queues: Map<string, Queue> = new Map();
  private redis: Redis;
  
  constructor() {
    this.redis = new Redis({
      host: process.env.REDIS_HOST || 'localhost',
      port: parseInt(process.env.REDIS_PORT || '6379'),
      maxRetriesPerRequest: null
    });
  }
  
  async initialize(): Promise<void> {
    await this.createQueue('main', {
      defaultJobOptions: {
        removeOnComplete: 100,
        removeOnFail: 50,
        attempts: 3,
        backoff: { type: 'exponential', delay: 2000 }
      }
    });
    
    await this.createQueue('priority', {
      defaultJobOptions: {
        removeOnComplete: 50,
        attempts: 5
      }
    });
  }
  
  private async createQueue(name: string, options?: any): Promise<Queue> {
    const queue = new Bull(name, {
      redis: {
        host: process.env.REDIS_HOST || 'localhost',
        port: parseInt(process.env.REDIS_PORT || '6379')
      },
      ...options
    });
    
    this.queues.set(name, queue);
    this.setupEventListeners(queue, name);
    return queue;
  }
  
  async addJob(queueName: string, jobName: string, data: JobData, options?: JobOptions): Promise<Job> {
    const queue = this.queues.get(queueName);
    if (!queue) throw new Error(`Queue ${queueName} not found`);
    
    return queue.add(jobName, data, {
      ...options,
      priority: this.getJobPriority(data.type)
    });
  }
  
  async getJobStatus(queueName: string, jobId: string): Promise<any> {
    const queue = this.queues.get(queueName);
    if (!queue) throw new Error(`Queue ${queueName} not found`);
    
    const job = await queue.getJob(jobId);
    if (!job) return null;
    
    return {
      id: job.id,
      name: job.name,
      state: await job.getState(),
      progress: job.progress(),
      attemptsMade: job.attemptsMade
    };
  }
  
  async getQueueStats(queueName: string): Promise<any> {
    const queue = this.queues.get(queueName);
    if (!queue) throw new Error(`Queue ${queueName} not found`);
    
    const [waiting, active, completed, failed] = await Promise.all([
      queue.getWaitingCount(),
      queue.getActiveCount(),
      queue.getCompletedCount(),
      queue.getFailedCount()
    ]);
    
    return { name: queueName, counts: { waiting, active, completed, failed } };
  }
  
  private setupEventListeners(queue: Queue, name: string): void {
    queue.on('completed', (job) => {
      console.log(`Job ${job.id} completed in queue ${name}`);
    });
    
    queue.on('failed', (job, err) => {
      console.error(`Job ${job.id} failed in queue ${name}:`, err.message);
    });
  }
  
  private getJobPriority(jobType: JobType): number {
    const priorityMap: Record<JobType, JobPriority> = {
      [JobType.AGENT_EXECUTION]: JobPriority.HIGH,
      [JobType.PROJECT_BUILD]: JobPriority.HIGH,
      [JobType.COMPONENT_GENERATION]: JobPriority.NORMAL,
      [JobType.EMAIL_NOTIFICATION]: JobPriority.NORMAL
    };
    
    return priorityMap[jobType] || JobPriority.NORMAL;
  }
  
  async shutdown(): Promise<void> {
    for (const [name, queue] of this.queues) {
      await queue.close();
    }
    await this.redis.quit();
  }
}

export abstract class JobWorker {
  protected queue: Queue;
  
  constructor(queue: Queue) {
    this.queue = queue;
  }
  
  async start(): Promise<void> {
    this.queue.process(async (job: Job) => {
      await job.progress(0);
      const result = await this.process(job);
      await job.progress(100);
      return result;
    });
  }
  
  abstract process(job: Job): Promise<any>;
}