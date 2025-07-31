#!/bin/bash
# scripts/analyze_dependencies.sh

echo "📊 의존성 분석 시작..."

# 1. 전체 프로젝트 의존성 수집
find . -name "requirements*.txt" -type f > requirements_files.txt

# 2. 각 파일별 패키지 분석
while read -r req_file; do
    echo "분석 중: $req_file"
    
    # 패키지 개수
    package_count=$(grep -v "^#" "$req_file" | grep -v "^$" | wc -l)
    echo "  - 패키지 수: $package_count"
    
    # 버전 고정 여부 확인
    pinned=$(grep -E "==" "$req_file" | wc -l)
    echo "  - 버전 고정: $pinned/$package_count"
    
    # 특수 패키지 확인 (git, local 등)
    git_deps=$(grep -E "git\+|@" "$req_file" | wc -l)
    local_deps=$(grep -E "file://|-e \." "$req_file" | wc -l)
    echo "  - Git 의존성: $git_deps"
    echo "  - 로컬 의존성: $local_deps"
done < requirements_files.txt

# 3. 상세 보고서 생성
python3 << 'EOF'
import subprocess
import json
from collections import defaultdict

def analyze_package_sources():
    try:
        result = subprocess.run(['pip', 'list', '--format=json'], 
                              capture_output=True, text=True)
        packages = json.loads(result.stdout)
        
        sources = defaultdict(list)
        for pkg in packages:
            # PyPI 외 소스 확인
            info = subprocess.run(['pip', 'show', pkg['name']], 
                                capture_output=True, text=True)
            if 'Location' in info.stdout:
                if 'site-packages' not in info.stdout:
                    sources['non-pypi'].append(pkg['name'])
            
        return sources
    except Exception as e:
        print(f"Error analyzing packages: {e}")
        return defaultdict(list)

sources = analyze_package_sources()
print(f"\n📦 Non-PyPI 패키지: {len(sources['non-pypi'])}")
for pkg in sources['non-pypi']:
    print(f"  - {pkg}")
EOF