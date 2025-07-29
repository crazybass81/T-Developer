import { Command } from 'commander';
import inquirer from 'inquirer';
import { promises as fs } from 'fs';
import path from 'path';
import Handlebars from 'handlebars';
import chalk from 'chalk';

// 템플릿 매니저
class TemplateManager {
  private templatesDir = path.join(__dirname, 'templates');
  private templates: Map<string, HandlebarsTemplateDelegate> = new Map();
  
  async loadTemplates(): Promise<void> {
    try {
      await fs.mkdir(this.templatesDir, { recursive: true });
      const templateFiles = await fs.readdir(this.templatesDir);
      
      for (const file of templateFiles) {
        if (file.endsWith('.hbs')) {
          const name = path.basename(file, '.hbs');
          const content = await fs.readFile(
            path.join(this.templatesDir, file),
            'utf-8'
          );
          this.templates.set(name, Handlebars.compile(content));
        }
      }
    } catch (error) {
      console.log(chalk.yellow('Templates directory not found, creating basic templates...'));
      await this.createBasicTemplates();
    }
    
    this.registerHelpers();
  }
  
  private registerHelpers(): void {
    Handlebars.registerHelper('camelCase', (str: string) => 
      str.replace(/-./g, x => x[1].toUpperCase())
    );
    
    Handlebars.registerHelper('pascalCase', (str: string) => {
      const camel = str.replace(/-./g, x => x[1].toUpperCase());
      return camel.charAt(0).toUpperCase() + camel.slice(1);
    });
    
    Handlebars.registerHelper('kebabCase', (str: string) =>
      str.replace(/[A-Z]/g, letter => `-${letter.toLowerCase()}`).replace(/^-/, '')
    );
    
    Handlebars.registerHelper('if_eq', function(a, b, options) {
      if (a === b) {
        return options.fn(this);
      }
      return options.inverse(this);
    });
  }
  
  private async createBasicTemplates(): Promise<void> {
    const agentTemplate = `import { BaseAgent } from '../framework/base-agent';
import { logger } from '../../config/logger';

/**
 * {{description}}
 */
export class {{pascalCase name}}Agent extends BaseAgent {
  static readonly AGENT_NAME = '{{name}}';
  static readonly AGENT_TYPE = '{{type}}';
  
  constructor() {
    super(
      {{pascalCase name}}Agent.AGENT_NAME,
      '1.0.0',
      logger
    );
  }
  
  protected initialize(): void {
    this.registerCapability({
      name: '{{name}}-process',
      description: '{{description}}',
      inputSchema: {},
      outputSchema: {},
      version: '1.0.0'
    });
  }
  
  protected async process(message: any): Promise<any> {
    // TODO: Implement {{type}} agent logic
    return {
      success: true,
      data: message.payload,
      agentName: this.name
    };
  }
}`;

    await fs.writeFile(
      path.join(this.templatesDir, 'agent.hbs'),
      agentTemplate
    );
    
    this.templates.set('agent', Handlebars.compile(agentTemplate));
  }
  
  render(templateName: string, data: any): string {
    const template = this.templates.get(templateName);
    if (!template) {
      throw new Error(`Template '${templateName}' not found`);
    }
    return template(data);
  }
}

// 코드 생성기
class CodeGenerator {
  private templateManager = new TemplateManager();
  
  async initialize(): Promise<void> {
    await this.templateManager.loadTemplates();
  }
  
  async generateAgent(name: string): Promise<void> {
    const answers = await inquirer.prompt([
      {
        type: 'list',
        name: 'type',
        message: 'Select agent type:',
        choices: [
          'processing',
          'analysis', 
          'generation',
          'integration'
        ]
      },
      {
        type: 'input',
        name: 'description',
        message: 'Agent description:',
        default: `${name} agent for T-Developer`
      }
    ]);
    
    const data = {
      name,
      ...answers
    };
    
    // 에이전트 디렉토리 생성
    const agentDir = path.join(process.cwd(), 'backend/src/agents');
    await fs.mkdir(agentDir, { recursive: true });
    
    // 에이전트 파일 생성
    const agentCode = this.templateManager.render('agent', data);
    const agentPath = path.join(agentDir, `${name}-agent.ts`);
    
    await fs.writeFile(agentPath, agentCode);
    
    console.log(chalk.green(`✅ Agent '${name}' generated successfully!`));
    console.log(chalk.blue('Generated files:'));
    console.log(`  - ${agentPath}`);
  }
  
  async generateAPI(resource: string): Promise<void> {
    const answers = await inquirer.prompt([
      {
        type: 'checkbox',
        name: 'methods',
        message: 'Select HTTP methods:',
        choices: ['GET', 'POST', 'PUT', 'DELETE'],
        default: ['GET', 'POST']
      }
    ]);
    
    // API 디렉토리 생성
    const apiDir = path.join(process.cwd(), 'backend/src/api');
    await fs.mkdir(path.join(apiDir, 'controllers'), { recursive: true });
    await fs.mkdir(path.join(apiDir, 'routes'), { recursive: true });
    
    // 컨트롤러 생성
    const controllerCode = `import { Request, Response } from 'express';
import { logger } from '../../config/logger';

export class ${this.toPascalCase(resource)}Controller {
  ${answers.methods.includes('GET') ? `
  async get${this.toPascalCase(resource)}(req: Request, res: Response): Promise<void> {
    try {
      // TODO: Implement GET logic
      res.json({ message: 'GET ${resource}' });
    } catch (error) {
      logger.error('Error getting ${resource}:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }` : ''}
  
  ${answers.methods.includes('POST') ? `
  async create${this.toPascalCase(resource)}(req: Request, res: Response): Promise<void> {
    try {
      // TODO: Implement POST logic
      res.status(201).json({ message: 'Created ${resource}' });
    } catch (error) {
      logger.error('Error creating ${resource}:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }` : ''}
}`;
    
    const controllerPath = path.join(apiDir, 'controllers', `${resource}.controller.ts`);
    await fs.writeFile(controllerPath, controllerCode);
    
    // 라우트 생성
    const routeCode = `import { Router } from 'express';
import { ${this.toPascalCase(resource)}Controller } from '../controllers/${resource}.controller';

const router = Router();
const controller = new ${this.toPascalCase(resource)}Controller();

${answers.methods.includes('GET') ? `router.get('/', controller.get${this.toPascalCase(resource)}.bind(controller));` : ''}
${answers.methods.includes('POST') ? `router.post('/', controller.create${this.toPascalCase(resource)}.bind(controller));` : ''}

export default router;`;
    
    const routePath = path.join(apiDir, 'routes', `${resource}.routes.ts`);
    await fs.writeFile(routePath, routeCode);
    
    console.log(chalk.green(`✅ API endpoint '${resource}' generated successfully!`));
    console.log(chalk.blue('Generated files:'));
    console.log(`  - ${controllerPath}`);
    console.log(`  - ${routePath}`);
  }
  
  private toPascalCase(str: string): string {
    return str
      .split(/[-_]/)
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join('');
  }
}

// CLI 설정
const program = new Command();
const generator = new CodeGenerator();

program
  .name('t-dev-gen')
  .description('T-Developer code generator')
  .version('1.0.0');

program
  .command('agent <name>')
  .description('Generate a new agent')
  .action(async (name) => {
    await generator.initialize();
    await generator.generateAgent(name);
  });

program
  .command('api <resource>')
  .description('Generate API endpoint')
  .action(async (resource) => {
    await generator.initialize();
    await generator.generateAPI(resource);
  });

if (require.main === module) {
  program.parse();
}

export { CodeGenerator };