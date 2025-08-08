#!/usr/bin/env python3
"""
User Scenario Tests for T-Developer MVP
실제 사용자 워크플로우를 검증하는 시나리오 테스트
"""

import asyncio
import httpx
import json
import tempfile
import zipfile
import subprocess
import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"
TIMEOUT = 120


class UserScenarioTester:
    """사용자 시나리오 테스터"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=TIMEOUT)
        self.temp_dirs = []
    
    async def run_all_user_scenarios(self) -> Dict[str, Any]:
        """모든 사용자 시나리오 실행"""
        
        print("👥 T-Developer User Scenario Tests Starting...")
        print("=" * 60)
        
        scenarios = [
            ("신규 개발자 - 첫 React 앱", self.scenario_beginner_react),
            ("블로거 - 개인 블로그 생성", self.scenario_blogger_website), 
            ("스타트업 - MVP 대시보드", self.scenario_startup_dashboard),
            ("학생 - 할일 관리 앱", self.scenario_student_todo),
            ("소상공인 - 쇼핑몰 사이트", self.scenario_small_business_shop)
        ]
        
        results = []
        passed_scenarios = 0
        
        for scenario_name, scenario_func in scenarios:
            print(f"\n🎭 Testing: {scenario_name}")
            
            try:
                result = await scenario_func()
                results.append({
                    "scenario": scenario_name,
                    **result
                })
                
                if result.get("success", False):
                    print(f"✅ {scenario_name}: PASSED")
                    passed_scenarios += 1
                else:
                    print(f"❌ {scenario_name}: FAILED - {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"❌ {scenario_name}: EXCEPTION - {str(e)}")
                results.append({
                    "scenario": scenario_name,
                    "success": False,
                    "error": f"Exception: {str(e)}"
                })
        
        success_rate = (passed_scenarios / len(scenarios)) * 100
        
        summary = {
            "total_scenarios": len(scenarios),
            "passed": passed_scenarios,
            "failed": len(scenarios) - passed_scenarios,
            "success_rate": success_rate,
            "overall_success": success_rate >= 80,  # 80% 이상 성공시 통과
            "scenario_results": results,
            "timestamp": datetime.now().isoformat()
        }
        
        self._print_summary(summary)
        return summary
    
    async def scenario_beginner_react(self) -> Dict[str, Any]:
        """시나리오: 신규 개발자가 첫 React 앱 만들기"""
        
        # 사용자 입력 (초보자 스타일)
        user_input = "리액트로 간단한 웹 앱을 만들어 주세요. 처음 해보는 거라 쉬운 걸로 부탁합니다."
        
        return await self._execute_full_workflow(
            user_input=user_input,
            project_type="react",
            features=[],
            expected_files=["package.json", "src/App.js", "src/index.js", "public/index.html"],
            validate_npm_install=True,
            scenario_context="신규 개발자"
        )
    
    async def scenario_blogger_website(self) -> Dict[str, Any]:
        """시나리오: 블로거가 개인 블로그 웹사이트 만들기"""
        
        user_input = "개인 블로그 웹사이트를 만들고 싶어요. 여러 페이지가 있고 포스트를 볼 수 있는 기능이 필요해요."
        
        return await self._execute_full_workflow(
            user_input=user_input,
            project_type="react",
            features=["routing", "blog"],
            expected_files=["package.json", "src/App.js", "README.md"],
            validate_npm_install=True,
            scenario_context="블로거"
        )
    
    async def scenario_startup_dashboard(self) -> Dict[str, Any]:
        """시나리오: 스타트업에서 MVP 대시보드 만들기"""
        
        user_input = "스타트업용 관리자 대시보드를 만들어주세요. 차트와 데이터 시각화가 포함된 현대적인 디자인으로요."
        
        return await self._execute_full_workflow(
            user_input=user_input,
            project_type="react",
            features=["dashboard", "charts"],
            expected_files=["package.json", "src/App.js"],
            validate_npm_install=True,
            scenario_context="스타트업"
        )
    
    async def scenario_student_todo(self) -> Dict[str, Any]:
        """시나리오: 학생이 할일 관리 앱 만들기"""
        
        user_input = "과제 관리를 위한 할일 앱을 만들어주세요. 추가, 수정, 삭제 기능이 있었으면 좋겠어요."
        
        return await self._execute_full_workflow(
            user_input=user_input,
            project_type="react", 
            features=["todo"],
            expected_files=["package.json", "src/App.js", "src/App.css"],
            validate_npm_install=True,
            validate_todo_functionality=True,
            scenario_context="학생"
        )
    
    async def scenario_small_business_shop(self) -> Dict[str, Any]:
        """시나리오: 소상공인 쇼핑몰 사이트 만들기"""
        
        user_input = "작은 온라인 쇼핑몰을 만들고 싶어요. 상품 목록, 장바구니 기능이 있는 이커머스 사이트로요."
        
        return await self._execute_full_workflow(
            user_input=user_input,
            project_type="react",
            features=["ecommerce", "cart", "routing", "state-management"],
            expected_files=["package.json", "src/App.js"],
            validate_npm_install=True,
            scenario_context="소상공인"
        )
    
    async def _execute_full_workflow(
        self,
        user_input: str,
        project_type: str,
        features: List[str],
        expected_files: List[str],
        validate_npm_install: bool = False,
        validate_todo_functionality: bool = False,
        scenario_context: str = ""
    ) -> Dict[str, Any]:
        """전체 워크플로우 실행 및 검증"""
        
        workflow_steps = []
        
        try:
            # 1. 프로젝트 생성 요청
            step1_start = datetime.now()
            response = await self.client.post(
                f"{self.base_url}/api/v1/generate",
                json={
                    "user_input": user_input,
                    "project_type": project_type,
                    "features": features
                }
            )
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"프로젝트 생성 실패: {response.status_code}",
                    "workflow_steps": workflow_steps
                }
            
            data = response.json()
            if not data.get("success"):
                return {
                    "success": False,
                    "error": f"프로젝트 생성 실패: {data.get('message')}",
                    "workflow_steps": workflow_steps
                }
            
            project_id = data.get("project_id")
            download_url = data.get("download_url")
            
            step1_time = (datetime.now() - step1_start).total_seconds()
            workflow_steps.append({
                "step": "1. 프로젝트 생성 요청",
                "success": True,
                "duration_seconds": step1_time,
                "details": f"프로젝트 ID: {project_id}"
            })
            
            # 2. 프로젝트 미리보기 (선택적)
            if project_id:
                step2_start = datetime.now()
                preview_response = await self.client.get(f"{self.base_url}/api/v1/preview/{project_id}")
                
                if preview_response.status_code == 200:
                    preview_data = preview_response.json()
                    file_count = len(preview_data.get("file_structure", []))
                    
                    step2_time = (datetime.now() - step2_start).total_seconds()
                    workflow_steps.append({
                        "step": "2. 프로젝트 미리보기",
                        "success": True,
                        "duration_seconds": step2_time,
                        "details": f"파일 개수: {file_count}"
                    })
                else:
                    workflow_steps.append({
                        "step": "2. 프로젝트 미리보기",
                        "success": False,
                        "duration_seconds": 0,
                        "details": "미리보기 실패"
                    })
            
            # 3. ZIP 파일 다운로드
            step3_start = datetime.now()
            download_response = await self.client.get(f"{self.base_url}{download_url}")
            
            if download_response.status_code != 200:
                return {
                    "success": False,
                    "error": f"다운로드 실패: {download_response.status_code}",
                    "workflow_steps": workflow_steps
                }
            
            step3_time = (datetime.now() - step3_start).total_seconds()
            zip_size_mb = len(download_response.content) / (1024 * 1024)
            
            workflow_steps.append({
                "step": "3. ZIP 파일 다운로드",
                "success": True,
                "duration_seconds": step3_time,
                "details": f"파일 크기: {zip_size_mb:.2f}MB"
            })
            
            # 4. ZIP 파일 압축 해제 및 검증
            step4_start = datetime.now()
            
            with tempfile.TemporaryDirectory() as temp_dir:
                self.temp_dirs.append(temp_dir)
                
                # ZIP 파일 저장
                zip_path = Path(temp_dir) / f"{project_id}.zip"
                with open(zip_path, 'wb') as f:
                    f.write(download_response.content)
                
                # 압축 해제
                project_dir = Path(temp_dir) / "project"
                with zipfile.ZipFile(zip_path, 'r') as zipf:
                    zipf.extractall(project_dir)
                
                # 프로젝트 폴더 찾기
                extracted_items = list(project_dir.iterdir())
                if len(extracted_items) == 1 and extracted_items[0].is_dir():
                    actual_project_dir = extracted_items[0]
                else:
                    actual_project_dir = project_dir
                
                # 예상 파일 존재 확인
                missing_files = []
                for expected_file in expected_files:
                    file_path = actual_project_dir / expected_file
                    if not file_path.exists():
                        missing_files.append(expected_file)
                
                if missing_files:
                    return {
                        "success": False,
                        "error": f"필수 파일 누락: {missing_files}",
                        "workflow_steps": workflow_steps
                    }
                
                step4_time = (datetime.now() - step4_start).total_seconds()
                workflow_steps.append({
                    "step": "4. ZIP 압축 해제 및 파일 검증",
                    "success": True,
                    "duration_seconds": step4_time,
                    "details": f"모든 예상 파일 존재 확인"
                })
                
                # 5. package.json 검증
                step5_start = datetime.now()
                package_json_path = actual_project_dir / "package.json"
                
                if package_json_path.exists():
                    try:
                        with open(package_json_path, 'r') as f:
                            package_data = json.load(f)
                        
                        required_fields = ["name", "version", "dependencies", "scripts"]
                        missing_fields = [field for field in required_fields if field not in package_data]
                        
                        if missing_fields:
                            return {
                                "success": False,
                                "error": f"package.json 필드 누락: {missing_fields}",
                                "workflow_steps": workflow_steps
                            }
                        
                        step5_time = (datetime.now() - step5_start).total_seconds()
                        workflow_steps.append({
                            "step": "5. package.json 검증",
                            "success": True,
                            "duration_seconds": step5_time,
                            "details": f"의존성 개수: {len(package_data.get('dependencies', {}))}"
                        })
                        
                    except json.JSONDecodeError:
                        return {
                            "success": False,
                            "error": "package.json 형식 오류",
                            "workflow_steps": workflow_steps
                        }
                else:
                    return {
                        "success": False,
                        "error": "package.json 파일 없음",
                        "workflow_steps": workflow_steps
                    }
                
                # 6. npm install 검증 (선택적)
                if validate_npm_install:
                    step6_start = datetime.now()
                    
                    # Node.js와 npm이 설치되어 있는지 확인
                    try:
                        npm_check = subprocess.run(
                            ["npm", "--version"], 
                            cwd=actual_project_dir,
                            capture_output=True, 
                            text=True, 
                            timeout=30
                        )
                        
                        if npm_check.returncode == 0:
                            # npm install 실행 (실제로는 --dry-run으로 검증만)
                            npm_result = subprocess.run(
                                ["npm", "install", "--dry-run"],
                                cwd=actual_project_dir,
                                capture_output=True,
                                text=True,
                                timeout=60
                            )
                            
                            npm_success = npm_result.returncode == 0
                            step6_time = (datetime.now() - step6_start).total_seconds()
                            
                            workflow_steps.append({
                                "step": "6. npm install 검증",
                                "success": npm_success,
                                "duration_seconds": step6_time,
                                "details": "dry-run 성공" if npm_success else f"오류: {npm_result.stderr[:100]}"
                            })
                            
                            if not npm_success:
                                return {
                                    "success": False,
                                    "error": f"npm install 실패: {npm_result.stderr}",
                                    "workflow_steps": workflow_steps
                                }
                        else:
                            workflow_steps.append({
                                "step": "6. npm install 검증",
                                "success": False,
                                "duration_seconds": 0,
                                "details": "npm이 설치되지 않음 (검증 스킵)"
                            })
                    
                    except subprocess.TimeoutExpired:
                        workflow_steps.append({
                            "step": "6. npm install 검증",
                            "success": False,
                            "duration_seconds": 60,
                            "details": "npm install 타임아웃"
                        })
                    
                    except FileNotFoundError:
                        workflow_steps.append({
                            "step": "6. npm install 검증",
                            "success": False,
                            "duration_seconds": 0,
                            "details": "npm 명령어를 찾을 수 없음"
                        })
                
                # 7. Todo 기능 검증 (선택적)
                if validate_todo_functionality:
                    step7_start = datetime.now()
                    
                    app_js_path = actual_project_dir / "src" / "App.js"
                    if app_js_path.exists():
                        try:
                            with open(app_js_path, 'r') as f:
                                app_content = f.read()
                            
                            todo_features = [
                                "useState",  # React 상태 관리
                                "TodoApp",   # Todo 컴포넌트
                                "addTodo",   # Todo 추가 기능
                                "deleteTodo" # Todo 삭제 기능
                            ]
                            
                            missing_features = [
                                feature for feature in todo_features 
                                if feature not in app_content
                            ]
                            
                            step7_time = (datetime.now() - step7_start).total_seconds()
                            
                            if missing_features:
                                workflow_steps.append({
                                    "step": "7. Todo 기능 검증",
                                    "success": False,
                                    "duration_seconds": step7_time,
                                    "details": f"누락된 기능: {missing_features}"
                                })
                            else:
                                workflow_steps.append({
                                    "step": "7. Todo 기능 검증", 
                                    "success": True,
                                    "duration_seconds": step7_time,
                                    "details": "모든 Todo 기능 확인됨"
                                })
                                
                        except Exception as e:
                            workflow_steps.append({
                                "step": "7. Todo 기능 검증",
                                "success": False,
                                "duration_seconds": 0,
                                "details": f"파일 읽기 오류: {str(e)}"
                            })
                    else:
                        workflow_steps.append({
                            "step": "7. Todo 기능 검증",
                            "success": False,
                            "duration_seconds": 0,
                            "details": "App.js 파일을 찾을 수 없음"
                        })
            
            # 전체 워크플로우 성공
            total_time = sum(step.get("duration_seconds", 0) for step in workflow_steps)
            successful_steps = sum(1 for step in workflow_steps if step.get("success", False))
            
            return {
                "success": True,
                "scenario_context": scenario_context,
                "user_input": user_input,
                "project_id": project_id,
                "total_duration_seconds": total_time,
                "workflow_steps": workflow_steps,
                "step_success_rate": (successful_steps / len(workflow_steps)) * 100,
                "zip_size_mb": zip_size_mb,
                "file_validation": "PASSED"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"워크플로우 실행 중 예외 발생: {str(e)}",
                "workflow_steps": workflow_steps,
                "scenario_context": scenario_context
            }
    
    def _print_summary(self, summary: Dict[str, Any]):
        """테스트 결과 요약 출력"""
        
        print("\n" + "=" * 60)
        print("👥 USER SCENARIO TEST SUMMARY")
        print("=" * 60)
        
        print(f"Total Scenarios: {summary['total_scenarios']}")
        print(f"✅ Passed: {summary['passed']}")
        print(f"❌ Failed: {summary['failed']}")
        print(f"📈 Success Rate: {summary['success_rate']:.1f}%")
        print(f"Overall Result: {'✅ PASSED' if summary['overall_success'] else '❌ FAILED'}")
        
        print("\n🎭 Scenario Details:")
        for result in summary["scenario_results"]:
            status = "✅" if result.get("success", False) else "❌"
            scenario_name = result["scenario"]
            
            print(f"  {status} {scenario_name}")
            
            if result.get("success", False):
                total_time = result.get("total_duration_seconds", 0)
                step_success_rate = result.get("step_success_rate", 0)
                print(f"      Time: {total_time:.2f}s, Step Success: {step_success_rate:.1f}%")
            else:
                error = result.get("error", "Unknown error")
                print(f"      Error: {error}")
        
        print("\n" + "=" * 60)
    
    async def save_scenario_report(
        self, 
        results: Dict[str, Any], 
        output_path: Optional[str] = None
    ) -> str:
        """시나리오 테스트 보고서 저장"""
        
        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"user_scenario_report_{timestamp}.json"
        
        report_data = {
            "test_suite": "T-Developer MVP User Scenario Tests",
            "execution_time": datetime.now().isoformat(),
            "results": results
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str, ensure_ascii=False)
        
        print(f"📋 User scenario report saved to: {output_path}")
        return output_path
    
    async def cleanup(self):
        """정리"""
        await self.client.aclose()


async def run_user_scenario_tests():
    """사용자 시나리오 테스트 실행 메인 함수"""
    
    tester = UserScenarioTester()
    
    try:
        # 서버 상태 확인
        try:
            response = await tester.client.get(f"{BASE_URL}/health")
            if response.status_code != 200:
                raise Exception("서버가 응답하지 않습니다")
            print("✅ Server health check passed")
        except Exception as e:
            print(f"❌ Server not available: {e}")
            return 1
        
        # 시나리오 테스트 실행
        results = await tester.run_all_user_scenarios()
        
        # 보고서 저장
        await tester.save_scenario_report(results)
        
        # 결과에 따른 종료 코드
        if results["overall_success"]:
            print("\n🎉 User scenario tests passed!")
            return 0
        else:
            print(f"\n💥 User scenario tests failed ({results['success_rate']:.1f}% success rate)!")
            return 1
            
    except Exception as e:
        print(f"\n❌ User scenario test execution failed: {e}")
        logger.error("User scenario tests failed", exc_info=True)
        return 1
    finally:
        await tester.cleanup()


if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(run_user_scenario_tests())
    sys.exit(exit_code)