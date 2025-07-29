import { Router } from 'express';
import { TracedAgent, TracedExternalService } from '../utils/traced-agent';

const router = Router();

router.get('/agent/:agentName', async (req, res) => {
  try {
    const { agentName } = req.params;
    const projectId = req.query.projectId as string || 'test-project';
    
    const agent = new TracedAgent(agentName);
    const result = await agent.execute(projectId, { test: true });
    
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.get('/bedrock', async (req, res) => {
  try {
    const result = await TracedExternalService.callBedrock('claude-3', 'test prompt');
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.get('/db', async (req, res) => {
  try {
    const result = await TracedExternalService.queryDynamoDB('test-table', 'test-key');
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

export default router;