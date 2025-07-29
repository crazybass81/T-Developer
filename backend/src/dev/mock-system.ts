import { faker } from '@faker-js/faker';
import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';

export class MockServiceManager {
  private mockServers: Map<string, any> = new Map();
  
  async startAll(): Promise<void> {
    await Promise.all([
      this.startBedrockMock(),
      this.startDynamoDBMock(),
      this.startS3Mock(),
      this.startExternalAPIMocks()
    ]);
    
    console.log('✅ All mock services started');
  }
  
  private async startBedrockMock(): Promise<void> {
    const app = express();
    app.use(express.json());
    
    app.post('/model/anthropic.claude-*/invoke', async (req, res) => {
      const { prompt } = req.body;
      
      await this.simulateLatency(500, 2000);
      const response = this.generateMockLLMResponse(prompt);
      
      res.json({
        completion: response,
        stop_reason: 'stop_sequence',
        model: req.params[0],
        usage: {
          input_tokens: prompt.split(' ').length * 1.3,
          output_tokens: response.split(' ').length * 1.3
        }
      });
    });
    
    const server = app.listen(4567, () => {
      console.log('🤖 Bedrock mock server running on port 4567');
    });
    
    this.mockServers.set('bedrock', server);
  }
  
  private async startDynamoDBMock(): Promise<void> {
    const app = express();
    app.use(express.json());
    
    const tables: Map<string, any[]> = new Map();
    
    app.post('/tables/:tableName/items', (req, res) => {
      const { tableName } = req.params;
      const item = req.body.Item;
      
      if (!tables.has(tableName)) {
        tables.set(tableName, []);
      }
      
      const tableData = tables.get(tableName)!;
      const existingIndex = tableData.findIndex(i => i.id === item.id);
      
      if (existingIndex >= 0) {
        tableData[existingIndex] = item;
      } else {
        tableData.push(item);
      }
      
      res.json({ Attributes: item });
    });
    
    app.get('/tables/:tableName/items/:id', (req, res) => {
      const { tableName, id } = req.params;
      const tableData = tables.get(tableName) || [];
      const item = tableData.find(i => i.id === id);
      
      if (item) {
        res.json({ Item: item });
      } else {
        res.status(404).json({ message: 'Item not found' });
      }
    });
    
    app.post('/tables/:tableName/query', (req, res) => {
      const { tableName } = req.params;
      const tableData = tables.get(tableName) || [];
      
      res.json({
        Items: tableData,
        Count: tableData.length,
        ScannedCount: tableData.length
      });
    });
    
    const server = app.listen(8000, () => {
      console.log('🗃️  DynamoDB mock server running on port 8000');
    });
    
    this.mockServers.set('dynamodb', server);
    await this.seedDynamoDBData(tables);
  }
  
  private async startS3Mock(): Promise<void> {
    const app = express();
    app.use(express.json());
    app.use(express.raw({ type: '*/*', limit: '100mb' }));
    
    const buckets: Map<string, Map<string, any>> = new Map();
    
    app.put('/:bucket', (req, res) => {
      const { bucket } = req.params;
      
      if (!buckets.has(bucket)) {
        buckets.set(bucket, new Map());
        res.status(200).send();
      } else {
        res.status(409).json({ 
          Code: 'BucketAlreadyExists',
          Message: 'The requested bucket name is not available'
        });
      }
    });
    
    app.put('/:bucket/:key(*)', (req, res) => {
      const { bucket, key } = req.params;
      
      if (!buckets.has(bucket)) {
        return res.status(404).json({ Code: 'NoSuchBucket' });
      }
      
      const bucketData = buckets.get(bucket)!;
      bucketData.set(key, {
        Body: req.body,
        ContentType: req.headers['content-type'],
        ContentLength: req.body.length,
        ETag: `"${faker.string.alphanumeric(32)}"`,
        LastModified: new Date().toISOString()
      });
      
      res.json({ ETag: bucketData.get(key).ETag });
    });
    
    app.get('/:bucket/:key(*)', (req, res) => {
      const { bucket, key } = req.params;
      
      if (!buckets.has(bucket)) {
        return res.status(404).json({ Code: 'NoSuchBucket' });
      }
      
      const bucketData = buckets.get(bucket)!;
      const object = bucketData.get(key);
      
      if (!object) {
        return res.status(404).json({ Code: 'NoSuchKey' });
      }
      
      res.set({
        'Content-Type': object.ContentType,
        'Content-Length': object.ContentLength,
        'ETag': object.ETag,
        'Last-Modified': object.LastModified
      });
      
      res.send(object.Body);
    });
    
    const server = app.listen(4568, () => {
      console.log('☁️  S3 mock server running on port 4568');
    });
    
    this.mockServers.set('s3', server);
  }
  
  private async startExternalAPIMocks(): Promise<void> {
    const app = express();
    app.use(express.json());
    
    app.get('/npm/:package', (req, res) => {
      const packageInfo = this.generateMockNPMPackage(req.params.package);
      res.json(packageInfo);
    });
    
    app.get('/github/repos/:owner/:repo', (req, res) => {
      const repoInfo = this.generateMockGitHubRepo(req.params.owner, req.params.repo);
      res.json(repoInfo);
    });
    
    app.get('/pypi/:package', (req, res) => {
      const packageInfo = this.generateMockPyPIPackage(req.params.package);
      res.json(packageInfo);
    });
    
    const server = app.listen(4569, () => {
      console.log('🌐 External API mock server running on port 4569');
    });
    
    this.mockServers.set('external', server);
  }
  
  private generateMockLLMResponse(prompt: string): string {
    const responses: Record<string, string> = {
      'analyze': 'Based on my analysis, this appears to be a web application project that requires user authentication, data storage, and a RESTful API.',
      'generate': 'Here\'s the generated code:\n\n```javascript\nclass ExampleService {\n  async getData() {\n    return { success: true, data: [] };\n  }\n}\n```',
      'default': faker.lorem.paragraphs(2)
    };
    
    const keyword = Object.keys(responses).find(k => prompt.toLowerCase().includes(k));
    return responses[keyword || 'default'];
  }
  
  private generateMockNPMPackage(packageName: string): any {
    return {
      name: packageName,
      version: faker.system.semver(),
      description: faker.lorem.sentence(),
      keywords: faker.lorem.words(5).split(' '),
      author: faker.person.fullName(),
      license: faker.helpers.arrayElement(['MIT', 'Apache-2.0', 'GPL-3.0']),
      repository: {
        type: 'git',
        url: `https://github.com/${faker.internet.userName()}/${packageName}`
      },
      dependencies: this.generateMockDependencies(),
      downloads: {
        weekly: faker.number.int({ min: 1000, max: 1000000 })
      }
    };
  }
  
  private generateMockGitHubRepo(owner: string, repo: string): any {
    return {
      id: faker.number.int({ min: 1000000, max: 9999999 }),
      name: repo,
      full_name: `${owner}/${repo}`,
      owner: {
        login: owner,
        avatar_url: faker.image.avatar()
      },
      description: faker.lorem.sentence(),
      fork: false,
      created_at: faker.date.past().toISOString(),
      updated_at: faker.date.recent().toISOString(),
      pushed_at: faker.date.recent().toISOString(),
      stargazers_count: faker.number.int({ min: 0, max: 50000 }),
      watchers_count: faker.number.int({ min: 0, max: 5000 }),
      forks_count: faker.number.int({ min: 0, max: 10000 }),
      language: faker.helpers.arrayElement(['JavaScript', 'TypeScript', 'Python', 'Java', 'Go']),
      license: {
        key: 'mit',
        name: 'MIT License'
      }
    };
  }
  
  private generateMockPyPIPackage(packageName: string): any {
    return {
      info: {
        name: packageName,
        version: faker.system.semver(),
        summary: faker.lorem.sentence(),
        author: faker.person.fullName(),
        author_email: faker.internet.email(),
        license: faker.helpers.arrayElement(['MIT', 'Apache-2.0', 'GPL-3.0']),
        keywords: faker.lorem.words(5),
        classifiers: [
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Programming Language :: Python :: 3'
        ]
      },
      releases: this.generateMockReleases()
    };
  }
  
  private generateMockDependencies(): Record<string, string> {
    const deps: Record<string, string> = {};
    const count = faker.number.int({ min: 3, max: 10 });
    
    for (let i = 0; i < count; i++) {
      const packageName = faker.helpers.arrayElement([
        'express', 'react', 'vue', 'lodash', 'axios',
        'moment', 'uuid', 'bcrypt', 'jsonwebtoken', 'dotenv'
      ]);
      deps[packageName] = `^${faker.system.semver()}`;
    }
    
    return deps;
  }
  
  private generateMockReleases(): Record<string, any[]> {
    const releases: Record<string, any[]> = {};
    const versionCount = faker.number.int({ min: 3, max: 10 });
    
    for (let i = 0; i < versionCount; i++) {
      const version = faker.system.semver();
      releases[version] = [{
        filename: `package-${version}.tar.gz`,
        size: faker.number.int({ min: 10000, max: 1000000 }),
        upload_time: faker.date.past().toISOString()
      }];
    }
    
    return releases;
  }
  
  private async seedDynamoDBData(tables: Map<string, any[]>): Promise<void> {
    const projects = [];
    for (let i = 0; i < 20; i++) {
      projects.push({
        id: `proj_${faker.string.uuid()}`,
        name: faker.commerce.productName(),
        description: faker.lorem.paragraph(),
        status: faker.helpers.arrayElement(['analyzing', 'building', 'completed']),
        createdAt: faker.date.past().toISOString()
      });
    }
    tables.set('T-Developer-Projects', projects);
    
    const components = [];
    for (let i = 0; i < 50; i++) {
      components.push({
        id: `comp_${faker.string.uuid()}`,
        name: faker.hacker.noun(),
        version: faker.system.semver(),
        language: faker.helpers.arrayElement(['javascript', 'typescript', 'python']),
        downloads: faker.number.int({ min: 100, max: 100000 })
      });
    }
    tables.set('T-Developer-Components', components);
  }
  
  private async simulateLatency(min: number, max: number): Promise<void> {
    const delay = faker.number.int({ min, max });
    await new Promise(resolve => setTimeout(resolve, delay));
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
      cors: {
        origin: '*',
        methods: ['GET', 'POST']
      }
    });
    
    this.setupHandlers();
  }
  
  private setupHandlers(): void {
    this.io.on('connection', (socket) => {
      console.log('Mock WebSocket client connected');
      
      this.simulateProjectUpdates(socket);
      this.simulateAgentExecutions(socket);
      
      socket.on('disconnect', () => {
        console.log('Mock WebSocket client disconnected');
      });
    });
  }
  
  private simulateProjectUpdates(socket: any): void {
    const projectId = `proj_${faker.string.uuid()}`;
    const statuses = ['analyzing', 'designing', 'building', 'testing', 'completed'];
    let currentIndex = 0;
    
    const interval = setInterval(() => {
      if (currentIndex >= statuses.length) {
        clearInterval(interval);
        return;
      }
      
      socket.emit('project:update', {
        projectId,
        status: statuses[currentIndex],
        progress: (currentIndex + 1) / statuses.length * 100,
        timestamp: new Date().toISOString()
      });
      
      currentIndex++;
    }, 3000);
  }
  
  private simulateAgentExecutions(socket: any): void {
    const agents = [
      'nl-input', 'ui-selection', 'parsing', 'component-decision',
      'matching-rate', 'search', 'generation', 'assembly', 'download'
    ];
    
    agents.forEach((agent, index) => {
      setTimeout(() => {
        socket.emit('agent:start', {
          agentName: agent,
          timestamp: new Date().toISOString()
        });
        
        setTimeout(() => {
          socket.emit('agent:complete', {
            agentName: agent,
            result: 'success',
            duration: faker.number.int({ min: 1000, max: 5000 }),
            timestamp: new Date().toISOString()
          });
        }, faker.number.int({ min: 2000, max: 8000 }));
      }, index * 2000);
    });
  }
}

export const mockConfig = {
  enabled: process.env.USE_MOCKS === 'true',
  services: {
    bedrock: process.env.MOCK_BEDROCK === 'true',
    dynamodb: process.env.MOCK_DYNAMODB === 'true',
    s3: process.env.MOCK_S3 === 'true',
    external: process.env.MOCK_EXTERNAL_APIS === 'true'
  },
  endpoints: {
    bedrock: 'http://localhost:4567',
    dynamodb: 'http://localhost:8000',
    s3: 'http://localhost:4568',
    npm: 'http://localhost:4569/npm',
    github: 'http://localhost:4569/github',
    pypi: 'http://localhost:4569/pypi'
  }
};