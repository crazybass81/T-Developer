#!/usr/bin/env python3
"""모든 에이전트에 document_context 파라미터 추가"""

import os
import re
from pathlib import Path

agents_dir = Path("/home/ec2-user/T-Developer/backend/packages/agents")

# 업데이트할 에이전트 파일들
agent_files = [
    "external_researcher.py",
    "gap_analyzer.py",
    "system_architect.py",
    "orchestrator_designer.py",
    "planner_agent.py",
    "task_creator_agent.py",
    "code_generator.py",
    "quality_gate.py",
    "static_analyzer.py",
    "code_analysis_agent.py",
    "behavior_analyzer.py",
    "impact_analyzer.py"
]

def update_agent(file_path):
    """에이전트 파일 업데이트"""
    print(f"Processing {file_path.name}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 이미 document_context가 있으면 스킵
    if 'document_context' in content and 'def __init__' in content:
        print(f"  ⏭️ {file_path.name} already has document_context")
        return False
    
    # __init__ 메서드 찾기 및 수정
    # 패턴 1: memory_hub만 있는 경우
    pattern1 = r'(def __init__\(self,\s*memory_hub=None)(\):|,)'
    if re.search(pattern1, content):
        content = re.sub(
            pattern1,
            r'\1, document_context=None\2',
            content
        )
        print(f"  ✓ Added document_context parameter to __init__")
    
    # 패턴 2: memory_hub와 다른 파라미터가 있는 경우
    pattern2 = r'(def __init__\([^)]*memory_hub[^)]*)\):'
    if re.search(pattern2, content):
        # document_context가 없는 경우에만 추가
        if 'document_context' not in content:
            content = re.sub(
                pattern2,
                r'\1, document_context=None):',
                content
            )
            print(f"  ✓ Added document_context parameter to __init__")
    
    # super().__init__ 호출 수정
    super_pattern = r'(super\(\).__init__\([^)]*memory_hub=[^)]*)\)'
    super_match = re.search(super_pattern, content)
    
    if super_match and 'document_context=document_context' not in content:
        old_super = super_match.group(0)
        # 줄바꿈과 들여쓰기 유지
        if '\n' in old_super:
            new_super = old_super.replace(')', ',\n            document_context=document_context\n        )')
        else:
            new_super = old_super.replace(')', ', document_context=document_context)')
        content = content.replace(old_super, new_super)
        print(f"  ✓ Added document_context to super().__init__")
    
    # docstring에 document_context 설명 추가
    docstring_pattern = r'("""[^"]*Args:[^"]*memory_hub:[^"]*)("""|\n\s+""")'
    docstring_match = re.search(docstring_pattern, content, re.DOTALL)
    
    if docstring_match and 'document_context:' not in content:
        old_docstring = docstring_match.group(0)
        # 들여쓰기 감지
        indent_match = re.search(r'\n(\s+)memory_hub:', old_docstring)
        if indent_match:
            indent = indent_match.group(1)
            new_docstring = old_docstring.replace(
                docstring_match.group(2),
                f'\n{indent}document_context: SharedDocumentContext 인스턴스\n        {docstring_match.group(2)}'
            )
            content = content.replace(old_docstring, new_docstring)
            print(f"  ✓ Added document_context to docstring")
    
    # 파일 저장
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def main():
    print("=" * 60)
    print("Updating all agents with document_context parameter")
    print("=" * 60)
    
    updated_count = 0
    skipped_count = 0
    not_found_count = 0
    
    for agent_file in agent_files:
        file_path = agents_dir / agent_file
        if file_path.exists():
            if update_agent(file_path):
                updated_count += 1
                print(f"  ✅ {agent_file} updated successfully")
            else:
                skipped_count += 1
        else:
            print(f"  ❌ {agent_file} not found")
            not_found_count += 1
        print()
    
    print("=" * 60)
    print(f"Summary:")
    print(f"  ✅ Updated: {updated_count} files")
    print(f"  ⏭️ Skipped: {skipped_count} files")
    print(f"  ❌ Not found: {not_found_count} files")
    print("=" * 60)

if __name__ == "__main__":
    main()