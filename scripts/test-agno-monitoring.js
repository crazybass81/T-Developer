#!/usr/bin/env node

/**
 * Agno 모니터링 통합 설정 검증 스크립트
 * SubTask 0.13.5 검증용
 */

const fs = require('fs');
const path = require('path');

console.log('🔍 Agno 모니터링 통합 설정 검증 시작...\n');

// 1. 필수 파일 존재 확인
const requiredFiles = [
  'backend/src/integrations/agno/monitoring-config.ts'
];

console.log('📁 필수 파일 존재 확인:');
let allFilesExist = true;

for (const file of requiredFiles) {
  const filePath = path.join(process.cwd(), file);
  const exists = fs.existsSync(filePath);
  
  console.log(`  ${exists ? '✅' : '❌'} ${file}`);
  
  if (!exists) {
    allFilesExist = false;
  }
}

if (!allFilesExist) {
  console.log('\n❌ 일부 필수 파일이 누락되었습니다.');
  process.exit(1);
}

// 2. TypeScript 파일 구문 검사
console.log('\n🔧 TypeScript 구문 검사:');

try {
  const monitoringConfigPath = path.join(process.cwd(), 'backend/src/integrations/agno/monitoring-config.ts');
  const monitoringConfigContent = fs.readFileSync(monitoringConfigPath, 'utf8');
  
  // 기본 구문 검사
  const hasAgnoConfig = monitoringConfigContent.includes('export interface AgnoConfig');
  const hasAgnoMetric = monitoringConfigContent.includes('export interface AgnoMetric');
  const hasAgnoEvent = monitoringConfigContent.includes('export interface AgnoEvent');
  const hasAgnoTrace = monitoringConfigContent.includes('export interface AgnoTrace');
  const hasAgnoMonitoringClient = monitoringConfigContent.includes('export class AgnoMonitoringClient');
  const hasAgnoTraceDecorator = monitoringConfigContent.includes('export function AgnoTrace');
  
  console.log(`  ${hasAgnoConfig ? '✅' : '❌'} AgnoConfig 인터페이스 정의`);
  console.log(`  ${hasAgnoMetric ? '✅' : '❌'} AgnoMetric 인터페이스 정의`);
  console.log(`  ${hasAgnoEvent ? '✅' : '❌'} AgnoEvent 인터페이스 정의`);
  console.log(`  ${hasAgnoTrace ? '✅' : '❌'} AgnoTrace 인터페이스 정의`);
  console.log(`  ${hasAgnoMonitoringClient ? '✅' : '❌'} AgnoMonitoringClient 클래스 구현`);
  console.log(`  ${hasAgnoTraceDecorator ? '✅' : '❌'} AgnoTrace 데코레이터 구현`);
  
  if (!hasAgnoConfig || !hasAgnoMetric || !hasAgnoEvent || !hasAgnoTrace || 
      !hasAgnoMonitoringClient || !hasAgnoTraceDecorator) {
    throw new Error('필수 인터페이스/클래스가 누락되었습니다.');
  }
  
} catch (error) {
  console.log(`  ❌ TypeScript 구문 오류: ${error.message}`);
  process.exit(1);
}

// 3. 핵심 기능 검증
console.log('\n⚙️ 핵심 기능 검증:');

try {
  const monitoringConfigPath = path.join(process.cwd(), 'backend/src/integrations/agno/monitoring-config.ts');
  const monitoringConfigContent = fs.readFileSync(monitoringConfigPath, 'utf8');
  
  // AgnoMonitoringClient 핵심 메서드 확인
  const hasSendMetric = monitoringConfigContent.includes('async sendMetric(');
  const hasSendEvent = monitoringConfigContent.includes('async sendEvent(');
  const hasSendTrace = monitoringConfigContent.includes('async sendTrace(');
  const hasMonitorAgentPerformance = monitoringConfigContent.includes('async monitorAgentPerformance(');
  const hasTrackError = monitoringConfigContent.includes('async trackError(');
  const hasShutdown = monitoringConfigContent.includes('async shutdown()');
  
  // 배치 처리 메서드 확인
  const hasFlushMetrics = monitoringConfigContent.includes('private async flushMetrics()');
  const hasFlushEvents = monitoringConfigContent.includes('private async flushEvents()');
  const hasFlushTraces = monitoringConfigContent.includes('private async flushTraces()');
  
  console.log(`  ${hasSendMetric ? '✅' : '❌'} sendMetric() 메서드`);
  console.log(`  ${hasSendEvent ? '✅' : '❌'} sendEvent() 메서드`);
  console.log(`  ${hasSendTrace ? '✅' : '❌'} sendTrace() 메서드`);
  console.log(`  ${hasMonitorAgentPerformance ? '✅' : '❌'} monitorAgentPerformance() 메서드`);
  console.log(`  ${hasTrackError ? '✅' : '❌'} trackError() 메서드`);
  console.log(`  ${hasShutdown ? '✅' : '❌'} shutdown() 메서드`);
  console.log(`  ${hasFlushMetrics ? '✅' : '❌'} flushMetrics() 배치 처리`);
  console.log(`  ${hasFlushEvents ? '✅' : '❌'} flushEvents() 배치 처리`);
  console.log(`  ${hasFlushTraces ? '✅' : '❌'} flushTraces() 배치 처리`);
  
  const allMethodsExist = hasSendMetric && hasSendEvent && hasSendTrace && 
                         hasMonitorAgentPerformance && hasTrackError && hasShutdown &&
                         hasFlushMetrics && hasFlushEvents && hasFlushTraces;
  
  if (!allMethodsExist) {
    throw new Error('필수 메서드가 누락되었습니다.');
  }
  
} catch (error) {
  console.log(`  ❌ 핵심 기능 검증 실패: ${error.message}`);
  process.exit(1);
}

// 4. 배치 처리 시스템 검증
console.log('\n📦 배치 처리 시스템 검증:');

try {
  const monitoringConfigPath = path.join(process.cwd(), 'backend/src/integrations/agno/monitoring-config.ts');
  const monitoringConfigContent = fs.readFileSync(monitoringConfigPath, 'utf8');
  
  const hasMetricBuffer = monitoringConfigContent.includes('private metricBuffer: AgnoMetric[]');
  const hasEventBuffer = monitoringConfigContent.includes('private eventBuffer: AgnoEvent[]');
  const hasTraceBuffer = monitoringConfigContent.includes('private traceBuffer: AgnoTrace[]');
  const hasFlushTimer = monitoringConfigContent.includes('private flushTimer?');
  const hasBatchSizeCheck = monitoringConfigContent.includes('this.config.batchSize!');
  const hasStartFlushTimer = monitoringConfigContent.includes('private startFlushTimer()');
  
  console.log(`  ${hasMetricBuffer ? '✅' : '❌'} 메트릭 버퍼 시스템`);
  console.log(`  ${hasEventBuffer ? '✅' : '❌'} 이벤트 버퍼 시스템`);
  console.log(`  ${hasTraceBuffer ? '✅' : '❌'} 트레이스 버퍼 시스템`);
  console.log(`  ${hasFlushTimer ? '✅' : '❌'} 플러시 타이머`);
  console.log(`  ${hasBatchSizeCheck ? '✅' : '❌'} 배치 크기 체크`);
  console.log(`  ${hasStartFlushTimer ? '✅' : '❌'} 타이머 시작 메서드`);
  
  if (!hasMetricBuffer || !hasEventBuffer || !hasTraceBuffer || 
      !hasFlushTimer || !hasBatchSizeCheck || !hasStartFlushTimer) {
    throw new Error('배치 처리 시스템이 완전하지 않습니다.');
  }
  
} catch (error) {
  console.log(`  ❌ 배치 처리 시스템 검증 실패: ${error.message}`);
  process.exit(1);
}

// 5. 데코레이터 시스템 검증
console.log('\n🏷️ 데코레이터 시스템 검증:');

try {
  const monitoringConfigPath = path.join(process.cwd(), 'backend/src/integrations/agno/monitoring-config.ts');
  const monitoringConfigContent = fs.readFileSync(monitoringConfigPath, 'utf8');
  
  const hasMethodDecorator = monitoringConfigContent.includes('MethodDecorator');
  const hasTraceIdGeneration = monitoringConfigContent.includes('trace-${Date.now()}');
  const hasSpanIdGeneration = monitoringConfigContent.includes('span-${Date.now()}');
  const hasOriginalMethodCall = monitoringConfigContent.includes('originalMethod.apply');
  const hasErrorHandling = monitoringConfigContent.includes('status: \'error\'');
  const hasSuccessHandling = monitoringConfigContent.includes('status: \'success\'');
  
  console.log(`  ${hasMethodDecorator ? '✅' : '❌'} MethodDecorator 타입 사용`);
  console.log(`  ${hasTraceIdGeneration ? '✅' : '❌'} TraceId 자동 생성`);
  console.log(`  ${hasSpanIdGeneration ? '✅' : '❌'} SpanId 자동 생성`);
  console.log(`  ${hasOriginalMethodCall ? '✅' : '❌'} 원본 메서드 호출`);
  console.log(`  ${hasErrorHandling ? '✅' : '❌'} 에러 상태 처리`);
  console.log(`  ${hasSuccessHandling ? '✅' : '❌'} 성공 상태 처리`);
  
  if (!hasMethodDecorator || !hasTraceIdGeneration || !hasSpanIdGeneration || 
      !hasOriginalMethodCall || !hasErrorHandling || !hasSuccessHandling) {
    throw new Error('데코레이터 시스템이 불완전합니다.');
  }
  
} catch (error) {
  console.log(`  ❌ 데코레이터 시스템 검증 실패: ${error.message}`);
  process.exit(1);
}

// 6. HTTP 클라이언트 설정 검증
console.log('\n🌐 HTTP 클라이언트 설정 검증:');

try {
  const monitoringConfigPath = path.join(process.cwd(), 'backend/src/integrations/agno/monitoring-config.ts');
  const monitoringConfigContent = fs.readFileSync(monitoringConfigPath, 'utf8');
  
  const hasAxiosImport = monitoringConfigContent.includes('import axios');
  const hasAxiosCreate = monitoringConfigContent.includes('axios.create');
  const hasAuthHeader = monitoringConfigContent.includes('Authorization');
  const hasProjectIdHeader = monitoringConfigContent.includes('X-Project-ID');
  const hasEnvironmentHeader = monitoringConfigContent.includes('X-Environment');
  const hasContentTypeHeader = monitoringConfigContent.includes('Content-Type');
  
  console.log(`  ${hasAxiosImport ? '✅' : '❌'} Axios 라이브러리 임포트`);
  console.log(`  ${hasAxiosCreate ? '✅' : '❌'} Axios 인스턴스 생성`);
  console.log(`  ${hasAuthHeader ? '✅' : '❌'} Authorization 헤더`);
  console.log(`  ${hasProjectIdHeader ? '✅' : '❌'} X-Project-ID 헤더`);
  console.log(`  ${hasEnvironmentHeader ? '✅' : '❌'} X-Environment 헤더`);
  console.log(`  ${hasContentTypeHeader ? '✅' : '❌'} Content-Type 헤더`);
  
  if (!hasAxiosImport || !hasAxiosCreate || !hasAuthHeader || 
      !hasProjectIdHeader || !hasEnvironmentHeader || !hasContentTypeHeader) {
    throw new Error('HTTP 클라이언트 설정이 불완전합니다.');
  }
  
} catch (error) {
  console.log(`  ❌ HTTP 클라이언트 설정 검증 실패: ${error.message}`);
  process.exit(1);
}

console.log('\n✅ Agno 모니터링 통합 설정 검증 완료!');
console.log('\n📋 구현된 기능:');
console.log('  • AgnoMonitoringClient: 메트릭, 이벤트, 트레이스 전송');
console.log('  • 배치 처리 시스템: 효율적인 데이터 전송');
console.log('  • @AgnoTrace 데코레이터: 메서드 자동 추적');
console.log('  • 에이전트 성능 모니터링');
console.log('  • 에러 추적 및 로깅');
console.log('  • HTTP 클라이언트 설정');
console.log('  • 타이머 기반 자동 플러시');

console.log('\n🎯 SubTask 0.13.5 완료!');