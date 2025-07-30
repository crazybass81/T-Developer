import { RuntimeManager } from './runtime-manager';
import { RuntimeMonitor } from './runtime-monitor';

export { AgentCoreClient } from './agentcore-client';
export { RuntimeManager } from './runtime-manager';
export { AgentDeployer } from './agent-deployer';
export { RuntimeMonitor } from './runtime-monitor';

// Initialize runtime system
export async function initializeBedrockRuntime(): Promise<RuntimeManager> {
  const runtimeManager = new RuntimeManager();
  const monitor = new RuntimeMonitor();
  
  await runtimeManager.initializeRuntime();
  await monitor.startMonitoring();
  
  console.log('🚀 Bedrock AgentCore runtime system initialized');
  
  return runtimeManager;
}