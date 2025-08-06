import { Intent, Decision } from '../agents/supervisor/types';

export enum StepType {
  SEQUENTIAL = "sequential",
  PARALLEL = "parallel",
  CONDITIONAL = "conditional"
}

export interface WorkflowStep {
  id: string;
  name: string;
  type: StepType;
  agents: string[];
  dependencies: string[];
  condition?: string;
  timeout: number;
}

export interface Workflow {
  id: string;
  name: string;
  steps: WorkflowStep[];
  estimatedDuration: number;
  createdAt: Date;
}

export interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  intentTypes: string[];
  steps: WorkflowStep[];
}

export class WorkflowEngine {
  private templates: Map<string, WorkflowTemplate> = new Map();
  private validator: WorkflowValidator;

  constructor() {
    this.validator = new WorkflowValidator();
    this.loadWorkflowTemplates();
  }

  async createWorkflow(intent: Intent, agents: string[]): Promise<Workflow> {
    // 1. 템플릿 선택
    const template = this.selectTemplate(intent);
    
    let workflow: Workflow;
    
    if (template) {
      // 2a. 템플릿 기반 워크플로우 생성
      workflow = this.applyTemplate(template, agents);
    } else {
      // 2b. 동적 워크플로우 생성
      workflow = this.createDynamicWorkflow(intent, agents);
    }
    
    // 3. 검증
    await this.validator.validate(workflow);
    
    // 4. 최적화
    workflow = this.optimizeWorkflow(workflow);
    
    return workflow;
  }

  private createDynamicWorkflow(intent: Intent, agents: string[]): Workflow {
    const steps: WorkflowStep[] = [];
    
    // 의존성 분석
    const dependencies = this.analyzeDependencies(agents);
    
    // 병렬화 가능한 작업 식별
    const parallelGroups = this.identifyParallelTasks(dependencies);
    
    // 워크플로우 스텝 생성
    parallelGroups.forEach((group, index) => {
      if (group.length > 1) {
        steps.push({
          id: `step_${index}`,
          name: `Parallel execution: ${group.join(', ')}`,
          type: StepType.PARALLEL,
          agents: group,
          dependencies: index > 0 ? [`step_${index - 1}`] : [],
          timeout: 300
        });
      } else {
        steps.push({
          id: `step_${index}`,
          name: `Execute: ${group[0]}`,
          type: StepType.SEQUENTIAL,
          agents: group,
          dependencies: index > 0 ? [`step_${index - 1}`] : [],
          timeout: 300
        });
      }
    });

    return {
      id: `workflow_${Date.now()}`,
      name: `Dynamic workflow for ${intent.type}`,
      steps,
      estimatedDuration: this.calculateEstimatedDuration(steps),
      createdAt: new Date()
    };
  }

  private selectTemplate(intent: Intent): WorkflowTemplate | null {
    for (const template of this.templates.values()) {
      if (template.intentTypes.includes(intent.type)) {
        return template;
      }
    }
    return null;
  }

  private applyTemplate(template: WorkflowTemplate, agents: string[]): Workflow {
    const steps = template.steps.map(step => ({
      ...step,
      agents: this.mapAgentsToStep(step, agents)
    }));

    return {
      id: `workflow_${Date.now()}`,
      name: `${template.name} workflow`,
      steps,
      estimatedDuration: this.calculateEstimatedDuration(steps),
      createdAt: new Date()
    };
  }

  private analyzeDependencies(agents: string[]): Map<string, string[]> {
    const dependencies = new Map<string, string[]>();
    
    // 에이전트 간 의존성 규칙
    const dependencyRules = {
      'CodeAgent': [],
      'UIAgent': ['CodeAgent'],
      'APIAgent': ['CodeAgent'],
      'TestAgent': ['CodeAgent', 'UIAgent', 'APIAgent'],
      'SecurityAgent': ['CodeAgent', 'APIAgent'],
      'DeploymentAgent': ['CodeAgent', 'TestAgent', 'SecurityAgent']
    };

    agents.forEach(agent => {
      const deps = dependencyRules[agent] || [];
      dependencies.set(agent, deps.filter(dep => agents.includes(dep)));
    });

    return dependencies;
  }

  private identifyParallelTasks(dependencies: Map<string, string[]>): string[][] {
    const groups: string[][] = [];
    const processed = new Set<string>();
    
    // 의존성이 없는 에이전트들을 첫 번째 그룹으로
    const independentAgents = Array.from(dependencies.entries())
      .filter(([_, deps]) => deps.length === 0)
      .map(([agent, _]) => agent);
    
    if (independentAgents.length > 0) {
      groups.push(independentAgents);
      independentAgents.forEach(agent => processed.add(agent));
    }

    // 나머지 에이전트들을 의존성에 따라 그룹화
    while (processed.size < dependencies.size) {
      const nextGroup: string[] = [];
      
      for (const [agent, deps] of dependencies.entries()) {
        if (!processed.has(agent) && deps.every(dep => processed.has(dep))) {
          nextGroup.push(agent);
        }
      }
      
      if (nextGroup.length > 0) {
        groups.push(nextGroup);
        nextGroup.forEach(agent => processed.add(agent));
      } else {
        // 순환 의존성이 있는 경우 강제로 처리
        const remaining = Array.from(dependencies.keys()).filter(agent => !processed.has(agent));
        if (remaining.length > 0) {
          groups.push([remaining[0]]);
          processed.add(remaining[0]);
        }
      }
    }

    return groups;
  }

  private mapAgentsToStep(step: WorkflowStep, availableAgents: string[]): string[] {
    return step.agents.filter(agent => availableAgents.includes(agent));
  }

  private calculateEstimatedDuration(steps: WorkflowStep[]): number {
    let totalDuration = 0;
    
    steps.forEach(step => {
      if (step.type === StepType.PARALLEL) {
        // 병렬 실행은 가장 긴 작업 시간
        totalDuration += Math.max(...step.agents.map(() => step.timeout));
      } else {
        // 순차 실행은 모든 작업 시간의 합
        totalDuration += step.agents.length * step.timeout;
      }
    });

    return totalDuration;
  }

  private optimizeWorkflow(workflow: Workflow): Workflow {
    // 불필요한 의존성 제거
    const optimizedSteps = workflow.steps.map(step => ({
      ...step,
      dependencies: this.removeRedundantDependencies(step.dependencies, workflow.steps)
    }));

    // 병렬화 가능한 스텝 병합
    const mergedSteps = this.mergeParallelizableSteps(optimizedSteps);

    return {
      ...workflow,
      steps: mergedSteps,
      estimatedDuration: this.calculateEstimatedDuration(mergedSteps)
    };
  }

  private removeRedundantDependencies(dependencies: string[], allSteps: WorkflowStep[]): string[] {
    // 간접 의존성 제거 (A -> B -> C에서 A -> C 제거)
    return dependencies.filter(dep => {
      const depStep = allSteps.find(s => s.id === dep);
      if (!depStep) return true;
      
      return !dependencies.some(otherDep => {
        const otherDepStep = allSteps.find(s => s.id === otherDep);
        return otherDepStep && otherDepStep.dependencies.includes(dep);
      });
    });
  }

  private mergeParallelizableSteps(steps: WorkflowStep[]): WorkflowStep[] {
    const merged: WorkflowStep[] = [];
    let i = 0;

    while (i < steps.length) {
      const currentStep = steps[i];
      
      if (currentStep.type === StepType.SEQUENTIAL && i < steps.length - 1) {
        const nextStep = steps[i + 1];
        
        // 연속된 순차 스텝을 병렬로 병합 가능한지 확인
        if (nextStep.type === StepType.SEQUENTIAL && 
            this.canMergeSteps(currentStep, nextStep)) {
          merged.push({
            id: `merged_${currentStep.id}_${nextStep.id}`,
            name: `Merged: ${currentStep.name} + ${nextStep.name}`,
            type: StepType.PARALLEL,
            agents: [...currentStep.agents, ...nextStep.agents],
            dependencies: currentStep.dependencies,
            timeout: Math.max(currentStep.timeout, nextStep.timeout)
          });
          i += 2; // 두 스텝을 건너뜀
        } else {
          merged.push(currentStep);
          i++;
        }
      } else {
        merged.push(currentStep);
        i++;
      }
    }

    return merged;
  }

  private canMergeSteps(step1: WorkflowStep, step2: WorkflowStep): boolean {
    // 에이전트 간 충돌이 없고, 의존성이 허용하는 경우만 병합
    const hasAgentConflict = step1.agents.some(agent => step2.agents.includes(agent));
    const hasDependencyConflict = step2.dependencies.includes(step1.id);
    
    return !hasAgentConflict && !hasDependencyConflict;
  }

  private loadWorkflowTemplates(): void {
    // 개발 워크플로우 템플릿
    this.templates.set('development', {
      id: 'development',
      name: 'Development Workflow',
      description: 'Standard development workflow',
      intentTypes: ['development', 'build', 'create'],
      steps: [
        {
          id: 'analysis',
          name: 'Requirement Analysis',
          type: StepType.SEQUENTIAL,
          agents: ['AnalysisAgent'],
          dependencies: [],
          timeout: 300
        },
        {
          id: 'design',
          name: 'System Design',
          type: StepType.SEQUENTIAL,
          agents: ['DesignAgent'],
          dependencies: ['analysis'],
          timeout: 600
        },
        {
          id: 'implementation',
          name: 'Code Implementation',
          type: StepType.PARALLEL,
          agents: ['CodeAgent', 'UIAgent', 'APIAgent'],
          dependencies: ['design'],
          timeout: 1200
        },
        {
          id: 'testing',
          name: 'Testing & Validation',
          type: StepType.SEQUENTIAL,
          agents: ['TestAgent', 'SecurityAgent'],
          dependencies: ['implementation'],
          timeout: 900
        }
      ]
    });

    // 테스트 워크플로우 템플릿
    this.templates.set('testing', {
      id: 'testing',
      name: 'Testing Workflow',
      description: 'Comprehensive testing workflow',
      intentTypes: ['test', 'validate', 'verify'],
      steps: [
        {
          id: 'unit_test',
          name: 'Unit Testing',
          type: StepType.PARALLEL,
          agents: ['TestAgent'],
          dependencies: [],
          timeout: 600
        },
        {
          id: 'integration_test',
          name: 'Integration Testing',
          type: StepType.SEQUENTIAL,
          agents: ['TestAgent', 'APIAgent'],
          dependencies: ['unit_test'],
          timeout: 900
        },
        {
          id: 'security_test',
          name: 'Security Testing',
          type: StepType.SEQUENTIAL,
          agents: ['SecurityAgent'],
          dependencies: ['integration_test'],
          timeout: 1200
        }
      ]
    });
  }
}

class WorkflowValidator {
  async validate(workflow: Workflow): Promise<void> {
    // 순환 의존성 검사
    this.checkCircularDependencies(workflow.steps);
    
    // 의존성 존재 검사
    this.checkDependencyExistence(workflow.steps);
    
    // 에이전트 유효성 검사
    this.checkAgentValidity(workflow.steps);
  }

  private checkCircularDependencies(steps: WorkflowStep[]): void {
    const visited = new Set<string>();
    const recursionStack = new Set<string>();

    const hasCycle = (stepId: string): boolean => {
      if (recursionStack.has(stepId)) return true;
      if (visited.has(stepId)) return false;

      visited.add(stepId);
      recursionStack.add(stepId);

      const step = steps.find(s => s.id === stepId);
      if (step) {
        for (const dep of step.dependencies) {
          if (hasCycle(dep)) return true;
        }
      }

      recursionStack.delete(stepId);
      return false;
    };

    for (const step of steps) {
      if (hasCycle(step.id)) {
        throw new Error(`Circular dependency detected involving step: ${step.id}`);
      }
    }
  }

  private checkDependencyExistence(steps: WorkflowStep[]): void {
    const stepIds = new Set(steps.map(s => s.id));
    
    for (const step of steps) {
      for (const dep of step.dependencies) {
        if (!stepIds.has(dep)) {
          throw new Error(`Step ${step.id} depends on non-existent step: ${dep}`);
        }
      }
    }
  }

  private checkAgentValidity(steps: WorkflowStep[]): void {
    const validAgents = [
      'CodeAgent', 'UIAgent', 'APIAgent', 'TestAgent', 
      'SecurityAgent', 'DesignAgent', 'DeploymentAgent', 'AnalysisAgent'
    ];

    for (const step of steps) {
      for (const agent of step.agents) {
        if (!validAgents.includes(agent)) {
          throw new Error(`Invalid agent in step ${step.id}: ${agent}`);
        }
      }
    }
  }
}