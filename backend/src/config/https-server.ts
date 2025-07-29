import https from 'https';
import fs from 'fs';
import path from 'path';
import express from 'express';

export function createHttpsServer(app: express.Application) {
  const certPath = path.join(process.cwd(), 'certs');
  
  const options = {
    key: fs.readFileSync(path.join(certPath, 'server.key')),
    cert: fs.readFileSync(path.join(certPath, 'server.crt'))
  };
  
  return https.createServer(options, app);
}

export function setupHttpsInDevelopment(app: express.Application) {
  if (process.env.NODE_ENV === 'development' && process.env.USE_HTTPS === 'true') {
    const httpsServer = createHttpsServer(app);
    httpsServer.listen(443, () => {
      console.log('🔒 HTTPS Server running on https://localhost');
    });
  }
}