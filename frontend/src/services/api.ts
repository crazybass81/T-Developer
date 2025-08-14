const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface HealthResponse {
  status: string;
  timestamp: string;
  service: string;
}

export interface EvolutionStatus {
  ai_autonomy_level: number;
  evolution_mode: string;
  environment: string;
  phase: number;
  day: number;
  progress: number;
}

export interface AgentRequest {
  task: string;
  context?: Record<string, any>;
}

export interface AgentResponse {
  result: any;
  metadata: {
    agent: string;
    timestamp: string;
    execution_time: number;
  };
}

export interface SystemMetrics {
  avg_agent_size_kb: number;
  instantiation_speed_us: number;
  test_coverage_percent: number;
  total_agents: number;
  total_tests: number;
  memory_usage_mb: number;
  phase_stats: {
    phase1: { completed: boolean; progress: number };
    phase2: { completed: boolean; progress: number };
    phase3: { completed: boolean; progress: number };
    phase4: { completed: boolean; progress: number };
  };
}

class APIService {
  private baseURL: string;

  constructor() {
    this.baseURL = API_URL;
  }

  async health(): Promise<HealthResponse> {
    const response = await fetch(`${this.baseURL}/health`);
    if (!response.ok) throw new Error('Health check failed');
    return response.json();
  }

  async getEvolutionStatus(): Promise<EvolutionStatus> {
    const response = await fetch(`${this.baseURL}/evolution/status`);
    if (!response.ok) throw new Error('Failed to get evolution status');
    return response.json();
  }

  async executeAgent(agentName: string, request: AgentRequest): Promise<AgentResponse> {
    const response = await fetch(`${this.baseURL}/agents/${agentName}/execute`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    if (!response.ok) throw new Error(`Agent execution failed: ${response.statusText}`);
    return response.json();
  }

  async listAgents(): Promise<string[]> {
    const response = await fetch(`${this.baseURL}/agents`);
    if (!response.ok) throw new Error('Failed to list agents');
    const data = await response.json();
    return data.agents || [];
  }

  async getMetrics(): Promise<SystemMetrics> {
    const response = await fetch(`${this.baseURL}/metrics`);
    if (!response.ok) throw new Error('Failed to get metrics');
    return response.json();
  }
}

export const apiService = new APIService();
