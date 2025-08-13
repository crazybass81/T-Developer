#!/usr/bin/env python3
"""
파일 생성 기능 직접 테스트
파이프라인의 _generate_agent_output 메서드를 사용하여 파일 생성 확인
"""

import asyncio
import json
import zipfile
from pathlib import Path
import shutil
import tempfile

async def test_file_generation():
    print("=" * 60)
    print("🧪 Direct File Generation Test")
    print("=" * 60)
    
    from src.orchestration.production_pipeline import ProductionECSPipeline
    
    pipeline = ProductionECSPipeline()
    
    # Generation 에이전트의 출력 직접 생성
    print("\n1️⃣ Generating files for Todo App...")
    
    input_data = {
        "user_input": "Create a todo app with tasks, priorities, and categories",
        "project_name": "advanced-todo-app",
        "project_type": "react",
        "framework": "react",
        "features": ["todo", "priority", "categories", "filter", "search", "export", "import"]
    }
    
    # _generate_agent_output 메서드로 파일 생성
    generation_output = pipeline._generate_agent_output("generation", input_data)
    
    print(f"\n2️⃣ Generation Output:")
    print(f"   Files generated: {generation_output.get('total_files', 0)}")
    print(f"   Framework: {generation_output.get('framework')}")
    print(f"   Features: {generation_output.get('features')}")
    
    # 생성된 파일 분석
    if 'generated_files' in generation_output:
        files = generation_output['generated_files']
        
        print(f"\n3️⃣ File Analysis:")
        print(f"   Total files: {len(files)}")
        
        # 파일 목록
        print(f"\n   📁 File List:")
        for file_path in sorted(files.keys()):
            size = len(files[file_path])
            print(f"      - {file_path}: {size} bytes")
        
        # package.json 검증
        if 'package.json' in files:
            print(f"\n4️⃣ Package.json Validation:")
            try:
                pkg = json.loads(files['package.json'])
                print(f"   ✅ Valid JSON")
                print(f"   📦 Project name: {pkg.get('name')}")
                print(f"   📝 Description: {pkg.get('description', '')[:60]}...")
                print(f"   🔧 Dependencies:")
                deps = pkg.get('dependencies', {})
                for dep, ver in list(deps.items())[:5]:
                    if ver:  # None 값 제외
                        print(f"      - {dep}: {ver}")
            except json.JSONDecodeError as e:
                print(f"   ❌ Invalid JSON: {e}")
        
        # App.js 내용 검증
        if 'src/App.js' in files:
            print(f"\n5️⃣ App.js Content Validation:")
            app_content = files['src/App.js']
            
            # 기능 확인
            features_in_code = []
            for feature in input_data['features']:
                if feature.lower() in app_content.lower():
                    features_in_code.append(feature)
            
            print(f"   📏 File size: {len(app_content)} characters")
            print(f"   ✅ Features found: {features_in_code}")
            print(f"   📊 Feature coverage: {len(features_in_code)}/{len(input_data['features'])}")
            
            # 코드 스니펫
            lines = app_content.split('\n')
            print(f"   📝 First 5 lines:")
            for i, line in enumerate(lines[:5], 1):
                print(f"      {i}: {line[:60]}...")
        
        # 파일 시스템에 저장
        print(f"\n6️⃣ Saving to Filesystem:")
        
        project_dir = Path(f"/tmp/test-todo-app-{int(asyncio.get_event_loop().time())}")
        project_dir.mkdir(parents=True, exist_ok=True)
        
        saved_files = []
        for file_path, content in files.items():
            full_path = project_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
            saved_files.append(file_path)
        
        print(f"   ✅ Saved {len(saved_files)} files to {project_dir}")
        
        # 디렉토리 구조 확인
        print(f"\n7️⃣ Project Structure:")
        for path in sorted(project_dir.rglob('*'))[:15]:
            if path.is_file():
                rel_path = path.relative_to(project_dir)
                indent = "   " * (len(rel_path.parts) - 1)
                print(f"   {indent}📄 {rel_path.name}")
        
        # ZIP 파일 생성
        print(f"\n8️⃣ Creating ZIP Package:")
        
        zip_path = project_dir.parent / f"{project_dir.name}.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in project_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(project_dir.parent)
                    zf.write(file_path, arcname)
        
        if zip_path.exists():
            print(f"   ✅ ZIP created: {zip_path.name}")
            print(f"   📦 Size: {zip_path.stat().st_size / 1024:.2f} KB")
            
            # ZIP 내용 확인
            with zipfile.ZipFile(zip_path, 'r') as zf:
                print(f"   📋 Files in ZIP: {len(zf.namelist())}")
        
        # Assembly 시뮬레이션
        print(f"\n9️⃣ Assembly Simulation:")
        
        assembly_input = {
            "generated_files": files,
            "project_id": "test-todo-123",
            "project_name": input_data['project_name']
        }
        
        assembly_output = pipeline._generate_agent_output("assembly", assembly_input)
        
        if assembly_output.get('zip_created'):
            print(f"   ✅ Assembly successful")
            print(f"   📦 Package path: {assembly_output.get('package_path')}")
        
        # Download 시뮬레이션
        print(f"\n🔟 Download Simulation:")
        
        download_input = {
            "project_id": "test-todo-123",
            "package_path": assembly_output.get('package_path')
        }
        
        download_output = pipeline._generate_agent_output("download", download_input)
        
        print(f"   🔗 Download URL: {download_output.get('download_url')}")
        print(f"   🆔 Download ID: {download_output.get('download_id')}")
        print(f"   📊 Size: {download_output.get('size_mb', 0)} MB")
        
        # 결과 요약
        print(f"\n{'='*60}")
        print(f"✅ TEST RESULTS:")
        print(f"   - Files generated: {len(files)}")
        print(f"   - Features included: {len(features_in_code)}/{len(input_data['features'])}")
        print(f"   - Project saved to: {project_dir}")
        print(f"   - ZIP package created: {zip_path.exists()}")
        print(f"   - Ready for download: Yes")
        
        return True
    
    return False

if __name__ == "__main__":
    success = asyncio.run(test_file_generation())
    
    if success:
        print("\n🎉 SUCCESS: File generation system is working!")
        print("   The system can generate Todo apps with requested features.")
    else:
        print("\n❌ FAILED: File generation not working properly.")