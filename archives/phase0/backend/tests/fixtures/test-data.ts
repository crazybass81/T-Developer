export const testProjects = [
  {
    id: 'proj_test_001',
    userId: 'user_test_123',
    name: 'E-commerce Platform',
    description: 'Modern e-commerce platform with React and Node.js',
    status: 'completed',
    createdAt: '2024-01-01T00:00:00.000Z'
  },
  {
    id: 'proj_test_002', 
    userId: 'user_test_456',
    name: 'Blog System',
    description: 'Simple blog system with authentication',
    status: 'analyzing',
    createdAt: '2024-01-02T00:00:00.000Z'
  }
];

export const testUsers = [
  {
    id: 'user_test_123',
    email: 'test1@example.com',
    role: 'user',
    createdAt: '2024-01-01T00:00:00.000Z'
  },
  {
    id: 'user_test_456',
    email: 'test2@example.com', 
    role: 'admin',
    createdAt: '2024-01-01T00:00:00.000Z'
  }
];

export const testAgentExecutions = [
  {
    id: 'exec_test_001',
    projectId: 'proj_test_001',
    agentName: 'NL Input Agent',
    agentType: 'nl_input',
    status: 'completed',
    startedAt: '2024-01-01T01:00:00.000Z',
    completedAt: '2024-01-01T01:05:00.000Z'
  }
];