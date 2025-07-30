import express from 'express';
import { env, validateEnv } from './config/env';
import { BaseOrchestrator } from './orchestration/base-orchestrator';
import { AgentRegistry } from './orchestration/agent-registry';
import { OrchestratorHealthCheck } from './monitoring/health-check';
import { ExecutionTracker } from './workflow/execution-tracker';

// Validate environment variables
validateEnv();

const app = express();
const port = env.PORT;

// Middleware
app.use(express.json());

// Initialize components
const orchestrator = new BaseOrchestrator();
const agentRegistry = new AgentRegistry();
const healthCheck = new OrchestratorHealthCheck(orchestrator);
const executionTracker = new ExecutionTracker();

// Health check
app.get('/health', async (req, res) => {
  const health = await healthCheck.checkHealth();
  res.json(health);
});

// Agent registry endpoint
app.get('/agents', (req, res) => {
  res.json({
    agents: agentRegistry.getRegisteredAgents(),
    timestamp: new Date().toISOString()
  });
});

// Task execution endpoint
app.post('/execute', async (req, res) => {
  try {
    const result = await orchestrator.routeTask(req.body);
    res.json({ success: true, result });
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Routing metrics endpoint
app.get('/metrics/routing', (req, res) => {
  const metrics = (orchestrator as any).routingMonitor?.getMetricsSummary() || {};
  res.json({
    metrics,
    timestamp: new Date().toISOString()
  });
});

// Workflow execution endpoint
app.post('/workflow/execute', async (req, res) => {
  try {
    const { name, tasks, dependencies } = req.body;
    
    const workflowDefinition = {
      id: `workflow-${Date.now()}`,
      name: name || 'Test Workflow',
      tasks: tasks || [
        {
          id: 'task1',
          name: 'First Task',
          execute: async () => ({ result: 'Task 1 completed' }),
          dependencies: [],
          type: 'processing'
        },
        {
          id: 'task2', 
          name: 'Second Task',
          execute: async () => ({ result: 'Task 2 completed' }),
          dependencies: ['task1'],
          type: 'processing'
        },
        {
          id: 'task3',
          name: 'Third Task', 
          execute: async () => ({ result: 'Task 3 completed' }),
          dependencies: ['task1'],
          type: 'processing'
        }
      ],
      dependencies: dependencies || [
        { taskId: 'task2', dependsOn: ['task1'], type: 'hard' },
        { taskId: 'task3', dependsOn: ['task1'], type: 'hard' }
      ]
    };
    
    const result = await orchestrator.executeWorkflow(workflowDefinition);
    
    res.json({
      success: true,
      workflowId: workflowDefinition.id,
      result
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Workflow status endpoint
app.get('/workflow/:workflowId/status', (req, res) => {
  try {
    const { workflowId } = req.params;
    const state = orchestrator.getWorkflowState(workflowId);
    
    res.json({
      success: true,
      workflowId,
      state
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Agno execution endpoint
app.post('/agno/execute', async (req, res) => {
  try {
    const result = await orchestrator.executeWithAgno(req.body);
    res.json({ success: true, result });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Agno metrics endpoint
app.get('/agno/metrics', async (req, res) => {
  try {
    const metrics = await orchestrator.getMetrics();
    res.json({
      success: true,
      metrics
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Multimodal processing endpoint
app.post('/multimodal/process', async (req, res) => {
  try {
    const { type, data, options } = req.body;
    
    const input = {
      type,
      data: type === 'text' ? data : Buffer.from(data, 'base64'),
      options
    };
    
    const result = await orchestrator.processMultimodal(input);
    res.json({ success: true, result });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Multimodal batch processing endpoint
app.post('/multimodal/batch', async (req, res) => {
  try {
    const { inputs } = req.body;
    
    const processedInputs = inputs.map((input: any) => ({
      type: input.type,
      data: input.type === 'text' ? input.data : Buffer.from(input.data, 'base64'),
      options: input.options
    }));
    
    const results = await orchestrator.processMultimodalBatch(processedInputs);
    res.json({ success: true, results });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// LLM processing endpoint
app.post('/llm/process', async (req, res) => {
  try {
    const { prompt, sessionId, preferredModel } = req.body;
    
    if (!prompt) {
      return res.status(400).json({ error: 'Prompt is required' });
    }
    
    const result = await orchestrator.processWithLLM(prompt, sessionId, preferredModel);
    res.json({ success: true, result });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Template-based LLM processing
app.post('/llm/template', async (req, res) => {
  try {
    const { templateId, variables, sessionId, preferredModel } = req.body;
    
    if (!templateId || !variables) {
      return res.status(400).json({ error: 'Template ID and variables are required' });
    }
    
    const result = await orchestrator.processWithTemplate(templateId, variables, sessionId, preferredModel);
    res.json({ success: true, result });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Available models list
app.get('/llm/models', (req, res) => {
  try {
    const models = orchestrator.getAvailableModels();
    res.json({ success: true, models });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Available templates list
app.get('/llm/templates', (req, res) => {
  try {
    const { category } = req.query;
    const templates = orchestrator.getAvailableTemplates(category as string);
    res.json({ success: true, templates });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Conversation context retrieval
app.get('/llm/context/:sessionId', (req, res) => {
  try {
    const { sessionId } = req.params;
    const context = orchestrator.getConversationContext(sessionId);
    res.json({ success: true, context });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Clear conversation context
app.delete('/llm/context/:sessionId', (req, res) => {
  try {
    const { sessionId } = req.params;
    orchestrator.clearConversationContext(sessionId);
    res.json({ success: true, message: 'Context cleared successfully' });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Memory management endpoints
app.post('/memory/store', (req, res) => {
  try {
    const { type, content, ttl } = req.body;
    const id = orchestrator.storeMemory(type, content, ttl);
    res.json({ success: true, id });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

app.get('/memory/:id', (req, res) => {
  try {
    const { id } = req.params;
    const memory = orchestrator.retrieveMemory(id);
    res.json({ success: true, memory });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// State management endpoints
app.post('/state/:agentId', (req, res) => {
  try {
    const { agentId } = req.params;
    const { state } = req.body;
    const snapshotId = orchestrator.saveAgentState(agentId, state);
    res.json({ success: true, snapshotId });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

app.get('/state/:agentId', (req, res) => {
  try {
    const { agentId } = req.params;
    const state = orchestrator.getAgentState(agentId);
    res.json({ success: true, state });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Session management endpoints
app.post('/session/create', (req, res) => {
  try {
    const { userId, agentId } = req.body;
    const sessionId = orchestrator.createUserSession(userId, agentId);
    res.json({ success: true, sessionId });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

app.get('/session/:sessionId', (req, res) => {
  try {
    const { sessionId } = req.params;
    const session = orchestrator.getUserSession(sessionId);
    res.json({ success: true, session });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Cache management endpoints
app.post('/cache/:key', (req, res) => {
  try {
    const { key } = req.params;
    const { value, ttl } = req.body;
    orchestrator.setCache(key, value, ttl);
    res.json({ success: true, message: 'Cache set successfully' });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

app.get('/cache/:key', (req, res) => {
  try {
    const { key } = req.params;
    const value = orchestrator.getCache(key);
    res.json({ success: true, value });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Bedrock AgentCore endpoints
app.post('/bedrock/runtime/create', (req, res) => {
  try {
    const config = req.body;
    const runtimeId = orchestrator.createAgentCoreRuntime(config);
    res.json({ success: true, runtimeId });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

app.post('/bedrock/runtime/:runtimeId/invoke', async (req, res) => {
  try {
    const { runtimeId } = req.params;
    const { inputText, sessionId } = req.body;
    
    if (!inputText) {
      return res.status(400).json({ error: 'inputText is required' });
    }
    
    const result = await orchestrator.invokeAgentCore(runtimeId, inputText, sessionId);
    res.json({ success: true, result });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

app.get('/bedrock/runtimes', (req, res) => {
  try {
    const runtimes = orchestrator.listAgentCoreRuntimes();
    res.json({ success: true, runtimes });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Start server
app.listen(port, async () => {
  await orchestrator.initialize();
  
  // Register sample agents
  await agentRegistry.register({
    name: 'code-agent',
    version: '1.0.0',
    capabilities: ['code-generation', 'refactoring'],
    maxConcurrent: 5,
    timeout: 30000
  });
  
  console.log(`🚀 T-Developer backend running on port ${port}`);
  console.log(`📋 Phase 1: Tasks 1.1-1.6 Complete`);
  console.log(`✅ BaseOrchestrator initialized`);
  console.log(`✅ AgentRegistry initialized`);
  console.log(`✅ HealthCheck system active`);
  console.log(`✅ ExecutionTracker ready`);
  console.log(`🔄 WorkflowCoordinator ready`);
  console.log(`⚡ Agno Framework ready`);
  console.log(`🎨 Multimodal Processor ready`);
  console.log(`🧠 LLM Integration ready`);
  console.log(`💾 Memory & State Management ready`);
  console.log(`🏗️ Bedrock AgentCore Runtime ready`);
  console.log(`\n🌐 Available endpoints:`);
  console.log(`   📊 Health: http://localhost:${port}/health`);
  console.log(`   🎯 Execute: http://localhost:${port}/execute`);
  console.log(`   📈 Metrics: http://localhost:${port}/metrics/routing`);
  console.log(`   🔄 Workflow: http://localhost:${port}/workflow/execute`);
  console.log(`   📋 Status: http://localhost:${port}/workflow/:id/status`);
  console.log(`   ⚡ Agno Execute: http://localhost:${port}/agno/execute`);
  console.log(`   📈 Agno Metrics: http://localhost:${port}/agno/metrics`);
  console.log(`   🎨 Multimodal: http://localhost:${port}/multimodal/process`);
  console.log(`   📦 Multimodal Batch: http://localhost:${port}/multimodal/batch`);
  console.log(`   🧠 LLM Process: http://localhost:${port}/llm/process`);
  console.log(`   📝 LLM Template: http://localhost:${port}/llm/template`);
  console.log(`   🤖 LLM Models: http://localhost:${port}/llm/models`);
  console.log(`   📋 LLM Templates: http://localhost:${port}/llm/templates`);
  console.log(`   💬 LLM Context: http://localhost:${port}/llm/context/:sessionId`);
  console.log(`   💾 Memory Store: http://localhost:${port}/memory/store`);
  console.log(`   🔍 Memory Get: http://localhost:${port}/memory/:id`);
  console.log(`   📸 State Save: http://localhost:${port}/state/:agentId`);
  console.log(`   📂 State Get: http://localhost:${port}/state/:agentId`);
  console.log(`   🎫 Session Create: http://localhost:${port}/session/create`);
  console.log(`   📋 Session Get: http://localhost:${port}/session/:sessionId`);
  console.log(`   ⚡ Cache Set: http://localhost:${port}/cache/:key`);
  console.log(`   🔍 Cache Get: http://localhost:${port}/cache/:key`);
  console.log(`   🏗️ Bedrock Runtime Create: http://localhost:${port}/bedrock/runtime/create`);
  console.log(`   🚀 Bedrock Runtime Invoke: http://localhost:${port}/bedrock/runtime/:id/invoke`);
  console.log(`   📋 Bedrock Runtimes List: http://localhost:${port}/bedrock/runtimes`);
});