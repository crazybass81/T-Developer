#!/usr/bin/env ts-node

import { createTable } from '../backend/src/data/scripts/create-table';
import { DataService } from '../backend/src/data/services/data-service';

async function testTask21(): Promise<void> {
  console.log('🧪 Testing Task 2.1: DynamoDB Table Design\n');
  
  try {
    // 1. Create table
    console.log('📊 Creating DynamoDB table...');
    await createTable();
    
    // 2. Initialize data service
    console.log('🔧 Initializing data service...');
    const dataService = new DataService();
    
    // 3. Test user operations
    console.log('👤 Testing user operations...');
    await dataService.createUser('user1', 'test@example.com', 'testuser');
    const user = await dataService.getUser('user1');
    console.log(`   ✅ User created and retrieved: ${user?.Username}`);
    
    // 4. Test project operations
    console.log('📁 Testing project operations...');
    await dataService.createProject('proj1', 'user1', 'Test Project');
    const project = await dataService.getProject('proj1');
    console.log(`   ✅ Project created: ${project?.ProjectName}`);
    
    const userProjects = await dataService.getUserProjects('user1');
    console.log(`   ✅ User projects retrieved: ${userProjects.length} projects`);
    
    // 5. Test agent operations
    console.log('🤖 Testing agent operations...');
    await dataService.createAgent('agent1', 'proj1', 'nl-input');
    const agents = await dataService.getProjectAgents('proj1');
    console.log(`   ✅ Agent created: ${agents.length} agents in project`);
    
    console.log('\n🎉 Task 2.1 Tests Completed Successfully!');
    
  } catch (error) {
    console.error('❌ Task 2.1 test failed:', error);
    process.exit(1);
  }
}

if (require.main === module) {
  testTask21();
}