import { HotModuleReplacementManager, setupHMRMiddleware } from './hot-reload';
import express from 'express';

// HMR 개발 서버
export class HMRDevServer {
  private hmr: HotModuleReplacementManager;
  private app: express.Application;
  
  constructor() {
    this.app = express();
    
    this.hmr = new HotModuleReplacementManager({
      watchPaths: ['src'],
      ignorePaths: ['node_modules', 'dist', '**/*.test.ts'],
      hotReloadableExtensions: ['.ts', '.js', '.json'],
      debounceDelay: 100,
      wsPort: 3001,
      appPort: 3002
    });
    
    setupHMRMiddleware(this.app);
  }
  
  async start(): Promise<void> {
    // Start HMR
    await this.hmr.start();
    
    // Basic routes
    this.app.get('/health', (req, res) => {
      res.json({ status: 'ok', hmr: 'enabled' });
    });
    
    this.app.get('/', (req, res) => {
      res.send(`
        <!DOCTYPE html>
        <html>
        <head><title>HMR Test</title></head>
        <body>
          <h1>Hot Module Replacement Test</h1>
          <p>Edit files in src/ to see HMR in action</p>
          <div id="status">Ready</div>
        </body>
        </html>
      `);
    });
    
    // Start server
    this.app.listen(3002, () => {
      console.log('🔥 HMR Dev Server running on http://localhost:3002');
      console.log('📡 HMR WebSocket on ws://localhost:3001');
    });
  }
  
  async stop(): Promise<void> {
    await this.hmr.stop();
  }
}

// CLI usage
if (require.main === module) {
  const server = new HMRDevServer();
  
  server.start().catch(console.error);
  
  process.on('SIGINT', async () => {
    console.log('\nShutting down HMR server...');
    await server.stop();
    process.exit(0);
  });
}