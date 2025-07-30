import { BaseModel } from './base.model';

export interface ProjectSettings {
  framework: string;
  language: string;
  buildTool: string;
}

export class Project extends BaseModel {
  name: string;
  description: string;
  ownerId: string;
  status: 'draft' | 'analyzing' | 'building' | 'completed' | 'failed';
  settings: ProjectSettings;
  progress: number;

  constructor(data: Partial<Project>) {
    super(data.id);
    this.name = data.name!;
    this.description = data.description!;
    this.ownerId = data.ownerId!;
    this.status = data.status || 'draft';
    this.settings = data.settings || {
      framework: 'react',
      language: 'typescript',
      buildTool: 'vite'
    };
    this.progress = data.progress || 0;
  }

  protected getEntityPrefix(): string {
    return 'proj';
  }

  protected serialize(): any {
    return {
      name: this.name,
      description: this.description,
      ownerId: this.ownerId,
      status: this.status,
      settings: this.settings,
      progress: this.progress
    };
  }

  updateStatus(status: Project['status'], progress?: number): void {
    this.status = status;
    if (progress !== undefined) {
      this.progress = progress;
    }
    this.updateVersion();
  }
}