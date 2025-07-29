#!/usr/bin/env ts-node

import { AdvancedDebugger, ExecutionTracer, EnhancedConsole } from '../backend/src/dev/debugging-tools';
import chalk from 'chalk';

// 디버깅 환경 설정
class DebuggingSetup {
  private debugger: AdvancedDebugger;
  private tracer: ExecutionTracer;
  private console: EnhancedConsole;
  
  constructor() {
    this.debugger = new AdvancedDebugger();
    this.tracer = new ExecutionTracer();
    this.console = new EnhancedConsole();
  }
  
  async setup(): Promise<void> {
    console.log(chalk.blue('🔧 Setting up debugging environment...'));
    
    // 향상된 콘솔 설치
    this.console.install();
    console.log(chalk.green('✅ Enhanced console installed'));
    
    // 개발 환경 브레이크포인트 설정
    await this.setupDevelopmentBreakpoints();
    
    // 성능 모니터링 설정
    this.setupPerformanceMonitoring();
    
    // 에러 핸들링 설정
    this.setupErrorHandling();
    
    console.log(chalk.green('✅ Debugging environment ready!'));
  }
  
  private async setupDevelopmentBreakpoints(): Promise<void> {
    const breakpoints = [
      {
        file: 'backend/src/agents/nl-input-agent.ts',
        line: 50,
        condition: 'input.length > 1000',
        message: 'Large input detected'
      },
      {
        file: 'backend/src/services/agent-orchestrator.ts',
        line: 25,
        condition: 'agents.length === 0',
        message: 'No agents available'
      }
    ];
    
    for (const bp of breakpoints) {
      try {
        await this.debugger.setConditionalBreakpoint(
          bp.file,
          bp.line,
          bp.condition,
          bp.message
        );
        console.log(chalk.yellow(`📍 Breakpoint set: ${bp.file}:${bp.line}`));
      } catch (error) {
        console.log(chalk.red(`❌ Failed to set breakpoint: ${bp.file}:${bp.line}`));
      }
    }
  }
  
  private setupPerformanceMonitoring(): void {
    // 글로벌 성능 모니터링
    const originalSetTimeout = global.setTimeout;
    global.setTimeout = function(callback: Function, delay: number, ...args: any[]) {
      const start = Date.now();
      return originalSetTimeout(() => {
        const actualDelay = Date.now() - start;
        if (actualDelay > delay + 100) {
          console.log(chalk.yellow(`⚠️ Timer delay: expected ${delay}ms, actual ${actualDelay}ms`));
        }
        callback(...args);
      }, delay);
    };
    
    console.log(chalk.green('✅ Performance monitoring enabled'));
  }
  
  private setupErrorHandling(): void {
    // 미처리 예외 캐치
    process.on('uncaughtException', (error) => {
      console.log(chalk.red('💥 Uncaught Exception:'), error);
      // 개발 환경에서는 프로세스를 종료하지 않음
      if (process.env.NODE_ENV !== 'development') {
        process.exit(1);
      }
    });
    
    // 미처리 Promise 거부 캐치
    process.on('unhandledRejection', (reason, promise) => {
      console.log(chalk.red('💥 Unhandled Rejection at:'), promise, 'reason:', reason);
    });
    
    console.log(chalk.green('✅ Error handling configured'));
  }
  
  // 디버깅 명령어 등록
  registerCommands(): void {
    // 전역 디버깅 함수들
    (global as any).debug = {
      // 메모리 스냅샷
      snapshot: async (tag?: string) => {
        const filename = await this.debugger.takeHeapSnapshot(tag);
        console.log(chalk.blue(`📸 Heap snapshot saved: ${filename}`));
        return filename;
      },
      
      // 프로파일링 시작
      startProfile: async (name: string) => {
        await this.debugger.startProfiling(name);
        console.log(chalk.blue(`🚀 Profiling started: ${name}`));
      },
      
      // 프로파일링 중지
      stopProfile: async (name: string) => {
        const profile = await this.debugger.stopProfiling(name);
        console.log(chalk.blue(`🏁 Profiling stopped: ${name}`));
        console.log('Top hotspots:');
        profile.hotspots.slice(0, 5).forEach((hotspot, i) => {
          console.log(`  ${i + 1}. ${hotspot.functionName} (${hotspot.percentage.toFixed(2)}%)`);
        });
        return profile;
      },
      
      // 추적 조회
      getTrace: (traceId: string) => {
        return this.tracer.getTrace(traceId);
      }
    };
    
    console.log(chalk.green('✅ Debug commands registered (global.debug)'));
  }
}

// 스크립트 실행
async function main() {
  const setup = new DebuggingSetup();
  
  try {
    await setup.setup();
    setup.registerCommands();
    
    console.log(chalk.blue('\n📚 Available debug commands:'));
    console.log('  global.debug.snapshot(tag?) - Take heap snapshot');
    console.log('  global.debug.startProfile(name) - Start CPU profiling');
    console.log('  global.debug.stopProfile(name) - Stop CPU profiling');
    console.log('  global.debug.getTrace(traceId) - Get execution trace');
    
  } catch (error) {
    console.error(chalk.red('❌ Failed to setup debugging:'), error);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

export { DebuggingSetup };