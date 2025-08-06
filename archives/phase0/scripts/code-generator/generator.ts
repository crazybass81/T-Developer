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
    
    Handlebars.registerHelper('includes', (array: string[], value: string) =>
      array && array.includes(value)
    );
    
    Handlebars.registerHelper('if_eq', function(a, b, options) {
      if (a === b) {
        return options.fn(this);
      }
      return options.inverse(this);
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
        choices: ['processing', 'analysis', 'generation', 'integration']
      },
      {
        type: 'checkbox',
        name: 'capabilities',
        message: 'Select agent capabilities:',
        choices: ['database-access', 'file-operations', 'api-calls', 'llm-integration', 'caching']
      },
      {
        type: 'input',
        name: 'description',
        message: 'Agent description:'
      }
    ]);
    
    const data = {
      name,
      className: this.toPascalCase(name),
      ...answers
    };
    
    // 디렉토리 생성
    await fs.mkdir(path.join(process.cwd(), 'backend/src/agents'), { recursive: true });
    await fs.mkdir(path.join(process.cwd(), 'backend/tests/agents'), { recursive: true });
    await fs.mkdir(path.join(process.cwd(), 'docs/agents'), { recursive: true });
    
    // 파일 생성
    const agentCode = this.templateManager.render('agent', data);
    await fs.writeFile(
      path.join(process.cwd(), 'backend/src/agents', `${name}-agent.ts`),
      agentCode
    );
    
    const testCode = this.templateManager.render('agent-test', data);
    await fs.writeFile(
      path.join(process.cwd(), 'backend/tests/agents', `${name}-agent.test.ts`),
      testCode
    );
    
    const docCode = this.templateManager.render('agent-doc', data);
    await fs.writeFile(
      path.join(process.cwd(), 'docs/agents', `${name}-agent.md`),
      docCode
    );
    
    console.log(chalk.green(`✅ Agent '${name}' generated successfully!`));
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

program.parse();