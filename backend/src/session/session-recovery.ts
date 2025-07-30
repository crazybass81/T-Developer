import { SessionManager } from './session-manager';

interface SessionSnapshot {
  sessionId: string;
  state: any;
  timestamp: Date;
  checksum: string;
}

export class SessionRecovery {
  private sessionManager: SessionManager;
  private snapshots: Map<string, SessionSnapshot[]> = new Map();

  constructor(sessionManager: SessionManager) {
    this.sessionManager = sessionManager;
  }

  async createSnapshot(sessionId: string, state: any): Promise<void> {
    const snapshot: SessionSnapshot = {
      sessionId,
      state: JSON.parse(JSON.stringify(state)),
      timestamp: new Date(),
      checksum: this.calculateChecksum(state)
    };

    if (!this.snapshots.has(sessionId)) {
      this.snapshots.set(sessionId, []);
    }

    const sessionSnapshots = this.snapshots.get(sessionId)!;
    sessionSnapshots.push(snapshot);

    // Keep only last 10 snapshots
    if (sessionSnapshots.length > 10) {
      sessionSnapshots.shift();
    }
  }

  async recoverSession(sessionId: string): Promise<any | null> {
    const sessionSnapshots = this.snapshots.get(sessionId);
    if (!sessionSnapshots || sessionSnapshots.length === 0) {
      return null;
    }

    // Get latest valid snapshot
    const latestSnapshot = sessionSnapshots[sessionSnapshots.length - 1];
    
    // Verify checksum
    const currentChecksum = this.calculateChecksum(latestSnapshot.state);
    if (currentChecksum !== latestSnapshot.checksum) {
      console.warn(`Checksum mismatch for session ${sessionId}`);
      return null;
    }

    return latestSnapshot.state;
  }

  async validateSession(sessionId: string): Promise<boolean> {
    const session = await this.sessionManager.getSession(sessionId);
    return session !== null && session.status === 'active';
  }

  private calculateChecksum(data: any): string {
    const crypto = require('crypto');
    return crypto.createHash('md5').update(JSON.stringify(data)).digest('hex');
  }

  async cleanupSnapshots(sessionId: string): Promise<void> {
    this.snapshots.delete(sessionId);
  }
}