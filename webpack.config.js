const path = require('path');
const webpack = require('webpack');
const TerserPlugin = require('terser-webpack-plugin');
const CompressionPlugin = require('compression-webpack-plugin');
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
const nodeExternals = require('webpack-node-externals');

module.exports = {
  mode: process.env.NODE_ENV === 'production' ? 'production' : 'development',
  target: 'node',
  entry: {
    main: './backend/src/main.ts',
    'agents/nl-input': './backend/src/agents/nl-input-agent.ts',
    'agents/ui-selection': './backend/src/agents/ui-selection-agent.ts',
    'agents/parsing': './backend/src/agents/parsing-agent.ts',
    'agents/component-decision': './backend/src/agents/component-decision-agent.ts',
    'agents/matching-rate': './backend/src/agents/matching-rate-agent.ts',
    'agents/search': './backend/src/agents/search-agent.ts',
    'agents/generation': './backend/src/agents/generation-agent.ts',
    'agents/assembly': './backend/src/agents/assembly-agent.ts',
    'agents/download': './backend/src/agents/download-agent.ts'
  },
  output: {
    path: path.resolve(__dirname, 'dist'),
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
      '@': path.resolve(__dirname, 'backend/src')
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
          test: /[\\/]backend[\\/]src[\\/]shared[\\/]/,
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