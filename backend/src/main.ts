// T-Developer Main Entry Point - Agno + Agent Squad Architecture
import express from 'express';
import { UnifiedAgentSystem } from './orchestration/unified-agent-system';
import { BedrockAgentCoreIntegration } from './bedrock/agentcore-integration';

const app = express();
app.use(express.json());

// Initialize AI Multi-Agent System
const agentSystem = new UnifiedAgentSystem();
const agentCore = new BedrockAgentCoreIntegration();

// Health check
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy',
    architecture: 'Agno + Agent Squad + Bedrock AgentCore',
    agents: 9
  });
});

// Main agent processing endpoint
app.post('/api/process', async (req, res) => {
  try {
    const result = await agentSystem.processRequest(req.body);
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 T-Developer running on port ${PORT}`);
  console.log('📋 Architecture: Agno Framework + AWS Agent Squad + Bedrock AgentCore');
});