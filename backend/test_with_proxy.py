#!/usr/bin/env python3
"""
프록시 에이전트로 Todo 앱 생성 테스트
실제 에이전트 대신 프록시를 사용하여 파일 생성 확인
"""

import asyncio
import json
import zipfile
from pathlib import Path
import shutil

async def test_with_proxy():
    print("=" * 60)
    print("🧪 Todo App Generation with Proxy Agents")
    print("=" * 60)
    
    from src.orchestration.production_pipeline import ProductionECSPipeline
    
    # 프록시 에이전트만 사용하도록 설정
    pipeline = ProductionECSPipeline()
    
    # 실제 에이전트를 비우고 프록시만 사용
    pipeline.agents = {}  # 실제 에이전트 비우기
    
    # 파이프라인 초기화 (프록시 생성)
    print("\n1️⃣ Initializing pipeline with proxy agents...")
    await pipeline.initialize()
    print(f"   Real agents: {len(pipeline.agents)}")
    print(f"   Proxy agents: {len(pipeline.agent_proxies)}")
    
    # Todo 앱 생성 요청
    print("\n2️⃣ Requesting Todo App Generation...")
    
    result = await pipeline.execute(
        user_input="Create a comprehensive todo app with tasks, priorities, categories, and due dates",
        project_name="todo-app-comprehensive",
        project_type="react",
        features=["todo", "priority", "categories", "due_dates", "filter", "search", "export"]
    )
    
    print(f"\n3️⃣ Pipeline Result:")
    print(f"   ✅ Success: {result.success}")
    print(f"   📋 Project ID: {result.project_id}")
    print(f"   ⏱️ Execution Time: {result.execution_time:.2f}s")
    
    if result.errors:
        print(f"   ⚠️ Errors: {len(result.errors)}")
    
    # 생성된 파일 확인
    if result.metadata and 'pipeline_data' in result.metadata:
        pipeline_data = result.metadata['pipeline_data']
        
        # Generation 결과 확인
        if 'generation_result' in pipeline_data:
            gen_result = pipeline_data['generation_result']
            
            print(f"\n4️⃣ Generated Files:")
            if 'generated_files' in gen_result:
                files = gen_result['generated_files']
                print(f"   📁 Total files: {len(files)}")
                
                # 파일 목록
                for file_path in sorted(files.keys()):
                    file_size = len(files[file_path])
                    print(f"      - {file_path} ({file_size} bytes)")
                
                # package.json 상세 확인
                if 'package.json' in files:
                    print(f"\n5️⃣ Package.json Analysis:")
                    try:
                        package_data = json.loads(files['package.json'])
                        print(f"   📦 Name: {package_data.get('name')}")
                        print(f"   📝 Description: {package_data.get('description', '')[:60]}...")
                        print(f"   🔧 Dependencies:")
                        for dep, ver in list(package_data.get('dependencies', {}).items())[:5]:
                            print(f"      - {dep}: {ver}")
                        print(f"   📜 Scripts:")
                        for script, cmd in package_data.get('scripts', {}).items():
                            print(f"      - {script}: {cmd}")
                    except json.JSONDecodeError as e:
                        print(f"   ❌ Invalid JSON: {e}")
                
                # App.js 내용 확인
                if 'src/App.js' in files:
                    print(f"\n6️⃣ App.js Content Analysis:")
                    app_content = files['src/App.js']
                    
                    # 기능 포함 여부 확인
                    features_found = []
                    for feature in ["todo", "priority", "categories", "due dates", "filter", "search", "export"]:
                        if feature.lower() in app_content.lower():
                            features_found.append(feature)
                    
                    print(f"   ✅ Features found in code: {features_found}")
                    print(f"   📏 File size: {len(app_content)} characters")
                    print(f"   📝 First 200 chars:")
                    print(f"      {app_content[:200]}...")
        
        # Assembly 결과 확인
        if 'assembly_result' in pipeline_data:
            asm_result = pipeline_data['assembly_result']
            
            print(f"\n7️⃣ Assembly Result:")
            if 'package_path' in asm_result and asm_result['package_path']:
                zip_path = Path(asm_result['package_path'])
                if zip_path.exists():
                    print(f"   ✅ ZIP created: {zip_path}")
                    print(f"   📦 Size: {zip_path.stat().st_size / 1024:.2f} KB")
                    
                    # ZIP 내용 확인
                    with zipfile.ZipFile(zip_path, 'r') as zf:
                        file_list = zf.namelist()
                        print(f"   📋 Files in ZIP: {len(file_list)}")
                        for file in sorted(file_list)[:10]:
                            info = zf.getinfo(file)
                            print(f"      - {file} ({info.file_size} bytes)")
                else:
                    print(f"   ❌ ZIP file not found: {zip_path}")
            else:
                print(f"   ⚠️ No package path in result")
        
        # Download 정보
        if 'download_url' in pipeline_data:
            print(f"\n8️⃣ Download Information:")
            print(f"   🔗 URL: {pipeline_data['download_url']}")
            print(f"   🆔 ID: {pipeline_data.get('download_id')}")
            
            # 실제 다운로드 디렉토리 확인
            download_dir = Path("/home/ec2-user/T-DeveloperMVP/backend/downloads")
            if download_dir.exists():
                zip_files = list(download_dir.glob(f"*{result.project_id}*.zip"))
                if zip_files:
                    print(f"   ✅ Found {len(zip_files)} ZIP file(s) in downloads/")
                    for zf in zip_files:
                        print(f"      - {zf.name} ({zf.stat().st_size / 1024:.2f} KB)")
    
    # 최종 결과
    print(f"\n{'='*60}")
    print(f"🎯 Final Result: {'✅ SUCCESS' if result.success else '❌ FAILED'}")
    
    if result.success:
        print(f"   - Project successfully generated")
        print(f"   - Files created and packaged")
        print(f"   - Ready for download")
    else:
        print(f"   - Generation failed")
        print(f"   - Check errors above")
    
    return result

if __name__ == "__main__":
    result = asyncio.run(test_with_proxy())
    
    # 추가 검증
    if result.success:
        print("\n" + "="*60)
        print("📋 VALIDATION SUMMARY")
        print("="*60)
        
        checks = {
            "Pipeline executed": result.success,
            "Files generated": 'pipeline_data' in result.metadata and 'generation_result' in result.metadata['pipeline_data'],
            "Package created": 'assembly_result' in result.metadata.get('pipeline_data', {}),
            "Download ready": 'download_url' in result.metadata.get('pipeline_data', {})
        }
        
        for check, passed in checks.items():
            print(f"{'✅' if passed else '❌'} {check}")
        
        all_passed = all(checks.values())
        print(f"\n🏆 Overall: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")