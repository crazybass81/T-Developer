#!/usr/bin/env ts-node

import { DataService } from '../backend/src/data/services/data.service';
import { UserEntity } from '../backend/src/data/entities/user.entity';
import { ProjectEntity } from '../backend/src/data/entities/project.entity';
import { TableCreator } from '../backend/src/data/scripts/create-tables';

async function testPhase2DataLayer(): Promise<void> {
  console.log('🧪 Testing Phase 2 Data Layer Implementation...\n');
  
  try {
    // 1. Create DynamoDB table
    console.log('📊 Creating DynamoDB table...');
    const tableCreator = new TableCreator();
    await tableCreator.createMainTable();
    
    // 2. Initialize data service
    console.log('🔧 Initializing data service...');
    const dataService = new DataService();
    
    // 3. Health check
    console.log('❤️ Running health checks...');
    const health = await dataService.healthCheck();
    console.log(`   DynamoDB: ${health.dynamodb ? '✅' : '❌'}`);
    console.log(`   Redis: ${health.redis ? '✅' : '❌'}`);
    
    // 4. Test user operations
    console.log('👤 Testing user operations...');
    const user = new UserEntity('test-user-1');
    user.Email = 'test@example.com';
    user.Username = 'testuser';
    user.Role = 'developer';
    
    await dataService.users.create(user);
    console.log('   ✅ User created');
    
    const retrievedUser = await dataService.users.getById('test-user-1');
    console.log(`   ✅ User retrieved: ${retrievedUser?.Username}`);
    
    const userByEmail = await dataService.users.getByEmail('test@example.com');
    console.log(`   ✅ User found by email: ${userByEmail?.Username}`);
    
    // 5. Test project operations
    console.log('📁 Testing project operations...');
    const project = new ProjectEntity('test-project-1', 'test-user-1');
    project.ProjectName = 'Test Project';
    project.Description = 'A test project for Phase 2';
    
    await dataService.projects.create(project);
    console.log('   ✅ Project created');
    
    const userProjects = await dataService.projects.getByUser('test-user-1');
    console.log(`   ✅ User projects retrieved: ${userProjects.length} projects`);
    
    // 6. Test caching
    console.log('💾 Testing Redis cache...');
    const cache = dataService.getCache();
    
    await cache.set('test-key', { message: 'Hello Phase 2!' }, { ttl: 60 });
    const cachedValue = await cache.get('test-key');
    console.log(`   ✅ Cache test: ${JSON.stringify(cachedValue)}`);
    
    // 7. Performance test
    console.log('⚡ Running performance tests...');
    const startTime = Date.now();
    
    const promises = [];
    for (let i = 0; i < 10; i++) {
      promises.push(dataService.users.getById('test-user-1'));
    }
    
    await Promise.all(promises);
    const duration = Date.now() - startTime;
    console.log(`   ✅ 10 concurrent reads completed in ${duration}ms`);
    
    // Cleanup
    await dataService.disconnect();
    
    console.log('\n🎉 Phase 2 Data Layer Tests Completed Successfully!');
    
  } catch (error) {
    console.error('❌ Phase 2 test failed:', error);
    process.exit(1);
  }
}

// Run tests
if (require.main === module) {
  testPhase2DataLayer();
}