import webpack from 'webpack';
import TerserPlugin from 'terser-webpack-plugin';
import CompressionPlugin from 'compression-webpack-plugin';
import { BundleAnalyzerPlugin } from 'webpack-bundle-analyzer';
import nodeExternals from 'webpack-node-externals';
import path from 'path';
import fs from 'fs/promises';

// 백엔드 번들 최적화 설정
export const backendWebpackConfig: webpack.Configuration = {
  mode: process.env.NODE_ENV === 'production' ? 'production' : 'development',
  target: 'node',
  entry: {
    main: './src/main.ts',
    'agents/nl-input': './src/agents/nl-input-agent.ts',
    'agents/ui-selection': './src/agents/ui-selection-agent.ts',
    'agents/parsing': './src/agents/parsing-agent.ts',
    'agents/component-decision': './src/agents/component-decision-agent.ts',
    'agents/matching-rate': './src/agents/matching-rate-agent.ts',
    'agents/search': './src/agents/search-agent.ts',
    'agents/generation': './src/agents/generation-agent.ts',
    'agents/assembly': './src/agents/assembly-agent.ts',
    'agents/download': './src/agents/download-agent.ts'
  },
  output: {
    path: path.resolve(__dirname, '../../dist'),
    filename: '[name].js',
    libraryTarget: 'commonjs2'
  },
  externals: [nodeExternals()],
  module: {
    rules: [
      {
        test: /\.ts$/,
        use: 'ts-loader',
        exclude: /node_modules/
      }
    ]
  },
  resolve: {
    extensions: ['.ts', '.js'],
    alias: {
      '@': path.resolve(__dirname, '../src')
    }
  },
  optimization: {
    minimize: process.env.NODE_ENV === 'production',
    minimizer: [
      new TerserPlugin({
        terserOptions: {
          keep_classnames: true,
          keep_fnames: true
        }
      })
    ],
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        commons: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'initial'
        },
        shared: {
          test: /[\\/]src[\\/]shared[\\/]/,
          name: 'shared',
          chunks: 'all',
          minSize: 0
        }
      }
    }
  },
  plugins: [
    new webpack.DefinePlugin({
      'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV)
    }),
    new CompressionPlugin({
      algorithm: 'gzip',
      test: /\.(js|ts)$/,
      threshold: 10240,
      minRatio: 0.8
    }),
    ...(process.env.ANALYZE === 'true' ? [
      new BundleAnalyzerPlugin({
        analyzerMode: 'static',
        reportFilename: 'bundle-report.html'
      })
    ] : [])
  ]
};

// Lambda 함수 최적화 설정
export class LambdaOptimizer {
  createLambdaConfig(functionName: string, entryPoint: string): webpack.Configuration {
    return {
      mode: 'production',
      target: 'node18',
      entry: entryPoint,
      output: {
        path: path.resolve(__dirname, `../../dist/lambda/${functionName}`),
        filename: 'index.js',
        libraryTarget: 'commonjs2'
      },
      externals: [
        /^@aws-sdk/,
        'sharp',
        'puppeteer',
        'canvas'
      ],
      optimization: {
        minimize: true,
        minimizer: [
          new TerserPlugin({
            terserOptions: {
              compress: {
                drop_console: true,
                drop_debugger: true,
                pure_funcs: ['console.log', 'console.info']
              },
              mangle: {
                reserved: ['handler', 'exports']
              },
              output: {
                comments: false
              }
            }
          })
        ],
        usedExports: true,
        sideEffects: false
      },
      resolve: {
        extensions: ['.ts', '.js']
      },
      module: {
        rules: [
          {
            test: /\.ts$/,
            use: [
              {
                loader: 'ts-loader',
                options: {
                  transpileOnly: true,
                  compilerOptions: {
                    target: 'ES2022'
                  }
                }
              }
            ]
          }
        ]
      },
      plugins: [
        new webpack.optimize.LimitChunkCountPlugin({
          maxChunks: 1
        }),
        new webpack.EnvironmentPlugin({
          NODE_ENV: 'production',
          AWS_REGION: 'us-east-1'
        })
      ]
    };
  }

  async buildAllFunctions(): Promise<void> {
    const functions = [
      { name: 'nl-processor', entry: './src/lambda/nl-processor.ts' },
      { name: 'code-generator', entry: './src/lambda/code-generator.ts' },
      { name: 'component-searcher', entry: './src/lambda/component-searcher.ts' }
    ];

    for (const func of functions) {
      const config = this.createLambdaConfig(func.name, func.entry);
      await this.buildFunction(config);
      await this.validateBundleSize(func.name);
    }
  }

  private async buildFunction(config: webpack.Configuration): Promise<void> {
    return new Promise((resolve, reject) => {
      webpack(config, (err, stats) => {
        if (err || stats?.hasErrors()) {
          reject(err || new Error('Build failed'));
          return;
        }
        resolve();
      });
    });
  }

  private async validateBundleSize(functionName: string): Promise<void> {
    const bundlePath = path.resolve(__dirname, `../../dist/lambda/${functionName}/index.js`);
    const stats = await fs.stat(bundlePath);
    const sizeInMB = stats.size / (1024 * 1024);

    if (sizeInMB > 45) {
      throw new Error(`Lambda function ${functionName} bundle size (${sizeInMB.toFixed(2)}MB) exceeds safe limit`);
    }

    console.log(`✅ ${functionName} bundle size: ${sizeInMB.toFixed(2)}MB`);
  }
}

// 동적 임포트 헬퍼
export class DynamicImportManager {
  private loadedModules: Map<string, any> = new Map();

  async loadAgent(agentName: string): Promise<any> {
    const cached = this.loadedModules.get(agentName);
    if (cached) {
      return cached;
    }

    try {
      const module = await import(`../agents/${agentName}-agent`);
      this.loadedModules.set(agentName, module.default);
      return module.default;
    } catch (error) {
      console.error(`Failed to load agent ${agentName}:`, error);
      throw error;
    }
  }

  generatePreloadHints(requiredAgents: string[]): string[] {
    return requiredAgents.map(agent => 
      `<link rel="preload" href="/agents/${agent}.js" as="script">`
    );
  }

  unloadModule(moduleName: string): void {
    this.loadedModules.delete(moduleName);
    const resolvedPath = require.resolve(`../agents/${moduleName}-agent`);
    delete require.cache[resolvedPath];
  }
}