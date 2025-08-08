#!/usr/bin/env python3
"""
End-to-End Test Scenarios for T-Developer MVP
실제 사용자 워크플로우를 검증하는 E2E 테스트
"""

import asyncio
import pytest
import httpx
import json
import zipfile
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, Any, List
import time
from datetime import datetime
import os

# 테스트 설정
BASE_URL = "http://localhost:8000"
TIMEOUT = 60  # 60초 타임아웃


class E2ETestRunner:
    """E2E 테스트 실행기"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=TIMEOUT)
        self.test_results = []
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """모든 E2E 테스트 실행"""
        test_scenarios = [
            ("Health Check", self.test_health_check),
            ("Framework Status", self.test_framework_status),
            ("Simple Todo App", self.test_simple_todo_app),
            ("Blog Website", self.test_blog_website),
            ("Dashboard App", self.test_dashboard_app),
            ("Complex E-commerce", self.test_complex_ecommerce),
            ("Project Preview", self.test_project_preview),
            ("Bedrock Integration", self.test_bedrock_integration),
            ("Performance Benchmark", self.test_performance_benchmark),
            ("Error Handling", self.test_error_handling)
        ]
        
        total_start_time = datetime.now()
        passed_tests = 0
        failed_tests = 0
        
        print("🚀 T-Developer MVP E2E Test Suite Starting...")
        print("=" * 60)
        
        for test_name, test_func in test_scenarios:
            print(f"\n🧪 Running: {test_name}")
            start_time = time.time()
            
            try:
                result = await test_func()
                execution_time = time.time() - start_time
                
                if result.get("success", False):
                    print(f"✅ {test_name}: PASSED ({execution_time:.2f}s)")
                    passed_tests += 1
                else:
                    print(f"❌ {test_name}: FAILED ({execution_time:.2f}s)")
                    print(f"   Error: {result.get('error', 'Unknown error')}")
                    failed_tests += 1
                
                self.test_results.append({
                    "test_name": test_name,
                    "success": result.get("success", False),
                    "execution_time": execution_time,
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                execution_time = time.time() - start_time
                print(f"❌ {test_name}: FAILED ({execution_time:.2f}s)")
                print(f"   Exception: {str(e)}")
                failed_tests += 1
                
                self.test_results.append({
                    "test_name": test_name,
                    "success": False,
                    "execution_time": execution_time,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        total_execution_time = (datetime.now() - total_start_time).total_seconds()
        
        # 결과 요약
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {len(test_scenarios)}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {(passed_tests/len(test_scenarios)*100):.1f}%")
        print(f"⏱️  Total Time: {total_execution_time:.2f}s")
        
        return {
            "total_tests": len(test_scenarios),
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": passed_tests / len(test_scenarios) * 100,
            "total_execution_time": total_execution_time,
            "test_results": self.test_results,
            "overall_success": failed_tests == 0
        }
    
    async def test_health_check(self) -> Dict[str, Any]:
        """서버 헬스 체크 테스트"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            
            if response.status_code != 200:
                return {"success": False, "error": f"Health check failed: {response.status_code}"}
            
            data = response.json()
            expected_fields = ["status", "timestamp", "service"]
            
            for field in expected_fields:
                if field not in data:
                    return {"success": False, "error": f"Missing field in health response: {field}"}
            
            return {"success": True, "data": data}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_framework_status(self) -> Dict[str, Any]:
        """3대 프레임워크 상태 확인 테스트"""
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/agents")
            
            if response.status_code != 200:
                return {"success": False, "error": f"Agent status failed: {response.status_code}"}
            
            data = response.json()
            
            # 9-Agent 확인
            if data.get("total", 0) < 9:
                return {"success": False, "error": f"Expected 9 agents, got {data.get('total', 0)}"}
            
            # 3대 프레임워크 확인
            frameworks = data.get("frameworks", {})
            expected_frameworks = ["aws_agent_squad", "agno_framework", "aws_bedrock_agentcore"]
            
            for fw in expected_frameworks:
                if fw not in frameworks:
                    return {"success": False, "error": f"Framework {fw} not found"}
            
            return {
                "success": True,
                "agent_count": data.get("total"),
                "frameworks": list(frameworks.keys()),
                "bedrock_available": data.get("bedrock_integration", False)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_simple_todo_app(self) -> Dict[str, Any]:
        """간단한 Todo 앱 생성 테스트"""
        return await self._test_project_generation(
            user_input="Create a simple Todo app with React",
            project_type="react",
            features=["todo"],
            expected_files=["package.json", "src/App.js", "src/index.js", "public/index.html", "README.md"],
            test_name="Simple Todo App"
        )
    
    async def test_blog_website(self) -> Dict[str, Any]:
        """블로그 웹사이트 생성 테스트"""
        return await self._test_project_generation(
            user_input="Create a blog website with React and routing",
            project_type="react",
            features=["routing", "blog"],
            expected_files=["package.json", "src/App.js", "src/index.js"],
            test_name="Blog Website"
        )
    
    async def test_dashboard_app(self) -> Dict[str, Any]:
        """대시보드 앱 생성 테스트"""
        return await self._test_project_generation(
            user_input="Create a admin dashboard with charts and data visualization",
            project_type="react",
            features=["dashboard", "charts"],
            expected_files=["package.json", "src/App.js"],
            test_name="Dashboard App"
        )
    
    async def test_complex_ecommerce(self) -> Dict[str, Any]:
        """복잡한 이커머스 앱 테스트"""
        return await self._test_project_generation(
            user_input="Create an e-commerce website with React, routing, state management, and shopping cart",
            project_type="react",
            features=["routing", "state-management", "ecommerce", "cart"],
            expected_files=["package.json", "src/App.js"],
            test_name="E-commerce App",
            timeout=120  # 복잡한 프로젝트는 더 긴 시간 필요
        )
    
    async def _test_project_generation(
        self, 
        user_input: str, 
        project_type: str, 
        features: List[str],
        expected_files: List[str],
        test_name: str,
        timeout: int = 60
    ) -> Dict[str, Any]:
        """프로젝트 생성 테스트 헬퍼"""
        try:
            # 1. 프로젝트 생성 요청
            payload = {
                "user_input": user_input,
                "project_type": project_type,
                "features": features
            }
            
            start_time = time.time()
            response = await self.client.post(
                f"{self.base_url}/api/v1/generate",
                json=payload,
                timeout=timeout
            )
            generation_time = time.time() - start_time
            
            if response.status_code != 200:
                return {"success": False, "error": f"Generation failed: {response.status_code}"}
            
            data = response.json()
            
            if not data.get("success"):
                return {"success": False, "error": f"Generation unsuccessful: {data.get('message')}"}
            
            project_id = data.get("project_id")
            download_url = data.get("download_url")
            
            if not project_id or not download_url:
                return {"success": False, "error": "Missing project_id or download_url"}
            
            # 2. 프로젝트 다운로드
            download_response = await self.client.get(f"{self.base_url}{download_url}")
            
            if download_response.status_code != 200:
                return {"success": False, "error": f"Download failed: {download_response.status_code}"}
            
            # 3. ZIP 파일 검증
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
                temp_zip.write(download_response.content)
                temp_zip_path = temp_zip.name
            
            try:
                validation_result = await self._validate_project_zip(temp_zip_path, expected_files)
                
                if not validation_result["success"]:
                    return validation_result
                
                return {
                    "success": True,
                    "project_id": project_id,
                    "generation_time": generation_time,
                    "zip_size_mb": len(download_response.content) / (1024 * 1024),
                    "file_count": validation_result["file_count"],
                    "validated_files": validation_result["found_files"],
                    "bedrock_enhanced": data.get("bedrock_enhanced", False),
                    "stats": data.get("stats", {})
                }
                
            finally:
                os.unlink(temp_zip_path)
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _validate_project_zip(self, zip_path: str, expected_files: List[str]) -> Dict[str, Any]:
        """ZIP 파일 내용 검증"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                file_list = zipf.namelist()
                
                # 예상 파일들이 존재하는지 확인
                found_files = []
                missing_files = []
                
                for expected_file in expected_files:
                    # 프로젝트 폴더 내에서 파일 찾기
                    file_found = any(
                        expected_file in file_path 
                        for file_path in file_list
                    )
                    
                    if file_found:
                        found_files.append(expected_file)
                    else:
                        missing_files.append(expected_file)
                
                # package.json 내용 검증
                package_json_found = False
                for file_path in file_list:
                    if file_path.endswith('package.json'):
                        package_json_content = zipf.read(file_path).decode('utf-8')
                        try:
                            package_data = json.loads(package_json_content)
                            
                            # 필수 필드 확인
                            required_fields = ["name", "version", "dependencies", "scripts"]
                            for field in required_fields:
                                if field not in package_data:
                                    return {"success": False, "error": f"package.json missing field: {field}"}
                            
                            package_json_found = True
                            break
                        except json.JSONDecodeError:
                            return {"success": False, "error": "Invalid package.json format"}
                
                if not package_json_found:
                    return {"success": False, "error": "package.json not found"}
                
                if missing_files:
                    return {
                        "success": False, 
                        "error": f"Missing expected files: {missing_files}",
                        "found_files": found_files,
                        "all_files": file_list
                    }
                
                return {
                    "success": True,
                    "file_count": len(file_list),
                    "found_files": found_files,
                    "all_files": file_list[:10]  # 처음 10개 파일만 표시
                }
                
        except Exception as e:
            return {"success": False, "error": f"ZIP validation error: {str(e)}"}
    
    async def test_project_preview(self) -> Dict[str, Any]:
        """프로젝트 미리보기 기능 테스트"""
        try:
            # 먼저 프로젝트 생성
            payload = {
                "user_input": "Create a simple React app",
                "project_type": "react"
            }
            
            response = await self.client.post(f"{self.base_url}/api/v1/generate", json=payload)
            
            if response.status_code != 200:
                return {"success": False, "error": "Failed to generate project for preview test"}
            
            data = response.json()
            project_id = data.get("project_id")
            
            if not project_id:
                return {"success": False, "error": "No project_id returned"}
            
            # 미리보기 요청
            preview_response = await self.client.get(f"{self.base_url}/api/v1/preview/{project_id}")
            
            if preview_response.status_code != 200:
                return {"success": False, "error": f"Preview failed: {preview_response.status_code}"}
            
            preview_data = preview_response.json()
            
            # 미리보기 데이터 검증
            required_fields = ["project_id", "file_structure", "file_contents", "stats"]
            for field in required_fields:
                if field not in preview_data:
                    return {"success": False, "error": f"Missing preview field: {field}"}
            
            return {
                "success": True,
                "project_id": project_id,
                "file_count": len(preview_data["file_structure"]),
                "preview_files": len(preview_data["file_contents"]),
                "stats": preview_data["stats"]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_bedrock_integration(self) -> Dict[str, Any]:
        """Bedrock AgentCore 통합 테스트"""
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/bedrock/status")
            
            if response.status_code != 200:
                return {"success": False, "error": f"Bedrock status check failed: {response.status_code}"}
            
            data = response.json()
            
            return {
                "success": True,
                "bedrock_available": data.get("available", False),
                "integration_status": data.get("integration_status", {}),
                "framework": data.get("framework", "Unknown")
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_performance_benchmark(self) -> Dict[str, Any]:
        """성능 벤치마크 테스트"""
        try:
            # 간단한 프로젝트로 성능 측정
            payload = {
                "user_input": "Create a simple React component",
                "project_type": "react"
            }
            
            # 3번 실행하여 평균 성능 측정
            execution_times = []
            
            for i in range(3):
                start_time = time.time()
                
                response = await self.client.post(f"{self.base_url}/api/v1/generate", json=payload)
                
                if response.status_code != 200:
                    return {"success": False, "error": f"Benchmark test {i+1} failed"}
                
                execution_time = time.time() - start_time
                execution_times.append(execution_time)
            
            avg_time = sum(execution_times) / len(execution_times)
            
            # 성능 기준: 30초 이내
            performance_target = 30.0
            performance_passed = avg_time <= performance_target
            
            return {
                "success": performance_passed,
                "avg_execution_time": avg_time,
                "execution_times": execution_times,
                "performance_target": performance_target,
                "performance_passed": performance_passed,
                "error": None if performance_passed else f"Performance target missed: {avg_time:.2f}s > {performance_target}s"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_error_handling(self) -> Dict[str, Any]:
        """에러 처리 테스트"""
        try:
            test_cases = [
                # 빈 입력
                {"user_input": "", "expected_status": 400},
                # 너무 긴 입력
                {"user_input": "x" * 3000, "expected_status": 400},
                # 지원되지 않는 프로젝트 타입
                {"user_input": "Create an app", "project_type": "unsupported", "expected_status": 400}
            ]
            
            passed_cases = 0
            
            for i, test_case in enumerate(test_cases):
                response = await self.client.post(f"{self.base_url}/api/v1/generate", json=test_case)
                
                expected_status = test_case["expected_status"]
                if response.status_code == expected_status:
                    passed_cases += 1
                else:
                    return {
                        "success": False,
                        "error": f"Error handling test {i+1} failed: expected {expected_status}, got {response.status_code}"
                    }
            
            return {
                "success": True,
                "test_cases": len(test_cases),
                "passed_cases": passed_cases
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def cleanup(self):
        """테스트 정리"""
        await self.client.aclose()
    
    def generate_report(self, output_path: str = None):
        """테스트 결과 보고서 생성"""
        if not output_path:
            output_path = f"e2e_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report_data = {
            "test_suite": "T-Developer MVP E2E Tests",
            "execution_time": datetime.now().isoformat(),
            "results": self.test_results,
            "summary": {
                "total_tests": len(self.test_results),
                "passed": sum(1 for r in self.test_results if r.get("success", False)),
                "failed": sum(1 for r in self.test_results if not r.get("success", False))
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"📋 Test report saved to: {output_path}")
        return output_path


async def run_e2e_tests():
    """E2E 테스트 실행 메인 함수"""
    runner = E2ETestRunner()
    
    try:
        results = await runner.run_all_tests()
        
        # 보고서 생성
        report_path = runner.generate_report()
        
        # 결과에 따른 종료 코드
        if results["overall_success"]:
            print("\n🎉 All E2E tests passed!")
            return 0
        else:
            print(f"\n💥 {results['failed']} test(s) failed!")
            return 1
            
    except Exception as e:
        print(f"\n❌ E2E test execution failed: {e}")
        return 1
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(run_e2e_tests())
    sys.exit(exit_code)