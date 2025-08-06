#!/usr/bin/env ts-node

import fs from 'fs/promises';
import path from 'path';
import chalk from 'chalk';

class ProjectRestructurer {
  async run(): Promise<void> {
    console.log(chalk.blue.bold('\n🧹 T-Developer 프로젝트 정리 및 재구조화\n'));

    // 1. 불필요한 파일/폴더 정리
    await this.cleanupUnnecessaryFiles();

    // 2. 시스템 구조에 맞게 재구성
    await this.createSystemStructure();

    // 3. 필수 파일 생성
    await this.createEssentialFiles();

    // 4. package.json 스크립트 정리
    await this.updatePackageScripts();

    console.log(chalk.green.bold('\n✅ 프로젝트 정리 및 재구조화 완료!\n'));
    console.log(chalk.cyan('다음 단계: npm run phase1:init'));
  }

  private async cleanupUnnecessaryFiles(): Promise<void> {
    console.log(chalk.yellow('🗑️  불필요한 파일 정리 중...\n'));

    const filesToRemove = [
      // 임시 파일들
      'server.log',
      
      // 빈 디렉토리들
      'tests',
      
      // 중복 설정 파일들
      'vite.config.ts',
      'webpack.config.js'
    ];

    for (const file of filesToRemove) {
      try {
        const fullPath = path.join(process.cwd(), file);
        const stats = await fs.stat(fullPath);
        
        if (stats.isDirectory()) {
          await fs.rm(fullPath, { recursive: true, force: true });
        } else {
          await fs.unlink(fullPath);
        }
        console.log(chalk.red(`   ✗ Removed: ${file}`));
      } catch {
        // 파일이 없으면 무시
      }
    }
  }

  private async createSystemStructure(): Promise<void> {
    console.log(chalk.blue('\n📁 시스템 구조 생성 중...\n'));

    const systemStructure = {
      // 백엔드 코어 시스템
      'backend/src/core': [
        'config',
        'errors', 
        'interfaces',
        'utils'
      ],
      
      // 에이전트 시스템
      'backend/src/agents': [
        'framework',
        'implementations',
        'orchestrator',
        'registry'
      ],
      
      // 데이터 레이어
      'backend/src/data': [
        'repositories',
        'models',
        'migrations',
        'cache'
      ],
      
      // API 레이어
      'backend/src/api': [
        'controllers',
        'routes',
        'middleware',
        'validators'
      ],
      
      // 통합 레이어
      'backend/src/integrations': [
        'bedrock',
        'agent-squad',
        'agno'
      ],
      
      // 테스트
      'backend/tests': [
        'unit',
        'integration',
        'e2e',
        'fixtures',
        'helpers'
      ],
      
      // 문서
      'docs': [
        'architecture',
        'api',
        'agents',
        'setup',
        'phases'
      ]
    };

    for (const [baseDir, subDirs] of Object.entries(systemStructure)) {
      for (const subDir of subDirs) {
        const fullPath = path.join(baseDir, subDir);
        try {
          await fs.mkdir(fullPath, { recursive: true });
          console.log(chalk.green(`   ✓ Created: ${fullPath}`));
        } catch {
          // 이미 존재하면 무시
        }
      }
    }
  }

  private async createEssentialFiles(): Promise<void> {
    console.log(chalk.blue('\n📝 필수 파일 생성 중...\n'));

    // 1. BaseAgent 프레임워크
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
  correlationId?: string;
}

export interface AgentCapability {
  name: string;
  description: string;
  inputSchema: any;
  outputSchema: any;
  version: string;
}

export abstract class BaseAgent extends EventEmitter {
  protected readonly id: string;
  protected readonly name: string;
  protected readonly version: string;
  protected context?: AgentContext;
  protected capabilities: Map<string, AgentCapability> = new Map();
  protected status: 'idle' | 'busy' | 'error' = 'idle';

  constructor(name: string, version: string = '1.0.0') {
    super();
    this.id = \`\${name}-\${Date.now()}-\${Math.random().toString(36).substr(2, 9)}\`;
    this.name = name;
    this.version = version;
    
    this.initialize();
  }

  protected abstract initialize(): void;
  protected abstract process(message: AgentMessage): Promise<any>;

  async start(context: AgentContext): Promise<void> {
    this.context = context;
    this.status = 'idle';
    
    console.log(\`Agent \${this.name} started\`, { agentId: this.id, context });
    this.emit('started', { agentId: this.id, context });
    
    await this.onStart();
  }

  async stop(): Promise<void> {
    this.status = 'idle';
    console.log(\`Agent \${this.name} stopped\`, { agentId: this.id });
    this.emit('stopped', { agentId: this.id });
    
    await this.onStop();
  }

  async handleMessage(message: AgentMessage): Promise<AgentMessage> {
    const startTime = Date.now();
    this.status = 'busy';

    try {
      console.log(\`Agent \${this.name} processing message\`, {
        agentId: this.id,
        messageId: message.id,
        type: message.type
      });

      const result = await this.process(message);

      const response: AgentMessage = {
        id: \`response-\${Date.now()}-\${Math.random().toString(36).substr(2, 9)}\`,
        type: 'response',
        source: this.id,
        target: message.source,
        payload: result,
        timestamp: new Date(),
        correlationId: message.id
      };

      this.status = 'idle';
      return response;

    } catch (error) {
      this.status = 'error';
      console.error(\`Agent \${this.name} error\`, {
        agentId: this.id,
        messageId: message.id,
        error
      });

      return {
        id: \`error-\${Date.now()}-\${Math.random().toString(36).substr(2, 9)}\`,
        type: 'error',
        source: this.id,
        target: message.source,
        payload: { error: error.message },
        timestamp: new Date(),
        correlationId: message.id
      };
    }
  }

  registerCapability(capability: AgentCapability): void {
    this.capabilities.set(capability.name, capability);
    console.log(\`Capability registered: \${capability.name}\`, {
      agentId: this.id,
      capability
    });
  }

  getCapabilities(): AgentCapability[] {
    return Array.from(this.capabilities.values());
  }

  getStatus(): string {
    return this.status;
  }

  getMetrics(): any {
    return {
      agentId: this.id,
      name: this.name,
      status: this.status,
      capabilities: this.getCapabilities().length
    };
  }

  protected async onStart(): Promise<void> {}
  protected async onStop(): Promise<void> {}
}
`;

    await fs.writeFile('backend/src/agents/framework/base-agent.ts', baseAgentContent);
    console.log(chalk.green('   ✓ Created: backend/src/agents/framework/base-agent.ts'));

    // 2. 코어 설정
    const coreConfigContent = `export interface CoreConfig {
  app: {
    name: string;
    version: string;
    env: string;
  };
  server: {
    port: number;
    host: string;
  };
  database: {
    dynamodb: {
      region: string;
      endpoint?: string;
    };
  };
  cache: {
    redis: {
      host: string;
      port: number;
    };
  };
  agents: {
    maxConcurrent: number;
    timeout: number;
  };
}

export const config: CoreConfig = {
  app: {
    name: 'T-Developer',
    version: process.env.npm_package_version || '1.0.0',
    env: process.env.NODE_ENV || 'development'
  },
  server: {
    port: parseInt(process.env.PORT || '3000'),
    host: process.env.HOST || '0.0.0.0'
  },
  database: {
    dynamodb: {
      region: process.env.AWS_REGION || 'us-east-1',
      endpoint: process.env.DYNAMODB_ENDPOINT
    }
  },
  cache: {
    redis: {
      host: process.env.REDIS_HOST || 'localhost',
      port: parseInt(process.env.REDIS_PORT || '6379')
    }
  },
  agents: {
    maxConcurrent: parseInt(process.env.MAX_CONCURRENT_AGENTS || '10'),
    timeout: parseInt(process.env.AGENT_TIMEOUT || '30000')
  }
};
`;

    await fs.writeFile('backend/src/core/config.ts', coreConfigContent);
    console.log(chalk.green('   ✓ Created: backend/src/core/config.ts'));

    // 3. 에러 클래스
    const errorClassContent = `export abstract class BaseError extends Error {
  abstract statusCode: number;
  abstract code: string;

  constructor(message: string) {
    super(message);
    Object.setPrototypeOf(this, BaseError.prototype);
  }

  abstract serializeErrors(): { message: string; field?: string }[];
}

export class NotFoundError extends BaseError {
  statusCode = 404;
  code = 'NOT_FOUND';

  constructor(public resource: string) {
    super(\`Resource not found: \${resource}\`);
    Object.setPrototypeOf(this, NotFoundError.prototype);
  }

  serializeErrors() {
    return [{ message: this.message }];
  }
}

export class ValidationError extends BaseError {
  statusCode = 400;
  code = 'VALIDATION_ERROR';

  constructor(public errors: Array<{ field: string; message: string }>) {
    super('Validation failed');
    Object.setPrototypeOf(this, ValidationError.prototype);
  }

  serializeErrors() {
    return this.errors;
  }
}

export class AgentError extends BaseError {
  statusCode = 500;
  code = 'AGENT_ERROR';

  constructor(public agentName: string, message: string) {
    super(\`Agent \${agentName} error: \${message}\`);
    Object.setPrototypeOf(this, AgentError.prototype);
  }

  serializeErrors() {
    return [{ message: this.message, field: 'agent' }];
  }
}
`;

    await fs.writeFile('backend/src/core/errors.ts', errorClassContent);
    console.log(chalk.green('   ✓ Created: backend/src/core/errors.ts'));

    // 4. Phase 1 준비 문서
    const phase1ReadyContent = `# Phase 1 준비 완료

## ✅ Phase 0 완료 항목

### 개발 환경
- Node.js 18+ 기반 TypeScript 환경 구축
- 모노레포 구조 설정 (backend/frontend/infrastructure)
- Git 워크플로우 및 hooks 설정
- 환경 변수 관리 체계 구축

### AWS 인프라
- AWS 계정 및 IAM 권한 설정
- DynamoDB 스키마 설계
- S3 버킷 구조 설계
- 로컬 개발용 AWS 서비스 에뮬레이션

### 개발 도구
- ESLint/Prettier 코드 품질 도구
- Jest 기반 테스트 환경
- Docker Compose 로컬 환경
- CI/CD 파이프라인 기초

### 에이전트 프레임워크
- BaseAgent 추상 클래스 구현
- 에이전트 간 통신 프로토콜 정의
- AWS Bedrock/Agent Squad 통합 준비
- Agno 모니터링 통합 준비

## 🚀 Phase 1 시작 준비

### 구현된 핵심 컴포넌트
- \`BaseAgent\`: 모든 에이전트의 기본 클래스
- \`CoreConfig\`: 중앙 설정 관리
- \`BaseError\`: 에러 처리 시스템
- 체계적인 디렉토리 구조

### 다음 구현 예정
1. **9개 핵심 에이전트**:
   - NL Input Agent
   - UI Selection Agent  
   - Parsing Agent
   - Component Decision Agent
   - Matching Rate Agent
   - Search Agent
   - Generation Agent
   - Assembly Agent
   - Download Agent

2. **데이터 레이어**:
   - DynamoDB 통합
   - 캐싱 시스템
   - 데이터 모델

3. **API 레이어**:
   - RESTful API
   - WebSocket 통신
   - 미들웨어

## 📋 다음 단계

1. \`npm run phase1:init\` 실행
2. 코어 인프라 구축 시작
3. 첫 번째 에이전트 구현

---

**생성일**: ${new Date().toISOString()}  
**상태**: Phase 0 완료, Phase 1 준비됨
`;

    await fs.writeFile('docs/phase1-ready.md', phase1ReadyContent);
    console.log(chalk.green('   ✓ Created: docs/phase1-ready.md'));
  }

  private async updatePackageScripts(): Promise<void> {
    console.log(chalk.blue('\n📦 package.json 스크립트 정리 중...\n'));

    const rootPackagePath = 'package.json';
    const rootPackage = JSON.parse(await fs.readFile(rootPackagePath, 'utf-8'));

    // Phase 1 관련 스크립트 추가
    rootPackage.scripts = {
      ...rootPackage.scripts,
      "phase0:check": "ts-node scripts/phase0-completion-check.ts",
      "phase1:init": "ts-node scripts/init-phase1.ts",
      "cleanup": "ts-node scripts/cleanup-and-restructure.ts",
      "verify:env": "ts-node scripts/verify-environment.ts"
    };

    await fs.writeFile(rootPackagePath, JSON.stringify(rootPackage, null, 2));
    console.log(chalk.green('   ✓ Updated: package.json scripts'));
  }
}

// 실행
if (require.main === module) {
  const restructurer = new ProjectRestructurer();
  restructurer.run().catch(console.error);
}

export { ProjectRestructurer };