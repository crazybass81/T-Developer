import https from 'https';
import fs from 'fs';
import path from 'path';
import express from 'express';

export interface HttpsServerOptions {
  keyPath?: string;
  certPath?: string;
  port?: number;
}

export function createHttpsServer(
  app: express.Application,
  options: HttpsServerOptions = {}
) {
  const certDir = path.join(process.cwd(), 'certs');
  
  const keyPath = options.keyPath || path.join(certDir, 'server.key');
  const certPath = options.certPath || path.join(certDir, 'server.crt');
  
  // 인증서 파일 존재 확인
  if (!fs.existsSync(keyPath) || !fs.existsSync(certPath)) {
    throw new Error(
      `SSL 인증서를 찾을 수 없습니다. scripts/generate-ssl-certs.sh를 실행하세요.\n` +
      `Key: ${keyPath}\n` +
      `Cert: ${certPath}`
    );
  }
  
  const httpsOptions = {
    key: fs.readFileSync(keyPath),
    cert: fs.readFileSync(certPath)
  };
  
  return https.createServer(httpsOptions, app);
}

export function startHttpsServer(
  app: express.Application,
  options: HttpsServerOptions = {}
): Promise<https.Server> {
  return new Promise((resolve, reject) => {
    try {
      const httpsServer = createHttpsServer(app, options);
      const port = options.port || 443;
      
      httpsServer.listen(port, () => {
        console.log(`🔒 HTTPS Server running on https://localhost:${port}`);
        resolve(httpsServer);
      });
      
      httpsServer.on('error', (error) => {
        reject(error);
      });
      
    } catch (error) {
      reject(error);
    }
  });
}