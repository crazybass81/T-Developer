import fs from 'fs/promises';
import chalk from 'chalk';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

interface ChecklistItem {
  task: string;
  description: string;
  check: () => Promise<boolean>;
  critical: boolean;
}

class Phase0Checklist {
  private items: ChecklistItem[] = [
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
      task: '0.13.1',
      description: '에이전트 프레임워크',
      check: async () => {
        try {
          await fs.access('backend/src/agents/framework/base-agent.ts');
          return true;
        } catch {
          return false;
        }
      },
      critical: true
    }
  ];
  
  async run(): Promise<void> {
    console.log(chalk.blue.bold('\n🔍 Phase 0 완료 체크리스트\n'));
    console.log(chalk.gray('='.repeat(60)) + '\n');
    
    let passCount = 0;
    let criticalFailCount = 0;
    
    for (const item of this.items) {
      const result = await item.check();
      const icon = result ? chalk.green('✅') : chalk.red('❌');
      const taskColor = result ? chalk.green : chalk.red;
      
      console.log(
        `${icon} ${chalk.gray(`[${item.task}]`)} ${taskColor(item.description)}` +
        (item.critical && !result ? chalk.red(' (필수)') : '')
      );
      
      if (result) {
        passCount++;
      } else if (item.critical) {
        criticalFailCount++;
      }
    }
    
    console.log('\n' + chalk.gray('='.repeat(60)));
    console.log(chalk.blue.bold('\n📊 결과 요약\n'));
    
    const totalItems = this.items.length;
    const completionRate = Math.round((passCount / totalItems) * 100);
    
    console.log(`완료: ${chalk.green(passCount)}/${totalItems} (${completionRate}%)`);
    console.log(`필수 항목 실패: ${chalk.red(criticalFailCount)}`);
    
    if (criticalFailCount > 0) {
      console.log('\n' + chalk.red.bold('❌ Phase 0를 완료하기 전에 필수 항목을 해결해야 합니다.'));
    } else if (passCount === totalItems) {
      console.log('\n' + chalk.green.bold('🎉 축하합니다! Phase 0가 완벽하게 완료되었습니다!'));
      console.log(chalk.green('이제 Phase 1로 진행할 수 있습니다.'));
    } else {
      console.log('\n' + chalk.yellow.bold('⚠️  Phase 0의 필수 항목은 완료되었지만 일부 선택 항목이 남아있습니다.'));
      console.log(chalk.yellow('Phase 1로 진행할 수 있지만, 나중에 완료하는 것을 권장합니다.'));
    }
    
    console.log('\n' + chalk.blue.bold('📌 다음 단계:'));
    console.log(chalk.gray('1. 남은 항목 완료 (선택사항)'));
    console.log(chalk.gray('2. Phase 1: 코어 인프라 구축 시작'));
    console.log(chalk.gray('   - npm run phase1:start'));
  }
}

if (require.main === module) {
  const checklist = new Phase0Checklist();
  checklist.run().catch(console.error);
}

export { Phase0Checklist };