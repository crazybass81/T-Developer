import { performance } from 'perf_hooks';
import { AsyncLocalStorage } from 'async_hooks';
import util from 'util';
import chalk from 'chalk';

export const traceContext = new AsyncLocalStorage<TraceContext>();

interface TraceContext {
  traceId: string;
  spanId: string;
  parentSpanId?: string;
  startTime: number;
  metadata: Record<string, any>;
}

interface TraceOptions {
  log?: boolean;
  logArgs?: boolean;
  logResult?: boolean;
}

interface Trace {
  traceId: string;
  spanId: string;
  method: string;
  args?: any[];
  result?: any;
  error?: any;
  startTime: number;
  endTime?: number;
  duration?: number;
  success?: boolean;
  metadata: Record<string, any>;
}

export class ExecutionTracer {
  private traces: Map<string, Trace[]> = new Map();
  
  trace(options: TraceOptions = {}) {
    return (target: any, propertyKey: string, descriptor: PropertyDescriptor) => {
      const originalMethod = descriptor.value;
      
      descriptor.value = async function(...args: any[]) {
        const traceId = traceContext.getStore()?.traceId || generateTraceId();
        const spanId = generateSpanId();
        const startTime = performance.now();
        
        const trace: Trace = {
          traceId,
          spanId,
          method: `${target.constructor.name}.${propertyKey}`,
          args: options.logArgs ? args : undefined,
          startTime,
          metadata: {}
        };
        
        if (options.log) {
          console.log(chalk.blue(`→ ${trace.method}`), {
            traceId,
            spanId,
            args: options.logArgs ? args : '[hidden]'
          });
        }
        
        try {
          const result = await traceContext.run(
            {
              traceId,
              spanId,
              parentSpanId: traceContext.getStore()?.spanId,
              startTime,
              metadata: {}
            },
            async () => await originalMethod.apply(this, args)
          );
          
          trace.endTime = performance.now();
          trace.duration = trace.endTime - trace.startTime;
          trace.result = options.logResult ? result : undefined;
          trace.success = true;
          
          if (options.log) {
            console.log(
              chalk.green(`← ${trace.method}`),
              chalk.gray(`(${trace.duration.toFixed(2)}ms)`),
              {
                traceId,
                spanId,
                result: options.logResult ? result : '[hidden]'
              }
            );
          }
          
          return result;
          
        } catch (error) {
          trace.endTime = performance.now();
          trace.duration = trace.endTime - trace.startTime;
          trace.error = error;
          trace.success = false;
          
          if (options.log) {
            console.log(
              chalk.red(`✗ ${trace.method}`),
              chalk.gray(`(${trace.duration.toFixed(2)}ms)`),
              {
                traceId,
                spanId,
                error: error.message
              }
            );
          }
          
          throw error;
          
        } finally {
          this.saveTrace(trace);
        }
      };
      
      return descriptor;
    };
  }
  
  async traceExecution<T>(
    name: string,
    fn: () => Promise<T>,
    metadata?: Record<string, any>
  ): Promise<T> {
    const traceId = traceContext.getStore()?.traceId || generateTraceId();
    const spanId = generateSpanId();
    const startTime = performance.now();
    
    console.log(chalk.blue(`→ ${name}`), { traceId, spanId });
    
    try {
      const result = await traceContext.run(
        {
          traceId,
          spanId,
          parentSpanId: traceContext.getStore()?.spanId,
          startTime,
          metadata: metadata || {}
        },
        fn
      );
      
      const duration = performance.now() - startTime;
      console.log(
        chalk.green(`← ${name}`),
        chalk.gray(`(${duration.toFixed(2)}ms)`)
      );
      
      return result;
      
    } catch (error) {
      const duration = performance.now() - startTime;
      console.log(
        chalk.red(`✗ ${name}`),
        chalk.gray(`(${duration.toFixed(2)}ms)`),
        error
      );
      throw error;
    }
  }
  
  private saveTrace(trace: Trace): void {
    if (!this.traces.has(trace.traceId)) {
      this.traces.set(trace.traceId, []);
    }
    
    this.traces.get(trace.traceId)!.push(trace);
  }
  
  getTrace(traceId: string): Trace[] | undefined {
    return this.traces.get(traceId);
  }
  
  visualizeTrace(traceId: string): string {
    const traces = this.getTrace(traceId);
    if (!traces) return 'Trace not found';
    
    const sorted = traces.sort((a, b) => a.startTime - b.startTime);
    const lines: string[] = [''];
    
    sorted.forEach((trace, index) => {
      const indent = '  '.repeat(trace.metadata.depth || 0);
      const duration = trace.duration?.toFixed(2) || '?';
      const status = trace.success ? '✓' : '✗';
      
      lines.push(
        `${indent}${status} ${trace.method} (${duration}ms)`
      );
    });
    
    return lines.join('\n');
  }
}

export class EnhancedConsole {
  private originalConsole = { ...console };
  
  install(): void {
    console.log = (...args: any[]) => {
      const enhanced = this.enhance(args);
      this.originalConsole.log(...enhanced);
    };
    
    console.error = (...args: any[]) => {
      const enhanced = this.enhance(args, 'error');
      this.originalConsole.error(...enhanced);
    };
  }
  
  private enhance(args: any[], type: string = 'log'): any[] {
    const ctx = traceContext.getStore();
    const timestamp = new Date().toISOString();
    
    const prefix = type === 'error' 
      ? chalk.red(`[${timestamp}]`)
      : chalk.gray(`[${timestamp}]`);
    
    const traceInfo = ctx 
      ? chalk.dim(`[${ctx.traceId.slice(0, 8)}/${ctx.spanId.slice(0, 8)}]`)
      : '';
    
    const enhanced = args.map(arg => {
      if (typeof arg === 'object' && arg !== null) {
        return util.inspect(arg, {
          colors: true,
          depth: 4,
          maxArrayLength: 100,
          breakLength: 80,
          compact: false
        });
      }
      return arg;
    });
    
    return [prefix, traceInfo, ...enhanced];
  }
}

export function createDebugProxy<T extends object>(
  target: T,
  name: string = 'Object'
): T {
  return new Proxy(target, {
    get(obj, prop, receiver) {
      const value = Reflect.get(obj, prop, receiver);
      console.log(chalk.yellow(`[Proxy:${name}] GET`), prop, '→', value);
      return value;
    },
    
    set(obj, prop, value, receiver) {
      console.log(chalk.yellow(`[Proxy:${name}] SET`), prop, '←', value);
      return Reflect.set(obj, prop, value, receiver);
    },
    
    deleteProperty(obj, prop) {
      console.log(chalk.yellow(`[Proxy:${name}] DELETE`), prop);
      return Reflect.deleteProperty(obj, prop);
    },
    
    has(obj, prop) {
      const exists = Reflect.has(obj, prop);
      console.log(chalk.yellow(`[Proxy:${name}] HAS`), prop, '→', exists);
      return exists;
    }
  });
}

function generateTraceId(): string {
  return `trace_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

function generateSpanId(): string {
  return `span_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

export function debuggingMiddleware() {
  return (req: any, res: any, next: any) => {
    const traceId = req.headers['x-trace-id'] as string || generateTraceId();
    const spanId = generateSpanId();
    
    console.log(chalk.blue('→ HTTP Request'), {
      method: req.method,
      path: req.path,
      traceId,
      spanId
    });
    
    traceContext.run(
      {
        traceId,
        spanId,
        startTime: Date.now(),
        metadata: {
          method: req.method,
          path: req.path
        }
      },
      () => {
        const originalSend = res.send;
        res.send = function(data: any) {
          console.log(chalk.green('← HTTP Response'), {
            traceId,
            spanId,
            statusCode: res.statusCode
          });
          
          return originalSend.call(this, data);
        };
        
        next();
      }
    );
  };
}