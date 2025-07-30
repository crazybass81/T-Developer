// backend/src/memory/state-manager.ts
export interface StateSnapshot {
  id: string;
  agentId: string;
  state: any;
  timestamp: Date;
  version: number;
}

export class StateManager {
  private states: Map<string, StateSnapshot> = new Map();
  private stateHistory: Map<string, StateSnapshot[]> = new Map();

  // Save agent state
  saveState(agentId: string, state: any): string {
    const currentState = this.states.get(agentId);
    const version = currentState ? currentState.version + 1 : 1;
    
    const snapshot: StateSnapshot = {
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
    this.stateHistory.get(agentId)!.push(snapshot);
    
    // Keep only last 10 versions
    const history = this.stateHistory.get(agentId)!;
    if (history.length > 10) {
      history.shift();
    }

    return snapshot.id;
  }

  // Get current state
  getState(agentId: string): any {
    const snapshot = this.states.get(agentId);
    return snapshot ? snapshot.state : null;
  }

  // Get state history
  getStateHistory(agentId: string): StateSnapshot[] {
    return this.stateHistory.get(agentId) || [];
  }

  // Restore to previous state
  restoreState(agentId: string, version: number): boolean {
    const history = this.stateHistory.get(agentId);
    if (!history) return false;

    const targetSnapshot = history.find(s => s.version === version);
    if (!targetSnapshot) return false;

    this.states.set(agentId, {
      ...targetSnapshot,
      id: this.generateSnapshotId(),
      timestamp: new Date(),
      version: this.states.get(agentId)?.version || 0 + 1
    });

    return true;
  }

  // Clear agent state
  clearState(agentId: string): void {
    this.states.delete(agentId);
    this.stateHistory.delete(agentId);
  }

  private generateSnapshotId(): string {
    return `snap_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  getStats(): {
    activeStates: number;
    totalSnapshots: number;
    agents: string[];
  } {
    const totalSnapshots = Array.from(this.stateHistory.values())
      .reduce((sum, history) => sum + history.length, 0);

    return {
      activeStates: this.states.size,
      totalSnapshots,
      agents: Array.from(this.states.keys())
    };
  }
}