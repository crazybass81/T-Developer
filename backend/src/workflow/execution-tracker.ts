import { EventEmitter } from 'events';
import { WorkflowPlan } from '../agents/supervisor/supervisor-agent';

interface ExecutionState {
  workflowId: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  currentStep: string;
  startTime: Date;
  endTime?: Date;
  results: Map<string, any>;
  errors: Error[];
  progress: number;
}

export class ExecutionTracker extends EventEmitter {
  private states: Map<string, ExecutionState> = new Map();
  
  async trackExecution(workflowId: string, workflow: WorkflowPlan): Promise<void> {
    const state: ExecutionState = {
      workflowId,
      status: 'pending',
      currentStep: workflow.steps[0]?.id || '',
      startTime: new Date(),
      results: new Map(),
      errors: [],
      progress: 0
    };
    
    this.states.set(workflowId, state);
    this.emitUpdate(workflowId, state);
    
    // 실시간 업데이트를 위한 WebSocket 연결 설정
    this.setupRealtimeUpdates(workflowId);
  }
  
  async updateStepProgress(
    workflowId: string,
    stepId: string,
    progress: number
  ): Promise<void> {
    const state = this.states.get(workflowId);
    if (!state) return;
    
    state.currentStep = stepId;
    state.progress = progress;
    state.status = 'running';
    
    this.emitUpdate(workflowId, state);
  }
  
  async completeStep(
    workflowId: string,
    stepId: string,
    result: any
  ): Promise<void> {
    const state = this.states.get(workflowId);
    if (!state) return;
    
    state.results.set(stepId, result);
    
    this.emitUpdate(workflowId, state);
  }
  
  async failStep(
    workflowId: string,
    stepId: string,
    error: Error
  ): Promise<void> {
    const state = this.states.get(workflowId);
    if (!state) return;
    
    state.errors.push(error);
    state.status = 'failed';
    
    this.emitUpdate(workflowId, state);
  }
  
  async completeWorkflow(workflowId: string): Promise<void> {
    const state = this.states.get(workflowId);
    if (!state) return;
    
    state.status = 'completed';
    state.endTime = new Date();
    state.progress = 100;
    
    this.emitUpdate(workflowId, state);
  }
  
  getExecutionState(workflowId: string): ExecutionState | undefined {
    return this.states.get(workflowId);
  }
  
  getAllExecutions(): ExecutionState[] {
    return Array.from(this.states.values());
  }
  
  private emitUpdate(workflowId: string, state: ExecutionState): void {
    this.emit('stateUpdate', {
      workflowId,
      state: { ...state, results: Object.fromEntries(state.results) }
    });
  }
  
  private setupRealtimeUpdates(workflowId: string): void {
    // WebSocket을 통한 실시간 업데이트
    this.on(`progress:${workflowId}`, (data) => {
      this.broadcast(workflowId, {
        type: 'progress',
        data
      });
    });
    
    this.on(`error:${workflowId}`, (error) => {
      this.broadcast(workflowId, {
        type: 'error',
        error: error.message
      });
    });
    
    this.on(`complete:${workflowId}`, (result) => {
      this.broadcast(workflowId, {
        type: 'complete',
        result
      });
    });
  }
  
  private broadcast(workflowId: string, message: any): void {
    // WebSocket 브로드캐스트 (추후 구현)
    console.log(`Broadcasting to ${workflowId}:`, message);
  }
}