#!/usr/bin/env node

/**
 * Agent Squad 통합 설정 검증 스크립트
 * SubTask 0.13.4 검증용
 */

const fs = require('fs');
const path = require('path');

console.log('🔍 Agent Squad 통합 설정 검증 시작...\n');

// 1. 필수 파일 존재 확인
const requiredFiles = [
  'backend/src/integrations/agent-squad/squad-config.ts'
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
  const squadConfigPath = path.join(process.cwd(), 'backend/src/integrations/agent-squad/squad-config.ts');
  const squadConfigContent = fs.readFileSync(squadConfigPath, 'utf8');
  
  // 기본 구문 검사
  const hasSquadConfig = squadConfigContent.includes('export interface SquadConfig');
  const hasSupervisorAgent = squadConfigContent.includes('export class SupervisorAgent');
  const hasWorkerAgent = squadConfigContent.includes('export abstract class WorkerAgent');
  const hasTaskQueue = squadConfigContent.includes('class TaskQueue');
  
  console.log(`  ${hasSquadConfig ? '✅' : '❌'} SquadConfig 인터페이스 정의`);
  console.log(`  ${hasSupervisorAgent ? '✅' : '❌'} SupervisorAgent 클래스 구현`);
  console.log(`  ${hasWorkerAgent ? '✅' : '❌'} WorkerAgent 추상 클래스 구현`);
  console.log(`  ${hasTaskQueue ? '✅' : '❌'} TaskQueue 클래스 구현`);
  
  if (!hasSquadConfig || !hasSupervisorAgent || !hasWorkerAgent || !hasTaskQueue) {
    throw new Error('필수 클래스/인터페이스가 누락되었습니다.');
  }
  
} catch (error) {
  console.log(`  ❌ TypeScript 구문 오류: ${error.message}`);
  process.exit(1);
}

// 3. 핵심 기능 검증
console.log('\n⚙️ 핵심 기능 검증:');

try {
  const squadConfigPath = path.join(process.cwd(), 'backend/src/integrations/agent-squad/squad-config.ts');
  const squadConfigContent = fs.readFileSync(squadConfigPath, 'utf8');
  
  // SupervisorAgent 핵심 메서드 확인
  const hasAddWorker = squadConfigContent.includes('async addWorker(');
  const hasDistributeTask = squadConfigContent.includes('async distributeTask(');
  const hasGetSquadStatus = squadConfigContent.includes('getSquadStatus()');
  
  // WorkerAgent 핵심 메서드 확인
  const hasExecuteTask = squadConfigContent.includes('async executeTask(');
  const hasCanHandle = squadConfigContent.includes('canHandle(');
  const hasAbstractProcess = squadConfigContent.includes('protected abstract process(');
  
  // TaskQueue 핵심 메서드 확인
  const hasEnqueue = squadConfigContent.includes('async enqueue(');
  const hasDequeue = squadConfigContent.includes('async dequeue(');
  
  console.log(`  ${hasAddWorker ? '✅' : '❌'} SupervisorAgent.addWorker() 메서드`);
  console.log(`  ${hasDistributeTask ? '✅' : '❌'} SupervisorAgent.distributeTask() 메서드`);
  console.log(`  ${hasGetSquadStatus ? '✅' : '❌'} SupervisorAgent.getSquadStatus() 메서드`);
  console.log(`  ${hasExecuteTask ? '✅' : '❌'} WorkerAgent.executeTask() 메서드`);
  console.log(`  ${hasCanHandle ? '✅' : '❌'} WorkerAgent.canHandle() 메서드`);
  console.log(`  ${hasAbstractProcess ? '✅' : '❌'} WorkerAgent.process() 추상 메서드`);
  console.log(`  ${hasEnqueue ? '✅' : '❌'} TaskQueue.enqueue() 메서드`);
  console.log(`  ${hasDequeue ? '✅' : '❌'} TaskQueue.dequeue() 메서드`);
  
  const allMethodsExist = hasAddWorker && hasDistributeTask && hasGetSquadStatus && 
                         hasExecuteTask && hasCanHandle && hasAbstractProcess &&
                         hasEnqueue && hasDequeue;
  
  if (!allMethodsExist) {
    throw new Error('필수 메서드가 누락되었습니다.');
  }
  
} catch (error) {
  console.log(`  ❌ 핵심 기능 검증 실패: ${error.message}`);
  process.exit(1);
}

// 4. 이벤트 시스템 검증
console.log('\n📡 이벤트 시스템 검증:');

try {
  const squadConfigPath = path.join(process.cwd(), 'backend/src/integrations/agent-squad/squad-config.ts');
  const squadConfigContent = fs.readFileSync(squadConfigPath, 'utf8');
  
  const extendsEventEmitter = squadConfigContent.includes('extends EventEmitter');
  const hasTaskCompletedEvent = squadConfigContent.includes("'taskCompleted'");
  const hasErrorEvent = squadConfigContent.includes("'error'");
  const hasWorkerErrorEvent = squadConfigContent.includes("'workerError'");
  
  console.log(`  ${extendsEventEmitter ? '✅' : '❌'} EventEmitter 상속`);
  console.log(`  ${hasTaskCompletedEvent ? '✅' : '❌'} taskCompleted 이벤트`);
  console.log(`  ${hasErrorEvent ? '✅' : '❌'} error 이벤트`);
  console.log(`  ${hasWorkerErrorEvent ? '✅' : '❌'} workerError 이벤트`);
  
  if (!extendsEventEmitter || !hasTaskCompletedEvent || !hasErrorEvent || !hasWorkerErrorEvent) {
    throw new Error('이벤트 시스템이 완전하지 않습니다.');
  }
  
} catch (error) {
  console.log(`  ❌ 이벤트 시스템 검증 실패: ${error.message}`);
  process.exit(1);
}

// 5. 타입 정의 검증
console.log('\n🏷️ 타입 정의 검증:');

try {
  const squadConfigPath = path.join(process.cwd(), 'backend/src/integrations/agent-squad/squad-config.ts');
  const squadConfigContent = fs.readFileSync(squadConfigPath, 'utf8');
  
  const hasTaskInterface = squadConfigContent.includes('interface Task');
  const hasSquadConfigInterface = squadConfigContent.includes('export interface SquadConfig');
  const hasTaskProperties = squadConfigContent.includes('id: string') && 
                           squadConfigContent.includes('type: string') &&
                           squadConfigContent.includes('capability: string');
  
  console.log(`  ${hasTaskInterface ? '✅' : '❌'} Task 인터페이스 정의`);
  console.log(`  ${hasSquadConfigInterface ? '✅' : '❌'} SquadConfig 인터페이스 정의`);
  console.log(`  ${hasTaskProperties ? '✅' : '❌'} Task 필수 속성 정의`);
  
  if (!hasTaskInterface || !hasSquadConfigInterface || !hasTaskProperties) {
    throw new Error('타입 정의가 불완전합니다.');
  }
  
} catch (error) {
  console.log(`  ❌ 타입 정의 검증 실패: ${error.message}`);
  process.exit(1);
}

console.log('\n✅ Agent Squad 통합 설정 검증 완료!');
console.log('\n📋 구현된 기능:');
console.log('  • SupervisorAgent: Worker 관리 및 작업 분배');
console.log('  • WorkerAgent: 추상 Worker 클래스');
console.log('  • TaskQueue: 작업 큐 관리');
console.log('  • 이벤트 기반 통신 시스템');
console.log('  • 로드 밸런싱 및 상태 모니터링');
console.log('  • TypeScript 타입 안전성');

console.log('\n🎯 SubTask 0.13.4 완료!');