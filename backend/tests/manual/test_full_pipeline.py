#!/usr/bin/env python3
"""
T-Developer Full Pipeline Integration Test
9개 에이전트의 완전한 통합 테스트
"""

import asyncio
import logging
import json
import time
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend/src'))

from orchestration.master_orchestrator import MasterOrchestrator, PipelineConfig
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PipelineIntegrationTest:
    """Complete pipeline integration test"""
    
    def __init__(self):
        self.orchestrator = None
        self.test_cases = [
            {
                "name": "Simple Todo App",
                "input": "React와 TypeScript로 할일 관리 앱을 만들어주세요. 할일 추가, 완료 표시, 삭제 기능이 필요합니다.",
                "expected_framework": "react",
                "expected_components": ["TodoList", "TodoItem", "AddTodo"]
            },
            {
                "name": "E-commerce API",
                "input": "FastAPI로 이커머스 REST API를 만들어주세요. 사용자 인증, 상품 목록, 장바구니, 주문 기능이 필요합니다.",
                "expected_framework": "fastapi",
                "expected_features": ["auth", "products", "cart", "orders"]
            },
            {
                "name": "Blog Platform",
                "input": "Vue.js로 블로그 플랫폼을 만들어주세요. 게시글 CRUD, 댓글, 카테고리, 검색 기능이 필요합니다.",
                "expected_framework": "vue",
                "expected_components": ["PostList", "PostDetail", "CommentSection"]
            }
        ]
    
    async def test_full_pipeline(self, test_case):
        """Test complete 9-agent pipeline"""
        
        print(f"\n{'='*80}")
        print(f"🧪 Testing: {test_case['name']}")
        print(f"{'='*80}")
        print(f"📝 Input: {test_case['input']}")
        print(f"{'='*80}\n")
        
        # Initialize orchestrator with monitoring
        config = PipelineConfig(
            enable_monitoring=True,
            enable_caching=False,  # Disable cache for testing
            debug_mode=True,
            timeout_seconds=120
        )
        
        self.orchestrator = MasterOrchestrator(config)
        
        try:
            start_time = time.time()
            
            # Execute full pipeline
            print("🚀 Starting 9-Agent Pipeline Execution...")
            print("-" * 60)
            
            result = await self.orchestrator.execute_pipeline(
                user_input=test_case['input'],
                context_data={
                    "test_mode": True,
                    "project_type": "web_app"
                }
            )
            
            execution_time = time.time() - start_time
            
            # Print results
            print("\n" + "="*60)
            print("📊 PIPELINE EXECUTION RESULTS")
            print("="*60)
            
            if result['success']:
                print(f"✅ Status: SUCCESS")
            else:
                print(f"❌ Status: FAILED")
                print(f"Error: {result.get('error', 'Unknown error')}")
            
            print(f"⏱️  Execution Time: {execution_time:.2f} seconds")
            print(f"🎯 Completion: {result.get('progress', 0)}%")
            
            # Print stage results
            if 'stage_results' in result:
                print("\n📈 Agent Execution Results:")
                print("-" * 60)
                
                agents = [
                    "nl_input", "ui_selection", "parser", 
                    "component_decision", "match_rate", "search",
                    "generation", "assembly", "download"
                ]
                
                for i, agent in enumerate(agents, 1):
                    if agent in result['stage_results']:
                        agent_result = result['stage_results'][agent]
                        status_icon = "✅" if agent_result.get('success', False) else "❌"
                        exec_time = agent_result.get('execution_time', 0)
                        
                        print(f"{i}. {status_icon} {agent.upper():20} - {exec_time:.2f}s")
                        
                        # Print key outputs
                        if agent == 'nl_input' and 'requirements' in agent_result:
                            print(f"   📋 Requirements: {', '.join(agent_result['requirements'][:3])}")
                        elif agent == 'ui_selection' and 'framework' in agent_result:
                            print(f"   🎨 Framework: {agent_result['framework']}")
                        elif agent == 'component_decision' and 'architecture' in agent_result:
                            print(f"   🏗️  Architecture: {agent_result['architecture']}")
                        elif agent == 'match_rate' and 'score' in agent_result:
                            print(f"   📊 Match Score: {agent_result['score']:.1f}%")
                        elif agent == 'generation' and 'files_generated' in agent_result:
                            print(f"   📁 Files Generated: {agent_result['files_generated']}")
                        elif agent == 'download' and 'download_url' in agent_result:
                            print(f"   📦 Download: {agent_result['download_url']}")
            
            # Validate results
            print("\n🔍 Validation Results:")
            print("-" * 60)
            
            validation_passed = True
            
            # Check if expected framework was selected
            if 'expected_framework' in test_case:
                ui_result = result.get('stage_results', {}).get('ui_selection', {})
                selected_framework = ui_result.get('framework', '').lower()
                
                if test_case['expected_framework'] in selected_framework:
                    print(f"✅ Framework Selection: {selected_framework} (Expected: {test_case['expected_framework']})")
                else:
                    print(f"❌ Framework Selection: {selected_framework} (Expected: {test_case['expected_framework']})")
                    validation_passed = False
            
            # Check if key components were identified
            if 'expected_components' in test_case:
                parser_result = result.get('stage_results', {}).get('parser', {})
                identified_components = parser_result.get('components', [])
                
                matched = sum(1 for comp in test_case['expected_components'] 
                             if any(comp.lower() in str(ic).lower() for ic in identified_components))
                
                print(f"✅ Components Identified: {matched}/{len(test_case['expected_components'])}")
            
            # Check if files were generated
            generation_result = result.get('stage_results', {}).get('generation', {})
            files_generated = generation_result.get('files_generated', 0)
            
            if files_generated > 0:
                print(f"✅ Code Generation: {files_generated} files generated")
            else:
                print(f"❌ Code Generation: No files generated")
                validation_passed = False
            
            # Performance metrics
            print("\n📊 Performance Metrics:")
            print("-" * 60)
            
            if 'performance_metrics' in result:
                metrics = result['performance_metrics']
                print(f"💾 Memory Usage: {metrics.get('memory_usage_mb', 0):.1f} MB")
                print(f"🔄 Cache Hit Rate: {metrics.get('cache_hit_rate', 0):.1%}")
                print(f"⚡ Parallel Execution: {metrics.get('parallel_agents', 0)} agents")
            
            # Final summary
            print("\n" + "="*60)
            if validation_passed and result['success']:
                print("🎉 TEST PASSED - Pipeline executed successfully!")
            else:
                print("⚠️  TEST FAILED - Check errors above")
            print("="*60)
            
            return result
            
        except Exception as e:
            logger.error(f"Pipeline test failed: {e}")
            print(f"\n❌ CRITICAL ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
        
        finally:
            if self.orchestrator:
                await self.orchestrator.cleanup()
    
    async def run_all_tests(self):
        """Run all test cases"""
        
        print("\n" + "🚀"*40)
        print(" T-DEVELOPER 9-AGENT PIPELINE INTEGRATION TEST")
        print("🚀"*40)
        print(f"\nTest Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Test Cases: {len(self.test_cases)}")
        
        results = []
        
        for i, test_case in enumerate(self.test_cases, 1):
            print(f"\n\n{'='*80}")
            print(f"Test Case {i}/{len(self.test_cases)}")
            
            result = await self.test_full_pipeline(test_case)
            results.append({
                "test": test_case['name'],
                "success": result['success'],
                "execution_time": result.get('execution_time', 0)
            })
            
            # Brief pause between tests
            await asyncio.sleep(2)
        
        # Print final summary
        print("\n\n" + "="*80)
        print("📊 FINAL TEST SUMMARY")
        print("="*80)
        
        successful = sum(1 for r in results if r['success'])
        total = len(results)
        
        print(f"\n✅ Passed: {successful}/{total}")
        print(f"❌ Failed: {total - successful}/{total}")
        print(f"📈 Success Rate: {(successful/total)*100:.1f}%")
        
        print("\nDetailed Results:")
        for i, result in enumerate(results, 1):
            status = "✅" if result['success'] else "❌"
            print(f"  {i}. {status} {result['test']:30} - {result.get('execution_time', 0):.2f}s")
        
        print("\n" + "="*80)
        if successful == total:
            print("🎉 ALL TESTS PASSED - 9-Agent Pipeline Working Perfectly!")
        else:
            print(f"⚠️  {total - successful} test(s) failed - Review logs above")
        print("="*80)

async def main():
    """Main test runner"""
    
    # Check if running in correct directory
    if not os.path.exists('backend/src/orchestration/master_orchestrator.py'):
        print("❌ Error: Please run this script from the T-DeveloperMVP root directory")
        return 1
    
    # Run integration tests
    tester = PipelineIntegrationTest()
    
    try:
        await tester.run_all_tests()
        return 0
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    print("\n🔧 Initializing T-Developer Pipeline Test Environment...")
    print("📍 Working Directory:", os.getcwd())
    print("🐍 Python Version:", sys.version.split()[0])
    print("-" * 60)
    
    # Run async main
    exit_code = asyncio.run(main())
    sys.exit(exit_code)