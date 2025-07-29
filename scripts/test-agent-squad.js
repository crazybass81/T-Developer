#!/usr/bin/env node
// scripts/test-agent-squad.js

async function testAgentSquad() {
    try {
        console.log('🔍 Agent Squad 설치 테스트 중...');
        
        // Agent Squad 임포트 테스트
        const { AgentSquad } = require('agent-squad');
        console.log('✅ Agent Squad 모듈 임포트 성공');
        
        // 간단한 에이전트 스쿼드 생성 테스트
        const squad = new AgentSquad({
            name: 'TestSquad',
            description: 'Test squad for installation verification'
        });
        
        console.log('✅ Agent Squad 인스턴스 생성 성공');
        console.log(`   - 스쿼드 이름: ${squad.name || 'TestSquad'}`);
        
        // 기본 기능 테스트
        if (typeof squad.addAgent === 'function') {
            console.log('✅ addAgent 메서드 확인됨');
        }
        
        console.log('\n🎉 Agent Squad가 정상적으로 설치되어 있습니다!');
        console.log(`📋 Node.js 버전: ${process.version}`);
        
        return true;
        
    } catch (error) {
        console.error('❌ Agent Squad 테스트 실패:', error.message);
        console.log('\n📋 문제 해결 방법:');
        console.log('1. Node.js v18 사용 확인: nvm use 18');
        console.log('2. 재설치: npm install agent-squad');
        console.log('3. 캐시 정리: npm cache clean --force');
        
        return false;
    }
}

// 실행
testAgentSquad().then(success => {
    process.exit(success ? 0 : 1);
});