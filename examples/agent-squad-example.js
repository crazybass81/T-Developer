#!/usr/bin/env node
// examples/agent-squad-example.js
// Agent Squad 사용 예제

const { AgentSquad } = require('agent-squad');

async function createTDeveloperAgentSquad() {
    console.log('🚀 T-Developer Agent Squad 예제 시작...\n');
    
    try {
        // Agent Squad 생성
        const squad = new AgentSquad({
            name: 'T-Developer-Squad',
            description: 'Multi-agent system for T-Developer project'
        });
        
        console.log('✅ Agent Squad 생성 완료');
        console.log(`   - 이름: ${squad.name}`);
        console.log(`   - 설명: ${squad.description}\n`);
        
        // 에이전트 추가 예제 (실제 구현은 Phase 3에서)
        console.log('📋 계획된 에이전트들:');
        const plannedAgents = [
            'NL-Input Agent - 자연어 입력 처리',
            'UI-Selection Agent - UI 프레임워크 선택',
            'Parsing Agent - 코드 파싱 및 분석',
            'Component-Decision Agent - 컴포넌트 결정',
            'Matching-Rate Agent - 매칭률 계산',
            'Search Agent - 컴포넌트 검색',
            'Generation Agent - 코드 생성',
            'Assembly Agent - 서비스 조립',
            'Download Agent - 패키지 다운로드'
        ];
        
        plannedAgents.forEach((agent, index) => {
            console.log(`   ${index + 1}. ${agent}`);
        });
        
        console.log('\n🎯 다음 단계: Phase 3에서 실제 에이전트 구현');
        
        return squad;
        
    } catch (error) {
        console.error('❌ Agent Squad 예제 실행 실패:', error);
        throw error;
    }
}

// 실행
if (require.main === module) {
    createTDeveloperAgentSquad()
        .then(() => {
            console.log('\n✅ Agent Squad 예제 완료!');
        })
        .catch((error) => {
            console.error('\n❌ 예제 실행 실패:', error.message);
            process.exit(1);
        });
}

module.exports = { createTDeveloperAgentSquad };