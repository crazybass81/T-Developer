#!/usr/bin/env node
// scripts/test-frontend-deps.js

const fs = require('fs');
const path = require('path');

function testFrontendDependencies() {
    console.log('🔍 프론트엔드 의존성 테스트 중...\n');
    
    const frontendDir = path.join(process.cwd(), 'frontend');
    const packageJsonPath = path.join(frontendDir, 'package.json');
    const nodeModulesPath = path.join(frontendDir, 'node_modules');
    
    // package.json 확인
    if (!fs.existsSync(packageJsonPath)) {
        console.log('❌ package.json이 없습니다');
        return false;
    }
    
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
    console.log('✅ package.json 확인됨');
    
    // node_modules 확인
    if (!fs.existsSync(nodeModulesPath)) {
        console.log('❌ node_modules가 없습니다');
        return false;
    }
    
    console.log('✅ node_modules 확인됨');
    
    // 주요 의존성 확인
    const keyDependencies = [
        'react',
        'react-dom',
        'vite',
        'typescript',
        '@vitejs/plugin-react'
    ];
    
    console.log('\n📦 주요 의존성 확인:');
    let allDepsInstalled = true;
    
    keyDependencies.forEach(dep => {
        const depPath = path.join(nodeModulesPath, dep);
        if (fs.existsSync(depPath)) {
            console.log(`✅ ${dep}`);
        } else {
            console.log(`❌ ${dep} - 설치되지 않음`);
            allDepsInstalled = false;
        }
    });
    
    console.log('\n📋 설치 상태:');
    if (allDepsInstalled) {
        console.log('✅ 모든 주요 의존성이 설치되었습니다!');
        console.log('🎯 다음 단계: npm run dev로 개발 서버 시작');
    } else {
        console.log('⚠️  일부 의존성이 누락되었습니다');
    }
    
    return allDepsInstalled;
}

if (require.main === module) {
    const success = testFrontendDependencies();
    process.exit(success ? 0 : 1);
}

module.exports = { testFrontendDependencies };