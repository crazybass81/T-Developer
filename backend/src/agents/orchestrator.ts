/**
 * T-Developer Agent Orchestrator
 * 에이전트 오케스트레이션 및 워크플로우 관리
 */

import { EventEmitter } from 'events';
import { v4 as uuidv4 } from 'uuid';
import { BaseAgent, AgentMessage } from './framework/base-agent';
import { Logger } from '../utils/logger';

/**
 * Workflow Definition
 */
export interface WorkflowDefinition {
  id: string;
  name: string;
  description?: string;
  steps: WorkflowStep[];
  variables?: Record<string, any>;
  timeout?: number;
}

/**
 * Workflow Step
 */
export interface WorkflowStep {
  id: string;
  agentType: string;
  action: string;
  input?: any;
  dependencies?: string[];
  condition?: string;
  retryPolicy?: {
    maxRetries: number;
    delay: number;
  };
}

/**
 * Workflow Execution State
 */
export interface WorkflowExecution {
  id: string;
  workflowId: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  currentStep?: string;
  context: Record<string, any>;
  results: Record<string, any>;
  startedAt: Date;
  completedAt?: Date;
  error?: Error;
}

/**
 * Agent Registry Entry
 */
interface AgentRegistryEntry {
  agent: BaseAgent;
  type: string;
  capabilities: string[];
  status: string;
  registeredAt: Date;
}

/**
 * Agent Orchestrator Class
 */
export class AgentOrchestrator extends EventEmitter {
  private agents: Map<string, AgentRegistryEntry>;
  private workflows: Map<string, WorkflowDefinition>;
  private executions: Map<string, WorkflowExecution>;
  private messageQueue: AgentMessage[];
  private logger: Logger;
  private isRunning: boolean;
  
  constructor() {
    super();
    this.agents = new Map();
    this.workflows = new Map();
    this.executions = new Map();
    this.messageQueue = [];
    this.logger = new Logger('AgentOrchestrator');
    this.isRunning = false;
  }
  
  /**
   * Start the orchestrator
   */
  async start(): Promise<void> {
    if (this.isRunning) {
      return;
    }
    
    this.isRunning = true;
    this.logger.info('Agent Orchestrator started');
    
    // Start message processing loop
    this.processMessageQueue();
    
    this.emit('orchestrator:started');
  }
  
  /**
   * Stop the orchestrator
   */
  async stop(): Promise<void> {
    this.isRunning = false;
    
    // Stop all agents
    for (const [agentId, entry] of this.agents) {
      try {
        // Agents should implement proper cleanup
        this.logger.info(`Stopping agent ${agentId}`);
      } catch (error) {
        this.logger.error(`Error stopping agent ${agentId}:`, error);
      }
    }
    
    this.logger.info('Agent Orchestrator stopped');
    this.emit('orchestrator:stopped');
  }
  
  /**
   * Register an agent
   */
  registerAgent(agent: BaseAgent, type: string, capabilities: string[] = []): void {
    const agentId = agent.getMetrics().agentId;
    
    if (this.agents.has(agentId)) {
      throw new Error(`Agent ${agentId} already registered`);
    }
    
    const entry: AgentRegistryEntry = {
      agent,
      type,
      capabilities,
      status: agent.getStatus(),
      registeredAt: new Date()
    };
    
    this.agents.set(agentId, entry);
    
    // Setup message handling
    this.setupAgentMessageHandling(agent);
    
    this.logger.info(`Agent registered: ${agentId} (type: ${type})`);
    this.emit('agent:registered', { agentId, type });
  }
  
  /**
   * Unregister an agent
   */
  unregisterAgent(agentId: string): void {
    const entry = this.agents.get(agentId);
    
    if (!entry) {
      throw new Error(`Agent ${agentId} not found`);
    }
    
    this.agents.delete(agentId);
    
    this.logger.info(`Agent unregistered: ${agentId}`);
    this.emit('agent:unregistered', { agentId });
  }
  
  /**
   * Get agent by ID
   */
  getAgent(agentId: string): BaseAgent | undefined {
    return this.agents.get(agentId)?.agent;
  }
  
  /**
   * Get agents by type
   */
  getAgentsByType(type: string): BaseAgent[] {
    const agents: BaseAgent[] = [];
    
    for (const entry of this.agents.values()) {
      if (entry.type === type) {
        agents.push(entry.agent);
      }
    }
    
    return agents;
  }
  
  /**
   * Get all registered agents
   */
  getAllAgents(): BaseAgent[] {
    return Array.from(this.agents.values()).map(entry => entry.agent);
  }
  
  /**
   * Register a workflow
   */
  registerWorkflow(workflow: WorkflowDefinition): void {
    if (this.workflows.has(workflow.id)) {
      throw new Error(`Workflow ${workflow.id} already registered`);
    }
    
    this.workflows.set(workflow.id, workflow);
    
    this.logger.info(`Workflow registered: ${workflow.name} (${workflow.id})`);
    this.emit('workflow:registered', workflow);
  }
  
  /**
   * Execute a workflow
   */
  async executeWorkflow(workflowId: string, input?: Record<string, any>): Promise<WorkflowExecution> {
    const workflow = this.workflows.get(workflowId);
    
    if (!workflow) {
      throw new Error(`Workflow ${workflowId} not found`);
    }
    
    const execution: WorkflowExecution = {
      id: uuidv4(),
      workflowId,
      status: 'running',
      context: { ...workflow.variables, ...input },
      results: {},
      startedAt: new Date()
    };
    
    this.executions.set(execution.id, execution);
    
    this.logger.info(`Starting workflow execution: ${execution.id}`);
    this.emit('workflow:started', execution);
    
    try {
      // Execute workflow steps
      for (const step of workflow.steps) {
        // Check dependencies
        if (step.dependencies) {
          await this.waitForDependencies(execution, step.dependencies);
        }
        
        // Check condition
        if (step.condition && !this.evaluateCondition(step.condition, execution.context)) {
          this.logger.info(`Skipping step ${step.id} due to condition`);
          continue;
        }
        
        // Execute step
        execution.currentStep = step.id;
        const result = await this.executeStep(step, execution);
        execution.results[step.id] = result;
        
        // Update context with result
        execution.context[step.id] = result;
      }
      
      execution.status = 'completed';
      execution.completedAt = new Date();
      
      this.logger.info(`Workflow execution completed: ${execution.id}`);
      this.emit('workflow:completed', execution);
      
    } catch (error) {
      execution.status = 'failed';
      execution.error = error as Error;
      execution.completedAt = new Date();
      
      this.logger.error(`Workflow execution failed: ${execution.id}`, error);
      this.emit('workflow:failed', execution);
      
      throw error;
    }
    
    return execution;
  }
  
  /**
   * Cancel a workflow execution
   */
  async cancelWorkflow(executionId: string): Promise<void> {
    const execution = this.executions.get(executionId);
    
    if (!execution) {
      throw new Error(`Execution ${executionId} not found`);
    }
    
    if (execution.status !== 'running') {
      throw new Error(`Cannot cancel execution in status ${execution.status}`);
    }
    
    execution.status = 'cancelled';
    execution.completedAt = new Date();
    
    this.logger.info(`Workflow execution cancelled: ${executionId}`);
    this.emit('workflow:cancelled', execution);
  }
  
  /**
   * Send message to agent
   */
  async sendMessage(targetAgentId: string, message: AgentMessage): Promise<void> {
    const agent = this.getAgent(targetAgentId);
    
    if (!agent) {
      throw new Error(`Agent ${targetAgentId} not found`);
    }
    
    // Add to message queue
    this.messageQueue.push(message);
    
    this.emit('message:queued', message);
  }
  
  /**
   * Process message queue
   */
  private async processMessageQueue(): Promise<void> {
    while (this.isRunning) {
      if (this.messageQueue.length > 0) {
        const message = this.messageQueue.shift();
        
        if (message) {
          try {
            const agent = this.getAgent(message.target);
            
            if (agent) {
              const response = await agent.handleMessage(message);
              
              if (response) {
                // Route response back if needed
                if (response.target && response.target !== message.target) {
                  this.messageQueue.push(response);
                }
              }
            }
          } catch (error) {
            this.logger.error('Error processing message:', error);
          }
        }
      }
      
      // Small delay to prevent busy waiting
      await new Promise(resolve => setTimeout(resolve, 10));
    }
  }
  
  /**
   * Execute a workflow step
   */
  private async executeStep(step: WorkflowStep, execution: WorkflowExecution): Promise<any> {
    const agents = this.getAgentsByType(step.agentType);
    
    if (agents.length === 0) {
      throw new Error(`No agents of type ${step.agentType} available`);
    }
    
    // Select first available agent (could implement load balancing)
    const agent = agents[0];
    
    // Prepare input
    const input = this.resolveInput(step.input, execution.context);
    
    // Create message
    const message: AgentMessage = {
      id: uuidv4(),
      type: 'request',
      source: 'orchestrator',
      target: agent.getMetrics().agentId,
      payload: {
        action: step.action,
        input
      },
      timestamp: new Date()
    };
    
    // Execute with retry
    let lastError: Error | undefined;
    const maxRetries = step.retryPolicy?.maxRetries || 0;
    
    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        const response = await agent.handleMessage(message);
        
        if (response && response.type === 'response') {
          return response.payload;
        } else if (response && response.type === 'error') {
          throw new Error(response.payload.error);
        }
      } catch (error) {
        lastError = error as Error;
        
        if (attempt < maxRetries) {
          const delay = step.retryPolicy?.delay || 1000;
          await new Promise(resolve => setTimeout(resolve, delay * (attempt + 1)));
        }
      }
    }
    
    throw lastError || new Error(`Step ${step.id} failed`);
  }
  
  /**
   * Wait for step dependencies
   */
  private async waitForDependencies(execution: WorkflowExecution, dependencies: string[]): Promise<void> {
    for (const dep of dependencies) {
      while (!execution.results[dep] && execution.status === 'running') {
        await new Promise(resolve => setTimeout(resolve, 100));
      }
      
      if (execution.status !== 'running') {
        throw new Error('Workflow execution cancelled or failed');
      }
    }
  }
  
  /**
   * Evaluate condition
   */
  private evaluateCondition(condition: string, context: Record<string, any>): boolean {
    try {
      // Simple condition evaluation (could use a proper expression evaluator)
      const func = new Function('context', `return ${condition}`);
      return func(context);
    } catch (error) {
      this.logger.error(`Error evaluating condition: ${condition}`, error);
      return false;
    }
  }
  
  /**
   * Resolve input with context variables
   */
  private resolveInput(input: any, context: Record<string, any>): any {
    if (typeof input === 'string' && input.startsWith('$')) {
      // Variable reference
      const path = input.substring(1).split('.');
      let value = context;
      
      for (const key of path) {
        value = value[key];
        if (value === undefined) break;
      }
      
      return value;
    } else if (typeof input === 'object' && input !== null) {
      // Recursively resolve object properties
      const resolved: any = Array.isArray(input) ? [] : {};
      
      for (const [key, value] of Object.entries(input)) {
        resolved[key] = this.resolveInput(value, context);
      }
      
      return resolved;
    }
    
    return input;
  }
  
  /**
   * Setup agent message handling
   */
  private setupAgentMessageHandling(agent: BaseAgent): void {
    // This would typically set up event listeners or message routing
    // For now, we'll use the orchestrator's message queue
  }
  
  /**
   * Get orchestrator metrics
   */
  getMetrics(): {
    registeredAgents: number;
    registeredWorkflows: number;
    activeExecutions: number;
    queuedMessages: number;
  } {
    const activeExecutions = Array.from(this.executions.values())
      .filter(e => e.status === 'running').length;
    
    return {
      registeredAgents: this.agents.size,
      registeredWorkflows: this.workflows.size,
      activeExecutions,
      queuedMessages: this.messageQueue.length
    };
  }
}

// Export singleton instance
export const orchestrator = new AgentOrchestrator();