// Task 1.16.2: 자동 복구 메커니즘
export interface RecoveryStrategy {
  canRecover(error: Error): boolean;
  recover(error: Error, context: any): Promise<any>;
  maxRetries: number;
}

export class RetryStrategy implements RecoveryStrategy {
  maxRetries: number;
  private backoffMultiplier: number;

  constructor(maxRetries: number = 3, backoffMultiplier: number = 2) {
    this.maxRetries = maxRetries;
    this.backoffMultiplier = backoffMultiplier;
  }

  canRecover(error: Error): boolean {
    return error.name === 'TimeoutError' || 
           error.name === 'NetworkError' ||
           error.message.includes('ECONNRESET');
  }

  async recover(error: Error, context: any): Promise<any> {
    const { operation, attempt = 0 } = context;
    
    if (attempt >= this.maxRetries) {
      throw error;
    }

    const delay = Math.pow(this.backoffMultiplier, attempt) * 1000;
    await new Promise(resolve => setTimeout(resolve, delay));

    return operation({ ...context, attempt: attempt + 1 });
  }
}

export class CircuitBreakerStrategy implements RecoveryStrategy {
  maxRetries: number = 5;
  private failures: Map<string, number> = new Map();
  private lastFailureTime: Map<string, number> = new Map();
  private readonly threshold = 5;
  private readonly timeout = 60000; // 1분

  canRecover(error: Error): boolean {
    return error.name === 'ExternalServiceError';
  }

  async recover(error: Error, context: any): Promise<any> {
    const { serviceId, operation } = context;
    const failures = this.failures.get(serviceId) || 0;
    const lastFailure = this.lastFailureTime.get(serviceId) || 0;

    // Circuit breaker open
    if (failures >= this.threshold) {
      if (Date.now() - lastFailure < this.timeout) {
        throw new Error('Circuit breaker is open');
      }
      // Half-open state
      this.failures.set(serviceId, 0);
    }

    try {
      const result = await operation();
      this.failures.set(serviceId, 0);
      return result;
    } catch (err) {
      this.failures.set(serviceId, failures + 1);
      this.lastFailureTime.set(serviceId, Date.now());
      throw err;
    }
  }
}

export class ErrorRecoveryManager {
  private strategies: RecoveryStrategy[] = [];

  constructor() {
    this.strategies.push(new RetryStrategy());
    this.strategies.push(new CircuitBreakerStrategy());
  }

  async attemptRecovery(error: Error, context: any): Promise<any> {
    for (const strategy of this.strategies) {
      if (strategy.canRecover(error)) {
        try {
          return await strategy.recover(error, context);
        } catch (recoveryError) {
          console.error('Recovery failed:', recoveryError);
        }
      }
    }
    throw error;
  }

  addStrategy(strategy: RecoveryStrategy): void {
    this.strategies.push(strategy);
  }
}