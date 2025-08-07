import express from 'express';
import { configManager } from './config/aws-secrets';

const app = express();

async function startServer() {
  try {
    // Initialize configuration from AWS Secrets Manager
    console.log('🔐 Initializing configuration from AWS Secrets Manager...');
    await configManager.initialize();
    
    const PORT = configManager.get<number>('app.port') || 8000;
    const environment = configManager.get<string>('app.environment');
    
    app.use(express.json());

    app.get('/health', (req, res) => {
      res.json({ 
        status: 'ok', 
        timestamp: new Date().toISOString(),
        service: 'T-Developer Backend',
        environment: environment,
        version: '1.0.0'
      });
    });

    // Config endpoint (only in development)
    if (environment === 'development') {
      app.get('/api/config', (req, res) => {
        const config = configManager.getAll();
        // Remove sensitive data
        const safeConfig = {
          app: config.app,
          features: config.features,
          environment: environment
        };
        res.json(safeConfig);
      });
    }

    app.listen(PORT, () => {
      console.log(`✅ T-Developer Backend running on port ${PORT}`);
      console.log(`🌍 Environment: ${environment}`);
      console.log(`🔗 Health check: http://localhost:${PORT}/health`);
      
      if (environment === 'development') {
        console.log(`⚙️ Config endpoint: http://localhost:${PORT}/api/config`);
      }
    });
  } catch (error) {
    console.error('❌ Failed to start server:', error);
    process.exit(1);
  }
}

// Start the server
startServer();