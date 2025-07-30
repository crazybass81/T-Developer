const { EventEmitter } = require('events');

class ExecutionTracker extends EventEmitter {
  constructor() {
    super();
    this.states = new Map();
  }
  
  async trackExecution(workflowId, workflow) {
    const state = {
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
    
    this.setupRealtimeUpdates(workflowId);
  }
  
  async updateStepProgress(workflowId, stepId, progress) {
    const state = this.states.get(workflowId);
    if (!state) return;
    
    state.currentStep = stepId;
    state.progress = progress;
    state.status = 'running';
    
    this.emitUpdate(workflowId, state);
  }
  
  async completeStep(workflowId, stepId, result) {
    const state = this.states.get(workflowId);
    if (!state) return;
    
    state.results.set(stepId, result);
    this.emitUpdate(workflowId, state);
  }
  
  async failStep(workflowId, stepId, error) {
    const state = this.states.get(workflowId);
    if (!state) return;
    
    state.errors.push(error);
    state.status = 'failed';
    
    this.emitUpdate(workflowId, state);
  }
  
  async completeWorkflow(workflowId) {
    const state = this.states.get(workflowId);
    if (!state) return;
    
    state.status = 'completed';
    state.endTime = new Date();
    state.progress = 100;
    
    this.emitUpdate(workflowId, state);
  }
  
  getExecutionState(workflowId) {
    return this.states.get(workflowId);
  }
  
  getAllExecutions() {
    return Array.from(this.states.values());
  }
  
  emitUpdate(workflowId, state) {
    this.emit('stateUpdate', {
      workflowId,
      state: { ...state, results: Object.fromEntries(state.results) }
    });
  }
  
  setupRealtimeUpdates(workflowId) {
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
  
  broadcast(workflowId, message) {
    console.log(`Broadcasting to ${workflowId}:`, message);
  }
}

module.exports = { ExecutionTracker };