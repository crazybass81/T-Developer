// Task 1.15.1: 구조화된 로깅 시스템
import { CloudWatchLogsClient, PutLogEventsCommand } from '@aws-sdk/client-cloudwatch-logs';

interface LogEntry {
  level: 'debug' | 'info' | 'warn' | 'error';
  message: string;
  metadata?: any;
  timestamp?: Date;
}

export class Logger {
  private cloudWatchClient: CloudWatchLogsClient;
  private logGroupName: string;
  private logStreamName: string;

  constructor(logGroupName: string = '/aws/t-developer') {
    this.cloudWatchClient = new CloudWatchLogsClient({ region: process.env.AWS_REGION });
    this.logGroupName = logGroupName;
    this.logStreamName = `${process.env.NODE_ENV}-${Date.now()}`;
  }

  async log(entry: LogEntry): Promise<void> {
    const logEvent = {
      timestamp: (entry.timestamp || new Date()).getTime(),
      message: JSON.stringify({
        level: entry.level,
        message: entry.message,
        metadata: entry.metadata,
        service: 't-developer'
      })
    };

    // Console output for development
    if (process.env.NODE_ENV === 'development') {
      console.log(`[${entry.level.toUpperCase()}] ${entry.message}`, entry.metadata || '');
    }

    // CloudWatch for production
    if (process.env.NODE_ENV === 'production') {
      try {
        await this.cloudWatchClient.send(new PutLogEventsCommand({
          logGroupName: this.logGroupName,
          logStreamName: this.logStreamName,
          logEvents: [logEvent]
        }));
      } catch (error) {
        console.error('Failed to send log to CloudWatch:', error);
      }
    }
  }

  debug(message: string, metadata?: any): Promise<void> {
    return this.log({ level: 'debug', message, metadata });
  }

  info(message: string, metadata?: any): Promise<void> {
    return this.log({ level: 'info', message, metadata });
  }

  warn(message: string, metadata?: any): Promise<void> {
    return this.log({ level: 'warn', message, metadata });
  }

  error(message: string, metadata?: any): Promise<void> {
    return this.log({ level: 'error', message, metadata });
  }
}

// Global logger instance
export const logger = new Logger();