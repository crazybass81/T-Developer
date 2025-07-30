export { SessionManager } from './session-manager';
export { SessionTracker } from './session-tracker';
export { SessionRecovery } from './session-recovery';
export { SessionMiddleware } from './session-middleware';

import { SessionManager } from './session-manager';
import { SessionTracker } from './session-tracker';
import { SessionMiddleware } from './session-middleware';

// Initialize session system
export function initializeSessionSystem() {
  const sessionManager = new SessionManager();
  const sessionTracker = new SessionTracker();
  const sessionMiddleware = new SessionMiddleware();

  // Setup cleanup interval for expired sessions
  setInterval(async () => {
    await sessionManager.cleanupExpiredSessions();
  }, 60 * 60 * 1000); // Every hour

  console.log('✅ Session management system initialized');

  return {
    sessionManager,
    sessionTracker,
    sessionMiddleware
  };
}