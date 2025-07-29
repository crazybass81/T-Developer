import { TestServer, TestClient } from './test-server';
import { AuthTestHelpers } from './auth-helpers';
import { DatabaseTestHelpers } from './database-helpers';
import app from '../../src/app';

export class IntegrationTestSetup {
  private testServer: TestServer;
  private testClient: TestClient;
  private authHelpers: AuthTestHelpers;
  private port: number = 0;

  constructor() {
    this.testServer = new TestServer();
    this.authHelpers = new AuthTestHelpers();
  }

  async setup(): Promise<void> {
    // Setup database mocks
    DatabaseTestHelpers.setupMocks();
    
    // Mount the actual app routes
    this.testServer.getApp().use(app);
    
    // Start test server
    this.port = await this.testServer.start();
    this.testClient = new TestClient(this.testServer.getUrl(this.port));
  }

  async teardown(): Promise<void> {
    await this.testServer.stop();
  }

  getClient(): TestClient {
    return this.testClient;
  }

  getAuthHelpers(): AuthTestHelpers {
    return this.authHelpers;
  }

  async createAuthenticatedClient(userOverrides?: any): Promise<{
    client: TestClient;
    user: any;
    token: string;
  }> {
    const tokens = await this.authHelpers.generateTestTokens(userOverrides);
    const headers = this.authHelpers.createAuthHeaders(tokens.accessToken);
    
    // Create client with auth headers
    const authenticatedClient = new TestClient(this.testServer.getUrl(this.port));
    
    return {
      client: authenticatedClient,
      user: userOverrides || { id: 'test-user', email: 'test@example.com', role: 'user' },
      token: tokens.accessToken
    };
  }
}