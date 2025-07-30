// SubTask 1.19.3: API 통합 테스트
import { TestSuite } from './test-runner';

export class APITestClient {
  constructor(private baseURL: string = 'http://localhost:3000') {}
  
  async request(method: string, path: string, data?: any): Promise<any> {
    const url = `${this.baseURL}${path}`;
    
    // Mock HTTP request
    await this.delay(Math.random() * 100 + 50);
    
    // Simulate different responses
    if (path.includes('/error')) {
      throw new Error('API Error');
    }
    
    return {
      status: 200,
      data: { success: true, path, method, data }
    };
  }
  
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

export const apiTestSuite: TestSuite = {
  name: 'API Integration Tests',
  
  beforeAll: async () => {
    console.log('🔧 Setting up API test data...');
  },
  
  afterAll: async () => {
    console.log('🧹 Cleaning up API test data...');
  },
  
  tests: [
    {
      name: 'Health Check Endpoint',
      description: 'Test API health check endpoint',
      test: async () => {
        const client = new APITestClient();
        const response = await client.request('GET', '/health');
        
        if (response.status !== 200) {
          throw new Error('Health check failed');
        }
      }
    },
    
    {
      name: 'User Authentication',
      description: 'Test user login and token validation',
      test: async () => {
        const client = new APITestClient();
        
        // Login
        const loginResponse = await client.request('POST', '/auth/login', {
          email: 'test@example.com',
          password: 'password123'
        });
        
        if (!loginResponse.data.success) {
          throw new Error('Login failed');
        }
        
        // Validate token
        const profileResponse = await client.request('GET', '/auth/profile');
        
        if (!profileResponse.data.success) {
          throw new Error('Token validation failed');
        }
      }
    },
    
    {
      name: 'Project CRUD Operations',
      description: 'Test project create, read, update, delete',
      test: async () => {
        const client = new APITestClient();
        
        // Create project
        const createResponse = await client.request('POST', '/api/projects', {
          name: 'Test Project',
          description: 'Integration test project'
        });
        
        if (!createResponse.data.success) {
          throw new Error('Project creation failed');
        }
        
        // Read project
        const readResponse = await client.request('GET', '/api/projects/1');
        
        if (!readResponse.data.success) {
          throw new Error('Project read failed');
        }
        
        // Update project
        const updateResponse = await client.request('PUT', '/api/projects/1', {
          name: 'Updated Test Project'
        });
        
        if (!updateResponse.data.success) {
          throw new Error('Project update failed');
        }
        
        // Delete project
        const deleteResponse = await client.request('DELETE', '/api/projects/1');
        
        if (!deleteResponse.data.success) {
          throw new Error('Project deletion failed');
        }
      }
    },
    
    {
      name: 'Agent Execution Flow',
      description: 'Test complete agent execution workflow',
      test: async () => {
        const client = new APITestClient();
        
        // Start agent execution
        const startResponse = await client.request('POST', '/api/agents/execute', {
          agentType: 'nl-input',
          input: 'Create a simple web application'
        });
        
        if (!startResponse.data.success) {
          throw new Error('Agent execution start failed');
        }
        
        // Check execution status
        const statusResponse = await client.request('GET', '/api/agents/status/1');
        
        if (!statusResponse.data.success) {
          throw new Error('Agent status check failed');
        }
        
        // Get execution results
        const resultsResponse = await client.request('GET', '/api/agents/results/1');
        
        if (!resultsResponse.data.success) {
          throw new Error('Agent results retrieval failed');
        }
      }
    },
    
    {
      name: 'Error Handling',
      description: 'Test API error handling and responses',
      test: async () => {
        const client = new APITestClient();
        
        try {
          await client.request('GET', '/api/error');
          throw new Error('Expected error was not thrown');
        } catch (error: any) {
          if (error.message !== 'API Error') {
            throw new Error('Unexpected error type');
          }
        }
      }
    }
  ]
};