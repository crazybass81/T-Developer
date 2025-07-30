import { Request, Response, NextFunction } from 'express';
import { SessionManager } from './session-manager';
import { SessionTracker } from './session-tracker';

declare global {
  namespace Express {
    interface Request {
      session?: any;
      sessionId?: string;
    }
  }
}

export class SessionMiddleware {
  private sessionManager: SessionManager;
  private sessionTracker: SessionTracker;

  constructor() {
    this.sessionManager = new SessionManager();
    this.sessionTracker = new SessionTracker();
  }

  middleware() {
    return async (req: Request, res: Response, next: NextFunction) => {
      const sessionId = req.headers['x-session-id'] as string || 
                       req.query.sessionId as string;

      if (!sessionId) {
        return res.status(401).json({ error: 'Session ID required' });
      }

      try {
        const session = await this.sessionManager.getSession(sessionId);
        
        if (!session) {
          return res.status(401).json({ error: 'Invalid or expired session' });
        }

        // Update session activity
        await this.sessionManager.updateActivity(sessionId);
        this.sessionTracker.updateActivity(sessionId);

        // Attach session to request
        req.session = session;
        req.sessionId = sessionId;

        next();
      } catch (error: any) {
        res.status(500).json({ error: 'Session validation failed' });
      }
    };
  }

  async createSessionEndpoint(req: Request, res: Response) {
    try {
      const { userId, metadata = {} } = req.body;
      
      if (!userId) {
        return res.status(400).json({ error: 'User ID required' });
      }

      const sessionId = await this.sessionManager.createSession(userId, metadata);
      this.sessionTracker.trackSession(sessionId, userId);

      res.json({ 
        sessionId, 
        expiresIn: 8 * 60 * 60 * 1000, // 8 hours in ms
        message: 'Session created successfully' 
      });
    } catch (error: any) {
      res.status(500).json({ error: 'Failed to create session' });
    }
  }

  async terminateSessionEndpoint(req: Request, res: Response) {
    try {
      const { sessionId } = req.params;
      
      await this.sessionManager.terminateSession(sessionId);
      this.sessionTracker.expireSession(sessionId);

      res.json({ message: 'Session terminated successfully' });
    } catch (error: any) {
      res.status(500).json({ error: 'Failed to terminate session' });
    }
  }

  async getSessionMetrics(req: Request, res: Response) {
    const metrics = this.sessionTracker.getSessionMetrics();
    res.json(metrics);
  }
}