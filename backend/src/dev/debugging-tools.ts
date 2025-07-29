import { InspectorSession } from 'inspector';
import { performance } from 'perf_hooks';
import { AsyncLocalStorage } from 'async_hooks';
import util from 'util';
import chalk from 'chalk';
import { promises as fs } from 'fs';
import crypto from 'crypto';

// 트레이스 컨텍스트 관리
export const traceContext = new AsyncLocalStorage<TraceContext>();

interface TraceContext {
  traceId: string;
  spanId: string;
  parentSpanId?: string;
  startTime: number;
  metadata: Record<string, any>;
}

// 고급 디버거
export class AdvancedDebugger {
  private session: InspectorSession;
  private breakpoints: Map<string, Breakpoint> = new Map();
  private profiles: Map<string, any> = new Map();
  
  constructor() {
    this.session = new InspectorSession();
    this.session.connect();
  }
  
  // 조건부 브레이크포인트 설정
  async setConditionalBreakpoint(
    file: string,
    line: number,
    condition: string,
    logMessage?: string
  ): Promise<void> {
    const scriptId = await this.getScriptId(file);
    
    await this.post('Debugger.setBreakpoint', {
      location: {
        scriptId,
        lineNumber: line - 1
      },
      condition
    });
    
    this.breakpoints.set(`${file}:${line}`, {
      file,
      line,
      condition,
      logMessage,
      hitCount: 0
    });
  }
  
  // 성능 프로파일링 시작
  async startProfiling(profileName: string): Promise<void> {
    await this.post('Profiler.enable');
    await this.post('Profiler.start');
    
    this.profiles.set(profileName, {
      startTime: Date.now(),
      name: profileName
    });
  }
  
  // 성능 프로파일링 중지
  async stopProfiling(profileName: string): Promise<CPUProfile> {
    const result = await this.post('Profiler.stop');
    await this.post('Profiler.disable');
    
    const profile = this.profiles.get(profileName);
    if (profile) {
      profile.endTime = Date.now();
      profile.data = result.profile;
    }
    
    return this.analyzeCPUProfile(result.profile);
  }
  
  // 메모리 스냅샷
  async takeHeapSnapshot(tag?: string): Promise<string> {
    await this.post('HeapProfiler.enable');
    
    const chunks: string[] = [];
    
    this.session.on('HeapProfiler.addHeapSnapshotChunk', (message) => {
      chunks.push(message.params.chunk);
    });
    
    await this.post('HeapProfiler.takeHeapSnapshot', {
      reportProgress: true,
      treatGlobalObjectsAsRoots: true
    });
    
    await this.post('HeapProfiler.disable');
    
    const snapshot = chunks.join('');
    const filename = `heapsnapshot-${tag || Date.now()}.json`;
    
    await fs.writeFile(filename, snapshot);
    
    return filename;
  }
  
  // CPU 프로파일 분석
  private analyzeCPUProfile(profile: any): CPUProfile {
    const nodes = new Map<number, any>();
    let totalTime = 0;
    
    // 노드 맵 생성
    profile.nodes.forEach((node: any) => {
      nodes.set(node.id, {
        ...node,
        selfTime: 0,
        totalTime: 0,
        children: []
      });
    });
    
    // 핫스팟 찾기
    const hotspots = Array.from(nodes.values())
      .filter(node => node.selfTime > 0)
      .sort((a, b) => b.selfTime - a.selfTime)
      .slice(0, 10)
      .map(node => ({
        functionName: node.callFrame?.functionName || '(anonymous)',
        url: node.callFrame?.url || '',
        lineNumber: node.callFrame?.lineNumber || 0,
        selfTime: node.selfTime,
        totalTime: node.totalTime,
        percentage: (node.selfTime / totalTime) * 100
      }));
    
    return {
      totalTime,
      hotspots,
      profile
    };
  }
  
  // Inspector 세션 명령 실행
  private post(method: string, params?: any): Promise<any> {
    return new Promise((resolve, reject) => {
      this.session.post(method, params, (err, result) => {
        if (err) reject(err);
        else resolve(result);
      });
    });
  }
  
  // 스크립트 ID 가져오기
  private async getScriptId(filename: string): Promise<string> {
    await this.post('Debugger.enable');
    return '1'; // 임시
  }
}

// 실행 추적기
export class ExecutionTracer {
  private traces: Map<string, Trace[]> = new Map();
  
  // 함수 추적 데코레이터
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
            spanId
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
          trace.success = true;
          
          if (options.log) {
            console.log(
              chalk.green(`← ${trace.method}`),
              chalk.gray(`(${trace.duration.toFixed(2)}ms)`)
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
              chalk.gray(`(${trace.duration.toFixed(2)}ms)`)
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
  
  // 추적 저장
  private saveTrace(trace: Trace): void {
    if (!this.traces.has(trace.traceId)) {
      this.traces.set(trace.traceId, []);
    }
    
    this.traces.get(trace.traceId)!.push(trace);
  }
  
  // 추적 조회
  getTrace(traceId: string): Trace[] | undefined {
    return this.traces.get(traceId);
  }
}

// 향상된 콘솔 로깅
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
    
    return [prefix, traceInfo, ...args];
  }
}

// 타입 정의
interface Breakpoint {
  file: string;
  line: number;
  condition?: string;
  logMessage?: string;
  hitCount: number;
}

interface CPUProfile {
  totalTime: number;
  hotspots: Array<{
    functionName: string;
    url: string;
    lineNumber: number;
    selfTime: number;
    totalTime: number;
    percentage: number;
  }>;
  profile: any;
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

// 유틸리티 함수
function generateTraceId(): string {
  return crypto.randomBytes(16).toString('hex');
}

function generateSpanId(): string {
  return crypto.randomBytes(8).toString('hex');
}

// 디버깅 미들웨어
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