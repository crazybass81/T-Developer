import app from './app';
import { SecureEnvLoader } from './utils/env-loader';
import { initializeSecrets } from './config/secrets-manager';
import { startHttpsServer } from './config/https-server';

async function startServer() {
  // Initialize secrets from AWS Secrets Manager
  await initializeSecrets();
  
  // Load environment variables
  const envLoader = new SecureEnvLoader();
  await envLoader.loadEnvironment();

  const PORT = process.env.PORT || 8000;
  
  // HTTP 서버 시작
  app.listen(PORT, () => {
    console.log(`✅ T-Developer server running on port ${PORT}`);
    console.log(`🔒 Security headers enabled`);
    console.log(`🛡️  CORS configured`);
    console.log(`⚡ Rate limiting active`);
    console.log(`📊 Request tracking enabled`);
  });
  
  // HTTPS 서버 시작 (개발 환경)
  startHttpsServer(app, 8443);
}

startServer().catch(console.error);