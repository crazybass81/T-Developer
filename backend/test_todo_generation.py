#!/usr/bin/env python3
"""
Todo 앱 생성 기능 테스트
입력된 기능에 맞게 작동하는 서비스가 생성되는지 확인
"""

import asyncio
import json
import zipfile
from pathlib import Path
import shutil
import tempfile

async def test_todo_generation():
    print("=" * 60)
    print("🧪 Todo App Generation Test")
    print("=" * 60)
    
    from src.orchestration.production_pipeline import ProductionECSPipeline
    
    # 1. 파이프라인 초기화
    print("\n1️⃣ Initializing pipeline...")
    pipeline = ProductionECSPipeline()
    await pipeline.initialize()
    print("   ✅ Pipeline initialized")
    
    # 2. Todo 앱 생성 요청
    test_cases = [
        {
            "name": "Basic Todo App",
            "input": "Create a simple todo app with add and delete tasks",
            "features": ["add_task", "delete_task", "list_tasks"],
            "expected_files": ["package.json", "src/App.js", "src/index.js"]
        },
        {
            "name": "Advanced Todo App",
            "input": "Create a todo app with priority levels, categories, and due dates",
            "features": ["priority", "categories", "due_dates", "filter", "search"],
            "expected_files": ["package.json", "src/App.js", "src/components/TodoList.js"]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"Test Case {i}: {test_case['name']}")
        print(f"{'='*60}")
        
        print(f"\n2️⃣ Requesting: {test_case['input']}")
        print(f"   Features: {test_case['features']}")
        
        result = await pipeline.execute(
            user_input=test_case['input'],
            project_name=f"todo-app-{i}",
            project_type="react",
            features=test_case['features']
        )
        
        print(f"\n3️⃣ Pipeline Result:")
        print(f"   Success: {result.success}")
        print(f"   Project ID: {result.project_id}")
        print(f"   Execution Time: {result.execution_time:.2f}s")
        
        if result.errors:
            print(f"   ⚠️ Errors ({len(result.errors)}):")
            for err in result.errors[:3]:
                print(f"      - {err[:80]}")
        
        # 4. 생성된 파일 확인
        print(f"\n4️⃣ Checking generated files...")
        
        if result.metadata and 'pipeline_data' in result.metadata:
            pipeline_data = result.metadata['pipeline_data']
            
            # Generation 결과 확인
            if 'generation_result' in pipeline_data:
                gen_result = pipeline_data['generation_result']
                if 'generated_files' in gen_result:
                    files = gen_result['generated_files']
                    print(f"   📁 Generated {len(files)} files:")
                    for file_path in list(files.keys())[:5]:
                        print(f"      - {file_path}")
                    
                    # 파일 내용 검증
                    print(f"\n5️⃣ Validating file contents...")
                    
                    # package.json 확인
                    if 'package.json' in files:
                        try:
                            package_data = json.loads(files['package.json'])
                            print(f"   ✅ package.json valid")
                            print(f"      - Name: {package_data.get('name')}")
                            print(f"      - Dependencies: {list(package_data.get('dependencies', {}).keys())[:3]}")
                        except json.JSONDecodeError:
                            print(f"   ❌ Invalid package.json")
                    
                    # App.js 확인
                    if 'src/App.js' in files:
                        app_content = files['src/App.js']
                        has_todo = 'todo' in app_content.lower()
                        has_features = any(f in app_content.lower() for f in test_case['features'])
                        print(f"   {'✅' if has_todo else '❌'} App.js contains 'todo': {has_todo}")
                        print(f"   {'✅' if has_features else '❌'} App.js references features: {has_features}")
                    
                    # Todo 관련 컴포넌트 확인
                    todo_components = [f for f in files.keys() if 'todo' in f.lower()]
                    if todo_components:
                        print(f"   ✅ Found {len(todo_components)} Todo-related files:")
                        for comp in todo_components[:3]:
                            print(f"      - {comp}")
                    
                    # 동적 에이전트 생성 확인
                    if 'is_todo_app' in gen_result:
                        print(f"\n6️⃣ Dynamic Agent Generation:")
                        print(f"   Is Todo App: {gen_result.get('is_todo_app')}")
                        print(f"   Agents Created: {gen_result.get('agents_created', 0)}")
                        if 'agent_names' in gen_result:
                            print(f"   Agent Names: {gen_result['agent_names'][:5]}")
            
            # Assembly 결과 확인
            if 'assembly_result' in pipeline_data:
                asm_result = pipeline_data['assembly_result']
                if 'package_path' in asm_result:
                    zip_path = Path(asm_result['package_path'])
                    if zip_path.exists():
                        print(f"\n7️⃣ Package Assembly:")
                        print(f"   ✅ ZIP file created: {zip_path}")
                        print(f"   Size: {zip_path.stat().st_size / 1024:.2f} KB")
                        
                        # ZIP 내용 확인
                        with zipfile.ZipFile(zip_path, 'r') as zf:
                            file_list = zf.namelist()
                            print(f"   Files in ZIP: {len(file_list)}")
                            for file in file_list[:5]:
                                print(f"      - {file}")
            
            # Download URL 확인
            if 'download_url' in pipeline_data:
                print(f"\n8️⃣ Download Ready:")
                print(f"   URL: {pipeline_data['download_url']}")
                print(f"   ID: {pipeline_data.get('download_id')}")
        
        # 실제 파일 시스템 확인
        print(f"\n9️⃣ Filesystem Check:")
        download_dir = Path("/home/ec2-user/T-DeveloperMVP/backend/downloads")
        if download_dir.exists():
            zip_files = list(download_dir.glob(f"*{result.project_id}*.zip"))
            if zip_files:
                print(f"   ✅ Found {len(zip_files)} ZIP files")
                for zf in zip_files:
                    print(f"      - {zf.name} ({zf.stat().st_size / 1024:.2f} KB)")
                    
                    # ZIP 파일 내용 추출해서 확인
                    with tempfile.TemporaryDirectory() as tmpdir:
                        with zipfile.ZipFile(zf, 'r') as zip_ref:
                            zip_ref.extractall(tmpdir)
                            
                            extracted_files = list(Path(tmpdir).rglob('*'))
                            print(f"   📦 Extracted {len(extracted_files)} files")
                            
                            # package.json 확인
                            package_files = [f for f in extracted_files if f.name == 'package.json']
                            if package_files:
                                with open(package_files[0], 'r') as f:
                                    pkg = json.load(f)
                                    print(f"      Project name: {pkg.get('name')}")
                                    print(f"      Description: {pkg.get('description', '')[:50]}")
            else:
                print(f"   ⚠️ No ZIP files found for project {result.project_id}")
        
        print(f"\n{'='*60}")
        print(f"Test Case {i} Complete: {'✅ PASSED' if result.success else '❌ FAILED'}")

if __name__ == "__main__":
    asyncio.run(test_todo_generation())