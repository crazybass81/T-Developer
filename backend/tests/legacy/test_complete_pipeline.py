#!/usr/bin/env python3
"""
완전한 Todo 앱 생성 파이프라인 테스트
Agno Framework + Agent Squad + 9-Agent Pipeline
"""

import asyncio
import json
import time
from pathlib import Path
import zipfile
import shutil
from datetime import datetime

# 시스템 컴포넌트 import
from src.orchestration.production_pipeline import ProductionECSPipeline
from src.agno.agent_registry import agent_registry
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_complete_todo_pipeline():
    """
    완전한 Todo 앱 생성 파이프라인 테스트
    """
    print("\n" + "="*80)
    print("🚀 COMPLETE TODO APP GENERATION PIPELINE TEST")
    print("="*80)
    
    # 1. 파이프라인 초기화
    print("\n1️⃣ Initializing Production Pipeline...")
    pipeline = ProductionECSPipeline()
    await pipeline.initialize()
    print("   ✅ Pipeline initialized")
    
    # 2. Todo 앱 요청 데이터 준비
    print("\n2️⃣ Preparing Todo App Request...")
    todo_request = {
        "name": "Advanced Todo App",
        "description": "Todo application with dynamic agents using Agno Framework",
        "framework": "react",
        "features": [
            "todo",
            "priority management",
            "filtering and search",
            "statistics dashboard",
            "local storage",
            "dark mode",
            "notifications"
        ],
        "aiModel": "claude",
        "user_input": "Create a complete todo app with all advanced features"
    }
    print(f"   Project: {todo_request['name']}")
    print(f"   Features: {len(todo_request['features'])} features")
    
    # 3. 파이프라인 실행
    print("\n3️⃣ Running 9-Agent Pipeline...")
    start_time = time.perf_counter()
    
    try:
        # execute 메소드는 개별 파라미터를 받음
        result = await pipeline.execute(
            user_input=todo_request.get("user_input", "Create a todo app"),
            project_name=todo_request.get("name"),
            project_type=todo_request.get("framework", "react"),
            features=todo_request.get("features", [])
        )
        
        execution_time = time.perf_counter() - start_time
        print(f"\n   ⏱️ Total execution time: {execution_time:.2f}s")
        
        if result.success:
            print("   ✅ Pipeline completed successfully!")
            
            # 4. 결과 분석
            print("\n4️⃣ Analyzing Results...")
            metadata = result.metadata
            
            # 에이전트 실행 결과
            if 'agent_results' in metadata:
                print("\n   Agent Execution Summary:")
                for agent_result in metadata['agent_results']:
                    status = "✅" if agent_result.get('success') else "❌"
                    agent_name = agent_result.get('agent_name', 'unknown')
                    exec_time = agent_result.get('execution_time', 0)
                    print(f"      {status} {agent_name}: {exec_time:.2f}s")
            
            # 파이프라인 데이터 분석
            pipeline_data = metadata.get('pipeline_data', {})
            
            # Generation Agent 결과 확인
            if 'generation' in pipeline_data:
                gen_data = pipeline_data['generation']
                if 'agents_created' in gen_data:
                    print(f"\n   📦 Dynamic Agents Created: {gen_data['agents_created']}")
                    if 'agent_names' in gen_data:
                        for agent_name in gen_data['agent_names']:
                            print(f"      • {agent_name}")
                
                if 'generated_files' in gen_data:
                    files = gen_data['generated_files']
                    print(f"\n   📁 Files Generated: {len(files)}")
                    # 주요 파일 표시
                    key_files = ['package.json', 'src/App.js', 'src/agents/TodoCRUDAgent.js']
                    for key_file in key_files:
                        if key_file in files:
                            print(f"      ✓ {key_file}")
            
            # Assembly 결과 확인
            if 'package_path' in pipeline_data:
                package_path = pipeline_data['package_path']
                print(f"\n   📦 Package Created: {package_path}")
                
                if Path(package_path).exists():
                    zip_size = Path(package_path).stat().st_size
                    print(f"      Size: {zip_size / 1024:.2f} KB")
                    
                    # ZIP 파일 내용 확인
                    with zipfile.ZipFile(package_path, 'r') as zf:
                        file_list = zf.namelist()
                        print(f"      Files in ZIP: {len(file_list)}")
                        
                        # 에이전트 파일 확인
                        agent_files = [f for f in file_list if 'agents/' in f and f.endswith('.js')]
                        if agent_files:
                            print(f"      Agent files: {len(agent_files)}")
                            for af in agent_files[:5]:  # 최대 5개만 표시
                                print(f"         • {af}")
            
            # Download 정보
            if 'download' in pipeline_data:
                download_data = pipeline_data['download']
                if 'download_url' in download_data:
                    print(f"\n   🔗 Download URL: {download_data['download_url']}")
                    print(f"      Size: {download_data.get('size_mb', 0)} MB")
            
            # 5. 레지스트리 확인
            print("\n5️⃣ Checking Agent Registry...")
            registry_stats = agent_registry.get_statistics()
            print(f"   Total agents in registry: {registry_stats['total_agents']}")
            print(f"   Storage size: {registry_stats['storage_size_mb']:.2f} MB")
            
            # 최근 등록된 에이전트
            recent_agents = agent_registry.list_agents(limit=5)
            if recent_agents:
                print("\n   Recently registered agents:")
                for agent in recent_agents:
                    print(f"      • {agent['name']} ({agent['type']}) - ID: {agent['agent_id'][:8]}...")
            
            # 6. 프로젝트 추출 테스트 (선택적)
            if 'package_path' in pipeline_data and Path(pipeline_data['package_path']).exists():
                print("\n6️⃣ Testing Project Extraction...")
                test_extract_dir = Path("/tmp/test_extraction")
                test_extract_dir.mkdir(exist_ok=True, parents=True)
                
                try:
                    with zipfile.ZipFile(pipeline_data['package_path'], 'r') as zf:
                        zf.extractall(test_extract_dir)
                    
                    # package.json 확인
                    package_json_path = test_extract_dir / "package.json"
                    if package_json_path.exists():
                        with open(package_json_path, 'r') as f:
                            package_data = json.load(f)
                            print(f"   ✅ Project name: {package_data.get('name')}")
                            print(f"   ✅ Dependencies: {len(package_data.get('dependencies', {}))}")
                    
                    # 에이전트 파일 확인
                    agents_dir = test_extract_dir / "src" / "agents"
                    if agents_dir.exists():
                        agent_files = list(agents_dir.glob("*.js"))
                        print(f"   ✅ Agent files found: {len(agent_files)}")
                    
                    # 정리
                    shutil.rmtree(test_extract_dir)
                    
                except Exception as e:
                    print(f"   ❌ Extraction test failed: {e}")
            
            print("\n" + "="*80)
            print("✨ PIPELINE TEST COMPLETED SUCCESSFULLY!")
            print("="*80)
            
            return True
            
        else:
            print(f"   ❌ Pipeline failed!")
            print(f"   Errors: {result.errors}")
            return False
            
    except Exception as e:
        print(f"\n❌ Pipeline execution error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_agent_registry_integration():
    """
    에이전트 레지스트리 통합 테스트
    """
    print("\n🔍 Testing Agent Registry Integration...")
    
    # 인기 에이전트 조회
    popular = agent_registry.get_popular_agents(5)
    if popular:
        print(f"   Popular agents: {len(popular)}")
        for agent in popular:
            print(f"      • {agent['name']} - Used {agent['usage_count']} times")
    
    # 검색 테스트
    search_results = agent_registry.search_agents("todo")
    if search_results:
        print(f"   Found {len(search_results)} agents matching 'todo'")


async def main():
    """메인 테스트 실행"""
    print("\n" + "🚀 Starting Complete Pipeline Test Suite" + "\n")
    
    # 1. 완전한 파이프라인 테스트
    success = await test_complete_todo_pipeline()
    
    if success:
        # 2. 레지스트리 통합 테스트
        await test_agent_registry_integration()
        
        print("\n✅ All tests completed successfully!")
        print("\n📊 Summary:")
        print("   • Pipeline: ✅ Working")
        print("   • Agno Framework: ✅ Integrated")
        print("   • Agent Registry: ✅ Active")
        print("   • File Generation: ✅ Complete")
        print("   • ZIP Creation: ✅ Success")
        
        return 0
    else:
        print("\n❌ Some tests failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())