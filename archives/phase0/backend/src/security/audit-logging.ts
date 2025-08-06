import { CloudWatchLogsClient, PutLogEventsCommand } from '@aws-sdk/client-cloudwatch-logs';
import { DynamoDBDocumentClient, PutCommand } from '@aws-sdk/lib-dynamodb';
import { Request, Response, NextFunction } from 'express';
import crypto from 'crypto';

export enum SecurityEventType {
  LOGIN_ATTEMPT = 'LOGIN_ATTEMPT',
  LOGIN_SUCCESS = 'LOGIN_SUCCESS',
  LOGIN_FAILURE = 'LOGIN_FAILURE',
  UNAUTHORIZED_ACCESS = 'UNAUTHORIZED_ACCESS',
  API_KEY_CREATED = 'API_KEY_CREATED',
  SENSITIVE_DATA_ACCESS = 'SENSITIVE_DATA_ACCESS',
  SQL_INJECTION_ATTEMPT = 'SQL_INJECTION_ATTEMPT',
  XSS_ATTEMPT = 'XSS_ATTEMPT',
  RATE_LIMIT_EXCEEDED = 'RATE_LIMIT_EXCEEDED',
  SUSPICIOUS_ACTIVITY = 'SUSPICIOUS_ACTIVITY'
}

interface SecurityEvent {
  id: string;
  timestamp: Date;
  eventType: SecurityEventType;
  severity: 'low' | 'medium' | 'high' | 'critical';
  userId?: string;
  ipAddress?: string;
  resource?: string;
  action?: string;
  result: 'success' | 'failure';
  details?: Record<string, any>;
}

export class SecurityAuditLogger {
  private cloudWatchClient: CloudWatchLogsClient;
  private dynamoClient: DynamoDBDocumentClient;
  private logGroupName = '/aws/t-developer/security-audit';
  private tableName = 'T-Developer-SecurityAudit';
  
  constructor(cloudWatchClient: CloudWatchLogsClient, dynamoClient: DynamoDBDocumentClient) {
    this.cloudWatchClient = cloudWatchClient;
    this.dynamoClient = dynamoClient;
  }
  
  async logSecurityEvent(event: Omit<SecurityEvent, 'id' | 'timestamp'>): Promise<void> {
    const securityEvent: SecurityEvent = {
      ...event,
      id: `sec_${Date.now()}_${crypto.randomBytes(4).toString('hex')}`,
      timestamp: new Date()
    };
    
    await Promise.allSettled([
      this.saveToCloudWatch(securityEvent),
      this.saveToDynamoDB(securityEvent)
    ]);
  }
  
  private async saveToCloudWatch(event: SecurityEvent): Promise<void> {
    try {
      await this.cloudWatchClient.send(new PutLogEventsCommand({
        logGroupName: this.logGroupName,
        logStreamName: `security-${new Date().toISOString().split('T')[0]}`,
        logEvents: [{
          timestamp: event.timestamp.getTime(),
          message: JSON.stringify(event)
        }]
      }));
    } catch (error) {
      console.error('CloudWatch audit log failed:', error);
    }
  }
  
  private async saveToDynamoDB(event: SecurityEvent): Promise<void> {
    try {
      await this.dynamoClient.send(new PutCommand({
        TableName: this.tableName,
        Item: {
          ...event,
          timestamp: event.timestamp.toISOString(),
          ttl: Math.floor(Date.now() / 1000) + (365 * 24 * 60 * 60)
        }
      }));
    } catch (error) {
      console.error('DynamoDB audit log failed:', error);
    }
  }
}

export function auditMiddleware(auditLogger: SecurityAuditLogger) {
  return (req: Request, res: Response, next: NextFunction) => {
    res.on('finish', async () => {
      if (shouldAuditEndpoint(req.path)) {
        await auditLogger.logSecurityEvent({
          eventType: getEventType(req.path, req.method, res.statusCode),
          severity: res.statusCode >= 400 ? 'medium' : 'low',
          userId: (req as any).user?.id,
          ipAddress: req.ip,
          resource: req.path,
          action: req.method,
          result: res.statusCode < 400 ? 'success' : 'failure',
          details: {
            statusCode: res.statusCode,
            userAgent: req.headers['user-agent']
          }
        });
      }
    });
    
    next();
  };
}

function shouldAuditEndpoint(path: string): boolean {
  return ['/api/auth', '/api/users', '/api/admin'].some(p => path.startsWith(p));
}

function getEventType(path: string, method: string, statusCode: number): SecurityEventType {
  if (path.includes('/login')) {
    return statusCode === 200 ? SecurityEventType.LOGIN_SUCCESS : SecurityEventType.LOGIN_FAILURE;
  }
  if (statusCode === 401) return SecurityEventType.UNAUTHORIZED_ACCESS;
  if (statusCode === 429) return SecurityEventType.RATE_LIMIT_EXCEEDED;
  return SecurityEventType.SENSITIVE_DATA_ACCESS;
}