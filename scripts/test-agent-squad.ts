#!/usr/bin/env ts-node

import { TDeveloperSquadFactory, SquadAgentAdapter } from '../backend/src/integrations/agent-squad';
import { initializeAgentFramework } from '../backend/src/agents/framework';
import { v4 as uuidv4 } from 'uuid';

async function testAgentSquad() {
  console.log('👥 Testing Agent Squad Integration...\n');
  
  try {
    // Setup T-Developer squad
    console.log('🔧 Setting up T-Developer squad...');
    const supervisor = await TDeveloperSquadFactory.setupSquad();
    
    // Show initial squad status
    console.log('\n📊 Initial Squad Status:');
    console.table(supervisor.getSquadStatus());
    
    // Create tasks to distribute
    const tasks = [
      {
        type: 'nl-processing',
        capability: 'natural_language_processing',
        payload: {
          text: 'Build a task management app with user authentication'
        }
      },
      {
        type: 'ui-selection',
        capability: 'ui_framework_selection',
        payload: {
          project_type: 'web_application',
          target_platforms: ['web']
        }
      },
      {
        type: 'component-search',
        capability: 'component_discovery',
        payload: {
          requirements: ['authentication', 'task-list', 'dashboard']
        }
      }
    ];
    
    console.log('\n📤 Distributing tasks to squad...');
    
    // Distribute tasks and collect results
    const results = [];
    
    for (const taskData of tasks) {
      const task = {
        id: uuidv4(),
        type: taskData.type,
        capability: taskData.capability,
        payload: taskData.payload
      };
      
      console.log(`  - Distributing ${task.type} task...`);
      
      try {
        await supervisor.distributeTask(task);
        results.push({ taskId: task.id, status: 'distributed' });
      } catch (error) {
        results.push({ 
          taskId: task.id, 
          status: 'failed', 
          error: error instanceof Error ? error.message : 'Unknown error'
        });
      }
    }
    
    // Wait for tasks to complete
    console.log('\n⏳ Waiting for tasks to complete...');
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Show final squad status
    console.log('\n📊 Final Squad Status:');
    const finalStatus = supervisor.getSquadStatus();
    console.table(finalStatus);
    
    // Test integration with T-Developer framework
    console.log('\n🔗 Testing framework integration...');
    
    const { manager } = initializeAgentFramework();
    
    // Create squad adapter
    const squadAdapter = new SquadAgentAdapter(supervisor);
    
    // Register adapter with framework
    manager.registerAgentType('squad-adapter', () => squadAdapter);
    const adapterId = await manager.createAgent('squad-adapter');
    
    await manager.startAgent(adapterId, {
      projectId: 'test-project',
      userId: 'test-user',
      sessionId: 'test-session',
      metadata: { integration_test: true }
    });
    
    // Test orchestration through adapter
    const orchestrationMessage = {
      id: uuidv4(),
      type: 'request' as const,
      source: 'test-client',
      target: adapterId,
      payload: {
        action: 'orchestrate_tasks',
        tasks: [
          {
            type: 'nl-processing',
            capability: 'natural_language_processing',
            payload: { text: 'Create a blog platform' }
          }
        ]
      },
      timestamp: new Date()
    };
    
    const orchestrationResponse = await manager.sendMessage(adapterId, orchestrationMessage);
    console.log('📥 Orchestration Response:', orchestrationResponse.payload);
    
    // Cleanup
    await manager.stopAgent(adapterId);
    
    console.log('\n✅ Agent Squad integration test completed!');
    
  } catch (error) {
    console.error('❌ Agent Squad test failed:', error);
    
    console.log('\n💡 Agent Squad Features:');
    console.log('- Supervisor-worker pattern');
    console.log('- Task distribution and load balancing');
    console.log('- Error handling and recovery');
    console.log('- Integration with T-Developer framework');
  }
}

if (require.main === module) {
  testAgentSquad().catch(console.error);
}