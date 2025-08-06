import { EventEmitter } from 'events';
import { AgentSquad } from '../lib/agent-squad';
import { agentSquadConfig } from '../config/agent-squad.config';

interface Agent {
  id: string;
  name: string;
  type: string;
  status: 'idle' | 'busy' | 'error';
  execute(task: any): Promise<any>;
}

interface Task {
  id: string;
  type: string;
  data: any;
  priority: number;
  timeout?: number;
}

interface Session {
  id: string;
  userId: string;
  createdAt: Date;
  lastActivity: Date;
  context: Record<string, any>;
}

export class BaseOrchestrator extends EventEmitter {
  private squad: AgentSquad;
  private agentRegistry: Map<string, Agent> = new Map();
  private activeSessions: Map<string, Session> = new Map();
  private taskQueue: Task[] = [];
  private isInitialized = false;

  constructor() {
    super();
    this.squad = new AgentSquad(agentSquadConfig);
  }

  async initialize(): Promise<void> {
    if (this.isInitialized) return;

    await this.squad.initialize();
    await this.registerDefaultAgents();
    
    this.isInitialized = true;
    this.emit('initialized');
  }

  async registerAgent(name: string, agent: Agent): Promise<void> {
    this.agentRegistry.set(name, agent);
    await this.squad.addAgent(agent);
    this.emit('agentRegistered', { name, agent });
  }

  async routeTask(task: Task): Promise<any> {
    const agentName = this.determineAgent(task);
    const agent = this.agentRegistry.get(agentName);
    
    if (!agent) {
      throw new Error(`No agent found for task: ${task.type}`);
    }

    agent.status = 'busy';
    try {
      const result = await agent.execute(task);
      agent.status = 'idle';
      return result;
    } catch (error) {
      agent.status = 'error';
      throw error;
    }
  }

  private determineAgent(task: Task): string {
    // Simple routing logic based on task type
    const routingMap: Record<string, string> = {
      'nl-input': 'NLInputAgent',
      'ui-selection': 'UISelectionAgent',
      'parser': 'ParserAgent',
      'component-decision': 'ComponentDecisionAgent',
      'match-rate': 'MatchRateAgent',
      'search': 'SearchAgent',
      'generation': 'GenerationAgent',
      'assembly': 'AssemblyAgent',
      'download': 'DownloadAgent'
    };

    return routingMap[task.type] || 'DefaultAgent';
  }

  private async registerDefaultAgents(): Promise<void> {
    // Register placeholder agents for now
    const defaultAgents = [
      'NLInputAgent',
      'UISelectionAgent', 
      'ParserAgent',
      'ComponentDecisionAgent',
      'MatchRateAgent',
      'SearchAgent',
      'GenerationAgent',
      'AssemblyAgent',
      'DownloadAgent'
    ];

    for (const agentName of defaultAgents) {
      const mockAgent: Agent = {
        id: `${agentName.toLowerCase()}-001`,
        name: agentName,
        type: agentName.toLowerCase().replace('agent', ''),
        status: 'idle',
        execute: async (task: any) => {
          return { status: 'completed', result: `Mock result from ${agentName}` };
        }
      };

      await this.registerAgent(agentName, mockAgent);
    }
  }

  async createSession(userId: string): Promise<string> {
    const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const session: Session = {
      id: sessionId,
      userId,
      createdAt: new Date(),
      lastActivity: new Date(),
      context: {}
    };

    this.activeSessions.set(sessionId, session);
    return sessionId;
  }

  getActiveAgents(): Agent[] {
    return Array.from(this.agentRegistry.values());
  }

  getSessionCount(): number {
    return this.activeSessions.size;
  }

  async shutdown(): Promise<void> {
    this.emit('shutdown');
    await this.squad.shutdown();
    this.agentRegistry.clear();
    this.activeSessions.clear();
  }
}