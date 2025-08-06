export interface Task {
  id: string;
  type: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  retryCount: number;
  maxRetries: number;
  lastError?: string;
  data?: any;
}

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

export interface RecoveryAttempt {
  taskId: string;
  attemptNumber: number;
  timestamp: string;
  error: string;
  action: string;
}

export class RecoveryManager {
  private strategies = new Map<string, RecoveryStrategy>();
  private recoveryHistory = new Map<string, RecoveryAttempt[]>();
  private retryQueue = new Map<string, NodeJS.Timeout>();

  constructor() {
    this.initializeDefaultStrategies();
  }

  private initializeDefaultStrategies(): void {
    // 기본 복구 전략
    this.strategies.set('default', {
      maxRetries: 3,
      backoffMultiplier: 2,
      maxBackoffSeconds: 60,
      retryableErrors: ['TIMEOUT', 'CONNECTION_ERROR', 'TEMPORARY_FAILURE']
    });

    // 네트워크 관련 태스크
    this.strategies.set('network', {
      maxRetries: 5,
      backoffMultiplier: 1.5,
      maxBackoffSeconds: 30,
      retryableErrors: ['TIMEOUT', 'CONNECTION_ERROR', 'DNS_ERROR', 'HTTP_5XX']
    });

    // 데이터베이스 관련 태스크
    this.strategies.set('database', {
      maxRetries: 3,
      backoffMultiplier: 2,
      maxBackoffSeconds: 120,
      retryableErrors: ['CONNECTION_TIMEOUT', 'DEADLOCK', 'TEMPORARY_FAILURE']
    });

    // AI 모델 관련 태스크
    this.strategies.set('ai_model', {
      maxRetries: 2,
      backoffMultiplier: 3,
      maxBackoffSeconds: 180,
      retryableErrors: ['MODEL_TIMEOUT', 'RATE_LIMIT', 'TEMPORARY_UNAVAILABLE']
    });
  }

  async handleFailure(task: Task, error: Error): Promise<RecoveryAction> {
    const strategy = this.getStrategy(task.type);
    const history = this.getHistory(task.id);

    // 재시도 가능 여부 확인
    if (!this.isRetryable(error, strategy)) {
      return { 
        action: 'fail', 
        reason: `Non-retryable error: ${error.message}` 
      };
    }

    // 재시도 횟수 확인
    if (history.length >= strategy.maxRetries) {
      return { 
        action: 'fail', 
        reason: `Max retries (${strategy.maxRetries}) exceeded` 
      };
    }

    // 백오프 계산
    const backoffTime = this.calculateBackoff(history.length, strategy);

    // 복구 시도 기록
    this.recordRecoveryAttempt(task.id, history.length + 1, error.message, 'retry');

    return {
      action: 'retry',
      delaySeconds: backoffTime,
      attemptNumber: history.length + 1
    };
  }

  async executeRecovery(task: Task, action: RecoveryAction): Promise<void> {
    switch (action.action) {
      case 'retry':
        await this.scheduleRetry(task, action.delaySeconds || 0);
        break;
      case 'compensate':
        await this.executeCompensation(task);
        break;
      case 'fail':
        await this.handlePermanentFailure(task, action.reason);
        break;
    }
  }

  private getStrategy(taskType: string): RecoveryStrategy {
    return this.strategies.get(taskType) || this.strategies.get('default')!;
  }

  private getHistory(taskId: string): RecoveryAttempt[] {
    return this.recoveryHistory.get(taskId) || [];
  }

  private isRetryable(error: Error, strategy: RecoveryStrategy): boolean {
    const errorType = this.classifyError(error);
    return strategy.retryableErrors.includes(errorType);
  }

  private classifyError(error: Error): string {
    const message = error.message.toLowerCase();
    
    if (message.includes('timeout')) return 'TIMEOUT';
    if (message.includes('connection')) return 'CONNECTION_ERROR';
    if (message.includes('rate limit')) return 'RATE_LIMIT';
    if (message.includes('temporary')) return 'TEMPORARY_FAILURE';
    if (message.includes('deadlock')) return 'DEADLOCK';
    if (message.includes('dns')) return 'DNS_ERROR';
    if (message.includes('5')) return 'HTTP_5XX';
    
    return 'UNKNOWN_ERROR';
  }

  private calculateBackoff(attemptNumber: number, strategy: RecoveryStrategy): number {
    const baseBackoff = Math.min(
      strategy.backoffMultiplier ** attemptNumber,
      strategy.maxBackoffSeconds
    );

    // Jitter 추가로 재시도 폭주 방지 (±30%)
    const jitter = Math.random() * 0.6 - 0.3;
    const backoffWithJitter = baseBackoff * (1 + jitter);

    return Math.max(1, Math.floor(backoffWithJitter));
  }

  private recordRecoveryAttempt(
    taskId: string,
    attemptNumber: number,
    error: string,
    action: string
  ): void {
    if (!this.recoveryHistory.has(taskId)) {
      this.recoveryHistory.set(taskId, []);
    }

    const attempt: RecoveryAttempt = {
      taskId,
      attemptNumber,
      timestamp: new Date().toISOString(),
      error,
      action
    };

    this.recoveryHistory.get(taskId)!.push(attempt);
  }

  private async scheduleRetry(task: Task, delaySeconds: number): Promise<void> {
    // 기존 재시도 스케줄 취소
    const existingTimeout = this.retryQueue.get(task.id);
    if (existingTimeout) {
      clearTimeout(existingTimeout);
    }

    // 새 재시도 스케줄
    const timeout = setTimeout(async () => {
      try {
        await this.executeTaskRetry(task);
        this.retryQueue.delete(task.id);
      } catch (error) {
        console.error(`Retry execution failed for task ${task.id}:`, error);
      }
    }, delaySeconds * 1000);

    this.retryQueue.set(task.id, timeout);
    
    console.log(`Scheduled retry for task ${task.id} in ${delaySeconds} seconds`);
  }

  private async executeTaskRetry(task: Task): Promise<void> {
    // 태스크 재실행 로직 (실제 구현에서는 워크플로우 엔진과 연동)
    console.log(`Retrying task ${task.id} (attempt ${task.retryCount + 1})`);
    
    // 재시도 카운트 증가
    task.retryCount++;
    task.status = 'pending';
    
    // 워크플로우 엔진에 재실행 요청
    // await this.workflowEngine.retryTask(task);
  }

  private async executeCompensation(task: Task): Promise<void> {
    console.log(`Executing compensation for task ${task.id}`);
    
    // 보상 트랜잭션 실행
    // 예: 이전 단계 롤백, 리소스 정리 등
    
    this.recordRecoveryAttempt(task.id, 0, 'Compensation executed', 'compensate');
  }

  private async handlePermanentFailure(task: Task, reason?: string): Promise<void> {
    console.log(`Permanent failure for task ${task.id}: ${reason}`);
    
    task.status = 'failed';
    task.lastError = reason;
    
    this.recordRecoveryAttempt(task.id, 0, reason || 'Permanent failure', 'fail');
    
    // 실패 알림 발송
    await this.notifyFailure(task, reason);
  }

  private async notifyFailure(task: Task, reason?: string): Promise<void> {
    // 실패 알림 로직 (이메일, Slack, 로그 등)
    console.error(`Task ${task.id} permanently failed: ${reason}`);
  }

  // 복구 전략 설정
  setStrategy(taskType: string, strategy: RecoveryStrategy): void {
    this.strategies.set(taskType, strategy);
  }

  // 복구 히스토리 조회
  getRecoveryHistory(taskId: string): RecoveryAttempt[] {
    return this.getHistory(taskId);
  }

  // 복구 통계
  getRecoveryStats(): {
    totalAttempts: number;
    successfulRecoveries: number;
    permanentFailures: number;
    averageRetryCount: number;
  } {
    let totalAttempts = 0;
    let successfulRecoveries = 0;
    let permanentFailures = 0;
    let totalRetryCount = 0;

    for (const history of this.recoveryHistory.values()) {
      totalAttempts += history.length;
      
      const lastAttempt = history[history.length - 1];
      if (lastAttempt.action === 'retry') {
        successfulRecoveries++;
      } else if (lastAttempt.action === 'fail') {
        permanentFailures++;
      }
      
      totalRetryCount += history.filter(a => a.action === 'retry').length;
    }

    return {
      totalAttempts,
      successfulRecoveries,
      permanentFailures,
      averageRetryCount: this.recoveryHistory.size > 0 
        ? totalRetryCount / this.recoveryHistory.size 
        : 0
    };
  }

  // 정리
  cleanup(): void {
    // 모든 스케줄된 재시도 취소
    for (const timeout of this.retryQueue.values()) {
      clearTimeout(timeout);
    }
    this.retryQueue.clear();
    
    // 히스토리 정리 (선택적)
    this.recoveryHistory.clear();
  }

  // 활성 재시도 목록
  getActiveRetries(): string[] {
    return Array.from(this.retryQueue.keys());
  }

  // 재시도 취소
  cancelRetry(taskId: string): boolean {
    const timeout = this.retryQueue.get(taskId);
    if (timeout) {
      clearTimeout(timeout);
      this.retryQueue.delete(taskId);
      return true;
    }
    return false;
  }
}