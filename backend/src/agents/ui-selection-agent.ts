import { BaseAgent } from './base-agent';

export class UISelectionAgent extends BaseAgent {
  private frameworkMatrix: FrameworkMatrix;

  constructor() {
    super('ui-selection', 'analysis');
  }

  protected async setup(): Promise<void> {
    this.frameworkMatrix = {
      web: {
        react: { score: 9, complexity: 'medium', ecosystem: 'excellent' },
        vue: { score: 8, complexity: 'low', ecosystem: 'good' },
        angular: { score: 8, complexity: 'high', ecosystem: 'excellent' },
        svelte: { score: 7, complexity: 'low', ecosystem: 'growing' },
        nextjs: { score: 9, complexity: 'medium', ecosystem: 'excellent' }
      },
      mobile: {
        'react-native': { score: 8, complexity: 'medium', ecosystem: 'excellent' },
        flutter: { score: 8, complexity: 'medium', ecosystem: 'good' },
        ionic: { score: 6, complexity: 'low', ecosystem: 'good' }
      },
      desktop: {
        electron: { score: 7, complexity: 'medium', ecosystem: 'good' },
        tauri: { score: 8, complexity: 'medium', ecosystem: 'growing' }
      }
    };
  }

  protected validateInput(input: any): void {
    if (!input.projectType) {
      throw new Error('Project type is required');
    }
  }

  protected async process(input: any): Promise<any> {
    const { projectType, requirements } = input;
    
    // Get available frameworks for project type
    const frameworks = this.frameworkMatrix[projectType] || this.frameworkMatrix.web;
    
    // Score frameworks based on requirements
    const scoredFrameworks = Object.entries(frameworks).map(([name, info]) => ({
      name,
      ...info,
      finalScore: this.calculateScore(info, requirements)
    }));

    // Sort by score
    scoredFrameworks.sort((a, b) => b.finalScore - a.finalScore);

    const selectedFramework = scoredFrameworks[0];
    
    return {
      selectedFramework: selectedFramework.name,
      confidence: selectedFramework.finalScore / 10,
      alternatives: scoredFrameworks.slice(1, 3).map(f => f.name),
      reasoning: this.generateReasoning(selectedFramework, requirements),
      recommendations: {
        stateManagement: this.getStateManagementRecommendation(selectedFramework.name),
        styling: this.getStylingRecommendation(selectedFramework.name),
        testing: this.getTestingRecommendation(selectedFramework.name),
        buildTool: this.getBuildToolRecommendation(selectedFramework.name)
      },
      boilerplate: this.generateBoilerplate(selectedFramework.name)
    };
  }

  private calculateScore(framework: FrameworkInfo, requirements: any): number {
    let score = framework.score;
    
    // Adjust based on complexity preference
    if (requirements?.complexity === 'low' && framework.complexity === 'low') {
      score += 1;
    } else if (requirements?.complexity === 'high' && framework.complexity === 'high') {
      score += 0.5;
    }
    
    // Adjust based on ecosystem needs
    if (requirements?.needsLargeEcosystem && framework.ecosystem === 'excellent') {
      score += 1;
    }
    
    return Math.min(score, 10);
  }

  private generateReasoning(framework: any, requirements: any): string {
    return `Selected ${framework.name} due to its ${framework.complexity} complexity, ${framework.ecosystem} ecosystem, and high compatibility score of ${framework.finalScore}/10 for your project requirements.`;
  }

  private getStateManagementRecommendation(framework: string): string {
    const recommendations = {
      react: 'Redux Toolkit or Zustand',
      vue: 'Pinia or Vuex',
      angular: 'NgRx or Akita',
      svelte: 'Svelte stores',
      nextjs: 'Redux Toolkit or SWR'
    };
    return recommendations[framework] || 'Context API';
  }

  private getStylingRecommendation(framework: string): string {
    const recommendations = {
      react: 'Tailwind CSS or Styled Components',
      vue: 'Tailwind CSS or Vue Styled Components',
      angular: 'Angular Material or Tailwind CSS',
      svelte: 'Tailwind CSS or Svelte Styled Components',
      nextjs: 'Tailwind CSS or Styled JSX'
    };
    return recommendations[framework] || 'CSS Modules';
  }

  private getTestingRecommendation(framework: string): string {
    const recommendations = {
      react: 'Jest + React Testing Library',
      vue: 'Jest + Vue Test Utils',
      angular: 'Jasmine + Karma',
      svelte: 'Jest + Svelte Testing Library',
      nextjs: 'Jest + React Testing Library'
    };
    return recommendations[framework] || 'Jest';
  }

  private getBuildToolRecommendation(framework: string): string {
    const recommendations = {
      react: 'Vite or Create React App',
      vue: 'Vite or Vue CLI',
      angular: 'Angular CLI',
      svelte: 'Vite or SvelteKit',
      nextjs: 'Next.js built-in'
    };
    return recommendations[framework] || 'Vite';
  }

  private generateBoilerplate(framework: string): any {
    // Return basic project structure
    return {
      framework,
      structure: this.getProjectStructure(framework),
      dependencies: this.getCoreDependencies(framework),
      scripts: this.getPackageScripts(framework)
    };
  }

  private getProjectStructure(framework: string): any {
    const structures = {
      react: {
        'src/': {
          'components/': {},
          'pages/': {},
          'hooks/': {},
          'utils/': {},
          'App.tsx': '',
          'index.tsx': ''
        },
        'public/': {
          'index.html': ''
        }
      },
      vue: {
        'src/': {
          'components/': {},
          'views/': {},
          'composables/': {},
          'utils/': {},
          'App.vue': '',
          'main.ts': ''
        },
        'public/': {
          'index.html': ''
        }
      }
    };
    return structures[framework] || structures.react;
  }

  private getCoreDependencies(framework: string): string[] {
    const deps = {
      react: ['react', 'react-dom', '@types/react', '@types/react-dom'],
      vue: ['vue', '@vue/typescript'],
      angular: ['@angular/core', '@angular/common', '@angular/platform-browser'],
      svelte: ['svelte', '@sveltejs/kit'],
      nextjs: ['next', 'react', 'react-dom']
    };
    return deps[framework] || deps.react;
  }

  private getPackageScripts(framework: string): any {
    const scripts = {
      react: {
        dev: 'vite dev',
        build: 'vite build',
        preview: 'vite preview'
      },
      vue: {
        dev: 'vite dev',
        build: 'vite build',
        preview: 'vite preview'
      },
      nextjs: {
        dev: 'next dev',
        build: 'next build',
        start: 'next start'
      }
    };
    return scripts[framework] || scripts.react;
  }
}

interface FrameworkMatrix {
  [projectType: string]: {
    [framework: string]: FrameworkInfo;
  };
}

interface FrameworkInfo {
  score: number;
  complexity: 'low' | 'medium' | 'high';
  ecosystem: 'poor' | 'good' | 'excellent';
}