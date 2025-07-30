export { BaseModel } from './base.model';
export { User, UserPreferences } from './user.model';
export { Project, ProjectSettings, ProjectMetadata } from './project.model';
export { Agent, AgentConfiguration, AgentMetrics } from './agent.model';
export { Component, ComponentDependency, ComponentMetadata } from './component.model';
export { Session, SessionContext } from './session.model';

// Domain model types
export type EntityType = 'user' | 'project' | 'agent' | 'component' | 'session';

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
}

export interface ModelFactory<T extends BaseModel> {
  create(data: Partial<T>): T;
  validate(data: Partial<T>): ValidationResult;
}

// Model factories
export class UserFactory implements ModelFactory<User> {
  create(data: Partial<User>): User {
    return new User(data);
  }

  validate(data: Partial<User>): ValidationResult {
    const errors: string[] = [];
    if (!data.email) errors.push('Email is required');
    if (!data.username) errors.push('Username is required');
    if (data.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
      errors.push('Invalid email format');
    }
    return { isValid: errors.length === 0, errors };
  }
}

export class ProjectFactory implements ModelFactory<Project> {
  create(data: Partial<Project>): Project {
    return new Project(data);
  }

  validate(data: Partial<Project>): ValidationResult {
    const errors: string[] = [];
    if (!data.name) errors.push('Project name is required');
    if (!data.description) errors.push('Project description is required');
    if (!data.ownerId) errors.push('Owner ID is required');
    return { isValid: errors.length === 0, errors };
  }
}