import express from 'express';
import path from 'path';
import { createHash } from 'crypto';
import { promises as fs } from 'fs';

export class LocalCDN {
  private app: express.Application;
  private cache: Map<string, Buffer> = new Map();
  
  constructor() {
    this.app = express();
    this.setupRoutes();
  }
  
  private setupRoutes() {
    // 정적 파일 서빙
    this.app.use('/static', express.static(path.join(process.cwd(), 'public'), {
      maxAge: '1y',
      etag: true,
      lastModified: true,
      setHeaders: (res, filepath) => {
        if (filepath.endsWith('.js') || filepath.endsWith('.css')) {
          res.setHeader('Cache-Control', 'public, max-age=31536000, immutable');
        } else if (filepath.endsWith('.html')) {
          res.setHeader('Cache-Control', 'no-cache');
        }
        res.setHeader('Access-Control-Allow-Origin', '*');
      }
    }));
    
    // 이미지 최적화
    this.app.get('/images/:size/:filename', async (req, res) => {
      const { size, filename } = req.params;
      const cacheKey = `${size}-${filename}`;
      
      if (this.cache.has(cacheKey)) {
        res.setHeader('X-Cache', 'HIT');
        return res.send(this.cache.get(cacheKey));
      }
      
      try {
        const originalPath = path.join(process.cwd(), 'public/images', filename);
        res.setHeader('X-Cache', 'MISS');
        res.sendFile(originalPath);
      } catch (error) {
        res.status(404).send('Image not found');
      }
    });
    
    // 파일 버전 관리
    this.app.get('/versioned/*', async (req, res) => {
      const filepath = req.params[0];
      const fullPath = path.join(process.cwd(), 'public', filepath);
      
      try {
        const content = await fs.readFile(fullPath);
        const hash = createHash('md5').update(content).digest('hex').substr(0, 8);
        
        res.setHeader('ETag', `"${hash}"`);
        res.setHeader('Cache-Control', 'public, max-age=31536000');
        res.send(content);
      } catch (error) {
        res.status(404).send('File not found');
      }
    });
  }
  
  start(port: number = 3002) {
    this.app.listen(port, () => {
      console.log(`🌐 Local CDN running on http://localhost:${port}`);
    });
  }
}