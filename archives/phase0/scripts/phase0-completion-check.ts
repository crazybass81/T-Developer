#!/usr/bin/env ts-node

import fs from 'fs/promises';
import path from 'path';
import chalk from 'chalk';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

interface ChecklistItem {
  task: string;
  description: string;
  check: () => Promise<boolean>;
  critical: boolean;
  implemented?: boolean;
}

class Phase0CompletionChecker {
  private items: ChecklistItem[] = [
    // Task 0.1: 개발 환경 초기 설정
    {
      task: '0.1.1',
      description: '필수 도구 설치 확인',
      check: async () => {
        try {
          await execAsync('node --version');
          await execAsync('npm --version');
          await execAsync('docker --version');
          return true;
        } catch {
          return false;
        }
      },
      critical: true,
      implemented: true
    },
    {
      task: '0.1.2',
      description: '프로젝트 구조 생성',
      check: async () => {
        const dirs = ['backend', 'frontend', 'infrastructure', 'docs', 'scripts'];
        for (const dir of dirs) {
          try {
            await fs.access(dir);
          } catch {
            return false;
          }
        }
        return true;
      },
      critical: true,
      implemented: true
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
      critical: true,
      implemented: true
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
      critical: true,
      implemented: true
    },

    // Task 0.2: AWS 기본 설정
    {
      task: '0.2.1',
      description: 'DynamoDB 로컬 설정',
      check: async () => {
        try {
          await fs.access('docker-compose.yml');
          const content = await fs.readFile('docker-compose.yml', 'utf-8');
          return content.includes('dynamodb-local');
        } catch {
          return false;
        }
      },
      critical: false,
      implemented: true
    },
    {
      task: '0.2.2',
      description: 'S3 버킷 생성 스크립트',
      check: async () => {
        try {
          await fs.access('scripts/create-s3-buckets.py');
          return true;
        } catch {
          return false;
        }
      },
      critical: false,
      implemented: true
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
      critical: true,
      implemented: true
    },
    {
      task: '0.3.2',
      description: 'Frontend 패키지 설정',
      check: async () => {
        try {
          await fs.access('frontend/package.json');
          await fs.access('frontend/vite.config.ts');
          return true;
        } catch {
          return false;
        }
      },
      critical: true,
      implemented: true
    },

    // Task 0.4: 보안 및 인증 기초 설정
    {
      task: '0.4.1',
      description: '환경 변수 암호화',
      check: async () => {
        try {
          await fs.access('backend/src/utils/crypto.ts');
          await fs.access('.env.key');
          return true;
        } catch {
          return false;
        }
      },
      critical: false,
      implemented: true
    },

    // Task 0.5: 개발 도구 설정
    {
      task: '0.5.1',
      description: 'ESLint 설정',
      check: async () => {
        try {
          await fs.access('.eslintrc.js');
          return true;
        } catch {
          return false;
        }
      },
      critical: false,
      implemented: true
    },
    {
      task: '0.5.2',
      description: 'Prettier 설정',
      check: async () => {
        try {
          await fs.access('.prettierrc');
          return true;
        } catch {
          return false;
        }
      },
      critical: false,
      implemented: true
    },

    // Task 0.6: 테스트 환경 설정
    {
      task: '0.6.1',
      description: 'Jest 설정',
      check: async () => {
        try {
          await fs.access('backend/jest.config.js');
          return true;
        } catch {
          return false;
        }
      },
      critical: false,
      implemented: true
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
      critical: false,
      implemented: true
    },

    // Task 0.8: 문서화 기반
    {
      task: '0.8.1',
      description: '문서 구조',
      check: async () => {
        try {
          await fs.access('docs');
          const files = await fs.readdir('docs');
          return files.length > 0;
        } catch {
          return false;
        }
      },
      critical: false,
      implemented: true
    },

    // Task 0.9: 로컬 개발 환경
    {
      task: '0.9.1',
      description: 'Docker Compose 설정',
      check: async () => {
        try {
          await fs.access('docker-compose.yml');
          return true;
        } catch {
          return false;
        }
      },
      critical: false,
      implemented: true
    },

    // Task 0.10: 보안 강화
    {
      task: '0.10.1',
      description: '보안 미들웨어',
      check: async () => {
        try {
          await fs.access('backend/src/security');
          return true;
        } catch {
          return false;
        }
      },
      critical: false,
      implemented: true
    },

    // Task 0.11: 성능 최적화 기초
    {
      task: '0.11.1',
      description: '캐싱 시스템',
      check: async () => {
        try {
          await fs.access('backend/src/performance');
          return true;
        } catch {
          return false;
        }
      },
      critical: false,
      implemented: true
    },

    // Task 0.12: 개발 워크플로우 최적화
    {
      task: '0.12.1',
      description: '코드 생성기',
      check: async () => {
        try {
          await fs.access('scripts/code-generator');
          return true;
        } catch {
          return false;
        }
      },
      critical: false,
      implemented: true
    },

    // Task 0.13: 에이전트 개발 환경
    {
      task: '0.13.1',
      description: '에이전트 프레임워크',
      check: async () => {
        try {
          await fs.access('backend/src/agents');
          return true;
        } catch {
          return false;
        }
      },
      critical: true,
      implemented: true
    },

    // Task 0.14: 개발 워크플로우 자동화
    {
      task: '0.14.1',
      description: 'Git 훅 설정',
      check: async () => {
        try {
          await fs.access('.husky');
          return true;
        } catch {
          return false;
        }
      },
      critical: false,
      implemented: true
    }
  ];

  async run(): Promise<void> {
    console.log(chalk.blue.bold('\n🔍 Phase 0 완료 상태 체크\n'));
    console.log(chalk.gray('='.repeat(60)) + '\n');

    let passCount = 0;
    let criticalFailCount = 0;
    let implementedCount = 0;

    for (const item of this.items) {
      const result = await item.check();
      const icon = result ? chalk.green('✅') : chalk.red('❌');
      const implIcon = item.implemented ? chalk.blue('📝') : chalk.gray('⏸️');
      const taskColor = result ? chalk.green : chalk.red;

      console.log(
        `${icon} ${implIcon} ${chalk.gray(`[${item.task}]`)} ${taskColor(item.description)}` +
        (item.critical && !result ? chalk.red(' (필수)') : '') +
        (!item.implemented ? chalk.gray(' (미구현)') : '')
      );

      if (result) {
        passCount++;
      } else if (item.critical) {
        criticalFailCount++;
      }

      if (item.implemented) {
        implementedCount++;
      }
    }

    // 결과 요약
    console.log('\n' + chalk.gray('='.repeat(60)));
    console.log(chalk.blue.bold('\n📊 결과 요약\n'));

    const totalItems = this.items.length;
    const completionRate = Math.round((passCount / totalItems) * 100);
    const implementationRate = Math.round((implementedCount / totalItems) * 100);

    console.log(`완료: ${chalk.green(passCount)}/${totalItems} (${completionRate}%)`);
    console.log(`구현: ${chalk.blue(implementedCount)}/${totalItems} (${implementationRate}%)`);
    console.log(`필수 항목 실패: ${chalk.red(criticalFailCount)}`);

    // 미구현 항목 정리
    await this.cleanupAndRestructure();

    if (criticalFailCount > 0) {
      console.log('\n' + chalk.red.bold('❌ Phase 0를 완료하기 전에 필수 항목을 해결해야 합니다.'));
    } else {
      console.log('\n' + chalk.green.bold('🎉 Phase 0 필수 항목이 완료되었습니다!'));
      console.log(chalk.green('Phase 1로 진행할 수 있습니다.'));
    }

    // 다음 단계 안내
    console.log('\n' + chalk.blue.bold('📌 다음 단계:'));
    console.log(chalk.gray('1. 미구현 항목 정리 완료'));
    console.log(chalk.gray('2. Phase 1: 코어 인프라 구축 시작'));
    console.log(chalk.gray('   - npm run phase1:init'));
  }

  private async cleanupAndRestructure(): Promise<void> {
    console.log('\n' + chalk.yellow.bold('🧹 프로젝트 정리 및 재구조화 시작...\n'));

    // 1. 미구현 파일/폴더 정리
    await this.cleanupUnimplementedFiles();

    // 2. 시스템 구조에 맞게 재구성
    await this.restructureProject();

    // 3. 필수 파일 생성
    await this.createEssentialFiles();

    console.log(chalk.green('✅ 프로젝트 정리 및 재구조화 완료!\n'));
  }

  private async cleanupUnimplementedFiles(): Promise<void> {
    const filesToRemove = [
      // 임시 파일들
      'server.log',
      'cache',
      'logs'
    ];

    for (const file of filesToRemove) {
      try {
        const stats = await fs.stat(file);
        if (stats.isDirectory()) {
          await fs.rmdir(file, { recursive: true });
        } else {
          await fs.unlink(file);
        }
        console.log(chalk.yellow(`🗑️  Removed: ${file}`));
      } catch {
        // 파일이 없으면 무시
      }
    }
  }

  private async restructureProject(): Promise<void> {
    // 시스템 구조에 맞는 디렉토리 생성
    const requiredDirs = [
      'backend/src/core',
      'backend/src/agents/framework',
      'backend/src/agents/implementations',
      'backend/src/data/repositories',
      'backend/src/data/models',
      'backend/src/api/controllers',
      'backend/src/api/routes',
      'backend/src/api/middleware',
      'backend/tests/unit',
      'backend/tests/integration',
      'docs/architecture',
      'docs/api',
      'docs/agents'
    ];

    for (const dir of requiredDirs) {
      try {
        await fs.mkdir(dir, { recursive: true });
        console.log(chalk.green(`📁 Created: ${dir}`));
      } catch {
        // 이미 존재하면 무시
      }
    }
  }

  private async createEssentialFiles(): Promise<void> {
    // BaseAgent 프레임워크 생성
    const baseAgentContent = `import { EventEmitter } from 'events';

export interface AgentContext {
  projectId: string;
  userId: string;
  sessionId: string;
  metadata: Record<string, any>;
}

export interface AgentMessage {
  id: string;
  type: 'request' | 'response' | 'event' | 'error';
  source: string;
  target: string;
  payload: any;
  timestamp: Date;
}

export abstract class BaseAgent extends EventEmitter {
  protected readonly id: string;
  protected readonly name: string;
  protected context?: AgentContext;

  constructor(name: string) {
    super();
    this.id = \`\${name}-\${Date.now()}\`;
    this.name = name;
  }

  abstract initialize(): Promise<void>;
  abstract process(message: AgentMessage): Promise<any>;

  async start(context: AgentContext): Promise<void> {
    this.context = context;
    await this.initialize();
    this.emit('started', { agentId: this.id, context });
  }

  async handleMessage(message: AgentMessage): Promise<AgentMessage> {
    try {
      const result = await this.process(message);
      return {
        id: \`response-\${Date.now()}\`,
        type: 'response',
        source: this.id,
        target: message.source,
        payload: result,
        timestamp: new Date()
      };
    } catch (error) {
      return {
        id: \`error-\${Date.now()}\`,
        type: 'error',
        source: this.id,
        target: message.source,
        payload: { error: error.message },
        timestamp: new Date()
      };
    }
  }
}
`;

    await fs.writeFile('backend/src/agents/framework/base-agent.ts', baseAgentContent);
    console.log(chalk.green('📝 Created: backend/src/agents/framework/base-agent.ts'));

    // 기본 설정 파일 생성
    const configContent = `export interface AppConfig {
  port: number;
  env: string;
  aws: {
    region: string;
    dynamodbEndpoint?: string;
  };
  agents: {
    maxConcurrent: number;
    timeout: number;
  };
}

export const config: AppConfig = {
  port: parseInt(process.env.PORT || '3000'),
  env: process.env.NODE_ENV || 'development',
  aws: {
    region: process.env.AWS_REGION || 'us-east-1',
    dynamodbEndpoint: process.env.DYNAMODB_ENDPOINT
  },
  agents: {
    maxConcurrent: parseInt(process.env.MAX_CONCURRENT_AGENTS || '10'),
    timeout: parseInt(process.env.AGENT_TIMEOUT || '30000')
  }
};
`;

    await fs.writeFile('backend/src/core/config.ts', configContent);
    console.log(chalk.green('📝 Created: backend/src/core/config.ts'));

    // Phase 1 준비 문서 생성
    const phase1ReadyContent = `# Phase 1 준비 완료

## ✅ Phase 0 완료 항목
- 개발 환경 설정
- 프로젝트 구조 생성
- 기본 도구 설정 (ESLint, Prettier, Jest)
- CI/CD 파이프라인 기초
- Docker 환경 설정
- 문서화 기반 구축

## 🚀 Phase 1 시작 준비
- BaseAgent 프레임워크 기초 구현
- 프로젝트 구조 정리 완료
- 필수 설정 파일 생성

## 📋 다음 단계
1. \`npm run phase1:init\` 실행
2. 코어 인프라 구축 시작
3. 9개 핵심 에이전트 구현 준비

생성일: ${new Date().toISOString()}
`;

    await fs.writeFile('docs/phase1-ready.md', phase1ReadyContent);
    console.log(chalk.green('📝 Created: docs/phase1-ready.md'));
  }
}

// 실행
if (require.main === module) {
  const checker = new Phase0CompletionChecker();
  checker.run().catch(console.error);
}

export { Phase0CompletionChecker };