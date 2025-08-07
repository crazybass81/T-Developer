/**
 * Saga Orchestrator for Distributed Transaction Management
 * Implements the Saga pattern for long-running transactions
 */

import { TransactionManager, TransactionItem } from './transaction-manager';
import { v4 as uuidv4 } from 'uuid';

export interface SagaStep {
  id: string;
  name: string;
  execute: () => Promise<void>;
  compensate: () => Promise<void>;
  retryable?: boolean;
  timeout?: number;
}

export interface SagaOptions {
  maxRetries?: number;
  enableLogging?: boolean;
  timeoutMs?: number;
}

export enum SagaStatus {
  PENDING = 'PENDING',
  EXECUTING = 'EXECUTING',
  COMPLETED = 'COMPLETED',
  COMPENSATING = 'COMPENSATING',
  COMPENSATED = 'COMPENSATED',
  FAILED = 'FAILED'
}

export class SagaOrchestrator {
  private steps: SagaStep[] = [];
  private executedSteps: SagaStep[] = [];
  private status: SagaStatus = SagaStatus.PENDING;
  private sagaId: string;
  private options: Required<SagaOptions>;

  constructor(options: SagaOptions = {}) {
    this.sagaId = uuidv4();
    this.options = {
      maxRetries: 3,
      enableLogging: true,
      timeoutMs: 30000,
      ...options
    };
  }

  public addStep(step: SagaStep): this {
    this.steps.push(step);
    return this;
  }

  public async execute(): Promise<void> {
    this.status = SagaStatus.EXECUTING;
    
    try {
      for (const step of this.steps) {
        await step.execute();
        this.executedSteps.push(step);
      }
      
      this.status = SagaStatus.COMPLETED;
    } catch (error) {
      this.status = SagaStatus.COMPENSATING;
      await this.compensate();
      throw error;
    }
  }

  private async compensate(): Promise<void> {
    // Execute compensation in reverse order
    for (let i = this.executedSteps.length - 1; i >= 0; i--) {
      try {
        await this.executedSteps[i].compensate();
      } catch (error) {
        console.error(`Compensation failed for step ${this.executedSteps[i].name}:`, error);
      }
    }
    
    this.status = SagaStatus.COMPENSATED;
  }

  public getStatus(): SagaStatus {
    return this.status;
  }

  public getSagaId(): string {
    return this.sagaId;
  }
}