#!/usr/bin/env ts-node

import { HotModuleReplacementManager } from '../backend/src/dev/hot-reload';
import express from 'express';
import { createServer } from 'http';
import chalk from 'chalk';

class DevServer {
  private hmr: HotModuleReplacementManager;
  private app: express.Application;
  private server: any;
  
  constructor() {
    this.app = express();
    this.server = createServer(this.app);
    
    this.hmr = new HotModuleReplacementManager({
      watchPaths: ['backend/src'],
      ignorePaths: ['node_modules', 'dist', '**/*.test.ts'],
      debounceDelay: 300,
      wsPort: 3001
    });
    
    this.setupRoutes();
    this.setupHMR();
  }
  
  private setupRoutes(): void {
    this.app.get('/health', (req, res) => {
      res.json({ 
        status: 'ok', 
        timestamp: new Date().toISOString(),
        hmr: process.env.NODE_ENV === 'development'
      });
    });
    
    this.app.get('/', (req, res) => {
      res.send(`
        <!DOCTYPE html>
        <html>
        <head>
          <title>T-Developer Dev Server</title>
        </head>
        <body>
          <h1>T-Developer Development Server</h1>
          <p>HMR is active. Edit files to see changes.</p>
          <div id="status">Ready</div>
        </body>
        </html>
      `);
    });
  }
  
  private setupHMR(): void {
    this.hmr.on('module:reload', (filePath) => {
      console.log(chalk.green(`🔄 Module reloaded: ${filePath}`));
    });
    
    // Inject HMR client into HTML responses
    this.app.use((req, res, next) => {
      if (req.path.endsWith('.html') || req.path === '/') {
        const originalSend = res.send;
        res.send = function(html: string) {
          if (typeof html === 'string' && html.includes('</body>')) {
            const hmrScript = `
              <script>
                ${require('../backend/src/dev/hot-reload').hmrClient}
              </script>
            `;
            html = html.replace('</body>', `${hmrScript}</body>`);
          }
          originalSend.call(this, html);
        };
      }
      next();
    });
  }
  
  async start(): Promise<void> {
    const port = process.env.PORT || 3000;
    
    // Start HMR
    await this.hmr.start();
    
    // Start HTTP server
    this.server.listen(port, () => {
      console.log(chalk.blue(`🚀 Dev server running on http://localhost:${port}`));
      console.log(chalk.blue(`📡 HMR WebSocket on ws://localhost:3001`));
      console.log(chalk.yellow('👀 Watching for file changes...'));
    });
    
    // Graceful shutdown
    process.on('SIGINT', async () => {
      console.log(chalk.yellow('\n🛑 Shutting down dev server...'));
      await this.hmr.stop();
      this.server.close();
      process.exit(0);
    });
  }
}

if (require.main === module) {
  const devServer = new DevServer();
  devServer.start().catch(console.error);
}

export { DevServer };