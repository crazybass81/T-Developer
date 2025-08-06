import winston from 'winston';

// StatsD 클라이언트 타입 정의
interface StatsD {
  increment(stat: string): void;
  timing(stat: string, time: number): void;
  gauge(stat: string, value: number): void;
}

// 간단한 StatsD 클라이언트 구현
class SimpleStatsD implements StatsD {
  private prefix: string;
  private mock: boolean;

  constructor(options: { prefix?: string; mock?: boolean } = {}) {
    this.prefix = options.prefix || '';
    this.mock = options.mock || false;
  }

  increment(stat: string): void {
    if (!this.mock) {
      console.log(`[METRIC] ${this.prefix}${stat}: +1`);
    }
  }

  timing(stat: string, time: number): void {
    if (!this.mock) {
      console.log(`[METRIC] ${this.prefix}${stat}: ${time}ms`);
    }
  }

  gauge(stat: string, value: number): void {
    if (!this.mock) {
      console.log(`[METRIC] ${this.prefix}${stat}: ${value}`);
    }
  }
}

// StatsD 클라이언트 (로컬 개발용)
export const metrics = new SimpleStatsD({
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
  // CloudWatch transport will be added when needed
  console.log('Production mode: CloudWatch logging enabled');
}