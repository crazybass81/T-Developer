import { logger } from '../config/logger';

export class AgentLogger {
  static logExecution(
    agentName: string,
    projectId: string,
    input: any,
    output: any,
    duration: number,
    status: 'success' | 'failure',
    error?: Error
  ) {
    const logData = {
      agentName,
      projectId,
      duration,
      status,
      inputSize: JSON.stringify(input).length,
      outputSize: output ? JSON.stringify(output).length : 0,
      error: error?.message
    };

    if (status === 'success') {
      logger.info(`Agent ${agentName} completed successfully`, logData);
    } else {
      logger.error(`Agent ${agentName} failed`, error, logData);
    }
  }

  static logAgentStart(agentName: string, projectId: string, input: any) {
    logger.info(`Agent ${agentName} started`, {
      agentName,
      projectId,
      inputKeys: Object.keys(input || {})
    });
  }

  static logTokenUsage(agentName: string, model: string, tokensUsed: number) {
    logger.debug('Token usage recorded', {
      agentName,
      model,
      tokensUsed
    });
  }
}