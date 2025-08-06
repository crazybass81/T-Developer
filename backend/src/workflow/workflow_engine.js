const StepType = {
  SEQUENTIAL: "sequential",
  PARALLEL: "parallel",
  CONDITIONAL: "conditional"
};

class WorkflowEngine {
  constructor() {
    this.templates = new Map();
    this.validator = new WorkflowValidator();
    this.loadWorkflowTemplates();
  }

  async createWorkflow(intent, agents) {
    const template = this.selectTemplate(intent);
    
    let workflow;
    
    if (template) {
      workflow = this.applyTemplate(template, agents);
    } else {
      workflow = this.createDynamicWorkflow(intent, agents);
    }
    
    await this.validator.validate(workflow);
    workflow = this.optimizeWorkflow(workflow);
    
    return workflow;
  }

  createDynamicWorkflow(intent, agents) {
    const steps = [];
    const dependencies = this.analyzeDependencies(agents);
    const parallelGroups = this.identifyParallelTasks(dependencies);
    
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

  selectTemplate(intent) {
    for (const template of this.templates.values()) {
      if (template.intentTypes.includes(intent.type)) {
        return template;
      }
    }
    return null;
  }

  applyTemplate(template, agents) {
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

  analyzeDependencies(agents) {
    const dependencies = new Map();
    
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

  identifyParallelTasks(dependencies) {
    const groups = [];
    const processed = new Set();
    
    const independentAgents = Array.from(dependencies.entries())
      .filter(([_, deps]) => deps.length === 0)
      .map(([agent, _]) => agent);
    
    if (independentAgents.length > 0) {
      groups.push(independentAgents);
      independentAgents.forEach(agent => processed.add(agent));
    }

    while (processed.size < dependencies.size) {
      const nextGroup = [];
      
      for (const [agent, deps] of dependencies.entries()) {
        if (!processed.has(agent) && deps.every(dep => processed.has(dep))) {
          nextGroup.push(agent);
        }
      }
      
      if (nextGroup.length > 0) {
        groups.push(nextGroup);
        nextGroup.forEach(agent => processed.add(agent));
      } else {
        const remaining = Array.from(dependencies.keys()).filter(agent => !processed.has(agent));
        if (remaining.length > 0) {
          groups.push([remaining[0]]);
          processed.add(remaining[0]);
        }
      }
    }

    return groups;
  }

  mapAgentsToStep(step, availableAgents) {
    return step.agents.filter(agent => availableAgents.includes(agent));
  }

  calculateEstimatedDuration(steps) {
    let totalDuration = 0;
    
    steps.forEach(step => {
      if (step.type === StepType.PARALLEL) {
        totalDuration += Math.max(...step.agents.map(() => step.timeout));
      } else {
        totalDuration += step.agents.length * step.timeout;
      }
    });

    return totalDuration;
  }

  optimizeWorkflow(workflow) {
    const optimizedSteps = workflow.steps.map(step => ({
      ...step,
      dependencies: this.removeRedundantDependencies(step.dependencies, workflow.steps)
    }));

    const mergedSteps = this.mergeParallelizableSteps(optimizedSteps);

    return {
      ...workflow,
      steps: mergedSteps,
      estimatedDuration: this.calculateEstimatedDuration(mergedSteps)
    };
  }

  removeRedundantDependencies(dependencies, allSteps) {
    return dependencies.filter(dep => {
      const depStep = allSteps.find(s => s.id === dep);
      if (!depStep) return true;
      
      return !dependencies.some(otherDep => {
        const otherDepStep = allSteps.find(s => s.id === otherDep);
        return otherDepStep && otherDepStep.dependencies.includes(dep);
      });
    });
  }

  mergeParallelizableSteps(steps) {
    const merged = [];
    let i = 0;

    while (i < steps.length) {
      const currentStep = steps[i];
      
      if (currentStep.type === StepType.SEQUENTIAL && i < steps.length - 1) {
        const nextStep = steps[i + 1];
        
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
          i += 2;
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

  canMergeSteps(step1, step2) {
    const hasAgentConflict = step1.agents.some(agent => step2.agents.includes(agent));
    const hasDependencyConflict = step2.dependencies.includes(step1.id);
    
    return !hasAgentConflict && !hasDependencyConflict;
  }

  loadWorkflowTemplates() {
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
  async validate(workflow) {
    this.checkCircularDependencies(workflow.steps);
    this.checkDependencyExistence(workflow.steps);
    this.checkAgentValidity(workflow.steps);
  }

  checkCircularDependencies(steps) {
    const visited = new Set();
    const recursionStack = new Set();

    const hasCycle = (stepId) => {
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

  checkDependencyExistence(steps) {
    const stepIds = new Set(steps.map(s => s.id));
    
    for (const step of steps) {
      for (const dep of step.dependencies) {
        if (!stepIds.has(dep)) {
          throw new Error(`Step ${step.id} depends on non-existent step: ${dep}`);
        }
      }
    }
  }

  checkAgentValidity(steps) {
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

module.exports = { WorkflowEngine, WorkflowValidator, StepType };