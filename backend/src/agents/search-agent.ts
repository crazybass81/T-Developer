/**
 * Search Agent - 코드 템플릿 및 외부 리소스 검색
 * Match Rate Agent의 결과를 받아 실제 코드 구현을 위한 검색 수행
 */

import { MatchRateResult } from './match-rate-agent';
import { ComponentDecision } from './component-decision-agent';

export interface SearchResult {
  componentName: string;
  codeTemplate: string;
  imports: string[];
  dependencies: string[];
  documentation: string;
  examples: string[];
  relatedFiles: RelatedFile[];
  searchScore: number;
}

export interface RelatedFile {
  path: string;
  type: 'style' | 'test' | 'type' | 'config';
  content: string;
  description: string;
}

export interface CodeSnippet {
  id: string;
  title: string;
  code: string;
  language: string;
  framework: string;
  tags: string[];
  score: number;
}

export class SearchAgent {
  private name = 'Search Agent';
  private codeDatabase: Map<string, CodeSnippet[]>;

  constructor() {
    this.codeDatabase = this.initializeCodeDatabase();
  }

  /**
   * Match Rate 결과를 기반으로 코드 템플릿 검색
   */
  async searchCodeTemplates(
    matchRateResults: MatchRateResult[],
    componentDecisions: ComponentDecision[]
  ): Promise<SearchResult[]> {
    console.log(`[${this.name}] Searching code templates for ${matchRateResults.length} components`);

    const results: SearchResult[] = [];

    for (let i = 0; i < matchRateResults.length; i++) {
      const matchResult = matchRateResults[i];
      const decision = componentDecisions[i];
      
      const searchResult = await this.searchForComponent(matchResult, decision);
      results.push(searchResult);
    }

    return results;
  }

  private async searchForComponent(
    matchResult: MatchRateResult,
    decision: ComponentDecision
  ): Promise<SearchResult> {
    const { componentName, bestMatch, recommendedAction } = matchResult;

    let codeTemplate = '';
    let imports: string[] = [];
    let dependencies: string[] = [];
    let documentation = '';
    let examples: string[] = [];
    let searchScore = 0;

    switch (recommendedAction) {
      case 'use-library':
        const libraryResult = await this.searchLibraryComponent(componentName, bestMatch!, decision);
        codeTemplate = libraryResult.code;
        imports = libraryResult.imports;
        dependencies = libraryResult.dependencies;
        documentation = libraryResult.documentation;
        examples = libraryResult.examples;
        searchScore = 0.9;
        break;

      case 'use-template':
        const templateResult = await this.searchTemplateComponent(componentName, bestMatch!, decision);
        codeTemplate = templateResult.code;
        imports = templateResult.imports;
        dependencies = templateResult.dependencies;
        documentation = templateResult.documentation;
        examples = templateResult.examples;
        searchScore = 0.75;
        break;

      case 'generate-custom':
        const customResult = await this.generateCustomComponent(componentName, decision);
        codeTemplate = customResult.code;
        imports = customResult.imports;
        dependencies = customResult.dependencies;
        documentation = customResult.documentation;
        examples = customResult.examples;
        searchScore = 0.6;
        break;
    }

    const relatedFiles = await this.searchRelatedFiles(componentName, decision);

    return {
      componentName,
      codeTemplate,
      imports,
      dependencies,
      documentation,
      examples,
      relatedFiles,
      searchScore
    };
  }

  private async searchLibraryComponent(
    componentName: string,
    bestMatch: any,
    decision: ComponentDecision
  ): Promise<{code: string, imports: string[], dependencies: string[], documentation: string, examples: string[]}> {
    const { library } = bestMatch;

    // Generate code using the library component
    let code = '';
    let imports: string[] = [];
    let dependencies: string[] = [];
    let documentation = '';
    let examples: string[] = [];

    if (library === 'antd') {
      const antdResult = this.generateAntDesignCode(componentName, decision);
      code = antdResult.code;
      imports = antdResult.imports;
      dependencies = ['antd'];
      documentation = this.generateAntDesignDocs(componentName);
      examples = this.getAntDesignExamples(componentName);
    } else if (library === '@mui/material') {
      const muiResult = this.generateMaterialUICode(componentName, decision);
      code = muiResult.code;
      imports = muiResult.imports;
      dependencies = ['@mui/material', '@emotion/react', '@emotion/styled'];
      documentation = this.generateMaterialUIDocs(componentName);
      examples = this.getMaterialUIExamples(componentName);
    } else if (library === '@chakra-ui/react') {
      const chakraResult = this.generateChakraUICode(componentName, decision);
      code = chakraResult.code;
      imports = chakraResult.imports;
      dependencies = ['@chakra-ui/react', '@emotion/react', '@emotion/styled'];
      documentation = this.generateChakraUIDocs(componentName);
      examples = this.getChakraUIExamples(componentName);
    }

    return { code, imports, dependencies, documentation, examples };
  }

  private generateAntDesignCode(componentName: string, decision: ComponentDecision): {code: string, imports: string[]} {
    switch (componentName) {
      case 'Button':
        return {
          code: `import React from 'react';
import { Button } from 'antd';
import type { ButtonProps } from 'antd';

interface Custom${componentName}Props extends ButtonProps {
  // Add custom props here
}

const ${componentName}: React.FC<Custom${componentName}Props> = ({
  children,
  onClick,
  type = 'primary',
  disabled = false,
  ...props
}) => {
  return (
    <Button
      type={type}
      onClick={onClick}
      disabled={disabled}
      {...props}
    >
      {children}
    </Button>
  );
};

export default ${componentName};`,
          imports: ['React', 'Button', 'ButtonProps']
        };

      case 'Form':
        return {
          code: `import React from 'react';
import { Form, Input, Button, message } from 'antd';
import type { FormProps } from 'antd';

interface Custom${componentName}Props extends FormProps {
  onSubmit: (values: any) => void;
}

const ${componentName}: React.FC<Custom${componentName}Props> = ({
  onSubmit,
  ...props
}) => {
  const [form] = Form.useForm();

  const handleSubmit = async (values: any) => {
    try {
      await onSubmit(values);
      message.success('Form submitted successfully');
    } catch (error) {
      message.error('Form submission failed');
    }
  };

  return (
    <Form
      form={form}
      onFinish={handleSubmit}
      layout="vertical"
      {...props}
    >
      {/* Add form fields here */}
      <Form.Item>
        <Button type="primary" htmlType="submit">
          Submit
        </Button>
      </Form.Item>
    </Form>
  );
};

export default ${componentName};`,
          imports: ['React', 'Form', 'Input', 'Button', 'message', 'FormProps']
        };

      case 'Table':
        return {
          code: `import React from 'react';
import { Table } from 'antd';
import type { TableProps, ColumnsType } from 'antd';

interface Custom${componentName}Props extends TableProps<any> {
  data: any[];
  columns: ColumnsType<any>;
}

const ${componentName}: React.FC<Custom${componentName}Props> = ({
  data,
  columns,
  ...props
}) => {
  return (
    <Table
      dataSource={data}
      columns={columns}
      pagination={{
        pageSize: 10,
        showSizeChanger: true,
        showQuickJumper: true,
      }}
      {...props}
    />
  );
};

export default ${componentName};`,
          imports: ['React', 'Table', 'TableProps', 'ColumnsType']
        };

      default:
        return {
          code: `import React from 'react';

const ${componentName}: React.FC = () => {
  return (
    <div className="${componentName.toLowerCase()}">
      {/* Component content */}
    </div>
  );
};

export default ${componentName};`,
          imports: ['React']
        };
    }
  }

  private generateMaterialUICode(componentName: string, decision: ComponentDecision): {code: string, imports: string[]} {
    switch (componentName) {
      case 'Button':
        return {
          code: `import React from 'react';
import Button from '@mui/material/Button';
import type { ButtonProps } from '@mui/material/Button';

interface Custom${componentName}Props extends ButtonProps {
  // Add custom props here
}

const ${componentName}: React.FC<Custom${componentName}Props> = ({
  children,
  onClick,
  variant = 'contained',
  disabled = false,
  ...props
}) => {
  return (
    <Button
      variant={variant}
      onClick={onClick}
      disabled={disabled}
      {...props}
    >
      {children}
    </Button>
  );
};

export default ${componentName};`,
          imports: ['React', 'Button', 'ButtonProps']
        };

      default:
        return {
          code: `import React from 'react';

const ${componentName}: React.FC = () => {
  return (
    <div className="${componentName.toLowerCase()}">
      {/* Component content */}
    </div>
  );
};

export default ${componentName};`,
          imports: ['React']
        };
    }
  }

  private generateChakraUICode(componentName: string, decision: ComponentDecision): {code: string, imports: string[]} {
    switch (componentName) {
      case 'Button':
        return {
          code: `import React from 'react';
import { Button } from '@chakra-ui/react';
import type { ButtonProps } from '@chakra-ui/react';

interface Custom${componentName}Props extends ButtonProps {
  // Add custom props here
}

const ${componentName}: React.FC<Custom${componentName}Props> = ({
  children,
  onClick,
  colorScheme = 'blue',
  isDisabled = false,
  ...props
}) => {
  return (
    <Button
      colorScheme={colorScheme}
      onClick={onClick}
      isDisabled={isDisabled}
      {...props}
    >
      {children}
    </Button>
  );
};

export default ${componentName};`,
          imports: ['React', 'Button', 'ButtonProps']
        };

      default:
        return {
          code: `import React from 'react';
import { Box } from '@chakra-ui/react';

const ${componentName}: React.FC = () => {
  return (
    <Box className="${componentName.toLowerCase()}">
      {/* Component content */}
    </Box>
  );
};

export default ${componentName};`,
          imports: ['React', 'Box']
        };
    }
  }

  private async searchTemplateComponent(
    componentName: string,
    bestMatch: any,
    decision: ComponentDecision
  ): Promise<{code: string, imports: string[], dependencies: string[], documentation: string, examples: string[]}> {
    // Search in our template database
    const templates = this.codeDatabase.get(componentName) || [];
    const relevantTemplate = templates.find(t => t.framework === 'react') || templates[0];

    if (relevantTemplate) {
      return {
        code: relevantTemplate.code,
        imports: this.extractImports(relevantTemplate.code),
        dependencies: [],
        documentation: `Template-based ${componentName} component`,
        examples: [`// Example usage of ${componentName}`]
      };
    }

    return this.generateCustomComponent(componentName, decision);
  }

  private async generateCustomComponent(
    componentName: string,
    decision: ComponentDecision
  ): Promise<{code: string, imports: string[], dependencies: string[], documentation: string, examples: string[]}> {
    const code = this.generateBasicReactComponent(componentName, decision);
    const imports = this.extractImports(code);
    
    return {
      code,
      imports,
      dependencies: [],
      documentation: `Custom ${componentName} component`,
      examples: [`// Custom implementation of ${componentName}`]
    };
  }

  private generateBasicReactComponent(componentName: string, decision: ComponentDecision): string {
    const props = decision.props.map(p => `${p.name}${p.required ? '' : '?'}: ${p.type}`).join(';\n  ');
    const propsInterface = props ? `
interface ${componentName}Props {
  ${props};
}` : '';

    const stateHooks = decision.state?.map(s => 
      `const [${s.name}, set${s.name.charAt(0).toUpperCase() + s.name.slice(1)}] = useState<${s.type}>(${JSON.stringify(s.initialValue)});`
    ).join('\n  ') || '';

    const methods = decision.methods.map(m => {
      const params = m.parameters.join(', ');
      const isAsync = m.type === 'async' ? 'async ' : '';
      return `  const ${m.name} = ${isAsync}(${params}): ${m.returnType} => {
    // TODO: Implement ${m.description}
  };`;
    }).join('\n\n');

    return `import React, { useState${decision.hooks?.includes('useEffect') ? ', useEffect' : ''}${decision.hooks?.includes('useCallback') ? ', useCallback' : ''} } from 'react';
${propsInterface}

const ${componentName}: React.FC${propsInterface ? `<${componentName}Props>` : ''} = (${props ? `{
  ${decision.props.map(p => p.name).join(',\n  ')}
}` : ''}) => {
  ${stateHooks}

${methods}

  return (
    <div className="${componentName.toLowerCase()}">
      {/* Component JSX */}
      <h2>${componentName}</h2>
    </div>
  );
};

export default ${componentName};`;
  }

  private extractImports(code: string): string[] {
    const importRegex = /import\s+.*?\s+from\s+['"`](.*?)['"`]/g;
    const imports: string[] = [];
    let match;

    while ((match = importRegex.exec(code)) !== null) {
      imports.push(match[1]);
    }

    return imports;
  }

  private async searchRelatedFiles(
    componentName: string,
    decision: ComponentDecision
  ): Promise<RelatedFile[]> {
    const relatedFiles: RelatedFile[] = [];

    // Style file
    if (decision.styling.approach !== 'inline') {
      relatedFiles.push({
        path: `/src/components/${componentName}/${componentName}.${this.getStyleExtension(decision.styling.approach)}`,
        type: 'style',
        content: this.generateStyleContent(componentName, decision),
        description: `Styles for ${componentName} component`
      });
    }

    // Test file
    if (decision.testing.testTypes.includes('unit')) {
      relatedFiles.push({
        path: `/src/components/${componentName}/${componentName}.test.tsx`,
        type: 'test',
        content: this.generateTestContent(componentName, decision),
        description: `Unit tests for ${componentName} component`
      });
    }

    // Type definitions file
    relatedFiles.push({
      path: `/src/components/${componentName}/${componentName}.types.ts`,
      type: 'type',
      content: this.generateTypeDefinitions(componentName, decision),
      description: `Type definitions for ${componentName} component`
    });

    return relatedFiles;
  }

  private getStyleExtension(approach: string): string {
    switch (approach) {
      case 'css-modules':
        return 'module.css';
      case 'sass':
        return 'scss';
      case 'styled-components':
        return 'styles.ts';
      default:
        return 'css';
    }
  }

  private generateStyleContent(componentName: string, decision: ComponentDecision): string {
    const className = componentName.toLowerCase();
    
    switch (decision.styling.approach) {
      case 'css-modules':
      case 'css':
        return `.${className} {
  /* Component styles */
  display: block;
}

.${className}__title {
  font-size: 1.5rem;
  font-weight: bold;
}`;

      case 'styled-components':
        return `import styled from 'styled-components';

export const ${componentName}Container = styled.div\`
  /* Component styles */
  display: block;
\`;

export const ${componentName}Title = styled.h2\`
  font-size: 1.5rem;
  font-weight: bold;
\`;`;

      case 'sass':
        return `.${className} {
  display: block;
  
  &__title {
    font-size: 1.5rem;
    font-weight: bold;
  }
}`;

      default:
        return `/* Styles for ${componentName} */`;
    }
  }

  private generateTestContent(componentName: string, decision: ComponentDecision): string {
    return `import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ${componentName} from './${componentName}';

describe('${componentName}', () => {
  it('renders without crashing', () => {
    render(<${componentName} />);
    expect(screen.getByText('${componentName}')).toBeInTheDocument();
  });

  ${decision.methods.filter(m => m.type === 'handler').map(m => `
  it('handles ${m.name}', async () => {
    const user = userEvent.setup();
    // TODO: Implement test for ${m.name}
  });`).join('\n')}
});`;
  }

  private generateTypeDefinitions(componentName: string, decision: ComponentDecision): string {
    const propsType = decision.props.length > 0 ? `
export interface ${componentName}Props {
  ${decision.props.map(p => 
    `${p.name}${p.required ? '' : '?'}: ${p.type}; // ${p.description}`
  ).join('\n  ')}
}` : '';

    const stateTypes = decision.state?.length ? `
export interface ${componentName}State {
  ${decision.state.map(s => 
    `${s.name}: ${s.type}; // ${s.description}`
  ).join('\n  ')}
}` : '';

    return `// Type definitions for ${componentName} component
${propsType}${stateTypes}

export type ${componentName}Component = React.FC<${componentName}Props>;`;
  }

  private generateAntDesignDocs(componentName: string): string {
    return `## ${componentName} Component

A ${componentName} component built with Ant Design.

### Props
- Inherits all Ant Design ${componentName} props
- See [Ant Design ${componentName}](https://ant.design/components/${componentName.toLowerCase()}) for full documentation

### Example
\`\`\`tsx
<${componentName} />
\`\`\``;
  }

  private generateMaterialUIDocs(componentName: string): string {
    return `## ${componentName} Component

A ${componentName} component built with Material-UI.

### Props
- Inherits all Material-UI ${componentName} props
- See [Material-UI ${componentName}](https://mui.com/components/${componentName.toLowerCase()}) for full documentation

### Example
\`\`\`tsx
<${componentName} />
\`\`\``;
  }

  private generateChakraUIDocs(componentName: string): string {
    return `## ${componentName} Component

A ${componentName} component built with Chakra UI.

### Props
- Inherits all Chakra UI ${componentName} props
- See [Chakra UI ${componentName}](https://chakra-ui.com/docs/components/${componentName.toLowerCase()}) for full documentation

### Example
\`\`\`tsx
<${componentName} />
\`\`\``;
  }

  private getAntDesignExamples(componentName: string): string[] {
    return [
      `// Basic ${componentName} example`,
      `<${componentName} />`,
      `// Advanced ${componentName} example`,
      `<${componentName} size="large" />`
    ];
  }

  private getMaterialUIExamples(componentName: string): string[] {
    return [
      `// Basic ${componentName} example`,
      `<${componentName} />`,
      `// Variant ${componentName} example`,
      `<${componentName} variant="outlined" />`
    ];
  }

  private getChakraUIExamples(componentName: string): string[] {
    return [
      `// Basic ${componentName} example`,
      `<${componentName} />`,
      `// Colored ${componentName} example`,
      `<${componentName} colorScheme="blue" />`
    ];
  }

  private initializeCodeDatabase(): Map<string, CodeSnippet[]> {
    const db = new Map<string, CodeSnippet[]>();

    // Button snippets
    db.set('Button', [
      {
        id: 'react-button-1',
        title: 'Basic React Button',
        code: `import React from 'react';

const Button = ({ children, onClick, variant = 'primary', ...props }) => {
  return (
    <button 
      className={\`btn btn-\${variant}\`}
      onClick={onClick}
      {...props}
    >
      {children}
    </button>
  );
};

export default Button;`,
        language: 'tsx',
        framework: 'react',
        tags: ['button', 'basic'],
        score: 0.8
      }
    ]);

    // Form snippets
    db.set('Form', [
      {
        id: 'react-form-1',
        title: 'Basic React Form',
        code: `import React, { useState } from 'react';

const Form = ({ onSubmit, children }) => {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await onSubmit(new FormData(e.target));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {children}
      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Submitting...' : 'Submit'}
      </button>
    </form>
  );
};

export default Form;`,
        language: 'tsx',
        framework: 'react',
        tags: ['form', 'basic'],
        score: 0.75
      }
    ]);

    return db;
  }
}