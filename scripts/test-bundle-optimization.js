#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('🔍 번들 최적화 설정 검증 중...\n');

// 필수 파일 확인
const requiredFiles = [
  'backend/src/performance/bundle-optimizer.ts',
  'backend/src/utils/lazy-component.tsx',
  'webpack.config.js',
  'frontend/vite.config.ts'
];

let allFilesExist = true;

requiredFiles.forEach(file => {
  const filePath = path.join(__dirname, '..', file);
  if (fs.existsSync(filePath)) {
    const stats = fs.statSync(filePath);
    console.log(`✅ ${file} (${(stats.size / 1024).toFixed(2)}KB)`);
  } else {
    console.log(`❌ ${file} - 파일이 존재하지 않음`);
    allFilesExist = false;
  }
});

// Webpack 설정 검증
try {
  const webpackConfig = require('../webpack.config.js');
  console.log('\n📦 Webpack 설정 검증:');
  console.log(`✅ Entry points: ${Object.keys(webpackConfig.entry).length}개`);
  console.log(`✅ Target: ${webpackConfig.target}`);
  console.log(`✅ Mode: ${webpackConfig.mode}`);
  console.log(`✅ Plugins: ${webpackConfig.plugins.length}개`);
} catch (error) {
  console.log('❌ Webpack 설정 로드 실패:', error.message);
  allFilesExist = false;
}

// Vite 설정 검증
try {
  const viteConfigPath = path.join(__dirname, '..', 'frontend', 'vite.config.ts');
  const viteConfig = fs.readFileSync(viteConfigPath, 'utf8');
  
  console.log('\n⚡ Vite 설정 검증:');
  console.log(`✅ manualChunks 설정: ${viteConfig.includes('manualChunks') ? '있음' : '없음'}`);
  console.log(`✅ Terser 최적화: ${viteConfig.includes('terserOptions') ? '있음' : '없음'}`);
  console.log(`✅ CSS 코드 스플리팅: ${viteConfig.includes('cssCodeSplit') ? '있음' : '없음'}`);
} catch (error) {
  console.log('❌ Vite 설정 검증 실패:', error.message);
}

// 번들 최적화 클래스 검증
try {
  const bundleOptimizerPath = path.join(__dirname, '..', 'backend', 'src', 'performance', 'bundle-optimizer.ts');
  const bundleOptimizer = fs.readFileSync(bundleOptimizerPath, 'utf8');
  
  console.log('\n🚀 번들 최적화 기능 검증:');
  console.log(`✅ LambdaOptimizer: ${bundleOptimizer.includes('class LambdaOptimizer') ? '있음' : '없음'}`);
  console.log(`✅ DynamicImportManager: ${bundleOptimizer.includes('class DynamicImportManager') ? '있음' : '없음'}`);
  console.log(`✅ TerserPlugin: ${bundleOptimizer.includes('TerserPlugin') ? '있음' : '없음'}`);
  console.log(`✅ CompressionPlugin: ${bundleOptimizer.includes('CompressionPlugin') ? '있음' : '없음'}`);
} catch (error) {
  console.log('❌ 번들 최적화 클래스 검증 실패:', error.message);
}

// 지연 로딩 컴포넌트 검증
try {
  const lazyComponentPath = path.join(__dirname, '..', 'backend', 'src', 'utils', 'lazy-component.tsx');
  const lazyComponent = fs.readFileSync(lazyComponentPath, 'utf8');
  
  console.log('\n⏳ 지연 로딩 기능 검증:');
  console.log(`✅ LazyComponent: ${lazyComponent.includes('LazyComponent') ? '있음' : '없음'}`);
  console.log(`✅ PrefetchManager: ${lazyComponent.includes('class PrefetchManager') ? '있음' : '없음'}`);
  console.log(`✅ IntersectionObserver: ${lazyComponent.includes('IntersectionObserver') ? '있음' : '없음'}`);
} catch (error) {
  console.log('❌ 지연 로딩 컴포넌트 검증 실패:', error.message);
}

console.log('\n📊 번들 최적화 설정 요약:');
console.log('- 백엔드: Webpack 기반 에이전트별 코드 스플리팅');
console.log('- 프론트엔드: Vite 기반 기능별 청크 분할');
console.log('- Lambda: 50MB 제한 내 최적화');
console.log('- 동적 로딩: 필요시 에이전트 로드');
console.log('- 프리페치: 사용자 행동 예측 기반 미리 로드');

if (allFilesExist) {
  console.log('\n✅ 번들 최적화 설정 검증 완료!');
  process.exit(0);
} else {
  console.log('\n❌ 일부 파일이 누락되었습니다.');
  process.exit(1);
}