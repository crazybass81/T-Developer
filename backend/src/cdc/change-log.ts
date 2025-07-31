import { ChangeEvent } from './change-capture';

export interface ChangeLogEntry {
  id: string;
  timestamp: Date;
  tableName: string;
  operation: string;
  entityId: string;
  changes: FieldChange[];
  metadata: Record<string, any>;
}

export interface FieldChange {
  field: string;
  oldValue: any;
  newValue: any;
  changeType: 'added' | 'modified' | 'removed';
}

export class ChangeLogger {
  private logs: ChangeLogEntry[] = [];
  private maxEntries = 10000;

  logChange(event: ChangeEvent): ChangeLogEntry {
    const entry: ChangeLogEntry = {
      id: event.id,
      timestamp: event.timestamp,
      tableName: event.tableName,
      operation: event.eventName,
      entityId: this.extractEntityId(event.keys),
      changes: this.calculateChanges(event.oldImage, event.newImage),
      metadata: {
        sequenceNumber: event.sequenceNumber
      }
    };

    this.logs.push(entry);
    
    // Maintain size limit
    if (this.logs.length > this.maxEntries) {
      this.logs.shift();
    }

    return entry;
  }

  private extractEntityId(keys: Record<string, any>): string {
    return keys.PK?.S || keys.id?.S || 'unknown';
  }

  private calculateChanges(oldImage?: Record<string, any>, newImage?: Record<string, any>): FieldChange[] {
    const changes: FieldChange[] = [];
    
    if (!oldImage && newImage) {
      // INSERT - all fields are new
      Object.keys(newImage).forEach(field => {
        changes.push({
          field,
          oldValue: null,
          newValue: this.extractValue(newImage[field]),
          changeType: 'added'
        });
      });
    } else if (oldImage && newImage) {
      // MODIFY - compare fields
      const allFields = new Set([...Object.keys(oldImage), ...Object.keys(newImage)]);
      
      allFields.forEach(field => {
        const oldVal = this.extractValue(oldImage[field]);
        const newVal = this.extractValue(newImage[field]);
        
        if (oldVal === undefined && newVal !== undefined) {
          changes.push({ field, oldValue: null, newValue: newVal, changeType: 'added' });
        } else if (oldVal !== undefined && newVal === undefined) {
          changes.push({ field, oldValue: oldVal, newValue: null, changeType: 'removed' });
        } else if (JSON.stringify(oldVal) !== JSON.stringify(newVal)) {
          changes.push({ field, oldValue: oldVal, newValue: newVal, changeType: 'modified' });
        }
      });
    } else if (oldImage && !newImage) {
      // REMOVE - all fields removed
      Object.keys(oldImage).forEach(field => {
        changes.push({
          field,
          oldValue: this.extractValue(oldImage[field]),
          newValue: null,
          changeType: 'removed'
        });
      });
    }

    return changes;
  }

  private extractValue(dynamoValue: any): any {
    if (!dynamoValue) return undefined;
    
    if (dynamoValue.S) return dynamoValue.S;
    if (dynamoValue.N) return Number(dynamoValue.N);
    if (dynamoValue.BOOL) return dynamoValue.BOOL;
    if (dynamoValue.M) return dynamoValue.M;
    if (dynamoValue.L) return dynamoValue.L;
    
    return dynamoValue;
  }

  getChangesForEntity(entityId: string, limit = 100): ChangeLogEntry[] {
    return this.logs
      .filter(entry => entry.entityId === entityId)
      .slice(-limit);
  }

  getChangesSince(timestamp: Date): ChangeLogEntry[] {
    return this.logs.filter(entry => entry.timestamp >= timestamp);
  }

  getChangesForTable(tableName: string, limit = 100): ChangeLogEntry[] {
    return this.logs
      .filter(entry => entry.tableName === tableName)
      .slice(-limit);
  }
}

export class ChangeAggregator {
  private aggregates: Map<string, any> = new Map();

  processChange(entry: ChangeLogEntry): void {
    const key = `${entry.tableName}:${entry.operation}`;
    
    if (!this.aggregates.has(key)) {
      this.aggregates.set(key, {
        count: 0,
        lastSeen: entry.timestamp,
        entities: new Set()
      });
    }

    const aggregate = this.aggregates.get(key)!;
    aggregate.count++;
    aggregate.lastSeen = entry.timestamp;
    aggregate.entities.add(entry.entityId);
  }

  getAggregates(): Record<string, any> {
    const result: Record<string, any> = {};
    
    this.aggregates.forEach((value, key) => {
      result[key] = {
        ...value,
        entities: value.entities.size
      };
    });

    return result;
  }

  reset(): void {
    this.aggregates.clear();
  }
}