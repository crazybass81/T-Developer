import { Express } from 'express';
import { AgentOrchestrator } from '../orchestration/agent-orchestrator';
import { projectRoutes } from './project-routes';
import { agentRoutes } from './agent-routes';

export function setupRoutes(app: Express, orchestrator: AgentOrchestrator): void {
  // API prefix
  const apiPrefix = '/api/v1';

  // Project routes
  app.use(`${apiPrefix}/projects`, projectRoutes(orchestrator));
  
  // Agent routes
  app.use(`${apiPrefix}/agents`, agentRoutes(orchestrator));

  // Root API info
  app.get(apiPrefix, (req, res) => {
    res.json({
      name: 'T-Developer API',
      version: '1.0.0',
      description: 'AI-powered multi-agent development platform',
      endpoints: {
        projects: `${apiPrefix}/projects`,
        agents: `${apiPrefix}/agents`,
        health: '/health'
      }
    });
  });
}