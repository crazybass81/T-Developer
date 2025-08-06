#!/usr/bin/env node

const fs = require('fs').promises;
const path = require('path');
const { exec } = require('child_process');
const { promisify } = require('util');

const execAsync = promisify(exec);

// 간단한 색상 함수
const colors = {
  green: (text) => `\x1b[32m${text}\x1b[0m`,
  red: (text) => `\x1b[31m${text}\x1b[0m`,
  blue: (text) => `\x1b[34m${text}\x1b[0m`,
  yellow: (text) => `\x1b[33m${text}\x1b[0m`,
  gray: (text) => `\x1b[90m${text}\x1b[0m`,
  bold: (text) => `\x1b[1m${text}\x1b[0m`
};

class Phase0Checklist {
  constructor() {
    this.items = [
      // Task 0.1: 개발 환경 초기 설정
      {
        task: '0.1.1',
        description: '필수 도구 설치 확인',
        check: async () => {
          try {
            await execAsync('node --version');
            await execAsync('npm --version');
            await execAsync('aws --version');
            await execAsync('docker --version');
            return true;
          } catch {
            return false;
          }
        },
        critical: true
      },
      {
        task: '0.1.3',
        description: 'Git 저장소 초기화',
        check: async () => {
          try {
            await fs.access('.git');
            await fs.access('.gitignore');
            return true;
          } catch {
            return false;
          }
        },
        critical: true
      },
      {
        task: '0.1.4',
        description: '환경 변수 템플릿',
        check: async () => {
          try {
            await fs.access('.env.example');
            return true;
          } catch {
            return false;
          }
        },
        critical: true
      },
      
      // Task 0.2: AWS 기본 설정
      {
        task: '0.2.1',
        description: 'DynamoDB 로컬 설정',
        check: async () => {
          try {
            await fs.access('docker-compose.dev.yml');
            return true;
          } catch {
            return false;
          }
        },
        critical: false
      },
      
      // Task 0.3: 프로젝트 의존성 설정
      {
        task: '0.3.1',
        description: 'Backend 패키지 설정',
        check: async () => {
          try {
            await fs.access('backend/package.json');
            await fs.access('backend/tsconfig.json');
            return true;
          } catch {
            return false;
          }
        },
        critical: true
      },
      {
        task: '0.3.2',
        description: 'Python 의존성 설정',
        check: async () => {
          try {
            await fs.access('requirements.txt');
            return true;
          } catch {
            return false;
          }
        },
        critical: true
      },
      
      // Task 0.4: 보안 및 인증 기초 설정
      {
        task: '0.4.1',
        description: '환경 변수 암호화',
        check: async () => {
          try {
            await fs.access('backend/src/utils/crypto.ts');
            return true;
          } catch {
            return false;
          }
        },
        critical: false
      },
      {
        task: '0.4.2',
        description: 'JWT 토큰 관리',
        check: async () => {
          try {
            await fs.access('backend/src/utils/auth.ts');
            return true;
          } catch {
            return false;
          }
        },
        critical: false
      },
      
      // Task 0.5: 테스트 환경 설정
      {
        task: '0.5.1',
        description: '테스트 헬퍼 생성',
        check: async () => {
          try {
            await fs.access('backend/tests/helpers/test-utils.ts');
            await fs.access('backend/jest.config.js');
            return true;
          } catch {
            return false;
          }
        },
        critical: false
      },
      
      // Task 0.6: 로컬 개발 환경
      {
        task: '0.6.1',
        description: 'Docker Compose 설정',
        check: async () => {
          try {
            await fs.access('docker-compose.yml');
            return true;
          } catch {
            return false;
          }
        },
        critical: false
      },
      
      // Task 0.7: CI/CD 파이프라인 기초
      {
        task: '0.7.1',
        description: 'GitHub Actions 워크플로우',
        check: async () => {
          try {
            await fs.access('.github/workflows');
            return true;
          } catch {
            return false;
          }
        },
        critical: false
      },
      
      // Task 0.10: 보안 강화
      {
        task: '0.10.1',
        description: '입력 검증 시스템',
        check: async () => {
          try {
            await fs.access('backend/src/security/input-validation.ts');
            return true;
          } catch {
            return false;
          }
        },
        critical: false
      },
      
      // Task 0.11: 성능 최적화
      {
        task: '0.11.1',
        description: '캐싱 시스템',
        check: async () => {
          try {
            await fs.access('backend/src/performance/caching.ts');
            return true;
          } catch {
            return false;
          }
        },
        critical: false
      },
      
      // Task 0.13: 에이전트 개발 환경
      {
        task: '0.13.2',
        description: '에이전트 통신 프로토콜',
        check: async () => {
          try {
            await fs.access('backend/src/agents/framework/communication.ts');
            return true;
          } catch {
            return false;
          }
        },
        critical: true
      }
    ];
  }
  
  async run() {
    console.log(colors.blue(colors.bold('\n🔍 Phase 0 완료 체크리스트\n')));
    console.log(colors.gray('='.repeat(60)) + '\n');
    
    let passCount = 0;
    let criticalFailCount = 0;
    
    for (const item of this.items) {
      const result = await item.check();
      const icon = result ? colors.green('✅') : colors.red('❌');
      const taskColor = result ? colors.green : colors.red;
      
      console.log(
        `${icon} ${colors.gray(`[${item.task}]`)} ${taskColor(item.description)}` +
        (item.critical && !result ? colors.red(' (필수)') : '')
      );
      
      if (result) {
        passCount++;
      } else if (item.critical) {
        criticalFailCount++;
      }
    }
    
    // 결과 요약
    console.log('\n' + colors.gray('='.repeat(60)));
    console.log(colors.blue(colors.bold('\n📊 결과 요약\n')));
    
    const totalItems = this.items.length;
    const completionRate = Math.round((passCount / totalItems) * 100);
    
    console.log(`완료: ${colors.green(passCount)}/${totalItems} (${completionRate}%)`);
    console.log(`필수 항목 실패: ${colors.red(criticalFailCount)}`);
    
    if (criticalFailCount > 0) {
      console.log('\n' + colors.red(colors.bold('❌ Phase 0를 완료하기 전에 필수 항목을 해결해야 합니다.')));
    } else if (passCount === totalItems) {
      console.log('\n' + colors.green(colors.bold('🎉 축하합니다! Phase 0가 완벽하게 완료되었습니다!')));
      console.log(colors.green('이제 Phase 1로 진행할 수 있습니다.'));
    } else {
      console.log('\n' + colors.yellow(colors.bold('⚠️  Phase 0의 필수 항목은 완료되었지만 일부 선택 항목이 남아있습니다.')));
      console.log(colors.yellow('Phase 1로 진행할 수 있지만, 나중에 완료하는 것을 권장합니다.'));
    }
    
    // 다음 단계 안내
    console.log('\n' + colors.blue(colors.bold('📌 다음 단계:')));
    console.log(colors.gray('1. 남은 항목 완료 (선택사항)'));
    console.log(colors.gray('2. Phase 1: 코어 인프라 구축 시작'));
    console.log(colors.gray('   - npm run phase1:start'));
  }
}

// 실행
if (require.main === module) {
  const checklist = new Phase0Checklist();
  checklist.run().catch(console.error);
}

module.exports = { Phase0Checklist };