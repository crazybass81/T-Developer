import { faker } from '@faker-js/faker';
import express from 'express';
import { Server } from 'socket.io';

export class MockServiceManager {
  private mockServers: Map<string, any> = new Map();
  
  async startAll(): Promise<void> {
    await Promise.all([
      this.startBedrockMock(),
      this.startExternalAPIMocks()
    ]);
    console.log('✅ All mock services started');
  }
  
  private async startBedrockMock(): Promise<void> {
    const app = express();
    app.use(express.json());
    
    app.post('/model/anthropic.claude-*/invoke', async (req, res) => {
      const { prompt } = req.body;
      await new Promise(resolve => setTimeout(resolve, faker.number.int({ min: 500, max: 2000 })));
      
      const responses: Record<string, string> = {
        'analyze': 'Based on my analysis, this appears to be a web application project that requires user authentication, data storage, and a RESTful API.',
        'generate': 'Here\'s the generated code:\n\n```javascript\nclass ExampleService {\n  async getData() {\n    return { success: true, data: [] };\n  }\n}\n```',
        'default': faker.lorem.paragraphs(2)
      };
      
      const keyword = Object.keys(responses).find(k => prompt.toLowerCase().includes(k));
      const response = responses[keyword || 'default'];
      
      res.json({
        completion: response,
        stop_reason: 'stop_sequence',
        model: req.params[0],
        usage: {
          input_tokens: Math.floor(prompt.split(' ').length * 1.3),
          output_tokens: Math.floor(response.split(' ').length * 1.3)
        }
      });
    });
    
    const server = app.listen(4567, () => {
      console.log('🤖 Bedrock mock server running on port 4567');
    });
    
    this.mockServers.set('bedrock', server);
  }
  
  private async startExternalAPIMocks(): Promise<void> {
    const app = express();
    app.use(express.json());
    
    // NPM Registry
    app.get('/npm/:package', (req, res) => {
      res.json({
        name: req.params.package,
        version: faker.system.semver(),
        description: faker.lorem.sentence(),
        author: faker.person.fullName(),
        license: faker.helpers.arrayElement(['MIT', 'Apache-2.0', 'GPL-3.0']),
        downloads: { weekly: faker.number.int({ min: 1000, max: 1000000 }) }
      });
    });
    
    // GitHub API
    app.get('/github/repos/:owner/:repo', (req, res) => {
      res.json({
        name: req.params.repo,
        full_name: `${req.params.owner}/${req.params.repo}`,
        description: faker.lorem.sentence(),
        stargazers_count: faker.number.int({ min: 0, max: 50000 }),
        language: faker.helpers.arrayElement(['JavaScript', 'TypeScript', 'Python', 'Java'])
      });
    });
    
    const server = app.listen(4569, () => {
      console.log('🌐 External API mock server running on port 4569');
    });
    
    this.mockServers.set('external', server);
  }
  
  async stopAll(): Promise<void> {
    for (const [name, server] of this.mockServers) {
      server.close();
      console.log(`🛑 ${name} mock server stopped`);
    }
    this.mockServers.clear();
  }
}

export class WebSocketMockServer {
  private io: Server;
  
  constructor(httpServer: any) {
    this.io = new Server(httpServer, {
      cors: { origin: '*', methods: ['GET', 'POST'] }
    });
    
    this.io.on('connection', (socket) => {
      console.log('Mock WebSocket client connected');
      
      // Simulate project updates
      const projectId = `proj_${faker.string.uuid()}`;
      const statuses = ['analyzing', 'designing', 'building', 'testing', 'completed'];
      
      statuses.forEach((status, index) => {
        setTimeout(() => {
          socket.emit('project:update', {
            projectId,
            status,
            progress: (index + 1) / statuses.length * 100,
            timestamp: new Date().toISOString()
          });
        }, index * 3000);
      });
      
      socket.on('disconnect', () => {
        console.log('Mock WebSocket client disconnected');
      });
    });
  }
}

export const mockConfig = {
  enabled: process.env.USE_MOCKS === 'true',
  endpoints: {
    bedrock: 'http://localhost:4567',
    npm: 'http://localhost:4569/npm',
    github: 'http://localhost:4569/github'
  }
};