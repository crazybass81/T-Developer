// Task 1.15.2: 메트릭 수집 시스템
import { CloudWatchClient, PutMetricDataCommand } from '@aws-sdk/client-cloudwatch';

interface Metric {
  name: string;
  value: number;
  unit: 'Count' | 'Seconds' | 'Bytes' | 'Percent';
  dimensions?: Record<string, string>;
}

export class MetricsCollector {
  private cloudWatchClient: CloudWatchClient;
  private namespace: string = 'T-Developer';
  private buffer: Metric[] = [];

  constructor() {
    this.cloudWatchClient = new CloudWatchClient({ region: process.env.AWS_REGION });
    this.startBufferFlush();
  }

  record(metric: Metric): void {
    this.buffer.push({
      ...metric,
      dimensions: {
        Environment: process.env.NODE_ENV || 'development',
        ...metric.dimensions
      }
    });
  }

  recordCount(name: string, value: number = 1, dimensions?: Record<string, string>): void {
    this.record({ name, value, unit: 'Count', dimensions });
  }

  recordDuration(name: string, durationMs: number, dimensions?: Record<string, string>): void {
    this.record({ name, value: durationMs / 1000, unit: 'Seconds', dimensions });
  }

  recordMemory(name: string, bytes: number, dimensions?: Record<string, string>): void {
    this.record({ name, value: bytes, unit: 'Bytes', dimensions });
  }

  private async flush(): Promise<void> {
    if (this.buffer.length === 0) return;

    const metrics = this.buffer.splice(0, 20); // CloudWatch limit
    
    try {
      await this.cloudWatchClient.send(new PutMetricDataCommand({
        Namespace: this.namespace,
        MetricData: metrics.map(metric => ({
          MetricName: metric.name,
          Value: metric.value,
          Unit: metric.unit,
          Dimensions: Object.entries(metric.dimensions || {}).map(([name, value]) => ({
            Name: name,
            Value: value
          })),
          Timestamp: new Date()
        }))
      }));
    } catch (error) {
      console.error('Failed to send metrics to CloudWatch:', error);
    }
  }

  private startBufferFlush(): void {
    setInterval(() => this.flush(), 60000); // Flush every minute
  }
}

// Global metrics collector
export const metrics = new MetricsCollector();