export interface RecoveryStrategy {
  maxRetries: number;
  backoffMultiplier: number;
  maxBackoffSeconds: number;
  retryableErrors: string[];
}

export interface RecoveryAction {
  action: 'retry' | 'compensate' | 'fail';
  delaySeconds?: number;
  attemptNumber?: number;
  reason?: string;
}

export class RecoveryManager {
  private strategies = new Map<string, RecoveryStrategy>();
  private recoveryHistory = new Map<string, any[]>();

  constructor() {
    this.setupDefaultStrategies();
  }

  private setupDefaultStrategies(): void {
    // 기본 재시도 전략
    this.strategies.set('default', {
      maxRetries: 3,
      backoffMultiplier: 2,
      maxBackoffSeconds: 30,
      retryableErrors: ['TIMEOUT', 'CONNECTION_ERROR', 'TEMPORARY_FAILURE']
    });

    // 네트워크 오류 전략
    this.strategies.set('network', {
      maxRetries: 5,
      backoffMultiplier: 1.5,
      maxBackoffSeconds: 60,
      retryableErrors: ['ECONNRESET', 'ENOTFOUND', 'ETIMEDOUT']
    });

    // 리소스 부족 전략
    this.strategies.set('resource', {
      maxRetries: 10,
      backoffMultiplier: 3,
      maxBackoffSeconds: 120,
      retryableErrors: ['RESOURCE_EXHAUSTED', 'RATE_LIMITED']
    });
  }

  async handleFailure(taskId: string, error: Error, taskType = 'default'): Promise<RecoveryAction> {
    const strategy = this.getStrategy(taskType);
    const history = this.getHistory(taskId);

    // 재시도 가능 여부 확인
    if (!this.isRetryable(error, strategy)) {
      return { action: 'fail', reason: 'Non-retryable error' };
    }

    // 재시도 횟수 확인
    if (history.length >= strategy.maxRetries) {
      return { action: 'fail', reason: 'Max retries exceeded' };
    }

    // 백오프 계산
    const backoffTime = this.calculateBackoff(history.length, strategy);

    // 히스토리 기록
    this.recordAttempt(taskId, error, backoffTime);

    return {
      action: 'retry',
      delaySeconds: backoffTime,
      attemptNumber: history.length + 1
    };
  }

  async executeRecovery(taskId: string, action: RecoveryAction, task: () => Promise<any>): Promise<any> {
    switch (action.action) {
      case 'retry':
        if (action.delaySeconds) {
          await this.delay(action.delaySeconds * 1000);
        }
        return await this.executeWithRetry(taskId, task);

      case 'compensate':
        return await this.executeCompensation(taskId);

      case 'fail':
        throw new Error(`Task ${taskId} failed permanently: ${action.reason}`);
    }
  }

  private async executeWithRetry(taskId: string, task: () => Promise<any>): Promise<any> {
    try {
      const result = await task();
      this.clearHistory(taskId); // 성공 시 히스토리 클리어
      return result;
    } catch (error) {
      const recoveryAction = await this.handleFailure(taskId, error instanceof Error ? error : new Error(String(error)));
      
      if (recoveryAction.action === 'retry') {
        return await this.executeRecovery(taskId, recoveryAction, task);
      } else {
        throw error;
      }
    }
  }

  private getStrategy(taskType: string): RecoveryStrategy {
    return this.strategies.get(taskType) || this.strategies.get('default')!;
  }

  private getHistory(taskId: string): any[] {
    return this.recoveryHistory.get(taskId) || [];
  }

  private isRetryable(error: Error, strategy: RecoveryStrategy): boolean {
    return strategy.retryableErrors.some(pattern => 
      error.message.includes(pattern) || error.name.includes(pattern)
    );
  }

  private calculateBackoff(attemptNumber: number, strategy: RecoveryStrategy): number {
    const backoff = Math.min(
      strategy.backoffMultiplier ** attemptNumber,
      strategy.maxBackoffSeconds
    );

    // Jitter 추가로 재시도 폭주 방지
    const jitter = Math.random() * 0.3 * backoff;
    return Math.floor(backoff + jitter);
  }

  private recordAttempt(taskId: string, error: Error, backoffTime: number): void {
    const history = this.getHistory(taskId);
    history.push({
      timestamp: new Date(),
      error: error.message,
      backoffTime,
      attemptNumber: history.length + 1
    });
    this.recoveryHistory.set(taskId, history);
  }

  private clearHistory(taskId: string): void {
    this.recoveryHistory.delete(taskId);
  }

  private async executeCompensation(taskId: string): Promise<any> {
    // 보상 트랜잭션 실행 (실제로는 더 복잡한 로직)
    console.log(`Executing compensation for task: ${taskId}`);
    return { compensated: true, taskId };
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // 회로 차단기 패턴
  private circuitBreakers = new Map<string, CircuitBreaker>();

  getCircuitBreaker(serviceId: string): CircuitBreaker {
    if (!this.circuitBreakers.has(serviceId)) {
      this.circuitBreakers.set(serviceId, new CircuitBreaker(serviceId));
    }
    return this.circuitBreakers.get(serviceId)!;
  }
}

class CircuitBreaker {
  private state: 'closed' | 'open' | 'half-open' = 'closed';
  private failureCount = 0;
  private lastFailureTime = 0;
  private readonly failureThreshold = 5;
  private readonly timeout = 60000; // 1분

  constructor(private serviceId: string) {}

  async execute<T>(operation: () => Promise<T>): Promise<T> {
    if (this.state === 'open') {
      if (Date.now() - this.lastFailureTime > this.timeout) {
        this.state = 'half-open';
      } else {
        throw new Error(`Circuit breaker is open for ${this.serviceId}`);
      }
    }

    try {
      const result = await operation();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  private onSuccess(): void {
    this.failureCount = 0;
    this.state = 'closed';
  }

  private onFailure(): void {
    this.failureCount++;
    this.lastFailureTime = Date.now();

    if (this.failureCount >= this.failureThreshold) {
      this.state = 'open';
    }
  }
}