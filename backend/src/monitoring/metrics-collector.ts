interface SystemMetrics {
  timestamp: string;
  cpu_usage: number;
  memory_usage: number;
  active_connections: number;
  request_rate: number;
  error_rate: number;
}

export class MetricsCollector {
  private metrics: SystemMetrics[] = [];
  private intervalId: NodeJS.Timeout | null = null;
  private requestCount = 0;
  private errorCount = 0;
  private lastResetTime = Date.now();

  start(intervalMs: number = 30000): void {
    this.intervalId = setInterval(() => {
      this.collectSystemMetrics();
    }, intervalMs);
  }

  stop(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
  }

  private collectSystemMetrics(): void {
    const memUsage = process.memoryUsage();
    const cpuUsage = process.cpuUsage();
    const now = Date.now();
    const timeDiff = (now - this.lastResetTime) / 1000; // seconds

    const metric: SystemMetrics = {
      timestamp: new Date().toISOString(),
      cpu_usage: Math.round((cpuUsage.user + cpuUsage.system) / 1000000), // Convert to ms
      memory_usage: Math.round(memUsage.heapUsed / 1024 / 1024), // MB
      active_connections: this.getActiveConnections(),
      request_rate: Math.round(this.requestCount / timeDiff),
      error_rate: this.requestCount > 0 ? Math.round((this.errorCount / this.requestCount) * 100) : 0
    };

    this.metrics.push(metric);
    
    // Keep only last 100 metrics
    if (this.metrics.length > 100) {
      this.metrics.shift();
    }

    // Reset counters
    this.requestCount = 0;
    this.errorCount = 0;
    this.lastResetTime = now;
  }

  private getActiveConnections(): number {
    // Estimate based on server connections (simplified)
    return process.listenerCount('connection') || 0;
  }

  recordRequest(): void {
    this.requestCount++;
  }

  recordError(): void {
    this.errorCount++;
  }

  getMetrics(): SystemMetrics[] {
    return [...this.metrics];
  }

  getLatestMetric(): SystemMetrics | null {
    return this.metrics.length > 0 ? this.metrics[this.metrics.length - 1] : null;
  }

  // Prometheus-style metrics export
  exportPrometheusMetrics(): string {
    const latest = this.getLatestMetric();
    if (!latest) return '';

    return `
# HELP orchestrator_cpu_usage CPU usage in milliseconds
# TYPE orchestrator_cpu_usage gauge
orchestrator_cpu_usage ${latest.cpu_usage}

# HELP orchestrator_memory_usage Memory usage in MB
# TYPE orchestrator_memory_usage gauge
orchestrator_memory_usage ${latest.memory_usage}

# HELP orchestrator_active_connections Active connections count
# TYPE orchestrator_active_connections gauge
orchestrator_active_connections ${latest.active_connections}

# HELP orchestrator_request_rate Requests per second
# TYPE orchestrator_request_rate gauge
orchestrator_request_rate ${latest.request_rate}

# HELP orchestrator_error_rate Error rate percentage
# TYPE orchestrator_error_rate gauge
orchestrator_error_rate ${latest.error_rate}
`.trim();
  }
}