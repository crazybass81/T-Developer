/**
 * Base Migration Class
 * Abstract class for database migrations
 */

import { SingleTableClient } from '../dynamodb/single-table';

export abstract class BaseMigration {
  protected client: SingleTableClient;
  public readonly id: string;
  public readonly version: string;
  public readonly description: string;
  public readonly createdAt: string;

  constructor(
    id: string,
    version: string,
    description: string,
    client: SingleTableClient
  ) {
    this.id = id;
    this.version = version;
    this.description = description;
    this.createdAt = new Date().toISOString();
    this.client = client;
  }

  public abstract up(): Promise<void>;
  public abstract down(): Promise<void>;

  protected async log(message: string): Promise<void> {
    console.log(`[Migration ${this.id}] ${message}`);
  }
}