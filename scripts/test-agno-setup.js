#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🔍 Testing Agno Framework setup...\n');

// 1. 설치 스크립트 확인
const installScript = path.join(__dirname, 'install-agno.sh');
if (fs.existsSync(installScript)) {
    console.log('✅ install-agno.sh exists');
} else {
    console.log('❌ install-agno.sh not found');
}

// 2. 설정 파일 확인
const configFile = path.join(__dirname, '../backend/src/config/agno_config.py');
if (fs.existsSync(configFile)) {
    console.log('✅ agno_config.py exists');
    
    // 설정 내용 확인
    const content = fs.readFileSync(configFile, 'utf8');
    const checks = [
        'AGNO_CONFIG',
        'instantiation_target_us',
        'memory_target_kb',
        'MonitoringConfig',
        'TracingConfig'
    ];
    
    checks.forEach(check => {
        if (content.includes(check)) {
            console.log(`✅ ${check} configured`);
        } else {
            console.log(`❌ ${check} missing`);
        }
    });
} else {
    console.log('❌ agno_config.py not found');
}

// 3. Python 환경 확인
try {
    const pythonVersion = execSync('python3 --version', { encoding: 'utf8' }).trim();
    console.log(`✅ Python available: ${pythonVersion}`);
} catch (error) {
    console.log('❌ Python 3 not available');
}

// 4. 가상환경 확인
const venvPath = path.join(__dirname, '../venv');
if (fs.existsSync(venvPath)) {
    console.log('✅ Python virtual environment exists');
} else {
    console.log('⚠️ Python virtual environment not found');
}

console.log('\n🎯 Agno Framework setup verification completed!');