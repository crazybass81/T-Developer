import { StatsD } from 'node-statsd';
import winston from 'winston';
import { CloudWatchTransport } from 'winston-cloudwatch';

// StatsD 클라이언트 (로컬 개발용)
export const metrics = new StatsD({
  host: process.env.STATSD_HOST || 'localhost',
  port: parseInt(process.env.STATSD_PORT || '8125'),
  prefix: 't-developer.',
  mock: process.env.NODE_ENV === 'test'
});

// Winston 로거 설정
export const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.splat(),
    winston.format.json()
  ),
  defaultMeta: { service: 't-developer' },
  transports: [
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      )
    }),
    new winston.transports.File({ 
      filename: 'logs/error.log', 
      level: 'error' 
    }),
    new winston.transports.File({ 
      filename: 'logs/combined.log' 
    })
  ]
});

// CloudWatch 전송 (프로덕션)
if (process.env.NODE_ENV === 'production') {
  logger.add(new CloudWatchTransport({
    logGroupName: '/aws/t-developer',
    logStreamName: `${process.env.NODE_ENV}-${new Date().toISOString().split('T')[0]}`,
    awsRegion: process.env.AWS_REGION
  }));
}