// Task 1.15.3: 헬스 체크 시스템
interface HealthCheck {
  name: string;
  check: () => Promise<boolean>;
  timeout?: number;
}

interface HealthStatus {
  status: 'healthy' | 'unhealthy' | 'degraded';
  checks: Record<string, { status: boolean; duration: number; error?: string }>;
  timestamp: Date;
}

export class HealthChecker {
  private checks: Map<string, HealthCheck> = new Map();

  addCheck(check: HealthCheck): void {
    this.checks.set(check.name, check);
  }

  async runChecks(): Promise<HealthStatus> {
    const results: Record<string, any> = {};
    let healthyCount = 0;

    for (const [name, check] of this.checks) {
      const start = Date.now();
      try {
        const timeout = check.timeout || 5000;
        const result = await Promise.race([
          check.check(),
          new Promise<boolean>((_, reject) => 
            setTimeout(() => reject(new Error('Timeout')), timeout)
          )
        ]);

        results[name] = {
          status: result,
          duration: Date.now() - start
        };

        if (result) healthyCount++;
      } catch (error) {
        results[name] = {
          status: false,
          duration: Date.now() - start,
          error: error instanceof Error ? error.message : 'Unknown error'
        };
      }
    }

    const totalChecks = this.checks.size;
    let status: 'healthy' | 'unhealthy' | 'degraded';

    if (healthyCount === totalChecks) {
      status = 'healthy';
    } else if (healthyCount === 0) {
      status = 'unhealthy';
    } else {
      status = 'degraded';
    }

    return {
      status,
      checks: results,
      timestamp: new Date()
    };
  }
}

// Default health checker with common checks
export const healthChecker = new HealthChecker();

// Add basic system checks
healthChecker.addCheck({
  name: 'memory',
  check: async () => {
    const usage = process.memoryUsage();
    return usage.heapUsed < usage.heapTotal * 0.9; // Less than 90% heap usage
  }
});

healthChecker.addCheck({
  name: 'eventLoop',
  check: async () => {
    const start = process.hrtime.bigint();
    await new Promise(resolve => setImmediate(resolve));
    const delay = Number(process.hrtime.bigint() - start) / 1000000; // Convert to ms
    return delay < 100; // Less than 100ms delay
  }
});