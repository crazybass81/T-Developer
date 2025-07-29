import Handlebars from 'handlebars';
import fs from 'fs/promises';

interface Project {
  name: string;
  description: string;
  userId: string;
  techStack?: {
    database?: string;
    cloud?: string;
  };
}

export class ReadmeGenerator {
  private template: HandlebarsTemplateDelegate;
  
  constructor(templatePath: string) {
    this.loadTemplate(templatePath);
  }
  
  private async loadTemplate(templatePath: string): Promise<void> {
    const templateContent = await fs.readFile(templatePath, 'utf-8');
    this.template = Handlebars.compile(templateContent);
  }
  
  async generate(project: Project): Promise<string> {
    const context = {
      PROJECT_NAME: project.name,
      VERSION: '1.0.0',
      LICENSE: 'MIT',
      PROJECT_DESCRIPTION: project.description,
      FEATURES: this.extractFeatures(project),
      NODE_VERSION: '18',
      REQUIREMENTS: this.extractRequirements(project),
      REPOSITORY_URL: `https://github.com/${project.userId}/${project.name}`,
      PORT: 3000,
      PRODUCTION_URL: `https://api.${project.name}.com`,
      ENV_VARS: this.extractEnvVars(project)
    };
    
    return this.template(context);
  }
  
  private extractFeatures(project: Project): string[] {
    return [
      '사용자 인증 및 권한 관리',
      'RESTful API',
      '실시간 데이터 업데이트',
      '확장 가능한 아키텍처'
    ];
  }
  
  private extractRequirements(project: Project): string[] {
    const reqs = ['npm 8+'];
    
    if (project.techStack?.database) {
      reqs.push(project.techStack.database);
    }
    
    if (project.techStack?.cloud === 'aws') {
      reqs.push('AWS CLI');
    }
    
    return reqs;
  }
  
  private extractEnvVars(project: Project): any[] {
    return [
      { NAME: 'NODE_ENV', DESCRIPTION: '실행 환경', DEFAULT: 'development' },
      { NAME: 'PORT', DESCRIPTION: '서버 포트', DEFAULT: '3000' },
      { NAME: 'DATABASE_URL', DESCRIPTION: '데이터베이스 연결 URL', DEFAULT: 'N/A' }
    ];
  }
}