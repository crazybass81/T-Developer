import { writeFileSync, mkdirSync } from 'fs';
import { join } from 'path';

export class CustomTestReporter {
  private results: any[] = [];
  
  onRunStart() {
    this.results = [];
    console.log('🧪 테스트 실행 시작...');
  }
  
  onTestResult(test: any, testResult: any) {
    this.results.push({
      testPath: test.path,
      duration: testResult.perfStats.runtime,
      passed: testResult.numFailingTests === 0,
      coverage: testResult.coverage
    });
  }
  
  onRunComplete(contexts: any, results: any) {
    const report = {
      startTime: results.startTime,
      endTime: Date.now(),
      duration: Date.now() - results.startTime,
      numTotalTests: results.numTotalTests,
      numPassedTests: results.numPassedTests,
      numFailedTests: results.numFailedTests,
      numPendingTests: results.numPendingTests,
      testResults: this.results,
      coverage: results.coverageMap
    };
    
    // 리포트 디렉토리 생성
    const reportDir = join(process.cwd(), 'test-reports');
    mkdirSync(reportDir, { recursive: true });
    
    // JSON 리포트 저장
    writeFileSync(
      join(reportDir, 'test-results.json'),
      JSON.stringify(report, null, 2)
    );
    
    // 간단한 요약 출력
    console.log('\n📊 테스트 결과 요약:');
    console.log(`✅ 성공: ${results.numPassedTests}`);
    console.log(`❌ 실패: ${results.numFailedTests}`);
    console.log(`⏭️  스킵: ${results.numPendingTests}`);
    console.log(`⏱️  시간: ${(report.duration / 1000).toFixed(2)}초`);
  }
}