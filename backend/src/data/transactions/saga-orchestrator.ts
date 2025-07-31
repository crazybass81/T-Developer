// backend/src/data/transactions/saga-orchestrator.ts
export interface SagaStep {
  name: string;
  execute: (context: any) => Promise<any>;
  compensate: (context: any) => Promise<void>;
  timeout?: number;
}

export interface SagaDefinition {
  name: string;
  steps: SagaStep[];
  timeout?: number;
}

export interface SagaExecution {
  id: string;
  sagaName: string;
  status: 'running' | 'completed' | 'failed' | 'compensating' | 'compensated';
  currentStep: number;
  context: any;
  startedAt: Date;
  completedAt?: Date;
  error?: string;
}

export class SagaOrchestrator {
  private executions = new Map<string, SagaExecution>();

  async executeSaga(definition: SagaDefinition, initialContext: any = {}): Promise<SagaExecution> {
    const execution: SagaExecution = {
      id: crypto.randomUUID(),
      sagaName: definition.name,
      status: 'running',
      currentStep: 0,
      context: initialContext,
      startedAt: new Date()
    };

    this.executions.set(execution.id, execution);

    try {
      // Execute steps sequentially
      for (let i = 0; i < definition.steps.length; i++) {
        execution.currentStep = i;
        const step = definition.steps[i];

        try {
          const result = await this.executeStepWithTimeout(step, execution.context);
          execution.context = { ...execution.context, ...result };
        } catch (error) {
          // Step failed, start compensation
          execution.status = 'compensating';
          execution.error = error instanceof Error ? error.message : 'Unknown error';
          
          await this.compensateSteps(definition.steps, i, execution.context);
          
          execution.status = 'compensated';
          execution.completedAt = new Date();
          throw error;
        }
      }

      execution.status = 'completed';
      execution.completedAt = new Date();
      return execution;

    } catch (error) {
      execution.status = 'failed';
      execution.completedAt = new Date();
      execution.error = error instanceof Error ? error.message : 'Unknown error';
      throw error;
    }
  }

  async getSagaExecution(id: string): Promise<SagaExecution | null> {
    return this.executions.get(id) || null;
  }

  private async executeStepWithTimeout(step: SagaStep, context: any): Promise<any> {
    const timeout = step.timeout || 30000; // 30 seconds default
    
    return Promise.race([
      step.execute(context),
      new Promise((_, reject) => 
        setTimeout(() => reject(new Error(`Step ${step.name} timed out`)), timeout)
      )
    ]);
  }

  private async compensateSteps(steps: SagaStep[], failedStepIndex: number, context: any): Promise<void> {
    // Compensate in reverse order
    for (let i = failedStepIndex - 1; i >= 0; i--) {
      try {
        await steps[i].compensate(context);
      } catch (error) {
        console.error(`Compensation failed for step ${steps[i].name}:`, error);
      }
    }
  }
}