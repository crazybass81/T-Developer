// Domain Aggregates for T-Developer

import { BaseModel } from '../base.model';
import { DomainEvent } from './events';

export abstract class AggregateRoot extends BaseModel {
  private domainEvents: DomainEvent[] = [];

  protected addDomainEvent(event: DomainEvent): void {
    this.domainEvents.push(event);
  }

  public getUncommittedEvents(): DomainEvent[] {
    return [...this.domainEvents];
  }

  public markEventsAsCommitted(): void {
    this.domainEvents = [];
  }

  public loadFromHistory(events: DomainEvent[]): void {
    events.forEach(event => this.apply(event));
    this.markEventsAsCommitted();
  }

  protected abstract apply(event: DomainEvent): void;
}

// Project Aggregate
export class ProjectAggregate extends AggregateRoot {
  private _name: string = '';
  private _status: string = 'draft';
  private _ownerId: string = '';
  private _agents: string[] = [];
  private _components: string[] = [];

  protected getEntityPrefix(): string {
    return 'proj_agg';
  }

  protected serialize(): any {
    return {
      name: this._name,
      status: this._status,
      ownerId: this._ownerId,
      agents: this._agents,
      components: this._components
    };
  }

  protected apply(event: DomainEvent): void {
    switch (event.eventType) {
      case 'ProjectCreated':
        this.applyProjectCreated(event);
        break;
      case 'ProjectStatusChanged':
        this.applyProjectStatusChanged(event);
        break;
      case 'AgentAdded':
        this.applyAgentAdded(event);
        break;
      case 'ComponentAdded':
        this.applyComponentAdded(event);
        break;
    }
  }

  // Business methods
  public createProject(name: string, ownerId: string, framework: string): void {
    if (this._name) {
      throw new Error('Project already exists');
    }

    const event = new (require('./events').ProjectCreatedEvent)(
      this.id,
      name,
      ownerId,
      framework
    );
    
    this.addDomainEvent(event);
    this.apply(event);
  }

  public changeStatus(newStatus: string, progress: number = 0): void {
    if (this._status === newStatus) {
      return;
    }

    const event = new (require('./events').ProjectStatusChangedEvent)(
      this.id,
      this._status,
      newStatus,
      progress
    );

    this.addDomainEvent(event);
    this.apply(event);
  }

  public addAgent(agentId: string): void {
    if (this._agents.includes(agentId)) {
      return;
    }

    this._agents.push(agentId);
    this.updateVersion();
  }

  public addComponent(componentId: string): void {
    if (this._components.includes(componentId)) {
      return;
    }

    this._components.push(componentId);
    this.updateVersion();
  }

  // Event handlers
  private applyProjectCreated(event: any): void {
    const data = event.getEventData();
    this._name = data.name;
    this._ownerId = data.ownerId;
    this._status = 'draft';
  }

  private applyProjectStatusChanged(event: any): void {
    const data = event.getEventData();
    this._status = data.newStatus;
  }

  private applyAgentAdded(event: any): void {
    const data = event.getEventData();
    if (!this._agents.includes(data.agentId)) {
      this._agents.push(data.agentId);
    }
  }

  private applyComponentAdded(event: any): void {
    const data = event.getEventData();
    if (!this._components.includes(data.componentId)) {
      this._components.push(data.componentId);
    }
  }

  // Getters
  public get name(): string { return this._name; }
  public get status(): string { return this._status; }
  public get ownerId(): string { return this._ownerId; }
  public get agents(): string[] { return [...this._agents]; }
  public get components(): string[] { return [...this._components]; }
}

// User Aggregate
export class UserAggregate extends AggregateRoot {
  private _email: string = '';
  private _username: string = '';
  private _role: string = 'developer';
  private _isActive: boolean = true;
  private _projects: string[] = [];

  protected getEntityPrefix(): string {
    return 'user_agg';
  }

  protected serialize(): any {
    return {
      email: this._email,
      username: this._username,
      role: this._role,
      isActive: this._isActive,
      projects: this._projects
    };
  }

  protected apply(event: DomainEvent): void {
    switch (event.eventType) {
      case 'UserCreated':
        this.applyUserCreated(event);
        break;
      case 'UserDeactivated':
        this.applyUserDeactivated(event);
        break;
    }
  }

  // Business methods
  public createUser(email: string, username: string, role: string = 'developer'): void {
    if (this._email) {
      throw new Error('User already exists');
    }

    const event = new (require('./events').UserCreatedEvent)(
      this.id,
      email,
      username,
      role
    );

    this.addDomainEvent(event);
    this.apply(event);
  }

  public deactivate(reason: string): void {
    if (!this._isActive) {
      return;
    }

    const event = new (require('./events').UserDeactivatedEvent)(
      this.id,
      reason
    );

    this.addDomainEvent(event);
    this.apply(event);
  }

  public addProject(projectId: string): void {
    if (!this._projects.includes(projectId)) {
      this._projects.push(projectId);
      this.updateVersion();
    }
  }

  // Event handlers
  private applyUserCreated(event: any): void {
    const data = event.getEventData();
    this._email = data.email;
    this._username = data.username;
    this._role = data.role;
    this._isActive = true;
  }

  private applyUserDeactivated(event: any): void {
    this._isActive = false;
  }

  // Getters
  public get email(): string { return this._email; }
  public get username(): string { return this._username; }
  public get role(): string { return this._role; }
  public get isActive(): boolean { return this._isActive; }
  public get projects(): string[] { return [...this._projects]; }
}