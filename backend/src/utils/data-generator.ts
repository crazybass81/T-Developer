import { faker } from '@faker-js/faker';
import { DynamoDBDocumentClient, PutCommand } from '@aws-sdk/lib-dynamodb';

export class DevelopmentDataGenerator {
  constructor(private docClient: DynamoDBDocumentClient) {}
  
  async generateProjects(count: number = 50): Promise<void> {
    const projects = [];
    
    for (let i = 0; i < count; i++) {
      const project = {
        id: `proj_${faker.string.uuid()}`,
        userId: `user_${faker.string.uuid()}`,
        name: this.generateProjectName(),
        description: this.generateProjectDescription(),
        projectType: faker.helpers.arrayElement(['web', 'api', 'mobile', 'desktop', 'cli']),
        status: this.generateWeightedStatus(),
        createdAt: faker.date.past({ years: 1 }).toISOString(),
        updatedAt: faker.date.recent({ days: 30 }).toISOString(),
        
        techStack: {
          frontend: faker.helpers.arrayElement(['react', 'vue', 'angular', 'svelte', null]),
          backend: faker.helpers.arrayElement(['node', 'python', 'java', 'go', null]),
          database: faker.helpers.arrayElement(['postgres', 'mysql', 'mongodb', 'dynamodb']),
          cloud: faker.helpers.arrayElement(['aws', 'gcp', 'azure', 'vercel'])
        },
        
        agentExecutions: this.generateAgentExecutions(),
        
        metrics: {
          buildTime: faker.number.int({ min: 30, max: 600 }),
          totalCost: faker.number.float({ min: 0.01, max: 10.00, fractionDigits: 2 }),
          componentsUsed: faker.number.int({ min: 5, max: 50 }),
          linesOfCode: faker.number.int({ min: 1000, max: 50000 })
        }
      };
      
      projects.push(project);
    }
    
    for (const project of projects) {
      await this.docClient.send(new PutCommand({
        TableName: 'T-Developer-Projects',
        Item: project
      }));
    }
    
    console.log(`✅ ${count}개의 프로젝트 데이터 생성 완료`);
  }
  
  private generateProjectName(): string {
    const templates = [
      () => `${faker.commerce.productAdjective()} ${faker.hacker.noun()} Platform`,
      () => `${faker.company.buzzNoun()} Management System`,
      () => `${faker.hacker.adjective()} ${faker.hacker.noun()} API`,
      () => `${faker.commerce.product()} Tracker`,
      () => `${faker.company.buzzAdjective()} Analytics Dashboard`
    ];
    
    return faker.helpers.arrayElement(templates)();
  }
  
  private generateProjectDescription(): string {
    const intros = [
      'A modern web application that',
      'An innovative platform designed to',
      'A comprehensive solution for',
      'A cutting-edge system that'
    ];
    
    const actions = [
      'streamlines business processes',
      'enhances user engagement',
      'automates workflow management',
      'provides real-time analytics',
      'optimizes resource allocation'
    ];
    
    const benefits = [
      'increasing productivity by up to 40%',
      'reducing operational costs',
      'improving customer satisfaction',
      'enabling data-driven decisions',
      'facilitating team collaboration'
    ];
    
    return `${faker.helpers.arrayElement(intros)} ${faker.helpers.arrayElement(actions)}, ${faker.helpers.arrayElement(benefits)}.`;
  }
  
  private generateWeightedStatus(): string {
    const weights = {
      'completed': 0.6,
      'building': 0.2,
      'testing': 0.1,
      'analyzing': 0.05,
      'error': 0.05
    };
    
    const random = Math.random();
    let cumulative = 0;
    
    for (const [status, weight] of Object.entries(weights)) {
      cumulative += weight;
      if (random < cumulative) {
        return status;
      }
    }
    
    return 'completed';
  }
  
  private generateAgentExecutions(): any[] {
    const agents = [
      'nl-input', 'ui-selection', 'parsing', 'component-decision',
      'matching-rate', 'search', 'generation', 'assembly', 'download'
    ];
    
    return agents.map((agent, index) => ({
      agentName: agent,
      executionTime: faker.number.int({ min: 100, max: 5000 }),
      status: index < 7 ? 'completed' : faker.helpers.arrayElement(['completed', 'running', 'pending']),
      tokensUsed: faker.number.int({ min: 100, max: 10000 })
    }));
  }
  
  async generateComponents(count: number = 200): Promise<void> {
    const components = [];
    
    const componentTypes = {
      'authentication': ['login-form', 'oauth-provider', 'jwt-handler', 'session-manager'],
      'database': ['orm-wrapper', 'query-builder', 'migration-tool', 'connection-pool'],
      'ui': ['data-table', 'chart-library', 'form-builder', 'modal-system'],
      'api': ['rest-client', 'graphql-resolver', 'rate-limiter', 'api-gateway'],
      'utility': ['logger', 'validator', 'error-handler', 'config-manager']
    };
    
    for (let i = 0; i < count; i++) {
      const category = faker.helpers.objectKey(componentTypes);
      const componentName = faker.helpers.arrayElement(componentTypes[category]);
      
      const component = {
        id: `comp_${faker.string.uuid()}`,
        name: `${faker.company.buzzAdjective()}-${componentName}`,
        category,
        version: faker.system.semver(),
        language: faker.helpers.arrayElement(['javascript', 'typescript', 'python', 'java']),
        framework: faker.helpers.arrayElement(['react', 'vue', 'express', 'fastapi', 'spring']),
        
        qualityScore: faker.number.float({ min: 3.0, max: 5.0, fractionDigits: 1 }),
        downloads: faker.number.int({ min: 100, max: 1000000 }),
        stars: faker.number.int({ min: 10, max: 50000 }),
        issues: faker.number.int({ min: 0, max: 100 }),
        
        author: faker.person.fullName(),
        license: faker.helpers.arrayElement(['MIT', 'Apache-2.0', 'GPL-3.0', 'BSD-3-Clause']),
        lastUpdated: faker.date.recent({ days: 90 }).toISOString(),
        description: faker.lorem.sentence(),
        keywords: faker.lorem.words(5).split(' '),
        
        dependencies: this.generateDependencies(),
        
        usageStats: {
          projects: faker.number.int({ min: 1, max: 1000 }),
          successRate: faker.number.float({ min: 85, max: 100, fractionDigits: 1 }),
          avgIntegrationTime: faker.number.int({ min: 5, max: 60 })
        }
      };
      
      components.push(component);
    }
    
    for (const component of components) {
      await this.docClient.send(new PutCommand({
        TableName: 'T-Developer-Components',
        Item: component
      }));
    }
    
    console.log(`✅ ${count}개의 컴포넌트 데이터 생성 완료`);
  }
  
  private generateDependencies(): Record<string, string> {
    const deps: Record<string, string> = {};
    const count = faker.number.int({ min: 0, max: 10 });
    
    const commonDeps = [
      'lodash', 'axios', 'express', 'react', 'vue',
      'moment', 'uuid', 'bcrypt', 'jsonwebtoken', 'dotenv'
    ];
    
    for (let i = 0; i < count; i++) {
      const dep = faker.helpers.arrayElement(commonDeps);
      deps[dep] = `^${faker.system.semver()}`;
    }
    
    return deps;
  }
}