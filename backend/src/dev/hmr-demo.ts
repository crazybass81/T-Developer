import express from 'express';
import { HotModuleReplacementManager, setupHMRMiddleware } from './hot-reload';

const app = express();
const port = 3002;

// Setup HMR middleware
setupHMRMiddleware(app);

// Basic routes
app.get('/', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>HMR Demo</title>
      <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .connected { background: #d4edda; color: #155724; }
        .disconnected { background: #f8d7da; color: #721c24; }
      </style>
    </head>
    <body>
      <h1>Hot Module Replacement Demo</h1>
      <div id="status" class="status disconnected">Connecting to HMR...</div>
      <p>Edit any file in the src directory to see HMR in action!</p>
      <p>Current time: ${new Date().toLocaleTimeString()}</p>
    </body>
    </html>
  `);
});

app.get('/api/test', (req, res) => {
  res.json({ 
    message: 'HMR Test API',
    timestamp: new Date().toISOString(),
    version: '1.0.0'
  });
});

// Start HMR if in development
if (process.env.NODE_ENV === 'development') {
  const hmr = new HotModuleReplacementManager({
    watchPaths: ['src'],
    ignorePaths: ['node_modules', 'dist', '**/*.test.ts'],
    debounceDelay: 100,
    wsPort: 3001
  });
  
  hmr.start().then(() => {
    console.log('🔥 HMR started on port 3001');
  });
  
  // Graceful shutdown
  process.on('SIGTERM', () => hmr.stop());
  process.on('SIGINT', () => hmr.stop());
}

app.listen(port, () => {
  console.log(`🚀 HMR Demo server running on http://localhost:${port}`);
  console.log('📝 Edit files in src/ to see hot reloading in action');
});