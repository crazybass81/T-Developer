#!/usr/bin/env python3
"""Docstring 오류 수정 스크립트"""

import os
import re
from pathlib import Path

agents_dir = Path("/home/ec2-user/T-Developer/backend/packages/agents")

# 수정할 파일들
files_to_fix = [
    "behavior_analyzer.py",
    "impact_analyzer.py",
    "static_analyzer.py"
]

def fix_docstring(file_path):
    """잘못된 docstring 수정"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 패턴: 잘못된 들여쓰기의 document_context 라인
    pattern = r'\n\s+document_context: SharedDocumentContext 인스턴스\n\s+"""'
    
    if re.search(pattern, content):
        # 수정: docstring 안으로 이동
        content = re.sub(
            pattern,
            '\n        """',
            content
        )
        print(f"  ✅ Fixed docstring indentation issue")
    
    # 패턴: __init__ 메서드의 중복된 document_context
    pattern = r'(super\([^)]*),\s*document_context=document_context\s*,\s*document_context=document_context'
    if re.search(pattern, content):
        content = re.sub(pattern, r'\1, document_context=document_context', content)
        print(f"  ✅ Fixed duplicate document_context parameter")
    
    # 패턴: 잘못된 super() 호출
    pattern = r'super\(,\s*document_context=document_context\s*\)'
    if re.search(pattern, content):
        content = re.sub(pattern, 'super()', content)
        print(f"  ✅ Fixed super() call")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def main():
    print("=" * 60)
    print("Docstring 오류 수정")
    print("=" * 60)
    
    for file_name in files_to_fix:
        file_path = agents_dir / file_name
        
        if not file_path.exists():
            print(f"❌ {file_name} not found")
            continue
        
        print(f"\n처리 중: {file_name}")
        fix_docstring(file_path)
    
    print("\n" + "=" * 60)
    print("✅ 완료")
    print("=" * 60)

if __name__ == "__main__":
    main()