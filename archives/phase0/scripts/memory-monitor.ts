#!/usr/bin/env ts-node

import { MemoryManager } from '../backend/src/performance/memory-manager';
import chalk from 'chalk';

class MemoryMonitorScript {
  private memoryManager = new MemoryManager();
  
  async run(): Promise<void> {
    console.log(chalk.blue('🧠 Starting memory monitoring...'));
    
    // 이벤트 리스너 설정
    this.setupEventListeners();
    
    // 모니터링 시작
    this.memoryManager.startMonitoring(10000); // 10초 간격
    
    // 초기 상태 출력
    this.printMemoryStatus();
    
    // 주기적 상태 출력
    setInterval(() => {
      this.printMemoryStatus();
    }, 30000); // 30초마다
    
    // 프로세스 종료 시 정리
    process.on('SIGINT', () => {
      console.log(chalk.yellow('\n🛑 Stopping memory monitoring...'));
      this.memoryManager.stopMonitoring();
      process.exit(0);
    });
    
    console.log(chalk.green('✅ Memory monitoring started. Press Ctrl+C to stop.'));
  }
  
  private setupEventListeners(): void {
    this.memoryManager.on('memory:warning', (status) => {
      console.log(chalk.yellow(`⚠️  Memory warning: ${status.heapUsed.toFixed(2)} MB`));
    });
    
    this.memoryManager.on('memory:critical', (status) => {
      console.log(chalk.red(`🚨 Critical memory usage: ${status.heapUsed.toFixed(2)} MB`));
    });
    
    this.memoryManager.on('gc', (gcInfo) => {
      if (gcInfo.duration > 50) {
        console.log(chalk.cyan(`🗑️  GC: ${gcInfo.duration.toFixed(2)}ms`));
      }
    });
  }
  
  private printMemoryStatus(): void {
    const status = this.memoryManager.getMemoryStatus();
    
    console.log(chalk.blue('\n📊 Memory Status:'));
    console.log(`  RSS: ${status.rss.toFixed(2)} MB`);
    console.log(`  Heap Used: ${status.heapUsed.toFixed(2)} MB`);
    console.log(`  Heap Total: ${status.heapTotal.toFixed(2)} MB`);
    console.log(`  Heap Usage: ${status.heapUsagePercent.toFixed(1)}%`);
    console.log(`  External: ${status.external.toFixed(2)} MB`);
  }
}

if (require.main === module) {
  const script = new MemoryMonitorScript();
  script.run().catch(console.error);
}

export { MemoryMonitorScript };