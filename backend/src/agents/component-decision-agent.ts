/**
 * Component Decision Agent - 컴포넌트 설계 및 의사결정
 * Parser Agent의 결과를 받아 각 컴포넌트의 상세 설계 결정
 */

import { ProjectStructure, FileTemplate } from './parser-agent';
import { UISelectionResult } from './ui-selection-agent';
import { ProjectRequirements } from './nl-input-agent';

export interface ComponentDecision {
  componentName: string;
  componentType: 'functional' | 'class' | 'composition';
  props: PropDefinition[];
  state?: StateDefinition[];
  methods: MethodDefinition[];
  hooks?: string[];
  imports: ImportStatement[];
  exports: ExportStatement[];
  styling: StylingDecision;
  testing: TestingStrategy;
  documentation: string;
}

export interface PropDefinition {
  name: string;
  type: string;
  required: boolean;
  defaultValue?: any;
  description?: string;
}

export interface StateDefinition {
  name: string;
  type: string;
  initialValue: any;
  description?: string;
}

export interface MethodDefinition {
  name: string;
  type: 'handler' | 'lifecycle' | 'utility' | 'async';
  parameters: string[];
  returnType: string;
  description?: string;
}

export interface ImportStatement {
  from: string;
  items: string[];
  isDefault?: boolean;
}

export interface ExportStatement {
  name: string;
  isDefault: boolean;
}

export interface StylingDecision {
  approach: 'inline' | 'css-modules' | 'styled-components' | 'tailwind' | 'sass' | 'css';
  classNames?: string[];
  styleVariables?: Record<string, string>;
}

export interface TestingStrategy {
  framework: 'jest' | 'vitest' | 'cypress';
  testTypes: ('unit' | 'integration' | 'e2e')[];
  coverage: number;
}

export class ComponentDecisionAgent {
  private name = 'Component Decision Agent';

  /**
   * 프로젝트 구조를 기반으로 각 컴포넌트의 상세 설계 결정
   */
  async makeComponentDecisions(
    projectStructure: ProjectStructure,
    uiSelection: UISelectionResult,
    requirements: ProjectRequirements
  ): Promise<ComponentDecision[]> {
    console.log(`[${this.name}] Making decisions for ${projectStructure.files.length} files`);

    const decisions: ComponentDecision[] = [];

    // 컴포넌트 파일들에 대해 의사결정
    const componentFiles = projectStructure.files.filter(f => f.type === 'component' || f.type === 'page');
    
    for (const file of componentFiles) {
      const decision = await this.makeDecisionForComponent(file, uiSelection, requirements);
      decisions.push(decision);
    }

    return decisions;
  }

  private async makeDecisionForComponent(
    file: FileTemplate,
    uiSelection: UISelectionResult,
    requirements: ProjectRequirements
  ): Promise<ComponentDecision> {
    const componentName = this.extractComponentName(file.path);
    const componentType = this.determineComponentType(componentName, uiSelection);
    const props = this.defineProps(componentName, requirements);
    const state = this.defineState(componentName, requirements);
    const methods = this.defineMethods(componentName, requirements);
    const hooks = this.defineHooks(componentName, uiSelection);
    const imports = this.defineImports(componentName, uiSelection, file.dependencies);
    const exports = this.defineExports(componentName);
    const styling = this.decideStyling(componentName, uiSelection);
    const testing = this.defineTestingStrategy(requirements);

    return {
      componentName,
      componentType,
      props,
      state,
      methods,
      hooks,
      imports,
      exports,
      styling,
      testing,
      documentation: this.generateDocumentation(componentName, props, methods)
    };
  }

  private extractComponentName(filePath: string): string {
    const parts = filePath.split('/');
    const fileName = parts[parts.length - 1];
    return fileName.replace(/\.(tsx?|jsx?|vue)$/, '');
  }

  private determineComponentType(
    componentName: string,
    uiSelection: UISelectionResult
  ): 'functional' | 'class' | 'composition' {
    // React/Next.js는 functional components 사용
    if (uiSelection.framework === 'react' || uiSelection.framework === 'nextjs') {
      return 'functional';
    }
    
    // Vue 3는 composition API 사용
    if (uiSelection.framework === 'vue') {
      return 'composition';
    }

    return 'functional';
  }

  private defineProps(componentName: string, requirements: ProjectRequirements): PropDefinition[] {
    const props: PropDefinition[] = [];

    // Common props
    props.push({
      name: 'className',
      type: 'string',
      required: false,
      description: 'Additional CSS classes'
    });

    // Component-specific props
    switch (componentName) {
      case 'Button':
        props.push(
          {
            name: 'onClick',
            type: '() => void',
            required: false,
            description: 'Click handler'
          },
          {
            name: 'variant',
            type: "'primary' | 'secondary' | 'danger'",
            required: false,
            defaultValue: 'primary',
            description: 'Button variant'
          },
          {
            name: 'disabled',
            type: 'boolean',
            required: false,
            defaultValue: false,
            description: 'Disable button'
          }
        );
        break;

      case 'Form':
        props.push(
          {
            name: 'onSubmit',
            type: '(data: any) => void',
            required: true,
            description: 'Form submission handler'
          },
          {
            name: 'initialValues',
            type: 'Record<string, any>',
            required: false,
            defaultValue: {},
            description: 'Initial form values'
          }
        );
        break;

      case 'Table':
        props.push(
          {
            name: 'data',
            type: 'any[]',
            required: true,
            description: 'Table data'
          },
          {
            name: 'columns',
            type: 'Column[]',
            required: true,
            description: 'Table columns configuration'
          }
        );
        break;

      case 'QRScanner':
        props.push(
          {
            name: 'onScan',
            type: '(data: string) => void',
            required: true,
            description: 'QR code scan handler'
          },
          {
            name: 'onError',
            type: '(error: Error) => void',
            required: false,
            description: 'Error handler'
          }
        );
        break;

      case 'Header':
        props.push(
          {
            name: 'user',
            type: 'User | null',
            required: false,
            description: 'Current user'
          },
          {
            name: 'onLogout',
            type: '() => void',
            required: false,
            description: 'Logout handler'
          }
        );
        break;
    }

    // Add children prop for container components
    if (['Card', 'Modal', 'Layout'].includes(componentName)) {
      props.push({
        name: 'children',
        type: 'React.ReactNode',
        required: true,
        description: 'Component children'
      });
    }

    return props;
  }

  private defineState(componentName: string, requirements: ProjectRequirements): StateDefinition[] {
    const state: StateDefinition[] = [];

    switch (componentName) {
      case 'Form':
        state.push(
          {
            name: 'values',
            type: 'Record<string, any>',
            initialValue: {},
            description: 'Form values'
          },
          {
            name: 'errors',
            type: 'Record<string, string>',
            initialValue: {},
            description: 'Form validation errors'
          },
          {
            name: 'isSubmitting',
            type: 'boolean',
            initialValue: false,
            description: 'Form submission state'
          }
        );
        break;

      case 'Table':
        state.push(
          {
            name: 'sortColumn',
            type: 'string | null',
            initialValue: null,
            description: 'Current sort column'
          },
          {
            name: 'sortDirection',
            type: "'asc' | 'desc'",
            initialValue: 'asc',
            description: 'Sort direction'
          },
          {
            name: 'currentPage',
            type: 'number',
            initialValue: 1,
            description: 'Current page number'
          }
        );
        break;

      case 'LoginPage':
        state.push(
          {
            name: 'email',
            type: 'string',
            initialValue: '',
            description: 'User email'
          },
          {
            name: 'password',
            type: 'string',
            initialValue: '',
            description: 'User password'
          },
          {
            name: 'rememberMe',
            type: 'boolean',
            initialValue: false,
            description: 'Remember me checkbox'
          }
        );
        break;

      case 'QRScanner':
        state.push(
          {
            name: 'isScanning',
            type: 'boolean',
            initialValue: false,
            description: 'Scanner active state'
          },
          {
            name: 'lastScannedData',
            type: 'string | null',
            initialValue: null,
            description: 'Last scanned QR data'
          }
        );
        break;
    }

    // Add loading state for data-fetching components
    if (['DashboardPage', 'ProfilePage'].includes(componentName)) {
      state.push(
        {
          name: 'isLoading',
          type: 'boolean',
          initialValue: true,
          description: 'Loading state'
        },
        {
          name: 'data',
          type: 'any | null',
          initialValue: null,
          description: 'Fetched data'
        }
      );
    }

    return state;
  }

  private defineMethods(componentName: string, requirements: ProjectRequirements): MethodDefinition[] {
    const methods: MethodDefinition[] = [];

    switch (componentName) {
      case 'Form':
        methods.push(
          {
            name: 'handleSubmit',
            type: 'handler',
            parameters: ['event: FormEvent'],
            returnType: 'void',
            description: 'Handle form submission'
          },
          {
            name: 'validateForm',
            type: 'utility',
            parameters: [],
            returnType: 'boolean',
            description: 'Validate form fields'
          },
          {
            name: 'resetForm',
            type: 'utility',
            parameters: [],
            returnType: 'void',
            description: 'Reset form to initial state'
          }
        );
        break;

      case 'Table':
        methods.push(
          {
            name: 'handleSort',
            type: 'handler',
            parameters: ['column: string'],
            returnType: 'void',
            description: 'Handle column sorting'
          },
          {
            name: 'handlePageChange',
            type: 'handler',
            parameters: ['page: number'],
            returnType: 'void',
            description: 'Handle pagination'
          }
        );
        break;

      case 'LoginPage':
        methods.push(
          {
            name: 'handleLogin',
            type: 'async',
            parameters: [],
            returnType: 'Promise<void>',
            description: 'Handle login submission'
          },
          {
            name: 'validateCredentials',
            type: 'utility',
            parameters: [],
            returnType: 'boolean',
            description: 'Validate login credentials'
          }
        );
        break;

      case 'QRScanner':
        methods.push(
          {
            name: 'startScanning',
            type: 'async',
            parameters: [],
            returnType: 'Promise<void>',
            description: 'Start QR scanning'
          },
          {
            name: 'stopScanning',
            type: 'handler',
            parameters: [],
            returnType: 'void',
            description: 'Stop QR scanning'
          },
          {
            name: 'handleScanResult',
            type: 'handler',
            parameters: ['result: string'],
            returnType: 'void',
            description: 'Process scan result'
          }
        );
        break;
    }

    // Add common lifecycle methods for pages
    if (componentName.endsWith('Page')) {
      methods.push({
        name: 'fetchData',
        type: 'async',
        parameters: [],
        returnType: 'Promise<void>',
        description: 'Fetch page data'
      });
    }

    return methods;
  }

  private defineHooks(componentName: string, uiSelection: UISelectionResult): string[] {
    if (uiSelection.framework !== 'react' && uiSelection.framework !== 'nextjs') {
      return [];
    }

    const hooks: string[] = ['useState'];

    // Add component-specific hooks
    if (componentName.endsWith('Page')) {
      hooks.push('useEffect');
    }

    if (componentName === 'Form') {
      hooks.push('useCallback', 'useMemo');
    }

    if (componentName === 'QRScanner') {
      hooks.push('useRef', 'useEffect');
    }

    // Add routing hooks for pages
    if (componentName.endsWith('Page') && uiSelection.routing === 'react-router-dom') {
      hooks.push('useNavigate', 'useParams');
    }

    // Add state management hooks
    if (uiSelection.stateManagement === 'redux-toolkit') {
      hooks.push('useSelector', 'useDispatch');
    } else if (uiSelection.stateManagement === 'zustand') {
      hooks.push('useStore');
    }

    return [...new Set(hooks)]; // Remove duplicates
  }

  private defineImports(
    componentName: string,
    uiSelection: UISelectionResult,
    dependencies?: string[]
  ): ImportStatement[] {
    const imports: ImportStatement[] = [];

    // React imports
    if (uiSelection.framework === 'react' || uiSelection.framework === 'nextjs') {
      const reactImports = ['React'];
      const hooks = this.defineHooks(componentName, uiSelection);
      if (hooks.length > 0) {
        reactImports.push(...hooks);
      }
      imports.push({
        from: 'react',
        items: reactImports,
        isDefault: true
      });
    }

    // Component library imports
    if (uiSelection.componentLibrary !== 'native') {
      const componentImports = this.getComponentLibraryImports(componentName, uiSelection.componentLibrary);
      if (componentImports.length > 0) {
        imports.push({
          from: uiSelection.componentLibrary,
          items: componentImports
        });
      }
    }

    // Routing imports
    if (componentName.endsWith('Page') && uiSelection.routing) {
      if (uiSelection.routing === 'react-router-dom') {
        imports.push({
          from: 'react-router-dom',
          items: ['useNavigate', 'useParams']
        });
      }
    }

    // Custom dependencies
    if (dependencies) {
      dependencies.forEach(dep => {
        if (dep.includes('/')) {
          // Specific import from component library
          const [lib, component] = dep.split('/');
          imports.push({
            from: lib,
            items: [component]
          });
        } else {
          // Default import
          imports.push({
            from: dep,
            items: [dep],
            isDefault: true
          });
        }
      });
    }

    // Style imports
    if (uiSelection.stylingApproach === 'css-modules') {
      imports.push({
        from: `./${componentName}.module.css`,
        items: ['styles'],
        isDefault: true
      });
    }

    return imports;
  }

  private getComponentLibraryImports(componentName: string, library: string): string[] {
    const imports: string[] = [];

    if (library === 'antd') {
      if (componentName === 'Button') imports.push('Button');
      if (componentName === 'Form') imports.push('Form', 'Input');
      if (componentName === 'Table') imports.push('Table');
      if (componentName === 'Card') imports.push('Card');
    } else if (library === 'mui') {
      if (componentName === 'Button') imports.push('Button');
      if (componentName === 'Form') imports.push('TextField', 'Box');
      if (componentName === 'Table') imports.push('Table', 'TableBody', 'TableCell');
    }

    return imports;
  }

  private defineExports(componentName: string): ExportStatement[] {
    return [{
      name: componentName,
      isDefault: true
    }];
  }

  private decideStyling(componentName: string, uiSelection: UISelectionResult): StylingDecision {
    const { stylingApproach } = uiSelection;
    
    const styling: StylingDecision = {
      approach: stylingApproach as any,
      classNames: [],
      styleVariables: {}
    };

    // Define common class names for Tailwind
    if (stylingApproach === 'tailwind') {
      switch (componentName) {
        case 'Button':
          styling.classNames = ['px-4', 'py-2', 'rounded', 'bg-blue-500', 'text-white', 'hover:bg-blue-600'];
          break;
        case 'Card':
          styling.classNames = ['p-6', 'bg-white', 'rounded-lg', 'shadow-md'];
          break;
        case 'Header':
          styling.classNames = ['w-full', 'bg-gray-800', 'text-white', 'p-4'];
          break;
      }
    }

    // Define style variables for CSS-in-JS
    if (stylingApproach === 'styled-components') {
      styling.styleVariables = {
        primaryColor: '#3B82F6',
        secondaryColor: '#10B981',
        dangerColor: '#EF4444',
        borderRadius: '0.375rem',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
      };
    }

    return styling;
  }

  private defineTestingStrategy(requirements: ProjectRequirements): TestingStrategy {
    const isSimple = requirements.constraints.includes('Keep it simple');
    
    return {
      framework: 'vitest',
      testTypes: isSimple ? ['unit'] : ['unit', 'integration'],
      coverage: isSimple ? 60 : 80
    };
  }

  private generateDocumentation(
    componentName: string,
    props: PropDefinition[],
    methods: MethodDefinition[]
  ): string {
    const propsDocs = props.map(p => `* @param {${p.type}} ${p.name} - ${p.description}`).join('\n');
    const methodsDocs = methods.map(m => `* ${m.name}: ${m.description}`).join('\n');
    
    return `/**
 * ${componentName} Component
 * 
 * Props:
${propsDocs}
 * 
 * Methods:
${methodsDocs}
 */`;
  }
}