import sharp from 'sharp';
import { createReadStream, createWriteStream } from 'fs';
import { pipeline } from 'stream/promises';
import zlib from 'zlib';
import crypto from 'crypto';
import path from 'path';
import fs from 'fs/promises';
import { Request, Response, NextFunction } from 'express';

export class ImageOptimizationService {
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
    
    sharpInstance = sharpInstance.withMetadata({
      exif: false,
      icc: false,
      iptc: false,
      xmp: false
    });
    
    await sharpInstance.toFile(outputPath);
  }
  
  generateCacheKey(options: any): string {
    return crypto
      .createHash('md5')
      .update(JSON.stringify(options))
      .digest('hex');
  }
}

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
      
      res.sendFile(compressedPath);
      
    } catch (error) {
      next(error);
    }
  };
}