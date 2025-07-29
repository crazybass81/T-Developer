import { Command } from 'commander';
import inquirer from 'inquirer';
import { promises as fs } from 'fs';
import path from 'path';
import Handlebars from 'handlebars';
import chalk from 'chalk';

class TemplateManager {
  private templates: Map<string, HandlebarsTemplateDelegate> = new Map();
  
  async loadTemplates(): Promise<void> {
    this.registerHelpers();
    this.loadInlineTemplates();
  }
  
  private registerHelpers(): void {
    Handlebars.registerHelper('camelCase', (str: string) => 
      str.replace(/-./g, x => x[1].toUpperCase())
    );
    
    Handlebars.registerHelper('pascalCase', (str: string) => {
      const camel = str.replace(/-./g, x => x[1].toUpperCase());
      return camel.charAt(0).toUpperCase() + camel.slice(1);
    });
    
    Handlebars.registerHelper('if_eq', function(a, b, options) {
      if (a === b) {
        return options.fn(this);
      }
      return options.inverse(this);
    });
    
    Handlebars.registerHelper('includes', function(array, value) {
      return array && array.includes(value);
    });
  }
  
  private loadInlineTemplates(): void {
    const templates = {
      'agent': `export class {{className}}Agent {
  static readonly AGENT_NAME = '{{name}}';
  static readonly AGENT_TYPE = '{{type}}';
  
  constructor() {
    console.log('Initializing {{name}} agent');
  }
  
  async execute(input: any): Promise<any> {
    console.log(\`Executing \${{{className}}Agent.AGENT_NAME} agent\`, { input });
    
    try {
      this.validateInput(input);
      const result = await this.process(input);
      
      return {
        success: true,
        data: result,
        metadata: {
          agentName: {{className}}Agent.AGENT_NAME,
          executionTime: Date.now(),
          version: '1.0.0'
        }
      };
      
    } catch (error) {
      console.error(\`Error in \${{{className}}Agent.AGENT_NAME} agent\`, error);
      throw error;
    }
  }
  
  private validateInput(input: any): void {
    if (!input) {
      throw new Error('Input is required');
    }
  }
  
  private async process(input: any): Promise<any> {
    {{#if_eq type 'processing'}}
    return this.processData(input);
    {{/if_eq}}
    {{#if_eq type 'analysis'}}
    return this.analyzeData(input);
    {{/if_eq}}
    {{#if_eq type 'generation'}}
    return this.generateOutput(input);
    {{/if_eq}}
    {{#if_eq type 'integration'}}
    return this.integrateServices(input);
    {{/if_eq}}
  }
  
  {{#if_eq type 'processing'}}
  private async processData(data: any): Promise<any> {
    // TODO: Implement data processing
    return { processed: data };
  }
  {{/if_eq}}
  
  {{#if_eq type 'analysis'}}
  private async analyzeData(data: any): Promise<any> {
    // TODO: Implement data analysis
    return { analyzed: true, data };
  }
  {{/if_eq}}
  
  {{#if_eq type 'generation'}}
  private async generateOutput(input: any): Promise<any> {
    // TODO: Implement output generation
    return { generated: true, input };
  }
  {{/if_eq}}
  
  {{#if_eq type 'integration'}}
  private async integrateServices(input: any): Promise<any> {
    // TODO: Implement service integration
    return { integrated: true, input };
  }
  {{/if_eq}}
}`,
      
      'controller': `import { Request, Response } from 'express';
import { {{resourceName}}Service } from '../services/{{resource}}.service';

export class {{resourceName}}Controller {
  private {{resource}}Service = new {{resourceName}}Service();
  
  {{#if (includes methods 'GET')}}
  async getAll(req: Request, res: Response): Promise<void> {
    try {
      {{#if pagination}}
      const page = parseInt(req.query.page as string) || 1;
      const limit = parseInt(req.query.limit as string) || 10;
      const result = await this.{{resource}}Service.findAll({ page, limit });
      {{else}}
      const result = await this.{{resource}}Service.findAll();
      {{/if}}
      
      res.json(result);
    } catch (error) {
      res.status(500).json({ error: (error as Error).message });
    }
  }
  
  async getById(req: Request, res: Response): Promise<void> {
    try {
      const result = await this.{{resource}}Service.findById(req.params.id);
      if (!result) {
        res.status(404).json({ error: '{{resourceName}} not found' });
        return;
      }
      res.json(result);
    } catch (error) {
      res.status(500).json({ error: (error as Error).message });
    }
  }
  {{/if}}
  
  {{#if (includes methods 'POST')}}
  async create(req: Request, res: Response): Promise<void> {
    try {
      const result = await this.{{resource}}Service.create(req.body);
      res.status(201).json(result);
    } catch (error) {
      res.status(400).json({ error: (error as Error).message });
    }
  }
  {{/if}}
  
  {{#if (includes methods 'PUT')}}
  async update(req: Request, res: Response): Promise<void> {
    try {
      const result = await this.{{resource}}Service.update(req.params.id, req.body);
      if (!result) {
        res.status(404).json({ error: '{{resourceName}} not found' });
        return;
      }
      res.json(result);
    } catch (error) {
      res.status(400).json({ error: (error as Error).message });
    }
  }
  {{/if}}
  
  {{#if (includes methods 'DELETE')}}
  async delete(req: Request, res: Response): Promise<void> {
    try {
      const result = await this.{{resource}}Service.delete(req.params.id);
      if (!result) {
        res.status(404).json({ error: '{{resourceName}} not found' });
        return;
      }
      res.status(204).send();
    } catch (error) {
      res.status(500).json({ error: (error as Error).message });
    }
  }
  {{/if}}
}`,
      
      'service': `export class {{resourceName}}Service {
  async findAll({{#if pagination}}options?: { page: number; limit: number }{{/if}}): Promise<any> {
    // TODO: Implement database query
    {{#if pagination}}
    const { page = 1, limit = 10 } = options || {};
    return {
      data: [],
      pagination: { page, limit, total: 0 }
    };
    {{else}}
    return [];
    {{/if}}
  }
  
  async findById(id: string): Promise<any> {
    // TODO: Implement database query
    return { id, name: 'Sample {{resourceName}}' };
  }
  
  async create(data: any): Promise<any> {
    // TODO: Implement database insert
    return { id: 'generated-id', ...data };
  }
  
  async update(id: string, data: any): Promise<any> {
    // TODO: Implement database update
    return { id, ...data };
  }
  
  async delete(id: string): Promise<boolean> {
    // TODO: Implement database delete
    return true;
  }
}`,
      
      'route': `import { Router } from 'express';
import { {{resourceName}}Controller } from '../controllers/{{resource}}.controller';
{{#if authentication}}
// import { authMiddleware } from '../middleware/auth';
{{/if}}

const router = Router();
const controller = new {{resourceName}}Controller();

{{#if authentication}}
// router.use(authMiddleware);
{{/if}}

{{#if (includes methods 'GET')}}
router.get('/', controller.getAll.bind(controller));
router.get('/:id', controller.getById.bind(controller));
{{/if}}

{{#if (includes methods 'POST')}}
router.post('/', controller.create.bind(controller));
{{/if}}

{{#if (includes methods 'PUT')}}
router.put('/:id', controller.update.bind(controller));
{{/if}}

{{#if (includes methods 'DELETE')}}
router.delete('/:id', controller.delete.bind(controller));
{{/if}}

export default router;`
    };
    
    Object.entries(templates).forEach(([name, template]) => {
      this.templates.set(name, Handlebars.compile(template));
    });
  }
  
  render(templateName: string, data: any): string {
    const template = this.templates.get(templateName);
    if (!template) {
      throw new Error(`Template '${templateName}' not found`);
    }
    return template(data);
  }
}

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
        choices: ['processing', 'analysis', 'generation', 'integration']
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
      className: this.toPascalCase(name),
      ...answers
    };
    
    const agentCode = this.templateManager.render('agent', data);
    const agentPath = path.join(process.cwd(), 'backend/src/agents', `${name}-agent.ts`);
    
    await fs.mkdir(path.dirname(agentPath), { recursive: true });
    await fs.writeFile(agentPath, agentCode);
    
    console.log(chalk.green(`✅ Agent '${name}' generated successfully!`));
    console.log(chalk.blue(`Generated: ${agentPath}`));
  }
  
  async generateEndpoint(resource: string): Promise<void> {
    const answers = await inquirer.prompt([
      {
        type: 'checkbox',
        name: 'methods',
        message: 'Select HTTP methods:',
        choices: ['GET', 'POST', 'PUT', 'DELETE'],
        default: ['GET', 'POST', 'PUT', 'DELETE']
      },
      {
        type: 'confirm',
        name: 'authentication',
        message: 'Require authentication?',
        default: true
      },
      {
        type: 'confirm',
        name: 'pagination',
        message: 'Include pagination?',
        default: true
      }
    ]);
    
    const data = {
      resource,
      resourceName: this.toPascalCase(resource),
      ...answers
    };
    
    const files = [
      { template: 'controller', path: `backend/src/controllers/${resource}.controller.ts` },
      { template: 'service', path: `backend/src/services/${resource}.service.ts` },
      { template: 'route', path: `backend/src/routes/${resource}.routes.ts` }
    ];
    
    for (const file of files) {
      const code = this.templateManager.render(file.template, data);
      const filePath = path.join(process.cwd(), file.path);
      
      await fs.mkdir(path.dirname(filePath), { recursive: true });
      await fs.writeFile(filePath, code);
      
      console.log(chalk.blue(`Generated: ${filePath}`));
    }
    
    console.log(chalk.green(`✅ API endpoint '${resource}' generated successfully!`));
  }
  
  private toPascalCase(str: string): string {
    return str
      .split(/[-_]/)
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join('');
  }
}

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
    await generator.generateEndpoint(resource);
  });

program.parse();

export { CodeGenerator };