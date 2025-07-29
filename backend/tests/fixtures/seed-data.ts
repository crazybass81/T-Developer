import { DynamoDBDocumentClient, PutCommand, BatchWriteCommand } from '@aws-sdk/lib-dynamodb';
import { faker } from '@faker-js/faker';

export class TestDataSeeder {
  constructor(private docClient: DynamoDBDocumentClient) {}
  
  async seedAll(): Promise<void> {
    await Promise.all([
      this.seedUsers(),
      this.seedProjects(),
      this.seedComponents()
    ]);
  }
  
  async seedUsers(count: number = 10): Promise<void> {
    const users = Array.from({ length: count }, () => ({
      id: `user_${faker.string.uuid()}`,
      email: faker.internet.email(),
      name: faker.person.fullName(),
      role: faker.helpers.arrayElement(['user', 'admin']),
      apiKey: `sk_test_${faker.string.alphanumeric(32)}`,
      createdAt: faker.date.past().toISOString()
    }));
    
    for (const user of users) {
      await this.docClient.send(new PutCommand({
        TableName: 'test-users',
        Item: user
      }));
    }
    
    console.log(`✅ Seeded ${count} test users`);
  }
  
  async seedProjects(count: number = 20): Promise<void> {
    const projects = Array.from({ length: count }, () => ({
      id: `proj_${faker.string.uuid()}`,
      userId: `user_${faker.string.uuid()}`,
      name: faker.commerce.productName(),
      description: faker.lorem.paragraph(),
      projectType: faker.helpers.arrayElement(['web', 'api', 'mobile']),
      status: faker.helpers.arrayElement(['analyzing', 'building', 'completed']),
      uiFramework: faker.helpers.arrayElement(['react', 'vue', 'angular']),
      createdAt: faker.date.past().toISOString()
    }));
    
    // 배치 쓰기 (25개씩)
    const chunks = this.chunkArray(projects, 25);
    
    for (const chunk of chunks) {
      await this.docClient.send(new BatchWriteCommand({
        RequestItems: {
          'test-projects': chunk.map(item => ({
            PutRequest: { Item: item }
          }))
        }
      }));
    }
    
    console.log(`✅ Seeded ${count} test projects`);
  }
  
  async seedComponents(count: number = 50): Promise<void> {
    const components = Array.from({ length: count }, () => ({
      id: `comp_${faker.string.uuid()}`,
      name: faker.hacker.noun(),
      version: faker.system.semver(),
      language: faker.helpers.arrayElement(['javascript', 'typescript', 'python']),
      framework: faker.helpers.arrayElement(['react', 'express', 'fastapi']),
      description: faker.lorem.sentence(),
      downloads: faker.number.int({ min: 0, max: 1000000 }),
      stars: faker.number.int({ min: 0, max: 50000 }),
      lastUpdated: faker.date.recent().toISOString()
    }));
    
    const chunks = this.chunkArray(components, 25);
    
    for (const chunk of chunks) {
      await this.docClient.send(new BatchWriteCommand({
        RequestItems: {
          'test-components': chunk.map(item => ({
            PutRequest: { Item: item }
          }))
        }
      }));
    }
    
    console.log(`✅ Seeded ${count} test components`);
  }
  
  private chunkArray<T>(array: T[], size: number): T[][] {
    const chunks: T[][] = [];
    for (let i = 0; i < array.length; i += size) {
      chunks.push(array.slice(i, i + size));
    }
    return chunks;
  }
}