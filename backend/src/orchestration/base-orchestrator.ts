import { AgentSquad } from './agent-squad';
import { agentSquadConfig } from '../config/agent-squad.config';
import { IntelligentRouter } from '../routing/intelligent-router';
import { LoadBalancer } from '../routing/load-balancer';
import { PriorityManager } from '../routing/priority-manager';
import { RoutingMonitor } from '../routing/routing-metrics';
import { WorkflowCoordinator, WorkflowDefinition } from '../workflow/workflow-coordinator';
import { AgnoManager } from '../agno/agno-manager';
import { MultimodalProcessor, MultimodalInput } from '../multimodal/multimodal-processor';
import { LLMModelManager } from '../llm/model-manager';
import { ModelRouter } from '../llm/model-router';
import { PromptTemplateManager } from '../llm/prompt-template';
import { ContextManager } from '../llm/context-manager';
import { MemoryManager } from '../memory/memory-manager';
import { StateManager } from '../memory/state-manager';
import { SessionManager } from '../memory/session-manager';
import { CacheManager } from '../memory/cache-manager';
import { RuntimeManager } from '../bedrock/runtime-manager';
import { ScalingManager } from '../bedrock/scaling-manager';
import { ResourceProvisioner } from '../bedrock/resource-provisioner';

export interface Agent {
  name: string;
  execute(task: any): Promise<any>;
}

export class BaseOrchestrator {
  private squad: AgentSquad;
  private agentRegistry: Map<string, Agent> = new Map();
  private activeSessions: Map<string, any> = new Map();
  private router: IntelligentRouter;
  private loadBalancer: LoadBalancer;
  private priorityManager: PriorityManager;
  private routingMonitor: RoutingMonitor;
  private workflowCoordinator: WorkflowCoordinator;
  private agnoManager: AgnoManager;
  private multimodalProcessor: MultimodalProcessor;
  private llmManager: LLMModelManager;
  private modelRouter: ModelRouter;
  private promptTemplateManager: PromptTemplateManager;
  private contextManager: ContextManager;
  private memoryManager: MemoryManager;
  private stateManager: StateManager;
  private sessionManager: SessionManager;
  private cacheManager: CacheManager;
  private runtimeManager: RuntimeManager;
  private scalingManager: ScalingManager;
  private resourceProvisioner: ResourceProvisioner;
  
  constructor() {
    this.squad = new AgentSquad({
      ...agentSquadConfig.orchestrator,
      storage: agentSquadConfig.storage.type
    });
    
    // 라우팅 시스템 초기화
    this.router = new IntelligentRouter();
    this.loadBalancer = new LoadBalancer('resource-based');
    this.priorityManager = new PriorityManager();
    this.routingMonitor = new RoutingMonitor();
    this.workflowCoordinator = new WorkflowCoordinator();
    this.agnoManager = new AgnoManager();
    this.multimodalProcessor = new MultimodalProcessor();
    
    // LLM 시스템 초기화
    this.llmManager = new LLMModelManager();
    this.modelRouter = new ModelRouter(this.llmManager);
    this.promptTemplateManager = new PromptTemplateManager();
    this.contextManager = new ContextManager();
    
    // 메모리 및 상태 관리 시스템 초기화
    this.memoryManager = new MemoryManager();
    this.stateManager = new StateManager();
    this.sessionManager = new SessionManager();
    this.cacheManager = new CacheManager();
    
    // Bedrock AgentCore 런타임 시스템 초기화
    this.runtimeManager = new RuntimeManager();
    this.scalingManager = new ScalingManager({
      minRuntimes: 1,
      maxRuntimes: 10,
      targetUtilization: 70,
      scaleUpThreshold: 100,
      scaleDownThreshold: 20
    });
    this.resourceProvisioner = new ResourceProvisioner();
    
    this.setupWorkflowEventHandlers();
    this.setupAgnoEventHandlers();
    this.setupMultimodalEventHandlers();
  }
  
  async initialize(): Promise<void> {
    await this.squad.initialize();
    await this.agnoManager.initialize();
    await this.registerDefaultAgents();
    console.log('✅ BaseOrchestrator initialized');
  }
  
  async registerAgent(name: string, agent: Agent): Promise<void> {
    this.agentRegistry.set(name, agent);
    await this.squad.addAgent(agent);
    console.log(`✅ Agent registered: ${name}`);
  }
  
  async routeTask(task: Record<string, any>): Promise<any> {
    const startTime = Date.now();
    
    try {
      // 지능형 라우팅으로 에이전트 선택
      const taskObj = {
        id: task.id || `task-${Date.now()}`,
        type: task.type || 'general',
        description: task.description || '',
        priority: task.priority || 3,
        createdAt: new Date()
      };
      
      const selectedAgent = await this.router.routeTask(taskObj);
      const agent = this.agentRegistry.get(selectedAgent.name);
      
      if (!agent) {
        throw new Error(`No agent found for task: ${JSON.stringify(task)}`);
      }
      
      // 라우팅 지연 시간 기록
      const routingLatency = Date.now() - startTime;
      this.routingMonitor.recordRoutingLatency(routingLatency);
      
      // 태스크 실행
      const result = await agent.execute(task);
      
      return {
        ...result,
        routing: {
          selectedAgent: selectedAgent.name,
          routingLatency,
          totalLatency: Date.now() - startTime
        }
      };
      
    } catch (error) {
      const routingLatency = Date.now() - startTime;
      this.routingMonitor.recordRoutingLatency(routingLatency);
      throw error;
    }
  }
  
  private determineAgent(task: Record<string, any>): string {
    // 간단한 태스크 라우팅 로직
    if (task.type === 'code') return 'code-agent';
    if (task.type === 'test') return 'test-agent';
    return 'default-agent';
  }
  
  private async registerDefaultAgents(): Promise<void> {
    // 기본 에이전트들 등록
    const defaultAgent: Agent = {
      name: 'default-agent',
      execute: async (task) => ({ result: 'processed', task })
    };
    
    const codeAgent: Agent = {
      name: 'code-agent',
      execute: async (task) => ({ 
        result: 'Code generated successfully', 
        task,
        generatedCode: 'function example() { return "Hello World"; }'
      })
    };
    
    const testAgent: Agent = {
      name: 'test-agent',
      execute: async (task) => ({ 
        result: 'Tests executed successfully', 
        task,
        testResults: { passed: 5, failed: 0 }
      })
    };
    
    await this.registerAgent('default-agent', defaultAgent);
    await this.registerAgent('code-agent', codeAgent);
    await this.registerAgent('test-agent', testAgent);
  }

  // 워크플로우 실행
  async executeWorkflow(definition: WorkflowDefinition): Promise<any> {
    console.log(`🔄 Executing workflow: ${definition.name}`);
    
    try {
      const result = await this.workflowCoordinator.executeWorkflow(definition);
      console.log(`✅ Workflow completed: ${definition.name}`);
      return result;
    } catch (error) {
      console.error(`❌ Workflow failed: ${definition.name}`, error);
      throw error;
    }
  }

  // 워크플로우 상태 조회
  getWorkflowState(workflowId: string): any {
    return this.workflowCoordinator.getWorkflowState(workflowId);
  }

  // 라우팅 메트릭 조회
  async getMetrics(): Promise<any> {
    return {
      routing: this.routingMonitor.getMetricsSummary(),
      agno: this.agnoManager.getMetrics(),
      llm: {
        availableModels: this.llmManager.getAvailableModels(),
        totalTemplates: this.promptTemplateManager.listTemplates().length
      },
      memory: this.memoryManager.getStats(),
      state: this.stateManager.getStats(),
      sessions: this.sessionManager.getStats(),
      cache: this.cacheManager.getStats(),
      bedrock: {
        runtimes: this.runtimeManager.getStats(),
        scaling: this.scalingManager.getRecommendations()
      }
    };
  }

  // Agno 에이전트로 태스크 실행
  async executeWithAgno(task: any): Promise<any> {
    return await this.agnoManager.executeWithAgent(task);
  }

  // 멀티모달 처리
  async processMultimodal(input: MultimodalInput): Promise<any> {
    return await this.multimodalProcessor.processSingle(input);
  }

  async processMultimodalBatch(inputs: MultimodalInput[]): Promise<any> {
    return await this.multimodalProcessor.processMultiple(inputs);
  }

  // LLM 처리
  async processWithLLM(
    prompt: string,
    sessionId?: string,
    preferredModel?: string
  ): Promise<any> {
    try {
      // 컨텍스트 관리
      if (sessionId) {
        let context = this.contextManager.getContext(sessionId);
        if (!context) {
          context = this.contextManager.createContext(sessionId);
        }
        this.contextManager.addMessage(sessionId, 'user', prompt);
      }

      // 모델 라우팅 및 실행
      const response = await this.modelRouter.route(prompt, {}, preferredModel);

      // 응답을 컨텍스트에 추가
      if (sessionId) {
        this.contextManager.addMessage(sessionId, 'assistant', response.content);
      }

      return {
        content: response.content,
        model: response.model,
        usage: response.usage,
        sessionId
      };
    } catch (error) {
      console.error('LLM processing error:', error);
      throw error;
    }
  }

  // 템플릿 기반 LLM 처리
  async processWithTemplate(
    templateId: string,
    variables: Record<string, any>,
    sessionId?: string,
    preferredModel?: string
  ): Promise<any> {
    const prompt = this.promptTemplateManager.renderTemplate(templateId, variables);
    return this.processWithLLM(prompt, sessionId, preferredModel);
  }

  // 사용 가능한 모델 목록
  getAvailableModels(): string[] {
    return this.llmManager.getAvailableModels();
  }

  // 템플릿 목록
  getAvailableTemplates(category?: string): any[] {
    return this.promptTemplateManager.listTemplates(category);
  }

  // 컨텍스트 관리
  getConversationContext(sessionId: string): any {
    return this.contextManager.getContext(sessionId);
  }

  clearConversationContext(sessionId: string): void {
    this.contextManager.clearContext(sessionId);
  }

  // 메모리 관리
  storeMemory(type: 'short_term' | 'long_term' | 'working', content: any, ttl?: number): string {
    return this.memoryManager.store({ type, content, ttl });
  }

  retrieveMemory(id: string): any {
    return this.memoryManager.retrieve(id);
  }

  searchMemories(query: string, type?: 'short_term' | 'long_term' | 'working'): any[] {
    return this.memoryManager.search(query, type);
  }

  // 상태 관리
  saveAgentState(agentId: string, state: any): string {
    return this.stateManager.saveState(agentId, state);
  }

  getAgentState(agentId: string): any {
    return this.stateManager.getState(agentId);
  }

  restoreAgentState(agentId: string, version: number): boolean {
    return this.stateManager.restoreState(agentId, version);
  }

  // 세션 관리
  createUserSession(userId?: string, agentId?: string): string {
    return this.sessionManager.createSession(userId, agentId);
  }

  getUserSession(sessionId: string): any {
    return this.sessionManager.getSession(sessionId);
  }

  setSessionData(sessionId: string, key: string, value: any): boolean {
    return this.sessionManager.setSessionData(sessionId, key, value);
  }

  getSessionData(sessionId: string, key?: string): any {
    return this.sessionManager.getSessionData(sessionId, key);
  }

  // 캐시 관리
  setCache<T>(key: string, value: T, ttl?: number): void {
    this.cacheManager.set(key, value, ttl);
  }

  getCache<T>(key: string): T | null {
    return this.cacheManager.get<T>(key);
  }

  clearCache(): void {
    this.cacheManager.clear();
  }

  // Bedrock AgentCore 런타임 관리
  createAgentCoreRuntime(config?: any): string {
    return this.runtimeManager.createRuntime(config);
  }

  async invokeAgentCore(
    runtimeId: string,
    inputText: string,
    sessionId?: string
  ): Promise<any> {
    return await this.runtimeManager.invokeAgent(runtimeId, inputText, sessionId);
  }

  listAgentCoreRuntimes(): any[] {
    return this.runtimeManager.listRuntimes();
  }

  removeAgentCoreRuntime(runtimeId: string): boolean {
    return this.runtimeManager.removeRuntime(runtimeId);
  }

  // 리소스 프로비저닝
  async provisionAgent(config: any): Promise<any> {
    return await this.resourceProvisioner.provisionAgent(config);
  }

  async checkAgentStatus(agentId: string): Promise<string> {
    return await this.resourceProvisioner.checkAgentStatus(agentId);
  }

  // 스케일링 관리
  recordScalingMetrics(metrics: any): void {
    this.scalingManager.recordMetrics(metrics);
  }

  getScalingRecommendations(): string[] {
    return this.scalingManager.getRecommendations();
  }

  private setupWorkflowEventHandlers(): void {
    this.workflowCoordinator.on('taskStarted', (taskId) => {
      console.log(`📋 Task started: ${taskId}`);
    });

    this.workflowCoordinator.on('taskCompleted', (taskId, result) => {
      console.log(`✅ Task completed: ${taskId}`);
    });

    this.workflowCoordinator.on('taskFailed', (taskId, error) => {
      console.log(`❌ Task failed: ${taskId} - ${error.message}`);
    });

    this.workflowCoordinator.on('workflowStateChanged', (event) => {
      console.log(`🔄 Workflow state changed: ${event.workflowId}`);
    });
  }

  private setupAgnoEventHandlers(): void {
    this.agnoManager.on('initialized', (event) => {
      console.log('⚡ Agno Framework ready:', event.benchmark);
    });
  }

  private setupMultimodalEventHandlers(): void {
    this.multimodalProcessor.on('processed', (event) => {
      console.log(`🎨 ${event.type} processed in ${event.processingTime.toFixed(2)}ms`);
    });

    this.multimodalProcessor.on('batchProcessed', (event) => {
      console.log(`📦 Batch processed: ${event.count} items in ${event.totalTime.toFixed(2)}ms`);
    });
  }
}