import { EventEmitter } from 'events';

export interface WorkflowState {
  workflowId: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  tasks: Map<string, any>;
  metadata: Record<string, any>;
  lastUpdated: Date;
}

export class StateSynchronizer extends EventEmitter {
  private states = new Map<string, WorkflowState>();
  private locks = new Map<string, boolean>();

  async syncState(workflowId: string, state: Partial<WorkflowState>): Promise<void> {
    // 분산 락 획득
    await this.acquireLock(workflowId);
    
    try {
      // 현재 상태 읽기
      const currentState = this.getState(workflowId);
      
      // 상태 병합
      const mergedState = this.mergeStates(currentState, state);
      
      // 상태 저장
      this.saveState(workflowId, mergedState);
      
      // 변경 사항 브로드캐스트
      this.broadcastStateChange(workflowId, mergedState);
      
    } finally {
      this.releaseLock(workflowId);
    }
  }

  getState(workflowId: string): WorkflowState {
    return this.states.get(workflowId) || {
      workflowId,
      status: 'pending',
      tasks: new Map(),
      metadata: {},
      lastUpdated: new Date()
    };
  }

  async updateTaskState(workflowId: string, taskId: string, taskState: any): Promise<void> {
    await this.acquireLock(workflowId);
    
    try {
      const state = this.getState(workflowId);
      state.tasks.set(taskId, taskState);
      state.lastUpdated = new Date();
      
      this.saveState(workflowId, state);
      this.emit('taskStateChanged', { workflowId, taskId, taskState });
      
    } finally {
      this.releaseLock(workflowId);
    }
  }

  async waitForTaskCompletion(workflowId: string, taskId: string, timeout = 30000): Promise<any> {
    return new Promise((resolve, reject) => {
      const timeoutId = setTimeout(() => {
        reject(new Error(`Task ${taskId} completion timeout`));
      }, timeout);
      
      const checkTask = () => {
        const state = this.getState(workflowId);
        const taskState = state.tasks.get(taskId);
        
        if (taskState && taskState.status === 'completed') {
          clearTimeout(timeoutId);
          resolve(taskState.result);
        } else if (taskState && taskState.status === 'failed') {
          clearTimeout(timeoutId);
          reject(new Error(taskState.error));
        }
      };
      
      // 즉시 확인
      checkTask();
      
      // 상태 변경 리스너
      this.on('taskStateChanged', (event) => {
        if (event.workflowId === workflowId && event.taskId === taskId) {
          checkTask();
        }
      });
    });
  }

  private async acquireLock(workflowId: string): Promise<void> {
    while (this.locks.get(workflowId)) {
      await new Promise(resolve => setTimeout(resolve, 10));
    }
    this.locks.set(workflowId, true);
  }

  private releaseLock(workflowId: string): void {
    this.locks.delete(workflowId);
  }

  private mergeStates(current: WorkflowState, update: Partial<WorkflowState>): WorkflowState {
    const merged = { ...current };
    
    if (update.status) merged.status = update.status;
    if (update.metadata) {
      merged.metadata = { ...merged.metadata, ...update.metadata };
    }
    if (update.tasks) {
      for (const [taskId, taskState] of update.tasks) {
        merged.tasks.set(taskId, taskState);
      }
    }
    
    merged.lastUpdated = new Date();
    return merged;
  }

  private saveState(workflowId: string, state: WorkflowState): void {
    this.states.set(workflowId, state);
  }

  private broadcastStateChange(workflowId: string, state: WorkflowState): void {
    this.emit('stateChanged', { workflowId, state });
  }

  // 상태 스냅샷
  createSnapshot(workflowId: string): WorkflowState {
    const state = this.getState(workflowId);
    return JSON.parse(JSON.stringify({
      ...state,
      tasks: Array.from(state.tasks.entries())
    }));
  }

  // 상태 복원
  restoreSnapshot(snapshot: any): void {
    const state: WorkflowState = {
      ...snapshot,
      tasks: new Map(snapshot.tasks)
    };
    
    this.states.set(state.workflowId, state);
    this.emit('stateRestored', state);
  }
}