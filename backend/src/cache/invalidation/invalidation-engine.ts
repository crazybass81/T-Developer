import { EventEmitter } from 'events';
import { CacheManager } from '../cache-manager';

export interface InvalidationRule {
  trigger: string;
  targets: string[];
  condition?: (data: any) => boolean;
  delay?: number;
}

export interface InvalidationEvent {
  type: string;
  entityId: string;
  data?: any;
  timestamp: Date;
}

export class InvalidationEngine extends EventEmitter {
  private rules: Map<string, InvalidationRule[]> = new Map();
  private pendingInvalidations: Map<string, NodeJS.Timeout> = new Map();

  constructor(private cacheManager: CacheManager) {
    super();
    this.initializeRules();
  }

  private initializeRules(): void {
    // User invalidation rules
    this.addRule({
      trigger: 'user:update',
      targets: ['user:*', 'user:*:projects', 'user:*:sessions']
    });

    this.addRule({
      trigger: 'user:delete',
      targets: ['user:*', 'user:*:*']
    });

    // Project invalidation rules
    this.addRule({
      trigger: 'project:update',
      targets: ['project:*', 'user:*:projects', 'project:*:agents']
    });

    this.addRule({
      trigger: 'project:delete',
      targets: ['project:*', 'user:*:projects', 'project:*:*']
    });

    // Agent invalidation rules
    this.addRule({
      trigger: 'agent:update',
      targets: ['agent:*', 'project:*:agents'],
      delay: 100 // Small delay for agent updates
    });

    this.addRule({
      trigger: 'agent:execute',
      targets: ['agent:*', 'session:*'],
      condition: (data) => data.status === 'completed'
    });

    // Session invalidation rules
    this.addRule({
      trigger: 'session:expire',
      targets: ['session:*', 'agent:*:session']
    });
  }

  addRule(rule: InvalidationRule): void {
    if (!this.rules.has(rule.trigger)) {
      this.rules.set(rule.trigger, []);
    }
    this.rules.get(rule.trigger)!.push(rule);
  }

  async invalidate(event: InvalidationEvent): Promise<void> {
    const rules = this.rules.get(event.type) || [];
    
    for (const rule of rules) {
      // Check condition if exists
      if (rule.condition && !rule.condition(event.data)) {
        continue;
      }

      // Apply delay if specified
      if (rule.delay) {
        this.scheduleDelayedInvalidation(event, rule);
      } else {
        await this.executeInvalidation(event, rule);
      }
    }
  }

  private scheduleDelayedInvalidation(event: InvalidationEvent, rule: InvalidationRule): void {
    const key = `${event.type}:${event.entityId}:${Date.now()}`;
    
    const timeout = setTimeout(async () => {
      await this.executeInvalidation(event, rule);
      this.pendingInvalidations.delete(key);
    }, rule.delay);

    this.pendingInvalidations.set(key, timeout);
  }

  private async executeInvalidation(event: InvalidationEvent, rule: InvalidationRule): Promise<void> {
    for (const target of rule.targets) {
      const pattern = target.replace('*', event.entityId);
      
      if (pattern.includes(':*')) {
        // Pattern-based invalidation
        await this.cacheManager.invalidateByPattern(pattern);
      } else {
        // Direct key invalidation
        await this.cacheManager.del(pattern);
      }
    }

    this.emit('invalidated', { event, rule, timestamp: new Date() });
  }

  // Cascade invalidation for related entities
  async cascadeInvalidation(entityType: string, entityId: string, changes: any): Promise<void> {
    const cascadeRules = this.getCascadeRules(entityType, changes);
    
    for (const rule of cascadeRules) {
      await this.invalidate({
        type: rule.trigger,
        entityId,
        data: changes,
        timestamp: new Date()
      });
    }
  }

  private getCascadeRules(entityType: string, changes: any): InvalidationRule[] {
    const rules: InvalidationRule[] = [];

    switch (entityType) {
      case 'user':
        if (changes.email || changes.username) {
          rules.push({
            trigger: 'user:profile_change',
            targets: ['user:*', 'user:*:projects', 'query:user:*']
          });
        }
        break;

      case 'project':
        if (changes.status === 'deleted') {
          rules.push({
            trigger: 'project:cascade_delete',
            targets: ['project:*:*', 'agent:*', 'session:*']
          });
        }
        break;

      case 'agent':
        if (changes.status === 'completed') {
          rules.push({
            trigger: 'agent:completion',
            targets: ['agent:*', 'project:*:progress']
          });
        }
        break;
    }

    return rules;
  }

  // Smart invalidation based on access patterns
  async smartInvalidate(entityType: string, entityId: string, accessFrequency: number): Promise<void> {
    // High-frequency entities get immediate invalidation
    if (accessFrequency > 100) {
      await this.invalidate({
        type: `${entityType}:update`,
        entityId,
        timestamp: new Date()
      });
    } else {
      // Low-frequency entities get delayed invalidation
      this.scheduleDelayedInvalidation(
        {
          type: `${entityType}:update`,
          entityId,
          timestamp: new Date()
        },
        {
          trigger: `${entityType}:update`,
          targets: [`${entityType}:${entityId}`],
          delay: 5000 // 5 second delay
        }
      );
    }
  }

  clearPendingInvalidations(): void {
    for (const timeout of this.pendingInvalidations.values()) {
      clearTimeout(timeout);
    }
    this.pendingInvalidations.clear();
  }
}