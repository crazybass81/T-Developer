#!/usr/bin/env ts-node

import fs from 'fs/promises';
import path from 'path';
import chalk from 'chalk';

class Phase1Initializer {
  async initialize(): Promise<void> {
    console.log(chalk.blue.bold('\n🚀 Phase 1: 코어 인프라 구축 초기화\n'));
    
    // 1. 디렉토리 구조 생성
    await this.createDirectoryStructure();
    
    // 2. 기본 파일 생성
    await this.createBaseFiles();
    
    // 3. Phase 1 체크리스트 생성
    await this.createChecklist();
    
    console.log(chalk.green.bold('\n✅ Phase 1 초기화 완료!\n'));
    console.log(chalk.gray('다음 명령으로 시작하세요:'));
    console.log(chalk.cyan('  npm run dev'));
  }
  
  private async createDirectoryStructure(): Promise<void> {
    const directories = [
      // 코어 시스템
      'backend/src/core/config',
      'backend/src/core/errors',
      'backend/src/core/interfaces',
      'backend/src/core/utils',
      
      // 데이터 레이어
      'backend/src/data/repositories',
      'backend/src/data/models',
      'backend/src/data/cache',
      
      // API 레이어
      'backend/src/api/controllers',
      'backend/src/api/routes',
      'backend/src/api/middleware',
      'backend/src/api/validators',
      
      // 에이전트 시스템
      'backend/src/agents/implementations',
      'backend/src/agents/orchestrator',
      'backend/src/agents/registry',
      
      // 테스트
      'backend/tests/core',
      'backend/tests/data',
      'backend/tests/api',
      'backend/tests/agents'
    ];
    
    for (const dir of directories) {
      await fs.mkdir(dir, { recursive: true });
      console.log(chalk.green(`✓ Created: ${dir}`));
    }
  }
  
  private async createBaseFiles(): Promise<void> {
    // 코어 설정 파일
    const coreConfig = `// backend/src/core/config/index.ts
export interface CoreConfig {
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
    version: '1.0.0',
    env: process.env.NODE_ENV || 'development'
  },
  server: {
    port: parseInt(process.env.PORT || '3000'),
    host: process.env.HOST || 'localhost'
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

    await fs.writeFile('backend/src/core/config/index.ts', coreConfig);
    console.log(chalk.green('✓ Created: backend/src/core/config/index.ts'));

    // 에러 핸들링
    const errorHandler = `// backend/src/core/errors/index.ts
export class AppError extends Error {
  public readonly statusCode: number;
  public readonly isOperational: boolean;

  constructor(message: string, statusCode: number = 500, isOperational: boolean = true) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = isOperational;

    Error.captureStackTrace(this, this.constructor);
  }
}

export class ValidationError extends AppError {
  constructor(message: string) {
    super(message, 400);
  }
}

export class NotFoundError extends AppError {
  constructor(message: string = 'Resource not found') {
    super(message, 404);
  }
}

export class UnauthorizedError extends AppError {
  constructor(message: string = 'Unauthorized') {
    super(message, 401);
  }
}
`;

    await fs.writeFile('backend/src/core/errors/index.ts', errorHandler);
    console.log(chalk.green('✓ Created: backend/src/core/errors/index.ts'));

    // 기본 인터페이스
    const interfaces = `// backend/src/core/interfaces/index.ts
export interface Repository<T> {
  create(item: Omit<T, 'id'>): Promise<T>;
  findById(id: string): Promise<T | null>;
  findAll(filters?: Record<string, any>): Promise<T[]>;
  update(id: string, updates: Partial<T>): Promise<T>;
  delete(id: string): Promise<void>;
}

export interface CacheService {
  get<T>(key: string): Promise<T | null>;
  set<T>(key: string, value: T, ttl?: number): Promise<void>;
  delete(key: string): Promise<void>;
  clear(): Promise<void>;
}

export interface Logger {
  info(message: string, meta?: any): void;
  error(message: string, error?: Error, meta?: any): void;
  warn(message: string, meta?: any): void;
  debug(message: string, meta?: any): void;
}
`;

    await fs.writeFile('backend/src/core/interfaces/index.ts', interfaces);
    console.log(chalk.green('✓ Created: backend/src/core/interfaces/index.ts'));

    // 기본 유틸리티
    const utils = `// backend/src/core/utils/index.ts
export function generateId(prefix: string = ''): string {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substr(2, 9);
  return prefix ? \`\${prefix}_\${timestamp}_\${random}\` : \`\${timestamp}_\${random}\`;
}

export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

export function sanitizeInput(input: string): string {
  return input.trim().replace(/[<>]/g, '');
}
`;

    await fs.writeFile('backend/src/core/utils/index.ts', utils);
    console.log(chalk.green('✓ Created: backend/src/core/utils/index.ts'));

    // 기본 모델
    const models = `// backend/src/data/models/index.ts
export interface BaseModel {
  id: string;
  createdAt: string;
  updatedAt: string;
}

export interface Project extends BaseModel {
  name: string;
  description: string;
  userId: string;
  status: 'analyzing' | 'building' | 'completed' | 'error';
  requirements?: any;
  components?: any[];
  metadata?: Record<string, any>;
}

export interface Agent extends BaseModel {
  name: string;
  type: string;
  status: 'idle' | 'busy' | 'error';
  capabilities: string[];
  metadata?: Record<string, any>;
}

export interface User extends BaseModel {
  email: string;
  name: string;
  role: 'user' | 'admin';
  preferences?: Record<string, any>;
}
`;

    await fs.writeFile('backend/src/data/models/index.ts', models);
    console.log(chalk.green('✓ Created: backend/src/data/models/index.ts'));

    // 기본 컨트롤러
    const controller = `// backend/src/api/controllers/health.controller.ts
import { Request, Response } from 'express';
import { config } from '../../core/config';

export class HealthController {
  async getHealth(req: Request, res: Response): Promise<void> {
    const health = {
      status: 'ok',
      timestamp: new Date().toISOString(),
      version: config.app.version,
      environment: config.app.env,
      services: {
        api: 'running',
        database: 'pending',
        cache: 'pending'
      }
    };

    res.json(health);
  }

  async getReadiness(req: Request, res: Response): Promise<void> {
    // TODO: Add actual readiness checks
    res.json({ ready: true });
  }
}
`;

    await fs.writeFile('backend/src/api/controllers/health.controller.ts', controller);
    console.log(chalk.green('✓ Created: backend/src/api/controllers/health.controller.ts'));

    // 기본 라우트
    const routes = `// backend/src/api/routes/health.routes.ts
import { Router } from 'express';
import { HealthController } from '../controllers/health.controller';

const router = Router();
const healthController = new HealthController();

router.get('/health', healthController.getHealth.bind(healthController));
router.get('/ready', healthController.getReadiness.bind(healthController));

export default router;
`;

    await fs.writeFile('backend/src/api/routes/health.routes.ts', routes);
    console.log(chalk.green('✓ Created: backend/src/api/routes/health.routes.ts'));
  }

  private async createChecklist(): Promise<void> {
    const checklist = `# Phase 1: 코어 인프라 구축 체크리스트

## Task 1.1: 코어 시스템 구축
- [ ] 1.1.1 설정 관리 시스템
- [ ] 1.1.2 에러 핸들링 시스템
- [ ] 1.1.3 로깅 시스템
- [ ] 1.1.4 유틸리티 함수

## Task 1.2: 데이터 레이어 구현
- [ ] 1.2.1 DynamoDB 연결
- [ ] 1.2.2 Repository 패턴 구현
- [ ] 1.2.3 캐싱 시스템
- [ ] 1.2.4 데이터 모델 정의

## Task 1.3: API 레이어 구현
- [ ] 1.3.1 Express 서버 설정
- [ ] 1.3.2 미들웨어 구성
- [ ] 1.3.3 라우팅 시스템
- [ ] 1.3.4 입력 검증

## Task 1.4: 에이전트 시스템 기초
- [ ] 1.4.1 BaseAgent 확장
- [ ] 1.4.2 에이전트 레지스트리
- [ ] 1.4.3 메시지 시스템
- [ ] 1.4.4 오케스트레이션 기초

## Task 1.5: 통합 및 테스트
- [ ] 1.5.1 통합 테스트
- [ ] 1.5.2 API 테스트
- [ ] 1.5.3 성능 테스트
- [ ] 1.5.4 문서화

생성일: ${new Date().toISOString()}
`;

    await fs.writeFile('docs/phase1-checklist.md', checklist);
    console.log(chalk.green('✓ Created: docs/phase1-checklist.md'));
  }
}

// 실행
if (require.main === module) {
  const initializer = new Phase1Initializer();
  initializer.initialize().catch(console.error);
}

export { Phase1Initializer };