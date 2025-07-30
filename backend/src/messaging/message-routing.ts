// Task 1.14.4: 메시지 라우팅 및 필터링
interface RoutingRule {
  condition: (message: any) => boolean;
  destination: string;
  priority: number;
}

export class MessageRouter {
  private rules: RoutingRule[] = [];

  addRule(rule: RoutingRule): void {
    this.rules.push(rule);
    this.rules.sort((a, b) => b.priority - a.priority);
  }

  route(message: any): string[] {
    const destinations: string[] = [];
    
    for (const rule of this.rules) {
      if (rule.condition(message)) {
        destinations.push(rule.destination);
      }
    }
    
    return destinations.length > 0 ? destinations : ['default'];
  }
}

export class MessageFilter {
  private filters: Map<string, (message: any) => boolean> = new Map();

  addFilter(name: string, filterFn: (message: any) => boolean): void {
    this.filters.set(name, filterFn);
  }

  filter(message: any): boolean {
    for (const [name, filterFn] of this.filters) {
      if (!filterFn(message)) {
        return false;
      }
    }
    return true;
  }
}

// Pre-configured routing for T-Developer
export class AgentMessageRouter extends MessageRouter {
  constructor() {
    super();
    this.setupDefaultRules();
  }

  private setupDefaultRules(): void {
    // High priority agent tasks
    this.addRule({
      condition: (msg) => msg.type === 'agent-task' && msg.priority === 'high',
      destination: 'high-priority-queue',
      priority: 100
    });

    // Regular agent tasks
    this.addRule({
      condition: (msg) => msg.type === 'agent-task',
      destination: 'agent-tasks-queue',
      priority: 50
    });

    // Notifications
    this.addRule({
      condition: (msg) => msg.type === 'notification',
      destination: 'notifications-queue',
      priority: 30
    });

    // Error handling
    this.addRule({
      condition: (msg) => msg.error,
      destination: 'error-queue',
      priority: 200
    });
  }
}