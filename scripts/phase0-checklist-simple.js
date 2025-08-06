#!/usr/bin/env node

const fs = require('fs').promises;
const { exec } = require('child_process');
const { promisify } = require('util');

const execAsync = promisify(exec);

// Simple color functions
const colors = {
  green: (text) => `\x1b[32m${text}\x1b[0m`,
  red: (text) => `\x1b[31m${text}\x1b[0m`,
  blue: (text) => `\x1b[34m${text}\x1b[0m`,
  yellow: (text) => `\x1b[33m${text}\x1b[0m`,
  white: (text) => `\x1b[37m${text}\x1b[0m`,
  bold: (text) => `\x1b[1m${text}\x1b[0m`
};

class Phase0Checklist {
  constructor() {
    this.items = [
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
        task: '0.1.2',
        description: '프로젝트 구조 생성',
        check: async () => {
          const dirs = ['backend', 'frontend', 'infrastructure', 'docs'];
          for (const dir of dirs) {
            try {
              await fs.access(dir);
            } catch {
              return false;
            }
          }
          return true;
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
      {
        task: '0.2.1',
        description: 'AWS 계정 및 권한 설정',
        check: async () => {
          try {
            const { stdout } = await execAsync('aws sts get-caller-identity');
            return stdout.includes('UserId');
          } catch {
            return false;
          }
        },
        critical: true
      },
      {
        task: '0.3.1',
        description: '백엔드 의존성 설치',
        check: async () => {
          try {
            await fs.access('backend/node_modules');
            await fs.access('backend/package.json');
            return true;
          } catch {
            return false;
          }
        },
        critical: true
      },
      {
        task: '0.5.1',
        description: '테스트 환경 구축',
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
      {
        task: '0.6.1',
        description: 'Docker 환경 설정',
        check: async () => {
          try {
            await fs.access('docker-compose.yml');
            return true;
          } catch {
            return false;
          }
        },
        critical: false
      }
    ];
  }

  async runChecklist() {
    console.log(colors.bold(colors.blue('🔍 Phase 0 완료 체크리스트\n')));
    
    let passed = 0;
    let failed = 0;
    let criticalFailed = 0;

    for (const item of this.items) {
      const result = await item.check();
      const icon = result ? colors.green('✅') : colors.red('❌');
      const critical = item.critical ? colors.red('[CRITICAL]') : '';
      
      console.log(`${icon} ${item.task}: ${item.description} ${critical}`);
      
      if (result) {
        passed++;
      } else {
        failed++;
        if (item.critical) {
          criticalFailed++;
        }
      }
    }

    console.log('\n' + colors.blue('='.repeat(60)));
    console.log(colors.white('결과 요약:'));
    console.log(colors.green(`✅ 통과: ${passed}`));
    console.log(colors.red(`❌ 실패: ${failed}`));
    
    if (criticalFailed > 0) {
      console.log(colors.bold(colors.red(`\n⚠️  ${criticalFailed}개의 중요한 항목이 실패했습니다!`)));
      console.log(colors.yellow('Phase 1으로 진행하기 전에 이 항목들을 완료하세요.'));
      process.exit(1);
    } else if (failed > 0) {
      console.log(colors.bold(colors.yellow(`\n⚠️  ${failed}개의 선택적 항목이 실패했습니다.`)));
      console.log(colors.green('Phase 1으로 진행할 수 있지만, 나중에 완료하는 것을 권장합니다.'));
    } else {
      console.log(colors.bold(colors.green('\n🎉 Phase 0 완료! Phase 1으로 진행할 수 있습니다.')));
    }
  }
}

// 실행
if (require.main === module) {
  const checklist = new Phase0Checklist();
  checklist.runChecklist().catch(console.error);
}

module.exports = { Phase0Checklist };