#!/usr/bin/env python3
"""
프록시만 사용하여 파일 생성 기능 확인
"""

import asyncio
import json
import shutil
from pathlib import Path

# Import 전에 에이전트 로더 비활성화
import sys
sys.modules['src.orchestration.agent_loader'] = type(sys)('mock_module')
sys.modules['src.orchestration.agent_loader'].AGENT_CLASSES = {}

async def test_proxy_only():
    print("=" * 60)
    print("🧪 Testing File Generation with Proxy Agents Only")
    print("=" * 60)
    
    from src.orchestration.production_pipeline import ProductionECSPipeline
    
    # 프록시만 사용하는 파이프라인
    pipeline = ProductionECSPipeline()
    
    # 실제 에이전트 완전히 비활성화
    pipeline.agents = {}
    AGENTS_AVAILABLE = False
    
    print("\n1️⃣ Initializing with proxy agents only...")
    await pipeline.initialize()
    
    print(f"   Real agents: {len(pipeline.agents)}")
    print(f"   Proxy agents: {len(pipeline.agent_proxies)}")
    
    # Todo 앱 생성 테스트
    print("\n2️⃣ Generating Todo App...")
    
    result = await pipeline.execute(
        user_input="Create a todo app with add, delete, and mark as complete features",
        project_name="proxy-todo-app",
        project_type="react",
        features=["add_task", "delete_task", "complete_task", "filter_tasks"]
    )
    
    print(f"\n3️⃣ Generation Result:")
    print(f"   Success: {result.success}")
    print(f"   Project ID: {result.project_id}")
    print(f"   Execution Time: {result.execution_time:.2f}s")
    
    # 파일 생성 확인
    if result.metadata and 'pipeline_data' in result.metadata:
        pipeline_data = result.metadata['pipeline_data']
        
        # Generation 프록시가 만든 파일들
        if 'generation_result' in pipeline_data:
            gen = pipeline_data['generation_result']
            if 'generated_files' in gen:
                files = gen['generated_files']
                
                print(f"\n4️⃣ Generated Files ({len(files)} total):")
                
                # 파일 목록과 크기
                total_size = 0
                for path, content in files.items():
                    size = len(content)
                    total_size += size
                    print(f"   📄 {path}: {size} bytes")
                
                print(f"   📊 Total size: {total_size / 1024:.2f} KB")
                
                # package.json 검증
                if 'package.json' in files:
                    print(f"\n5️⃣ Validating package.json:")
                    try:
                        pkg = json.loads(files['package.json'])
                        print(f"   ✅ Valid JSON")
                        print(f"   📦 Name: {pkg.get('name')}")
                        print(f"   📝 Version: {pkg.get('version')}")
                        print(f"   🔧 React version: {pkg.get('dependencies', {}).get('react')}")
                    except:
                        print(f"   ❌ Invalid JSON")
                
                # App.js 검증
                if 'src/App.js' in files:
                    app_content = files['src/App.js']
                    print(f"\n6️⃣ Validating App.js:")
                    print(f"   📏 Size: {len(app_content)} characters")
                    print(f"   ✅ Contains 'todo': {'todo' in app_content.lower()}")
                    print(f"   ✅ Contains features: {any(f in app_content.lower() for f in ['add', 'delete', 'complete'])}")
                
                # 실제 파일 시스템에 저장
                output_dir = Path(f"/tmp/generated_projects/{result.project_id}")
                output_dir.mkdir(parents=True, exist_ok=True)
                
                print(f"\n7️⃣ Saving to filesystem:")
                saved_count = 0
                for file_path, content in files.items():
                    full_path = output_dir / file_path
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    full_path.write_text(content)
                    saved_count += 1
                
                print(f"   ✅ Saved {saved_count} files to {output_dir}")
                
                # 디렉토리 구조 확인
                print(f"\n8️⃣ Project Structure:")
                for path in sorted(output_dir.rglob('*'))[:10]:
                    if path.is_file():
                        rel_path = path.relative_to(output_dir)
                        print(f"   📁 {rel_path}")
        
        # Assembly 확인
        if 'assembly_result' in pipeline_data:
            asm = pipeline_data['assembly_result']
            if 'package_path' in asm and asm['package_path']:
                zip_path = Path(asm['package_path'])
                if zip_path.exists():
                    print(f"\n9️⃣ Package Assembly:")
                    print(f"   ✅ ZIP created: {zip_path.name}")
                    print(f"   📦 Size: {zip_path.stat().st_size / 1024:.2f} KB")
        
        # Download URL
        if 'download_url' in pipeline_data:
            print(f"\n🔟 Download Ready:")
            print(f"   🔗 URL: {pipeline_data['download_url']}")
            print(f"   🆔 ID: {pipeline_data.get('download_id')}")
    
    # 성공 여부
    print(f"\n{'='*60}")
    if result.success:
        print("✅ SUCCESS: Files generated with proxy agents!")
        print("   - Project files created")
        print("   - Package assembled")
        print("   - Ready for download")
    else:
        print("❌ FAILED: Check errors above")
    
    return result

if __name__ == "__main__":
    result = asyncio.run(test_proxy_only())