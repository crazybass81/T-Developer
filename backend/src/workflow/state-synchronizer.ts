import Redis from 'ioredis';
import { EventEmitter } from 'events';

export interface WorkflowState {
  workflowId: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  tasks: Record<string, TaskState>;
  context: Record<string, any>;
  lastUpdated: string;
  version: number;
}

export interface TaskState {
  taskId: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  result?: any;
  error?: string;
  startTime?: string;
  endTime?: string;
}

export interface StateChange {
  workflowId: string;
  changes: Record<string, any>;
  timestamp: string;
  source: string;
}

export class StateSynchronizer extends EventEmitter {
  private redis: Redis;
  private subscriber: Redis;
  private locks = new Map<string, Promise<void>>();
  private subscribers = new Set<string>();

  constructor(redisConfig?: any) {
    super();
    const config = redisConfig || {
      host: process.env.REDIS_HOST || 'localhost',
      port: parseInt(process.env.REDIS_PORT || '6379'),
      retryDelayOnFailover: 100,
      maxRetriesPerRequest: 3
    };
    
    this.redis = new Redis(config);
    this.subscriber = new Redis(config);

    this.setupSubscriptions();
  }

  private setupSubscriptions(): void {
    // 별도 클라이언트로 구독
    this.subscriber.on('message', (channel: string, message: string) => {
      try {
        const stateChange: StateChange = JSON.parse(message);
        this.emit('stateChange', stateChange);
      } catch (error) {
        console.error('Failed to parse state change message:', error);
      }
    });
  }

  async syncState(workflowId: string, updates: Partial<WorkflowState>): Promise<void> {
    const lockKey = `lock:workflow:${workflowId}`;
    
    // 분산 락 획득
    await this.acquireLock(lockKey, async () => {
      // 현재 상태 읽기
      const currentState = await this.getState(workflowId);
      
      // 상태 병합
      const mergedState = this.mergeStates(currentState, updates);
      
      // 버전 증가
      mergedState.version = (currentState?.version || 0) + 1;
      mergedState.lastUpdated = new Date().toISOString();
      
      // 상태 저장
      await this.saveState(workflowId, mergedState);
      
      // 변경 사항 브로드캐스트
      await this.broadcastStateChange(workflowId, updates);
    });
  }

  private async acquireLock(lockKey: string, operation: () => Promise<void>): Promise<void> {
    // 기존 락이 있으면 대기
    if (this.locks.has(lockKey)) {
      await this.locks.get(lockKey);
    }

    // 새 락 생성
    const lockPromise = this.executeLock(lockKey, operation);
    this.locks.set(lockKey, lockPromise);

    try {
      await lockPromise;
    } finally {
      this.locks.delete(lockKey);
    }
  }

  private async executeLock(lockKey: string, operation: () => Promise<void>): Promise<void> {
    const lockValue = `${Date.now()}-${Math.random()}`;
    const lockTimeout = 30000; // 30초

    try {
      // Redis 분산 락 획득
      const acquired = await this.redis.set(
        lockKey,
        lockValue,
        'PX',
        lockTimeout,
        'NX'
      );

      if (!acquired) {
        // 락 획득 실패 시 재시도
        await new Promise(resolve => setTimeout(resolve, 100));
        return this.executeLock(lockKey, operation);
      }

      // 락 획득 성공 시 작업 실행
      await operation();

    } finally {
      // 락 해제 (자신이 설정한 락인지 확인)
      const script = `
        if redis.call("get", KEYS[1]) == ARGV[1] then
          return redis.call("del", KEYS[1])
        else
          return 0
        end
      `;
      
      await this.redis.eval(script, 1, lockKey, lockValue);
    }
  }

  async getState(workflowId: string): Promise<WorkflowState | null> {
    const stateKey = `workflow:state:${workflowId}`;
    const stateData = await this.redis.get(stateKey);
    
    if (!stateData) {
      return null;
    }

    try {
      return JSON.parse(stateData);
    } catch (error) {
      console.error(`Failed to parse state for workflow ${workflowId}:`, error);
      return null;
    }
  }

  private async saveState(workflowId: string, state: WorkflowState): Promise<void> {
    const stateKey = `workflow:state:${workflowId}`;
    const ttl = 24 * 60 * 60; // 24시간

    await this.redis.setex(stateKey, ttl, JSON.stringify(state));
  }

  private mergeStates(current: WorkflowState | null, updates: Partial<WorkflowState>): WorkflowState {
    if (!current) {
      return {
        workflowId: updates.workflowId!,
        status: 'pending',
        tasks: {},
        context: {},
        lastUpdated: new Date().toISOString(),
        version: 0,
        ...updates
      };
    }

    const merged = { ...current };

    // 기본 필드 업데이트
    Object.keys(updates).forEach(key => {
      if (key === 'tasks') {
        // 태스크 상태는 개별적으로 병합
        merged.tasks = { ...merged.tasks, ...updates.tasks };
      } else if (key === 'context') {
        // 컨텍스트는 깊은 병합
        merged.context = this.deepMerge(merged.context, updates.context || {});
      } else if (updates[key as keyof WorkflowState] !== undefined) {
        (merged as any)[key] = updates[key as keyof WorkflowState];
      }
    });

    return merged;
  }

  private deepMerge(target: any, source: any): any {
    const result = { ...target };

    Object.keys(source).forEach(key => {
      if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
        result[key] = this.deepMerge(result[key] || {}, source[key]);
      } else {
        result[key] = source[key];
      }
    });

    return result;
  }

  private async broadcastStateChange(workflowId: string, changes: Partial<WorkflowState>): Promise<void> {
    const stateChange: StateChange = {
      workflowId,
      changes,
      timestamp: new Date().toISOString(),
      source: 'state-synchronizer'
    };

    const channel = `workflow:state:${workflowId}`;
    await this.redis.publish(channel, JSON.stringify(stateChange));
  }

  // 태스크 상태 업데이트
  async updateTaskState(workflowId: string, taskId: string, taskState: Partial<TaskState>): Promise<void> {
    await this.syncState(workflowId, {
      tasks: {
        [taskId]: taskState as TaskState
      }
    });
  }

  // 워크플로우 상태 업데이트
  async updateWorkflowStatus(workflowId: string, status: WorkflowState['status']): Promise<void> {
    await this.syncState(workflowId, { status });
  }

  // 컨텍스트 업데이트
  async updateContext(workflowId: string, contextUpdates: Record<string, any>): Promise<void> {
    await this.syncState(workflowId, {
      context: contextUpdates
    });
  }

  // 상태 변경 구독
  subscribeToWorkflow(workflowId: string): void {
    const channel = `workflow:state:${workflowId}`;
    if (!this.subscribers.has(channel)) {
      this.subscriber.subscribe(channel);
      this.subscribers.add(channel);
    }
  }

  // 구독 해제
  unsubscribeFromWorkflow(workflowId: string): void {
    const channel = `workflow:state:${workflowId}`;
    if (this.subscribers.has(channel)) {
      this.subscriber.unsubscribe(channel);
      this.subscribers.delete(channel);
    }
  }

  // 워크플로우 상태 삭제
  async deleteState(workflowId: string): Promise<void> {
    const stateKey = `workflow:state:${workflowId}`;
    await this.redis.del(stateKey);
  }

  // 활성 워크플로우 목록
  async getActiveWorkflows(): Promise<string[]> {
    const pattern = 'workflow:state:*';
    const keys = await this.redis.keys(pattern);
    
    return keys.map(key => key.replace('workflow:state:', ''));
  }

  // 상태 통계
  async getStateStats(): Promise<{
    totalWorkflows: number;
    statusCounts: Record<string, number>;
    averageTaskCount: number;
  }> {
    const workflowIds = await this.getActiveWorkflows();
    const statusCounts: Record<string, number> = {};
    let totalTasks = 0;

    for (const workflowId of workflowIds) {
      const state = await this.getState(workflowId);
      if (state) {
        statusCounts[state.status] = (statusCounts[state.status] || 0) + 1;
        totalTasks += Object.keys(state.tasks).length;
      }
    }

    return {
      totalWorkflows: workflowIds.length,
      statusCounts,
      averageTaskCount: workflowIds.length > 0 ? totalTasks / workflowIds.length : 0
    };
  }

  // 정리
  async cleanup(): Promise<void> {
    await this.redis.disconnect();
    await this.subscriber.disconnect();
    this.removeAllListeners();
  }
}