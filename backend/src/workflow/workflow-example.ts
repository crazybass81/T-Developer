import { ExecutionTracker } from './execution-tracker';
import { WebSocket } from 'ws';

// Example usage of ExecutionTracker in a workflow system
export class WorkflowExecutor {
  private tracker = new ExecutionTracker();

  async executeWorkflow(workflowId: string, workflow: any, ws?: WebSocket): Promise<void> {
    // Setup WebSocket connection for real-time updates
    if (ws) {
      this.tracker.addWebSocketConnection(workflowId, ws);
    }

    try {
      // Start tracking
      await this.tracker.trackExecution(workflowId, workflow);

      // Simulate workflow execution
      for (let i = 0; i < workflow.steps.length; i++) {
        const step = workflow.steps[i];
        const progress = ((i + 1) / workflow.steps.length) * 100;

        // Update progress
        await this.tracker.updateStepProgress(workflowId, step.id, progress);

        // Simulate step execution time
        await new Promise(resolve => setTimeout(resolve, 1000));
      }

      // Complete execution
      await this.tracker.completeExecution(workflowId, { 
        message: 'Workflow completed successfully' 
      });

    } catch (error) {
      // Handle failure
      await this.tracker.failExecution(workflowId, error as Error);
      throw error;
    }
  }

  getExecutionStatus(workflowId: string) {
    return this.tracker.getExecutionState(workflowId);
  }
}

// Example WebSocket server integration
export function setupWebSocketServer(port: number = 8080) {
  const WebSocketServer = require('ws').Server;
  const wss = new WebSocketServer({ port });
  const executor = new WorkflowExecutor();

  wss.on('connection', (ws: WebSocket) => {
    ws.on('message', async (message: string) => {
      try {
        const { action, workflowId, workflow } = JSON.parse(message);
        
        if (action === 'execute') {
          await executor.executeWorkflow(workflowId, workflow, ws);
        } else if (action === 'status') {
          const status = executor.getExecutionStatus(workflowId);
          ws.send(JSON.stringify({ type: 'status', data: status }));
        }
      } catch (error) {
        ws.send(JSON.stringify({ 
          type: 'error', 
          message: (error as Error).message 
        }));
      }
    });
  });

  console.log(`WebSocket server running on port ${port}`);
  return wss;
}