import { AgentRegistry } from '../../src/orchestration/agent-registry';

// Mock AWS SDK
jest.mock('@aws-sdk/client-dynamodb');
jest.mock('@aws-sdk/util-dynamodb');

describe('AgentRegistry', () => {
  let registry: AgentRegistry;

  beforeEach(() => {
    registry = new AgentRegistry('test-table');
  });

  describe('register', () => {
    it('should register an agent successfully', async () => {
      const metadata = {
        name: 'test-agent',
        version: '1.0.0',
        capabilities: ['test'],
        maxConcurrent: 1,
        timeout: 5000
      };

      await expect(registry.register(metadata)).resolves.not.toThrow();
      
      const agents = await registry.listAgents();
      expect(agents).toHaveLength(1);
      expect(agents[0].name).toBe('test-agent');
    });
  });

  describe('getAgent', () => {
    it('should throw error for non-existent agent', async () => {
      await expect(registry.getAgent('non-existent')).rejects.toThrow('Agent non-existent not found');
    });
  });

  describe('listAgents', () => {
    it('should return empty array initially', async () => {
      const agents = await registry.listAgents();
      expect(agents).toEqual([]);
    });
  });

  describe('getAgentStatus', () => {
    it('should return null for non-existent agent', () => {
      const status = registry.getAgentStatus('non-existent');
      expect(status).toBeNull();
    });
  });

  describe('unregister', () => {
    it('should remove agent from registry', async () => {
      const metadata = {
        name: 'test-agent',
        version: '1.0.0',
        capabilities: ['test'],
        maxConcurrent: 1,
        timeout: 5000
      };

      await registry.register(metadata);
      await registry.unregister('test-agent');
      
      const agents = await registry.listAgents();
      expect(agents).toHaveLength(0);
    });
  });
});