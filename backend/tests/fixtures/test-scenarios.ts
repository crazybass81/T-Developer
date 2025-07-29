import { TestDataSeeder } from './seed-data';
import { TestDataGenerator } from '../helpers/test-utils';

export class TestScenarios {
  constructor(private seeder: TestDataSeeder) {}

  // 기본 시나리오: 일반적인 개발 환경
  async createBasicScenario(): Promise<void> {
    await this.seeder.seedUsers(5);
    await this.seeder.seedProjects(10);
    await this.seeder.seedComponents(20);
  }

  // 대용량 시나리오: 성능 테스트용
  async createLargeScenario(): Promise<void> {
    await this.seeder.seedUsers(100);
    await this.seeder.seedProjects(500);
    await this.seeder.seedComponents(1000);
  }

  // 최소 시나리오: 빠른 테스트용
  async createMinimalScenario(): Promise<void> {
    await this.seeder.seedUsers(2);
    await this.seeder.seedProjects(3);
    await this.seeder.seedComponents(5);
  }

  // 특정 사용자 시나리오
  createUserWithProjects(userId: string, projectCount: number = 3) {
    return Array.from({ length: projectCount }, (_, i) => 
      TestDataGenerator.project({
        userId,
        name: `User Project ${i + 1}`,
        status: i === 0 ? 'completed' : 'analyzing'
      })
    );
  }

  // 관리자 시나리오
  createAdminScenario() {
    return {
      admin: TestDataGenerator.user({
        role: 'admin',
        email: 'admin@t-developer.com'
      }),
      projects: this.createUserWithProjects('admin-user', 5)
    };
  }
}