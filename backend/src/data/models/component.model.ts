import { BaseModel } from './base.model';

export interface ComponentDependency {
  name: string;
  version: string;
  type: 'runtime' | 'dev' | 'peer';
}

export class Component extends BaseModel {
  name: string;
  version: string;
  description: string;
  type: 'library' | 'framework' | 'tool' | 'service';
  language: string;
  registry: 'npm' | 'pypi' | 'maven' | 'github';
  downloadCount: number;
  stars: number;
  lastUpdated: Date;
  dependencies: ComponentDependency[];
  tags: string[];

  constructor(data: Partial<Component>) {
    super(data.id);
    this.name = data.name!;
    this.version = data.version!;
    this.description = data.description!;
    this.type = data.type!;
    this.language = data.language!;
    this.registry = data.registry!;
    this.downloadCount = data.downloadCount || 0;
    this.stars = data.stars || 0;
    this.lastUpdated = data.lastUpdated || new Date();
    this.dependencies = data.dependencies || [];
    this.tags = data.tags || [];
  }

  protected getEntityPrefix(): string {
    return 'comp';
  }

  protected serialize(): any {
    return {
      name: this.name,
      version: this.version,
      description: this.description,
      type: this.type,
      language: this.language,
      registry: this.registry,
      downloadCount: this.downloadCount,
      stars: this.stars,
      lastUpdated: this.lastUpdated.toISOString(),
      dependencies: this.dependencies,
      tags: this.tags
    };
  }

  updateStats(downloadCount: number, stars: number): void {
    this.downloadCount = downloadCount;
    this.stars = stars;
    this.lastUpdated = new Date();
    this.updateVersion();
  }
}