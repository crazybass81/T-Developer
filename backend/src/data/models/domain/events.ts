// Domain Events for T-Developer

export abstract class DomainEvent {
  public readonly id: string;
  public readonly occurredAt: Date;
  public readonly version: number;

  constructor(
    public readonly aggregateId: string,
    public readonly eventType: string,
    version: number = 1
  ) {
    this.id = `${eventType}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    this.occurredAt = new Date();
    this.version = version;
  }

  abstract getEventData(): any;
}

// User Events
export class UserCreatedEvent extends DomainEvent {
  constructor(
    aggregateId: string,
    public readonly email: string,
    public readonly username: string,
    public readonly role: string
  ) {
    super(aggregateId, 'UserCreated');
  }

  getEventData(): any {
    return {
      email: this.email,
      username: this.username,
      role: this.role
    };
  }
}

export class UserDeactivatedEvent extends DomainEvent {
  constructor(
    aggregateId: string,
    public readonly reason: string
  ) {
    super(aggregateId, 'UserDeactivated');
  }

  getEventData(): any {
    return { reason: this.reason };
  }
}

// Project Events
export class ProjectCreatedEvent extends DomainEvent {
  constructor(
    aggregateId: string,
    public readonly name: string,
    public readonly ownerId: string,
    public readonly framework: string
  ) {
    super(aggregateId, 'ProjectCreated');
  }

  getEventData(): any {
    return {
      name: this.name,
      ownerId: this.ownerId,
      framework: this.framework
    };
  }
}

export class ProjectStatusChangedEvent extends DomainEvent {
  constructor(
    aggregateId: string,
    public readonly oldStatus: string,
    public readonly newStatus: string,
    public readonly progress: number
  ) {
    super(aggregateId, 'ProjectStatusChanged');
  }

  getEventData(): any {
    return {
      oldStatus: this.oldStatus,
      newStatus: this.newStatus,
      progress: this.progress
    };
  }
}

export class ProjectCompletedEvent extends DomainEvent {
  constructor(
    aggregateId: string,
    public readonly downloadUrl: string,
    public readonly processingTime: number
  ) {
    super(aggregateId, 'ProjectCompleted');
  }

  getEventData(): any {
    return {
      downloadUrl: this.downloadUrl,
      processingTime: this.processingTime
    };
  }
}

// Agent Events
export class AgentExecutionStartedEvent extends DomainEvent {
  constructor(
    aggregateId: string,
    public readonly agentName: string,
    public readonly projectId: string
  ) {
    super(aggregateId, 'AgentExecutionStarted');
  }

  getEventData(): any {
    return {
      agentName: this.agentName,
      projectId: this.projectId
    };
  }
}

export class AgentExecutionCompletedEvent extends DomainEvent {
  constructor(
    aggregateId: string,
    public readonly agentName: string,
    public readonly executionTime: number,
    public readonly success: boolean
  ) {
    super(aggregateId, 'AgentExecutionCompleted');
  }

  getEventData(): any {
    return {
      agentName: this.agentName,
      executionTime: this.executionTime,
      success: this.success
    };
  }
}

// Component Events
export class ComponentAddedEvent extends DomainEvent {
  constructor(
    aggregateId: string,
    public readonly componentName: string,
    public readonly version: string,
    public readonly source: string
  ) {
    super(aggregateId, 'ComponentAdded');
  }

  getEventData(): any {
    return {
      componentName: this.componentName,
      version: this.version,
      source: this.source
    };
  }
}

// Session Events
export class SessionStartedEvent extends DomainEvent {
  constructor(
    aggregateId: string,
    public readonly userId: string,
    public readonly ipAddress?: string
  ) {
    super(aggregateId, 'SessionStarted');
  }

  getEventData(): any {
    return {
      userId: this.userId,
      ipAddress: this.ipAddress
    };
  }
}

export class SessionExpiredEvent extends DomainEvent {
  constructor(
    aggregateId: string,
    public readonly userId: string,
    public readonly duration: number
  ) {
    super(aggregateId, 'SessionExpired');
  }

  getEventData(): any {
    return {
      userId: this.userId,
      duration: this.duration
    };
  }
}