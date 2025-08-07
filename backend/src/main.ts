import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import { HybridConfigManager } from './config/config-manager';

const app = express();
const configManager = new HybridConfigManager();

async function startServer() {
  try {
    // Initialize configuration from AWS
    console.log('🔐 Initializing configuration from AWS...');
    await configManager.initialize();
    
    const PORT = process.env.PORT || 8000;
    const environment = process.env.NODE_ENV || 'development';
    
    // Middleware
    app.use(helmet());
    app.use(cors({
      origin: process.env.FRONTEND_URL || 'http://localhost:5173',
      credentials: true
    }));
    app.use(express.json());
    app.use(express.urlencoded({ extended: true }));

    // Health check endpoint
    app.get('/health', (req, res) => {
      res.json({ 
        status: 'ok', 
        timestamp: new Date().toISOString(),
        service: 'T-Developer Backend',
        environment: environment,
        version: '1.0.0'
      });
    });

    // Natural Language API endpoint
    app.post('/api/v1/generate', async (req, res) => {
      try {
        const { query, framework } = req.body;
        
        if (!query) {
          return res.status(400).json({ 
            error: 'Query is required',
            message: 'Please provide a natural language description of what you want to build'
          });
        }

        // TODO: Implement actual NL processing with agents
        // For now, return a mock response
        const mockResponse = {
          status: 'success',
          query: query,
          framework: framework || 'auto-detect',
          message: 'Natural language processing endpoint is ready',
          timestamp: new Date().toISOString(),
          result: {
            components: ['Header', 'MainContent', 'Footer'],
            estimatedTime: '5 minutes',
            confidence: 0.85
          }
        };

        res.json(mockResponse);
      } catch (error) {
        console.error('Error processing NL query:', error);
        res.status(500).json({ 
          error: 'Internal server error',
          message: 'Failed to process natural language query'
        });
      }
    });

    // List available frameworks
    app.get('/api/v1/frameworks', (req, res) => {
      res.json({
        frameworks: [
          { id: 'react', name: 'React', version: '18.x' },
          { id: 'vue', name: 'Vue.js', version: '3.x' },
          { id: 'angular', name: 'Angular', version: '17.x' },
          { id: 'nextjs', name: 'Next.js', version: '14.x' },
          { id: 'svelte', name: 'Svelte', version: '4.x' }
        ]
      });
    });

    // Config endpoint (only in development)
    if (environment === 'development') {
      app.get('/api/config', (req, res) => {
        res.json({
          environment: environment,
          port: PORT,
          features: {
            nlProcessing: true,
            codeGeneration: true,
            multiFramework: true
          }
        });
      });
    }

    // 404 handler
    app.use((req, res) => {
      res.status(404).json({ 
        error: 'Not Found',
        message: `Cannot ${req.method} ${req.url}`
      });
    });

    // Error handler
    app.use((err: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
      console.error('Error:', err);
      res.status(err.status || 500).json({
        error: err.message || 'Internal Server Error',
        ...(environment === 'development' && { stack: err.stack })
      });
    });

    app.listen(PORT, () => {
      console.log(`✅ T-Developer Backend running on port ${PORT}`);
      console.log(`🌍 Environment: ${environment}`);
      console.log(`🔗 Health check: http://localhost:${PORT}/health`);
      console.log(`🤖 NL API: http://localhost:${PORT}/api/v1/generate`);
      console.log(`📦 Frameworks: http://localhost:${PORT}/api/v1/frameworks`);
      
      if (environment === 'development') {
        console.log(`⚙️ Config endpoint: http://localhost:${PORT}/api/config`);
      }
    });
  } catch (error) {
    console.error('❌ Failed to start server:', error);
    // In development, start without AWS config
    if (process.env.NODE_ENV === 'development') {
      console.log('⚠️ Starting in local mode without AWS configuration...');
      startLocalServer();
    } else {
      process.exit(1);
    }
  }
}

// Fallback local server without AWS
function startLocalServer() {
  const PORT = 8000;
  
  // Basic middleware
  app.use(cors());
  app.use(express.json());

  // Health check
  app.get('/health', (req, res) => {
    res.json({ 
      status: 'ok', 
      mode: 'local',
      timestamp: new Date().toISOString()
    });
  });

  // Natural Language API
  app.post('/api/v1/generate', (req, res) => {
    const { query } = req.body;
    res.json({
      status: 'success',
      mode: 'local',
      query: query,
      message: 'Running in local mode without AWS configuration'
    });
  });

  app.listen(PORT, () => {
    console.log(`✅ Server running in LOCAL mode on port ${PORT}`);
    console.log(`🔗 http://localhost:${PORT}/health`);
  });
}

// Start the server
startServer();