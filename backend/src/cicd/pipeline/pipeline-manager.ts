// SubTask 1.20.1: CI/CD Pipeline Manager
export interface PipelineStage {
  name: string;
  commands: string[];
  timeout: number;
  retries: number;
}

export interface PipelineConfig {
  name: string;
  stages: PipelineStage[];
  environment: Record<string, string>;
  notifications: string[];
}

export class PipelineManager {
  private pipelines: Map<string, PipelineConfig> = new Map();
  private executions: Map<string, PipelineExecution> = new Map();

  // Register pipeline
  register(config: PipelineConfig): void {
    this.pipelines.set(config.name, config);
  }

  // Execute pipeline
  async execute(pipelineName: string): Promise<PipelineResult> {
    const config = this.pipelines.get(pipelineName);
    if (!config) throw new Error(`Pipeline ${pipelineName} not found`);

    const executionId = `exec_${Date.now()}`;
    const execution: PipelineExecution = {
      id: executionId,
      pipeline: pipelineName,
      status: 'running',
      startTime: new Date(),
      stages: []
    };

    this.executions.set(executionId, execution);

    try {
      for (const stage of config.stages) {
        const stageResult = await this.executeStage(stage, config.environment);
        execution.stages.push(stageResult);
        
        if (!stageResult.success) {
          execution.status = 'failed';
          throw new Error(`Stage ${stage.name} failed`);
        }
      }

      execution.status = 'success';
      execution.endTime = new Date();

      return {
        executionId,
        success: true,
        duration: execution.endTime.getTime() - execution.startTime.getTime(),
        stages: execution.stages
      };

    } catch (error: any) {
      execution.status = 'failed';
      execution.endTime = new Date();
      execution.error = error.message;

      return {
        executionId,
        success: false,
        error: error.message,
        duration: execution.endTime.getTime() - execution.startTime.getTime(),
        stages: execution.stages
      };
    }
  }

  // Execute single stage
  private async executeStage(
    stage: PipelineStage, 
    env: Record<string, string>
  ): Promise<StageResult> {
    const startTime = Date.now();
    
    for (let attempt = 0; attempt <= stage.retries; attempt++) {
      try {
        const results = [];
        
        for (const command of stage.commands) {
          const result = await this.executeCommand(command, env, stage.timeout);
          results.push(result);
          
          if (!result.success) {
            throw new Error(`Command failed: ${command}`);
          }
        }

        return {
          name: stage.name,
          success: true,
          duration: Date.now() - startTime,
          attempt: attempt + 1,
          outputs: results.map(r => r.output)
        };

      } catch (error: any) {
        if (attempt === stage.retries) {
          return {
            name: stage.name,
            success: false,
            duration: Date.now() - startTime,
            attempt: attempt + 1,
            error: error.message
          };
        }
        await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
      }
    }
    
    throw new Error('All retries failed');
  }

  // Execute command with timeout
  private async executeCommand(
    command: string, 
    env: Record<string, string>,
    timeout: number
  ): Promise<CommandResult> {
    return new Promise((resolve, reject) => {
      const { spawn } = require('child_process');
      const [cmd, ...args] = command.split(' ');
      
      const childProcess = spawn(cmd, args, { env: { ...process.env, ...env } });
      let output = '';
      let error = '';

      const timer = setTimeout(() => {
        childProcess.kill();
        reject(new Error('Command timeout'));
      }, timeout);

      childProcess.stdout.on('data', (data: any) => output += data.toString());
      childProcess.stderr.on('data', (data: any) => error += data.toString());

      childProcess.on('close', (code: any) => {
        clearTimeout(timer);
        resolve({
          success: code === 0,
          output,
          error,
          exitCode: code
        });
      });
    });
  }

  // Get execution status
  getExecution(executionId: string): PipelineExecution | undefined {
    return this.executions.get(executionId);
  }

  // List all executions
  listExecutions(): PipelineExecution[] {
    return Array.from(this.executions.values());
  }
}

export interface PipelineExecution {
  id: string;
  pipeline: string;
  status: 'running' | 'success' | 'failed';
  startTime: Date;
  endTime?: Date;
  stages: StageResult[];
  error?: string;
}

export interface StageResult {
  name: string;
  success: boolean;
  duration: number;
  attempt: number;
  outputs?: string[];
  error?: string;
}

export interface CommandResult {
  success: boolean;
  output: string;
  error: string;
  exitCode: number;
}

export interface PipelineResult {
  executionId: string;
  success: boolean;
  duration: number;
  stages: StageResult[];
  error?: string;
}