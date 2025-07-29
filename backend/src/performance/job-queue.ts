import Bull, { Queue, Job, JobOptions, QueueScheduler } from 'bull';
import Redis from 'ioredis';

export enum JobType {
  AGENT_EXECUTION = 'agent_execution',
  PROJECT_BUILD = 'project_build',
  COMPONENT_GENERATION = 'component_generation',
  EMAIL_NOTIFICATION = 'email_notification',
  REPORT_GENERATION = 'report_generation',
  CACHE_WARMING = 'cache_warming',
  DATA_EXPORT = 'data_export',
  CLEANUP = 'cleanup'
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

interface AgentExecutionJob extends BaseJobData {
  type: JobType.AGENT_EXECUTION;
  agentName: string;
  input: any;
}

interface ProjectBuildJob extends BaseJobData {
  type: JobType.PROJECT_BUILD;
  projectConfig: any;
}

export type JobData = AgentExecutionJob | ProjectBuildJob;

export class QueueManager {
  private queues: Map<string, Queue> = new Map();
  private schedulers: Map<string, QueueScheduler> = new Map();
  private redisConnection: Redis;
  
  constructor() {
    this.redisConnection = new Redis({
      host: process.env.REDIS_HOST || 'localhost',
      port: parseInt(process.env.REDIS_PORT || '6379'),
      password: process.env.REDIS_PASSWORD,
      maxRetriesPerRequest: null
    });
  }
  
  async initialize(): Promise<void> {
    await this.createQueue('main', {
      defaultJobOptions: {
        removeOnComplete: 100,
        removeOnFail: 1000,
        attempts: 3,
        backoff: { type: 'exponential', delay: 2000 }
      }
    });
    
    await this.createQueue('priority', {
      defaultJobOptions: {
        removeOnComplete: 50,
        removeOnFail: 500,
        attempts: 5
      }
    });
    
    await this.createQueue('batch', {
      defaultJobOptions: {
        removeOnComplete: true,
        removeOnFail: false,
        attempts: 1
      }
    });
    
    console.log('Job queues initialized');
  }
  
  private async createQueue(name: string, options?: any): Promise<Queue> {
    const queue = new Bull(name, {
      redis: {
        host: process.env.REDIS_HOST || 'localhost',
        port: parseInt(process.env.REDIS_PORT || '6379'),
        password: process.env.REDIS_PASSWORD
      },
      ...options
    });
    
    const scheduler = new QueueScheduler(name, {
      connection: this.redisConnection
    });
    
    this.queues.set(name, queue);
    this.schedulers.set(name, scheduler);
    this.setupQueueEventListeners(queue, name);
    
    return queue;
  }
  
  async addJob(
    queueName: string,
    jobName: string,
    data: JobData,
    options?: JobOptions
  ): Promise<Job> {
    const queue = this.queues.get(queueName);
    if (!queue) {
      throw new Error(`Queue ${queueName} not found`);
    }
    
    const jobOptions: JobOptions = {
      ...options,
      priority: this.getJobPriority(data.type)
    };
    
    const job = await queue.add(jobName, data, jobOptions);
    console.log(`Job added to queue ${queueName}: ${job.id}`);
    
    return job;
  }
  
  async addBulkJobs(
    queueName: string,
    jobs: Array<{ name: string; data: JobData; opts?: JobOptions }>
  ): Promise<Job[]> {
    const queue = this.queues.get(queueName);
    if (!queue) {
      throw new Error(`Queue ${queueName} not found`);
    }
    
    const bulkJobs = jobs.map(job => ({
      name: job.name,
      data: job.data,
      opts: {
        ...job.opts,
        priority: this.getJobPriority(job.data.type)
      }
    }));
    
    const addedJobs = await queue.addBulk(bulkJobs);
    console.log(`${jobs.length} jobs added to queue ${queueName}`);
    
    return addedJobs;
  }
  
  async scheduleJob(
    queueName: string,
    jobName: string,
    data: JobData,
    cronExpression: string,
    options?: JobOptions
  ): Promise<void> {
    const queue = this.queues.get(queueName);
    if (!queue) {
      throw new Error(`Queue ${queueName} not found`);
    }
    
    await queue.add(jobName, data, {
      ...options,
      repeat: { cron: cronExpression, tz: 'UTC' }
    });
    
    console.log(`Scheduled job added: ${jobName} with cron ${cronExpression}`);
  }
  
  async addDelayedJob(
    queueName: string,
    jobName: string,
    data: JobData,
    delayMs: number,
    options?: JobOptions
  ): Promise<Job> {
    return this.addJob(queueName, jobName, data, {
      ...options,
      delay: delayMs
    });
  }
  
  async getJobStatus(queueName: string, jobId: string): Promise<any> {
    const queue = this.queues.get(queueName);
    if (!queue) {
      throw new Error(`Queue ${queueName} not found`);
    }
    
    const job = await queue.getJob(jobId);
    if (!job) return null;
    
    const state = await job.getState();
    
    return {
      id: job.id,
      name: job.name,
      data: job.data,
      state,
      progress: job.progress(),
      attemptsMade: job.attemptsMade,
      processedOn: job.processedOn,
      finishedOn: job.finishedOn,
      failedReason: job.failedReason
    };
  }
  
  async getQueueStats(queueName: string): Promise<any> {
    const queue = this.queues.get(queueName);
    if (!queue) {
      throw new Error(`Queue ${queueName} not found`);
    }
    
    const [waiting, active, completed, failed, delayed, paused] = await Promise.all([
      queue.getWaitingCount(),
      queue.getActiveCount(),
      queue.getCompletedCount(),
      queue.getFailedCount(),
      queue.getDelayedCount(),
      queue.isPaused()
    ]);
    
    return {
      name: queueName,
      counts: { waiting, active, completed, failed, delayed },
      isPaused: paused
    };
  }
  
  async pauseQueue(queueName: string): Promise<void> {
    const queue = this.queues.get(queueName);
    if (!queue) {
      throw new Error(`Queue ${queueName} not found`);
    }
    
    await queue.pause();
    console.log(`Queue ${queueName} paused`);
  }
  
  async resumeQueue(queueName: string): Promise<void> {
    const queue = this.queues.get(queueName);
    if (!queue) {
      throw new Error(`Queue ${queueName} not found`);
    }
    
    await queue.resume();
    console.log(`Queue ${queueName} resumed`);
  }
  
  async cleanQueue(queueName: string, grace: number = 5000): Promise<void> {
    const queue = this.queues.get(queueName);
    if (!queue) {
      throw new Error(`Queue ${queueName} not found`);
    }
    
    await queue.clean(grace, 'completed');
    await queue.clean(grace, 'failed');
    console.log(`Queue ${queueName} cleaned`);
  }
  
  async retryFailedJobs(queueName: string): Promise<number> {
    const queue = this.queues.get(queueName);
    if (!queue) {
      throw new Error(`Queue ${queueName} not found`);
    }
    
    const failedJobs = await queue.getFailed();
    let retryCount = 0;
    
    for (const job of failedJobs) {
      if (job.attemptsMade < (job.opts.attempts || 3)) {
        await job.retry();
        retryCount++;
      }
    }
    
    console.log(`Retried ${retryCount} failed jobs in queue ${queueName}`);
    return retryCount;
  }
  
  private setupQueueEventListeners(queue: Queue, name: string): void {
    queue.on('completed', (job) => {
      console.log(`Job ${job.id} completed in queue ${name}`);
    });
    
    queue.on('failed', (job, err) => {
      console.error(`Job ${job.id} failed in queue ${name}:`, err.message);
    });
    
    queue.on('stalled', (job) => {
      console.warn(`Job ${job.id} stalled in queue ${name}`);
    });
  }
  
  private getJobPriority(jobType: JobType): number {
    const priorityMap: Record<JobType, JobPriority> = {
      [JobType.AGENT_EXECUTION]: JobPriority.HIGH,
      [JobType.PROJECT_BUILD]: JobPriority.HIGH,
      [JobType.COMPONENT_GENERATION]: JobPriority.NORMAL,
      [JobType.EMAIL_NOTIFICATION]: JobPriority.NORMAL,
      [JobType.REPORT_GENERATION]: JobPriority.LOW,
      [JobType.CACHE_WARMING]: JobPriority.LOW,
      [JobType.DATA_EXPORT]: JobPriority.NORMAL,
      [JobType.CLEANUP]: JobPriority.LOW
    };
    
    return priorityMap[jobType] || JobPriority.NORMAL;
  }
  
  async shutdown(): Promise<void> {
    console.log('Shutting down job queues...');
    
    for (const [name, queue] of this.queues) {
      await queue.close();
      console.log(`Queue ${name} closed`);
    }
    
    for (const [name, scheduler] of this.schedulers) {
      await scheduler.close();
      console.log(`Scheduler ${name} closed`);
    }
    
    await this.redisConnection.quit();
    console.log('Job queues shutdown complete');
  }
}

export abstract class JobWorker {
  protected queue: Queue;
  protected concurrency: number;
  
  constructor(queue: Queue, concurrency: number = 1) {
    this.queue = queue;
    this.concurrency = concurrency;
  }
  
  async start(): Promise<void> {
    this.queue.process(this.concurrency, async (job: Job) => {
      const startTime = Date.now();
      
      try {
        console.log(`Processing job ${job.id} of type ${job.name}`);
        await job.progress(0);
        
        const result = await this.process(job);
        await job.progress(100);
        
        const duration = Date.now() - startTime;
        console.log(`Job ${job.id} completed in ${duration}ms`);
        
        return result;
      } catch (error) {
        console.error(`Job ${job.id} failed:`, error);
        throw error;
      }
    });
  }
  
  abstract process(job: Job): Promise<any>;
}

export class AgentExecutionWorker extends JobWorker {
  async process(job: Job<AgentExecutionJob>): Promise<any> {
    const { agentName, input } = job.data;
    
    await job.progress(10);
    const agent = await this.initializeAgent(agentName);
    
    await job.progress(30);
    const result = await agent.execute(input);
    
    await job.progress(90);
    await this.saveResult(job.data.projectId!, result);
    
    return result;
  }
  
  private async initializeAgent(agentName: string): Promise<any> {
    return { execute: async (input: any) => ({ success: true, data: input }) };
  }
  
  private async saveResult(projectId: string, result: any): Promise<void> {
    console.log(`Saving result for project ${projectId}`);
  }
}