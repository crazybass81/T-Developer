const { IntelligentRouter } = require('../../backend/src/routing/intelligent-router.js');
const { LoadBalancer } = require('../../backend/src/routing/load-balancer.js');
const { PriorityQueue, PriorityManager } = require('../../backend/src/routing/priority-manager.js');

describe('Task 1.3: 태스크 라우팅 엔진', () => {
  describe('IntelligentRouter', () => {
    let router;

    beforeEach(() => {
      router = new IntelligentRouter();
    });

    test('should route task to appropriate agent', async () => {
      const task = {
        id: 'task-1',
        type: 'code',
        description: 'Implement user authentication system',
        priority: 8,
        createdAt: new Date()
      };

      const agent = await router.routeTask(task);

      expect(agent).toBeDefined();
      expect(agent.name).toBe('code-agent');
      expect(agent.capabilities).toContain('coding');
    });

    test('should handle high priority tasks', async () => {
      const task = {
        id: 'task-2',
        type: 'test',
        description: 'Critical security test',
        priority: 10,
        createdAt: new Date()
      };

      const agent = await router.routeTask(task);

      expect(agent).toBeDefined();
      expect(agent.name).toBe('test-agent');
    });

    test('should fallback to available agent when preferred is busy', async () => {
      const task = {
        id: 'task-3',
        type: 'unknown',
        description: 'General task',
        priority: 5,
        createdAt: new Date()
      };

      const agent = await router.routeTask(task);

      expect(agent).toBeDefined();
      expect(['code-agent', 'test-agent']).toContain(agent.name);
    });
  });

  describe('LoadBalancer', () => {
    let loadBalancer;

    beforeEach(() => {
      loadBalancer = new LoadBalancer('least-connections');
    });

    test('should return available agents', async () => {
      const agents = await loadBalancer.getAvailableAgents();

      expect(agents).toBeDefined();
      expect(agents.length).toBeGreaterThan(0);
      expect(agents).toContain('code-agent');
    });

    test('should update agent load', async () => {
      await loadBalancer.updateAgentLoad('code-agent', {
        currentTasks: 3,
        cpuUsage: 0.7
      });

      const stats = loadBalancer.getLoadStats();
      expect(stats['code-agent'].currentTasks).toBe(3);
      expect(stats['code-agent'].cpuUsage).toBe(0.7);
    });

    test('should use least-connections strategy', async () => {
      // Update loads to create clear preference
      await loadBalancer.updateAgentLoad('code-agent', { currentTasks: 5 });
      await loadBalancer.updateAgentLoad('test-agent', { currentTasks: 1 });

      const agents = await loadBalancer.getAvailableAgents();

      // test-agent should be first (fewer connections)
      expect(agents[0]).toBe('test-agent');
    });
  });

  describe('PriorityQueue', () => {
    let queue;

    beforeEach(() => {
      queue = new PriorityQueue();
    });

    test('should add and retrieve tasks by priority', () => {
      const highPriorityTask = {
        id: 'task-high',
        priority: 1, // CRITICAL
        createdAt: Date.now(),
        data: { type: 'critical-bug' }
      };

      const lowPriorityTask = {
        id: 'task-low',
        priority: 4, // LOW
        createdAt: Date.now(),
        data: { type: 'general' }
      };

      queue.addTask(lowPriorityTask);
      queue.addTask(highPriorityTask);

      const nextTask = queue.getNextTask();
      expect(nextTask.id).toBe('task-high');
    });

    test('should handle empty queue', () => {
      expect(queue.isEmpty()).toBe(true);
      expect(queue.getNextTask()).toBeNull();
    });

    test('should update task priority', () => {
      const task = {
        id: 'task-update',
        priority: 3, // NORMAL
        createdAt: Date.now(),
        data: { type: 'general' }
      };

      queue.addTask(task);
      const updated = queue.updatePriority('task-update', 1); // CRITICAL

      expect(updated).toBe(true);
    });
  });

  describe('PriorityManager', () => {
    let manager;

    beforeEach(() => {
      manager = new PriorityManager();
    });

    test('should add tasks to agent queues', () => {
      const task = {
        id: 'task-1',
        type: 'code',
        description: 'Test task'
      };

      manager.addTask('code-agent', task, 1); // CRITICAL

      const stats = manager.getQueueStats();
      expect(stats['code-agent']).toBe(1);
    });

    test('should retrieve next task for agent', () => {
      const task = {
        id: 'task-2',
        type: 'test',
        description: 'Test task'
      };

      manager.addTask('test-agent', task, 2); // HIGH

      const nextTask = manager.getNextTask('test-agent');
      expect(nextTask).toBeDefined();
      expect(nextTask.id).toBe('task-2');
    });

    test('should handle non-existent agent', () => {
      expect(() => {
        manager.addTask('non-existent-agent', { id: 'test' }, 3);
      }).toThrow('No queue found for agent: non-existent-agent');
    });
  });

  describe('Integration Tests', () => {
    test('should integrate router with load balancer', async () => {
      const router = new IntelligentRouter();
      const loadBalancer = new LoadBalancer('resource-based');

      // Update load to influence routing
      await loadBalancer.updateAgentLoad('code-agent', {
        currentTasks: 4,
        cpuUsage: 0.9
      });

      const task = {
        id: 'integration-task',
        type: 'code',
        description: 'Integration test task',
        priority: 7,
        createdAt: new Date()
      };

      const agent = await router.routeTask(task);
      expect(agent).toBeDefined();
    });

    test('should handle priority routing with load balancing', async () => {
      const manager = new PriorityManager();
      const loadBalancer = new LoadBalancer('least-connections');

      // Add high priority task
      manager.addTask('code-agent', {
        id: 'urgent-task',
        type: 'security',
        description: 'Security vulnerability fix'
      }, 1); // CRITICAL

      // Check if task is properly queued
      const nextTask = manager.getNextTask('code-agent');
      expect(nextTask).toBeDefined();
      expect(nextTask.id).toBe('urgent-task');

      // Verify load balancer can handle the agent
      const availableAgents = await loadBalancer.getAvailableAgents();
      expect(availableAgents).toContain('code-agent');
    });
  });
});