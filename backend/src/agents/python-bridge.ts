/**
 * Python-TypeScript Bridge
 * Python 에이전트를 TypeScript에서 호출하기 위한 브릿지
 */

import { spawn, ChildProcess } from 'child_process';
import path from 'path';
import { EventEmitter } from 'events';

export interface PythonAgentResult {
  success: boolean;
  data?: any;
  error?: string;
  executionTime?: number;
}

export class PythonAgentBridge extends EventEmitter {
  private pythonPath: string;
  private agentBasePath: string;

  constructor() {
    super();
    this.pythonPath = process.env.PYTHON_PATH || 'python3';
    this.agentBasePath = path.join(__dirname, 'implementations');
  }

  /**
   * Python 에이전트 실행
   */
  async executeAgent(
    agentName: string,
    agentMethod: string,
    input: any
  ): Promise<PythonAgentResult> {
    const startTime = Date.now();
    
    return new Promise((resolve, reject) => {
      const scriptPath = path.join(this.agentBasePath, agentName, `${agentName}.py`);
      
      // Python 스크립트 실행
      const pythonProcess: ChildProcess = spawn(this.pythonPath, [
        '-m',
        `backend.src.agents.implementations.${agentName}.${agentName}`,
        '--method', agentMethod,
        '--input', JSON.stringify(input)
      ], {
        cwd: '/home/ec2-user/T-DeveloperMVP',
        env: { ...process.env, PYTHONPATH: '/home/ec2-user/T-DeveloperMVP' }
      });

      let outputData = '';
      let errorData = '';

      pythonProcess.stdout?.on('data', (data) => {
        outputData += data.toString();
        this.emit('progress', { agent: agentName, data: data.toString() });
      });

      pythonProcess.stderr?.on('data', (data) => {
        errorData += data.toString();
        console.error(`Python Agent Error (${agentName}):`, data.toString());
      });

      pythonProcess.on('close', (code) => {
        const executionTime = Date.now() - startTime;
        
        if (code !== 0) {
          resolve({
            success: false,
            error: errorData || `Process exited with code ${code}`,
            executionTime
          });
        } else {
          try {
            const result = JSON.parse(outputData);
            resolve({
              success: true,
              data: result,
              executionTime
            });
          } catch (e) {
            resolve({
              success: false,
              error: `Failed to parse output: ${outputData}`,
              executionTime
            });
          }
        }
      });

      pythonProcess.on('error', (err) => {
        reject({
          success: false,
          error: err.message,
          executionTime: Date.now() - startTime
        });
      });
    });
  }

  /**
   * NL Input Agent 실행
   */
  async executeNLInputAgent(query: string, framework?: string) {
    return this.executeAgent('nl_input', 'process', { query, framework });
  }

  /**
   * UI Selection Agent 실행
   */
  async executeUISelectionAgent(requirements: any) {
    return this.executeAgent('ui_selection', 'select', { requirements });
  }

  /**
   * Parser Agent 실행
   */
  async executeParserAgent(input: any) {
    return this.executeAgent('parser', 'parse', { input });
  }

  /**
   * Match Rate Agent 실행
   */
  async executeMatchRateAgent(components: any) {
    return this.executeAgent('match_rate', 'calculate', { components });
  }

  /**
   * Generation Agent 실행 - 실제 코드 생성
   */
  async executeGenerationAgent(specifications: any) {
    return this.executeAgent('generation', 'generate', { specifications });
  }

  /**
   * Assembly Agent 실행 - 프로젝트 조립
   */
  async executeAssemblyAgent(generatedCode: any) {
    return this.executeAgent('assembly', 'assemble', { generatedCode });
  }

  /**
   * Download Agent 실행 - ZIP 파일 생성
   */
  async executeDownloadAgent(project: any) {
    return this.executeAgent('download', 'package', { project });
  }
}

// 싱글톤 인스턴스
export const pythonBridge = new PythonAgentBridge();