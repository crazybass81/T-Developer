import { Router } from 'express';
import { v4 as uuidv4 } from 'uuid';
import { AgentOrchestrator, ProjectRequest } from '../orchestration/agent-orchestrator';
import { logger } from '../config/logger';

export function projectRoutes(orchestrator: AgentOrchestrator): Router {
  const router = Router();

  // Create new project
  router.post('/', async (req, res) => {
    try {
      const { description, requirements, existingCode, language, outputFormat } = req.body;

      if (!description) {
        return res.status(400).json({
          error: 'Project description is required'
        });
      }

      const projectRequest: ProjectRequest = {
        id: uuidv4(),
        description,
        requirements,
        existingCode,
        language,
        outputFormat,
        startTime: Date.now()
      };

      logger.info('Creating new project', { projectId: projectRequest.id });

      // Process project asynchronously
      const result = await orchestrator.processProject(projectRequest);

      res.json({
        success: true,
        project: result
      });

    } catch (error) {
      logger.error('Project creation failed:', error);
      res.status(500).json({
        error: 'Failed to create project',
        message: error.message
      });
    }
  });

  // Get project status
  router.get('/:projectId/status', async (req, res) => {
    try {
      const { projectId } = req.params;
      
      // In a real implementation, this would check project status from database
      res.json({
        projectId,
        status: 'processing',
        progress: 75,
        currentStep: 'Code Generation',
        estimatedCompletion: new Date(Date.now() + 300000).toISOString()
      });

    } catch (error) {
      logger.error('Failed to get project status:', error);
      res.status(500).json({
        error: 'Failed to get project status'
      });
    }
  });

  // Get project result
  router.get('/:projectId/result', async (req, res) => {
    try {
      const { projectId } = req.params;
      
      // In a real implementation, this would fetch from database
      res.json({
        projectId,
        status: 'completed',
        downloadUrl: `https://example.com/downloads/${projectId}.zip`,
        metadata: {
          framework: 'React',
          components: 12,
          generatedFiles: 45,
          processingTime: 120000
        }
      });

    } catch (error) {
      logger.error('Failed to get project result:', error);
      res.status(500).json({
        error: 'Failed to get project result'
      });
    }
  });

  return router;
}