import { Intent, WorkflowPlan, WorkflowStep } from '../agents/supervisor/supervisor-agent';

enum StepType {
  SEQUENTIAL = "sequential",
  PARALLEL = "parallel",
  CONDITIONAL = "conditional"
}

interface WorkflowTemplate {
  name: string;
  pattern: RegExp;
  steps: WorkflowStep[];
}

export class WorkflowEngine {
  private templates: WorkflowTemplate[] = [];
  
  constructor() {
    this.loadWorkflowTemplates();
  }
  
  async createWorkflow(intent: Intent, agents: string[]): Promise<WorkflowPlan> {
    // 1. 템플릿 선택
    const template = this.selectTemplate(intent);
    
    // 2. 워크플로우 생성
    let workflow: WorkflowPlan;
    
    if (template) {
      workflow = this.applyTemplate(template, agents);
    } else {
      workflow = this.createDynamicWorkflow(intent, agents);
    }
    
    // 3. 검증
    await this.validateWorkflow(workflow);
    
    // 4. 최적화
    workflow = this.optimizeWorkflow(workflow);
    
    return workflow;
  }
  
  private loadWorkflowTemplates(): void {
    this.templates = [
      {
        name: 'code-development',
        pattern: /code|develop|implement/i,
        steps: [
          {
            id: 'analyze',
            name: 'Analyze Requirements',
            agents: ['analysis-agent'],
            parallel: false,
            task: { type: 'analyze' }
          },
          {
            id: 'code',
            name: 'Generate Code',
            agents: ['code-agent'],
            parallel: false,
            task: { type: 'code' }
          },
          {
            id: 'test',
            name: 'Run Tests',
            agents: ['test-agent'],
            parallel: false,
            task: { type: 'test' }
          }
        ]
      }
    ];
  }
  
  private selectTemplate(intent: Intent): WorkflowTemplate | null {
    return this.templates.find(template => 
      template.pattern.test(intent.description)
    ) || null;
  }
  
  private applyTemplate(template: WorkflowTemplate, agents: string[]): WorkflowPlan {
    return {
      id: `workflow-${Date.now()}`,
      steps: template.steps.map(step => ({
        ...step,
        agents: agents.length > 0 ? agents : step.agents
      })),
      estimatedDuration: template.steps.length * 60000
    };
  }
  
  private createDynamicWorkflow(intent: Intent, agents: string[]): WorkflowPlan {
    // 의존성 분석
    const dependencies = this.analyzeDependencies(agents);
    
    // 병렬화 가능한 작업 식별
    const parallelGroups = this.identifyParallelTasks(dependencies);
    
    // 워크플로우 스텝 생성
    const steps: WorkflowStep[] = [];
    
    parallelGroups.forEach((group, index) => {
      const step: WorkflowStep = {
        id: `step-${index}`,
        name: group.length > 1 
          ? `Parallel execution: ${group.join(', ')}` 
          : `Execute: ${group[0]}`,
        agents: group,
        parallel: group.length > 1,
        task: { type: 'dynamic', agents: group }
      };
      
      steps.push(step);
    });
    
    return {
      id: `workflow-${Date.now()}`,
      steps,
      estimatedDuration: steps.length * 45000
    };
  }
  
  private analyzeDependencies(agents: string[]): Map<string, string[]> {
    const dependencies = new Map<string, string[]>();
    
    // 간단한 의존성 규칙
    agents.forEach(agent => {
      switch (agent) {
        case 'test-agent':
          dependencies.set(agent, ['code-agent']);
          break;
        case 'deploy-agent':
          dependencies.set(agent, ['test-agent', 'code-agent']);
          break;
        default:
          dependencies.set(agent, []);
      }
    });
    
    return dependencies;
  }
  
  private identifyParallelTasks(dependencies: Map<string, string[]>): string[][] {
    const groups: string[][] = [];
    const processed = new Set<string>();
    
    for (const [agent, deps] of dependencies) {
      if (processed.has(agent)) continue;
      
      if (deps.length === 0) {
        // 의존성이 없는 에이전트들은 병렬 실행 가능
        const parallelGroup = [agent];
        
        // 같은 레벨의 다른 에이전트들 찾기
        for (const [otherAgent, otherDeps] of dependencies) {
          if (!processed.has(otherAgent) && 
              otherAgent !== agent && 
              otherDeps.length === 0) {
            parallelGroup.push(otherAgent);
            processed.add(otherAgent);
          }
        }
        
        groups.push(parallelGroup);
        processed.add(agent);
      }
    }
    
    // 의존성이 있는 에이전트들은 순차 실행
    for (const [agent, deps] of dependencies) {
      if (!processed.has(agent)) {
        groups.push([agent]);
        processed.add(agent);
      }
    }
    
    return groups;
  }
  
  private async validateWorkflow(workflow: WorkflowPlan): Promise<void> {
    if (workflow.steps.length === 0) {
      throw new Error('Workflow must have at least one step');
    }
    
    // 순환 의존성 검사
    const stepIds = new Set(workflow.steps.map(s => s.id));
    workflow.steps.forEach(step => {
      if (!stepIds.has(step.id)) {
        throw new Error(`Invalid step reference: ${step.id}`);
      }
    });
  }
  
  private optimizeWorkflow(workflow: WorkflowPlan): WorkflowPlan {
    // 불필요한 스텝 제거
    const optimizedSteps = workflow.steps.filter(step => 
      step.agents.length > 0
    );
    
    return {
      ...workflow,
      steps: optimizedSteps,
      estimatedDuration: optimizedSteps.length * 45000
    };
  }
}