// backend/src/llm/prompt-template.ts
export interface PromptVariable {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'array' | 'object';
  required: boolean;
  description?: string;
  default?: any;
}

export interface PromptTemplate {
  id: string;
  name: string;
  description: string;
  template: string;
  variables: PromptVariable[];
  category: string;
  tags: string[];
}

export class PromptTemplateManager {
  private templates: Map<string, PromptTemplate> = new Map();

  constructor() {
    this.initializeDefaultTemplates();
  }

  private initializeDefaultTemplates(): void {
    // Code analysis template
    this.registerTemplate({
      id: 'code-analysis',
      name: 'Code Analysis',
      description: 'Analyze code for patterns, issues, and improvements',
      template: `Analyze the following {{language}} code:

{{code}}

Please provide:
1. Code quality assessment
2. Potential issues or bugs
3. Performance considerations
4. Suggested improvements
5. Best practices recommendations

Focus on: {{focus_areas}}`,
      variables: [
        { name: 'language', type: 'string', required: true, description: 'Programming language' },
        { name: 'code', type: 'string', required: true, description: 'Code to analyze' },
        { name: 'focus_areas', type: 'array', required: false, default: ['security', 'performance', 'maintainability'] }
      ],
      category: 'development',
      tags: ['code', 'analysis', 'review']
    });

    // Requirements analysis template
    this.registerTemplate({
      id: 'requirements-analysis',
      name: 'Requirements Analysis',
      description: 'Analyze project requirements and extract technical specifications',
      template: `Analyze the following project requirements:

{{requirements}}

Extract and provide:
1. Functional requirements
2. Non-functional requirements
3. Technical constraints
4. Suggested technology stack
5. Architecture recommendations
6. Estimated complexity: {{complexity_scale}}

Project type: {{project_type}}
Target platform: {{platform}}`,
      variables: [
        { name: 'requirements', type: 'string', required: true },
        { name: 'project_type', type: 'string', required: false, default: 'web application' },
        { name: 'platform', type: 'string', required: false, default: 'web' },
        { name: 'complexity_scale', type: 'string', required: false, default: '1-10 scale' }
      ],
      category: 'analysis',
      tags: ['requirements', 'analysis', 'planning']
    });

    // Component generation template
    this.registerTemplate({
      id: 'component-generation',
      name: 'Component Generation',
      description: 'Generate code components based on specifications',
      template: `Generate a {{component_type}} component with the following specifications:

Name: {{component_name}}
Framework: {{framework}}
Language: {{language}}

Requirements:
{{requirements}}

Features needed:
{{features}}

Please provide:
1. Complete component code
2. Props/interface definitions
3. Usage examples
4. Unit tests
5. Documentation

Style: {{coding_style}}`,
      variables: [
        { name: 'component_type', type: 'string', required: true },
        { name: 'component_name', type: 'string', required: true },
        { name: 'framework', type: 'string', required: true },
        { name: 'language', type: 'string', required: true },
        { name: 'requirements', type: 'string', required: true },
        { name: 'features', type: 'array', required: true },
        { name: 'coding_style', type: 'string', required: false, default: 'clean and modular' }
      ],
      category: 'generation',
      tags: ['component', 'generation', 'code']
    });
  }

  registerTemplate(template: PromptTemplate): void {
    this.templates.set(template.id, template);
  }

  getTemplate(id: string): PromptTemplate | undefined {
    return this.templates.get(id);
  }

  renderTemplate(id: string, variables: Record<string, any>): string {
    const template = this.templates.get(id);
    if (!template) {
      throw new Error(`Template not found: ${id}`);
    }

    // Validate required variables
    const missingVars = template.variables
      .filter(v => v.required && !(v.name in variables))
      .map(v => v.name);

    if (missingVars.length > 0) {
      throw new Error(`Missing required variables: ${missingVars.join(', ')}`);
    }

    // Apply defaults
    const mergedVars = { ...variables };
    template.variables.forEach(v => {
      if (!(v.name in mergedVars) && v.default !== undefined) {
        mergedVars[v.name] = v.default;
      }
    });

    // Render template
    let rendered = template.template;
    Object.entries(mergedVars).forEach(([key, value]) => {
      const placeholder = `{{${key}}}`;
      const replacement = Array.isArray(value) ? value.join(', ') : String(value);
      rendered = rendered.replace(new RegExp(placeholder, 'g'), replacement);
    });

    return rendered;
  }

  listTemplates(category?: string): PromptTemplate[] {
    const templates = Array.from(this.templates.values());
    return category 
      ? templates.filter(t => t.category === category)
      : templates;
  }

  searchTemplates(query: string): PromptTemplate[] {
    const lowerQuery = query.toLowerCase();
    return Array.from(this.templates.values()).filter(template =>
      template.name.toLowerCase().includes(lowerQuery) ||
      template.description.toLowerCase().includes(lowerQuery) ||
      template.tags.some(tag => tag.toLowerCase().includes(lowerQuery))
    );
  }
}