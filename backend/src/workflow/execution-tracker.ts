import { EventEmitter } from 'events';
import { WebSocket } from 'ws';

interface ExecutionState {
  workflowId: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  currentStep: string;
  startTime: Date;
  endTime?: Date;
  results: Map<string, any>;
  errors: Error[];
  progress?: number;
}

interface Workflow {
  steps: Array<{ id: string; name: string }>;
}

export class ExecutionTracker {
  private states: Map<string, ExecutionState> = new Map();
  private eventEmitter: EventEmitter = new EventEmitter();
  private wsConnections: Map<string, WebSocket[]> = new Map();

  async trackExecution(workflowId: string, workflow: Workflow): Promise<void> {
    const state: ExecutionState = {
      workflowId,
      status: 'pending',
      currentStep: workflow.steps[0]?.id || '',
      startTime: new Date(),
      results: new Map(),
      errors: []
    };
    
    this.states.set(workflowId, state);
    this.emitUpdate(workflowId, state);
    this.setupRealtimeUpdates(workflowId);
  }

  async updateStepProgress(workflowId: string, stepId: string, progress: number): Promise<void> {
    const state = this.states.get(workflowId);
    if (!state) return;
    
    state.currentStep = stepId;
    state.progress = progress;
    
    this.emitUpdate(workflowId, { ...state, progress });
  }

  async completeExecution(workflowId: string, result?: any): Promise<void> {
    const state = this.states.get(workflowId);
    if (!state) return;

    state.status = 'completed';
    state.endTime = new Date();
    if (result) state.results.set('final', result);

    this.emitUpdate(workflowId, state);
  }

  async failExecution(workflowId: string, error: Error): Promise<void> {
    const state = this.states.get(workflowId);
    if (!state) return;

    state.status = 'failed';
    state.endTime = new Date();
    state.errors.push(error);

    this.emitUpdate(workflowId, state);
  }

  getExecutionState(workflowId: string): ExecutionState | undefined {
    return this.states.get(workflowId);
  }

  private emitUpdate(workflowId: string, state: ExecutionState): void {
    this.eventEmitter.emit(`progress:${workflowId}`, state);
  }

  private setupRealtimeUpdates(workflowId: string): void {
    this.eventEmitter.on(`progress:${workflowId}`, (data) => {
      this.broadcast(workflowId, {
        type: 'progress',
        data
      });
    });
  }

  private broadcast(workflowId: string, message: any): void {
    const connections = this.wsConnections.get(workflowId) || [];
    connections.forEach(ws => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify(message));
      }
    });
  }

  addWebSocketConnection(workflowId: string, ws: WebSocket): void {
    if (!this.wsConnections.has(workflowId)) {
      this.wsConnections.set(workflowId, []);
    }
    this.wsConnections.get(workflowId)!.push(ws);

    ws.on('close', () => {
      const connections = this.wsConnections.get(workflowId) || [];
      const index = connections.indexOf(ws);
      if (index > -1) connections.splice(index, 1);
    });
  }
}