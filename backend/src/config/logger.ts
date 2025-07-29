import winston from 'winston';
import DailyRotateFile from 'winston-daily-rotate-file';

const customLevels = {
  levels: { fatal: 0, error: 1, warn: 2, info: 3, debug: 4, trace: 5 },
  colors: { fatal: 'red bold', error: 'red', warn: 'yellow', info: 'green', debug: 'blue', trace: 'gray' }
};

const logFormat = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss.SSS' }),
  winston.format.errors({ stack: true }),
  winston.format.metadata({ fillExcept: ['message', 'level', 'timestamp'] }),
  winston.format.json()
);

const devFormat = winston.format.combine(
  winston.format.colorize({ all: true }),
  winston.format.printf(({ timestamp, level, message, metadata }) => {
    const meta = Object.keys(metadata || {}).length ? JSON.stringify(metadata, null, 2) : '';
    return `${timestamp} [${level}]: ${message} ${meta}`;
  })
);

class Logger {
  private logger: winston.Logger;
  
  constructor(service: string) {
    this.logger = winston.createLogger({
      levels: customLevels.levels,
      defaultMeta: { service },
      transports: this.createTransports()
    });
    
    winston.addColors(customLevels.colors);
  }
  
  private createTransports(): winston.transport[] {
    const transports: winston.transport[] = [];
    
    if (process.env.NODE_ENV !== 'test') {
      transports.push(new winston.transports.Console({
        level: process.env.LOG_LEVEL || 'debug',
        format: process.env.NODE_ENV === 'production' ? logFormat : devFormat
      }));
    }
    
    if (process.env.NODE_ENV === 'production') {
      transports.push(new DailyRotateFile({
        level: 'error',
        filename: 'logs/error-%DATE%.log',
        datePattern: 'YYYY-MM-DD',
        maxSize: '20m',
        maxFiles: '14d',
        format: logFormat
      }));
      
      transports.push(new DailyRotateFile({
        filename: 'logs/combined-%DATE%.log',
        datePattern: 'YYYY-MM-DD',
        maxSize: '20m',
        maxFiles: '7d',
        format: logFormat
      }));
    }
    
    return transports;
  }
  
  fatal(message: string, meta?: any): void {
    this.logger.log('fatal', message, meta);
  }
  
  error(message: string, error?: Error | any, meta?: any): void {
    this.logger.error(message, { error: error?.stack || error, ...meta });
  }
  
  warn(message: string, meta?: any): void {
    this.logger.warn(message, meta);
  }
  
  info(message: string, meta?: any): void {
    this.logger.info(message, meta);
  }
  
  debug(message: string, meta?: any): void {
    this.logger.debug(message, meta);
  }
  
  trace(message: string, meta?: any): void {
    this.logger.log('trace', message, meta);
  }
  
  startTimer(): () => { duration: number } {
    const start = Date.now();
    return () => ({ duration: Date.now() - start });
  }
  
  logAgentExecution(agentName: string, projectId: string, result: 'success' | 'failure', meta?: any): void {
    this.info(`Agent execution: ${agentName}`, {
      agentName,
      projectId,
      result,
      ...meta
    });
  }
}

export const logger = new Logger('t-developer-backend');

export function createRequestLogger(requestId: string): Logger {
  const requestLogger = new Logger('t-developer-request');
  requestLogger['logger'].defaultMeta = { ...requestLogger['logger'].defaultMeta, requestId };
  return requestLogger;
}