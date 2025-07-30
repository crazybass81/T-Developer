// backend/src/data/access/data-source.interface.ts
export interface QueryOptions {
  limit?: number;
  offset?: number;
  sort?: { field: string; direction: 'asc' | 'desc' }[];
  filters?: Record<string, any>;
  projection?: string[];
}

export interface QueryResult<T> {
  items: T[];
  totalCount: number;
  hasMore: boolean;
  cursor?: string;
}

export interface TransactionContext {
  id: string;
  operations: TransactionOperation[];
}

export interface TransactionOperation {
  type: 'create' | 'update' | 'delete';
  table: string;
  key?: any;
  data?: any;
  conditions?: Record<string, any>;
}

export interface IDataSource {
  // Basic CRUD
  findById<T>(table: string, id: string): Promise<T | null>;
  findMany<T>(table: string, options?: QueryOptions): Promise<QueryResult<T>>;
  create<T>(table: string, data: T): Promise<T>;
  update<T>(table: string, id: string, data: Partial<T>): Promise<T>;
  delete(table: string, id: string): Promise<boolean>;
  
  // Batch operations
  batchCreate<T>(table: string, items: T[]): Promise<T[]>;
  batchUpdate<T>(table: string, updates: Array<{ id: string; data: Partial<T> }>): Promise<T[]>;
  batchDelete(table: string, ids: string[]): Promise<number>;
  
  // Transactions
  beginTransaction(): Promise<TransactionContext>;
  commitTransaction(context: TransactionContext): Promise<void>;
  rollbackTransaction(context: TransactionContext): Promise<void>;
  
  // Query building
  query<T>(table: string): IQueryBuilder<T>;
  
  // Health check
  isHealthy(): Promise<boolean>;
}

export interface IQueryBuilder<T> {
  where(field: string, operator: string, value: any): IQueryBuilder<T>;
  whereIn(field: string, values: any[]): IQueryBuilder<T>;
  whereBetween(field: string, start: any, end: any): IQueryBuilder<T>;
  orderBy(field: string, direction?: 'asc' | 'desc'): IQueryBuilder<T>;
  limit(count: number): IQueryBuilder<T>;
  offset(count: number): IQueryBuilder<T>;
  select(fields: string[]): IQueryBuilder<T>;
  execute(): Promise<QueryResult<T>>;
  first(): Promise<T | null>;
  count(): Promise<number>;
}