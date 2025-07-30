// Base Entity for T-Developer Data Layer
export abstract class BaseEntity {
  PK: string = '';
  SK: string = '';
  EntityType: string = '';
  EntityId: string = '';
  CreatedAt: string;
  UpdatedAt: string;
  Version: number;
  
  constructor() {
    this.CreatedAt = new Date().toISOString();
    this.UpdatedAt = new Date().toISOString();
    this.Version = 1;
  }
  
  abstract toDynamoDBItem(): Record<string, any>;
  abstract fromDynamoDBItem(item: Record<string, any>): void;
  
  updateTimestamp(): void {
    this.UpdatedAt = new Date().toISOString();
    this.Version++;
  }
}