import { BaseAgent } from './base-agent';

export class ComponentDecisionAgent extends BaseAgent {
  private decisionMatrix: DecisionMatrix;
  private architecturePatterns: ArchitecturePattern[];

  constructor() {
    super('component-decision', 'analysis');
  }

  protected async setup(): Promise<void> {
    this.decisionMatrix = {
      criteria: {
        performance: 0.25,
        maintainability: 0.20,
        scalability: 0.20,
        security: 0.15,
        cost: 0.10,
        ecosystem: 0.10
      }
    };

    this.architecturePatterns = [
      {
        name: 'Microservices',
        suitability: ['high-scale', 'distributed', 'team-autonomy'],
        complexity: 'high',
        benefits: ['scalability', 'technology-diversity', 'fault-isolation']
      },
      {
        name: 'Monolithic',
        suitability: ['simple', 'small-team', 'rapid-development'],
        complexity: 'low',
        benefits: ['simplicity', 'easy-deployment', 'performance']
      },
      {
        name: 'Serverless',
        suitability: ['event-driven', 'variable-load', 'cost-optimization'],
        complexity: 'medium',
        benefits: ['auto-scaling', 'pay-per-use', 'no-server-management']
      },
      {
        name: 'JAMstack',
        suitability: ['static-content', 'fast-loading', 'cdn-friendly'],
        complexity: 'low',
        benefits: ['performance', 'security', 'scalability']
      }
    ];
  }

  protected validateInput(input: any): void {
    if (!input.requirements) {
      throw new Error('Requirements are required for component decisions');
    }
  }

  protected async process(input: any): Promise<any> {
    const { requirements, framework, existingComponents = [] } = input;

    // Analyze requirements
    const analysis = this.analyzeRequirements(requirements);
    
    // Select architecture pattern
    const architecture = this.selectArchitecture(analysis);
    
    // Determine component requirements
    const componentRequirements = this.determineComponentRequirements(
      requirements,
      architecture,
      framework
    );
    
    // Evaluate existing components
    const existingEvaluation = this.evaluateExistingComponents(
      existingComponents,
      componentRequirements
    );
    
    // Generate component decisions
    const decisions = this.makeComponentDecisions(
      componentRequirements,
      existingEvaluation
    );

    return {
      architecture: {
        pattern: architecture.name,
        reasoning: architecture.reasoning,
        benefits: architecture.benefits,
        tradeoffs: architecture.tradeoffs
      },
      componentRequirements,
      decisions,
      existingComponentsUsage: existingEvaluation,
      searchCriteria: this.generateSearchCriteria(decisions),
      implementationPlan: this.generateImplementationPlan(decisions, architecture)
    };
  }

  private analyzeRequirements(requirements: any): RequirementAnalysis {
    const { technical = [], functional = [], nonFunctional = [] } = requirements;
    
    return {
      scale: this.determineScale(technical, nonFunctional),
      complexity: this.determineComplexity(functional, technical),
      performance: this.extractPerformanceRequirements(nonFunctional),
      security: this.extractSecurityRequirements(nonFunctional),
      integration: this.extractIntegrationRequirements(technical),
      constraints: this.extractConstraints(nonFunctional)
    };
  }

  private selectArchitecture(analysis: RequirementAnalysis): SelectedArchitecture {
    const scores = this.architecturePatterns.map(pattern => ({
      pattern,
      score: this.scoreArchitecture(pattern, analysis)
    }));

    scores.sort((a, b) => b.score - a.score);
    const selected = scores[0];

    return {
      name: selected.pattern.name,
      score: selected.score,
      reasoning: this.generateArchitectureReasoning(selected.pattern, analysis),
      benefits: selected.pattern.benefits,
      tradeoffs: this.getArchitectureTradeoffs(selected.pattern)
    };
  }

  private determineComponentRequirements(
    requirements: any,
    architecture: SelectedArchitecture,
    framework: string
  ): ComponentRequirement[] {
    const components: ComponentRequirement[] = [];

    // Core components based on architecture
    if (architecture.name === 'Microservices') {
      components.push(
        { name: 'API Gateway', type: 'infrastructure', priority: 'high' },
        { name: 'Service Discovery', type: 'infrastructure', priority: 'high' },
        { name: 'Load Balancer', type: 'infrastructure', priority: 'medium' }
      );
    }

    // Framework-specific components
    if (framework === 'react') {
      components.push(
        { name: 'State Management', type: 'library', priority: 'high' },
        { name: 'Router', type: 'library', priority: 'high' },
        { name: 'UI Components', type: 'library', priority: 'medium' }
      );
    }

    // Functional requirements components
    if (requirements.functional?.includes('authentication')) {
      components.push(
        { name: 'Authentication Service', type: 'service', priority: 'high' }
      );
    }

    if (requirements.functional?.includes('database')) {
      components.push(
        { name: 'Database', type: 'infrastructure', priority: 'high' },
        { name: 'ORM/ODM', type: 'library', priority: 'medium' }
      );
    }

    return components;
  }

  private evaluateExistingComponents(
    existingComponents: any[],
    requirements: ComponentRequirement[]
  ): ExistingComponentEvaluation[] {
    return existingComponents.map(component => {
      const matchingRequirement = requirements.find(req => 
        this.componentsMatch(component, req)
      );

      return {
        component,
        canReuse: !!matchingRequirement,
        matchingRequirement,
        modifications: matchingRequirement ? 
          this.getRequiredModifications(component, matchingRequirement) : [],
        reuseConfidence: matchingRequirement ? 
          this.calculateReuseConfidence(component, matchingRequirement) : 0
      };
    });
  }

  private makeComponentDecisions(
    requirements: ComponentRequirement[],
    existingEvaluation: ExistingComponentEvaluation[]
  ): ComponentDecision[] {
    return requirements.map(requirement => {
      const existingMatch = existingEvaluation.find(
        eval => eval.matchingRequirement?.name === requirement.name
      );

      if (existingMatch && existingMatch.canReuse && existingMatch.reuseConfidence > 0.7) {
        return {
          requirement,
          decision: 'reuse',
          component: existingMatch.component,
          confidence: existingMatch.reuseConfidence,
          reasoning: 'Existing component meets requirements with high confidence'
        };
      }

      return {
        requirement,
        decision: 'search',
        searchStrategy: this.determineSearchStrategy(requirement),
        fallbackStrategy: 'generate',
        confidence: 0.8,
        reasoning: 'Need to search for suitable component or generate new one'
      };
    });
  }

  private generateSearchCriteria(decisions: ComponentDecision[]): SearchCriteria {
    const searchDecisions = decisions.filter(d => d.decision === 'search');
    
    return {
      components: searchDecisions.map(decision => ({
        name: decision.requirement.name,
        type: decision.requirement.type,
        priority: decision.requirement.priority,
        keywords: this.generateSearchKeywords(decision.requirement),
        filters: this.generateSearchFilters(decision.requirement)
      })),
      globalFilters: {
        minStars: 100,
        maxAge: '2 years',
        activelyMaintained: true,
        hasDocumentation: true
      }
    };
  }

  private generateImplementationPlan(
    decisions: ComponentDecision[],
    architecture: SelectedArchitecture
  ): ImplementationPlan {
    const phases = this.groupDecisionsByPhase(decisions);
    
    return {
      phases: phases.map((phase, index) => ({
        name: `Phase ${index + 1}`,
        components: phase,
        estimatedDuration: this.estimatePhaseDuration(phase),
        dependencies: index > 0 ? [`Phase ${index}`] : []
      })),
      totalEstimatedDuration: phases.reduce(
        (total, phase) => total + this.estimatePhaseDuration(phase), 0
      ),
      criticalPath: this.identifyCriticalPath(decisions),
      risks: this.identifyImplementationRisks(decisions, architecture)
    };
  }

  // Helper methods with simplified implementations
  private determineScale(technical: string[], nonFunctional: string[]): 'small' | 'medium' | 'large' {
    const scaleIndicators = [...technical, ...nonFunctional].join(' ').toLowerCase();
    if (scaleIndicators.includes('enterprise') || scaleIndicators.includes('million')) return 'large';
    if (scaleIndicators.includes('team') || scaleIndicators.includes('thousand')) return 'medium';
    return 'small';
  }

  private determineComplexity(functional: string[], technical: string[]): 'low' | 'medium' | 'high' {
    const totalRequirements = functional.length + technical.length;
    if (totalRequirements > 10) return 'high';
    if (totalRequirements > 5) return 'medium';
    return 'low';
  }

  private scoreArchitecture(pattern: ArchitecturePattern, analysis: RequirementAnalysis): number {
    let score = 0;
    
    // Scale matching
    if (analysis.scale === 'large' && pattern.name === 'Microservices') score += 30;
    if (analysis.scale === 'small' && pattern.name === 'Monolithic') score += 30;
    
    // Complexity matching
    if (analysis.complexity === 'low' && pattern.complexity === 'low') score += 20;
    if (analysis.complexity === 'high' && pattern.complexity === 'high') score += 15;
    
    return score;
  }

  private generateArchitectureReasoning(pattern: ArchitecturePattern, analysis: RequirementAnalysis): string {
    return `Selected ${pattern.name} architecture based on ${analysis.scale} scale requirements and ${analysis.complexity} complexity. This pattern provides ${pattern.benefits.join(', ')}.`;
  }

  private getArchitectureTradeoffs(pattern: ArchitecturePattern): string[] {
    const tradeoffs = {
      'Microservices': ['Increased complexity', 'Network latency', 'Distributed system challenges'],
      'Monolithic': ['Limited scalability', 'Technology lock-in', 'Deployment coupling'],
      'Serverless': ['Vendor lock-in', 'Cold starts', 'Limited execution time'],
      'JAMstack': ['Limited dynamic functionality', 'Build time complexity', 'API dependency']
    };
    return tradeoffs[pattern.name] || [];
  }

  private componentsMatch(component: any, requirement: ComponentRequirement): boolean {
    return component.name?.toLowerCase().includes(requirement.name.toLowerCase()) ||
           component.type === requirement.type;
  }

  private calculateReuseConfidence(component: any, requirement: ComponentRequirement): number {
    // Simplified confidence calculation
    return 0.8;
  }

  private getRequiredModifications(component: any, requirement: ComponentRequirement): string[] {
    return ['Update dependencies', 'Refactor for new requirements'];
  }

  private determineSearchStrategy(requirement: ComponentRequirement): string {
    return requirement.type === 'library' ? 'npm-search' : 'github-search';
  }

  private generateSearchKeywords(requirement: ComponentRequirement): string[] {
    return [requirement.name.toLowerCase(), requirement.type];
  }

  private generateSearchFilters(requirement: ComponentRequirement): any {
    return { type: requirement.type, priority: requirement.priority };
  }

  private groupDecisionsByPhase(decisions: ComponentDecision[]): ComponentDecision[][] {
    const high = decisions.filter(d => d.requirement.priority === 'high');
    const medium = decisions.filter(d => d.requirement.priority === 'medium');
    const low = decisions.filter(d => d.requirement.priority === 'low');
    return [high, medium, low].filter(phase => phase.length > 0);
  }

  private estimatePhaseDuration(phase: ComponentDecision[]): number {
    return phase.length * 2; // 2 days per component
  }

  private identifyCriticalPath(decisions: ComponentDecision[]): string[] {
    return decisions
      .filter(d => d.requirement.priority === 'high')
      .map(d => d.requirement.name);
  }

  private identifyImplementationRisks(decisions: ComponentDecision[], architecture: SelectedArchitecture): string[] {
    const risks = [];
    if (decisions.some(d => d.decision === 'generate')) {
      risks.push('Custom component development may take longer than expected');
    }
    if (architecture.name === 'Microservices') {
      risks.push('Distributed system complexity may cause integration issues');
    }
    return risks;
  }

  private extractPerformanceRequirements(nonFunctional: string[]): any { return {}; }
  private extractSecurityRequirements(nonFunctional: string[]): any { return {}; }
  private extractIntegrationRequirements(technical: string[]): any { return {}; }
  private extractConstraints(nonFunctional: string[]): any { return {}; }
}

interface DecisionMatrix {
  criteria: {
    performance: number;
    maintainability: number;
    scalability: number;
    security: number;
    cost: number;
    ecosystem: number;
  };
}

interface ArchitecturePattern {
  name: string;
  suitability: string[];
  complexity: 'low' | 'medium' | 'high';
  benefits: string[];
}

interface RequirementAnalysis {
  scale: 'small' | 'medium' | 'large';
  complexity: 'low' | 'medium' | 'high';
  performance: any;
  security: any;
  integration: any;
  constraints: any;
}

interface SelectedArchitecture {
  name: string;
  score: number;
  reasoning: string;
  benefits: string[];
  tradeoffs: string[];
}

interface ComponentRequirement {
  name: string;
  type: 'library' | 'service' | 'infrastructure';
  priority: 'high' | 'medium' | 'low';
}

interface ExistingComponentEvaluation {
  component: any;
  canReuse: boolean;
  matchingRequirement?: ComponentRequirement;
  modifications: string[];
  reuseConfidence: number;
}

interface ComponentDecision {
  requirement: ComponentRequirement;
  decision: 'reuse' | 'search' | 'generate';
  component?: any;
  searchStrategy?: string;
  fallbackStrategy?: string;
  confidence: number;
  reasoning: string;
}

interface SearchCriteria {
  components: any[];
  globalFilters: any;
}

interface ImplementationPlan {
  phases: any[];
  totalEstimatedDuration: number;
  criticalPath: string[];
  risks: string[];
}