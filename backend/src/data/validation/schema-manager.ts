import { UserValidator } from './user.validator';
import { ProjectValidator } from './project.validator';
import { AgentValidator } from './agent.validator';
import { ValidationResult } from './base.validator';

export interface SchemaVersion {
  version: string;
  timestamp: Date;
  changes: SchemaChange[];
}

export interface SchemaChange {
  type: 'add' | 'remove' | 'modify';
  field: string;
  description: string;
}

export class SchemaManager {
  private validators = new Map<string, any>();
  private versions: SchemaVersion[] = [];

  constructor() {
    this.initializeValidators();
    this.loadSchemaVersions();
  }

  private initializeValidators(): void {
    this.validators.set('User', new UserValidator());
    this.validators.set('Project', new ProjectValidator());
    this.validators.set('Agent', new AgentValidator());
  }

  validate<T>(entityType: string, data: T): ValidationResult {
    const validator = this.validators.get(entityType);
    if (!validator) {
      throw new Error(`No validator found for entity type: ${entityType}`);
    }
    return validator.validate(data);
  }

  async validateAsync<T>(entityType: string, data: T): Promise<ValidationResult> {
    const validator = this.validators.get(entityType);
    if (!validator) {
      throw new Error(`No validator found for entity type: ${entityType}`);
    }
    return validator.validateAsync(data);
  }

  sanitize<T>(entityType: string, data: T): T {
    const validator = this.validators.get(entityType);
    if (!validator) {
      throw new Error(`No validator found for entity type: ${entityType}`);
    }
    return validator.sanitize(data);
  }

  addSchemaVersion(version: SchemaVersion): void {
    this.versions.push(version);
    this.versions.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
  }

  getCurrentVersion(): string {
    return this.versions[0]?.version || '1.0.0';
  }

  getVersionHistory(): SchemaVersion[] {
    return [...this.versions];
  }

  validateBatch<T>(entityType: string, items: T[]): ValidationResult[] {
    return items.map(item => this.validate(entityType, item));
  }

  private loadSchemaVersions(): void {
    // Initial schema version
    this.addSchemaVersion({
      version: '1.0.0',
      timestamp: new Date(),
      changes: [
        { type: 'add', field: 'User', description: 'Initial user model' },
        { type: 'add', field: 'Project', description: 'Initial project model' },
        { type: 'add', field: 'Agent', description: 'Initial agent model' }
      ]
    });
  }

  migrateSchema(fromVersion: string, toVersion: string, data: any): any {
    // Schema migration logic would go here
    // For now, return data as-is
    return data;
  }
}