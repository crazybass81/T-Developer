import { AgentType, getExecutionOrder, getAgentDependencies } from './agent-types';
import { AgentManager } from './agent-manager';
import { AgentCommunicationManager } from './communication';
import { AgentMessage, AgentContext } from './base-agent';
import { v4 as uuidv4 } from 'uuid';

export interface WorkflowStep {
  agentType: AgentType;
  agentId?: string;
  input: any;
  output?: any;
  status: 'pending' | 'running' | 'completed' | 'failed';
  startTime?: Date;
  endTime?: Date;
  error?: string;
}

export interface WorkflowConfig {
  projectId: string;
  userId: string;
  sessionId: string;
  initialInput: any;
  steps?: AgentType[];
}

export class AgentWorkflow {
  private agentManager: AgentManager;
  private communicationManager: AgentCommunicationManager;
  private steps: WorkflowStep[] = [];
  private currentStepIndex = 0;
  private status: 'idle' | 'running' | 'completed' | 'failed' = 'idle';
  
  constructor(
    agentManager: AgentManager,
    communicationManager: AgentCommunicationManager
  ) {
    this.agentManager = agentManager;
    this.communicationManager = communicationManager;
  }
  
  async execute(config: WorkflowConfig): Promise<any> {
    this.status = 'running';
    
    try {
      // Initialize workflow steps
      const executionOrder = config.steps || getExecutionOrder();
      this.initializeSteps(executionOrder, config.initialInput);
      
      console.log(`🚀 Starting workflow with ${this.steps.length} steps`);
      
      // Execute steps sequentially
      for (let i = 0; i < this.steps.length; i++) {
        this.currentStepIndex = i;
        const step = this.steps[i];
        
        console.log(`📋 Executing step ${i + 1}/${this.steps.length}: ${step.agentType}`);
        
        await this.executeStep(step, config);
        
        if (step.status === 'failed') {
          this.status = 'failed';
          throw new Error(`Workflow failed at step ${step.agentType}: ${step.error}`);
        }
      }
      
      this.status = 'completed';
      console.log('✅ Workflow completed successfully');
      
      return this.getWorkflowResult();
      
    } catch (error) {
      this.status = 'failed';
      console.error('❌ Workflow failed:', error);
      throw error;
    }
  }
  
  private initializeSteps(agentTypes: AgentType[], initialInput: any): void {
    this.steps = agentTypes.map((agentType, index) => ({
      agentType,
      input: index === 0 ? initialInput : null,
      status: 'pending' as const
    }));
  }
  
  private async executeStep(step: WorkflowStep, config: WorkflowConfig): Promise<void> {
    step.status = 'running';
    step.startTime = new Date();
    
    try {
      // Create agent if not exists
      if (!step.agentId) {
        step.agentId = await this.agentManager.createAgent(step.agentType);
        
        // Start agent
        const context: AgentContext = {
          projectId: config.projectId,
          userId: config.userId,
          sessionId: config.sessionId,
          metadata: {
            workflowStep: this.currentStepIndex,
            agentType: step.agentType
          }
        };
        
        await this.agentManager.startAgent(step.agentId, context);
      }
      
      // Prepare input (combine with previous step output)
      const input = this.prepareStepInput(step);
      
      // Send message to agent
      const message: AgentMessage = {
        id: uuidv4(),
        type: 'request',
        source: 'workflow-manager',
        target: step.agentId,
        payload: {
          action: 'process',
          data: input
        },
        timestamp: new Date()
      };
      
      const response = await this.agentManager.sendMessage(step.agentId, message);
      
      if (response.type === 'error') {
        throw new Error(response.payload.error);
      }
      
      step.output = response.payload;
      step.status = 'completed';
      step.endTime = new Date();
      
      console.log(`✅ Step ${step.agentType} completed in ${step.endTime.getTime() - step.startTime!.getTime()}ms`);
      
    } catch (error) {
      step.status = 'failed';
      step.endTime = new Date();
      step.error = error instanceof Error ? error.message : 'Unknown error';
      
      console.error(`❌ Step ${step.agentType} failed:`, error);
      throw error;
    }
  }
  
  private prepareStepInput(step: WorkflowStep): any {
    // For first step, use initial input
    if (this.currentStepIndex === 0) {
      return step.input;
    }
    
    // Combine current step input with previous outputs
    const previousOutputs: Record<string, any> = {};
    
    for (let i = 0; i < this.currentStepIndex; i++) {
      const prevStep = this.steps[i];
      if (prevStep.output) {
        previousOutputs[prevStep.agentType] = prevStep.output;
      }
    }
    
    return {
      ...step.input,
      previousOutputs,
      context: {
        currentStep: this.currentStepIndex,
        totalSteps: this.steps.length
      }
    };
  }
  
  private getWorkflowResult(): any {
    const lastStep = this.steps[this.steps.length - 1];
    
    return {
      success: true,
      result: lastStep.output,
      steps: this.steps.map(step => ({
        agentType: step.agentType,
        status: step.status,
        duration: step.startTime && step.endTime 
          ? step.endTime.getTime() - step.startTime.getTime()
          : null,
        error: step.error
      })),
      totalDuration: this.getTotalDuration(),
      completedAt: new Date()
    };
  }
  
  private getTotalDuration(): number {
    const firstStep = this.steps.find(s => s.startTime);
    const lastStep = this.steps.slice().reverse().find(s => s.endTime);
    
    if (firstStep?.startTime && lastStep?.endTime) {
      return lastStep.endTime.getTime() - firstStep.startTime.getTime();
    }
    
    return 0;
  }
  
  getStatus(): string {
    return this.status;
  }
  
  getProgress(): { current: number; total: number; percentage: number } {
    const completed = this.steps.filter(s => s.status === 'completed').length;
    
    return {
      current: completed,
      total: this.steps.length,
      percentage: Math.round((completed / this.steps.length) * 100)
    };
  }
  
  getSteps(): WorkflowStep[] {
    return [...this.steps];
  }
}