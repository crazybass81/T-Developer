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
        // 파일 타입별 캐시 설정
        if (filepath.endsWith('.js') || filepath.endsWith('.css')) {
          res.setHeader('Cache-Control', 'public, max-age=31536000, immutable');
        } else if (filepath.endsWith('.html')) {
          res.setHeader('Cache-Control', 'no-cache');
        }
        
        // CORS 헤더
        res.setHeader('Access-Control-Allow-Origin', '*');
      }
    }));
    
    // 이미지 최적화
    this.app.get('/images/:size/:filename', async (req, res) => {
      const { size, filename } = req.params;
      const cacheKey = `${size}-${filename}`;
      
      // 캐시 확인
      if (this.cache.has(cacheKey)) {
        res.setHeader('X-Cache', 'HIT');
        return res.send(this.cache.get(cacheKey));
      }
      
      try {
        const originalPath = path.join(process.cwd(), 'public/images', filename);
        
        // 파일 존재 확인
        await fs.access(originalPath);
        
        // 원본 파일 읽기 (실제로는 sharp로 리사이징)
        const content = await fs.readFile(originalPath);
        
        // 캐시에 저장
        this.cache.set(cacheKey, content);
        
        res.setHeader('X-Cache', 'MISS');
        res.setHeader('Content-Type', this.getContentType(filename));
        res.send(content);
      } catch (error) {
        res.status(404).send('Image not found');
      }
    });
    
    // 파일 버전 관리
    this.app.get('/versioned/*', async (req, res) => {
      const filepath = (req.params as any)[0];
      const fullPath = path.join(process.cwd(), 'public', filepath);
      
      try {
        const content = await fs.readFile(fullPath);
        const hash = createHash('md5').update(content).digest('hex').substr(0, 8);
        
        res.setHeader('ETag', `"${hash}"`);
        res.setHeader('Cache-Control', 'public, max-age=31536000');
        res.setHeader('Content-Type', this.getContentType(filepath));
        
        res.send(content);
      } catch (error) {
        res.status(404).send('File not found');
      }
    });
    
    // 헬스 체크
    this.app.get('/health', (req, res) => {
      res.json({
        status: 'healthy',
        cache_size: this.cache.size,
        uptime: process.uptime()
      });
    });
  }
  
  private getContentType(filename: string): string {
    const ext = path.extname(filename).toLowerCase();
    const types: Record<string, string> = {
      '.js': 'application/javascript',
      '.css': 'text/css',
      '.html': 'text/html',
      '.json': 'application/json',
      '.png': 'image/png',
      '.jpg': 'image/jpeg',
      '.jpeg': 'image/jpeg',
      '.gif': 'image/gif',
      '.svg': 'image/svg+xml'
    };
    return types[ext] || 'application/octet-stream';
  }
  
  start(port: number = 3003) {
    this.app.listen(port, () => {
      console.log(`🌐 Local CDN running on http://localhost:${port}`);
    });
  }
}