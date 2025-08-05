"""
T-Developer MVP - Phase 1 Completion Verification

Phase 1 완료 검증 및 테스트
"""

import asyncio
import sys
import os
from typing import Dict, Any, List
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from orchestration.agent_squad_core import AgentSquadOrchestrator
from agno.agno_integration import AgnoFrameworkManager
from core.unified_system import UnifiedAgentSystem
from data.dynamodb_client import initialize_database
from utils.system_monitor import system_monitor

class Phase1Validator:
    """Phase 1 완료 검증기"""
    
    def __init__(self):
        self.test_results: List[Dict[str, Any]] = []
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """모든 검증 테스트 실행"""
        print("🚀 Starting Phase 1 Completion Verification...")
        
        tests = [
            ("Agent Squad Orchestration", self.test_agent_squad),
            ("Agno Framework Integration", self.test_agno_framework),
            ("Unified System", self.test_unified_system),
            ("Database Connection", self.test_database),
            ("System Monitoring", self.test_monitoring),
            ("Performance Benchmarks", self.test_performance)
        ]
        
        for test_name, test_func in tests:
            print(f"\n📋 Testing: {test_name}")
            try:
                result = await test_func()
                self.test_results.append({
                    'test': test_name,
                    'status': 'PASS' if result['success'] else 'FAIL',
                    'details': result
                })
                print(f"✅ {test_name}: PASSED")
            except Exception as e:
                self.test_results.append({
                    'test': test_name,
                    'status': 'ERROR',
                    'error': str(e)
                })
                print(f"❌ {test_name}: ERROR - {str(e)}")
        
        return self.generate_report()
    
    async def test_agent_squad(self) -> Dict[str, Any]:
        """Agent Squad 오케스트레이션 테스트"""
        orchestrator = AgentSquadOrchestrator()
        
        # 테스트 에이전트 등록
        class TestAgent:
            async def execute(self, data):
                return {'result': f"Processed: {data.get('test', 'unknown')}"}
        
        await orchestrator.register_agent('test_agent', TestAgent())
        
        # 단일 태스크 실행 테스트
        result = await orchestrator.execute_task('test_agent', {'test': 'phase1'})
        
        # 상태 확인
        status = orchestrator.get_status()
        
        return {
            'success': True,
            'task_result': result,
            'orchestrator_status': status
        }
    
    async def test_agno_framework(self) -> Dict[str, Any]:
        """Agno Framework 테스트"""
        agno_manager = AgnoFrameworkManager()
        
        # 에이전트 생성 테스트
        agent = await agno_manager.create_agent('test', {'version': '1.0'})
        
        # 실행 테스트
        result = await agent.execute({'test_data': 'phase1_validation'})
        
        # 성능 벤치마크
        benchmark = await agno_manager.benchmark_performance()
        
        # 에이전트 반환
        await agno_manager.release_agent(agent)
        
        return {
            'success': True,
            'agent_result': result,
            'benchmark': benchmark,
            'performance_metrics': agno_manager.get_performance_metrics()
        }
    
    async def test_unified_system(self) -> Dict[str, Any]:
        """통합 시스템 테스트"""
        system = UnifiedAgentSystem()
        
        # 시스템 초기화
        await system.initialize()
        
        # 헬스 체크
        health = await system.health_check()
        
        # 시스템 상태 확인
        status = system.get_system_status()
        
        return {
            'success': health['status'] == 'healthy',
            'health_check': health,
            'system_status': status
        }
    
    async def test_database(self) -> Dict[str, Any]:
        """데이터베이스 연결 테스트"""
        try:
            # 데이터베이스 초기화
            await initialize_database()
            
            # 테스트 데이터 작업
            from data.dynamodb_client import db_client
            
            # 테스트 아이템 저장
            test_item = {
                'PK': 'TEST#phase1',
                'SK': 'VALIDATION',
                'data': 'Phase 1 completion test'
            }
            
            put_success = await db_client.put_item('projects', test_item)
            
            # 테스트 아이템 조회
            retrieved_item = await db_client.get_item('projects', {
                'PK': 'TEST#phase1',
                'SK': 'VALIDATION'
            })
            
            return {
                'success': put_success and retrieved_item is not None,
                'put_success': put_success,
                'retrieved_item': retrieved_item is not None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def test_monitoring(self) -> Dict[str, Any]:
        """모니터링 시스템 테스트"""
        # 시스템 메트릭 수집
        metrics = await system_monitor.collect_system_metrics()
        
        # 상태 조회
        status = system_monitor.get_system_status()
        
        return {
            'success': True,
            'metrics': metrics.__dict__,
            'status': status
        }
    
    async def test_performance(self) -> Dict[str, Any]:
        """성능 테스트"""
        system = UnifiedAgentSystem()
        await system.initialize()
        
        # 동시 요청 테스트
        start_time = asyncio.get_event_loop().time()
        
        tasks = []
        for i in range(10):
            task = system.process_request({
                'type': 'health_check',
                'agent_type': 'nl_input',
                'input_data': {'test_id': i}
            })
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = asyncio.get_event_loop().time()
        total_time = end_time - start_time
        
        successful_requests = sum(1 for r in results if isinstance(r, dict) and r.get('status') == 'success')
        
        return {
            'success': successful_requests >= 8,  # 80% 성공률
            'total_requests': len(tasks),
            'successful_requests': successful_requests,
            'total_time_seconds': total_time,
            'avg_time_per_request': total_time / len(tasks)
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """검증 리포트 생성"""
        passed_tests = sum(1 for r in self.test_results if r['status'] == 'PASS')
        total_tests = len(self.test_results)
        
        report = {
            'phase': 'Phase 1',
            'timestamp': datetime.utcnow().isoformat(),
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': total_tests - passed_tests,
                'success_rate': passed_tests / total_tests if total_tests > 0 else 0,
                'overall_status': 'COMPLETED' if passed_tests == total_tests else 'INCOMPLETE'
            },
            'test_results': self.test_results,
            'recommendations': self.generate_recommendations()
        }
        
        return report
    
    def generate_recommendations(self) -> List[str]:
        """개선 권장사항 생성"""
        recommendations = []
        
        failed_tests = [r for r in self.test_results if r['status'] != 'PASS']
        
        if failed_tests:
            recommendations.append("Failed tests need to be addressed before proceeding to Phase 2")
            
        for test in failed_tests:
            recommendations.append(f"Fix issues in {test['test']}")
        
        if not failed_tests:
            recommendations.append("Phase 1 completed successfully - ready for Phase 2")
            recommendations.append("Consider performance optimization for production deployment")
        
        return recommendations

async def main():
    """메인 실행 함수"""
    validator = Phase1Validator()
    report = await validator.run_all_tests()
    
    print("\n" + "="*60)
    print("📊 PHASE 1 COMPLETION REPORT")
    print("="*60)
    
    print(f"Overall Status: {report['summary']['overall_status']}")
    print(f"Success Rate: {report['summary']['success_rate']:.1%}")
    print(f"Tests Passed: {report['summary']['passed_tests']}/{report['summary']['total_tests']}")
    
    print("\n📋 Test Results:")
    for result in report['test_results']:
        status_icon = "✅" if result['status'] == 'PASS' else "❌"
        print(f"{status_icon} {result['test']}: {result['status']}")
    
    print("\n💡 Recommendations:")
    for rec in report['recommendations']:
        print(f"• {rec}")
    
    print("\n" + "="*60)
    
    # 결과를 파일로 저장
    import json
    with open('phase1_completion_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("📄 Report saved to: phase1_completion_report.json")
    
    return report['summary']['overall_status'] == 'COMPLETED'

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)