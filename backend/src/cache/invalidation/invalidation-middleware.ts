import { Request, Response, NextFunction } from 'express';
import { CacheEventBus, CacheEvent } from './event-bus';

export interface InvalidationConfig {
  entity: string;
  operations: ('create' | 'update' | 'delete')[];
  extractId: (req: Request) => string;
  extractUserId?: (req: Request) => string;
}

export class InvalidationMiddleware {
  constructor(private eventBus: CacheEventBus) {}

  // Middleware factory for automatic cache invalidation
  createMiddleware(config: InvalidationConfig) {
    return (req: Request, res: Response, next: NextFunction) => {
      const originalSend = res.send;
      
      res.send = function(data: any) {
        // Only invalidate on successful operations
        if (res.statusCode >= 200 && res.statusCode < 300) {
          const operation = InvalidationMiddleware.getOperationFromMethod(req.method);
          
          if (config.operations.includes(operation)) {
            const event: CacheEvent = {
              type: operation,
              entity: config.entity,
              id: config.extractId(req),
              data: req.body,
              userId: config.extractUserId?.(req)
            };

            // Async invalidation - don't block response
            setImmediate(() => {
              InvalidationMiddleware.prototype.eventBus.publishEvent(event);
            });
          }
        }

        return originalSend.call(this, data);
      };

      next();
    };
  }

  private static getOperationFromMethod(method: string): 'create' | 'update' | 'delete' {
    switch (method.toUpperCase()) {
      case 'POST': return 'create';
      case 'PUT':
      case 'PATCH': return 'update';
      case 'DELETE': return 'delete';
      default: return 'update';
    }
  }

  // Bulk invalidation middleware
  createBulkMiddleware(configs: InvalidationConfig[]) {
    return (req: Request, res: Response, next: NextFunction) => {
      const originalSend = res.send;
      
      res.send = function(data: any) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          const operation = InvalidationMiddleware.getOperationFromMethod(req.method);
          
          // Process all configurations
          configs.forEach(config => {
            if (config.operations.includes(operation)) {
              const event: CacheEvent = {
                type: operation,
                entity: config.entity,
                id: config.extractId(req),
                data: req.body,
                userId: config.extractUserId?.(req)
              };

              setImmediate(() => {
                InvalidationMiddleware.prototype.eventBus.publishEvent(event);
              });
            }
          });
        }

        return originalSend.call(this, data);
      };

      next();
    };
  }

  // Manual invalidation trigger
  async triggerInvalidation(event: CacheEvent): Promise<void> {
    await this.eventBus.publishEvent(event);
  }
}

// Pre-configured middleware for T-Developer entities
export class TDeveloperInvalidationMiddleware {
  constructor(private middleware: InvalidationMiddleware) {}

  // User operations
  userMiddleware() {
    return this.middleware.createMiddleware({
      entity: 'user',
      operations: ['create', 'update', 'delete'],
      extractId: (req) => req.params.userId || req.params.id,
      extractUserId: (req) => req.user?.id
    });
  }

  // Project operations
  projectMiddleware() {
    return this.middleware.createMiddleware({
      entity: 'project',
      operations: ['create', 'update', 'delete'],
      extractId: (req) => req.params.projectId || req.params.id,
      extractUserId: (req) => req.user?.id
    });
  }

  // Agent operations
  agentMiddleware() {
    return this.middleware.createMiddleware({
      entity: 'agent',
      operations: ['create', 'update', 'delete'],
      extractId: (req) => req.params.agentId || req.params.id,
      extractUserId: (req) => req.user?.id
    });
  }

  // Session operations
  sessionMiddleware() {
    return this.middleware.createMiddleware({
      entity: 'session',
      operations: ['create', 'delete'],
      extractId: (req) => req.params.sessionId || req.params.id,
      extractUserId: (req) => req.user?.id
    });
  }
}