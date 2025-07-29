#!/usr/bin/env node
// scripts/check-frontend-setup.js

const fs = require('fs');
const path = require('path');

function checkFrontendSetup() {
    console.log('🔍 프론트엔드 설정 확인 중...\n');
    
    const frontendDir = path.join(process.cwd(), 'frontend');
    const requiredFiles = [
        'package.json',
        'vite.config.ts',
        'tsconfig.json',
        'index.html',
        'src/main.tsx',
        'src/App.tsx'
    ];
    
    let allFilesExist = true;
    
    console.log('📁 필수 파일 확인:');
    requiredFiles.forEach(file => {
        const filePath = path.join(frontendDir, file);
        if (fs.existsSync(filePath)) {
            console.log(`✅ ${file}`);
        } else {
            console.log(`❌ ${file} - 파일이 없습니다`);
            allFilesExist = false;
        }
    });
    
    console.log('\n📋 프론트엔드 설정 상태:');
    if (allFilesExist) {
        console.log('✅ 모든 필수 파일이 생성되었습니다');
        console.log('📦 의존성 설치는 디스크 공간 부족으로 보류됨');
        console.log('🎯 Phase 7에서 완전한 구현 예정');
    } else {
        console.log('⚠️  일부 파일이 누락되었습니다');
    }
    
    console.log('\n📋 다음 단계:');
    console.log('1. 디스크 공간 확보 후 npm install 실행');
    console.log('2. npm run dev로 개발 서버 시작');
    console.log('3. Phase 7에서 실제 UI 구현');
    
    return allFilesExist;
}

if (require.main === module) {
    const success = checkFrontendSetup();
    process.exit(success ? 0 : 1);
}

module.exports = { checkFrontendSetup };