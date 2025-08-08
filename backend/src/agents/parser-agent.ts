/**
 * Parser Agent - 프로젝트 구조 및 코드 템플릿 파싱
 * UI Selection Agent의 결과를 받아 프로젝트 구조를 파싱하고 정의
 */

import { UISelectionResult } from './ui-selection-agent';
import { ProjectRequirements } from './nl-input-agent';

export interface ProjectStructure {
  directories: DirectoryNode[];
  files: FileTemplate[];
  packageJson: PackageJsonTemplate;
  configFiles: ConfigFile[];
  totalFiles: number;
  estimatedSize: string;
}

export interface DirectoryNode {
  name: string;
  path: string;
  children?: DirectoryNode[];
  description?: string;
}

export interface FileTemplate {
  path: string;
  type: 'component' | 'page' | 'service' | 'util' | 'config' | 'style' | 'test';
  template: string;
  dependencies?: string[];
  description?: string;
}

export interface PackageJsonTemplate {
  name: string;
  version: string;
  scripts: Record<string, string>;
  dependencies: Record<string, string>;
  devDependencies: Record<string, string>;
}

export interface ConfigFile {
  name: string;
  path: string;
  content: string;
  format: 'json' | 'js' | 'ts' | 'yaml';
}

export class ParserAgent {
  private name = 'Parser Agent';

  /**
   * UI 선택 결과와 요구사항을 기반으로 프로젝트 구조 파싱
   */
  async parseProjectStructure(
    uiSelection: UISelectionResult,
    requirements: ProjectRequirements
  ): Promise<ProjectStructure> {
    console.log(`[${this.name}] Parsing project structure for ${uiSelection.framework}`);

    const directories = this.createDirectoryStructure(uiSelection, requirements);
    const files = this.createFileTemplates(uiSelection, requirements);
    const packageJson = this.createPackageJson(uiSelection, requirements);
    const configFiles = this.createConfigFiles(uiSelection);

    return {
      directories,
      files,
      packageJson,
      configFiles,
      totalFiles: this.countTotalFiles(files),
      estimatedSize: this.estimateProjectSize(files)
    };
  }

  private createDirectoryStructure(
    uiSelection: UISelectionResult,
    requirements: ProjectRequirements
  ): DirectoryNode[] {
    const { framework } = uiSelection;
    const baseStructure: DirectoryNode[] = [];

    if (framework === 'react' || framework === 'nextjs') {
      baseStructure.push({
        name: 'src',
        path: '/src',
        children: [
          {
            name: 'components',
            path: '/src/components',
            description: 'Reusable UI components',
            children: this.createComponentDirectories(requirements)
          },
          {
            name: 'pages',
            path: '/src/pages',
            description: 'Application pages',
            children: this.createPageDirectories(requirements)
          },
          {
            name: 'services',
            path: '/src/services',
            description: 'API and business logic services'
          },
          {
            name: 'hooks',
            path: '/src/hooks',
            description: 'Custom React hooks'
          },
          {
            name: 'utils',
            path: '/src/utils',
            description: 'Utility functions'
          },
          {
            name: 'styles',
            path: '/src/styles',
            description: 'Global styles and themes'
          },
          {
            name: 'types',
            path: '/src/types',
            description: 'TypeScript type definitions'
          }
        ]
      });

      if (uiSelection.stateManagement) {
        baseStructure[0].children?.push({
          name: 'store',
          path: '/src/store',
          description: 'State management'
        });
      }
    } else if (framework === 'vue') {
      baseStructure.push({
        name: 'src',
        path: '/src',
        children: [
          {
            name: 'components',
            path: '/src/components',
            description: 'Vue components'
          },
          {
            name: 'views',
            path: '/src/views',
            description: 'Vue views/pages'
          },
          {
            name: 'router',
            path: '/src/router',
            description: 'Vue Router configuration'
          },
          {
            name: 'store',
            path: '/src/store',
            description: 'Vuex/Pinia store'
          },
          {
            name: 'assets',
            path: '/src/assets',
            description: 'Static assets'
          }
        ]
      });
    }

    // Add public directory
    baseStructure.push({
      name: 'public',
      path: '/public',
      description: 'Static public assets'
    });

    // Add test directory if needed
    if (!requirements.constraints.includes('Keep it simple')) {
      baseStructure.push({
        name: 'tests',
        path: '/tests',
        description: 'Test files'
      });
    }

    return baseStructure;
  }

  private createComponentDirectories(requirements: ProjectRequirements): DirectoryNode[] {
    const componentDirs: DirectoryNode[] = [];
    const components = requirements.extractedEntities.components || [];

    // Group components by type
    if (components.includes('Form')) {
      componentDirs.push({
        name: 'forms',
        path: '/src/components/forms',
        description: 'Form components'
      });
    }

    if (components.includes('Table')) {
      componentDirs.push({
        name: 'tables',
        path: '/src/components/tables',
        description: 'Table components'
      });
    }

    if (components.includes('Header') || components.includes('Footer')) {
      componentDirs.push({
        name: 'layout',
        path: '/src/components/layout',
        description: 'Layout components'
      });
    }

    componentDirs.push({
      name: 'common',
      path: '/src/components/common',
      description: 'Common/shared components'
    });

    return componentDirs;
  }

  private createPageDirectories(requirements: ProjectRequirements): DirectoryNode[] {
    const pageDirs: DirectoryNode[] = [];
    const pages = requirements.extractedEntities.pages || [];

    // Create subdirectories for auth pages if needed
    if (pages.some(p => p.includes('Login') || p.includes('Signup'))) {
      pageDirs.push({
        name: 'auth',
        path: '/src/pages/auth',
        description: 'Authentication pages'
      });
    }

    return pageDirs;
  }

  private createFileTemplates(
    uiSelection: UISelectionResult,
    requirements: ProjectRequirements
  ): FileTemplate[] {
    const files: FileTemplate[] = [];

    // Create component files
    const components = requirements.extractedEntities.components || [];
    components.forEach(component => {
      files.push(this.createComponentFile(component, uiSelection));
    });

    // Create page files
    const pages = requirements.extractedEntities.pages || [];
    pages.forEach(page => {
      files.push(this.createPageFile(page, uiSelection));
    });

    // Create service files
    if (requirements.functionalRequirements.includes('Database integration')) {
      files.push(this.createServiceFile('api', uiSelection));
      files.push(this.createServiceFile('auth', uiSelection));
    }

    // Create main app file
    files.push(this.createAppFile(uiSelection));

    // Create index file
    files.push(this.createIndexFile(uiSelection));

    return files;
  }

  private createComponentFile(componentName: string, uiSelection: UISelectionResult): FileTemplate {
    const { framework } = uiSelection;
    const extension = framework === 'vue' ? 'vue' : 'tsx';
    const path = `/src/components/${this.getComponentPath(componentName)}/${componentName}.${extension}`;

    return {
      path,
      type: 'component',
      template: this.getComponentTemplate(componentName, framework),
      dependencies: this.getComponentDependencies(componentName, uiSelection),
      description: `${componentName} component`
    };
  }

  private getComponentPath(componentName: string): string {
    if (componentName.includes('Form')) return 'forms';
    if (componentName.includes('Table')) return 'tables';
    if (['Header', 'Footer', 'Sidebar', 'Navigation'].includes(componentName)) return 'layout';
    return 'common';
  }

  private getComponentTemplate(componentName: string, framework: string): string {
    if (framework === 'react' || framework === 'nextjs') {
      return 'react-component';
    } else if (framework === 'vue') {
      return 'vue-component';
    }
    return 'component';
  }

  private getComponentDependencies(componentName: string, uiSelection: UISelectionResult): string[] {
    const deps: string[] = [];
    
    if (componentName === 'QRScanner') {
      deps.push('qr-scanner', 'react-qr-reader');
    }
    
    if (componentName === 'Table' && uiSelection.componentLibrary === 'antd') {
      deps.push('antd/Table');
    }

    return deps;
  }

  private createPageFile(pageName: string, uiSelection: UISelectionResult): FileTemplate {
    const { framework } = uiSelection;
    const extension = framework === 'vue' ? 'vue' : 'tsx';
    const path = `/src/pages/${this.getPagePath(pageName)}/${pageName}.${extension}`;

    return {
      path,
      type: 'page',
      template: this.getPageTemplate(pageName, framework),
      dependencies: [],
      description: `${pageName} page`
    };
  }

  private getPagePath(pageName: string): string {
    if (pageName.includes('Login') || pageName.includes('Signup')) return 'auth';
    return '';
  }

  private getPageTemplate(pageName: string, framework: string): string {
    if (framework === 'react' || framework === 'nextjs') {
      return 'react-page';
    } else if (framework === 'vue') {
      return 'vue-page';
    }
    return 'page';
  }

  private createServiceFile(serviceName: string, uiSelection: UISelectionResult): FileTemplate {
    return {
      path: `/src/services/${serviceName}.service.ts`,
      type: 'service',
      template: 'service',
      dependencies: ['axios'],
      description: `${serviceName} service`
    };
  }

  private createAppFile(uiSelection: UISelectionResult): FileTemplate {
    const { framework } = uiSelection;
    const extension = framework === 'vue' ? 'vue' : 'tsx';
    
    return {
      path: `/src/App.${extension}`,
      type: 'component',
      template: `${framework}-app`,
      dependencies: [],
      description: 'Main application component'
    };
  }

  private createIndexFile(uiSelection: UISelectionResult): FileTemplate {
    return {
      path: '/src/index.tsx',
      type: 'component',
      template: 'index',
      dependencies: [],
      description: 'Application entry point'
    };
  }

  private createPackageJson(
    uiSelection: UISelectionResult,
    requirements: ProjectRequirements
  ): PackageJsonTemplate {
    const projectName = requirements.projectType.toLowerCase().replace(/\s+/g, '-');
    
    return {
      name: projectName,
      version: '1.0.0',
      scripts: this.createScripts(uiSelection),
      dependencies: this.createDependencies(uiSelection, requirements),
      devDependencies: this.createDevDependencies(uiSelection)
    };
  }

  private createScripts(uiSelection: UISelectionResult): Record<string, string> {
    const { buildTool, framework } = uiSelection;
    const scripts: Record<string, string> = {};

    if (buildTool === 'vite') {
      scripts.dev = 'vite';
      scripts.build = 'vite build';
      scripts.preview = 'vite preview';
    } else if (buildTool === 'nextjs') {
      scripts.dev = 'next dev';
      scripts.build = 'next build';
      scripts.start = 'next start';
    }

    scripts.lint = 'eslint . --ext .ts,.tsx';
    scripts.test = 'jest';

    return scripts;
  }

  private createDependencies(
    uiSelection: UISelectionResult,
    requirements: ProjectRequirements
  ): Record<string, string> {
    const deps: Record<string, string> = {};
    
    // Add framework dependencies
    uiSelection.dependencies.forEach(dep => {
      deps[dep] = 'latest';
    });

    // Add additional dependencies based on requirements
    if (requirements.functionalRequirements.includes('Database integration')) {
      deps['axios'] = '^1.6.0';
    }

    if (requirements.extractedEntities.components?.includes('QRScanner')) {
      deps['qr-scanner'] = '^1.4.2';
    }

    return deps;
  }

  private createDevDependencies(uiSelection: UISelectionResult): Record<string, string> {
    const devDeps: Record<string, string> = {};

    // TypeScript
    devDeps['typescript'] = '^5.3.0';
    devDeps['@types/node'] = '^20.10.0';

    // Linting
    devDeps['eslint'] = '^8.55.0';
    devDeps['prettier'] = '^3.1.0';

    // Build tool specific
    if (uiSelection.buildTool === 'vite') {
      devDeps['vite'] = '^5.0.0';
      devDeps['@vitejs/plugin-react'] = '^4.2.0';
    }

    return devDeps;
  }

  private createConfigFiles(uiSelection: UISelectionResult): ConfigFile[] {
    const configs: ConfigFile[] = [];

    // TypeScript config
    configs.push({
      name: 'tsconfig.json',
      path: '/tsconfig.json',
      content: this.getTsConfigContent(uiSelection),
      format: 'json'
    });

    // Vite/Next config
    if (uiSelection.buildTool === 'vite') {
      configs.push({
        name: 'vite.config.ts',
        path: '/vite.config.ts',
        content: this.getViteConfigContent(uiSelection),
        format: 'ts'
      });
    }

    // ESLint config
    configs.push({
      name: '.eslintrc.json',
      path: '/.eslintrc.json',
      content: this.getEslintConfigContent(),
      format: 'json'
    });

    return configs;
  }

  private getTsConfigContent(uiSelection: UISelectionResult): string {
    return JSON.stringify({
      compilerOptions: {
        target: 'ES2022',
        lib: ['ES2022', 'DOM'],
        jsx: uiSelection.framework === 'react' ? 'react-jsx' : 'preserve',
        module: 'ESNext',
        moduleResolution: 'bundler',
        strict: true,
        esModuleInterop: true,
        skipLibCheck: true,
        forceConsistentCasingInFileNames: true
      },
      include: ['src'],
      exclude: ['node_modules']
    }, null, 2);
  }

  private getViteConfigContent(uiSelection: UISelectionResult): string {
    return `import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000
  }
});`;
  }

  private getEslintConfigContent(): string {
    return JSON.stringify({
      extends: ['eslint:recommended', 'plugin:react/recommended'],
      parserOptions: {
        ecmaVersion: 2022,
        sourceType: 'module'
      },
      rules: {
        'react/react-in-jsx-scope': 'off'
      }
    }, null, 2);
  }

  private countTotalFiles(files: FileTemplate[]): number {
    return files.length;
  }

  private estimateProjectSize(files: FileTemplate[]): string {
    const avgFileSize = 2; // KB
    const totalSize = files.length * avgFileSize;
    
    if (totalSize < 100) return `${totalSize} KB`;
    if (totalSize < 1024) return `${(totalSize / 100).toFixed(1)} MB`;
    return `${(totalSize / 1024).toFixed(1)} MB`;
  }
}