import express from 'express';
import path from 'path';
import fs from 'fs/promises';
import { 
  ImageOptimizationService, 
  CompressionService, 
  CDNOptimizer,
  resourceOptimizationMiddleware 
} from '../performance/resource-optimizer';

const router = express.Router();

// Initialize services
const imageOptimizer = new ImageOptimizationService();
const compressionService = new CompressionService();
const cdnOptimizer = new CDNOptimizer();

// Apply resource optimization middleware
router.use(resourceOptimizationMiddleware({
  imageOptimizer,
  compressionService,
  cdnOptimizer
}));

// Demo endpoints
router.get('/optimize-image', async (req, res) => {
  try {
    const { width, height, quality, format } = req.query;
    
    // Create a sample image for demo
    const inputPath = path.join(process.cwd(), 'public', 'sample.jpg');
    const outputPath = path.join(process.cwd(), 'public', 'optimized.webp');
    
    await imageOptimizer.optimizeImage(inputPath, outputPath, {
      width: width ? parseInt(width as string) : undefined,
      height: height ? parseInt(height as string) : undefined,
      quality: quality ? parseInt(quality as string) : 85,
      format: format as string || 'webp'
    });
    
    res.json({
      message: 'Image optimized successfully',
      input: inputPath,
      output: outputPath,
      options: { width, height, quality, format }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.get('/compress-file', async (req, res) => {
  try {
    const { file, encoding } = req.query;
    
    if (!file) {
      return res.status(400).json({ error: 'File parameter required' });
    }
    
    const inputPath = path.join(process.cwd(), 'public', file as string);
    const outputDir = path.dirname(inputPath);
    
    const compressedPath = await compressionService.compressFile(
      inputPath,
      outputDir,
      encoding as string || 'gzip, br'
    );
    
    const originalStats = await fs.stat(inputPath);
    const compressedStats = await fs.stat(compressedPath);
    
    res.json({
      message: 'File compressed successfully',
      original: {
        path: inputPath,
        size: originalStats.size
      },
      compressed: {
        path: compressedPath,
        size: compressedStats.size,
        ratio: ((originalStats.size - compressedStats.size) / originalStats.size * 100).toFixed(2) + '%'
      }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.get('/cache-headers/:filename', (req, res) => {
  const { filename } = req.params;
  const headers = cdnOptimizer.getCacheHeaders(filename);
  
  res.json({
    filename,
    headers,
    explanation: {
      'Cache-Control': 'How long browsers and CDNs should cache the file',
      'Vary': 'Response varies based on Accept-Encoding header',
      'X-Content-Type-Options': 'Prevents MIME type sniffing'
    }
  });
});

router.get('/stats', async (req, res) => {
  try {
    const publicDir = path.join(process.cwd(), 'public');
    const files = await fs.readdir(publicDir);
    
    const stats = await Promise.all(
      files.map(async (file) => {
        const filePath = path.join(publicDir, file);
        const stat = await fs.stat(filePath);
        
        return {
          name: file,
          size: stat.size,
          modified: stat.mtime,
          cacheHeaders: cdnOptimizer.getCacheHeaders(file)
        };
      })
    );
    
    res.json({
      message: 'Resource optimization stats',
      totalFiles: files.length,
      files: stats,
      services: {
        imageOptimizer: 'Ready',
        compressionService: 'Ready',
        cdnOptimizer: 'Ready'
      }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

export default router;