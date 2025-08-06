import { spawn, ChildProcess } from 'child_process';
import chokidar from 'chokidar';
import { EventEmitter } from 'events';
import path from 'path';
import WebSocket from 'ws';

interface HMRConfig {
  watchPaths?: string[];
  ignorePaths?: string[];
  hotReloadableExtensions?: string[];
  debounceDelay?: number;
  wsPort?: number;
  appPort?: number;
}

export class HotModuleReplacementManager extends EventEmitter {
  private watcher?: chokidar.FSWatcher;
  private wsServer?: WebSocket.Server;
  private reloadTimer?: NodeJS.Timeout;
  
  constructor(private config: HMRConfig) {
    super();
  }
  
  async start(): Promise<void> {
    console.log('Starting Hot Module Replacement...');
    
    this.startWebSocketServer();
    this.startWatching();
  }
  
  private startWebSocketServer(): void {
    this.wsServer = new WebSocket.Server({ port: this.config.wsPort || 3001 });
    
    this.wsServer.on('connection', (ws) => {
      console.log('HMR client connected');
      ws.on('close', () => console.log('HMR client disconnected'));
    });
  }
  
  private startWatching(): void {
    const watchPaths = this.config.watchPaths || ['src'];
    const ignorePaths = this.config.ignorePaths || [
      'node_modules', 'dist', 'coverage', '.git', '**/*.test.ts'
    ];
    
    this.watcher = chokidar.watch(watchPaths, {
      ignored: ignorePaths,
      persistent: true,
      ignoreInitial: true,
      awaitWriteFinish: { stabilityThreshold: 300, pollInterval: 100 }
    });
    
    this.watcher.on('change', (filePath) => this.handleFileChange(filePath));
  }
  
  private handleFileChange(filePath: string): void {
    console.log(`File changed: ${filePath}`);
    
    if (this.reloadTimer) clearTimeout(this.reloadTimer);
    
    this.reloadTimer = setTimeout(() => {
      this.clearModuleCache(filePath);
      this.notifyClients('reload');
    }, this.config.debounceDelay || 100);
  }
  
  private clearModuleCache(filePath: string): void {
    try {
      const resolvedPath = require.resolve(path.resolve(filePath));
      delete require.cache[resolvedPath];
      
      Object.keys(require.cache).forEach((key) => {
        if (require.cache[key]?.children.some(child => child.id === resolvedPath)) {
          delete require.cache[key];
        }
      });
    } catch (error) {
      // File might not be in cache
    }
  }
  
  private notifyClients(action: string): void {
    if (!this.wsServer) return;
    
    const message = JSON.stringify({ action, timestamp: Date.now() });
    
    this.wsServer.clients.forEach((client) => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(message);
      }
    });
  }
  
  async stop(): Promise<void> {
    console.log('Stopping Hot Module Replacement...');
    
    if (this.watcher) await this.watcher.close();
    if (this.wsServer) this.wsServer.close();
  }
}

export const hmrClient = `
(function() {
  const ws = new WebSocket('ws://localhost:3001');
  
  ws.onopen = () => console.log('[HMR] Connected');
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.action === 'reload') {
      console.log('[HMR] Reloading page...');
      window.location.reload();
    }
  };
  
  ws.onclose = () => {
    console.log('[HMR] Disconnected. Retrying...');
    setTimeout(() => window.location.reload(), 2000);
  };
})();
`;

export function setupHMRMiddleware(app: any): void {
  if (process.env.NODE_ENV !== 'development') return;
  
  app.use((req: any, res: any, next: any) => {
    if (req.path.endsWith('.html')) {
      const originalSend = res.send;
      res.send = function(html: string) {
        if (typeof html === 'string' && html.includes('</body>')) {
          html = html.replace('</body>', `<script>${hmrClient}</script></body>`);
        }
        originalSend.call(this, html);
      };
    }
    next();
  });
}