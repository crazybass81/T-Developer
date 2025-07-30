export abstract class BaseModel {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  version: number;

  constructor(id?: string) {
    this.id = id || this.generateId();
    this.createdAt = new Date();
    this.updatedAt = new Date();
    this.version = 1;
  }

  protected generateId(): string {
    return `${this.getEntityPrefix()}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  protected abstract getEntityPrefix(): string;

  updateVersion(): void {
    this.version++;
    this.updatedAt = new Date();
  }

  toJSON(): any {
    return {
      id: this.id,
      createdAt: this.createdAt.toISOString(),
      updatedAt: this.updatedAt.toISOString(),
      version: this.version,
      ...this.serialize()
    };
  }

  protected abstract serialize(): any;
}