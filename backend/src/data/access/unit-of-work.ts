// backend/src/data/access/unit-of-work.ts
import { IDataSource, TransactionContext } from './data-source.interface';

export interface EntityState<T = any> {
  entity: T;
  state: 'new' | 'modified' | 'deleted';
  originalValues?: Partial<T>;
}

export class UnitOfWork {
  private entities = new Map<string, EntityState>();
  private context?: TransactionContext;

  constructor(private dataSource: IDataSource) {}

  registerNew<T>(table: string, entity: T): void {
    const key = this.getEntityKey(table, (entity as any).id);
    this.entities.set(key, { entity, state: 'new' });
  }

  registerModified<T>(table: string, entity: T, originalValues?: Partial<T>): void {
    const key = this.getEntityKey(table, (entity as any).id);
    this.entities.set(key, { entity, state: 'modified', originalValues });
  }

  registerDeleted<T>(table: string, entity: T): void {
    const key = this.getEntityKey(table, (entity as any).id);
    this.entities.set(key, { entity, state: 'deleted' });
  }

  async commit(): Promise<void> {
    if (this.entities.size === 0) return;

    this.context = await this.dataSource.beginTransaction();

    try {
      for (const [key, entityState] of this.entities) {
        const [table] = key.split(':');
        
        switch (entityState.state) {
          case 'new':
            this.context.operations.push({
              type: 'create',
              table,
              data: entityState.entity
            });
            break;
            
          case 'modified':
            this.context.operations.push({
              type: 'update',
              table,
              key: { PK: `${table.toUpperCase()}#${entityState.entity.id}`, SK: 'METADATA' },
              data: entityState.entity
            });
            break;
            
          case 'deleted':
            this.context.operations.push({
              type: 'delete',
              table,
              key: { PK: `${table.toUpperCase()}#${entityState.entity.id}`, SK: 'METADATA' }
            });
            break;
        }
      }

      await this.dataSource.commitTransaction(this.context);
      this.clear();

    } catch (error) {
      if (this.context) {
        await this.dataSource.rollbackTransaction(this.context);
      }
      throw error;
    }
  }

  async rollback(): Promise<void> {
    if (this.context) {
      await this.dataSource.rollbackTransaction(this.context);
    }
    this.clear();
  }

  clear(): void {
    this.entities.clear();
    this.context = undefined;
  }

  hasChanges(): boolean {
    return this.entities.size > 0;
  }

  private getEntityKey(table: string, id: string): string {
    return `${table}:${id}`;
  }
}