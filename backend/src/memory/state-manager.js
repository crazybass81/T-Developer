class StateManager {
  constructor() {
    this.states = new Map();
    this.stateHistory = new Map();
  }

  saveState(agentId, state) {
    const currentState = this.states.get(agentId);
    const version = currentState ? currentState.version + 1 : 1;
    
    const snapshot = {
      id: this.generateSnapshotId(),
      agentId,
      state: JSON.parse(JSON.stringify(state)), // Deep copy
      timestamp: new Date(),
      version
    };

    this.states.set(agentId, snapshot);
    
    // Store in history
    if (!this.stateHistory.has(agentId)) {
      this.stateHistory.set(agentId, []);
    }
    this.stateHistory.get(agentId).push(snapshot);
    
    // Keep only last 10 versions
    const history = this.stateHistory.get(agentId);
    if (history.length > 10) {
      history.shift();
    }

    return snapshot.id;
  }

  getState(agentId) {
    const snapshot = this.states.get(agentId);
    return snapshot ? snapshot.state : null;
  }

  getStateHistory(agentId) {
    return this.stateHistory.get(agentId) || [];
  }

  restoreState(agentId, version) {
    const history = this.stateHistory.get(agentId);
    if (!history) return false;

    const targetSnapshot = history.find(s => s.version === version);
    if (!targetSnapshot) return false;

    this.states.set(agentId, {
      ...targetSnapshot,
      id: this.generateSnapshotId(),
      timestamp: new Date(),
      version: (this.states.get(agentId)?.version || 0) + 1
    });

    return true;
  }

  clearState(agentId) {
    this.states.delete(agentId);
    this.stateHistory.delete(agentId);
  }

  generateSnapshotId() {
    return `snap_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  getStats() {
    const totalSnapshots = Array.from(this.stateHistory.values())
      .reduce((sum, history) => sum + history.length, 0);

    return {
      activeStates: this.states.size,
      totalSnapshots,
      agents: Array.from(this.states.keys())
    };
  }
}

module.exports = { StateManager };