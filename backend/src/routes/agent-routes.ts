import { Router } from 'express';
import { AgentOrchestrator } from '../orchestration/agent-orchestrator';
import { logger } from '../config/logger';

export function agentRoutes(orchestrator: AgentOrchestrator): Router {
  const router = Router();

  // Get all available agents
  router.get('/', async (req, res) => {
    try {
      const agents = [
        { name: 'nl-input', type: 'processing', status: 'active' },
        { name: 'ui-selection', type: 'analysis', status: 'active' },
        { name: 'parsing', type: 'analysis', status: 'active' },
        { name: 'component-decision', type: 'analysis', status: 'active' },
        { name: 'matching-rate', type: 'analysis', status: 'active' },
        { name: 'search', type: 'integration', status: 'active' },
        { name: 'generation', type: 'generation', status: 'active' },
        { name: 'assembly', type: 'integration', status: 'active' },
        { name: 'download', type: 'integration', status: 'active' }
      ];

      res.json({
        agents,
        totalCount: agents.length,
        activeCount: agents.filter(a => a.status === 'active').length
      });

    } catch (error) {
      logger.error('Failed to get agents:', error);
      res.status(500).json({
        error: 'Failed to get agents'
      });
    }
  });

  // Get agent details
  router.get('/:agentName', async (req, res) => {
    try {
      const { agentName } = req.params;
      
      const agentDetails = {
        name: agentName,
        type: 'processing',
        status: 'active',
        description: `T-Developer ${agentName} agent`,
        capabilities: ['analyze', 'process', 'generate'],
        performance: {
          averageExecutionTime: '150ms',
          successRate: '99.2%',
          totalExecutions: 1247
        },
        lastExecution: new Date().toISOString()
      };

      res.json(agentDetails);

    } catch (error) {
      logger.error('Failed to get agent details:', error);
      res.status(500).json({
        error: 'Failed to get agent details'
      });
    }
  });

  // Execute single agent (for testing)
  router.post('/:agentName/execute', async (req, res) => {
    try {
      const { agentName } = req.params;
      const { input } = req.body;

      if (!input) {
        return res.status(400).json({
          error: 'Input is required'
        });
      }

      logger.info(`Executing agent ${agentName}`, { input });

      // This would execute the specific agent
      const result = {
        success: true,
        agentName,
        executionTime: Math.random() * 1000 + 100,
        result: {
          processed: true,
          data: input,
          timestamp: new Date().toISOString()
        }
      };

      res.json(result);

    } catch (error) {
      logger.error(`Failed to execute agent ${req.params.agentName}:`, error);
      res.status(500).json({
        error: 'Failed to execute agent',
        message: error.message
      });
    }
  });

  return router;
}