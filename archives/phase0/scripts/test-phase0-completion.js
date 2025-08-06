#!/usr/bin/env node

const fs = require('fs').promises;
const path = require('path');
const chalk = require('chalk');

async function testPhase0Completion() {
  console.log(chalk.blue.bold('\n🧪 Phase 0 완료 검증 테스트\n'));
  
  const tests = [
    {
      name: '체크리스트 스크립트 존재',
      test: async () => {
        await fs.access('scripts/phase0-checklist.ts');
        return true;
      }
    },
    {
      name: 'Phase 1 초기화 스크립트 존재',
      test: async () => {
        await fs.access('scripts/init-phase1.ts');
        return true;
      }
    },
    {
      name: '아카이브 스크립트 존재',
      test: async () => {
        await fs.access('scripts/archive-phase0.sh');
        return true;
      }
    },
    {
      name: 'package.json에 Phase 스크립트 추가',
      test: async () => {
        const packageJson = JSON.parse(await fs.readFile('backend/package.json', 'utf8'));
        return packageJson.scripts['phase0:checklist'] && 
               packageJson.scripts['phase1:init'] &&
               packageJson.scripts['phase1:start'];
      }
    }
  ];
  
  let passed = 0;
  
  for (const test of tests) {
    try {
      const result = await test.test();
      if (result) {
        console.log(chalk.green(`✅ ${test.name}`));
        passed++;
      } else {
        console.log(chalk.red(`❌ ${test.name}`));
      }
    } catch (error) {
      console.log(chalk.red(`❌ ${test.name}: ${error.message}`));
    }
  }
  
  console.log(chalk.gray('\n' + '='.repeat(50)));
  console.log(chalk.blue.bold(`\n📊 결과: ${passed}/${tests.length} 테스트 통과\n`));
  
  if (passed === tests.length) {
    console.log(chalk.green.bold('🎉 Phase 0 완료 작업이 성공적으로 구현되었습니다!'));
    console.log(chalk.green('\n다음 명령으로 Phase 0 체크리스트를 실행하세요:'));
    console.log(chalk.cyan('  cd backend && npm run phase0:checklist'));
  } else {
    console.log(chalk.red.bold('❌ 일부 테스트가 실패했습니다.'));
  }
}

testPhase0Completion().catch(console.error);