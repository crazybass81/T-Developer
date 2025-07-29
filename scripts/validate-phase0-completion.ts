import { promises as fs } from 'fs';
import path from 'path';
import { logger } from '../backend/src/config/logger';

interface ValidationResult {
  passed: boolean;
  message: string;
  details?: any;
}

class Phase0Validator {
  private results: ValidationResult[] = [];

  async validateAll(): Promise<boolean> {
    console.log('🔍 Phase 0 완료 상태 검증 시작...\n');

    await this.validateEnvironmentSetup();
    await this.validateAWSResources();
    await this.validateDependencies();
    await this.validateSecurity();
    await this.validateTestEnvironment();
    await this.validateCodeGeneration();
    await this.validateAIIntegration();

    this.printResults();
    return this.results.every(r => r.passed);
  }

  private async validateEnvironmentSetup(): Promise<void> {
    console.log('📋 Task 0.1: 개발 환경 초기 설정 검증');

    // SubTask 0.1.1: 필수 도구 설치 확인
    try {
      const { execSync } = require('child_process');
      execSync('./scripts/check-requirements.sh', { stdio: 'pipe' });
      this.addResult(true, '✅ 필수 도구 설치 확인 완료');
    } catch (error) {
      this.addResult(false, '❌ 필수 도구 설치 확인 실패', error);
    }

    // SubTask 0.1.2: AWS 계정 및 권한 설정
    const awsConfigExists = await this.fileExists('.env') && 
                           await this.checkEnvVariable('AWS_ACCESS_KEY_ID');
    this.addResult(awsConfigExists, awsConfigExists ? 
      '✅ AWS 설정 확인 완료' : '❌ AWS 설정이 누락됨');

    // SubTask 0.1.3: 프로젝트 저장소 초기화
    const gitExists = await this.fileExists('.git');
    const readmeExists = await this.fileExists('README.md');
    this.addResult(gitExists && readmeExists, 
      gitExists && readmeExists ? '✅ 저장소 초기화 완료' : '❌ 저장소 초기화 미완료');

    // SubTask 0.1.4: 환경 변수 템플릿 생성
    const envExampleExists = await this.fileExists('.env.example');
    this.addResult(envExampleExists, envExampleExists ? 
      '✅ 환경 변수 템플릿 생성 완료' : '❌ 환경 변수 템플릿 누락');

    // SubTask 0.1.5: 개발 도구 설정 파일 생성
    const eslintExists = await this.fileExists('.eslintrc.js');
    const prettierExists = await this.fileExists('.prettierrc');
    this.addResult(eslintExists && prettierExists, 
      eslintExists && prettierExists ? '✅ 개발 도구 설정 완료' : '❌ 개발 도구 설정 미완료');
  }

  private async validateAWSResources(): Promise<void> {
    console.log('\n📋 Task 0.2: AWS 리소스 초기 설정 검증');

    // SubTask 0.2.1: DynamoDB 로컬 설정
    const dockerComposeExists = await this.fileExists('docker-compose.dev.yml');
    const setupScriptExists = await this.fileExists('scripts/setup-local-db.ts');
    this.addResult(dockerComposeExists && setupScriptExists, 
      dockerComposeExists && setupScriptExists ? '✅ DynamoDB 로컬 설정 완료' : '❌ DynamoDB 설정 미완료');

    // SubTask 0.2.2: S3 버킷 생성 스크립트
    const s3ScriptExists = await this.fileExists('scripts/create-s3-buckets.py');
    this.addResult(s3ScriptExists, s3ScriptExists ? 
      '✅ S3 버킷 스크립트 생성 완료' : '❌ S3 버킷 스크립트 누락');

    // SubTask 0.2.3: Bedrock 모델 액세스 요청
    const bedrockScriptExists = await this.fileExists('scripts/request-bedrock-access.ts');
    this.addResult(bedrockScriptExists, bedrockScriptExists ? 
      '✅ Bedrock 액세스 스크립트 생성 완료' : '❌ Bedrock 액세스 스크립트 누락');

    // SubTask 0.2.4: Lambda 레이어 준비
    const layerScriptExists = await this.fileExists('scripts/create-lambda-layers.sh');
    this.addResult(layerScriptExists, layerScriptExists ? 
      '✅ Lambda 레이어 스크립트 생성 완료' : '❌ Lambda 레이어 스크립트 누락');

    // SubTask 0.2.5: CloudWatch 대시보드 템플릿
    const dashboardExists = await this.fileExists('cloudwatch/dashboard-template.json');
    this.addResult(dashboardExists, dashboardExists ? 
      '✅ CloudWatch 대시보드 템플릿 생성 완료' : '❌ CloudWatch 대시보드 템플릿 누락');
  }

  private async validateDependencies(): Promise<void> {
    console.log('\n📋 Task 0.3: 프로젝트 의존성 설치 검증');

    // 백엔드 의존성
    const backendPackageExists = await this.fileExists('backend/package.json');
    const nodeModulesExists = await this.fileExists('node_modules');
    this.addResult(backendPackageExists && nodeModulesExists, 
      backendPackageExists && nodeModulesExists ? '✅ 백엔드 의존성 설치 완료' : '❌ 백엔드 의존성 설치 미완료');

    // Python 의존성
    const requirementsExists = await this.fileExists('requirements.txt');
    this.addResult(requirementsExists, requirementsExists ? 
      '✅ Python 의존성 파일 생성 완료' : '❌ Python 의존성 파일 누락');
  }

  private async validateSecurity(): Promise<void> {
    console.log('\n📋 Task 0.4: 보안 및 인증 기초 설정 검증');

    // 암호화 시스템
    const cryptoUtilExists = await this.fileExists('backend/src/utils/crypto.ts');
    const cryptoKeyExists = await this.fileExists('.env.key');
    this.addResult(cryptoUtilExists, cryptoUtilExists ? 
      '✅ 암호화 시스템 구현 완료' : '❌ 암호화 시스템 구현 미완료');

    // 입력 검증 시스템
    const validationExists = await this.fileExists('backend/src/security/input-validation.ts');
    this.addResult(validationExists, validationExists ? 
      '✅ 입력 검증 시스템 구현 완료' : '❌ 입력 검증 시스템 구현 미완료');

    // Rate Limiting
    const rateLimiterExists = await this.fileExists('backend/src/middleware/rate-limiter.ts');
    this.addResult(rateLimiterExists, rateLimiterExists ? 
      '✅ Rate Limiting 시스템 구현 완료' : '❌ Rate Limiting 시스템 구현 미완료');
  }

  private async validateTestEnvironment(): Promise<void> {
    console.log('\n📋 Task 0.5: 테스트 환경 구축 검증');

    // 테스트 헬퍼
    const testUtilsExists = await this.fileExists('backend/tests/helpers/test-utils.ts');
    this.addResult(testUtilsExists, testUtilsExists ? 
      '✅ 테스트 헬퍼 생성 완료' : '❌ 테스트 헬퍼 생성 미완료');

    // Jest 설정
    const jestConfigExists = await this.fileExists('backend/jest.config.js');
    this.addResult(jestConfigExists, jestConfigExists ? 
      '✅ Jest 설정 완료' : '❌ Jest 설정 미완료');
  }

  private async validateCodeGeneration(): Promise<void> {
    console.log('\n📋 개발 워크플로우 최적화 검증');

    // 코드 생성기
    const generatorExists = await this.fileExists('scripts/code-generator/generator.ts');
    this.addResult(generatorExists, generatorExists ? 
      '✅ 코드 생성기 구현 완료' : '❌ 코드 생성기 구현 미완료');

    // 모니터링 시스템
    const monitoringExists = await this.fileExists('backend/src/utils/monitoring.ts');
    this.addResult(monitoringExists, monitoringExists ? 
      '✅ 모니터링 시스템 구현 완료' : '❌ 모니터링 시스템 구현 미완료');
  }

  private async validateAIIntegration(): Promise<void> {
    console.log('\n📋 AI 멀티 에이전트 시스템 통합 검증');

    // 통합 에이전트 시스템
    const unifiedSystemExists = await this.fileExists('backend/src/services/ai/unified-agent-system.ts');
    this.addResult(unifiedSystemExists, unifiedSystemExists ? 
      '✅ 통합 에이전트 시스템 구현 완료' : '❌ 통합 에이전트 시스템 구현 미완료');

    // 기본 에이전트 프레임워크
    const baseAgentExists = await this.fileExists('backend/src/framework/base-agent.ts');
    this.addResult(baseAgentExists, baseAgentExists ? 
      '✅ 기본 에이전트 프레임워크 구현 완료' : '❌ 기본 에이전트 프레임워크 구현 미완료');
  }

  private async fileExists(filePath: string): Promise<boolean> {
    try {
      await fs.access(path.join(process.cwd(), filePath));
      return true;
    } catch {
      return false;
    }
  }

  private async checkEnvVariable(varName: string): Promise<boolean> {
    try {
      const envContent = await fs.readFile(path.join(process.cwd(), '.env'), 'utf8');
      return envContent.includes(`${varName}=`);
    } catch {
      return false;
    }
  }

  private addResult(passed: boolean, message: string, details?: any): void {
    this.results.push({ passed, message, details });
    console.log(`  ${message}`);
  }

  private printResults(): void {
    const passed = this.results.filter(r => r.passed).length;
    const total = this.results.length;
    const percentage = Math.round((passed / total) * 100);

    console.log('\n' + '='.repeat(60));
    console.log('📊 Phase 0 완료 상태 검증 결과');
    console.log('='.repeat(60));
    console.log(`총 검증 항목: ${total}`);
    console.log(`통과 항목: ${passed}`);
    console.log(`실패 항목: ${total - passed}`);
    console.log(`완료율: ${percentage}%`);
    
    if (percentage === 100) {
      console.log('\n🎉 Phase 0 완료! Phase 1으로 진행할 수 있습니다.');
    } else {
      console.log('\n⚠️  일부 항목이 미완료되었습니다. 위의 실패 항목들을 완료해주세요.');
    }
  }
}

async function main() {
  const validator = new Phase0Validator();
  const success = await validator.validateAll();
  process.exit(success ? 0 : 1);
}

if (require.main === module) {
  main();
}