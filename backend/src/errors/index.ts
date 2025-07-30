// Task 1.16: 에러 처리 프레임워크 - 통합 인덱스
export { 
  ErrorHandler, 
  AppError, 
  ErrorCode, 
  asyncHandler 
} from './error-handler';

export { 
  ErrorRecoveryManager, 
  RetryStrategy, 
  CircuitBreakerStrategy 
} from './error-recovery';

export { 
  ErrorTracker, 
  ErrorAnalyzer 
} from './error-tracking';

export { 
  AlertManager, 
  ErrorReporter 
} from './error-alerts';

// 통합 에러 시스템 초기화
import { ErrorTracker, ErrorAnalyzer } from './error-tracking';
import { AlertManager, ErrorReporter } from './error-alerts';
import { ErrorRecoveryManager } from './error-recovery';

export class ErrorSystem {
  public tracker: ErrorTracker;
  public analyzer: ErrorAnalyzer;
  public alertManager: AlertManager;
  public reporter: ErrorReporter;
  public recoveryManager: ErrorRecoveryManager;

  constructor() {
    this.tracker = new ErrorTracker();
    this.analyzer = new ErrorAnalyzer(this.tracker);
    this.alertManager = new AlertManager();
    this.reporter = new ErrorReporter(this.alertManager);
    this.recoveryManager = new ErrorRecoveryManager();

    this.startMonitoring();
  }

  private startMonitoring(): void {
    // 5분마다 에러 패턴 분석 및 알림 체크
    setInterval(() => {
      const metrics = this.tracker.getMetrics();
      const patterns = this.analyzer.analyzePatterns();
      
      this.alertManager.checkAlerts(metrics);
      
      if (patterns.length > 0) {
        console.log('Error patterns detected:', patterns);
      }
    }, 300000);
  }

  trackError(error: Error, context: any): void {
    this.tracker.trackError(error, context);
  }

  async attemptRecovery(error: Error, context: any): Promise<any> {
    return this.recoveryManager.attemptRecovery(error, context);
  }
}

// 글로벌 에러 시스템 인스턴스
export const errorSystem = new ErrorSystem();