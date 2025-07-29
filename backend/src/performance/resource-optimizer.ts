import sharp from 'sharp';
const imagemin = require('imagemin');
const imageminPngquant = require('imagemin-pngquant');
const imageminMozjpeg = require('imagemin-mozjpeg');
const imageminSvgo = require('imagemin-svgo');
import { createReadStream, createWriteStream } from 'fs';
import { promises as fs } from 'fs';
import { pipeline } from 'stream/promises';
import zlib from 'zlib';
import crypto from 'crypto';
import path from 'path';
import { Request, Response, NextFunction } from 'express';

// 이미지 최적화 서비스
export class ImageOptimizationService {
  private readonly cachePath = './cache/images';
  private readonly supportedFormats = ['jpeg', 'jpg', 'png', 'webp', 'avif'];
  
  async optimizeImage(
    inputPath: string,
    outputPath: string,
    options: {
      width?: number;
      height?: number;
      quality?: number;
      format?: string;
    } = {}
  ): Promise<void> {
    const { width, height, quality = 85, format } = options;
    
    let sharpInstance = sharp(inputPath);
    
    if (width || height) {
      sharpInstance = sharpInstance.resize(width, height, {
        fit: 'inside',
        withoutEnlargement: true
      });
    }
    
    if (format && this.supportedFormats.includes(format)) {
      sharpInstance = sharpInstance.toFormat(format as any, { quality });
    }
    
    sharpInstance = sharpInstance.withMetadata();
    
    await sharpInstance.toFile(outputPath);
    await this.furtherOptimize(outputPath, format || 'jpeg');
  }
  
  private async furtherOptimize(filePath: string, format: string): Promise<void> {
    const plugins = [];
    
    switch (format) {
      case 'jpeg':
      case 'jpg':
        plugins.push(imageminMozjpeg({ quality: 85 }));
        break;
      case 'png':
        plugins.push(imageminPngquant({ quality: [0.6, 0.8] }));
        break;
      case 'svg':
        plugins.push(imageminSvgo());
        break;
    }
    
    if (plugins.length > 0) {
      await imagemin([filePath], {
        destination: path.dirname(filePath),
        plugins
      });
    }
  }
  
  async generateResponsiveImages(
    inputPath: string,
    outputDir: string,
    breakpoints: number[] = [320, 640, 960, 1280, 1920]
  ): Promise<Record<string, string>> {
    const results: Record<string, string> = {};
    const format = 'webp';
    
    for (const width of breakpoints) {
      const outputName = `image-${width}w.${format}`;
      const outputPath = path.join(outputDir, outputName);
      
      await this.optimizeImage(inputPath, outputPath, {
        width,
        format,
        quality: this.getQualityForWidth(width)
      });
      
      results[`${width}w`] = outputPath;
    }
    
    const originalName = `image-original.${format}`;
    const originalPath = path.join(outputDir, originalName);
    await this.optimizeImage(inputPath, originalPath, { format });
    results['original'] = originalPath;
    
    return results;
  }
  
  private getQualityForWidth(width: number): number {
    if (width <= 640) return 70;
    if (width <= 1280) return 80;
    return 85;
  }
  
  generateCacheKey(options: any): string {
    const hash = crypto
      .createHash('md5')
      .update(JSON.stringify(options))
      .digest('hex');
    return hash;
  }
}

// 파일 압축 서비스
export class CompressionService {
  async gzipFile(inputPath: string, outputPath: string): Promise<void> {
    const gzip = zlib.createGzip({ level: 9 });
    await pipeline(
      createReadStream(inputPath),
      gzip,
      createWriteStream(outputPath)
    );
  }
  
  async brotliFile(inputPath: string, outputPath: string): Promise<void> {
    const brotli = zlib.createBrotliCompress({
      params: {
        [zlib.constants.BROTLI_PARAM_QUALITY]: 11
      }
    });
    await pipeline(
      createReadStream(inputPath),
      brotli,
      createWriteStream(outputPath)
    );
  }
  
  async compressFile(
    inputPath: string,
    outputDir: string,
    acceptEncoding: string = ''
  ): Promise<string> {
    const filename = path.basename(inputPath);
    const stats = await fs.stat(inputPath);
    
    if (stats.size < 1024) {
      return inputPath;
    }
    
    if (acceptEncoding.includes('br')) {
      const brotliPath = path.join(outputDir, `${filename}.br`);
      await this.brotliFile(inputPath, brotliPath);
      
      const brotliStats = await fs.stat(brotliPath);
      if (brotliStats.size < stats.size * 0.9) {
        return brotliPath;
      }
    }
    
    if (acceptEncoding.includes('gzip')) {
      const gzipPath = path.join(outputDir, `${filename}.gz`);
      await this.gzipFile(inputPath, gzipPath);
      
      const gzipStats = await fs.stat(gzipPath);
      if (gzipStats.size < stats.size * 0.9) {
        return gzipPath;
      }
    }
    
    return inputPath;
  }
}

// CDN 최적화 헤더
export class CDNOptimizer {
  private cacheRules: Record<string, string> = {
    'js.hash': 'public, max-age=31536000, immutable',
    'css.hash': 'public, max-age=31536000, immutable',
    'jpg': 'public, max-age=86400, stale-while-revalidate=604800',
    'png': 'public, max-age=86400, stale-while-revalidate=604800',
    'webp': 'public, max-age=86400, stale-while-revalidate=604800',
    'svg': 'public, max-age=86400, stale-while-revalidate=604800',
    'woff2': 'public, max-age=31536000, immutable',
    'json': 'no-cache, must-revalidate',
    'html': 'no-cache, no-store, must-revalidate'
  };
  
  getCacheHeaders(filename: string): Record<string, string> {
    const ext = path.extname(filename).slice(1);
    const hasHash = /\.[a-f0-9]{8,}\./i.test(filename);
    
    const cacheKey = hasHash ? `${ext}.hash` : ext;
    const cacheControl = this.cacheRules[cacheKey] || 'public, max-age=3600';
    
    return {
      'Cache-Control': cacheControl,
      'Vary': 'Accept-Encoding',
      'X-Content-Type-Options': 'nosniff'
    };
  }
  
  handleConditionalRequest(
    req: Request,
    res: Response,
    fileStats: any,
    etag: string
  ): boolean {
    if (req.headers['if-none-match'] === etag) {
      res.status(304).end();
      return true;
    }
    
    const lastModified = fileStats.mtime.toUTCString();
    if (req.headers['if-modified-since'] === lastModified) {
      res.status(304).end();
      return true;
    }
    
    res.setHeader('ETag', etag);
    res.setHeader('Last-Modified', lastModified);
    
    return false;
  }
  
  generateETag(content: Buffer | string): string {
    const hash = crypto
      .createHash('md5')
      .update(content)
      .digest('hex');
    return `"${hash}"`;
  }
}

// 리소스 최적화 미들웨어
export function resourceOptimizationMiddleware(options: {
  imageOptimizer: ImageOptimizationService;
  compressionService: CompressionService;
  cdnOptimizer: CDNOptimizer;
}) {
  const { imageOptimizer, compressionService, cdnOptimizer } = options;
  
  return async (req: Request, res: Response, next: NextFunction) => {
    if (!req.path.match(/\.(jpg|jpeg|png|webp|svg|js|css|woff2)$/i)) {
      return next();
    }
    
    const filePath = path.join(process.cwd(), 'public', req.path);
    
    try {
      const stats = await fs.stat(filePath);
      const content = await fs.readFile(filePath);
      const etag = cdnOptimizer.generateETag(content);
      
      if (cdnOptimizer.handleConditionalRequest(req, res, stats, etag)) {
        return;
      }
      
      const cacheHeaders = cdnOptimizer.getCacheHeaders(req.path);
      Object.entries(cacheHeaders).forEach(([key, value]) => {
        res.setHeader(key, value);
      });
      
      if (req.path.match(/\.(jpg|jpeg|png|webp)$/i)) {
        const acceptHeader = req.headers.accept || '';
        const supportsWebP = acceptHeader.includes('image/webp');
        const supportsAvif = acceptHeader.includes('image/avif');
        
        let format = 'original';
        if (supportsAvif) format = 'avif';
        else if (supportsWebP) format = 'webp';
        
        if (format !== 'original') {
          const cacheKey = imageOptimizer.generateCacheKey({
            path: req.path,
            format,
            width: req.query.w,
            quality: req.query.q
          });
          
          // 캐시된 최적화 이미지 확인 및 생성
          const cachedPath = path.join('./cache/images', `${cacheKey}.${format}`);
          try {
            await fs.access(cachedPath);
            return res.sendFile(path.resolve(cachedPath));
          } catch {
            await imageOptimizer.optimizeImage(filePath, cachedPath, {
              format,
              width: req.query.w ? parseInt(req.query.w as string) : undefined,
              quality: req.query.q ? parseInt(req.query.q as string) : undefined
            });
            return res.sendFile(path.resolve(cachedPath));
          }
        }
      }
      
      const acceptEncoding = req.headers['accept-encoding'] || '';
      const compressedPath = await compressionService.compressFile(
        filePath,
        path.dirname(filePath),
        acceptEncoding
      );
      
      if (compressedPath !== filePath) {
        const encoding = compressedPath.endsWith('.br') ? 'br' : 'gzip';
        res.setHeader('Content-Encoding', encoding);
      }
      
      res.sendFile(path.resolve(compressedPath));
      
    } catch (error) {
      next(error);
    }
  };
}

// 리소스 힌트 생성기
export class ResourceHintGenerator {
  generateHints(resources: Array<{ url: string; type: string; priority?: string }>): string[] {
    const hints: string[] = [];
    
    resources.forEach(resource => {
      if (resource.url.startsWith('http')) {
        const origin = new URL(resource.url).origin;
        hints.push(`<link rel="preconnect" href="${origin}">`);
        hints.push(`<link rel="dns-prefetch" href="${origin}">`);
      }
      
      if (resource.priority === 'high') {
        const as = this.getResourceType(resource.type);
        hints.push(`<link rel="preload" href="${resource.url}" as="${as}">`);
      }
      
      if (resource.priority === 'low') {
        hints.push(`<link rel="prefetch" href="${resource.url}">`);
      }
    });
    
    return [...new Set(hints)];
  }
  
  private getResourceType(mimeType: string): string {
    if (mimeType.includes('javascript')) return 'script';
    if (mimeType.includes('css')) return 'style';
    if (mimeType.includes('image')) return 'image';
    if (mimeType.includes('font')) return 'font';
    return 'fetch';
  }
  
  async extractCriticalCSS(html: string, css: string): Promise<string> {
    const criticalSelectors = [
      'body', 'header', 'nav', 'main',
      '.hero', '.container', '.btn-primary'
    ];
    
    // 간단한 CSS 필터링 (실제로는 더 정교한 파싱 필요)
    const lines = css.split('\n');
    const criticalCSS = lines.filter(line => 
      criticalSelectors.some(selector => line.includes(selector))
    );
    
    return criticalCSS.join('\n');
  }
}