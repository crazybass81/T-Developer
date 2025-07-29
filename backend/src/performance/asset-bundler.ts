import webpack from 'webpack';
import { promises as fs } from 'fs';
import path from 'path';
import crypto from 'crypto';

// 에셋 번들링 및 최적화
export class AssetBundler {
  private readonly outputDir: string;
  private readonly manifestPath: string;
  
  constructor(outputDir: string = './dist/assets') {
    this.outputDir = outputDir;
    this.manifestPath = path.join(outputDir, 'manifest.json');
  }
  
  // Webpack 설정 생성
  createWebpackConfig(env: 'development' | 'production'): webpack.Configuration {
    return {
      mode: env,
      entry: {
        main: './src/index.ts',
        vendor: ['react', 'react-dom', 'lodash']
      },
      output: {
        path: path.resolve(this.outputDir),
        filename: env === 'production' ? '[name].[contenthash:8].js' : '[name].js',
        chunkFilename: env === 'production' ? '[name].[contenthash:8].chunk.js' : '[name].chunk.js',
        clean: true
      },
      optimization: {
        splitChunks: {
          chunks: 'all',
          cacheGroups: {
            vendor: {
              test: /[\\/]node_modules[\\/]/,
              name: 'vendors',
              chunks: 'all',
            },
            common: {
              name: 'common',
              minChunks: 2,
              chunks: 'all',
              enforce: true
            }
          }
        },
        minimize: env === 'production',
        usedExports: true,
        sideEffects: false
      },
      resolve: {
        extensions: ['.ts', '.tsx', '.js', '.jsx']
      },
      module: {
        rules: [
          {
            test: /\.(ts|tsx)$/,
            use: 'ts-loader',
            exclude: /node_modules/
          },
          {
            test: /\.css$/,
            use: [
              'style-loader',
              {
                loader: 'css-loader',
                options: {
                  modules: true,
                  importLoaders: 1
                }
              },
              'postcss-loader'
            ]
          },
          {
            test: /\.(png|jpg|jpeg|gif|svg)$/,
            type: 'asset/resource',
            generator: {
              filename: 'images/[name].[hash:8][ext]'
            }
          }
        ]
      },
      plugins: [
        new webpack.DefinePlugin({
          'process.env.NODE_ENV': JSON.stringify(env)
        })
      ]
    };
  }
  
  // 번들링 실행
  async bundle(env: 'development' | 'production'): Promise<webpack.Stats> {
    const config = this.createWebpackConfig(env);
    const compiler = webpack(config);
    
    return new Promise((resolve, reject) => {
      compiler.run((err, stats) => {
        if (err) {
          reject(err);
          return;
        }
        
        if (stats?.hasErrors()) {
          reject(new Error(stats.toString()));
          return;
        }
        
        resolve(stats!);
      });
    });
  }
  
  // 매니페스트 파일 생성
  async generateManifest(stats: webpack.Stats): Promise<void> {
    const manifest: Record<string, string> = {};
    const compilation = stats.compilation;
    
    // 에셋 매핑 생성
    for (const [name, asset] of Object.entries(compilation.assets)) {
      const originalName = this.getOriginalName(name);
      manifest[originalName] = name;
    }
    
    await fs.writeFile(this.manifestPath, JSON.stringify(manifest, null, 2));
  }
  
  private getOriginalName(hashedName: string): string {
    return hashedName.replace(/\.[a-f0-9]{8}\./, '.');
  }
  
  // 번들 분석
  async analyzeBundles(stats: webpack.Stats): Promise<BundleAnalysis> {
    const compilation = stats.compilation;
    const chunks = Array.from(compilation.chunks);
    
    const analysis: BundleAnalysis = {
      totalSize: 0,
      chunks: [],
      duplicates: [],
      recommendations: []
    };
    
    for (const chunk of chunks) {
      const chunkSize = chunk.size();
      analysis.totalSize += chunkSize;
      
      analysis.chunks.push({
        name: chunk.name || 'unnamed',
        size: chunkSize,
        modules: chunk.getNumberOfModules(),
        files: Array.from(chunk.files)
      });
    }
    
    // 중복 모듈 감지
    analysis.duplicates = this.findDuplicateModules(compilation);
    
    // 최적화 권장사항
    analysis.recommendations = this.generateRecommendations(analysis);
    
    return analysis;
  }
  
  private findDuplicateModules(compilation: webpack.Compilation): DuplicateModule[] {
    const moduleMap = new Map<string, string[]>();
    
    compilation.modules.forEach(module => {
      const identifier = module.identifier();
      const chunks = Array.from(module.chunksIterable).map(chunk => chunk.name || 'unnamed');
      
      if (chunks.length > 1) {
        moduleMap.set(identifier, chunks);
      }
    });
    
    return Array.from(moduleMap.entries()).map(([module, chunks]) => ({
      module,
      chunks,
      impact: 'medium' as const
    }));
  }
  
  private generateRecommendations(analysis: BundleAnalysis): string[] {
    const recommendations: string[] = [];
    
    if (analysis.totalSize > 1024 * 1024) { // 1MB
      recommendations.push('Consider code splitting for large bundles');
    }
    
    if (analysis.duplicates.length > 0) {
      recommendations.push('Remove duplicate modules to reduce bundle size');
    }
    
    const largeChunks = analysis.chunks.filter(chunk => chunk.size > 500 * 1024);
    if (largeChunks.length > 0) {
      recommendations.push('Split large chunks for better caching');
    }
    
    return recommendations;
  }
}

// 타입 정의
interface BundleAnalysis {
  totalSize: number;
  chunks: ChunkInfo[];
  duplicates: DuplicateModule[];
  recommendations: string[];
}

interface ChunkInfo {
  name: string;
  size: number;
  modules: number;
  files: string[];
}

interface DuplicateModule {
  module: string;
  chunks: string[];
  impact: 'low' | 'medium' | 'high';
}

// 에셋 최적화 파이프라인
export class AssetOptimizationPipeline {
  private bundler: AssetBundler;
  
  constructor(outputDir?: string) {
    this.bundler = new AssetBundler(outputDir);
  }
  
  async optimize(env: 'development' | 'production'): Promise<OptimizationResult> {
    const startTime = Date.now();
    
    // 1. 번들링
    const stats = await this.bundler.bundle(env);
    
    // 2. 매니페스트 생성
    await this.bundler.generateManifest(stats);
    
    // 3. 분석
    const analysis = await this.bundler.analyzeBundles(stats);
    
    // 4. 최적화 메트릭
    const metrics = this.calculateMetrics(stats, analysis);
    
    return {
      success: true,
      duration: Date.now() - startTime,
      analysis,
      metrics,
      recommendations: analysis.recommendations
    };
  }
  
  private calculateMetrics(stats: webpack.Stats, analysis: BundleAnalysis): OptimizationMetrics {
    return {
      bundleSize: analysis.totalSize,
      chunkCount: analysis.chunks.length,
      compressionRatio: this.estimateCompressionRatio(analysis.totalSize),
      cacheEfficiency: this.calculateCacheEfficiency(analysis.chunks)
    };
  }
  
  private estimateCompressionRatio(size: number): number {
    // Gzip 압축률 추정 (일반적으로 70-80%)
    return 0.75;
  }
  
  private calculateCacheEfficiency(chunks: ChunkInfo[]): number {
    const vendorChunks = chunks.filter(chunk => chunk.name.includes('vendor'));
    const totalSize = chunks.reduce((sum, chunk) => sum + chunk.size, 0);
    const vendorSize = vendorChunks.reduce((sum, chunk) => sum + chunk.size, 0);
    
    // 벤더 청크 비율이 높을수록 캐시 효율성이 좋음
    return vendorSize / totalSize;
  }
}

interface OptimizationResult {
  success: boolean;
  duration: number;
  analysis: BundleAnalysis;
  metrics: OptimizationMetrics;
  recommendations: string[];
}

interface OptimizationMetrics {
  bundleSize: number;
  chunkCount: number;
  compressionRatio: number;
  cacheEfficiency: number;
}