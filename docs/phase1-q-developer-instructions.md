# Phase 1: 백엔드 기초 구현 - Q-Developer 작업지시서

## 📋 작업 개요
- **Phase**: 1 - 백엔드 기초 구현
- **목표**: 데이터베이스 연결, 기본 모델 정의, CRUD API 구현
- **예상 소요시간**: 16시간
- **선행조건**: Phase 0 완료

---

## 🎯 Task 1.1: 데이터베이스 설정

### 작업 지시사항

#### 1. DynamoDB 로컬 환경 설정

**docker-compose.yml** (프로젝트 루트):
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: t-developer-postgres
    environment:
      POSTGRES_DB: tdeveloper
      POSTGRES_USER: tdeveloper
      POSTGRES_PASSWORD: tdeveloper123
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./infrastructure/docker/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql

  redis:
    image: redis:7-alpine
    container_name: t-developer-redis
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

  dynamodb-local:
    image: amazon/dynamodb-local:latest
    container_name: t-developer-dynamodb
    ports:
      - "8000:8000"
    command: "-jar DynamoDBLocal.jar -sharedDb -inMemory"
    volumes:
      - "./docker/dynamodb:/home/dynamodblocal/data"

  dynamodb-admin:
    image: aaronshaf/dynamodb-admin
    container_name: t-developer-dynamodb-admin
    ports:
      - "8001:8001"
    environment:
      DYNAMO_ENDPOINT: "http://dynamodb-local:8000"
      AWS_REGION: "us-east-1"
      AWS_ACCESS_KEY_ID: "local"
      AWS_SECRET_ACCESS_KEY: "local"
    depends_on:
      - dynamodb-local

volumes:
  postgres_data:
  redis_data:
```

#### 2. Prisma ORM 설정 (PostgreSQL)

**backend/prisma/schema.prisma**:
```prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id        String   @id @default(uuid())
  email     String   @unique
  password  String
  name      String?
  role      UserRole @default(USER)
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
  
  projects  Project[]
  agents    Agent[]
  sessions  Session[]
}

model Project {
  id          String   @id @default(uuid())
  name        String
  description String?
  userId      String
  user        User     @relation(fields: [userId], references: [id])
  status      ProjectStatus @default(ACTIVE)
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt
  
  agents      Agent[]
  tasks       Task[]
}

model Agent {
  id          String   @id @default(uuid())
  name        String
  type        AgentType
  description String?
  config      Json
  projectId   String
  project     Project  @relation(fields: [projectId], references: [id])
  userId      String
  user        User     @relation(fields: [userId], references: [id])
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt
  
  tasks       Task[]
}

model Task {
  id          String   @id @default(uuid())
  title       String
  description String?
  status      TaskStatus @default(PENDING)
  priority    Int      @default(0)
  projectId   String
  project     Project  @relation(fields: [projectId], references: [id])
  agentId     String?
  agent       Agent?   @relation(fields: [agentId], references: [id])
  metadata    Json?
  result      Json?
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt
  completedAt DateTime?
}

model Session {
  id        String   @id @default(uuid())
  token     String   @unique
  userId    String
  user      User     @relation(fields: [userId], references: [id])
  expiresAt DateTime
  createdAt DateTime @default(now())
}

enum UserRole {
  ADMIN
  USER
  GUEST
}

enum ProjectStatus {
  ACTIVE
  ARCHIVED
  DELETED
}

enum AgentType {
  CODE_GENERATOR
  CODE_REVIEWER
  TEST_GENERATOR
  DOCUMENTATION
  DEPLOYMENT
  MONITORING
  SECURITY
  PERFORMANCE
  PROJECT_MANAGER
}

enum TaskStatus {
  PENDING
  IN_PROGRESS
  COMPLETED
  FAILED
  CANCELLED
}
```

#### 3. Database Service 구현

**backend/src/services/database.service.ts**:
```typescript
import { PrismaClient } from '@prisma/client';
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient } from '@aws-sdk/lib-dynamodb';
import Redis from 'ioredis';
import { logger } from '../utils/logger';
import { config } from '../config/config';

// PostgreSQL via Prisma
export const prisma = new PrismaClient({
  log: config.env === 'development' ? ['query', 'error', 'warn'] : ['error'],
});

// DynamoDB
const dynamodbClient = new DynamoDBClient({
  region: config.aws.region,
  ...(config.env === 'development' && {
    endpoint: 'http://localhost:8000',
    credentials: {
      accessKeyId: 'local',
      secretAccessKey: 'local',
    },
  }),
});

export const dynamodb = DynamoDBDocumentClient.from(dynamodbClient);

// Redis
export const redis = new Redis(config.redis.url, {
  retryStrategy: (times) => {
    const delay = Math.min(times * 50, 2000);
    return delay;
  },
});

// Database connection health check
export const checkDatabaseConnections = async (): Promise<{
  postgres: boolean;
  dynamodb: boolean;
  redis: boolean;
}> => {
  const status = {
    postgres: false,
    dynamodb: false,
    redis: false,
  };

  try {
    await prisma.$queryRaw`SELECT 1`;
    status.postgres = true;
  } catch (error) {
    logger.error('PostgreSQL connection failed:', error);
  }

  try {
    await redis.ping();
    status.redis = true;
  } catch (error) {
    logger.error('Redis connection failed:', error);
  }

  try {
    // DynamoDB health check
    const { ListTablesCommand } = await import('@aws-sdk/client-dynamodb');
    await dynamodbClient.send(new ListTablesCommand({ Limit: 1 }));
    status.dynamodb = true;
  } catch (error) {
    logger.error('DynamoDB connection failed:', error);
  }

  return status;
};

// Graceful shutdown
export const closeDatabaseConnections = async (): Promise<void> => {
  await prisma.$disconnect();
  redis.disconnect();
  logger.info('Database connections closed');
};
```

---

## 🎯 Task 1.2: 기본 모델 및 Repository 구현

### 작업 지시사항

#### 1. User Repository

**backend/src/repositories/user.repository.ts**:
```typescript
import { prisma } from '../services/database.service';
import { User, UserRole, Prisma } from '@prisma/client';
import bcrypt from 'bcryptjs';
import { AppError } from '../middlewares/errorHandler';

export class UserRepository {
  async create(data: {
    email: string;
    password: string;
    name?: string;
    role?: UserRole;
  }): Promise<User> {
    const hashedPassword = await bcrypt.hash(data.password, 10);
    
    try {
      return await prisma.user.create({
        data: {
          ...data,
          password: hashedPassword,
        },
      });
    } catch (error) {
      if (error instanceof Prisma.PrismaClientKnownRequestError) {
        if (error.code === 'P2002') {
          throw new AppError('Email already exists', 409);
        }
      }
      throw error;
    }
  }

  async findById(id: string): Promise<User | null> {
    return prisma.user.findUnique({
      where: { id },
    });
  }

  async findByEmail(email: string): Promise<User | null> {
    return prisma.user.findUnique({
      where: { email },
    });
  }

  async update(id: string, data: Partial<User>): Promise<User> {
    return prisma.user.update({
      where: { id },
      data,
    });
  }

  async delete(id: string): Promise<void> {
    await prisma.user.delete({
      where: { id },
    });
  }

  async list(params: {
    skip?: number;
    take?: number;
    where?: Prisma.UserWhereInput;
    orderBy?: Prisma.UserOrderByWithRelationInput;
  }): Promise<{ users: User[]; total: number }> {
    const { skip = 0, take = 10, where, orderBy } = params;

    const [users, total] = await Promise.all([
      prisma.user.findMany({
        skip,
        take,
        where,
        orderBy,
      }),
      prisma.user.count({ where }),
    ]);

    return { users, total };
  }

  async validatePassword(email: string, password: string): Promise<User | null> {
    const user = await this.findByEmail(email);
    if (!user) return null;

    const isValid = await bcrypt.compare(password, user.password);
    return isValid ? user : null;
  }
}

export const userRepository = new UserRepository();
```

#### 2. Project Repository

**backend/src/repositories/project.repository.ts**:
```typescript
import { prisma } from '../services/database.service';
import { Project, ProjectStatus, Prisma } from '@prisma/client';
import { dynamodb } from '../services/database.service';
import { PutCommand, GetCommand, QueryCommand } from '@aws-sdk/lib-dynamodb';

export class ProjectRepository {
  // PostgreSQL operations
  async create(data: Prisma.ProjectCreateInput): Promise<Project> {
    const project = await prisma.project.create({
      data,
      include: {
        user: true,
        agents: true,
      },
    });

    // Also store in DynamoDB for fast access
    await this.storeToDynamoDB(project);

    return project;
  }

  async findById(id: string): Promise<Project | null> {
    // Try DynamoDB first for faster access
    const dynamoResult = await this.getFromDynamoDB(id);
    if (dynamoResult) return dynamoResult;

    // Fallback to PostgreSQL
    return prisma.project.findUnique({
      where: { id },
      include: {
        user: true,
        agents: true,
        tasks: {
          take: 10,
          orderBy: { createdAt: 'desc' },
        },
      },
    });
  }

  async update(id: string, data: Prisma.ProjectUpdateInput): Promise<Project> {
    const project = await prisma.project.update({
      where: { id },
      data,
      include: {
        user: true,
        agents: true,
      },
    });

    // Update DynamoDB
    await this.storeToDynamoDB(project);

    return project;
  }

  async delete(id: string): Promise<void> {
    await prisma.project.update({
      where: { id },
      data: { status: ProjectStatus.DELETED },
    });
  }

  async listByUser(
    userId: string,
    params: {
      skip?: number;
      take?: number;
      status?: ProjectStatus;
    }
  ): Promise<{ projects: Project[]; total: number }> {
    const { skip = 0, take = 10, status } = params;

    const where: Prisma.ProjectWhereInput = {
      userId,
      ...(status && { status }),
    };

    const [projects, total] = await Promise.all([
      prisma.project.findMany({
        where,
        skip,
        take,
        orderBy: { createdAt: 'desc' },
        include: {
          agents: true,
          tasks: {
            take: 5,
            orderBy: { createdAt: 'desc' },
          },
        },
      }),
      prisma.project.count({ where }),
    ]);

    return { projects, total };
  }

  // DynamoDB operations for caching
  private async storeToDynamoDB(project: Project): Promise<void> {
    const params = {
      TableName: `${config.aws.dynamodb.tablePrefix}-projects`,
      Item: {
        id: project.id,
        userId: project.userId,
        data: JSON.stringify(project),
        ttl: Math.floor(Date.now() / 1000) + 3600, // 1 hour TTL
      },
    };

    await dynamodb.send(new PutCommand(params));
  }

  private async getFromDynamoDB(id: string): Promise<Project | null> {
    const params = {
      TableName: `${config.aws.dynamodb.tablePrefix}-projects`,
      Key: { id },
    };

    try {
      const result = await dynamodb.send(new GetCommand(params));
      return result.Item ? JSON.parse(result.Item.data) : null;
    } catch {
      return null;
    }
  }
}

export const projectRepository = new ProjectRepository();
```

---

## 🎯 Task 1.3: CRUD API 엔드포인트 구현

### 작업 지시사항

#### 1. User Controller

**backend/src/controllers/user.controller.ts**:
```typescript
import { Request, Response } from 'express';
import { userRepository } from '../repositories/user.repository';
import { asyncHandler } from '../middlewares/errorHandler';
import { validate } from '../utils/validator';
import Joi from 'joi';

const createUserSchema = Joi.object({
  email: Joi.string().email().required(),
  password: Joi.string().min(8).required(),
  name: Joi.string().optional(),
  role: Joi.string().valid('ADMIN', 'USER', 'GUEST').optional(),
});

export class UserController {
  createUser = asyncHandler(async (req: Request, res: Response) => {
    const data = validate(req.body, createUserSchema);
    const user = await userRepository.create(data);
    
    // Remove password from response
    const { password, ...userWithoutPassword } = user;
    
    res.status(201).json({
      status: 'success',
      data: userWithoutPassword,
    });
  });

  getUser = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;
    const user = await userRepository.findById(id);
    
    if (!user) {
      return res.status(404).json({
        status: 'error',
        message: 'User not found',
      });
    }
    
    const { password, ...userWithoutPassword } = user;
    
    res.json({
      status: 'success',
      data: userWithoutPassword,
    });
  });

  updateUser = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;
    const user = await userRepository.update(id, req.body);
    
    const { password, ...userWithoutPassword } = user;
    
    res.json({
      status: 'success',
      data: userWithoutPassword,
    });
  });

  deleteUser = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;
    await userRepository.delete(id);
    
    res.status(204).send();
  });

  listUsers = asyncHandler(async (req: Request, res: Response) => {
    const { page = 1, limit = 10 } = req.query;
    
    const skip = (Number(page) - 1) * Number(limit);
    const take = Number(limit);
    
    const { users, total } = await userRepository.list({
      skip,
      take,
    });
    
    // Remove passwords from response
    const usersWithoutPasswords = users.map(({ password, ...user }) => user);
    
    res.json({
      status: 'success',
      data: usersWithoutPasswords,
      meta: {
        total,
        page: Number(page),
        limit: Number(limit),
        totalPages: Math.ceil(total / Number(limit)),
      },
    });
  });
}

export const userController = new UserController();
```

#### 2. API Routes

**backend/src/api/routes/index.ts**:
```typescript
import { Router } from 'express';
import { userRoutes } from './user.routes';
import { projectRoutes } from './project.routes';
import { agentRoutes } from './agent.routes';
import { taskRoutes } from './task.routes';

const router = Router();

// Health check
router.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// API routes
router.use('/users', userRoutes);
router.use('/projects', projectRoutes);
router.use('/agents', agentRoutes);
router.use('/tasks', taskRoutes);

export const apiRouter = router;
```

**backend/src/api/routes/user.routes.ts**:
```typescript
import { Router } from 'express';
import { userController } from '../../controllers/user.controller';
import { authenticate } from '../../middlewares/auth';
import { authorize } from '../../middlewares/authorize';

const router = Router();

// Public routes
router.post('/', userController.createUser);

// Protected routes
router.use(authenticate);
router.get('/', authorize('ADMIN'), userController.listUsers);
router.get('/:id', userController.getUser);
router.put('/:id', userController.updateUser);
router.delete('/:id', authorize('ADMIN'), userController.deleteUser);

export const userRoutes = router;
```

---

## 🎯 Task 1.4: 데이터베이스 초기화 스크립트

### 작업 지시사항

#### 1. Prisma Migration

```bash
# Terminal commands
cd backend

# Install Prisma
npm install prisma @prisma/client

# Initialize Prisma
npx prisma init

# Create migration
npx prisma migrate dev --name init

# Generate Prisma Client
npx prisma generate

# Seed database (optional)
npx prisma db seed
```

#### 2. Seed Script

**backend/prisma/seed.ts**:
```typescript
import { PrismaClient, UserRole } from '@prisma/client';
import bcrypt from 'bcryptjs';

const prisma = new PrismaClient();

async function main() {
  // Create admin user
  const adminPassword = await bcrypt.hash('admin123456', 10);
  const admin = await prisma.user.upsert({
    where: { email: 'admin@t-developer.com' },
    update: {},
    create: {
      email: 'admin@t-developer.com',
      password: adminPassword,
      name: 'Admin User',
      role: UserRole.ADMIN,
    },
  });

  // Create test user
  const userPassword = await bcrypt.hash('user123456', 10);
  const user = await prisma.user.upsert({
    where: { email: 'user@t-developer.com' },
    update: {},
    create: {
      email: 'user@t-developer.com',
      password: userPassword,
      name: 'Test User',
      role: UserRole.USER,
    },
  });

  // Create sample project
  const project = await prisma.project.create({
    data: {
      name: 'Sample Project',
      description: 'A sample project for testing',
      userId: user.id,
    },
  });

  console.log({ admin, user, project });
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
```

**backend/package.json** (prisma seed 추가):
```json
{
  "prisma": {
    "seed": "ts-node prisma/seed.ts"
  }
}
```

---

## ✅ 검증 체크리스트

Phase 1 완료 후 다음 사항을 확인하세요:

- [ ] Docker 컨테이너 실행 중 (PostgreSQL, Redis, DynamoDB)
- [ ] Prisma 마이그레이션 완료
- [ ] 기본 CRUD API 동작 확인
- [ ] User 생성/조회/수정/삭제 테스트
- [ ] Project 생성/조회/수정/삭제 테스트
- [ ] 데이터베이스 연결 상태 확인 (`/api/v1/health`)

---

## 🚀 테스트 명령어

```bash
# 1. Docker 컨테이너 실행
docker-compose up -d

# 2. 데이터베이스 마이그레이션
cd backend
npx prisma migrate dev

# 3. 시드 데이터 생성
npx prisma db seed

# 4. 서버 실행
npm run dev

# 5. API 테스트
# Create user
curl -X POST http://localhost:3000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","name":"Test User"}'

# Get users
curl http://localhost:3000/api/v1/users

# Health check
curl http://localhost:3000/api/v1/health
```

---

## 📝 참고사항

- 모든 API는 `/api/v1` prefix 사용
- 에러 응답은 일관된 형식 유지
- 비밀번호는 bcrypt로 해시화
- JWT 토큰 인증은 Phase 2에서 구현
- 테스트 코드는 별도 파일로 작성