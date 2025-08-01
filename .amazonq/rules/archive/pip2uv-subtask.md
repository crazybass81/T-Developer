# pip → uv 전환 프로젝트 상세 작업 지시서

## 📋 Phase 1: 준비 및 검증 (Day 1-3)

### Task 1.1: 현재 환경 분석 및 백업

#### SubTask 1.1.1: 의존성 목록 수집 및 분석
**담당자**: DevOps 엔지니어  
**예상 소요시간**: 2시간

```bash
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

sources = analyze_package_sources()
print(f"\n📦 Non-PyPI 패키지: {len(sources['non-pypi'])}")
for pkg in sources['non-pypi']:
    print(f"  - {pkg}")
EOF
```

#### SubTask 1.1.2: 환경 구성 백업
**담당자**: 시스템 관리자  
**예상 소요시간**: 1시간

```bash
#!/bin/bash
# scripts/backup_environment.sh

BACKUP_DIR="backup/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "💾 환경 백업 시작: $BACKUP_DIR"

# 1. Python 환경 정보
python3 -m pip freeze > "$BACKUP_DIR/pip_freeze.txt"
python3 -m pip list --format=json > "$BACKUP_DIR/pip_list.json"
python3 -V > "$BACKUP_DIR/python_version.txt"
pip -V >> "$BACKUP_DIR/python_version.txt"

# 2. 시스템 정보
uname -a > "$BACKUP_DIR/system_info.txt"
cat /etc/os-release >> "$BACKUP_DIR/system_info.txt" 2>/dev/null || true

# 3. 환경 변수
env | grep -E "PYTHON|PIP|PATH" > "$BACKUP_DIR/env_vars.txt"

# 4. pip 설정
pip config list > "$BACKUP_DIR/pip_config.txt"
cp ~/.pip/pip.conf "$BACKUP_DIR/" 2>/dev/null || true

# 5. 가상환경 메타데이터
if [ -d ".venv" ]; then
    cp .venv/pyvenv.cfg "$BACKUP_DIR/" 2>/dev/null || true
fi

# 6. 백업 검증
tar -czf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"
echo "✅ 백업 완료: $BACKUP_DIR.tar.gz"
```

#### SubTask 1.1.3: 위험 요소 식별
**담당자**: 시니어 개발자  
**예상 소요시간**: 1시간

```python
# scripts/identify_risks.py
import json
import subprocess
import re
from typing import List, Dict

class RiskAnalyzer:
    def __init__(self):
        self.risks = []
        
    def analyze_package_compatibility(self):
        """패키지 호환성 위험 분석"""
        with open('backup/pip_list.json', 'r') as f:
            packages = json.load(f)
        
        for pkg in packages:
            # 오래된 패키지 확인
            if self._is_legacy_package(pkg['name']):
                self.risks.append({
                    'type': 'compatibility',
                    'severity': 'high',
                    'package': pkg['name'],
                    'issue': 'Legacy package may not be compatible with uv',
                    'mitigation': f'Test {pkg["name"]} installation separately'
                })
            
            # 특수 설치 옵션 사용 패키지
            if self._has_special_install_options(pkg['name']):
                self.risks.append({
                    'type': 'installation',
                    'severity': 'medium',
                    'package': pkg['name'],
                    'issue': 'Package requires special installation options',
                    'mitigation': 'Document installation process'
                })
    
    def analyze_ci_dependencies(self):
        """CI/CD 파이프라인 의존성 분석"""
        # GitHub Actions 워크플로우 분석
        workflows = self._find_github_workflows()
        
        for workflow in workflows:
            if 'pip install' in open(workflow).read():
                self.risks.append({
                    'type': 'ci/cd',
                    'severity': 'medium',
                    'file': workflow,
                    'issue': 'Workflow uses pip directly',
                    'mitigation': 'Update workflow to use uv'
                })
    
    def _is_legacy_package(self, name: str) -> bool:
        # 알려진 레거시 패키지 목록
        legacy_packages = ['nose', 'distribute', 'PIL']
        return name in legacy_packages
    
    def _has_special_install_options(self, name: str) -> bool:
        # 특수 설치가 필요한 패키지
        special_packages = ['mysqlclient', 'psycopg2', 'Pillow']
        return name in special_packages
    
    def _find_github_workflows(self) -> List[str]:
        import glob
        return glob.glob('.github/workflows/*.yml')
    
    def generate_report(self):
        """위험 분석 보고서 생성"""
        report = {
            'total_risks': len(self.risks),
            'by_severity': {
                'high': len([r for r in self.risks if r['severity'] == 'high']),
                'medium': len([r for r in self.risks if r['severity'] == 'medium']),
                'low': len([r for r in self.risks if r['severity'] == 'low'])
            },
            'risks': self.risks
        }
        
        with open('risk_analysis_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"⚠️  총 {report['total_risks']}개의 위험 요소 발견")
        print(f"   - 높음: {report['by_severity']['high']}")
        print(f"   - 중간: {report['by_severity']['medium']}")
        print(f"   - 낮음: {report['by_severity']['low']}")

if __name__ == "__main__":
    analyzer = RiskAnalyzer()
    analyzer.analyze_package_compatibility()
    analyzer.analyze_ci_dependencies()
    analyzer.generate_report()
```

### Task 1.2: uv 호환성 테스트 환경 구축

#### SubTask 1.2.1: 격리된 테스트 환경 생성
**담당자**: DevOps 엔지니어  
**예상 소요시간**: 2시간

```bash
#!/bin/bash
# scripts/create_test_environment.sh

echo "🧪 uv 테스트 환경 구축 중..."

# 1. 테스트 디렉토리 구조 생성
TEST_DIR="uv-compatibility-test"
rm -rf "$TEST_DIR"
mkdir -p "$TEST_DIR"/{results,logs,temp}

cd "$TEST_DIR"

# 2. Docker 기반 격리 환경 생성
cat > Dockerfile.test << 'EOF'
FROM python:3.11-slim

# 테스트에 필요한 시스템 패키지
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    libpq-dev \
    libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# uv 설치
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

WORKDIR /test
EOF

# 3. 테스트 스크립트 생성
cat > test_uv_installation.py << 'EOF'
import subprocess
import time
import json
import sys
from pathlib import Path

class UvCompatibilityTester:
    def __init__(self, requirements_file):
        self.requirements_file = requirements_file
        self.results = {
            'total_packages': 0,
            'successful': [],
            'failed': [],
            'warnings': [],
            'timing': {}
        }
    
    def test_individual_packages(self):
        """각 패키지를 개별적으로 테스트"""
        with open(self.requirements_file, 'r') as f:
            packages = [line.strip() for line in f 
                       if line.strip() and not line.startswith('#')]
        
        self.results['total_packages'] = len(packages)
        
        for package in packages:
            print(f"Testing: {package}")
            start_time = time.time()
            
            # uv로 설치 시도
            result = subprocess.run(
                ['uv', 'pip', 'install', '--dry-run', package],
                capture_output=True,
                text=True
            )
            
            elapsed = time.time() - start_time
            
            if result.returncode == 0:
                self.results['successful'].append(package)
                self.results['timing'][package] = elapsed
            else:
                self.results['failed'].append({
                    'package': package,
                    'error': result.stderr,
                    'stdout': result.stdout
                })
                
                # 대체 방법 시도
                self._try_alternative_install(package)
    
    def _try_alternative_install(self, package):
        """실패한 패키지에 대한 대체 설치 방법 시도"""
        # --pre 옵션으로 시도
        result = subprocess.run(
            ['uv', 'pip', 'install', '--dry-run', '--pre', package],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            self.results['warnings'].append({
                'package': package,
                'message': 'Requires --pre flag',
                'solution': f'uv pip install --pre {package}'
            })
    
    def test_bulk_installation(self):
        """전체 requirements 파일로 한번에 설치 테스트"""
        print("\n🔄 Bulk installation test...")
        
        start_time = time.time()
        result = subprocess.run(
            ['uv', 'pip', 'install', '--dry-run', '-r', self.requirements_file],
            capture_output=True,
            text=True
        )
        elapsed = time.time() - start_time
        
        self.results['bulk_install'] = {
            'success': result.returncode == 0,
            'time': elapsed,
            'output': result.stdout,
            'error': result.stderr
        }
    
    def compare_with_pip(self):
        """pip과 성능 비교"""
        print("\n⚡ Performance comparison...")
        
        # pip 설치 시간
        start_time = time.time()
        subprocess.run(
            ['pip', 'install', '--dry-run', '-r', self.requirements_file],
            capture_output=True
        )
        pip_time = time.time() - start_time
        
        # uv 설치 시간
        start_time = time.time()
        subprocess.run(
            ['uv', 'pip', 'install', '--dry-run', '-r', self.requirements_file],
            capture_output=True
        )
        uv_time = time.time() - start_time
        
        self.results['performance'] = {
            'pip_time': pip_time,
            'uv_time': uv_time,
            'speedup': pip_time / uv_time if uv_time > 0 else 0
        }
    
    def generate_report(self):
        """상세 보고서 생성"""
        success_rate = len(self.results['successful']) / self.results['total_packages'] * 100
        
        report = f"""
# uv 호환성 테스트 결과

## 요약
- 전체 패키지: {self.results['total_packages']}
- 성공: {len(self.results['successful'])} ({success_rate:.1f}%)
- 실패: {len(self.results['failed'])}
- 경고: {len(self.results['warnings'])}

## 성능 비교
- pip 설치 시간: {self.results['performance']['pip_time']:.2f}초
- uv 설치 시간: {self.results['performance']['uv_time']:.2f}초
- 속도 향상: {self.results['performance']['speedup']:.1f}x

## 실패한 패키지
"""
        for fail in self.results['failed']:
            report += f"\n### {fail['package']}\n"
            report += f"```\n{fail['error']}\n```\n"
        
        with open('results/compatibility_report.md', 'w') as f:
            f.write(report)
        
        # JSON 형식으로도 저장
        with open('results/compatibility_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)

if __name__ == '__main__':
    tester = UvCompatibilityTester('../requirements.txt')
    tester.test_individual_packages()
    tester.test_bulk_installation()
    tester.compare_with_pip()
    tester.generate_report()
EOF

# 4. 테스트 실행 스크립트
cat > run_tests.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting uv compatibility tests..."

# Docker 이미지 빌드
docker build -f Dockerfile.test -t uv-test .

# 테스트 실행
docker run --rm \
    -v $(pwd)/../requirements.txt:/test/requirements.txt:ro \
    -v $(pwd)/results:/test/results \
    -v $(pwd)/logs:/test/logs \
    uv-test python test_uv_installation.py

echo "✅ Tests completed. Check results/ directory for reports."
EOF

chmod +x run_tests.sh
```

#### SubTask 1.2.2: 패키지별 호환성 매트릭스 생성
**담당자**: 백엔드 개발자  
**예상 소요시간**: 3시간

```python
# scripts/create_compatibility_matrix.py
import json
import pandas as pd
from typing import Dict, List, Tuple
import subprocess
import concurrent.futures
from dataclasses import dataclass
import platform

@dataclass
class PackageTestResult:
    name: str
    version: str
    pip_compatible: bool
    uv_compatible: bool
    install_time_pip: float
    install_time_uv: float
    error_message: str = ""
    special_flags: List[str] = None
    platform: str = platform.system()

class CompatibilityMatrixBuilder:
    def __init__(self):
        self.results: List[PackageTestResult] = []
        self.test_environments = self._setup_test_environments()
    
    def _setup_test_environments(self):
        """pip과 uv 테스트 환경 설정"""
        return {
            'pip': {
                'venv_path': '.venv_pip_test',
                'command': ['pip', 'install']
            },
            'uv': {
                'venv_path': '.venv_uv_test',
                'command': ['uv', 'pip', 'install']
            }
        }
    
    def test_package(self, package_spec: str) -> PackageTestResult:
        """단일 패키지 테스트"""
        package_name, version = self._parse_package_spec(package_spec)
        
        result = PackageTestResult(
            name=package_name,
            version=version,
            pip_compatible=False,
            uv_compatible=False,
            install_time_pip=0,
            install_time_uv=0
        )
        
        # pip 테스트
        pip_result = self._test_with_pip(package_spec)
        result.pip_compatible = pip_result['success']
        result.install_time_pip = pip_result['time']
        
        # uv 테스트
        uv_result = self._test_with_uv(package_spec)
        result.uv_compatible = uv_result['success']
        result.install_time_uv = uv_result['time']
        result.error_message = uv_result.get('error', '')
        
        # 특수 플래그 필요 여부 확인
        if not result.uv_compatible:
            result.special_flags = self._check_special_flags(package_spec)
        
        return result
    
    def _test_with_pip(self, package: str) -> Dict:
        """pip으로 패키지 설치 테스트"""
        import time
        
        start = time.time()
        try:
            subprocess.run(
                ['pip', 'install', '--dry-run', package],
                check=True,
                capture_output=True,
                timeout=60
            )
            return {'success': True, 'time': time.time() - start}
        except subprocess.CalledProcessError as e:
            return {
                'success': False, 
                'time': time.time() - start,
                'error': e.stderr.decode()
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'time': 60,
                'error': 'Timeout'
            }
    
    def _test_with_uv(self, package: str) -> Dict:
        """uv로 패키지 설치 테스트"""
        import time
        
        start = time.time()
        try:
            subprocess.run(
                ['uv', 'pip', 'install', '--dry-run', package],
                check=True,
                capture_output=True,
                timeout=60
            )
            return {'success': True, 'time': time.time() - start}
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'time': time.time() - start,
                'error': e.stderr.decode()
            }
    
    def _check_special_flags(self, package: str) -> List[str]:
        """특수 플래그로 재시도"""
        flags_to_try = ['--pre', '--no-binary :all:', '--only-binary :all:']
        working_flags = []
        
        for flag in flags_to_try:
            try:
                subprocess.run(
                    ['uv', 'pip', 'install', '--dry-run', flag, package],
                    check=True,
                    capture_output=True
                )
                working_flags.append(flag)
            except:
                pass
        
        return working_flags
    
    def _parse_package_spec(self, spec: str) -> Tuple[str, str]:
        """패키지 명세 파싱"""
        if '==' in spec:
            name, version = spec.split('==')
            return name.strip(), version.strip()
        elif '>=' in spec or '<=' in spec:
            # 버전 범위 지정
            for op in ['>=', '<=', '>', '<', '~=']:
                if op in spec:
                    name, version = spec.split(op)
                    return name.strip(), f"{op}{version.strip()}"
        return spec.strip(), 'any'
    
    def test_all_packages(self, requirements_file: str):
        """모든 패키지 병렬 테스트"""
        with open(requirements_file, 'r') as f:
            packages = [line.strip() for line in f 
                       if line.strip() and not line.startswith('#')]
        
        print(f"🧪 Testing {len(packages)} packages...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_package = {
                executor.submit(self.test_package, pkg): pkg 
                for pkg in packages
            }
            
            for future in concurrent.futures.as_completed(future_to_package):
                package = future_to_package[future]
                try:
                    result = future.result()
                    self.results.append(result)
                    self._print_progress(result)
                except Exception as exc:
                    print(f'❌ {package} generated an exception: {exc}')
    
    def _print_progress(self, result: PackageTestResult):
        """진행 상황 출력"""
        if result.uv_compatible:
            speedup = result.install_time_pip / result.install_time_uv if result.install_time_uv > 0 else 0
            print(f"✅ {result.name}: {speedup:.1f}x faster")
        else:
            print(f"❌ {result.name}: {result.error_message[:50]}...")
    
    def generate_matrix(self):
        """호환성 매트릭스 생성"""
        # DataFrame 생성
        df = pd.DataFrame([
            {
                'Package': r.name,
                'Version': r.version,
                'pip': '✅' if r.pip_compatible else '❌',
                'uv': '✅' if r.uv_compatible else '❌',
                'pip_time': f"{r.install_time_pip:.2f}s",
                'uv_time': f"{r.install_time_uv:.2f}s",
                'Speedup': f"{r.install_time_pip/r.install_time_uv:.1f}x" if r.install_time_uv > 0 else 'N/A',
                'Special_Flags': ', '.join(r.special_flags) if r.special_flags else '',
                'Error': r.error_message[:50] if r.error_message else ''
            }
            for r in self.results
        ])
        
        # HTML 보고서 생성
        html_report = f"""
<!DOCTYPE html>
<html>
<head>
    <title>uv Compatibility Matrix</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .success {{ color: green; }}
        .failure {{ color: red; }}
        .summary {{ background-color: #e7f3fe; padding: 15px; margin: 20px 0; }}
    </style>
</head>
<body>
    <h1>uv Compatibility Matrix</h1>
    <div class="summary">
        <h2>Summary</h2>
        <p>Total Packages: {len(self.results)}</p>
        <p>uv Compatible: {sum(1 for r in self.results if r.uv_compatible)} ({sum(1 for r in self.results if r.uv_compatible)/len(self.results)*100:.1f}%)</p>
        <p>Average Speedup: {sum(r.install_time_pip/r.install_time_uv for r in self.results if r.install_time_uv > 0)/len([r for r in self.results if r.install_time_uv > 0]):.1f}x</p>
    </div>
    {df.to_html(index=False, escape=False)}
</body>
</html>
"""
        
        # 파일 저장
        with open('results/compatibility_matrix.html', 'w') as f:
            f.write(html_report)
        
        df.to_csv('results/compatibility_matrix.csv', index=False)
        
        # 문제 패키지 별도 저장
        problem_packages = df[df['uv'] == '❌']
        if not problem_packages.empty:
            problem_packages.to_csv('results/problem_packages.csv', index=False)
            
            # 해결 방안 문서 생성
            self._generate_solutions_doc(problem_packages)
    
    def _generate_solutions_doc(self, problem_packages):
        """문제 패키지 해결 방안 문서"""
        doc = """# uv 호환성 문제 해결 가이드

## 문제 패키지 및 해결 방안

"""
        for _, pkg in problem_packages.iterrows():
            doc += f"""
### {pkg['Package']} {pkg['Version']}
- **오류**: {pkg['Error']}
- **해결 방안**:
"""
            if pkg['Special_Flags']:
                doc += f"  - 특수 플래그 사용: `uv pip install {pkg['Special_Flags']} {pkg['Package']}`\n"
            
            # 알려진 해결 방안 추가
            solutions = self._get_known_solutions(pkg['Package'])
            for solution in solutions:
                doc += f"  - {solution}\n"
        
        with open('results/problem_solutions.md', 'w') as f:
            f.write(doc)
    
    def _get_known_solutions(self, package: str) -> List[str]:
        """알려진 패키지별 해결 방안"""
        known_solutions = {
            'mysqlclient': [
                'MySQL 개발 헤더 설치 필요: `apt-get install libmysqlclient-dev`',
                '대안: `pymysql` 사용 고려'
            ],
            'psycopg2': [
                'PostgreSQL 개발 헤더 설치 필요: `apt-get install libpq-dev`',
                '대안: `psycopg2-binary` 사용'
            ],
            'Pillow': [
                '이미지 라이브러리 필요: `apt-get install libjpeg-dev zlib1g-dev`'
            ]
        }
        
        return known_solutions.get(package, ['수동 확인 필요'])

if __name__ == '__main__':
    builder = CompatibilityMatrixBuilder()
    builder.test_all_packages('requirements.txt')
    builder.generate_matrix()
    print("\n✅ Compatibility matrix generated in results/")
```

#### SubTask 1.2.3: 성능 벤치마크 수행
**담당자**: 성능 엔지니어  
**예상 소요시간**: 1시간

```python
# scripts/performance_benchmark.py
import subprocess
import time
import statistics
import json
import matplotlib.pyplot as plt
from typing import Dict, List
import psutil
import os

class PerformanceBenchmark:
    def __init__(self):
        self.results = {
            'pip': {'times': [], 'memory': [], 'cpu': []},
            'uv': {'times': [], 'memory': [], 'cpu': []}
        }
        self.scenarios = [
            {
                'name': 'clean_install',
                'description': 'Clean installation of all dependencies',
                'setup': self._clean_cache,
                'requirements': 'requirements.txt'
            },
            {
                'name': 'cached_install',
                'description': 'Installation with populated cache',
                'setup': self._populate_cache,
                'requirements': 'requirements.txt'
            },
            {
                'name': 'single_package',
                'description': 'Single package installation',
                'setup': self._clean_cache,
                'package': 'requests'
            },
            {
                'name': 'large_package',
                'description': 'Large package with many dependencies',
                'setup': self._clean_cache,
                'package': 'pandas[all]'
            }
        ]
    
    def _clean_cache(self):
        """캐시 정리"""
        subprocess.run(['pip', 'cache', 'purge'], capture_output=True)
        # uv 캐시 정리
        cache_dir = os.path.expanduser('~/.cache/uv')
        if os.path.exists(cache_dir):
            import shutil
            shutil.rmtree(cache_dir)
    
    def _populate_cache(self):
        """캐시 사전 로드"""
        # pip으로 한 번 설치하여 캐시 생성
        subprocess.run(
            ['pip', 'install', '--dry-run', '-r', 'requirements.txt'],
            capture_output=True
        )
    
    def benchmark_scenario(self, scenario: Dict) -> Dict:
        """단일 시나리오 벤치마크"""
        results = {
            'scenario': scenario['name'],
            'description': scenario['description'],
            'pip': [],
            'uv': []
        }
        
        # 5회 반복 측정
        for i in range(5):
            print(f"  Run {i+1}/5...")
            
            # Setup
            scenario['setup']()
            
            # pip 측정
            pip_result = self._measure_pip(scenario)
            results['pip'].append(pip_result)
            
            # Setup
            scenario['setup']()
            
            # uv 측정
            uv_result = self._measure_uv(scenario)
            results['uv'].append(uv_result)
        
        return results
    
    def _measure_pip(self, scenario: Dict) -> Dict:
        """pip 성능 측정"""
        process = psutil.Popen(
            self._get_pip_command(scenario),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        start_time = time.time()
        cpu_percent = []
        memory_mb = []
        
        # 프로세스 모니터링
        while process.poll() is None:
            try:
                cpu_percent.append(process.cpu_percent(interval=0.1))
                memory_mb.append(process.memory_info().rss / 1024 / 1024)
            except psutil.NoSuchProcess:
                break
        
        end_time = time.time()
        
        return {
            'time': end_time - start_time,
            'cpu_avg': statistics.mean(cpu_percent) if cpu_percent else 0,
            'memory_peak': max(memory_mb) if memory_mb else 0,
            'exit_code': process.returncode
        }
    
    def _measure_uv(self, scenario: Dict) -> Dict:
        """uv 성능 측정"""
        process = psutil.Popen(
            self._get_uv_command(scenario),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        start_time = time.time()
        cpu_percent = []
        memory_mb = []
        
        while process.poll() is None:
            try:
                cpu_percent.append(process.cpu_percent(interval=0.1))
                memory_mb.append(process.memory_info().rss / 1024 / 1024)
            except psutil.NoSuchProcess:
                break
        
        end_time = time.time()
        
        return {
            'time': end_time - start_time,
            'cpu_avg': statistics.mean(cpu_percent) if cpu_percent else 0,
            'memory_peak': max(memory_mb) if memory_mb else 0,
            'exit_code': process.returncode
        }
    
    def _get_pip_command(self, scenario: Dict) -> List[str]:
        """pip 명령 생성"""
        if 'requirements' in scenario:
            return ['pip', 'install', '-r', scenario['requirements']]
        else:
            return ['pip', 'install', scenario['package']]
    
    def _get_uv_command(self, scenario: Dict) -> List[str]:
        """uv 명령 생성"""
        if 'requirements' in scenario:
            return ['uv', 'pip', 'install', '-r', scenario['requirements']]
        else:
            return ['uv', 'pip', 'install', scenario['package']]
    
    def run_all_benchmarks(self):
        """모든 벤치마크 실행"""
        all_results = []
        
        for scenario in self.scenarios:
            print(f"\n🏃 Running benchmark: {scenario['name']}")
            result = self.benchmark_scenario(scenario)
            all_results.append(result)
            
            # 중간 결과 출력
            pip_avg = statistics.mean([r['time'] for r in result['pip']])
            uv_avg = statistics.mean([r['time'] for r in result['uv']])
            speedup = pip_avg / uv_avg if uv_avg > 0 else 0
            
            print(f"  pip: {pip_avg:.2f}s")
            print(f"  uv:  {uv_avg:.2f}s")
            print(f"  Speedup: {speedup:.1f}x")
        
        self.generate_report(all_results)
    
    def generate_report(self, results: List[Dict]):
        """벤치마크 보고서 생성"""
        # 그래프 생성
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('pip vs uv Performance Comparison')
        
        for idx, result in enumerate(results):
            ax = axes[idx // 2, idx % 2]
            
            # 시간 비교
            pip_times = [r['time'] for r in result['pip']]
            uv_times = [r['time'] for r in result['uv']]
            
            ax.boxplot([pip_times, uv_times], labels=['pip', 'uv'])
            ax.set_title(result['scenario'])
            ax.set_ylabel('Time (seconds)')
            
            # 평균과 속도 향상 표시
            pip_avg = statistics.mean(pip_times)
            uv_avg = statistics.mean(uv_times)
            speedup = pip_avg / uv_avg
            
            ax.text(0.5, 0.95, f'Speedup: {speedup:.1f}x',
                   transform=ax.transAxes,
                   verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        plt.savefig('results/performance_comparison.png')
        
        # 상세 보고서 생성
        report = {
            'summary': {
                'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'scenarios': len(results)
            },
            'results': []
        }
        
        for result in results:
            scenario_summary = {
                'scenario': result['scenario'],
                'description': result['description'],
                'pip': {
                    'avg_time': statistics.mean([r['time'] for r in result['pip']]),
                    'std_dev': statistics.stdev([r['time'] for r in result['pip']]),
                    'avg_cpu': statistics.mean([r['cpu_avg'] for r in result['pip']]),
                    'peak_memory': max([r['memory_peak'] for r in result['pip']])
                },
                'uv': {
                    'avg_time': statistics.mean([r['time'] for r in result['uv']]),
                    'std_dev': statistics.stdev([r['time'] for r in result['uv']]),
                    'avg_cpu': statistics.mean([r['cpu_avg'] for r in result['uv']]),
                    'peak_memory': max([r['memory_peak'] for r in result['uv']])
                }
            }
            
            scenario_summary['speedup'] = (
                scenario_summary['pip']['avg_time'] / 
                scenario_summary['uv']['avg_time']
            )
            
            report['results'].append(scenario_summary)
        
        # JSON 보고서 저장
        with open('results/benchmark_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        # Markdown 보고서 생성
        self._generate_markdown_report(report)
    
    def _generate_markdown_report(self, report: Dict):
        """Markdown 형식 보고서 생성"""
        md = f"""# Performance Benchmark Report

**Date**: {report['summary']['date']}

## Executive Summary

uv demonstrates significant performance improvements over pip across all tested scenarios.

## Detailed Results

| Scenario | pip (avg) | uv (avg) | Speedup | Memory Savings |
|----------|-----------|----------|---------|----------------|
"""
        
        for result in report['results']:
            pip_time = result['pip']['avg_time']
            uv_time = result['uv']['avg_time']
            speedup = result['speedup']
            memory_savings = (
                (result['pip']['peak_memory'] - result['uv']['peak_memory']) / 
                result['pip']['peak_memory'] * 100
            )
            
            md += f"| {result['scenario']} | {pip_time:.2f}s | {uv_time:.2f}s | {speedup:.1f}x | {memory_savings:.0f}% |\n"
        
        md += """

## Recommendations

Based on the benchmark results:

1. **Immediate adoption recommended** - uv shows consistent performance improvements
2. **CI/CD optimization** - Expect 50-80% reduction in dependency installation time
3. **Developer experience** - Significant time savings in daily development workflow

## Test Environment

- Python Version: 3.11
- OS: Linux/macOS
- CPU: [System CPU]
- Memory: [System Memory]
"""
        
        with open('results/benchmark_report.md', 'w') as f:
            f.write(md)

if __name__ == '__main__':
    benchmark = PerformanceBenchmark()
    benchmark.run_all_benchmarks()
    print("\n✅ Benchmark complete. Results saved to results/")
```

### Task 1.3: 문서화 및 가이드 작성

#### SubTask 1.3.1: 개발자 가이드 작성
**담당자**: 기술 문서 담당자  
**예상 소요시간**: 2시간

```markdown
# docs/developer-guide-uv.md

# uv 개발자 가이드

## 목차
1. [시작하기](#시작하기)
2. [기본 사용법](#기본-사용법)
3. [고급 기능](#고급-기능)
4. [문제 해결](#문제-해결)
5. [모범 사례](#모범-사례)

## 시작하기

### uv란?
uv는 Rust로 작성된 초고속 Python 패키지 관리자입니다. pip 대비 10-100배 빠른 성능을 제공합니다.

### 설치

#### macOS/Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Windows
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 설치 확인
```bash
uv --version
```

## 기본 사용법

### 가상환경 생성
```bash
# 기본 가상환경 생성
uv venv

# Python 버전 지정
uv venv --python python3.11

# 특정 경로에 생성
uv venv myenv
```

### 패키지 설치

#### 단일 패키지
```bash
# 최신 버전 설치
uv pip install requests

# 특정 버전 설치
uv pip install requests==2.31.0

# 버전 범위 지정
uv pip install "requests>=2.28,<3.0"
```

#### requirements.txt 사용
```bash
# 설치
uv pip install -r requirements.txt

# 동기화 (정확히 일치하도록)
uv pip sync requirements.txt
```

#### 개발 의존성
```bash
# 개발 의존성 포함 설치
uv pip install -e ".[dev]"
```

### 패키지 관리

#### 설치된 패키지 확인
```bash
uv pip list
uv pip freeze
```

#### 패키지 제거
```bash
uv pip uninstall requests
```

#### 패키지 업그레이드
```bash
uv pip install --upgrade requests
```

## 고급 기능

### 의존성 해결

uv는 pip보다 엄격한 의존성 해결을 수행합니다:

```bash
# 의존성 해결 과정 확인
uv pip install requests --verbose

# 의존성 충돌 무시 (권장하지 않음)
uv pip install requests --no-deps
```

### 캐싱

uv는 효율적인 캐싱을 자동으로 수행합니다:

```bash
# 캐시 위치 확인
echo $HOME/.cache/uv

# 캐시 정리
rm -rf ~/.cache/uv
```

### 인덱스 설정

#### 커스텀 인덱스 사용
```bash
# 단일 명령
uv pip install --index-url https://pypi.company.com/simple/ package

# 환경 변수로 설정
export UV_INDEX_URL=https://pypi.company.com/simple/
```

#### 추가 인덱스
```bash
uv pip install --extra-index-url https://pypi.company.com/simple/ package
```

### 프록시 설정

```bash
# HTTP 프록시
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080

# 프록시 예외
export NO_PROXY=localhost,127.0.0.1,.company.com
```

## 문제 해결

### 일반적인 문제

#### 1. "Package not found" 오류
```bash
# 인덱스 갱신
uv pip install --refresh package

# 프리릴리즈 포함
uv pip install --pre package
```

#### 2. 컴파일 오류
```bash
# 바이너리 휠 사용
uv pip install --only-binary :all: package

# 소스에서 빌드
uv pip install --no-binary :all: package
```

#### 3. 의존성 충돌
```bash
# 상세 정보 확인
uv pip install package --verbose

# 의존성 트리 확인
uv pip install pipdeptree
pipdeptree
```

### 디버깅

#### 상세 로그
```bash
uv pip install package -vvv
```

#### 환경 변수
```bash
# 디버그 모드
export UV_DEBUG=1

# 로그 파일
export UV_LOG_FILE=/tmp/uv.log
```

## 모범 사례

### 1. requirements 파일 분리

```
requirements/
├── base.txt       # 공통 의존성
├── dev.txt        # 개발 의존성
├── prod.txt       # 프로덕션 의존성
└── test.txt       # 테스트 의존성
```

```bash
# base.txt
fastapi==0.104.1
pydantic==2.5.0

# dev.txt
-r base.txt
pytest==7.4.3
black==23.11.0

# 사용
uv pip install -r requirements/dev.txt
```

### 2. 버전 고정

```bash
# 현재 환경 고정
uv pip freeze > requirements.lock

# 고정된 버전으로 설치
uv pip sync requirements.lock
```

### 3. CI/CD 최적화

```yaml
# .github/workflows/ci.yml
- name: Cache uv
  uses: actions/cache@v3
  with:
    path: ~/.cache/uv
    key: ${{ runner.os }}-uv-${{ hashFiles('**/requirements*.txt') }}

- name: Install dependencies
  run: |
    curl -LsSf https://astral.sh/uv/install.sh | sh
    uv pip install -r requirements.txt
```

### 4. Docker 최적화

```dockerfile
# 캐시 활용을 위한 레이어 분리
COPY requirements.txt .
RUN uv pip install -r requirements.txt

COPY . .
```

### 5. 개발 워크플로우

```bash
# Makefile
.PHONY: install
install:
	uv pip sync requirements.txt

.PHONY: update
update:
	uv pip install --upgrade -r requirements.txt
	uv pip freeze > requirements.lock
```

## 마이그레이션 체크리스트

- [ ] uv 설치 완료
- [ ] 가상환경 재생성
- [ ] requirements.txt 호환성 확인
- [ ] 개발 스크립트 업데이트
- [ ] CI/CD 파이프라인 수정
- [ ] 팀원 교육 완료

## 추가 리소스

- [uv 공식 문서](https://github.com/astral-sh/uv)
- [성능 벤치마크](./benchmark-results.md)
- [문제 해결 가이드](./troubleshooting.md)
- [팀 Slack 채널](#uv-support)
```

#### SubTask 1.3.2: 마이그레이션 가이드 작성
**담당자**: 시니어 개발자  
**예상 소요시간**: 1시간

```markdown
# docs/migration-guide.md

# pip → uv 마이그레이션 가이드

## 개요
이 문서는 기존 pip 기반 프로젝트를 uv로 안전하게 마이그레이션하는 단계별 가이드입니다.

## 사전 준비

### 1. 현재 상태 백업
```bash
# 현재 패키지 목록 저장
pip freeze > backup/pip_freeze_$(date +%Y%m%d).txt

# 가상환경 정보 저장
pip list --format=json > backup/pip_list_$(date +%Y%m%d).json
```

### 2. uv 설치
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# 설치 확인
uv --version
```

## 단계별 마이그레이션

### Phase 1: 개발 환경 (Day 1-3)

#### Step 1: 테스트 환경 구축
```bash
# 새 브랜치 생성
git checkout -b feature/uv-migration

# 기존 가상환경 백업
mv .venv .venv_pip_backup

# uv로 새 가상환경 생성
uv venv
source .venv/bin/activate
```

#### Step 2: 의존성 설치 테스트
```bash
# 기본 설치 시도
uv pip install -r requirements.txt

# 실패 시 개별 패키지 확인
while read package; do
    echo "Testing: $package"
    uv pip install "$package" || echo "$package" >> failed_packages.txt
done < requirements.txt
```

#### Step 3: 문제 해결
```bash
# 실패한 패키지 분석
cat failed_packages.txt

# 일반적인 해결 방법
# 1. 프리릴리즈 버전 허용
uv pip install --pre problematic-package

# 2. 바이너리 사용
uv pip install --only-binary :all: problematic-package

# 3. 대체 패키지 검토
# psycopg2 → psycopg2-binary
# mysqlclient → pymysql
```

### Phase 2: 스크립트 업데이트 (Day 4-5)

#### Step 1: 개발 스크립트 수정

**setup.sh (이전)**
```bash
#!/bin/bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

**setup.sh (이후)**
```bash
#!/bin/bash
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

uv venv
source .venv/bin/activate
uv pip sync requirements.txt
uv pip install -r requirements-dev.txt
```

#### Step 2: Makefile 업데이트

**Makefile (이전)**
```makefile
install:
	pip install -r requirements.txt

update:
	pip install --upgrade -r requirements.txt
	pip freeze > requirements.txt
```

**Makefile (이후)**
```makefile
install:
	uv pip sync requirements.txt

update:
	uv pip install --upgrade -r requirements.txt
	uv pip freeze > requirements.lock

install-dev:
	uv pip install -r requirements-dev.txt
```

### Phase 3: CI/CD 파이프라인 (Day 6-7)

#### Step 1: GitHub Actions 수정

**이전 (.github/workflows/test.yml)**
```yaml
- name: Install dependencies
  run: |
    pip install --upgrade pip
    pip install -r requirements.txt
```

**이후 (.github/workflows/test.yml)**
```yaml
- name: Install uv
  run: |
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "$HOME/.cargo/bin" >> $GITHUB_PATH

- name: Cache uv
  uses: actions/cache@v3
  with:
    path: ~/.cache/uv
    key: ${{ runner.os }}-uv-${{ hashFiles('requirements.txt') }}

- name: Install dependencies
  run: |
    uv venv
    source .venv/bin/activate
    uv pip install -r requirements.txt
```

#### Step 2: Docker 이미지 업데이트

**Dockerfile (이전)**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
```

**Dockerfile (이후)**
```dockerfile
FROM python:3.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
COPY requirements.txt .
RUN uv venv && . .venv/bin/activate && uv pip install -r requirements.txt
ENV PATH="/app/.venv/bin:$PATH"
COPY . .
```

### Phase 4: 프로덕션 배포 (Day 8-10)

#### Step 1: 단계적 배포
```bash
# 1. 스테이징 환경 배포
./deploy.sh staging uv-test

# 2. 모니터링 (24시간)
# - 성능 메트릭 확인
# - 오류 로그 모니터링
# - 리소스 사용량 체크

# 3. 카나리 배포 (10%)
kubectl set image deployment/api api=api:uv-version -n production
kubectl scale deployment/api --replicas=1 -n production

# 4. 점진적 확대
# 25% → 50% → 100%
```

#### Step 2: 롤백 계획
```bash
#!/bin/bash
# rollback.sh

echo "Rolling back to pip version..."

# 1. 이전 이미지로 복원
kubectl set image deployment/api api=api:pip-version -n production

# 2. 가상환경 복원 (개발 환경)
rm -rf .venv
mv .venv_pip_backup .venv

# 3. CI/CD 설정 복원
git revert --no-commit HEAD~3..HEAD
git commit -m "Rollback to pip"
```

## 검증 체크리스트

### 개발 환경
- [ ] 모든 패키지 정상 설치
- [ ] 테스트 통과
- [ ] 개발 서버 정상 작동
- [ ] IDE 통합 확인

### CI/CD
- [ ] 빌드 시간 단축 확인
- [ ] 모든 테스트 통과
- [ ] 아티팩트 생성 정상

### 프로덕션
- [ ] 성능 메트릭 개선
- [ ] 오류율 변화 없음
- [ ] 리소스 사용량 정상

## 트러블슈팅

### 문제: "Package not found"
```bash
# 해결 1: 인덱스 URL 확인
uv pip install --index-url https://pypi.org/simple package

# 해결 2: 프리릴리즈 포함
uv pip install --pre package
```

### 문제: 컴파일 오류
```bash
# 해결 1: 시스템 의존성 설치
apt-get install build-essential python3-dev

# 해결 2: 바이너리 패키지 사용
uv pip install --only-binary :all: package
```

### 문제: 의존성 충돌
```bash
# 해결: 명시적 버전 지정
uv pip install "package1==1.0.0" "package2==2.0.0"
```

## 성공 지표

| 지표 | 목표 | 측정 방법 |
|------|------|-----------|
| 설치 시간 | 80% 감소 | CI/CD 로그 |
| 캐시 효율 | 90% 히트율 | uv 통계 |
| 개발자 만족도 | 4.5/5 | 설문조사 |
| 오류율 | < 0.1% | 모니터링 |

## 마이그레이션 완료 후

### 1. 문서 업데이트
- README.md의 설치 가이드
- 기여 가이드
- 온보딩 문서

### 2. 팀 교육
- uv 기본 사용법 세션
- 트러블슈팅 워크샵
- Q&A 세션

### 3. 지속적 개선
- 성능 모니터링
- 피드백 수집
- 프로세스 최적화
```

#### SubTask 1.3.3: FAQ 및 트러블슈팅 문서
**담당자**: 지원 엔지니어  
**예상 소요시간**: 1시간

```markdown
# docs/uv-faq-troubleshooting.md

# uv FAQ 및 트러블슈팅

## 자주 묻는 질문 (FAQ)

### 일반 질문

**Q: uv가 pip보다 빠른 이유는?**
A: uv는 Rust로 작성되어 있고, 효율적인 의존성 해결 알고리즘과 병렬 처리를 사용합니다. 또한 더 나은 캐싱 메커니즘을 제공합니다.

**Q: pip와 uv를 함께 사용할 수 있나요?**
A: 기술적으로 가능하지만 권장하지 않습니다. 하나의 프로젝트에서는 일관되게 하나의 도구만 사용하세요.

**Q: uv가 지원하는 Python 버전은?**
A: Python 3.8 이상을 지원합니다. 최적의 성능을 위해 Python 3.10+ 권장합니다.

### 설치 관련

**Q: 기업 프록시 환경에서 uv 설치가 안 됩니다**
A:
```bash
# 프록시 설정
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080

# 설치 재시도
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Q: Windows에서 "명령을 찾을 수 없음" 오류**
A:
```powershell
# PATH에 추가
$env:Path += ";$env:USERPROFILE\.cargo\bin"

# 영구적으로 추가
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$env:USERPROFILE\.cargo\bin", [EnvironmentVariableTarget]::User)
```

### 패키지 설치

**Q: 특정 패키지만 uv로 설치가 안 됩니다**
A: 몇 가지 해결 방법을 시도하세요:
```bash
# 1. 프리릴리즈 버전 허용
uv pip install --pre package

# 2. 특정 소스에서 설치
uv pip install --index-url https://pypi.org/simple package

# 3. 의존성 무시 (주의 필요)
uv pip install --no-deps package
```

**Q: "No matching distribution" 오류**
A:
```bash
# Python 버전 확인
python --version

# 호환 버전 검색
uv pip install package --dry-run --verbose

# 다른 버전 시도
uv pip install "package<2.0" 또는 "package>=1.0,<2.0"
```

## 트러블슈팅

### 🔴 심각한 문제

#### 1. uv가 전혀 실행되지 않음

**증상**: `uv: command not found`

**해결**:
```bash
# PATH 확인
echo $PATH | grep -q .cargo/bin || echo "PATH not set"

# 수동으로 PATH 추가
export PATH="$HOME/.cargo/bin:$PATH"

# shell 설정 파일에 추가
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

#### 2. 세그멘테이션 폴트

**증상**: `Segmentation fault (core dumped)`

**해결**:
```bash
# uv 재설치
rm -rf ~/.cargo/bin/uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 시스템 라이브러리 업데이트
sudo apt-get update && sudo apt-get upgrade

# glibc 버전 확인
ldd --version
```

### 🟡 일반적인 문제

#### 1. 의존성 충돌

**증상**: `ResolutionImpossible` 오류

**해결**:
```bash
# 1. 상세 정보 확인
uv pip install package -vvv

# 2. 의존성 트리 분석
pip install pipdeptree
pipdeptree --packages package

# 3. 수동으로 버전 조정
uv pip install "package1==1.0" "package2>=2.0,<3.0"
```

#### 2. 캐시 문제

**증상**: 오래된 패키지 버전 설치

**해결**:
```bash
# 캐시 위치 확인
ls -la ~/.cache/uv

# 특정 패키지 캐시 삭제
rm -rf ~/.cache/uv/wheels/package*

# 전체 캐시 삭제
rm -rf ~/.cache/uv

# 캐시 무시하고 설치
uv pip install --refresh package
```

#### 3. SSL 인증서 오류

**증상**: `SSL: CERTIFICATE_VERIFY_FAILED`

**해결**:
```bash
# 1. 시스템 인증서 업데이트
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install ca-certificates

# macOS
brew install ca-certificates

# 2. 기업 인증서 추가
export REQUESTS_CA_BUNDLE=/path/to/company-cert.pem
export SSL_CERT_FILE=/path/to/company-cert.pem

# 3. (임시) SSL 검증 비활성화 (보안 주의!)
export UV_INSECURE=true
```

### 🟢 성능 문제

#### 1. 설치가 예상보다 느림

**원인 분석**:
```bash
# 네트워크 속도 확인
curl -o /dev/null http://pypi.org/simple/

# 상세 로그로 병목 확인
uv pip install package -vvv

# 시스템 리소스 확인
htop
```

**최적화**:
```bash
# 병렬 다운로드 수 조정
export UV_CONCURRENT_DOWNLOADS=10

# 가까운 미러 사용
uv pip install --index-url https://pypi.kr/simple package
```

#### 2. 메모리 사용량 높음

**해결**:
```bash
# 메모리 제한 설정
ulimit -v 2097152  # 2GB 제한

# 작은 배치로 설치
uv pip install -r requirements1.txt
uv pip install -r requirements2.txt
```

### 플랫폼별 문제

#### macOS

**문제**: Apple Silicon에서 특정 패키지 설치 실패

```bash
# Rosetta로 실행
arch -x86_64 uv pip install package

# ARM64 네이티브 빌드
export ARCHFLAGS="-arch arm64"
uv pip install package
```

#### Windows

**문제**: 긴 경로명 오류

```powershell
# 긴 경로 지원 활성화
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" `
    -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

#### Linux

**문제**: 권한 오류

```bash
# 사용자 설치 사용
uv pip install --user package

# 가상환경 사용 (권장)
uv venv
source .venv/bin/activate
uv pip install package
```

## 디버깅 도구

### 1. 상세 로깅
```bash
# 최대 상세 레벨
uv pip install package -vvv

# 로그 파일로 저장
uv pip install package -vvv 2>&1 | tee install.log
```

### 2. 환경 정보 수집
```bash
#!/bin/bash
# debug-info.sh

echo "=== System Info ==="
uname -a
python --version
uv --version

echo -e "\n=== Environment ==="
env | grep -E "PYTHON|UV|PATH|PROXY"

echo -e "\n=== uv Config ==="
ls -la ~/.config/uv/

echo -e "\n=== Cache Info ==="
du -sh ~/.cache/uv/
```

### 3. 의존성 분석
```python
# analyze_deps.py
import subprocess
import json

def analyze_package(package):
    # uv로 의존성 정보 수집
    result = subprocess.run(
        ['uv', 'pip', 'show', package],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"✓ {package} 정보:")
        print(result.stdout)
    else:
        print(f"✗ {package} 오류:")
        print(result.stderr)

# 사용
analyze_package('requests')
```

## 지원 채널

### 내부 지원
- Slack: #uv-support
- Wiki: https://wiki.company.com/uv
- 티켓: https://helpdesk.company.com

### 외부 리소스
- GitHub Issues: https://github.com/astral-sh/uv/issues
- Discord: https://discord.gg/astral-sh
- 공식 문서: https://github.com/astral-sh/uv

## 응급 조치

### uv 완전 제거 및 재설치
```bash
#!/bin/bash
# emergency-reset.sh

echo "⚠️  uv 완전 재설정 시작..."

# 1. uv 제거
rm -rf ~/.cargo/bin/uv
rm -rf ~/.cache/uv
rm -rf ~/.config/uv

# 2. pip로 임시 전환
python -m venv .venv_temp
source .venv_temp/bin/activate
pip install -r requirements.txt

# 3. uv 재설치
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.cargo/env

echo "✅ 재설정 완료"
```

---

문제가 지속되면 #uv-support 채널에 다음 정보와 함께 문의하세요:
1. 오류 메시지 전문
2. `uv --version` 출력
3. `python --version` 출력
4. 실행한 명령어
5. requirements.txt 관련 부분
```

---

## 📋 Phase 2: 개발 환경 전환 (Day 4-7)

### Task 2.1: 개발 환경 설정 스크립트 생성

#### SubTask 2.1.1: 플랫폼별 설치 스크립트
**담당자**: DevOps 엔지니어  
**예상 소요시간**: 2시간

```bash
#!/bin/bash
# scripts/install_uv_multiplatform.sh

set -e

# 색상 코드
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 로깅 함수
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# OS 감지
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            OS=$ID
            VER=$VERSION_ID
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        VER=$(sw_vers -productVersion)
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
        VER=$(cmd //c ver 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
    else
        log_error "Unsupported OS: $OSTYPE"
        exit 1
    fi
    
    log_info "Detected OS: $OS $VER"
}

# 아키텍처 감지
detect_arch() {
    ARCH=$(uname -m)
    case $ARCH in
        x86_64)
            ARCH="x86_64"
            ;;
        aarch64|arm64)
            ARCH="aarch64"
            ;;
        *)
            log_error "Unsupported architecture: $ARCH"
            exit 1
            ;;
    esac
    
    log_info "Detected architecture: $ARCH"
}

# Linux 설치
install_linux() {
    log_info "Installing uv for Linux..."
    
    # 필수 패키지 확인
    if command -v apt-get &> /dev/null; then
        log_info "Installing dependencies via apt..."
        sudo apt-get update
        sudo apt-get install -y curl ca-certificates
    elif command -v yum &> /dev/null; then
        log_info "Installing dependencies via yum..."
        sudo yum install -y curl ca-certificates
    fi
    
    # uv 설치
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # PATH 설정
    add_to_path_linux
}

# macOS 설치
install_macos() {
    log_info "Installing uv for macOS..."
    
    # Homebrew 확인
    if command -v brew &> /dev/null; then
        log_info "Installing via Homebrew..."
        brew install uv
    else
        log_info "Installing via install script..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        add_to_path_macos
    fi
    
    # Apple Silicon 특별 처리
    if [[ $ARCH == "aarch64" ]]; then
        log_warn "Apple Silicon detected. Some packages may require Rosetta."
        log_info "To install Rosetta: softwareupdate --install-rosetta"
    fi
}

# Windows 설치
install_windows() {
    log_info "Installing uv for Windows..."
    
    # PowerShell 스크립트 생성
    cat > install_uv_windows.ps1 << 'EOF'
# Requires -RunAsAdministrator

Write-Host "Installing uv for Windows..." -ForegroundColor Green

# 설치 스크립트 다운로드 및 실행
irm https://astral.sh/uv/install.ps1 | iex

# PATH 업데이트
$uvPath = "$env:USERPROFILE\.cargo\bin"
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")

if ($currentPath -notlike "*$uvPath*") {
    [Environment]::SetEnvironmentVariable(
        "Path",
        "$currentPath;$uvPath",
        "User"
    )
    Write-Host "Added uv to PATH" -ForegroundColor Green
}

# 설치 확인
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","User")
uv --version

Write-Host "Installation complete!" -ForegroundColor Green
EOF

    log_info "Please run the following command in PowerShell as Administrator:"
    echo "powershell -ExecutionPolicy Bypass -File install_uv_windows.ps1"
}

# PATH 추가 - Linux
add_to_path_linux() {
    local shell_rc=""
    
    if [[ $SHELL == *"bash"* ]]; then
        shell_rc="$HOME/.bashrc"
    elif [[ $SHELL == *"zsh"* ]]; then
        shell_rc="$HOME/.zshrc"
    elif [[ $SHELL == *"fish"* ]]; then
        shell_rc="$HOME/.config/fish/config.fish"
    fi
    
    if [ -n "$shell_rc" ]; then
        echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> "$shell_rc"
        log_info "Added uv to PATH in $shell_rc"
        log_warn "Please run: source $shell_rc"
    fi
}

# PATH 추가 - macOS
add_to_path_macos() {
    # macOS는 기본적으로 zsh 사용
    local shell_rc="$HOME/.zshrc"
    
    if [ -f "$HOME/.bash_profile" ]; then
        shell_rc="$HOME/.bash_profile"
    fi
    
    echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> "$shell_rc"
    log_info "Added uv to PATH in $shell_rc"
    log_warn "Please run: source $shell_rc"
}

# 설치 확인
verify_installation() {
    log_info "Verifying installation..."
    
    # PATH 새로고침
    export PATH="$HOME/.cargo/bin:$PATH"
    
    if command -v uv &> /dev/null; then
        local version=$(uv --version)
        log_info "✅ uv installed successfully: $version"
        return 0
    else
        log_error "❌ uv installation failed"
        return 1
    fi
}

# 환경 설정
setup_environment() {
    log_info "Setting up uv environment..."
    
    # 캐시 디렉토리 생성
    mkdir -p "$HOME/.cache/uv"
    
    # 설정 파일 생성
    mkdir -p "$HOME/.config/uv"
    cat > "$HOME/.config/uv/config.toml" << EOF
# uv configuration

[cache]
dir = "$HOME/.cache/uv"

[pip]
# 기본 인덱스 URL
index-url = "https://pypi.org/simple"

# 추가 인덱스 (필요 시)
# extra-index-url = ["https://pypi.company.com/simple"]

[install]
# 컴파일 옵션
compile-bytecode = true
EOF

    log_info "Configuration saved to ~/.config/uv/config.toml"
}

# 메인 함수
main() {
    echo "🚀 uv Installation Script"
    echo "========================"
    
    # OS 및 아키텍처 감지
    detect_os
    detect_arch
    
    # OS별 설치
    case $OS in
        ubuntu|debian)
            install_linux
            ;;
        fedora|centos|rhel)
            install_linux
            ;;
        macos)
            install_macos
            ;;
        windows)
            install_windows
            ;;
        *)
            log_error "Unsupported OS: $OS"
            exit 1
            ;;
    esac
    
    # Windows가 아닌 경우 검증 및 설정
    if [[ $OS != "windows" ]]; then
        if verify_installation; then
            setup_environment
            
            echo ""
            echo "✅ Installation complete!"
            echo ""
            echo "Next steps:"
            echo "1. Restart your terminal or run: source ~/.bashrc (or ~/.zshrc)"
            echo "2. Verify installation: uv --version"
            echo "3. Create virtual environment: uv venv"
            echo "4. Install packages: uv pip install -r requirements.txt"
        else
            echo ""
            echo "❌ Installation failed. Please check the errors above."
            exit 1
        fi
    fi
}

# 스크립트 실행
main "$@"
```

#### SubTask 2.1.2: 가상환경 마이그레이션 도구
**담당자**: 백엔드 개발자  
**예상 소요시간**: 3시간

```python
#!/usr/bin/env python3
# scripts/migrate_venv.py

import os
import sys
import json
import shutil
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional

class VenvMigrator:
    """가상환경을 pip에서 uv로 마이그레이션"""
    
    def __init__(self, venv_path: str, backup: bool = True):
        self.venv_path = Path(venv_path)
        self.backup = backup
        self.backup_path = None
        self.report = {
            'start_time': datetime.now().isoformat(),
            'original_venv': str(self.venv_path),
            'packages': [],
            'issues': [],
            'success': False
        }
    
    def check_prerequisites(self) -> bool:
        """사전 요구사항 확인"""
        print("🔍 Checking prerequisites...")
        
        # uv 설치 확인
        if not shutil.which('uv'):
            self.report['issues'].append({
                'type': 'missing_uv',
                'message': 'uv is not installed'
            })
            print("❌ uv is not installed. Please install it first.")
            return False
        
        # 가상환경 확인
        if not self.venv_path.exists():
            self.report['issues'].append({
                'type': 'missing_venv',
                'message': f'Virtual environment not found: {self.venv_path}'
            })
            print(f"❌ Virtual environment not found: {self.venv_path}")
            return False
        
        # Python 실행 파일 확인
        python_exe = self._get_venv_python()
        if not python_exe.exists():
            self.report['issues'].append({
                'type': 'invalid_venv',
                'message': 'Invalid virtual environment structure'
            })
            print("❌ Invalid virtual environment structure")
            return False
        
        print("✅ Prerequisites check passed")
        return True
    
    def _get_venv_python(self) -> Path:
        """가상환경 Python 경로 반환"""
        if sys.platform == 'win32':
            return self.venv_path / 'Scripts' / 'python.exe'
        return self.venv_path / 'bin' / 'python'
    
    def backup_venv(self) -> bool:
        """기존 가상환경 백업"""
        if not self.backup:
            return True
        
        print("💾 Backing up virtual environment...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.backup_path = Path(f"{self.venv_path}_backup_{timestamp}")
        
        try:
            shutil.copytree(self.venv_path, self.backup_path)
            self.report['backup_path'] = str(self.backup_path)
            print(f"✅ Backup created: {self.backup_path}")
            return True
        except Exception as e:
            self.report['issues'].append({
                'type': 'backup_failed',
                'message': str(e)
            })
            print(f"❌ Backup failed: {e}")
            return False
    
    def extract_packages(self) -> List[Dict[str, str]]:
        """현재 설치된 패키지 목록 추출"""
        print("📦 Extracting installed packages...")
        
        python_exe = self._get_venv_python()
        
        try:
            # pip list --format=json 실행
            result = subprocess.run(
                [str(python_exe), '-m', 'pip', 'list', '--format=json'],
                capture_output=True,
                text=True,
                check=True
            )
            
            packages = json.loads(result.stdout)
            
            # 패키지 정보 강화
            enhanced_packages = []
            for pkg in packages:
                # pip show로 상세 정보 가져오기
                show_result = subprocess.run(
                    [str(python_exe), '-m', 'pip', 'show', pkg['name']],
                    capture_output=True,
                    text=True
                )
                
                # Requires 정보 파싱
                requires = []
                if show_result.returncode == 0:
                    for line in show_result.stdout.split('\n'):
                        if line.startswith('Requires:'):
                            requires_str = line.split(':', 1)[1].strip()
                            if requires_str:
                                requires = [r.strip() for r in requires_str.split(',')]
                
                enhanced_packages.append({
                    'name': pkg['name'],
                    'version': pkg['version'],
                    'requires': requires
                })
            
            self.report['packages'] = enhanced_packages
            print(f"✅ Found {len(enhanced_packages)} packages")
            return enhanced_packages
            
        except Exception as e:
            self.report['issues'].append({
                'type': 'package_extraction_failed',
                'message': str(e)
            })
            print(f"❌ Failed to extract packages: {e}")
            return []
    
    def create_requirements_file(self, packages: List[Dict[str, str]]) -> Path:
        """requirements.txt 파일 생성"""
        print("📝 Creating requirements file...")
        
        req_file = Path('requirements_migration.txt')
        
        with open(req_file, 'w') as f:
            for pkg in packages:
                # 시스템 패키지 제외
                if pkg['name'] in ['pip', 'setuptools', 'wheel']:
                    continue
                f.write(f"{pkg['name']}=={pkg['version']}\n")
        
        print(f"✅ Requirements file created: {req_file}")
        return req_file
    
    def create_new_venv(self) -> bool:
        """uv로 새 가상환경 생성"""
        print("🔨 Creating new virtual environment with uv...")
        
        # 임시 이름으로 생성
        temp_venv = Path(f"{self.venv_path}_uv_temp")
        
        try:
            # 기존 임시 환경 제거
            if temp_venv.exists():
                shutil.rmtree(temp_venv)
            
            # uv venv 실행
            result = subprocess.run(
                ['uv', 'venv', str(temp_venv)],
                capture_output=True,
                text=True,
                check=True
            )
            
            self.report['new_venv'] = str(temp_venv)
            print(f"✅ New virtual environment created: {temp_venv}")
            return True
            
        except subprocess.CalledProcessError as e:
            self.report['issues'].append({
                'type': 'venv_creation_failed',
                'message': e.stderr
            })
            print(f"❌ Failed to create virtual environment: {e.stderr}")
            return False
    
    def install_packages(self, req_file: Path) -> Tuple[List[str], List[str]]:
        """uv로 패키지 설치"""
        print("📥 Installing packages with uv...")
        
        temp_venv = Path(self.report.get('new_venv', ''))
        if not temp_venv.exists():
            return [], []
        
        # 가상환경 활성화 스크립트 경로
        if sys.platform == 'win32':
            activate = temp_venv / 'Scripts' / 'activate.bat'
            python_exe = temp_venv / 'Scripts' / 'python.exe'
        else:
            activate = temp_venv / 'bin' / 'activate'
            python_exe = temp_venv / 'bin' / 'python'
        
        success_packages = []
        failed_packages = []
        
        # 전체 설치 시도
        try:
            # Windows와 Unix 계열 구분
            if sys.platform == 'win32':
                cmd = f'"{activate}" && uv pip install -r {req_file}'
                shell = True
            else:
                cmd = f'source "{activate}" && uv pip install -r {req_file}'
                shell = True
            
            result = subprocess.run(
                cmd,
                shell=shell,
                capture_output=True,
                text=True,
                executable='/bin/bash' if sys.platform != 'win32' else None
            )
            
            if result.returncode == 0:
                # 모든 패키지 성공
                with open(req_file, 'r') as f:
                    success_packages = [
                        line.strip() for line in f 
                        if line.strip() and not line.startswith('#')
                    ]
                print(f"✅ All packages installed successfully")
            else:
                # 실패한 경우 개별 설치 시도
                print("⚠️  Bulk installation failed. Trying individual packages...")
                success_packages, failed_packages = self._install_individually(
                    req_file, activate
                )
                
        except Exception as e:
            self.report['issues'].append({
                'type': 'installation_error',
                'message': str(e)
            })
            print(f"❌ Installation error: {e}")
        
        return success_packages, failed_packages
    
    def _install_individually(
        self, 
        req_file: Path, 
        activate: Path
    ) -> Tuple[List[str], List[str]]:
        """패키지를 개별적으로 설치"""
        success = []
        failed = []
        
        with open(req_file, 'r') as f:
            packages = [
                line.strip() for line in f 
                if line.strip() and not line.startswith('#')
            ]
        
        for i, package in enumerate(packages, 1):
            print(f"  [{i}/{len(packages)}] Installing {package}...")
            
            if sys.platform == 'win32':
                cmd = f'"{activate}" && uv pip install {package}'
            else:
                cmd = f'source "{activate}" && uv pip install {package}'
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                executable='/bin/bash' if sys.platform != 'win32' else None
            )
            
            if result.returncode == 0:
                success.append(package)
                print(f"    ✅ Success")
            else:
                failed.append({
                    'package': package,
                    'error': result.stderr
                })
                print(f"    ❌ Failed: {result.stderr.split('error:')[-1].strip()}")
                
                # 대체 방법 시도
                alt_success = self._try_alternative_install(package, activate)
                if alt_success:
                    success.append(package)
                    failed = [f for f in failed if f['package'] != package]
        
        return success, failed
    
    def _try_alternative_install(self, package: str, activate: Path) -> bool:
        """대체 설치 방법 시도"""
        alternatives = [
            '--pre',  # 프리릴리즈 허용
            '--no-deps',  # 의존성 무시
        ]
        
        for alt in alternatives:
            if sys.platform == 'win32':
                cmd = f'"{activate}" && uv pip install {alt} {package}'
            else:
                cmd = f'source "{activate}" && uv pip install {alt} {package}'
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                executable='/bin/bash' if sys.platform != 'win32' else None
            )
            
            if result.returncode == 0:
                print(f"    ✅ Success with {alt}")
                return True
        
        return False
    
    def replace_venv(self) -> bool:
        """기존 가상환경을 새 환경으로 교체"""
        print("🔄 Replacing old virtual environment...")
        
        temp_venv = Path(self.report.get('new_venv', ''))
        if not temp_venv.exists():
            return False
        
        try:
            # 기존 환경 제거
            if self.venv_path.exists():
                shutil.rmtree(self.venv_path)
            
            # 새 환경으로 이동
            shutil.move(str(temp_venv), str(self.venv_path))
            
            print(f"✅ Virtual environment replaced successfully")
            return True
            
        except Exception as e:
            self.report['issues'].append({
                'type': 'replacement_failed',
                'message': str(e)
            })
            print(f"❌ Failed to replace virtual environment: {e}")
            return False
    
    def verify_migration(self) -> bool:
        """마이그레이션 검증"""
        print("🔍 Verifying migration...")
        
        python_exe = self._get_venv_python()
        
        # Python 버전 확인
        try:
            result = subprocess.run(
                [str(python_exe), '--version'],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"  Python version: {result.stdout.strip()}")
            
            # 패키지 수 확인
            result = subprocess.run(
                [str(python_exe), '-m', 'pip', 'list', '--format=json'],
                capture_output=True,
                text=True,
                check=True
            )
            
            packages = json.loads(result.stdout)
            print(f"  Installed packages: {len(packages)}")
            
            # uv 사용 확인
            cfg_file = self.venv_path / 'pyvenv.cfg'
            if cfg_file.exists():
                with open(cfg_file, 'r') as f:
                    content = f.read()
                    if 'uv' in content.lower():
                        print("  ✅ Virtual environment created with uv")
                    else:
                        print("  ⚠️  Virtual environment might not be created with uv")
            
            return True
            
        except Exception as e:
            self.report['issues'].append({
                'type': 'verification_failed',
                'message': str(e)
            })
            print(f"❌ Verification failed: {e}")
            return False
    
    def generate_report(self) -> None:
        """마이그레이션 보고서 생성"""
        self.report['end_time'] = datetime.now().isoformat()
        
        report_file = Path('venv_migration_report.json')
        with open(report_file, 'w') as f:
            json.dump(self.report, f, indent=2)
        
        print(f"\n📊 Migration report saved to: {report_file}")
        
        # 요약 출력
        print("\n=== Migration Summary ===")
        print(f"Original venv: {self.report['original_venv']}")
        print(f"Backup: {self.report.get('backup_path', 'N/A')}")
        print(f"Total packages: {len(self.report['packages'])}")
        print(f"Issues: {len(self.report['issues'])}")
        print(f"Success: {'✅ Yes' if self.report['success'] else '❌ No'}")
    
    def rollback(self) -> bool:
        """백업에서 복원"""
        if not self.backup_path or not self.backup_path.exists():
            print("❌ No backup available for rollback")
            return False
        
        print("⏪ Rolling back to original virtual environment...")
        
        try:
            # 현재 환경 제거
            if self.venv_path.exists():
                shutil.rmtree(self.venv_path)
            
            # 백업 복원
            shutil.copytree(self.backup_path, self.venv_path)
            
            print("✅ Rollback completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            return False
    
    def migrate(self) -> bool:
        """전체 마이그레이션 프로세스 실행"""
        print("🚀 Starting virtual environment migration to uv...\n")
        
        # 1. 사전 확인
        if not self.check_prerequisites():
            return False
        
        # 2. 백업
        if self.backup and not self.backup_venv():
            return False
        
        # 3. 패키지 추출
        packages = self.extract_packages()
        if not packages:
            return False
        
        # 4. Requirements 파일 생성
        req_file = self.create_requirements_file(packages)
        
        # 5. 새 가상환경 생성
        if not self.create_new_venv():
            if self.backup_path:
                self.rollback()
            return False
        
        # 6. 패키지 설치
        success, failed = self.install_packages(req_file)
        
        if failed:
            print(f"\n⚠️  {len(failed)} packages failed to install:")
            for f in failed:
                if isinstance(f, dict):
                    print(f"  - {f['package']}")
                else:
                    print(f"  - {f}")
            
            # 사용자 확인
            response = input("\nContinue with migration? (y/N): ")
            if response.lower() != 'y':
                if self.backup_path:
                    self.rollback()
                return False
        
        # 7. 가상환경 교체
        if not self.replace_venv():
            if self.backup_path:
                self.rollback()
            return False
        
        # 8. 검증
        self.report['success'] = self.verify_migration()
        
        # 9. 보고서 생성
        self.generate_report()
        
        # 10. 정리
        req_file.unlink()
        
        return self.report['success']


def main():
    parser = argparse.ArgumentParser(
        description='Migrate pip virtual environment to uv'
    )
    parser.add_argument(
        'venv_path',
        help='Path to virtual environment'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip backup creation'
    )
    parser.add_argument(
        '--rollback',
        action='store_true',
        help='Rollback to backup'
    )
    
    args = parser.parse_args()
    
    migrator = VenvMigrator(
        args.venv_path,
        backup=not args.no_backup
    )
    
    if args.rollback:
        # 백업에서 복원
        success = migrator.rollback()
    else:
        # 마이그레이션 실행
        success = migrator.migrate()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
```

#### SubTask 2.1.3: IDE 통합 설정
**담당자**: 개발 도구 전문가  
**예상 소요시간**: 1시간

```python
# scripts/setup_ide_integration.py
#!/usr/bin/env python3

import json
import os
from pathlib import Path
from typing import Dict, Any

class IDEIntegrator:
    """주요 IDE에 uv 통합 설정"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        
    def setup_vscode(self):
        """VS Code 설정"""
        print("🔧 Setting up VS Code integration...")
        
        vscode_dir = self.project_root / '.vscode'
        vscode_dir.mkdir(exist_ok=True)
        
        # settings.json
        settings = {
            "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
            "python.terminal.activateEnvironment": True,
            "python.terminal.activateEnvInCurrentTerminal": True,
            "python.linting.enabled": True,
            "python.linting.pylintEnabled": False,
            "python.linting.flake8Enabled": True,
            "python.formatting.provider": "black",
            "python.testing.pytestEnabled": True,
            "python.testing.unittestEnabled": False,
            
            # uv 관련 설정
            "terminal.integrated.env.linux": {
                "PATH": "${env:HOME}/.cargo/bin:${env:PATH}"
            },
            "terminal.integrated.env.osx": {
                "PATH": "${env:HOME}/.cargo/bin:${env:PATH}"
            },
            "terminal.integrated.env.windows": {
                "PATH": "${env:USERPROFILE}\\.cargo\\bin;${env:PATH}"
            },
            
            # 커스텀 태스크
            "python.terminal.executeInFileDir": True,
            
            # 파일 제외
            "files.exclude": {
                "**/__pycache__": True,
                "**/*.pyc": True,
                ".venv": False,  # 가상환경은 표시
                ".venv_pip_backup*": True
            }
        }
        
        settings_file = vscode_dir / 'settings.json'
        if settings_file.exists():
            with open(settings_file, 'r') as f:
                existing = json.load(f)
            existing.update(settings)
            settings = existing
        
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=2)
        
        # tasks.json
        tasks = {
            "version": "2.0.0",
            "tasks": [
                {
                    "label": "uv: Install dependencies",
                    "type": "shell",
                    "command": "uv pip install -r requirements.txt",
                    "group": {
                        "kind": "build",
                        "isDefault": True
                    },
                    "problemMatcher": []
                },
                {
                    "label": "uv: Install dev dependencies",
                    "type": "shell",
                    "command": "uv pip install -r requirements-dev.txt",
                    "group": "build",
                    "problemMatcher": []
                },
                {
                    "label": "uv: Update dependencies",
                    "type": "shell",
                    "command": "uv pip install --upgrade -r requirements.txt",
                    "group": "build",
                    "problemMatcher": []
                },
                {
                    "label": "uv: Create virtual environment",
                    "type": "shell",
                    "command": "uv venv",
                    "group": "build",
                    "problemMatcher": []
                }
            ]
        }
        
        with open(vscode_dir / 'tasks.json', 'w') as f:
            json.dump(tasks, f, indent=2)
        
        # launch.json
        launch = {
            "version": "0.2.0",
            "configurations": [
                {
                    "name": "Python: Current File",
                    "type": "python",
                    "request": "launch",
                    "program": "${file}",
                    "console": "integratedTerminal",
                    "justMyCode": True,
                    "env": {
                        "PYTHONPATH": "${workspaceFolder}"
                    }
                },
                {
                    "name": "Python: FastAPI",
                    "type": "python",
                    "request": "launch",
                    "module": "uvicorn",
                    "args": [
                        "app.main:app",
                        "--reload",
                        "--host",
                        "0.0.0.0",
                        "--port",
                        "8000"
                    ],
                    "jinja": True,
                    "justMyCode": True,
                    "env": {
                        "PYTHONPATH": "${workspaceFolder}"
                    }
                }
            ]
        }
        
        with open(vscode_dir / 'launch.json', 'w') as f:
            json.dump(launch, f, indent=2)
        
        # extensions.json
        extensions = {
            "recommendations": [
                "ms-python.python",
                "ms-python.vscode-pylance",
                "ms-python.black-formatter",
                "charliermarsh.ruff",
                "ms-vscode.makefile-tools"
            ]
        }
        
        with open(vscode_dir / 'extensions.json', 'w') as f:
            json.dump(extensions, f, indent=2)
        
        print("✅ VS Code configuration complete")
    
    def setup_pycharm(self):
        """PyCharm 설정"""
        print("🔧 Setting up PyCharm integration...")
        
        idea_dir = self.project_root / '.idea'
        idea_dir.mkdir(exist_ok=True)
        
        # 환경 변수 설정
        env_xml = '''<component name="EnvironmentVariables">
  <envs>
    <env name="PATH" value="$USER_HOME$/.cargo/bin:$PATH$" />
  </envs>
</component>'''
        
        # 외부 도구 설정
        external_tools = '''<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="ExternalTools">
    <tool name="uv install" description="Install dependencies with uv" showInMainMenu="true" showInEditor="false" showInProject="true" showInSearchPopup="false" disabled="false" useConsole="true" showConsoleOnStdOut="false" showConsoleOnStdErr="false" synchronizeAfterRun="true">
      <exec>
        <option name="COMMAND" value="uv" />
        <option name="PARAMETERS" value="pip install -r requirements.txt" />
        <option name="WORKING_DIRECTORY" value="$ProjectFileDir$" />
      </exec>
    </tool>
    <tool name="uv update" description="Update dependencies with uv" showInMainMenu="true" showInEditor="false" showInProject="true" showInSearchPopup="false" disabled="false" useConsole="true" showConsoleOnStdOut="false" showConsoleOnStdErr="false" synchronizeAfterRun="true">
      <exec>
        <option name="COMMAND" value="uv" />
        <option name="PARAMETERS" value="pip install --upgrade -r requirements.txt" />
        <option name="WORKING_DIRECTORY" value="$ProjectFileDir$" />
      </exec>
    </tool>
  </component>
</project>'''
        
        with open(idea_dir / 'externalTools.xml', 'w') as f:
            f.write(external_tools)
        
        # 실행 구성
        run_config = '''<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="RunConfigurationProducerService">
    <option name="ignoredProducers">
      <set>
        <option value="com.jetbrains.python.run.PythonRunConfigurationProducer" />
      </set>
    </option>
  </component>
  <component name="RunManager">
    <configuration name="Run with uv" type="PythonConfigurationType" factoryName="Python">
      <module name="$PROJECT_NAME$" />
      <option name="INTERPRETER_OPTIONS" value="" />
      <option name="PARENT_ENVS" value="true" />
      <envs>
        <env name="PYTHONUNBUFFERED" value="1" />
        <env name="PATH" value="$USER_HOME$/.cargo/bin:$PATH$" />
      </envs>
      <option name="SDK_HOME" value="$PROJECT_DIR$/.venv/bin/python" />
      <option name="WORKING_DIRECTORY" value="$PROJECT_DIR$" />
      <option name="IS_MODULE_SDK" value="false" />
      <option name="ADD_CONTENT_ROOTS" value="true" />
      <option name="ADD_SOURCE_ROOTS" value="true" />
      <option name="SCRIPT_NAME" value="" />
      <option name="PARAMETERS" value="" />
      <option name="SHOW_COMMAND_LINE" value="false" />
      <option name="EMULATE_TERMINAL" value="false" />
      <option name="MODULE_MODE" value="false" />
      <option name="REDIRECT_INPUT" value="false" />
      <option name="INPUT_FILE" value="" />
      <method v="2" />
    </configuration>
  </component>
</project>'''
        
        with open(idea_dir / 'runConfigurations.xml', 'w') as f:
            f.write(run_config)
        
        # 사용 가이드 생성
        guide = '''# PyCharm uv Integration Guide

## Setup Complete! 

### Using uv in PyCharm:

1. **Terminal**: uv is available in the integrated terminal
2. **External Tools**: Tools → External Tools → uv install/update
3. **Python Interpreter**: Settings → Project → Python Interpreter → .venv/bin/python

### Keyboard Shortcuts:
- Install dependencies: Assign shortcut in Settings → Keymap → External Tools
- Update dependencies: Assign shortcut in Settings → Keymap → External Tools

### Tips:
- Use File Watchers to auto-install when requirements.txt changes
- Configure pre-commit hooks in Version Control settings
'''
        
        with open(self.project_root / 'PYCHARM_UV_GUIDE.md', 'w') as f:
            f.write(guide)
        
        print("✅ PyCharm configuration complete")
        print("📖 See PYCHARM_UV_GUIDE.md for usage instructions")
    
    def setup_vim(self):
        """Vim/Neovim 설정"""
        print("🔧 Setting up Vim/Neovim integration...")
        
        # .vimrc 또는 init.vim 설정
        vim_config = '''
" uv integration for Python development

" 가상환경 자동 활성화
let g:python3_host_prog = getcwd() . '/.venv/bin/python'

" ALE (Asynchronous Lint Engine) 설정
let g:ale_python_auto_virtualenv = 1
let g:ale_virtualenv_dir_names = ['.venv']

" 커스텀 명령어
command! UvInstall :!uv pip install -r requirements.txt
command! UvUpdate :!uv pip install --upgrade -r requirements.txt
command! UvFreeze :!uv pip freeze > requirements.lock
command! UvList :!uv pip list

" 키 매핑
nnoremap <leader>ui :UvInstall<CR>
nnoremap <leader>uu :UvUpdate<CR>
nnoremap <leader>uf :UvFreeze<CR>
nnoremap <leader>ul :UvList<CR>

" 자동 명령
autocmd BufWritePost requirements*.txt :UvInstall

" 상태 표시줄에 가상환경 표시
set statusline+=%{virtualenv#statusline()}
'''
        
        # 홈 디렉토리에 저장
        vimrc_path = Path.home() / '.vimrc.uv'
        with open(vimrc_path, 'w') as f:
            f.write(vim_config)
        
        # Neovim Lua 설정
        nvim_config = '''
-- uv integration for Neovim

-- 가상환경 설정
vim.g.python3_host_prog = vim.fn.getcwd() .. '/.venv/bin/python'

-- 커스텀 명령어
vim.api.nvim_create_user_command('UvInstall', '!uv pip install -r requirements.txt', {})
vim.api.nvim_create_user_command('UvUpdate', '!uv pip install --upgrade -r requirements.txt', {})
vim.api.nvim_create_user_command('UvFreeze', '!uv pip freeze > requirements.lock', {})
vim.api.nvim_create_user_command('UvList', '!uv pip list', {})

-- 키 매핑
vim.keymap.set('n', '<leader>ui', ':UvInstall<CR>')
vim.keymap.set('n', '<leader>uu', ':UvUpdate<CR>')
vim.keymap.set('n', '<leader>uf', ':UvFreeze<CR>')
vim.keymap.set('n', '<leader>ul', ':UvList<CR>')

-- 자동 명령
vim.api.nvim_create_autocmd("BufWritePost", {
    pattern = "requirements*.txt",
    command = "UvInstall"
})
'''
        
        nvim_config_dir = Path.home() / '.config' / 'nvim'
        nvim_config_dir.mkdir(parents=True, exist_ok=True)
        
        with open(nvim_config_dir / 'uv.lua', 'w') as f:
            f.write(nvim_config)
        
        print("✅ Vim/Neovim configuration complete")
        print("📝 Add 'source ~/.vimrc.uv' to your .vimrc")
        print("📝 Add 'require(\"uv\")' to your init.lua for Neovim")
    
    def generate_editorconfig(self):
        """EditorConfig 파일 생성"""
        editorconfig = '''# EditorConfig is awesome: https://EditorConfig.org

root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.py]
indent_style = space
indent_size = 4
max_line_length = 88

[*.{json,yml,yaml,toml}]
indent_style = space
indent_size = 2

[Makefile]
indent_style = tab

[*.md]
trim_trailing_whitespace = false
'''
        
        with open(self.project_root / '.editorconfig', 'w') as f:
            f.write(editorconfig)
    
    def run(self):
        """모든 IDE 설정 실행"""
        print("🚀 Setting up IDE integrations for uv...\n")
        
        # VS Code
        self.setup_vscode()
        print()
        
        # PyCharm
        self.setup_pycharm()
        print()
        
        # Vim/Neovim
        self.setup_vim()
        print()
        
        # EditorConfig
        self.generate_editorconfig()
        print("✅ Created .editorconfig")
        
        print("\n✅ All IDE integrations configured!")
        print("\n📌 Next steps:")
        print("1. Restart your IDE")
        print("2. Select Python interpreter from .venv")
        print("3. Install recommended extensions")


if __name__ == '__main__':
    integrator = IDEIntegrator()
    integrator.run()
```

### Task 2.2: pyproject.toml 마이그레이션

#### SubTask 2.2.1: 의존성 구조 분석
**담당자**: 백엔드 리드  
**예상 소요시간**: 2시간

```python
#!/usr/bin/env python3
# scripts/analyze_dependencies.py

import re
import ast
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
import json
import graphviz

class DependencyAnalyzer:
    """프로젝트 의존성 구조 분석"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.dependencies = defaultdict(set)
        self.import_map = defaultdict(set)
        self.package_usage = defaultdict(set)
        
    def analyze_imports(self) -> Dict[str, Set[str]]:
        """모든 Python 파일의 import 분석"""
        print("🔍 Analyzing Python imports...")
        
        py_files = list(self.project_root.rglob("*.py"))
        
        for py_file in py_files:
            if '.venv' in str(py_file) or '__pycache__' in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                imports = self._extract_imports(tree)
                
                relative_path = py_file.relative_to(self.project_root)
                self.import_map[str(relative_path)] = imports
                
                # 패키지별 사용 파일 매핑
                for imp in imports:
                    base_package = imp.split('.')[0]
                    self.package_usage[base_package].add(str(relative_path))
                    
            except Exception as e:
                print(f"  ⚠️  Error analyzing {py_file}: {e}")
        
        print(f"  ✅ Analyzed {len(py_files)} Python files")
        return dict(self.import_map)
    
    def _extract_imports(self, tree: ast.AST) -> Set[str]:
        """AST에서 import 추출"""
        imports = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)
        
        return imports
    
    def analyze_requirements(self) -> Dict[str, List[Dict[str, str]]]:
        """requirements 파일 분석"""
        print("📦 Analyzing requirements files...")
        
        req_files = list(self.project_root.glob("requirements*.txt"))
        requirements = {}
        
        for req_file in req_files:
            packages = []
            
            with open(req_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # -r 다른파일 처리
                        if line.startswith('-r '):
                            ref_file = line[3:].strip()
                            ref_path = req_file.parent / ref_file
                            if ref_path.exists():
                                sub_packages = self._parse_requirements_file(ref_path)
                                packages.extend(sub_packages)
                        else:
                            package_info = self._parse_requirement_line(line)
                            if package_info:
                                packages.append(package_info)
            
            requirements[req_file.name] = packages
            print(f"  ✅ {req_file.name}: {len(packages)} packages")
        
        return requirements
    
    def _parse_requirement_line(self, line: str) -> Optional[Dict[str, str]]:
        """requirements 라인 파싱"""
        # 다양한 형식 지원
        patterns = [
            # package==1.0.0
            r'^([a-zA-Z0-9\-_]+)==([0-9\.]+.*)$',
            # package>=1.0.0,<2.0.0
            r'^([a-zA-Z0-9\-_]+)([><=~]+.*)$',
            # package[extra]==1.0.0
            r'^([a-zA-Z0-9\-_]+)\[([^\]]+)\]([><=~]+.*)$',
            # git+https://...
            r'^git\+(.+)#egg=([a-zA-Z0-9\-_]+)$',
            # -e ./path
            r'^-e\s+(.+)$',
        ]
        
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                if pattern.startswith('^git'):
                    return {
                        'name': match.group(2),
                        'version': 'git',
                        'source': match.group(1),
                        'original': line
                    }
                elif pattern.startswith('^-e'):
                    return {
                        'name': 'editable',
                        'version': 'local',
                        'path': match.group(1),
                        'original': line
                    }
                elif '[' in pattern:
                    return {
                        'name': match.group(1),
                        'extras': match.group(2),
                        'version': match.group(3),
                        'original': line
                    }
                else:
                    return {
                        'name': match.group(1),
                        'version': match.group(2) if len(match.groups()) > 1 else 'any',
                        'original': line
                    }
        
        # 단순 패키지명
        if re.match(r'^[a-zA-Z0-9\-_]+$', line):
            return {
                'name': line,
                'version': 'any',
                'original': line
            }
        
        return None
    
    def _parse_requirements_file(self, path: Path) -> List[Dict[str, str]]:
        """requirements 파일 파싱"""
        packages = []
        
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('-r '):
                    package_info = self._parse_requirement_line(line)
                    if package_info:
                        packages.append(package_info)
        
        return packages
    
    def categorize_dependencies(self) -> Dict[str, List[str]]:
        """의존성을 카테고리별로 분류"""
        print("🏷️  Categorizing dependencies...")
        
        categories = {
            'core': [],           # 핵심 프레임워크
            'database': [],       # 데이터베이스
            'web': [],           # 웹 관련
            'ml': [],            # 머신러닝
            'testing': [],       # 테스트
            'linting': [],       # 린팅/포맷팅
            'development': [],   # 개발 도구
            'deployment': [],    # 배포
            'utilities': []      # 유틸리티
        }
        
        # 카테고리 매핑
        category_patterns = {
            'core': ['fastapi', 'django', 'flask', 'starlette', 'uvicorn', 'gunicorn'],
            'database': ['sqlalchemy', 'psycopg', 'pymongo', 'redis', 'alembic', 'asyncpg'],
            'web': ['requests', 'httpx', 'aiohttp', 'beautifulsoup', 'selenium', 'httptools'],
            'ml': ['langchain', 'openai', 'anthropic', 'transformers', 'torch', 'tensorflow', 'numpy', 'pandas', 'scikit-learn'],
            'testing': ['pytest', 'unittest', 'mock', 'faker', 'factory-boy', 'hypothesis'],
            'linting': ['black', 'flake8', 'pylint', 'mypy', 'ruff', 'isort', 'bandit'],
            'development': ['ipython', 'jupyter', 'notebook', 'ipdb', 'rich', 'click'],
            'deployment': ['docker', 'kubernetes', 'ansible', 'fabric', 'supervisor'],
            'utilities': ['python-dotenv', 'pydantic', 'celery', 'schedule', 'arrow', 'pendulum']
        }
        
        # 모든 requirements 파일에서 패키지 수집
        all_packages = set()
        requirements = self.analyze_requirements()
        
        for req_file, packages in requirements.items():
            for pkg in packages:
                all_packages.add(pkg['name'])
        
        # 카테고리별 분류
        categorized = set()
        
        for category, patterns in category_patterns.items():
            for package in all_packages:
                package_lower = package.lower()
                for pattern in patterns:
                    if pattern in package_lower:
                        categories[category].append(package)
                        categorized.add(package)
                        break
        
        # 미분류 패키지
        uncategorized = all_packages - categorized
        categories['utilities'].extend(list(uncategorized))
        
        # 결과 출력
        for category, packages in categories.items():
            if packages:
                print(f"  {category}: {len(packages)} packages")
        
        return categories
    
    def detect_unused_dependencies(self) -> List[str]:
        """사용하지 않는 의존성 감지"""
        print("🔍 Detecting unused dependencies...")
        
        # import 분석
        self.analyze_imports()
        
        # 설치된 패키지와 import 비교
        installed_packages = set()
        requirements = self.analyze_requirements()
        
        for packages in requirements.values():
            for pkg in packages:
                installed_packages.add(pkg['name'].lower())
        
        # 실제 사용되는 패키지
        used_packages = set()
        for imports in self.import_map.values():
            for imp in imports:
                base_package = imp.split('.')[0].lower()
                used_packages.add(base_package)
        
        # import 이름과 패키지 이름 매핑 (일부 패키지는 import 이름이 다름)
        package_import_map = {
            'pillow': 'PIL',
            'beautifulsoup4': 'bs4',
            'python-jose': 'jose',
            'python-multipart': 'multipart',
            'python-dotenv': 'dotenv',
            'scikit-learn': 'sklearn',
            'msgpack-python': 'msgpack',
            'mysqlclient': 'MySQLdb',
            'psycopg2-binary': 'psycopg2',
        }
        
        # 역매핑도 생성
        import_package_map = {v.lower(): k for k, v in package_import_map.items()}
        
        # 사용하지 않는 패키지 찾기
        unused = []
        for package in installed_packages:
            # 패키지 이름으로 확인
            if package not in used_packages:
                # import 이름으로도 확인
                import_name = package_import_map.get(package, package)
                if import_name.lower() not in used_packages:
                    # 개발/테스트 도구는 제외
                    dev_tools = ['pytest', 'black', 'flake8', 'mypy', 'ruff', 'pre-commit', 'ipython', 'ipdb']
                    if not any(tool in package for tool in dev_tools):
                        unused.append(package)
        
        if unused:
            print(f"  ⚠️  Found {len(unused)} potentially unused packages:")
            for pkg in sorted(unused):
                # 해당 패키지가 어느 requirements 파일에 있는지 표시
                files = []
                for req_file, packages in requirements.items():
                    if any(p['name'].lower() == pkg for p in packages):
                        files.append(req_file)
                print(f"    - {pkg} (in {', '.join(files)})")
        else:
            print("  ✅ No unused dependencies detected")
        
        return unused
    
    def generate_dependency_graph(self) -> None:
        """의존성 그래프 생성"""
        print("📊 Generating dependency graph...")
        
        # graphviz 객체 생성
        dot = graphviz.Digraph(comment='Dependency Graph')
        dot.attr(rankdir='TB', size='10,10')
        
        # 색상 정의
        colors = {
            'core': '#FF6B6B',
            'database': '#4ECDC4',
            'web': '#45B7D1',
            'ml': '#96CEB4',
            'testing': '#FECA57',
            'linting': '#FF9FF3',
            'development': '#54A0FF',
            'deployment': '#48DBFB',
            'utilities': '#C8C8C8'
        }
        
        # 카테고리별 의존성
        categories = self.categorize_dependencies()
        
        # 노드 추가
        for category, packages in categories.items():
            with dot.subgraph(name=f'cluster_{category}') as c:
                c.attr(label=category.title(), style='filled', color=colors.get(category, 'lightgrey'))
                for package in packages:
                    c.node(package, shape='box', style='filled', fillcolor='white')
        
        # import 관계 추가
        for file_path, imports in self.import_map.items():
            if 'test' not in file_path:  # 테스트 파일 제외
                for imp in imports:
                    base_import = imp.split('.')[0]
                    # 프로젝트 내부 import 표시
                    if base_import in ['app', 'src', 'api', 'core']:
                        dot.edge(file_path, base_import, style='dashed', color='grey')
        
        # 그래프 저장
        output_path = self.project_root / 'dependency_graph'
        dot.render(output_path, format='png', cleanup=True)
        print(f"  ✅ Dependency graph saved to {output_path}.png")
    
    def generate_report(self) -> Dict[str, any]:
        """종합 분석 보고서 생성"""
        print("\n📊 Generating dependency analysis report...")
        
        # 분석 수행
        imports = self.analyze_imports()
        requirements = self.analyze_requirements()
        categories = self.categorize_dependencies()
        unused = self.detect_unused_dependencies()
        
        # 통계 생성
        total_packages = sum(len(pkgs) for pkgs in requirements.values())
        total_imports = len(set().union(*self.import_map.values()))
        
        report = {
            'summary': {
                'total_packages': total_packages,
                'total_imports': total_imports,
                'total_files_analyzed': len(imports),
                'unused_dependencies': len(unused)
            },
            'requirements_files': requirements,
            'categories': categories,
            'unused_dependencies': unused,
            'package_usage': {
                pkg: list(files) for pkg, files in self.package_usage.items()
                if len(files) > 0
            },
            'recommendations': self._generate_recommendations(categories, unused)
        }
        
        # JSON 파일로 저장
        with open(self.project_root / 'dependency_analysis.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        # Markdown 보고서 생성
        self._generate_markdown_report(report)
        
        print("✅ Report generated: dependency_analysis.json & dependency_analysis.md")
        
        return report
    
    def _generate_recommendations(self, categories: Dict, unused: List) -> List[str]:
        """개선 권장사항 생성"""
        recommendations = []
        
        # 사용하지 않는 패키지
        if unused:
            recommendations.append(f"Remove {len(unused)} unused packages to reduce dependencies")
        
        # 중복 기능 패키지
        if 'requests' in categories.get('web', []) and 'httpx' in categories.get('web', []):
            recommendations.append("Consider using only httpx instead of both requests and httpx")
        
        # 개발 의존성 분리
        dev_deps = len(categories.get('testing', [])) + len(categories.get('linting', [])) + len(categories.get('development', []))
        if dev_deps > 10:
            recommendations.append("Consider separating development dependencies into requirements-dev.txt")
        
        # 버전 고정
        all_packages = []
        for packages in self.analyze_requirements().values():
            all_packages.extend(packages)
        
        unpinned = [p for p in all_packages if p['version'] == 'any']
        if unpinned:
            recommendations.append(f"Pin versions for {len(unpinned)} packages for reproducible builds")
        
        return recommendations
    
    def _generate_markdown_report(self, report: Dict) -> None:
        """Markdown 형식 보고서 생성"""
        md_content = f"""# Dependency Analysis Report

Generated: {import datetime; datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

- **Total Packages**: {report['summary']['total_packages']}
- **Total Imports**: {report['summary']['total_imports']}
- **Files Analyzed**: {report['summary']['total_files_analyzed']}
- **Unused Dependencies**: {report['summary']['unused_dependencies']}

## Dependencies by Category

"""
        
        for category, packages in report['categories'].items():
            if packages:
                md_content += f"### {category.title()} ({len(packages)} packages)\n"
                for pkg in sorted(packages):
                    md_content += f"- {pkg}\n"
                md_content += "\n"
        
        if report['unused_dependencies']:
            md_content += "## Unused Dependencies\n\n"
            md_content += "The following packages appear to be unused:\n\n"
            for pkg in report['unused_dependencies']:
                md_content += f"- {pkg}\n"
            md_content += "\n"
        
        if report['recommendations']:
            md_content += "## Recommendations\n\n"
            for i, rec in enumerate(report['recommendations'], 1):
                md_content += f"{i}. {rec}\n"
        
        md_content += "\n## Package Usage\n\n"
        md_content += "Top 10 most used packages:\n\n"
        
        # 사용 빈도 정렬
        usage_sorted = sorted(
            report['package_usage'].items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:10]
        
        for pkg, files in usage_sorted:
            md_content += f"- **{pkg}**: Used in {len(files)} files\n"
        
        with open(self.project_root / 'dependency_analysis.md', 'w') as f:
            f.write(md_content)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze project dependencies')
    parser.add_argument('--path', default='.', help='Project root path')
    parser.add_argument('--graph', action='store_true', help='Generate dependency graph')
    
    args = parser.parse_args()
    
    analyzer = DependencyAnalyzer(args.path)
    report = analyzer.generate_report()
    
    if args.graph:
        analyzer.generate_dependency_graph()
    
    print("\n✅ Analysis complete!")


if __name__ == '__main__':
    main()
```

#### SubTask 2.2.2: pyproject.toml 생성 및 검증
**담당자**: 빌드 엔지니어  
**예상 소요시간**: 3시간

```python
#!/usr/bin/env python3
# scripts/generate_pyproject.py

import toml
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
import re
from packaging.version import Version
from packaging.specifiers import SpecifierSet

class PyProjectGenerator:
    """requirements.txt를 pyproject.toml로 변환"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.config = {
            'project': {},
            'build-system': {},
            'tool': {}
        }
    
    def analyze_project_metadata(self) -> Dict[str, Any]:
        """프로젝트 메타데이터 수집"""
        print("📋 Collecting project metadata...")
        
        metadata = {
            'name': 'ai-agent-framework',
            'version': '0.1.0',
            'description': '',
            'authors': [],
            'license': 'MIT',
            'readme': 'README.md',
            'requires-python': '>=3.11',
            'homepage': '',
            'repository': '',
            'keywords': []
        }
        
        # setup.py가 있으면 정보 추출
        setup_py = self.project_root / 'setup.py'
        if setup_py.exists():
            metadata.update(self._extract_from_setup_py(setup_py))
        
        # README에서 설명 추출
        readme_files = ['README.md', 'README.rst', 'README.txt']
        for readme in readme_files:
            readme_path = self.project_root / readme
            if readme_path.exists():
                metadata['readme'] = readme
                with open(readme_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 첫 단락을 설명으로 사용
                    lines = content.split('\n')
                    for line in lines:
                        if line.strip() and not line.startswith('#'):
                            metadata['description'] = line.strip()
                            break
                break
        
        # Git 정보에서 저자와 저장소 URL 추출
        try:
            # 저자 정보
            result = subprocess.run(
                ['git', 'config', 'user.name'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                name = result.stdout.strip()
                email_result = subprocess.run(
                    ['git', 'config', 'user.email'],
                    capture_output=True,
                    text=True
                )
                email = email_result.stdout.strip() if email_result.returncode == 0 else ''
                metadata['authors'] = [{'name': name, 'email': email}]
            
            # 저장소 URL
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                repo_url = result.stdout.strip()
                # SSH를 HTTPS로 변환
                if repo_url.startswith('git@github.com:'):
                    repo_url = repo_url.replace('git@github.com:', 'https://github.com/')
                if repo_url.endswith('.git'):
                    repo_url = repo_url[:-4]
                metadata['repository'] = repo_url
                metadata['homepage'] = repo_url
        except:
            pass
        
        # Python 버전 확인
        py_version_file = self.project_root / '.python-version'
        if py_version_file.exists():
            with open(py_version_file, 'r') as f:
                version = f.read().strip()
                metadata['requires-python'] = f'>={version}'
        
        return metadata
    
    def _extract_from_setup_py(self, setup_py: Path) -> Dict[str, Any]:
        """setup.py에서 메타데이터 추출"""
        metadata = {}
        
        try:
            with open(setup_py, 'r') as f:
                content = f.read()
            
            # 정규식으로 기본 정보 추출
            patterns = {
                'name': r"name\s*=\s*['\"]([^'\"]+)['\"]",
                'version': r"version\s*=\s*['\"]([^'\"]+)['\"]",
                'description': r"description\s*=\s*['\"]([^'\"]+)['\"]",
                'author': r"author\s*=\s*['\"]([^'\"]+)['\"]",
                'author_email': r"author_email\s*=\s*['\"]([^'\"]+)['\"]",
                'url': r"url\s*=\s*['\"]([^'\"]+)['\"]",
                'license': r"license\s*=\s*['\"]([^'\"]+)['\"]",
            }
            
            for key, pattern in patterns.items():
                match = re.search(pattern, content)
                if match:
                    if key == 'author':
                        metadata['authors'] = [{'name': match.group(1)}]
                    elif key == 'author_email' and 'authors' in metadata:
                        metadata['authors'][0]['email'] = match.group(1)
                    elif key == 'url':
                        metadata['homepage'] = match.group(1)
                    else:
                        metadata[key] = match.group(1)
            
        except Exception as e:
            print(f"  ⚠️  Error reading setup.py: {e}")
        
        return metadata
    
    def parse_requirements(self) -> Dict[str, List[str]]:
        """requirements 파일 파싱 및 분류"""
        print("📦 Parsing requirements files...")
        
        dependencies = {
            'main': [],
            'dev': [],
            'test': [],
            'docs': [],
            'optional': {}
        }
        
        # requirements 파일 매핑
        file_mapping = {
            'requirements.txt': 'main',
            'requirements-dev.txt': 'dev',
            'requirements-test.txt': 'test',
            'requirements-docs.txt': 'docs',
            'dev-requirements.txt': 'dev',
            'test-requirements.txt': 'test'
        }
        
        for req_file, category in file_mapping.items():
            req_path = self.project_root / req_file
            if req_path.exists():
                deps = self._parse_requirements_file(req_path)
                dependencies[category].extend(deps)
                print(f"  ✅ {req_file}: {len(deps)} dependencies")
        
        # 중복 제거
        main_packages = {self._get_package_name(dep): dep for dep in dependencies['main']}
        
        # dev에서 main과 중복된 것 제거
        dev_packages = []
        for dep in dependencies['dev']:
            pkg_name = self._get_package_name(dep)
            if pkg_name not in main_packages:
                dev_packages.append(dep)
        dependencies['dev'] = dev_packages
        
        return dependencies
    
    def _parse_requirements_file(self, file_path: Path) -> List[str]:
        """requirements 파일 파싱"""
        dependencies = []
        
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                
                # 주석과 빈 줄 제외
                if not line or line.startswith('#'):
                    continue
                
                # -r 다른 파일 참조
                if line.startswith('-r '):
                    ref_file = line[3:].strip()
                    ref_path = file_path.parent / ref_file
                    if ref_path.exists():
                        dependencies.extend(self._parse_requirements_file(ref_path))
                    continue
                
                # -e 편집 가능 설치
                if line.startswith('-e '):
                    # 로컬 패키지는 pyproject.toml에서 다르게 처리
                    continue
                
                # 특수 형식 변환
                dependency = self._convert_requirement_format(line)
                if dependency:
                    dependencies.append(dependency)
        
        return dependencies
    
    def _convert_requirement_format(self, requirement: str) -> Optional[str]:
        """requirements 형식을 pyproject.toml 형식으로 변환"""
        # Git URL
        if requirement.startswith('git+'):
            match = re.match(r'git\+([^@#]+)(?:@([^#]+))?(?:#egg=(.+))?', requirement)
            if match:
                url, ref, name = match.groups()
                if not name:
                    # URL에서 프로젝트 이름 추출
                    name = url.rstrip('/').split('/')[-1].replace('.git', '')
                
                if ref:
                    return f'{name} @ git+{url}@{ref}'
                else:
                    return f'{name} @ git+{url}'
        
        # 일반 패키지
        return requirement
    
    def _get_package_name(self, requirement: str) -> str:
        """requirement에서 패키지 이름 추출"""
        # @ 형식 (git 등)
        if ' @ ' in requirement:
            return requirement.split(' @ ')[0].strip()
        
        # 버전 지정자 제거
        for op in ['==', '>=', '<=', '>', '<', '~=', '!=']:
            if op in requirement:
                return requirement.split(op)[0].strip()
        
        # extras 제거
        if '[' in requirement:
            return requirement.split('[')[0].strip()
        
        return requirement.strip()
    
    def generate_pyproject_toml(self) -> Dict[str, Any]:
        """pyproject.toml 생성"""
        print("🔨 Generating pyproject.toml...")
        
        # 프로젝트 메타데이터
        metadata = self.analyze_project_metadata()
        
        # 의존성 파싱
        dependencies = self.parse_requirements()
        
        # [project] 섹션
        self.config['project'] = {
            'name': metadata['name'],
            'version': metadata['version'],
            'description': metadata['description'],
            'readme': metadata['readme'],
            'requires-python': metadata['requires-python'],
            'license': {'text': metadata['license']},
            'authors': metadata['authors'],
            'dependencies': dependencies['main']
        }
        
        if metadata.get('homepage'):
            self.config['project']['urls'] = {
                'Homepage': metadata['homepage'],
                'Repository': metadata.get('repository', metadata['homepage']),
                'Issues': f"{metadata.get('repository', metadata['homepage'])}/issues"
            }
        
        # [project.optional-dependencies] 섹션
        optional_deps = {}
        if dependencies['dev']:
            optional_deps['dev'] = dependencies['dev']
        if dependencies['test']:
            optional_deps['test'] = dependencies['test']
        if dependencies['docs']:
            optional_deps['docs'] = dependencies['docs']
        
        # all extras
        all_extras = []
        for deps in optional_deps.values():
            all_extras.extend(deps)
        optional_deps['all'] = list(set(all_extras))
        
        if optional_deps:
            self.config['project']['optional-dependencies'] = optional_deps
        
        # [build-system] 섹션
        self.config['build-system'] = {
            'requires': ['setuptools>=68.0.0', 'wheel'],
            'build-backend': 'setuptools.build_meta'
        }
        
        # [tool] 섹션
        self.config['tool'] = self._generate_tool_config()
        
        return self.config
    
    def _generate_tool_config(self) -> Dict[str, Any]:
        """도구별 설정 생성"""
        tool_config = {}
        
        # [tool.uv]
        tool_config['uv'] = {
            'index-url': 'https://pypi.org/simple'
        }
        
        # [tool.black] - black 설정이 있으면
        if (self.project_root / 'pyproject.toml').exists():
            # 기존 설정 유지
            try:
                with open(self.project_root / 'pyproject.toml', 'r') as f:
                    existing = toml.load(f)
                    if 'tool' in existing:
                        for tool in ['black', 'isort', 'mypy', 'pytest', 'ruff']:
                            if tool in existing['tool']:
                                tool_config[tool] = existing['tool'][tool]
            except:
                pass
        
        # 기본 설정 추가
        if 'black' not in tool_config:
            tool_config['black'] = {
                'line-length': 88,
                'target-version': ['py311'],
                'include': '\\.pyi?$',
                'exclude': '''
/(
    \\.git
  | \\.hg
  | \\.mypy_cache
  | \\.tox
  | \\.venv
  | _build
  | buck-out
  | build
  | dist
)/
'''
            }
        
        if 'ruff' not in tool_config:
            tool_config['ruff'] = {
                'select': ['E', 'F', 'B', 'I'],
                'ignore': ['E501'],
                'fixable': ['ALL'],
                'unfixable': [],
                'exclude': [
                    '.git',
                    '.venv',
                    '__pycache__',
                    '.mypy_cache',
                    '.pytest_cache'
                ],
                'line-length': 88,
                'dummy-variable-rgx': '^(_+|(_+[a-zA-Z0-9_]*[a-zA-Z0-9]+?))$',
                'target-version': 'py311'
            }
        
        if 'mypy' not in tool_config:
            tool_config['mypy'] = {
                'python_version': '3.11',
                'warn_return_any': True,
                'warn_unused_configs': True,
                'disallow_untyped_defs': True,
                'ignore_missing_imports': True
            }
        
        if 'pytest' not in tool_config:
            tool_config['pytest'] = {
                'ini_options': {
                    'minversion': '7.0',
                    'addopts': '-ra -q --strict-markers',
                    'testpaths': ['tests'],
                    'python_files': ['test_*.py', '*_test.py'],
                    'python_classes': ['Test*'],
                    'python_functions': ['test_*']
                }
            }
        
        return tool_config
    
    def validate_pyproject(self) -> List[str]:
        """생성된 pyproject.toml 검증"""
        print("✔️  Validating pyproject.toml...")
        
        issues = []
        
        # 필수 필드 확인
        required_fields = ['name', 'version', 'dependencies']
        for field in required_fields:
            if field not in self.config['project']:
                issues.append(f"Missing required field: project.{field}")
        
        # 의존성 형식 검증
        all_deps = []
        all_deps.extend(self.config['project'].get('dependencies', []))
        
        for deps in self.config['project'].get('optional-dependencies', {}).values():
            all_deps.extend(deps)
        
        for dep in all_deps:
            if not self._validate_dependency_format(dep):
                issues.append(f"Invalid dependency format: {dep}")
        
        # Python 버전 형식 검증
        py_version = self.config['project'].get('requires-python', '')
        if py_version and not self._validate_python_version(py_version):
            issues.append(f"Invalid Python version specifier: {py_version}")
        
        return issues
    
    def _validate_dependency_format(self, dep: str) -> bool:
        """의존성 형식 검증"""
        # Git URL
        if ' @ git+' in dep:
            return True
        
        # 패키지 이름과 버전
        try:
            if any(op in dep for op in ['==', '>=', '<=', '>', '<', '~=', '!=']):
                name, version = re.split(r'[<>=!~]+', dep, 1)
                # 버전 형식 검증
                SpecifierSet(f'>={version.strip()}")
            return True
        except:
            return False
    
    def _validate_python_version(self, version_spec: str) -> bool:
        """Python 버전 지정자 검증"""
        try:
            SpecifierSet(version_spec)
            return True
        except:
            return False
    
    def write_pyproject_toml(self, output_path: Optional[Path] = None) -> None:
        """pyproject.toml 파일 작성"""
        if output_path is None:
            output_path = self.project_root / 'pyproject.toml'
        
        # 백업
        if output_path.exists():
            backup_path = output_path.with_suffix('.toml.backup')
            import shutil
            shutil.copy2(output_path, backup_path)
            print(f"  📋 Backed up existing file to {backup_path}")
        
        # 파일 작성
        with open(output_path, 'w') as f:
            toml.dump(self.config, f)
        
        print(f"  ✅ Written to {output_path}")
    
    def test_with_uv(self) -> bool:
        """uv로 설치 테스트"""
        print("🧪 Testing with uv...")
        
        # 임시 가상환경에서 테스트
        test_dir = self.project_root / '.test_venv'
        
        try:
            # 가상환경 생성
            subprocess.run(['uv', 'venv', str(test_dir)], check=True, capture_output=True)
            
            # pyproject.toml로 설치
            if test_dir.exists():
                activate = test_dir / 'bin' / 'activate'
                cmd = f'source {activate} && uv pip install -e .'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("  ✅ Installation test passed")
                    return True
                else:
                    print(f"  ❌ Installation test failed: {result.stderr}")
                    return False
        finally:
            # 정리
            if test_dir.exists():
                import shutil
                shutil.rmtree(test_dir)
        
        return False
    
    def migrate(self) -> bool:
        """전체 마이그레이션 프로세스"""
        print("🚀 Starting pyproject.toml migration...\n")
        
        # 1. pyproject.toml 생성
        self.generate_pyproject_toml()
        
        # 2. 검증
        issues = self.validate_pyproject()
        if issues:
            print("\n⚠️  Validation issues found:")
            for issue in issues:
                print(f"  - {issue}")
            
            response = input("\nContinue anyway? (y/N): ")
            if response.lower() != 'y':
                return False
        
        # 3. 파일 작성
        self.write_pyproject_toml()
        
        # 4. 설치 테스트
        if shutil.which('uv'):
            self.test_with_uv()
        
        # 5. 마이그레이션 가이드 생성
        self._generate_migration_guide()
        
        print("\n✅ Migration complete!")
        return True
    
    def _generate_migration_guide(self) -> None:
        """마이그레이션 가이드 생성"""
        guide = f"""# pyproject.toml Migration Guide

## Changes Made

1. Created `pyproject.toml` with:
   - Project metadata from setup.py and git
   - Dependencies from requirements*.txt files
   - Tool configurations for black, ruff, mypy, pytest

## Next Steps

### 1. Install with uv
```bash
# Create new virtual environment
uv venv

# Activate it
source .venv/bin/activate  # On Unix
# or
.venv\\Scripts\\activate  # On Windows

# Install project in editable mode
uv pip install -e .

# Install with dev dependencies
uv pip install -e ".[dev]"
```

### 2. Update CI/CD
Replace:
```yaml
pip install -r requirements.txt
```

With:
```yaml
uv pip install -e .
```

### 3. Update Documentation
Update README.md installation instructions to use:
```bash
uv pip install -e .
```

### 4. Optional: Remove old files
Once confirmed working:
```bash
rm requirements*.txt
rm setup.py  # if exists
```

## Dependency Changes

- Main dependencies: {len(self.config['project']['dependencies'])} packages
- Dev dependencies: {len(self.config['project'].get('optional-dependencies', {}).get('dev', []))} packages
- Test dependencies: {len(self.config['project'].get('optional-dependencies', {}).get('test', []))} packages

## Troubleshooting

If you encounter issues:

1. Check `pyproject.toml.backup` for the previous version
2. Ensure all git URLs are accessible
3. Verify Python version requirement
4. Run `uv pip install -e . -v` for verbose output
"""
        
        with open(self.project_root / 'MIGRATION_GUIDE.md', 'w') as f:
            f.write(guide)
        
        print("📖 Migration guide written to MIGRATION_GUIDE.md")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate pyproject.toml from requirements.txt')
    parser.add_argument('--path', default='.', help='Project root path')
    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--no-test', action='store_true', help='Skip uv test')
    
    args = parser.parse_args()
    
    generator = PyProjectGenerator(args.path)
    
    if args.no_test:
        generator.generate_pyproject_toml()
        generator.write_pyproject_toml(Path(args.output) if args.output else None)
    else:
        generator.migrate()


if __name__ == '__main__':
    main()
```

#### SubTask 2.2.3: 도구 설정 통합
**담당자**: 인프라 엔지니어  
**예상 소요시간**: 3시간

```python
#!/usr/bin/env python3
# scripts/consolidate_tool_configs.py

import os
import json
import toml
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
import configparser

class ToolConfigConsolidator:
    """여러 도구 설정을 pyproject.toml로 통합"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.configs = {}
        self.pyproject_path = self.project_root / 'pyproject.toml'
        
    def find_config_files(self) -> Dict[str, List[Path]]:
        """프로젝트의 모든 설정 파일 찾기"""
        print("🔍 Finding configuration files...")
        
        config_patterns = {
            'black': ['.black.toml', 'pyproject.toml'],
            'flake8': ['.flake8', 'setup.cfg', 'tox.ini'],
            'mypy': ['mypy.ini', '.mypy.ini', 'setup.cfg'],
            'pytest': ['pytest.ini', 'tox.ini', 'setup.cfg'],
            'isort': ['.isort.cfg', 'setup.cfg'],
            'coverage': ['.coveragerc', 'setup.cfg'],
            'ruff': ['ruff.toml', '.ruff.toml', 'pyproject.toml'],
            'bandit': ['.bandit', 'setup.cfg'],
            'pylint': ['.pylintrc', 'pylintrc', 'setup.cfg']
        }
        
        found_configs = {}
        
        for tool, patterns in config_patterns.items():
            found_configs[tool] = []
            for pattern in patterns:
                config_path = self.project_root / pattern
                if config_path.exists():
                    found_configs[tool].append(config_path)
                    print(f"  ✅ Found {tool} config: {pattern}")
        
        return found_configs
    
    def extract_black_config(self, config_files: List[Path]) -> Dict[str, Any]:
        """Black 설정 추출"""
        config = {
            'line-length': 88,
            'target-version': ['py311'],
            'include': '\\.pyi?$'
        }
        
        for config_file in config_files:
            if config_file.name == 'pyproject.toml':
                try:
                    data = toml.load(config_file)
                    if 'tool' in data and 'black' in data['tool']:
                        config.update(data['tool']['black'])
                except:
                    pass
            elif config_file.suffix == '.toml':
                try:
                    data = toml.load(config_file)
                    config.update(data)
                except:
                    pass
        
        return config
    
    def extract_flake8_config(self, config_files: List[Path]) -> Dict[str, Any]:
        """Flake8 설정 추출 및 Ruff 형식으로 변환"""
        config = {}
        
        for config_file in config_files:
            if config_file.name == '.flake8':
                parser = configparser.ConfigParser()
                parser.read(config_file)
                
                if 'flake8' in parser:
                    section = parser['flake8']
                    
                    # Ruff로 변환
                    ruff_config = {
                        'line-length': int(section.get('max-line-length', 88)),
                        'select': ['E', 'F', 'W'],
                        'ignore': []
                    }
                    
                    # ignore 설정 변환
                    if 'ignore' in section:
                        ignores = section['ignore'].split(',')
                        ruff_config['ignore'] = [i.strip() for i in ignores]
                    
                    # extend-ignore 병합
                    if 'extend-ignore' in section:
                        extends = section['extend-ignore'].split(',')
                        ruff_config['ignore'].extend([i.strip() for i in extends])
                    
                    # exclude 설정
                    if 'exclude' in section:
                        excludes = section['exclude'].split(',')
                        ruff_config['exclude'] = [e.strip() for e in excludes]
                    
                    config = ruff_config
                    
        return config
    
    def extract_mypy_config(self, config_files: List[Path]) -> Dict[str, Any]:
        """MyPy 설정 추출"""
        config = {
            'python_version': '3.11',
            'warn_return_any': True,
            'warn_unused_configs': True
        }
        
        for config_file in config_files:
            if config_file.name in ['mypy.ini', '.mypy.ini']:
                parser = configparser.ConfigParser()
                parser.read(config_file)
                
                if 'mypy' in parser:
                    section = parser['mypy']
                    
                    # 불린 값 변환
                    bool_keys = [
                        'warn_return_any', 'warn_unused_configs',
                        'disallow_untyped_defs', 'ignore_missing_imports',
                        'strict_optional', 'warn_redundant_casts',
                        'warn_unused_ignores', 'warn_no_return',
                        'warn_unreachable', 'strict_equality'
                    ]
                    
                    for key in bool_keys:
                        if key in section:
                            config[key] = section.getboolean(key)
                    
                    # 문자열 값
                    if 'python_version' in section:
                        config['python_version'] = section['python_version']
                    
                    # 리스트 값
                    if 'exclude' in section:
                        config['exclude'] = section['exclude'].split('\n')
        
        return config
    
    def extract_pytest_config(self, config_files: List[Path]) -> Dict[str, Any]:
        """Pytest 설정 추출"""
        config = {
            'minversion': '7.0',
            'testpaths': ['tests'],
            'python_files': ['test_*.py', '*_test.py']
        }
        
        for config_file in config_files:
            if config_file.name == 'pytest.ini':
                parser = configparser.ConfigParser()
                parser.read(config_file)
                
                if 'pytest' in parser:
                    section = parser['pytest']
                    
                    # 직접 매핑되는 값들
                    direct_keys = ['minversion', 'addopts', 'norecursedirs']
                    for key in direct_keys:
                        if key in section:
                            config[key] = section[key]
                    
                    # 리스트 값들
                    list_keys = ['testpaths', 'python_files', 'python_classes', 'python_functions']
                    for key in list_keys:
                        if key in section:
                            values = section[key].strip().split('\n')
                            config[key] = [v.strip() for v in values if v.strip()]
        
        # ini_options로 래핑
        return {'ini_options': config}
    
    def extract_isort_config(self, config_files: List[Path]) -> Dict[str, Any]:
        """isort 설정 추출"""
        config = {
            'profile': 'black',
            'line_length': 88
        }
        
        for config_file in config_files:
            if config_file.name == '.isort.cfg':
                parser = configparser.ConfigParser()
                parser.read(config_file)
                
                if 'settings' in parser:
                    section = parser['settings']
                    
                    # 직접 매핑
                    if 'line_length' in section:
                        config['line_length'] = int(section['line_length'])
                    
                    if 'profile' in section:
                        config['profile'] = section['profile']
                    
                    # known_third_party 등
                    for key in ['known_third_party', 'known_first_party']:
                        if key in section:
                            values = section[key].strip().split(',')
                            config[key] = [v.strip() for v in values if v.strip()]
        
        return config
    
    def extract_coverage_config(self, config_files: List[Path]) -> Dict[str, Any]:
        """Coverage 설정 추출"""
        config = {}
        
        for config_file in config_files:
            if config_file.name == '.coveragerc':
                parser = configparser.ConfigParser()
                parser.read(config_file)
                
                # run 섹션
                if 'run' in parser:
                    run_config = {}
                    section = parser['run']
                    
                    if 'source' in section:
                        run_config['source'] = section['source'].split(',')
                    
                    if 'omit' in section:
                        omits = section['omit'].strip().split('\n')
                        run_config['omit'] = [o.strip() for o in omits if o.strip()]
                    
                    config['run'] = run_config
                
                # report 섹션
                if 'report' in parser:
                    report_config = {}
                    section = parser['report']
                    
                    if 'exclude_lines' in section:
                        lines = section['exclude_lines'].strip().split('\n')
                        report_config['exclude_lines'] = [l.strip() for l in lines if l.strip()]
                    
                    config['report'] = report_config
        
        return config
    
    def create_consolidated_config(self) -> Dict[str, Any]:
        """모든 도구 설정을 통합"""
        print("\n🔧 Consolidating tool configurations...")
        
        found_configs = self.find_config_files()
        tool_configs = {}
        
        # 각 도구별 설정 추출
        extractors = {
            'black': self.extract_black_config,
            'flake8': self.extract_flake8_config,  # Ruff로 변환
            'mypy': self.extract_mypy_config,
            'pytest': self.extract_pytest_config,
            'isort': self.extract_isort_config,
            'coverage': self.extract_coverage_config
        }
        
        for tool, extractor in extractors.items():
            if found_configs.get(tool):
                config = extractor(found_configs[tool])
                if config:
                    if tool == 'flake8':
                        # Flake8은 Ruff로 대체
                        tool_configs['ruff'] = config
                        print(f"  ✅ Converted flake8 → ruff config")
                    else:
                        tool_configs[tool] = config
                        print(f"  ✅ Extracted {tool} config")
        
        # 추가 도구 기본 설정
        if 'ruff' not in tool_configs:
            tool_configs['ruff'] = {
                'select': ['E', 'F', 'B', 'I'],
                'ignore': ['E501'],
                'line-length': 88,
                'target-version': 'py311'
            }
        
        return tool_configs
    
    def update_pyproject_toml(self, tool_configs: Dict[str, Any]) -> None:
        """pyproject.toml 업데이트"""
        print("\n📝 Updating pyproject.toml...")
        
        # 기존 pyproject.toml 읽기
        if self.pyproject_path.exists():
            with open(self.pyproject_path, 'r') as f:
                pyproject = toml.load(f)
        else:
            pyproject = {}
        
        # tool 섹션 업데이트
        if 'tool' not in pyproject:
            pyproject['tool'] = {}
        
        for tool, config in tool_configs.items():
            pyproject['tool'][tool] = config
            print(f"  ✅ Added [tool.{tool}] section")
        
        # 파일 쓰기
        with open(self.pyproject_path, 'w') as f:
            toml.dump(pyproject, f)
        
        print(f"\n✅ Updated {self.pyproject_path}")
    
    def create_migration_script(self) -> None:
        """마이그레이션 스크립트 생성"""
        script = '''#!/bin/bash
# Tool configuration migration script

echo "🚀 Migrating tool configurations to pyproject.toml"

# Backup existing configs
mkdir -p .config_backup
for config in .flake8 .isort.cfg .coveragerc mypy.ini pytest.ini .black.toml .pylintrc .bandit; do
    if [ -f "$config" ]; then
        cp "$config" .config_backup/
        echo "  📋 Backed up $config"
    fi
done

echo ""
echo "✅ Configuration migrated to pyproject.toml"
echo ""
echo "Next steps:"
echo "1. Test the new configuration:"
echo "   - black --check ."
echo "   - ruff check ."
echo "   - mypy ."
echo "   - pytest"
echo ""
echo "2. If everything works, remove old config files:"
echo "   rm .flake8 .isort.cfg .coveragerc mypy.ini pytest.ini"
echo ""
echo "3. Update your pre-commit hooks to use pyproject.toml"
'''
        
        script_path = self.project_root / 'migrate_configs.sh'
        with open(script_path, 'w') as f:
            f.write(script)
        
        os.chmod(script_path, 0o755)
        print(f"\n📜 Created migration script: {script_path}")
    
    def generate_pre_commit_config(self) -> None:
        """pre-commit 설정 업데이트"""
        pre_commit_config = {
            'repos': [
                {
                    'repo': 'https://github.com/pre-commit/pre-commit-hooks',
                    'rev': 'v4.5.0',
                    'hooks': [
                        {'id': 'trailing-whitespace'},
                        {'id': 'end-of-file-fixer'},
                        {'id': 'check-yaml'},
                        {'id': 'check-added-large-files'}
                    ]
                },
                {
                    'repo': 'https://github.com/psf/black',
                    'rev': '23.11.0',
                    'hooks': [
                        {'id': 'black'}
                    ]
                },
                {
                    'repo': 'https://github.com/charliermarsh/ruff-pre-commit',
                    'rev': 'v0.1.6',
                    'hooks': [
                        {'id': 'ruff'}
                    ]
                },
                {
                    'repo': 'https://github.com/pre-commit/mirrors-mypy',
                    'rev': 'v1.7.1',
                    'hooks': [
                        {
                            'id': 'mypy',
                            'additional_dependencies': ['types-all']
                        }
                    ]
                }
            ]
        }
        
        with open(self.project_root / '.pre-commit-config.yaml', 'w') as f:
            yaml.dump(pre_commit_config, f, default_flow_style=False)
        
        print("📝 Created .pre-commit-config.yaml")
    
    def consolidate(self) -> None:
        """전체 통합 프로세스 실행"""
        print("🔄 Starting tool configuration consolidation...\n")
        
        # 1. 도구 설정 추출 및 통합
        tool_configs = self.create_consolidated_config()
        
        # 2. pyproject.toml 업데이트
        self.update_pyproject_toml(tool_configs)
        
        # 3. 마이그레이션 스크립트 생성
        self.create_migration_script()
        
        # 4. pre-commit 설정 생성
        self.generate_pre_commit_config()
        
        # 5. 요약 출력
        self._print_summary(tool_configs)
    
    def _print_summary(self, tool_configs: Dict[str, Any]) -> None:
        """마이그레이션 요약 출력"""
        print("\n" + "="*50)
        print("📊 Configuration Consolidation Summary")
        print("="*50)
        
        print(f"\nTools configured in pyproject.toml:")
        for tool in sorted(tool_configs.keys()):
            print(f"  ✅ {tool}")
        
        print("\n⚠️  Old configuration files to remove:")
        old_configs = [
            '.flake8', '.isort.cfg', '.coveragerc', 
            'mypy.ini', 'pytest.ini', '.black.toml'
        ]
        for config in old_configs:
            if (self.project_root / config).exists():
                print(f"  - {config}")
        
        print("\n📌 Commands updated to use pyproject.toml:")
        print("  - black .  # Uses [tool.black]")
        print("  - ruff check .  # Uses [tool.ruff]")
        print("  - mypy .  # Uses [tool.mypy]")
        print("  - pytest  # Uses [tool.pytest]")
        print("  - isort .  # Uses [tool.isort]")
        
        print("\n✅ Configuration consolidation complete!")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Consolidate tool configurations into pyproject.toml'
    )
    parser.add_argument('--path', default='.', help='Project root path')
    
    args = parser.parse_args()
    
    consolidator = ToolConfigConsolidator(args.path)
    consolidator.consolidate()


if __name__ == '__main__':
    main()
```

### Task 2.3: 개발자 워크플로우 업데이트

#### SubTask 2.3.1: Makefile 업데이트
**담당자**: 빌드 엔지니어  
**예상 소요시간**: 2시간

```makefile
# Makefile - Updated for uv

# Variables
PYTHON := python3
UV := uv
VENV := .venv
PYTHON_VENV := $(VENV)/bin/python
UV_VENV := source $(VENV)/bin/activate &&

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

# Default target
.DEFAULT_GOAL := help

# Check if uv is installed
.PHONY: check-uv
check-uv:
	@command -v $(UV) >/dev/null 2>&1 || { \
		echo "$(RED)Error: uv is not installed$(NC)"; \
		echo "Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"; \
		exit 1; \
	}

# Help target
.PHONY: help
help:
	@echo "$(GREEN)AI Agent Framework - Development Commands$(NC)"
	@echo ""
	@echo "$(YELLOW)Setup:$(NC)"
	@echo "  make install          - Install all dependencies"
	@echo "  make install-dev      - Install with dev dependencies"
	@echo "  make clean            - Clean up generated files"
	@echo ""
	@echo "$(YELLOW)Development:$(NC)"
	@echo "  make format          - Format code with black"
	@echo "  make lint            - Run linting (ruff)"
	@echo "  make type-check      - Run type checking (mypy)"
	@echo "  make test            - Run tests"
	@echo "  make test-cov        - Run tests with coverage"
	@echo "  make check           - Run all checks (format, lint, type, test)"
	@echo ""
	@echo "$(YELLOW)Dependencies:$(NC)"
	@echo "  make deps-update     - Update all dependencies"
	@echo "  make deps-lock       - Lock current dependencies"
	@echo "  make deps-sync       - Sync with locked dependencies"
	@echo "  make deps-check      - Check for outdated dependencies"
	@echo ""
	@echo "$(YELLOW)Docker:$(NC)"
	@echo "  make docker-build    - Build Docker image"
	@echo "  make docker-run      - Run Docker container"
	@echo "  make docker-push     - Push to registry"
	@echo ""
	@echo "$(YELLOW)Database:$(NC)"
	@echo "  make db-upgrade      - Run database migrations"
	@echo "  make db-downgrade    - Rollback database migration"
	@echo "  make db-reset        - Reset database"
	@echo ""
	@echo "$(YELLOW)Utilities:$(NC)"
	@echo "  make shell           - Open Python shell"
	@echo "  make docs            - Generate documentation"
	@echo "  make clean-cache     - Clean Python cache files"
	@echo "  make benchmark       - Run performance benchmarks"

# Virtual environment setup
$(VENV)/bin/activate: check-uv
	@echo "$(GREEN)Creating virtual environment...$(NC)"
	@$(UV) venv $(VENV)
	@echo "$(GREEN)Virtual environment created$(NC)"

# Install dependencies
.PHONY: install
install: $(VENV)/bin/activate
	@echo "$(GREEN)Installing dependencies...$(NC)"
	@$(UV_VENV) $(UV) pip sync requirements.txt
	@echo "$(GREEN)Dependencies installed$(NC)"

# Install with dev dependencies
.PHONY: install-dev
install-dev: $(VENV)/bin/activate
	@echo "$(GREEN)Installing all dependencies...$(NC)"
	@$(UV_VENV) $(UV) pip install -e ".[dev,test]"
	@$(UV_VENV) pre-commit install
	@echo "$(GREEN)All dependencies installed$(NC)"

# Format code
.PHONY: format
format: $(VENV)/bin/activate
	@echo "$(GREEN)Formatting code...$(NC)"
	@$(UV_VENV) black .
	@$(UV_VENV) isort .
	@echo "$(GREEN)Code formatted$(NC)"

# Lint code
.PHONY: lint
lint: $(VENV)/bin/activate
	@echo "$(GREEN)Running linter...$(NC)"
	@$(UV_VENV) ruff check .
	@echo "$(GREEN)Linting complete$(NC)"

# Type checking
.PHONY: type-check
type-check: $(VENV)/bin/activate
	@echo "$(GREEN)Running type checker...$(NC)"
	@$(UV_VENV) mypy app/
	@echo "$(GREEN)Type checking complete$(NC)"

# Run tests
.PHONY: test
test: $(VENV)/bin/activate
	@echo "$(GREEN)Running tests...$(NC)"
	@$(UV_VENV) pytest tests/ -v
	@echo "$(GREEN)Tests complete$(NC)"

# Run tests with coverage
.PHONY: test-cov
test-cov: $(VENV)/bin/activate
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	@$(UV_VENV) pytest tests/ -v --cov=app --cov-report=html --cov-report=term
	@echo "$(GREEN)Coverage report generated in htmlcov/$(NC)"

# Run all checks
.PHONY: check
check: format lint type-check test
	@echo "$(GREEN)All checks passed!$(NC)"

# Update dependencies
.PHONY: deps-update
deps-update: $(VENV)/bin/activate
	@echo "$(GREEN)Updating dependencies...$(NC)"
	@$(UV_VENV) $(UV) pip install --upgrade -r requirements.txt
	@echo "$(GREEN)Dependencies updated$(NC)"

# Lock dependencies
.PHONY: deps-lock
deps-lock: $(VENV)/bin/activate
	@echo "$(GREEN)Locking dependencies...$(NC)"
	@$(UV_VENV) $(UV) pip freeze > requirements.lock
	@echo "$(GREEN)Dependencies locked$(NC)"

# Sync with locked dependencies
.PHONY: deps-sync
deps-sync: $(VENV)/bin/activate requirements.lock
	@echo "$(GREEN)Syncing dependencies...$(NC)"
	@$(UV_VENV) $(UV) pip sync requirements.lock
	@echo "$(GREEN)Dependencies synced$(NC)"

# Check for outdated dependencies
.PHONY: deps-check
deps-check: $(VENV)/bin/activate
	@echo "$(GREEN)Checking for outdated dependencies...$(NC)"
	@$(UV_VENV) pip list --outdated

# Docker build
.PHONY: docker-build
docker-build:
	@echo "$(GREEN)Building Docker image...$(NC)"
	@docker build -t ai-agent-framework:latest -f Dockerfile.uv .
	@echo "$(GREEN)Docker image built$(NC)"

# Docker run
.PHONY: docker-run
docker-run:
	@echo "$(GREEN)Running Docker container...$(NC)"
	@docker run -it --rm \
		-p 8000:8000 \
		-v $(PWD):/app \
		--env-file .env \
		ai-agent-framework:latest

# Docker push
.PHONY: docker-push
docker-push:
	@echo "$(GREEN)Pushing Docker image...$(NC)"
	@docker tag ai-agent-framework:latest $(DOCKER_REGISTRY)/ai-agent-framework:latest
	@docker push $(DOCKER_REGISTRY)/ai-agent-framework:latest

# Database migrations
.PHONY: db-upgrade
db-upgrade: $(VENV)/bin/activate
	@echo "$(GREEN)Running database migrations...$(NC)"
	@$(UV_VENV) alembic upgrade head

.PHONY: db-downgrade
db-downgrade: $(VENV)/bin/activate
	@echo "$(GREEN)Rolling back database migration...$(NC)"
	@$(UV_VENV) alembic downgrade -1

.PHONY: db-reset
db-reset: $(VENV)/bin/activate
	@echo "$(YELLOW)Warning: This will delete all data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(UV_VENV) alembic downgrade base; \
		$(UV_VENV) alembic upgrade head; \
		echo "$(GREEN)Database reset complete$(NC)"; \
	fi

# Python shell
.PHONY: shell
shell: $(VENV)/bin/activate
	@echo "$(GREEN)Starting Python shell...$(NC)"
	@$(UV_VENV) ipython

# Generate documentation
.PHONY: docs
docs: $(VENV)/bin/activate
	@echo "$(GREEN)Generating documentation...$(NC)"
	@$(UV_VENV) mkdocs build
	@echo "$(GREEN)Documentation generated in site/$(NC)"

# Clean cache files
.PHONY: clean-cache
clean-cache:
	@echo "$(GREEN)Cleaning cache files...$(NC)"
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*.pyd" -delete
	@find . -type f -name ".coverage" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)Cache cleaned$(NC)"

# Clean everything
.PHONY: clean
clean: clean-cache
	@echo "$(GREEN)Cleaning all generated files...$(NC)"
	@rm -rf $(VENV)
	@rm -rf htmlcov/
	@rm -rf dist/
	@rm -rf build/
	@rm -rf site/
	@rm -f requirements.lock
	@echo "$(GREEN)Clean complete$(NC)"

# Performance benchmark
.PHONY: benchmark
benchmark: $(VENV)/bin/activate
	@echo "$(GREEN)Running performance benchmarks...$(NC)"
	@$(UV_VENV) python scripts/benchmark_uv.py
	@echo "$(GREEN)Benchmark complete$(NC)"

# Development server
.PHONY: run
run: $(VENV)/bin/activate
	@echo "$(GREEN)Starting development server...$(NC)"
	@$(UV_VENV) uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production server
.PHONY: run-prod
run-prod: $(VENV)/bin/activate
	@echo "$(GREEN)Starting production server...$(NC)"
	@$(UV_VENV) gunicorn app.main:app \
		--workers 4 \
		--worker-class uvicorn.workers.UvicornWorker \
		--bind 0.0.0.0:8000

# Watch for changes and run tests
.PHONY: watch
watch: $(VENV)/bin/activate
	@echo "$(GREEN)Watching for changes...$(NC)"
	@$(UV_VENV) ptw tests/ -- -v

# Migration from pip to uv
.PHONY: migrate-from-pip
migrate-from-pip:
	@echo "$(GREEN)Migrating from pip to uv...$(NC)"
	@python scripts/migrate_venv.py $(VENV)
	@echo "$(GREEN)Migration complete$(NC)"

# Verify uv installation
.PHONY: verify-uv
verify-uv: $(VENV)/bin/activate
	@echo "$(GREEN)Verifying uv installation...$(NC)"
	@$(UV) --version
	@$(UV_VENV) $(UV) pip list | head -10
	@echo "$(GREEN)uv is working correctly$(NC)"

# Generate requirements files from pyproject.toml
.PHONY: requirements
requirements: $(VENV)/bin/activate
	@echo "$(GREEN)Generating requirements files...$(NC)"
	@$(UV_VENV) pip-compile pyproject.toml -o requirements.txt
	@$(UV_VENV) pip-compile --extra dev pyproject.toml -o requirements-dev.txt
	@echo "$(GREEN)Requirements files generated$(NC)"

# Quick install for CI
.PHONY: ci-install
ci-install: check-uv
	@$(UV) venv $(VENV)
	@$(UV_VENV) $(UV) pip install -e ".[test]"

# Security check
.PHONY: security
security: $(VENV)/bin/activate
	@echo "$(GREEN)Running security checks...$(NC)"
	@$(UV_VENV) bandit -r app/
	@$(UV_VENV) safety check
	@echo "$(GREEN)Security checks complete$(NC)"
```

#### SubTask 2.3.2: 개발 스크립트 업데이트
**담당자**: 스크립트 개발자  
**예상 소요시간**: 1시간

```bash
#!/bin/bash
# scripts/dev-setup.sh - Development environment setup with uv

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Functions
print_step() {
    echo -e "\n${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}!${NC} $1"
}

# Banner
echo -e "${GREEN}"
echo "╔═══════════════════════════════════════╗"
echo "║   AI Agent Framework Dev Setup (uv)   ║"
echo "╚═══════════════════════════════════════╝"
echo -e "${NC}"

# Check OS
print_step "Detecting operating system"
OS="Unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    OS="Windows"
fi
print_success "Detected: $OS"

# Check Python version
print_step "Checking Python version"
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
    print_success "Python $PYTHON_VERSION (>= $REQUIRED_VERSION required)"
else
    print_error "Python $PYTHON_VERSION is too old. Please install Python $REQUIRED_VERSION or newer."
    exit 1
fi

# Install uv if not present
print_step "Checking for uv installation"
if ! command -v uv &> /dev/null; then
    print_warning "uv not found. Installing..."
    
    if [[ "$OS" == "Windows" ]]; then
        print_error "Please run this in PowerShell as Administrator:"
        echo "powershell -c \"irm https://astral.sh/uv/install.ps1 | iex\""
        exit 1
    else
        curl -LsSf https://astral.sh/uv/install.sh | sh
        source $HOME/.cargo/env
    fi
    
    print_success "uv installed successfully"
else
    UV_VERSION=$(uv --version | cut -d' ' -f2)
    print_success "uv $UV_VERSION is already installed"
fi

# Create project structure
print_step "Setting up project structure"
mkdir -p {app,tests,scripts,docs,logs,data}
touch app/__init__.py tests/__init__.py
print_success "Project structure created"

# Create/update .gitignore
print_step "Creating .gitignore"
cat > .gitignore << 'EOF'
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Virtual environments
.venv/
venv/
ENV/
env/
.venv_pip_backup*/

# uv
.uv/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Testing
.coverage
.pytest_cache/
htmlcov/
.mypy_cache/
.ruff_cache/

# Logs
logs/
*.log

# Environment variables
.env
.env.local
.env.*.local

# Build
dist/
build/
*.egg-info/

# Data
data/
*.db
*.sqlite
EOF
print_success ".gitignore created"

# Create .env.example
print_step "Creating .env.example"
cat > .env.example << 'EOF'
# Application
APP_NAME=ai-agent-framework
APP_ENV=development
DEBUG=true

# Database
DATABASE_URL=postgresql://user:password@localhost/dbname

# Redis
REDIS_URL=redis://localhost:6379/0

# API Keys
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# AWS (optional)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1

# Logging
LOG_LEVEL=INFO
EOF
print_success ".env.example created"

# Create virtual environment
print_step "Creating virtual environment with uv"
if [ -d ".venv" ]; then
    print_warning "Virtual environment already exists. Recreating..."
    rm -rf .venv
fi

uv venv .venv
print_success "Virtual environment created"

# Activate virtual environment
print_step "Activating virtual environment"
if [[ "$OS" == "Windows" ]]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi
print_success "Virtual environment activated"

# Install dependencies
print_step "Installing dependencies with uv"
if [ -f "pyproject.toml" ]; then
    uv pip install -e ".[dev]"
elif [ -f "requirements.txt" ]; then
    uv pip sync requirements.txt
    if [ -f "requirements-dev.txt" ]; then
        uv pip install -r requirements-dev.txt
    fi
else
    print_warning "No requirements file found. Installing basic packages..."
    uv pip install fastapi uvicorn pydantic sqlalchemy alembic pytest black ruff mypy
fi
print_success "Dependencies installed"

# Setup pre-commit hooks
print_step "Setting up pre-commit hooks"
if [ -f ".pre-commit-config.yaml" ]; then
    pre-commit install
    print_success "Pre-commit hooks installed"
else
    print_warning "No .pre-commit-config.yaml found. Creating one..."
    cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
EOF
    pre-commit install
    print_success "Pre-commit config created and hooks installed"
fi

# Setup IDE
print_step "Setting up IDE integration"
python scripts/setup_ide_integration.py 2>/dev/null || print_warning "IDE setup script not found"

# Initialize git if needed
if [ ! -d ".git" ]; then
    print_step "Initializing git repository"
    git init
    git add .
    git commit -m "Initial commit with uv setup"
    print_success "Git repository initialized"
fi

# Create initial test
print_step "Creating sample test"
cat > tests/test_sample.py << 'EOF'
"""Sample test to verify setup."""
import pytest


def test_setup():
    """Test that the setup is working."""
    assert True


def test_imports():
    """Test that main imports work."""
    import fastapi
    import pydantic
    import sqlalchemy
    
    assert fastapi.__version__
    assert pydantic.__version__
    assert sqlalchemy.__version__


if __name__ == "__main__":
    pytest.main([__file__])
EOF
print_success "Sample test created"

# Run tests
print_step "Running tests to verify setup"
pytest tests/test_sample.py -v || print_warning "Tests failed - please check your setup"

# Performance comparison
print_step "Comparing uv vs pip performance (optional)"
if command -v pip &> /dev/null; then
    echo "Installing requests with pip (for comparison)..."
    TIME_PIP=$( { time pip install --dry-run requests >/dev/null 2>&1; } 2>&1 | grep real | awk '{print $2}' )
    
    echo "Installing requests with uv..."
    TIME_UV=$( { time uv pip install --dry-run requests >/dev/null 2>&1; } 2>&1 | grep real | awk '{print $2}' )
    
    echo -e "\n${GREEN}Performance Comparison:${NC}"
    echo "  pip:  $TIME_PIP"
    echo "  uv:   $TIME_UV"
fi

# Summary
echo -e "\n${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Development environment setup complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}\n"

echo "Next steps:"
echo "1. Copy .env.example to .env and fill in your values"
echo "2. Activate the virtual environment:"
if [[ "$OS" == "Windows" ]]; then
    echo "   .venv\\Scripts\\activate"
else
    echo "   source .venv/bin/activate"
fi
echo "3. Start developing!"
echo "   make run       # Start development server"
echo "   make test      # Run tests"
echo "   make check     # Run all checks"
echo ""
echo "For more commands, run: make help"

# Create quick start script
cat > start-dev.sh << 'EOF'
#!/bin/bash
source .venv/bin/activate
echo "Virtual environment activated. Run 'make help' for available commands."
exec bash
EOF
chmod +x start-dev.sh

echo -e "\nTip: Run ${GREEN}./start-dev.sh${NC} to quickly activate the environment next time!"
```

#### SubTask 2.3.3: 팀 교육 자료 작성
**담당자**: 교육 담당자  
**예상 소요시간**: 1시간

```markdown
# uv 교육 자료 - 개발팀 전환 가이드

## 📚 목차
1. [uv 소개](#uv-소개)
2. [주요 변경사항](#주요-변경사항)
3. [일상 작업 가이드](#일상-작업-가이드)
4. [트러블슈팅](#트러블슈팅)
5. [실습 예제](#실습-예제)

---

## uv 소개

### uv란?
- **Rust로 작성된 초고속 Python 패키지 매니저**
- pip 대비 10-100배 빠른 성능
- 더 나은 의존성 해결
- 효율적인 캐싱

### 왜 전환하는가?
1. **개발 생산성 향상**
   - 패키지 설치 시간 90% 단축
   - CI/CD 파이프라인 속도 개선

2. **더 나은 의존성 관리**
   - 엄격한 의존성 해결
   - 재현 가능한 빌드

3. **리소스 효율성**
   - 디스크 공간 절약
   - 네트워크 사용량 감소

---

## 주요 변경사항

### 명령어 비교표

| 작업 | pip (기존) | uv (새로운) |
|------|-----------|------------|
| 패키지 설치 | `pip install requests` | `uv pip install requests` |
| requirements 설치 | `pip install -r requirements.txt` | `uv pip sync requirements.txt` |
| 패키지 업그레이드 | `pip install --upgrade requests` | `uv pip install --upgrade requests` |
| 패키지 제거 | `pip uninstall requests` | `uv pip uninstall requests` |
| 설치된 패키지 확인 | `pip list` | `uv pip list` |
| 패키지 정보 | `pip show requests` | `uv pip show requests` |

### 가상환경 생성

**기존 (pip)**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**새로운 (uv)**
```bash
uv venv
source .venv/bin/activate
uv pip sync requirements.txt
```

---

## 일상 작업 가이드

### 1. 프로젝트 시작하기

```bash
# 저장소 클론
git clone https://github.com/company/project.git
cd project

# uv로 환경 설정
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

### 2. 새 패키지 추가하기

```bash
# 패키지 설치
uv pip install pandas

# pyproject.toml에 추가 (수동)
# dependencies = [
#     ...
#     "pandas>=2.0.0",
# ]

# 또는 requirements.txt 업데이트
uv pip freeze > requirements.txt
```

### 3. 의존성 업데이트

```bash
# 모든 패키지 업데이트
uv pip install --upgrade -r requirements.txt

# 특정 패키지만 업데이트
uv pip install --upgrade fastapi
```

### 4. 테스트 실행

```bash
# Makefile 사용 (권장)
make test

# 직접 실행
uv pip install -e ".[test]"
pytest tests/
```

### 5. 코드 품질 검사

```bash
# 전체 검사
make check

# 개별 실행
make format  # Black으로 포맷팅
make lint    # Ruff로 린팅
make type-check  # MyPy로 타입 체크
```

---

## 트러블슈팅

### 자주 발생하는 문제

#### 1. "uv: command not found"
```bash
# 해결: uv 재설치
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # 또는 새 터미널 열기
```

#### 2. 패키지 설치 실패
```bash
# 옵션 1: 프리릴리즈 버전 허용
uv pip install --pre problematic-package

# 옵션 2: 캐시 정리 후 재시도
rm -rf ~/.cache/uv
uv pip install problematic-package

# 옵션 3: 상세 로그 확인
uv pip install problematic-package -vvv
```

#### 3. 기업 프록시 환경
```bash
# 프록시 설정
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
export NO_PROXY=localhost,127.0.0.1,.company.com

# 사내 PyPI 사용
uv pip install --index-url https://pypi.company.com/simple package
```

#### 4. IDE가 가상환경을 인식하지 못함
```bash
# VS Code
1. Cmd+Shift+P → "Python: Select Interpreter"
2. .venv/bin/python 선택

# PyCharm
1. Settings → Project → Python Interpreter
2. Add → Existing Environment → .venv/bin/python
```

---

## 실습 예제

### 실습 1: 기본 프로젝트 설정
```bash
# 1. 새 프로젝트 생성
mkdir my-uv-project
cd my-uv-project

# 2. 가상환경 생성
uv venv

# 3. 활성화
source .venv/bin/activate

# 4. 패키지 설치
uv pip install fastapi uvicorn

# 5. 간단한 앱 작성
cat > main.py << 'EOF'
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World", "tool": "uv"}
EOF

# 6. 실행
uvicorn main:app --reload
```

### 실습 2: 성능 비교
```bash
# pip 성능 측정
time pip install --dry-run numpy pandas scikit-learn

# uv 성능 측정
time uv pip install --dry-run numpy pandas scikit-learn
```

### 실습 3: 프로젝트 마이그레이션
```bash
# 1. 기존 프로젝트에서
cd existing-project

# 2. 백업
cp -r .venv .venv_backup

# 3. uv로 재생성
rm -rf .venv
uv venv
source .venv/bin/activate
uv pip sync requirements.txt

# 4. 테스트
pytest tests/
```

---

## 팀 규칙

### 1. 브랜치별 작업
```bash
# feature 브랜치 체크아웃 후
git checkout feature/new-feature
uv pip sync requirements.txt  # 항상 의존성 동기화
```

### 2. 새 패키지 추가 시
1. 팀 리드와 논의
2. `pyproject.toml` 또는 `requirements.txt` 업데이트
3. PR에 변경 사항 명시

### 3. 문제 발생 시
1. 에러 메시지 캡처
2. `uv --version` 출력 포함
3. #dev-help 채널에 공유

---

## 추가 리소스

### 문서
- [uv 공식 문서](https://github.com/astral-sh/uv)
- [내부 위키 - uv 가이드](https://wiki.company.com/uv)
- [트러블슈팅 가이드](./docs/uv-troubleshooting.md)

### 지원
- Slack: #uv-support
- 주간 오피스아워: 목요일 오후 3시
- 1:1 지원: dev-support@company.com

---

## 체크리스트

신규 팀원은 다음을 완료해주세요:

- [ ] uv 설치 완료
- [ ] 실습 예제 3개 모두 완료
- [ ] IDE 설정 완료
- [ ] 첫 PR을 uv 환경에서 제출
- [ ] #uv-users 채널 가입

완료 후 팀 리드에게 확인받으세요.
```

---

## 📋 Phase 3: CI/CD 파이프라인 전환 (Day 8-12)

### Task 3.1: GitHub Actions 워크플로우 업데이트

#### SubTask 3.1.1: CI 파이프라인 수정
**담당자**: CI/CD 엔지니어  
**예상 소요시간**: 3시간

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on:
  push:
    branches: [main, develop, 'feature/**']
  pull_request:
    branches: [main, develop]
  workflow_dispatch:

env:
  PYTHON_VERSION: '3.11'
  UV_CACHE_DIR: ~/.cache/uv
  UV_SYSTEM_PYTHON: 1

jobs:
  # 코드 품질 검사
  quality-checks:
    name: Code Quality Checks
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      with:
        fetch-depth: 0  # Full history for better analysis
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    
    - name: Install uv
      run: |
        curl -LsSf https://astral.sh/uv/install.sh | sh
        echo "$HOME/.cargo/bin" >> $GITHUB_PATH
    
    - name: Cache uv packages
      uses: actions/cache@v3
      with:
        path: |
          ${{ env.UV_CACHE_DIR }}
          .venv
        key: ${{ runner.os }}-uv-${{ hashFiles('**/pyproject.toml', '**/requirements*.txt') }}
        restore-keys: |
          ${{ runner.os }}-uv-
    
    - name: Create virtual environment
      run: uv venv
    
    - name: Install dependencies
      run: |
        source .venv/bin/activate
        uv pip install -e ".[dev]"
    
    - name: Run formatters check
      run: |
        source .venv/bin/activate
        black --check .
        isort --check-only .
    
    - name: Run linters
      run: |
        source .venv/bin/activate
        ruff check .
        
    - name: Run type checking
      run: |
        source .venv/bin/activate
        mypy app/
    
    - name: Security scan with Bandit
      run: |
        source .venv/bin/activate
        bandit -r app/ -ll
    
    - name: Check for dependency vulnerabilities
      run: |
        source .venv/bin/activate
        pip install safety
        safety check

  # 테스트 실행
  test:
    name: Test - Python ${{ matrix.python-version }} on ${{ matrix.os }}
    needs: quality-checks
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ['3.11', '3.12']
        exclude:
          - os: macos-latest
            python-version: '3.12'  # Skip macOS + 3.12 for speed
    
    runs-on: ${{ matrix.os }}
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install uv (Unix)
      if: runner.os != 'Windows'
      run: |
        curl -LsSf https://astral.sh/uv/install.sh | sh
        echo "$HOME/.cargo/bin" >> $GITHUB_PATH
    
    - name: Install uv (Windows)
      if: runner.os == 'Windows'
      run: |
        irm https://astral.sh/uv/install.ps1 | iex
        echo "$env:USERPROFILE\.cargo\bin" | Out-File -FilePath $env:GITHUB_PATH -Encoding utf8 -Append
      shell: pwsh
    
    - name: Cache uv packages
      uses: actions/cache@v3
      with:
        path: |
          ${{ env.UV_CACHE_DIR }}
          .venv
        key: ${{ runner.os }}-${{ matrix.python-version }}-uv-${{ hashFiles('**/pyproject.toml', '**/requirements*.txt') }}
        restore-keys: |
          ${{ runner.os }}-${{ matrix.python-version }}-uv-
    
    - name: Create virtual environment
      run: uv venv
    
    - name: Install dependencies (Unix)
      if: runner.os != 'Windows'
      run: |
        source .venv/bin/activate
        uv pip install -e ".[test]"
    
    - name: Install dependencies (Windows)
      if: runner.os == 'Windows'
      run: |
        .venv\Scripts\activate
        uv pip install -e ".[test]"
      shell: pwsh
    
    - name: Run tests with coverage (Unix)
      if: runner.os != 'Windows'
      run: |
        source .venv/bin/activate
        pytest tests/ -v --cov=app --cov-report=xml --cov-report=html --cov-report=term
    
    - name: Run tests with coverage (Windows)
      if: runner.os == 'Windows'
      run: |
        .venv\Scripts\activate
        pytest tests/ -v --cov=app --cov-report=xml --cov-report=html --cov-report=term
      shell: pwsh
    
    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-${{ matrix.os }}-${{ matrix.python-version }}
    
    - name: Upload coverage HTML report
      uses: actions/upload-artifact@v3
      if: matrix.os == 'ubuntu-latest' && matrix.python-version == '3.11'
      with:
        name: coverage-report
        path: htmlcov/

  # 통합 테스트
  integration-test:
    name: Integration Tests
    needs: test
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    
    - name: Install uv
      run: |
        curl -LsSf https://astral.sh/uv/install.sh | sh
        echo "$HOME/.cargo/bin" >> $GITHUB_PATH
    
    - name: Cache uv packages
      uses: actions/cache@v3
      with:
        path: |
          ${{ env.UV_CACHE_DIR }}
          .venv
        key: ${{ runner.os }}-uv-integration-${{ hashFiles('**/pyproject.toml', '**/requirements*.txt') }}
    
    - name: Install dependencies
      run: |
        uv venv
        source .venv/bin/activate
        uv pip install -e ".[test]"
    
    - name: Run integration tests
      env:
        DATABASE_URL: postgresql://test:test@localhost:5432/test_db
        REDIS_URL: redis://localhost:6379/0
      run: |
        source .venv/bin/activate
        pytest tests/integration/ -v --tb=short

  # 성능 벤치마크
  benchmark:
    name: Performance Benchmark
    needs: quality-checks
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    
    - name: Install uv
      run: |
        curl -LsSf https://astral.sh/uv/install.sh | sh
        echo "$HOME/.cargo/bin" >> $GITHUB_PATH
    
    - name: Benchmark pip vs uv
      run: |
        # Create test requirements
        cat > benchmark-requirements.txt << EOF
        numpy==1.24.3
        pandas==2.0.3
        scikit-learn==1.3.0
        requests==2.31.0
        fastapi==0.104.1
        pydantic==2.5.0
        sqlalchemy==2.0.23
        EOF
        
        # Benchmark pip
        python -m venv .venv_pip
        source .venv_pip/bin/activate
        echo "Benchmarking pip..."
        PIP_TIME=$(time -p pip install -r benchmark-requirements.txt 2>&1 | grep real | awk '{print $2}')
        deactivate
        rm -rf .venv_pip
        
        # Benchmark uv
        echo "Benchmarking uv..."
        uv venv .venv_uv
        source .venv_uv/bin/activate
        UV_TIME=$(time -p uv pip install -r benchmark-requirements.txt 2>&1 | grep real | awk '{print $2}')
        deactivate
        rm -rf .venv_uv
        
        # Calculate speedup
        SPEEDUP=$(echo "scale=2; $PIP_TIME / $UV_TIME" | bc)
        
        # Create summary
        echo "## Performance Benchmark Results" >> $GITHUB_STEP_SUMMARY
        echo "" >> $GITHUB_STEP_SUMMARY
        echo "| Tool | Time (seconds) |" >> $GITHUB_STEP_SUMMARY
        echo "|------|----------------|" >> $GITHUB_STEP_SUMMARY
        echo "| pip  | $PIP_TIME |" >> $GITHUB_STEP_SUMMARY
        echo "| uv   | $UV_TIME |" >> $GITHUB_STEP_SUMMARY
        echo "" >> $GITHUB_STEP_SUMMARY
        echo "**Speedup: ${SPEEDUP}x** 🚀" >> $GITHUB_STEP_SUMMARY
    
    - name: Store benchmark results
      uses: actions/upload-artifact@v3
      with:
        name: benchmark-results
        path: |
          benchmark-*.txt

  # Docker 빌드 테스트
  docker-build:
    name: Docker Build Test
    needs: quality-checks
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Build Docker image
      uses: docker/build-push-action@v5
      with:
        context: .
        file: ./Dockerfile.uv
        push: false
        tags: ai-agent-framework:test
        cache-from: type=gha
        cache-to: type=gha,mode=max
        build-args: |
          PYTHON_VERSION=${{ env.PYTHON_VERSION }}
    
    - name: Test Docker image
      run: |
        docker run --rm ai-agent-framework:test python -c "import app; print('Docker image OK')"

  # 최종 상태 체크
  ci-success:
    name: CI Success
    needs: [quality-checks, test, integration-test, docker-build]
    runs-on: ubuntu-latest
    if: success()
    
    steps:
    - name: Success notification
      run: |
        echo "✅ All CI checks passed successfully!"
        echo "## CI Pipeline Success ✅" >> $GITHUB_STEP_SUMMARY
        echo "" >> $GITHUB_STEP_SUMMARY
        echo "All checks have passed:" >> $GITHUB_STEP_SUMMARY
        echo "- ✅ Code quality checks" >> $GITHUB_STEP_SUMMARY
        echo "- ✅ Unit tests (all platforms)" >> $GITHUB_STEP_SUMMARY
        echo "- ✅ Integration tests" >> $GITHUB_STEP_SUMMARY
        echo "- ✅ Docker build" >> $GITHUB_STEP_SUMMARY
```

#### SubTask 3.1.2: CD 파이프라인 수정
**담당자**: 배포 엔지니어  
**예상 소요시간**: 2시간

```yaml
# .github/workflows/cd.yml
name: CD Pipeline

on:
  push:
    branches: [main]
    tags:
      - 'v*'
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deployment environment'
        required: true
        default: 'staging'
        type: choice
        options:
          - staging
          - production

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}
  PYTHON_VERSION: '3.11'

jobs:
  # 빌드 및 푸시
  build-and-push:
    name: Build and Push Docker Image
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}
      image-digest: ${{ steps.build.outputs.digest }}
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=semver,pattern={{version}}
          type=semver,pattern={{major}}.{{minor}}
          type=semver,pattern={{major}}
          type=sha,prefix={{branch}}-
    
    - name: Build and push Docker image
      id: build
      uses: docker/build-push-action@v5
      with:
        context: .
        file: ./Dockerfile.uv
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
        build-args: |
          PYTHON_VERSION=${{ env.PYTHON_VERSION }}
          BUILD_DATE=${{ github.event.head_commit.timestamp }}
          VCS_REF=${{ github.sha }}
    
    - name: Generate SBOM
      uses: anchore/sbom-action@v0
      with:
        image: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}@${{ steps.build.outputs.digest }}
        format: spdx-json
        output-file: sbom.spdx.json
    
    - name: Upload SBOM
      uses: actions/upload-artifact@v3
      with:
        name: sbom
        path: sbom.spdx.json

  # 스테이징 배포
  deploy-staging:
    name: Deploy to Staging
    needs: build-and-push
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' || github.event.inputs.environment == 'staging'
    environment:
      name: staging
      url: https://staging.ai-agent-framework.com
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Install kubectl
      uses: azure/setup-kubectl@v3
      with:
        version: 'v1.28.0'
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1
    
    - name: Update kubeconfig
      run: |
        aws eks update-kubeconfig --name staging-cluster --region us-east-1
    
    - name: Deploy to Kubernetes
      run: |
        # Update image in deployment
        kubectl set image deployment/agent-api \
          agent-api=${{ needs.build-and-push.outputs.image-tag }} \
          -n staging
        
        # Wait for rollout
        kubectl rollout status deployment/agent-api -n staging --timeout=5m
        
        # Verify deployment
        kubectl get pods -n staging -l app=agent-api
    
    - name: Run smoke tests
      run: |
        # Wait for service to be ready
        sleep 30
        
        # Run smoke tests
        curl -f https://staging.ai-agent-framework.com/health || exit 1
        curl -f https://staging.ai-agent-framework.com/api/v1/status || exit 1
    
    - name: Notify deployment
      uses: 8398a7/action-slack@v3
      if: always()
      with:
        status: ${{ job.status }}
        text: |
          Staging Deployment ${{ job.status }}
          Image: ${{ needs.build-and-push.outputs.image-tag }}
        webhook_url: ${{ secrets.SLACK_WEBHOOK }}

  # 프로덕션 배포
  deploy-production:
    name: Deploy to Production
    needs: [build-and-push, deploy-staging]
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/v') || github.event.inputs.environment == 'production'
    environment:
      name: production
      url: https://ai-agent-framework.com
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID_PROD }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY_PROD }}
        aws-region: us-east-1
    
    - name: Update kubeconfig
      run: |
        aws eks update-kubeconfig --name production-cluster --region us-east-1
    
    - name: Create backup
      run: |
        # Backup current deployment
        kubectl get deployment agent-api -n production -o yaml > backup-deployment.yaml
        kubectl get service agent-api -n production -o yaml > backup-service.yaml
        
        # Upload backups
        aws s3 cp backup-deployment.yaml s3://prod-backups/deployments/$(date +%Y%m%d-%H%M%S)-deployment.yaml
        aws s3 cp backup-service.yaml s3://prod-backups/deployments/$(date +%Y%m%d-%H%M%S)-service.yaml
    
    - name: Deploy to Production (Canary)
      run: |
        # Deploy canary version (10% traffic)
        kubectl apply -f - <<EOF
        apiVersion: v1
        kind: Service
        metadata:
          name: agent-api-canary
          namespace: production
        spec:
          selector:
            app: agent-api
            version: canary
          ports:
            - port: 80
              targetPort: 8000
        ---
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: agent-api-canary
          namespace: production
        spec:
          replicas: 2
          selector:
            matchLabels:
              app: agent-api
              version: canary
          template:
            metadata:
              labels:
                app: agent-api
                version: canary
            spec:
              containers:
              - name: agent-api
                image: ${{ needs.build-and-push.outputs.image-tag }}
                ports:
                - containerPort: 8000
                env:
                - name: ENV
                  value: "production"
                livenessProbe:
                  httpGet:
                    path: /health
                    port: 8000
                  initialDelaySeconds: 30
                  periodSeconds: 10
                readinessProbe:
                  httpGet:
                    path: /ready
                    port: 8000
                  initialDelaySeconds: 5
                  periodSeconds: 5
        EOF
        
        # Wait for canary rollout
        kubectl rollout status deployment/agent-api-canary -n production --timeout=5m
    
    - name: Monitor canary metrics
      run: |
        # Monitor for 5 minutes
        echo "Monitoring canary deployment for 5 minutes..."
        sleep 300
        
        # Check error rates
        # This would typically query your monitoring system
        # For now, we'll do a simple health check
        CANARY_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" https://ai-agent-framework.com/health)
        
        if [ "$CANARY_HEALTH" != "200" ]; then
          echo "Canary health check failed!"
          exit 1
        fi
    
    - name: Promote to full production
      run: |
        # Update main deployment
        kubectl set image deployment/agent-api \
          agent-api=${{ needs.build-and-push.outputs.image-tag }} \
          -n production
        
        # Wait for rollout
        kubectl rollout status deployment/agent-api -n production --timeout=10m
        
        # Remove canary
        kubectl delete deployment agent-api-canary -n production
        kubectl delete service agent-api-canary -n production
    
    - name: Verify production deployment
      run: |
        # Run production tests
        curl -f https://ai-agent-framework.com/health || exit 1
        curl -f https://ai-agent-framework.com/api/v1/status || exit 1
        
        # Run more comprehensive tests
        python scripts/production_tests.py
    
    - name: Create release
      uses: actions/create-release@v1
      if: startsWith(github.ref, 'refs/tags/v')
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: ${{ github.ref }}
        release_name: Release ${{ github.ref }}
        body: |
          ## Changes in this release
          - Docker image: ${{ needs.build-and-push.outputs.image-tag }}
          - Digest: ${{ needs.build-and-push.outputs.image-digest }}
          
          ## Deployment notes
          - Deployed to production with canary rollout
          - All health checks passed
        draft: false
        prerelease: false
    
    - name: Notify deployment
      uses: 8398a7/action-slack@v3
      if: always()
      with:
        status: ${{ job.status }}
        text: |
          Production Deployment ${{ job.status }}
          Version: ${{ github.ref }}
          Image: ${{ needs.build-and-push.outputs.image-tag }}
        webhook_url: ${{ secrets.SLACK_WEBHOOK_PROD }}

  # 롤백 작업 (수동 트리거)
  rollback:
    name: Rollback Deployment
    runs-on: ubuntu-latest
    if: github.event_name == 'workflow_dispatch'
    environment:
      name: ${{ github.event.inputs.environment }}
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1
    
    - name: Rollback deployment
      run: |
        NAMESPACE=${{ github.event.inputs.environment }}
        
        # Get previous revision
        PREVIOUS_REVISION=$(kubectl rollout history deployment/agent-api -n $NAMESPACE | tail -2 | head -1 | awk '{print $1}')
        
        # Rollback
        kubectl rollout undo deployment/agent-api -n $NAMESPACE --to-revision=$PREVIOUS_REVISION
        
        # Wait for rollback
        kubectl rollout status deployment/agent-api -n $NAMESPACE --timeout=5m
        
        echo "Rolled back to revision $PREVIOUS_REVISION"
```

#### SubTask 3.1.3: 캐싱 전략 최적화
**담당자**: 성능 엔지니어  
**예상 소요시간**: 1시간

```yaml
# .github/workflows/cache-strategy.yml
name: Cache Strategy Test

on:
  workflow_dispatch:
  schedule:
    - cron: '0 2 * * 0'  # Weekly on Sunday at 2 AM

env:
  UV_CACHE_DIR: ~/.cache/uv

jobs:
  test-cache-strategies:
    name: Test Cache Strategy - ${{ matrix.strategy }}
    runs-on: ubuntu-latest
    strategy:
      matrix:
        strategy:
          - name: 'full-cache'
            cache-key: 'uv-full-${{ hashFiles(''**/pyproject.toml'', ''**/requirements*.txt'') }}'
            cache-paths: |
              ~/.cache/uv
              .venv
          
          - name: 'uv-only'
            cache-key: 'uv-only-${{ hashFiles(''**/pyproject.toml'', ''**/requirements*.txt'') }}'
            cache-paths: |
              ~/.cache/uv
          
          - name: 'split-cache'
            cache-key: 'uv-split'
            cache-paths: ''  # Will use multiple caches
          
          - name: 'no-cache'
            cache-key: ''
            cache-paths: ''
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install uv
      run: |
        curl -LsSf https://astral.sh/uv/install.sh | sh
        echo "$HOME/.cargo/bin" >> $GITHUB_PATH
    
    # Strategy: Full cache
    - name: Cache (full-cache)
      if: matrix.strategy.name == 'full-cache'
      uses: actions/cache@v3
      with:
        path: ${{ matrix.strategy.cache-paths }}
        key: ${{ matrix.strategy.cache-key }}
        restore-keys: |
          uv-full-
    
    # Strategy: uv only
    - name: Cache (uv-only)
      if: matrix.strategy.name == 'uv-only'
      uses: actions/cache@v3
      with:
        path: ${{ matrix.strategy.cache-paths }}
        key: ${{ matrix.strategy.cache-key }}
        restore-keys: |
          uv-only-
    
    # Strategy: Split cache
    - name: Cache uv packages (split-cache)
      if: matrix.strategy.name == 'split-cache'
      uses: actions/cache@v3
      with:
        path: ~/.cache/uv
        key: uv-packages-${{ hashFiles('**/requirements*.txt') }}
        restore-keys: |
          uv-packages-
    
    - name: Cache venv (split-cache)
      if: matrix.strategy.name == 'split-cache'
      uses: actions/cache@v3
      with:
        path: .venv
        key: venv-${{ runner.os }}-${{ hashFiles('**/pyproject.toml') }}
        restore-keys: |
          venv-${{ runner.os }}-
    
    # Measure performance
    - name: Measure installation time
      run: |
        # Clear any existing venv
        rm -rf .venv
        
        # Record start time
        START_TIME=$(date +%s.%N)
        
        # Create venv and install
        uv venv
        source .venv/bin/activate
        uv pip install -e ".[dev,test]"
        
        # Record end time
        END_TIME=$(date +%s.%N)
        
        # Calculate duration
        DURATION=$(echo "$END_TIME - $START_TIME" | bc)
        
        # Get cache sizes
        UV_CACHE_SIZE=$(du -sh ~/.cache/uv 2>/dev/null | cut -f1 || echo "0")
        VENV_SIZE=$(du -sh .venv 2>/dev/null | cut -f1 || echo "0")
        
        # Output results
        echo "## Cache Strategy: ${{ matrix.strategy.name }}" >> $GITHUB_STEP_SUMMARY
        echo "" >> $GITHUB_STEP_SUMMARY
        echo "| Metric | Value |" >> $GITHUB_STEP_SUMMARY
        echo "|--------|-------|" >> $GITHUB_STEP_SUMMARY
        echo "| Installation Time | ${DURATION}s |" >> $GITHUB_STEP_SUMMARY
        echo "| UV Cache Size | $UV_CACHE_SIZE |" >> $GITHUB_STEP_SUMMARY
        echo "| Venv Size | $VENV_SIZE |" >> $GITHUB_STEP_SUMMARY
        echo "| Total Packages | $(uv pip list | wc -l) |" >> $GITHUB_STEP_SUMMARY
        
        # Save results for comparison
        echo "${{ matrix.strategy.name }},$DURATION,$UV_CACHE_SIZE,$VENV_SIZE" >> results.csv
    
    - name: Upload results
      uses: actions/upload-artifact@v3
      with:
        name: cache-strategy-results-${{ matrix.strategy.name }}
        path: results.csv

  # 결과 분석
  analyze-results:
    name: Analyze Cache Strategy Results
    needs: test-cache-strategies
    runs-on: ubuntu-latest
    
    steps:
    - name: Download all results
      uses: actions/download-artifact@v3
      with:
        path: results
    
    - name: Analyze and create report
      run: |
        # Combine all results
        echo "Strategy,Duration,UV_Cache,Venv_Size" > combined_results.csv
        cat results/*/results.csv >> combined_results.csv
        
        # Create analysis script
        cat > analyze.py << 'EOF'
        import csv
        import statistics
        
        results = []
        with open('combined_results.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                results.append({
                    'strategy': row['Strategy'],
                    'duration': float(row['Duration']),
                    'uv_cache': row['UV_Cache'],
                    'venv_size': row['Venv_Size']
                })
        
        # Sort by duration
        results.sort(key=lambda x: x['duration'])
        
        print("# Cache Strategy Analysis")
        print()
        print("## Performance Ranking")
        print()
        print("| Rank | Strategy | Duration | UV Cache | Venv Size |")
        print("|------|----------|----------|----------|-----------|")
        
        for i, r in enumerate(results, 1):
            print(f"| {i} | {r['strategy']} | {r['duration']:.2f}s | {r['uv_cache']} | {r['venv_size']} |")
        
        print()
        print("## Recommendations")
        print()
        
        best = results[0]
        if best['strategy'] == 'full-cache':
            print("✅ **Full cache strategy is recommended** - Caching both uv packages and venv provides the best performance.")
        elif best['strategy'] == 'uv-only':
            print("✅ **UV-only cache strategy is recommended** - Caching only uv packages provides good performance with less storage.")
        elif best['strategy'] == 'split-cache':
            print("✅ **Split cache strategy is recommended** - Separate caches for uv and venv provide flexibility.")
        
        # Calculate speedup
        no_cache = next((r for r in results if r['strategy'] == 'no-cache'), None)
        if no_cache and best['strategy'] != 'no-cache':
            speedup = no_cache['duration'] / best['duration']
            print(f"\n**Speedup: {speedup:.1f}x** compared to no cache")
        EOF
        
        python analyze.py >> $GITHUB_STEP_SUMMARY
        
        # Save full report
        python analyze.py > cache_strategy_report.md
    
    - name: Upload analysis report
      uses: actions/upload-artifact@v3
      with:
        name: cache-strategy-analysis
        path: |
          combined_results.csv
          cache_strategy_report.md
    
    - name: Update cache strategy documentation
      run: |
        echo "Based on the analysis, update .github/workflows/README.md with the recommended cache strategy."
```

### Task 3.2: Docker 이미지 최적화

#### SubTask 3.2.1: Multi-stage Dockerfile 작성
**담당자**: 컨테이너 전문가  
**예상 소요시간**: 3시간

```dockerfile
# Dockerfile.uv - Optimized multi-stage build with uv
# Build with: docker build -f Dockerfile.uv -t ai-agent-framework:latest .

# Arguments
ARG PYTHON_VERSION=3.11
ARG UV_VERSION=0.1.0

# Stage 1: UV installer
FROM alpine:3.19 AS uv-installer

RUN apk add --no-cache curl
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
RUN mv /root/.cargo/bin/uv /usr/local/bin/uv

# Stage 2: Python dependencies builder
FROM python:${PYTHON_VERSION}-slim AS builder

# Install system dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy uv from installer stage
COPY --from=uv-installer /usr/local/bin/uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml .
COPY requirements*.txt ./

# Create virtual environment and install dependencies
ENV VIRTUAL_ENV=/opt/venv
RUN uv venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies
RUN uv pip install --no-cache -r requirements.txt

# Stage 3: Development image (optional)
FROM builder AS development

# Install dev dependencies
COPY requirements-dev.txt .
RUN uv pip install --no-cache -r requirements-dev.txt

# Copy application code
COPY . .

# Install package in editable mode
RUN uv pip install -e .

# Development command
CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]

# Stage 4: Production runtime
FROM python:${PYTHON_VERSION}-slim AS runtime

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set environment variables
ENV VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appuser . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["gunicorn", "app.main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]

# Stage 5: Test runner
FROM development AS test

# Run tests
RUN pytest tests/ -v --cov=app --cov-report=term-missing

# Stage 6: Production with monitoring
FROM runtime AS production-monitored

# Install monitoring agents (example with Datadog)
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    datadog-agent \
    && rm -rf /var/lib/apt/lists/*

# Copy monitoring configs
COPY monitoring/datadog.yaml /etc/datadog-agent/datadog.yaml

USER appuser

# Start script that runs both the app and monitoring
COPY scripts/start-with-monitoring.sh /app/
CMD ["/app/start-with-monitoring.sh"]
```

```yaml
# docker-compose.yml - Development environment with uv
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.uv
      target: development
    volumes:
      - .:/app
      - uv-cache:/root/.cache/uv
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/app_db
      - REDIS_URL=redis://redis:6379/0
      - ENVIRONMENT=development
    depends_on:
      - db
      - redis
    command: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=app_db
    volumes:
      - postgres-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data
    ports:
      - "6379:6379"

  # Development tools
  pgadmin:
    image: dpage/pgadmin4:latest
    environment:
      - PGADMIN_DEFAULT_EMAIL=admin@example.com
      - PGADMIN_DEFAULT_PASSWORD=admin
    ports:
      - "5050:80"
    depends_on:
      - db

volumes:
  postgres-data:
  redis-data:
  uv-cache:
```

#### SubTask 3.2.2: 이미지 크기 최적화
**담당자**: 인프라 엔지니어  
**예상 소요시간**: 2시간

```bash
#!/bin/bash
# scripts/optimize-docker-image.sh

set -e

echo "🐳 Docker Image Optimization Script"
echo "=================================="

# Variables
IMAGE_NAME="ai-agent-framework"
ORIGINAL_TAG="${IMAGE_NAME}:original"
OPTIMIZED_TAG="${IMAGE_NAME}:optimized"

# Build original image for comparison
echo "📦 Building original image with pip..."
cat > Dockerfile.pip << 'EOF'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

docker build -f Dockerfile.pip -t $ORIGINAL_TAG .

# Build optimized image with uv
echo "🚀 Building optimized image with uv..."
docker build -f Dockerfile.uv -t $OPTIMIZED_TAG .

# Analyze image sizes
echo -e "\n📊 Image Size Comparison:"
echo "========================"

ORIGINAL_SIZE=$(docker image inspect $ORIGINAL_TAG --format='{{.Size}}' | numfmt --to=iec)
OPTIMIZED_SIZE=$(docker image inspect $OPTIMIZED_TAG --format='{{.Size}}' | numfmt --to=iec)

echo "Original (pip): $ORIGINAL_SIZE"
echo "Optimized (uv): $OPTIMIZED_SIZE"

# Use dive for detailed analysis
echo -e "\n🔍 Detailed layer analysis with dive..."
if command -v dive &> /dev/null; then
    echo "Original image layers:"
    dive $ORIGINAL_TAG --ci --highestWastedBytes=0.1 --lowestEfficiency=0.9 || true
    
    echo -e "\nOptimized image layers:"
    dive $OPTIMIZED_TAG --ci --highestWastedBytes=0.1 --lowestEfficiency=0.9 || true
else
    echo "ℹ️  Install dive for detailed analysis: https://github.com/wagoodman/dive"
fi

# Security scanning
echo -e "\n🔒 Security scanning..."
if command -v trivy &> /dev/null; then
    echo "Scanning optimized image:"
    trivy image --severity HIGH,CRITICAL $OPTIMIZED_TAG
else
    echo "ℹ️  Install trivy for security scanning: https://github.com/aquasecurity/trivy"
fi

# Create optimization report
cat > docker-optimization-report.md << EOF
# Docker Image Optimization Report

Generated: $(date)

## Size Comparison

| Image | Size |
|-------|------|
| Original (pip) | $ORIGINAL_SIZE |
| Optimized (uv) | $OPTIMIZED_SIZE |

## Optimization Techniques Used

1. **Multi-stage builds** - Separate build and runtime stages
2. **uv for faster installs** - Reduced build time and layer size
3. **Minimal base image** - python:3.11-slim instead of full image
4. **Non-root user** - Security best practice
5. **Layer caching** - Optimized COPY order for better caching

## Build Time Comparison

\`\`\`bash
# Measure build times
time docker build -f Dockerfile.pip -t test:pip . --no-cache
time docker build -f Dockerfile.uv -t test:uv . --no-cache
\`\`\`

## Recommendations

1. Use \`.dockerignore\` to exclude unnecessary files
2. Combine RUN commands where possible
3. Order COPY commands from least to most frequently changed
4. Use specific version tags instead of \`latest\`
5. Regularly update base images for security patches

## Next Steps

1. Set up automated image scanning in CI/CD
2. Implement image signing for supply chain security
3. Use distroless images for even smaller size
4. Consider using BuildKit cache mounts for pip/uv cache
EOF

echo -e "\n✅ Optimization report saved to docker-optimization-report.md"

# Create .dockerignore if it doesn't exist
if [ ! -f .dockerignore ]; then
    echo "📝 Creating .dockerignore..."
    cat > .dockerignore << 'EOF'
# Git
.git
.gitignore
.github

# Python
__pycache__
*.pyc
*.pyo
*.pyd
.Python
*.egg-info
.pytest_cache
.mypy_cache
.ruff_cache
.coverage
htmlcov
.tox

# Virtual environments
venv
.venv
env
.env.*

# IDE
.vscode
.idea
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project specific
logs
*.log
tests
docs
scripts
*.md
!README.md
docker-compose*.yml
Dockerfile*
!requirements*.txt

# Backups
*.backup
*.bak
*~
EOF
    echo "✅ .dockerignore created"
fi

# Generate BuildKit optimization example
cat > Dockerfile.buildkit << 'EOF'
# syntax=docker/dockerfile:1.4
# Dockerfile with BuildKit optimizations

ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim AS builder

# Mount cache for uv
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    uv pip install --prefix=/install -r requirements.txt

FROM python:${PYTHON_VERSION}-slim AS runtime

COPY --from=builder /install /usr/local

WORKDIR /app
COPY . .

# Run as non-root
USER nobody

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

echo -e "\n💡 BuildKit example saved to Dockerfile.buildkit"
echo "   Build with: DOCKER_BUILDKIT=1 docker build -f Dockerfile.buildkit ."

# Cleanup
rm -f Dockerfile.pip
```

#### SubTask 3.2.3: 레지스트리 통합
**담당자**: DevOps 엔지니어  
**예상 소요시간**: 2시간

```bash
#!/bin/bash
# scripts/registry-integration.sh

set -e

# Configuration
REGISTRY_URL="${DOCKER_REGISTRY:-ghcr.io}"
ORGANIZATION="${DOCKER_ORG:-your-org}"
REPOSITORY="${DOCKER_REPO:-ai-agent-framework}"
FULL_IMAGE_NAME="${REGISTRY_URL}/${ORGANIZATION}/${REPOSITORY}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "🚀 Docker Registry Integration Setup"
echo "===================================="

# Function to check command exists
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}❌ $1 is not installed${NC}"
        return 1
    fi
    echo -e "${GREEN}✅ $1 is installed${NC}"
    return 0
}

# Check prerequisites
echo -e "\n📋 Checking prerequisites..."
check_command docker
check_command jq

# Registry login
echo -e "\n🔐 Registry Authentication"
case $REGISTRY_URL in
    "ghcr.io")
        echo "GitHub Container Registry detected"
        echo "Please set GITHUB_TOKEN environment variable"
        if [ -n "$GITHUB_TOKEN" ]; then
            echo $GITHUB_TOKEN | docker login ghcr.io -u $GITHUB_USER --password-stdin
        fi
        ;;
    "docker.io")
        echo "Docker Hub detected"
        docker login
        ;;
    *)
        echo "Custom registry: $REGISTRY_URL"
        docker login $REGISTRY_URL
        ;;
esac

# Create build and push script
cat > .github/scripts/docker-build-push.sh << 'EOF'
#!/bin/bash
set -e

# Arguments
TAG=${1:-latest}
PLATFORMS=${2:-linux/amd64,linux/arm64}

# Build metadata
BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
VCS_REF=$(git rev-parse --short HEAD)
VERSION=$(git describe --tags --always)

# Enable BuildKit
export DOCKER_BUILDKIT=1

echo "🏗️  Building multi-platform image..."
docker buildx create --use --name multibuilder || true

docker buildx build \
    --platform $PLATFORMS \
    --build-arg BUILD_DATE=$BUILD_DATE \
    --build-arg VCS_REF=$VCS_REF \
    --build-arg VERSION=$VERSION \
    --tag $FULL_IMAGE_NAME:$TAG \
    --tag $FULL_IMAGE_NAME:$VERSION \
    --push \
    -f Dockerfile.uv \
    .

echo "✅ Image pushed to registry"
EOF

chmod +x .github/scripts/docker-build-push.sh

# Create GitHub Actions workflow for automated builds
cat > .github/workflows/docker-publish.yml << 'EOF'
name: Docker Publish

on:
  push:
    branches: [main]
    tags:
      - 'v*'
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
    - name: Checkout
      uses: actions/checkout@v4

    - name: Set up QEMU
      uses: docker/setup-qemu-action@v3

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3

    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=semver,pattern={{version}}
          type=semver,pattern={{major}}.{{minor}}
          type=sha

    - name: Build and push Docker image
      uses: docker/build-push-action@v5
      with:
        context: .
        file: ./Dockerfile.uv
        platforms: linux/amd64,linux/arm64
        push: ${{ github.event_name != 'pull_request' }}
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
        build-args: |
          BUILD_DATE=${{ github.event.head_commit.timestamp }}
          VCS_REF=${{ github.sha }}
          VERSION=${{ steps.meta.outputs.version }}

    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ steps.meta.outputs.version }}
        format: 'sarif'
        output: 'trivy-results.sarif'

    - name: Upload Trivy scan results
      uses: github/codeql-action/upload-sarif@v3
      if: always()
      with:
        sarif_file: 'trivy-results.sarif'
EOF

# Create Makefile targets for Docker operations
cat >> Makefile << 'EOF'

# Docker targets
.PHONY: docker-build
docker-build:
	@echo "$(GREEN)Building Docker image...$(NC)"
	@docker build -f Dockerfile.uv -t $(REPOSITORY):latest .

.PHONY: docker-run
docker-run:
	@echo "$(GREEN)Running Docker container...$(NC)"
	@docker run -it --rm \
		-p 8000:8000 \
		-v $(PWD):/app \
		--env-file .env \
		$(REPOSITORY):latest

.PHONY: docker-push
docker-push:
	@echo "$(GREEN)Pushing to registry...$(NC)"
	@.github/scripts/docker-build-push.sh latest

.PHONY: docker-scan
docker-scan:
	@echo "$(GREEN)Scanning for vulnerabilities...$(NC)"
	@trivy image $(REPOSITORY):latest

.PHONY: docker-clean
docker-clean:
	@echo "$(GREEN)Cleaning up Docker resources...$(NC)"
	@docker system prune -af --volumes
EOF

# Create container registry documentation
cat > docs/container-registry.md << EOF
# Container Registry Setup

## Overview

This project uses container images built with uv for faster builds and smaller image sizes.

## Registry Configuration

- **Registry**: $REGISTRY_URL
- **Organization**: $ORGANIZATION
- **Repository**: $REPOSITORY
- **Full Image**: $FULL_IMAGE_NAME

## Authentication

### GitHub Container Registry (ghcr.io)
\`\`\`bash
export GITHUB_TOKEN=your_token
echo \$GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
\`\`\`

### Docker Hub
\`\`\`bash
docker login
\`\`\`

### Custom Registry
\`\`\`bash
docker login $REGISTRY_URL
\`\`\`

## Building Images

### Local Build
\`\`\`bash
make docker-build
\`\`\`

### Multi-platform Build
\`\`\`bash
docker buildx build --platform linux/amd64,linux/arm64 -t $FULL_IMAGE_NAME:latest .
\`\`\`

## Pushing Images

### Manual Push
\`\`\`bash
make docker-push
\`\`\`

### Automated Push
Images are automatically built and pushed on:
- Push to main branch
- New tags (v*)

## Using Images

### Pull Latest
\`\`\`bash
docker pull $FULL_IMAGE_NAME:latest
\`\`\`

### Run Container
\`\`\`bash
docker run -p 8000:8000 $FULL_IMAGE_NAME:latest
\`\`\`

### Docker Compose
\`\`\`yaml
services:
  app:
    image: $FULL_IMAGE_NAME:latest
    ports:
      - "8000:8000"
\`\`\`

## Image Tags

- \`latest\` - Latest build from main branch
- \`v1.2.3\` - Specific version release
- \`sha-xxxxx\` - Specific commit
- \`pr-123\` - Pull request build

## Security

### Vulnerability Scanning
\`\`\`bash
make docker-scan
\`\`\`

### Image Signing
\`\`\`bash
cosign sign $FULL_IMAGE_NAME:latest
\`\`\`

## Troubleshooting

### Push Denied
- Check authentication: \`docker login\`
- Verify permissions in registry
- Check organization membership

### Build Failures
- Clear Docker cache: \`docker builder prune\`
- Check Dockerfile syntax
- Verify base image availability

### Large Image Size
- Use multi-stage builds
- Minimize layers
- Use .dockerignore
- Check for unnecessary dependencies
EOF

echo -e "\n✅ Registry integration complete!"
echo -e "\n📋 Next steps:"
echo "1. Update DOCKER_REGISTRY, DOCKER_ORG, DOCKER_REPO in your environment"
echo "2. Set up registry authentication in CI/CD"
echo "3. Test the build and push workflow"
echo "4. Enable vulnerability scanning"
```

### Task 3.3: 배포 스크립트 업데이트

#### SubTask 3.3.1: 배포 자동화 스크립트
**담당자**: 배포 엔지니어  
**예상 소요시간**: 3시간

```bash
#!/bin/bash
# scripts/deploy.sh - Automated deployment script with uv

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DEPLOYMENT_CONFIG="${DEPLOYMENT_CONFIG:-deployment.yaml}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_help() {
    cat << EOF
Usage: $0 [COMMAND] [OPTIONS]

Commands:
    deploy      Deploy application to specified environment
    rollback    Rollback to previous version
    status      Check deployment status
    logs        View deployment logs
    shell       Open shell in deployment environment

Options:
    -e, --environment   Environment (staging/production)
    -v, --version      Version to deploy
    -f, --force        Force deployment without confirmations
    -n, --dry-run      Show what would be deployed
    -h, --help         Show this help message

Examples:
    $0 deploy -e staging -v v1.2.3
    $0 rollback -e production
    $0 status -e staging
EOF
}

# Parse arguments
COMMAND=""
ENVIRONMENT=""
VERSION=""
FORCE=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        deploy|rollback|status|logs|shell)
            COMMAND=$1
            shift
            ;;
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -v|--version)
            VERSION="$2"
            shift 2
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -n|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate inputs
if [ -z "$COMMAND" ]; then
    log_error "No command specified"
    show_help
    exit 1
fi

if [ -z "$ENVIRONMENT" ]; then
    log_error "Environment not specified"
    exit 1
fi

# Load deployment configuration
load_config() {
    local config_file="$PROJECT_ROOT/deployments/$ENVIRONMENT/$DEPLOYMENT_CONFIG"
    
    if [ ! -f "$config_file" ]; then
        log_error "Configuration file not found: $config_file"
        exit 1
    fi
    
    log_info "Loading configuration from $config_file"
    
    # Parse YAML configuration
    eval $(python3 -c "
import yaml
with open('$config_file', 'r') as f:
    config = yaml.safe_load(f)
    for key, value in config.items():
        if isinstance(value, dict):
            for k, v in value.items():
                print(f'{key.upper()}_{k.upper()}=\"{v}\"')
        else:
            print(f'{key.upper()}=\"{value}\"')
    ")
}

# Pre-deployment checks
pre_deploy_checks() {
    log_info "Running pre-deployment checks..."
    
    # Check uv installation
    if ! command -v uv &> /dev/null; then
        log_error "uv is not installed"
        exit 1
    fi
    
    # Check Docker
    if ! docker info &> /dev/null; then
        log_error "Docker is not running"
        exit 1
    fi
    
    # Check kubectl (for Kubernetes deployments)
    if [ "$DEPLOYMENT_TYPE" = "kubernetes" ]; then
        if ! command -v kubectl &> /dev/null; then
            log_error "kubectl is not installed"
            exit 1
        fi
        
        # Check cluster connectivity
        if ! kubectl cluster-info &> /dev/null; then
            log_error "Cannot connect to Kubernetes cluster"
            exit 1
        fi
    fi
    
    # Check AWS CLI (for AWS deployments)
    if [ "$DEPLOYMENT_TYPE" = "aws" ]; then
        if ! command -v aws &> /dev/null; then
            log_error "AWS CLI is not installed"
            exit 1
        fi
        
        # Check AWS credentials
        if ! aws sts get-caller-identity &> /dev/null; then
            log_error "AWS credentials not configured"
            exit 1
        fi
    fi
    
    log_success "Pre-deployment checks passed"
}

# Build application
build_application() {
    log_info "Building application with uv..."
    
    cd "$PROJECT_ROOT"
    
    # Create virtual environment
    if [ ! -d ".venv" ]; then
        uv venv
    fi
    
    # Activate and install dependencies
    source .venv/bin/activate
    uv pip sync requirements.txt
    
    # Run tests
    if [ "$RUN_TESTS" = "true" ] && [ "$DRY_RUN" = false ]; then
        log_info "Running tests..."
        pytest tests/ -v --tb=short || {
            log_error "Tests failed"
            exit 1
        }
    fi
    
    # Build Docker image
    local image_tag="${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${VERSION:-latest}"
    
    log_info "Building Docker image: $image_tag"
    
    if [ "$DRY_RUN" = false ]; then
        docker build -f Dockerfile.uv -t "$image_tag" . || {
            log_error "Docker build failed"
            exit 1
        }
        
        # Push to registry
        if [ "$PUSH_IMAGE" = "true" ]; then
            log_info "Pushing image to registry..."
            docker push "$image_tag"
        fi
    fi
    
    log_success "Build completed"
}

# Deploy to Kubernetes
deploy_kubernetes() {
    local namespace="${KUBERNETES_NAMESPACE:-default}"
    local deployment="${KUBERNETES_DEPLOYMENT:-app}"
    local image_tag="${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${VERSION:-latest}"
    
    log_info "Deploying to Kubernetes cluster..."
    log_info "Namespace: $namespace"
    log_info "Deployment: $deployment"
    log_info "Image: $image_tag"
    
    if [ "$DRY_RUN" = true ]; then
        log_warning "DRY RUN - No actual deployment will occur"
        kubectl set image deployment/$deployment \
            $deployment=$image_tag \
            -n $namespace \
            --dry-run=client -o yaml
        return
    fi
    
    # Create namespace if not exists
    kubectl create namespace $namespace --dry-run=client -o yaml | kubectl apply -f -
    
    # Apply configurations
    if [ -d "$PROJECT_ROOT/deployments/$ENVIRONMENT/k8s" ]; then
        log_info "Applying Kubernetes configurations..."
        kubectl apply -f "$PROJECT_ROOT/deployments/$ENVIRONMENT/k8s/" -n $namespace
    fi
    
    # Update deployment image
    kubectl set image deployment/$deployment \
        $deployment=$image_tag \
        -n $namespace \
        --record
    
    # Wait for rollout
    log_info "Waiting for rollout to complete..."
    kubectl rollout status deployment/$deployment -n $namespace --timeout=10m
    
    # Verify deployment
    local ready_replicas=$(kubectl get deployment $deployment -n $namespace -o jsonpath='{.status.readyReplicas}')
    local desired_replicas=$(kubectl get deployment $deployment -n $namespace -o jsonpath='{.spec.replicas}')
    
    if [ "$ready_replicas" = "$desired_replicas" ]; then
        log_success "Deployment successful! $ready_replicas/$desired_replicas replicas ready"
    else
        log_error "Deployment failed! Only $ready_replicas/$desired_replicas replicas ready"
        exit 1
    fi
}

# Deploy to AWS ECS
deploy_aws_ecs() {
    local cluster="${AWS_ECS_CLUSTER}"
    local service="${AWS_ECS_SERVICE}"
    local task_definition="${AWS_ECS_TASK_DEFINITION}"
    local image_tag="${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${VERSION:-latest}"
    
    log_info "Deploying to AWS ECS..."
    log_info "Cluster: $cluster"
    log_info "Service: $service"
    log_info "Image: $image_tag"
    
    if [ "$DRY_RUN" = true ]; then
        log_warning "DRY RUN - No actual deployment will occur"
        return
    fi
    
    # Update task definition with new image
    local task_def_json=$(aws ecs describe-task-definition --task-definition $task_definition)
    local new_task_def=$(echo $task_def_json | jq --arg IMAGE "$image_tag" '.taskDefinition | .containerDefinitions[0].image = $IMAGE | del(.taskDefinitionArn) | del(.revision) | del(.status) | del(.requiresAttributes) | del(.compatibilities) | del(.registeredAt) | del(.registeredBy)')
    
    # Register new task definition
    local new_task_arn=$(echo $new_task_def | aws ecs register-task-definition --cli-input-json file:///dev/stdin --query 'taskDefinition.taskDefinitionArn' --output text)
    
    # Update service
    aws ecs update-service \
        --cluster $cluster \
        --service $service \
        --task-definition $new_task_arn \
        --force-new-deployment
    
    # Wait for service to stabilize
    log_info "Waiting for service to stabilize..."
    aws ecs wait services-stable --cluster $cluster --services $service
    
    log_success "ECS deployment successful!"
}

# Deploy function
deploy() {
    load_config
    
    # Confirmation
    if [ "$FORCE" = false ] && [ "$DRY_RUN" = false ]; then
        echo -e "\n${YELLOW}Deployment Summary:${NC}"
        echo "  Environment: $ENVIRONMENT"
        echo "  Version: ${VERSION:-latest}"
        echo "  Type: $DEPLOYMENT_TYPE"
        echo ""
        read -p "Continue with deployment? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Deployment cancelled"
            exit 0
        fi
    fi
    
    # Run pre-deployment checks
    pre_deploy_checks
    
    # Build application
    build_application
    
    # Deploy based on type
    case $DEPLOYMENT_TYPE in
        kubernetes)
            deploy_kubernetes
            ;;
        aws)
            deploy_aws_ecs
            ;;
        docker-compose)
            deploy_docker_compose
            ;;
        *)
            log_error "Unknown deployment type: $DEPLOYMENT_TYPE"
            exit 1
            ;;
    esac
    
    # Post-deployment tasks
    if [ "$DRY_RUN" = false ]; then
        post_deploy_tasks
    fi
    
    log_success "Deployment completed successfully!"
}

# Rollback function
rollback() {
    load_config
    
    log_info "Starting rollback for $ENVIRONMENT environment..."
    
    case $DEPLOYMENT_TYPE in
        kubernetes)
            local namespace="${KUBERNETES_NAMESPACE:-default}"
            local deployment="${KUBERNETES_DEPLOYMENT:-app}"
            
            # Get rollout history
            log_info "Rollout history:"
            kubectl rollout history deployment/$deployment -n $namespace
            
            # Rollback to previous version
            kubectl rollout undo deployment/$deployment -n $namespace
            
            # Wait for rollout
            kubectl rollout status deployment/$deployment -n $namespace --timeout=10m
            ;;
        aws)
            # Implement AWS rollback
            log_error "AWS rollback not implemented yet"
            exit 1
            ;;
        *)
            log_error "Rollback not supported for deployment type: $DEPLOYMENT_TYPE"
            exit 1
            ;;
    esac
    
    log_success "Rollback completed successfully!"
}

# Status function
status() {
    load_config
    
    log_info "Checking deployment status for $ENVIRONMENT environment..."
    
    case $DEPLOYMENT_TYPE in
        kubernetes)
            local namespace="${KUBERNETES_NAMESPACE:-default}"
            local deployment="${KUBERNETES_DEPLOYMENT:-app}"
            
            echo -e "\n${GREEN}Deployment Status:${NC}"
            kubectl get deployment $deployment -n $namespace
            
            echo -e "\n${GREEN}Pods:${NC}"
            kubectl get pods -n $namespace -l app=$deployment
            
            echo -e "\n${GREEN}Recent Events:${NC}"
            kubectl get events -n $namespace --sort-by='.lastTimestamp' | tail -10
            ;;
        aws)
            local cluster="${AWS_ECS_CLUSTER}"
            local service="${AWS_ECS_SERVICE}"
            
            echo -e "\n${GREEN}Service Status:${NC}"
            aws ecs describe-services --cluster $cluster --services $service \
                --query 'services[0].{Status:status,Running:runningCount,Desired:desiredCount,Pending:pendingCount}'
            
            echo -e "\n${GREEN}Recent Tasks:${NC}"
            aws ecs list-tasks --cluster $cluster --service-name $service \
                --query 'taskArns' --output table
            ;;
        *)
            log_error "Status not supported for deployment type: $DEPLOYMENT_TYPE"
            exit 1
            ;;
    esac
}

# Post-deployment tasks
post_deploy_tasks() {
    log_info "Running post-deployment tasks..."
    
    # Run migrations if needed
    if [ "$RUN_MIGRATIONS" = "true" ]; then
        log_info "Running database migrations..."
        # Implement migration logic
    fi
    
    # Health checks
    if [ -n "$HEALTH_CHECK_URL" ]; then
        log_info "Running health checks..."
        
        local max_attempts=30
        local attempt=0
        
        while [ $attempt -lt $max_attempts ]; do
            if curl -sf "$HEALTH_CHECK_URL" > /dev/null; then
                log_success "Health check passed"
                break
            fi
            
            attempt=$((attempt + 1))
            log_info "Health check attempt $attempt/$max_attempts..."
            sleep 10
        done
        
        if [ $attempt -eq $max_attempts ]; then
            log_error "Health check failed after $max_attempts attempts"
            exit 1
        fi
    fi
    
    # Send notifications
    if [ "$SEND_NOTIFICATIONS" = "true" ]; then
        send_deployment_notification
    fi
}

# Send notifications
send_deployment_notification() {
    local message="Deployment completed: $ENVIRONMENT environment, version ${VERSION:-latest}"
    
    # Slack notification
    if [ -n "$SLACK_WEBHOOK" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"$message\"}" \
            "$SLACK_WEBHOOK"
    fi
    
    # Email notification
    if [ -n "$EMAIL_RECIPIENT" ]; then
        echo "$message" | mail -s "Deployment Notification" "$EMAIL_RECIPIENT"
    fi
}

# Main execution
case $COMMAND in
    deploy)
        deploy
        ;;
    rollback)
        rollback
        ;;
    status)
        status
        ;;
    logs)
        # Implement logs viewing
        log_error "Logs command not implemented yet"
        exit 1
        ;;
    shell)
        # Implement shell access
        log_error "Shell command not implemented yet"
        exit 1
        ;;
    *)
        log_error "Unknown command: $COMMAND"
        show_help
        exit 1
        ;;
esac
```

```yaml
# deployments/staging/deployment.yaml
# Staging environment configuration

deployment_type: kubernetes

# Docker configuration
docker:
  registry: ghcr.io
  image: your-org/ai-agent-framework
  push_image: true

# Kubernetes configuration
kubernetes:
  namespace: staging
  deployment: agent-api
  replicas: 2

# Build configuration
build:
  run_tests: true
  
# Health check
health_check:
  url: https://staging.example.com/health
  
# Notifications
notifications:
  send_notifications: true
  slack_webhook: ${SLACK_WEBHOOK}
  
# Feature flags
features:
  run_migrations: true
  enable_monitoring: true
```

#### SubTask 3.3.2: 환경별 설정 관리
**담당자**: 설정 관리자  
**예상 소요시간**: 2시간

```python
#!/usr/bin/env python3
# scripts/config_manager.py

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
import click
from cryptography.fernet import Fernet

@dataclass
class Environment:
    name: str
    config_path: Path
    secrets_path: Optional[Path] = None
    variables: Dict[str, Any] = None

class ConfigManager:
    """Manage environment-specific configurations"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "deployments"
        self.environments = self._load_environments()
        self._key = self._get_or_create_key()
        
    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key for secrets"""
        key_file = self.project_root / ".secrets.key"
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            os.chmod(key_file, 0o600)
            print(f"Created new encryption key: {key_file}")
            return key
    
    def _load_environments(self) -> Dict[str, Environment]:
        """Load all environment configurations"""
        environments = {}
        
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True)
            
        for env_dir in self.config_dir.iterdir():
            if env_dir.is_dir():
                env_name = env_dir.name
                config_path = env_dir / "config.yaml"
                secrets_path = env_dir / "secrets.enc"
                
                if config_path.exists():
                    with open(config_path, 'r') as f:
                        variables = yaml.safe_load(f)
                    
                    environments[env_name] = Environment(
                        name=env_name,
                        config_path=config_path,
                        secrets_path=secrets_path if secrets_path.exists() else None,
                        variables=variables
                    )
        
        return environments
    
    def create_environment(self, name: str, base: Optional[str] = None):
        """Create new environment configuration"""
        env_dir = self.config_dir / name
        env_dir.mkdir(parents=True, exist_ok=True)
        
        # Base configuration
        config = {
            'environment': name,
            'deployment': {
                'type': 'kubernetes',
                'namespace': name,
                'replicas': 1 if name == 'development' else 2
            },
            'app': {
                'name': 'ai-agent-framework',
                'version': '${VERSION}',
                'debug': name in ['development', 'staging']
            },
            'database': {
                'host': f'{name}-db.example.com',
                'port': 5432,
                'name': f'app_{name}'
            },
            'redis': {
                'host': f'{name}-redis.example.com',
                'port': 6379
            },
            'logging': {
                'level': 'DEBUG' if name == 'development' else 'INFO'
            }
        }
        
        # Copy from base environment if specified
        if base and base in self.environments:
            base_config = self.environments[base].variables
            config = self._merge_configs(base_config, config)
        
        # Write configuration
        config_path = env_dir / "config.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        # Create empty secrets file
        secrets_path = env_dir / "secrets.yaml"
        with open(secrets_path, 'w') as f:
            yaml.dump({
                'api_keys': {},
                'credentials': {},
                'certificates': {}
            }, f)
        
        # Create deployment files
        self._create_deployment_files(env_dir, name)
        
        print(f"Created environment: {name}")
        print(f"Configuration: {config_path}")
        print(f"Secrets: {secrets_path}")
    
    def _create_deployment_files(self, env_dir: Path, env_name: str):
        """Create deployment-specific files"""
        # Kubernetes manifests
        k8s_dir = env_dir / "k8s"
        k8s_dir.mkdir(exist_ok=True)
        
        # Namespace
        namespace_yaml = {
            'apiVersion': 'v1',
            'kind': 'Namespace',
            'metadata': {
                'name': env_name
            }
        }
        
        with open(k8s_dir / "namespace.yaml", 'w') as f:
            yaml.dump(namespace_yaml, f)
        
        # ConfigMap
        configmap_yaml = {
            'apiVersion': 'v1',
            'kind': 'ConfigMap',
            'metadata': {
                'name': 'app-config',
                'namespace': env_name
            },
            'data': {
                'APP_ENV': env_name,
                'LOG_LEVEL': 'INFO'
            }
        }
        
        with open(k8s_dir / "configmap.yaml", 'w') as f:
            yaml.dump(configmap_yaml, f)
        
        # Deployment
        deployment_yaml = {
            'apiVersion': 'apps/v1',
            'kind': 'Deployment',
            'metadata': {
                'name': 'agent-api',
                'namespace': env_name
            },
            'spec': {
                'replicas': 2 if env_name == 'production' else 1,
                'selector': {
                    'matchLabels': {
                        'app': 'agent-api'
                    }
                },
                'template': {
                    'metadata': {
                        'labels': {
                            'app': 'agent-api'
                        }
                    },
                    'spec': {
                        'containers': [{
                            'name': 'agent-api',
                            'image': 'ghcr.io/your-org/ai-agent-framework:latest',
                            'ports': [{
                                'containerPort': 8000
                            }],
                            'envFrom': [{
                                'configMapRef': {
                                    'name': 'app-config'
                                }
                            }, {
                                'secretRef': {
                                    'name': 'app-secrets'
                                }
                            }],
                            'resources': {
                                'requests': {
                                    'memory': '256Mi',
                                    'cpu': '100m'
                                },
                                'limits': {
                                    'memory': '512Mi' if env_name != 'production' else '1Gi',
                                    'cpu': '500m' if env_name != 'production' else '1000m'
                                }
                            }
                        }]
                    }
                }
            }
        }
        
        with open(k8s_dir / "deployment.yaml", 'w') as f:
            yaml.dump(deployment_yaml, f)
    
    def _merge_configs(self, base: Dict, overlay: Dict) -> Dict:
        """Deep merge configurations"""
        result = base.copy()
        
        for key, value in overlay.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def encrypt_secrets(self, env_name: str):
        """Encrypt secrets file"""
        if env_name not in self.environments:
            raise ValueError(f"Environment not found: {env_name}")
        
        env_dir = self.config_dir / env_name
        secrets_file = env_dir / "secrets.yaml"
        
        if not secrets_file.exists():
            raise FileNotFoundError(f"Secrets file not found: {secrets_file}")
        
        # Read secrets
        with open(secrets_file, 'r') as f:
            secrets = yaml.safe_load(f)
        
        # Encrypt
        fernet = Fernet(self._key)
        encrypted_data = fernet.encrypt(yaml.dump(secrets).encode())
        
        # Write encrypted file
        encrypted_file = env_dir / "secrets.enc"
        with open(encrypted_file, 'wb') as f:
            f.write(encrypted_data)
        
        # Remove plain text file
        secrets_file.unlink()
        
        print(f"Encrypted secrets for {env_name}")
        print(f"Encrypted file: {encrypted_file}")
    
    def decrypt_secrets(self, env_name: str) -> Dict[str, Any]:
        """Decrypt secrets file"""
        if env_name not in self.environments:
            raise ValueError(f"Environment not found: {env_name}")
        
        env = self.environments[env_name]
        
        if not env.secrets_path or not env.secrets_path.exists():
            return {}
        
        # Read encrypted file
        with open(env.secrets_path, 'rb') as f:
            encrypted_data = f.read()
        
        # Decrypt
        fernet = Fernet(self._key)
        decrypted_data = fernet.decrypt(encrypted_data)
        
        return yaml.safe_load(decrypted_data)
    
    def get_config(self, env_name: str, include_secrets: bool = False) -> Dict[str, Any]:
        """Get complete configuration for environment"""
        if env_name not in self.environments:
            raise ValueError(f"Environment not found: {env_name}")
        
        env = self.environments[env_name]
        config = env.variables.copy()
        
        if include_secrets:
            secrets = self.decrypt_secrets(env_name)
            config['secrets'] = secrets
        
        return config
    
    def validate_config(self, env_name: str) -> List[str]:
        """Validate environment configuration"""
        issues = []
        
        if env_name not in self.environments:
            issues.append(f"Environment not found: {env_name}")
            return issues
        
        config = self.get_config(env_name)
        
        # Required fields
        required_fields = [
            'environment',
            'deployment.type',
            'app.name',
            'database.host',
            'redis.host'
        ]
        
        for field in required_fields:
            value = config
            for part in field.split('.'):
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    issues.append(f"Missing required field: {field}")
                    break
        
        # Validate deployment type
        if config.get('deployment', {}).get('type') not in ['kubernetes', 'docker', 'aws']:
            issues.append("Invalid deployment type")
        
        # Validate replicas
        replicas = config.get('deployment', {}).get('replicas', 1)
        if not isinstance(replicas, int) or replicas < 1:
            issues.append("Invalid replica count")
        
        return issues
    
    def export_dotenv(self, env_name: str, output_file: str = ".env"):
        """Export configuration as .env file"""
        config = self.get_config(env_name, include_secrets=True)
        
        with open(output_file, 'w') as f:
            f.write(f"# Environment: {env_name}\n")
            f.write(f"# Generated by config_manager.py\n\n")
            
            self._write_dotenv_vars(f, config)
        
        print(f"Exported configuration to {output_file}")
    
    def _write_dotenv_vars(self, f, config: Dict, prefix: str = ""):
        """Recursively write configuration as environment variables"""
        for key, value in config.items():
            if isinstance(value, dict):
                new_prefix = f"{prefix}{key.upper()}_" if prefix else f"{key.upper()}_"
                self._write_dotenv_vars(f, value, new_prefix)
            else:
                var_name = f"{prefix}{key.upper()}"
                f.write(f"{var_name}={value}\n")

@click.group()
def cli():
    """Environment configuration manager"""
    pass

@cli.command()
@click.argument('name')
@click.option('--base', help='Base environment to copy from')
def create(name: str, base: Optional[str]):
    """Create new environment"""
    manager = ConfigManager()
    manager.create_environment(name, base)

@cli.command()
@click.argument('name')
def encrypt(name: str):
    """Encrypt secrets for environment"""
    manager = ConfigManager()
    manager.encrypt_secrets(name)

@cli.command()
@click.argument('name')
@click.option('--secrets', is_flag=True, help='Include decrypted secrets')
def show(name: str, secrets: bool):
    """Show environment configuration"""
    manager = ConfigManager()
    config = manager.get_config(name, include_secrets=secrets)
    print(yaml.dump(config, default_flow_style=False))

@cli.command()
@click.argument('name')
def validate(name: str):
    """Validate environment configuration"""
    manager = ConfigManager()
    issues = manager.validate_config(name)
    
    if issues:
        print("Configuration issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("Configuration is valid")

@cli.command()
@click.argument('name')
@click.option('--output', '-o', default='.env', help='Output file')
def export(name: str, output: str):
    """Export configuration as .env file"""
    manager = ConfigManager()
    manager.export_dotenv(name, output)

@cli.command()
def list():
    """List all environments"""
    manager = ConfigManager()
    
    print("Available environments:")
    for env_name, env in manager.environments.items():
        has_secrets = "Yes" if env.secrets_path else "No"
        print(f"  - {env_name} (secrets: {has_secrets})")

if __name__ == '__main__':
    cli()
```

#### SubTask 3.3.3: 모니터링 통합
**담당자**: 모니터링 엔지니어  
**예상 소요시간**: 2시간

```python
#!/usr/bin/env python3
# scripts/setup_monitoring.py

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, List
import requests
import click

class MonitoringSetup:
    """Setup monitoring for deployed applications"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.monitoring_dir = self.project_root / "monitoring"
        self.monitoring_dir.mkdir(exist_ok=True)
        
    def setup_prometheus(self, environment: str):
        """Setup Prometheus configuration"""
        print("📊 Setting up Prometheus monitoring...")
        
        # Prometheus configuration
        prometheus_config = {
            'global': {
                'scrape_interval': '15s',
                'evaluation_interval': '15s',
                'external_labels': {
                    'environment': environment,
                    'service': 'ai-agent-framework'
                }
            },
            'alerting': {
                'alertmanagers': [{
                    'static_configs': [{
                        'targets': ['alertmanager:9093']
                    }]
                }]
            },
            'rule_files': [
                '/etc/prometheus/rules/*.yaml'
            ],
            'scrape_configs': [
                {
                    'job_name': 'agent-api',
                    'static_configs': [{
                        'targets': ['agent-api:8000']
                    }],
                    'metrics_path': '/metrics'
                },
                {
                    'job_name': 'node-exporter',
                    'static_configs': [{
                        'targets': ['node-exporter:9100']
                    }]
                },
                {
                    'job_name': 'cadvisor',
                    'static_configs': [{
                        'targets': ['cadvisor:8080']
                    }]
                }
            ]
        }
        
        # Write Prometheus config
        prometheus_file = self.monitoring_dir / "prometheus.yaml"
        with open(prometheus_file, 'w') as f:
            yaml.dump(prometheus_config, f)
        
        # Create alert rules
        self._create_alert_rules()
        
        print(f"✅ Prometheus configuration saved to {prometheus_file}")
        
    def _create_alert_rules(self):
        """Create Prometheus alert rules"""
        rules_dir = self.monitoring_dir / "rules"
        rules_dir.mkdir(exist_ok=True)
        
        # Application alerts
        app_alerts = {
            'groups': [{
                'name': 'agent_api',
                'interval': '30s',
                'rules': [
                    {
                        'alert': 'HighErrorRate',
                        'expr': 'rate(http_requests_total{status=~"5.."}[5m]) > 0.05',
                        'for': '5m',
                        'labels': {
                            'severity': 'critical'
                        },
                        'annotations': {
                            'summary': 'High error rate detected',
                            'description': 'Error rate is above 5% for 5 minutes'
                        }
                    },
                    {
                        'alert': 'HighResponseTime',
                        'expr': 'histogram_quantile(0.95, http_request_duration_seconds_bucket) > 1',
                        'for': '5m',
                        'labels': {
                            'severity': 'warning'
                        },
                        'annotations': {
                            'summary': 'High response time detected',
                            'description': '95th percentile response time is above 1s'
                        }
                    },
                    {
                        'alert': 'PodDown',
                        'expr': 'up{job="agent-api"} == 0',
                        'for': '1m',
                        'labels': {
                            'severity': 'critical'
                        },
                        'annotations': {
                            'summary': 'Pod is down',
                            'description': 'Agent API pod has been down for 1 minute'
                        }
                    }
                ]
            }]
        }
        
        # Resource alerts
        resource_alerts = {
            'groups': [{
                'name': 'resources',
                'interval': '30s',
                'rules': [
                    {
                        'alert': 'HighCPUUsage',
                        'expr': 'rate(container_cpu_usage_seconds_total[5m]) * 100 > 80',
                        'for': '10m',
                        'labels': {
                            'severity': 'warning'
                        },
                        'annotations': {
                            'summary': 'High CPU usage',
                            'description': 'CPU usage is above 80% for 10 minutes'
                        }
                    },
                    {
                        'alert': 'HighMemoryUsage',
                        'expr': 'container_memory_usage_bytes / container_spec_memory_limit_bytes * 100 > 85',
                        'for': '5m',
                        'labels': {
                            'severity': 'warning'
                        },
                        'annotations': {
                            'summary': 'High memory usage',
                            'description': 'Memory usage is above 85% of limit'
                        }
                    },
                    {
                        'alert': 'DiskSpaceLow',
                        'expr': 'node_filesystem_avail_bytes / node_filesystem_size_bytes * 100 < 15',
                        'for': '5m',
                        'labels': {
                            'severity': 'critical'
                        },
                        'annotations': {
                            'summary': 'Low disk space',
                            'description': 'Disk space is below 15%'
                        }
                    }
                ]
            }]
        }
        
        # Write alert rules
        with open(rules_dir / "app_alerts.yaml", 'w') as f:
            yaml.dump(app_alerts, f)
        
        with open(rules_dir / "resource_alerts.yaml", 'w') as f:
            yaml.dump(resource_alerts, f)
        
    def setup_grafana(self, environment: str):
        """Setup Grafana dashboards"""
        print("📈 Setting up Grafana dashboards...")
        
        dashboards_dir = self.monitoring_dir / "grafana" / "dashboards"
        dashboards_dir.mkdir(parents=True, exist_ok=True)
        
        # Application dashboard
        app_dashboard = {
            "dashboard": {
                "title": f"AI Agent Framework - {environment}",
                "panels": [
                    {
                        "title": "Request Rate",
                        "targets": [{
                            "expr": "rate(http_requests_total[5m])"
                        }],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                    },
                    {
                        "title": "Error Rate",
                        "targets": [{
                            "expr": "rate(http_requests_total{status=~'5..'}[5m])"
                        }],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
                    },
                    {
                        "title": "Response Time (p95)",
                        "targets": [{
                            "expr": "histogram_quantile(0.95, http_request_duration_seconds_bucket)"
                        }],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
                    },
                    {
                        "title": "Active Agents",
                        "targets": [{
                            "expr": "agent_active_count"
                        }],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
                    }
                ]
            }
        }
        
        # Resource dashboard
        resource_dashboard = {
            "dashboard": {
                "title": f"Resource Usage - {environment}",
                "panels": [
                    {
                        "title": "CPU Usage",
                        "targets": [{
                            "expr": "rate(container_cpu_usage_seconds_total[5m]) * 100"
                        }],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                    },
                    {
                        "title": "Memory Usage",
                        "targets": [{
                            "expr": "container_memory_usage_bytes / 1024 / 1024 / 1024"
                        }],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
                    },
                    {
                        "title": "Network I/O",
                        "targets": [{
                            "expr": "rate(container_network_receive_bytes_total[5m])"
                        }],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
                    },
                    {
                        "title": "Disk Usage",
                        "targets": [{
                            "expr": "node_filesystem_avail_bytes / node_filesystem_size_bytes * 100"
                        }],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
                    }
                ]
            }
        }
        
        # Write dashboards
        with open(dashboards_dir / "app_dashboard.json", 'w') as f:
            json.dump(app_dashboard, f, indent=2)
        
        with open(dashboards_dir / "resource_dashboard.json", 'w') as f:
            json.dump(resource_dashboard, f, indent=2)
        
        # Grafana provisioning
        self._create_grafana_provisioning()
        
        print(f"✅ Grafana dashboards saved to {dashboards_dir}")
        
    def _create_grafana_provisioning(self):
        """Create Grafana provisioning configuration"""
        provisioning_dir = self.monitoring_dir / "grafana" / "provisioning"
        
        # Datasources
        datasources_dir = provisioning_dir / "datasources"
        datasources_dir.mkdir(parents=True, exist_ok=True)
        
        datasources_config = {
            'apiVersion': 1,
            'datasources': [{
                'name': 'Prometheus',
                'type': 'prometheus',
                'access': 'proxy',
                'url': 'http://prometheus:9090',
                'isDefault': True
            }]
        }
        
        with open(datasources_dir / "prometheus.yaml", 'w') as f:
            yaml.dump(datasources_config, f)
        
        # Dashboard provisioning
        dashboards_dir = provisioning_dir / "dashboards"
        dashboards_dir.mkdir(parents=True, exist_ok=True)
        
        dashboards_config = {
            'apiVersion': 1,
            'providers': [{
                'name': 'default',
                'orgId': 1,
                'folder': '',
                'type': 'file',
                'disableDeletion': False,
                'updateIntervalSeconds': 10,
                'options': {
                    'path': '/var/lib/grafana/dashboards'
                }
            }]
        }
        
        with open(dashboards_dir / "dashboards.yaml", 'w') as f:
            yaml.dump(dashboards_config, f)
        
    def setup_logging(self, environment: str):
        """Setup centralized logging"""
        print("📝 Setting up centralized logging...")
        
        # Fluent Bit configuration
        fluentbit_config = """
[SERVICE]
    Flush         5
    Daemon        off
    Log_Level     info

[INPUT]
    Name              forward
    Listen            0.0.0.0
    Port              24224

[INPUT]
    Name              tail
    Path              /var/log/containers/*.log
    Parser            docker
    Tag               kube.*
    Refresh_Interval  5

[FILTER]
    Name              kubernetes
    Match             kube.*
    Kube_URL          https://kubernetes.default.svc:443
    Kube_CA_File      /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    Kube_Token_File   /var/run/secrets/kubernetes.io/serviceaccount/token

[OUTPUT]
    Name              es
    Match             *
    Host              elasticsearch
    Port              9200
    Index             agent-logs
    Type              _doc

[OUTPUT]
    Name              stdout
    Match             *
    Format            json_lines
"""
        
        fluentbit_file = self.monitoring_dir / "fluent-bit.conf"
        with open(fluentbit_file, 'w') as f:
            f.write(fluentbit_config)
        
        # Elasticsearch index template
        index_template = {
            "index_patterns": ["agent-logs-*"],
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "index.lifecycle.name": "agent-logs-policy",
                "index.lifecycle.rollover_alias": "agent-logs"
            },
            "mappings": {
                "properties": {
                    "@timestamp": {"type": "date"},
                    "level": {"type": "keyword"},
                    "service": {"type": "keyword"},
                    "environment": {"type": "keyword"},
                    "message": {"type": "text"},
                    "trace_id": {"type": "keyword"},
                    "span_id": {"type": "keyword"}
                }
            }
        }
        
        template_file = self.monitoring_dir / "elasticsearch_template.json"
        with open(template_file, 'w') as f:
            json.dump(index_template, f, indent=2)
        
        print(f"✅ Logging configuration saved")
        
    def create_docker_compose(self):
        """Create Docker Compose file for monitoring stack"""
        print("🐳 Creating monitoring stack Docker Compose...")
        
        compose_config = {
            'version': '3.8',
            'services': {
                'prometheus': {
                    'image': 'prom/prometheus:latest',
                    'volumes': [
                        './monitoring/prometheus.yaml:/etc/prometheus/prometheus.yml',
                        './monitoring/rules:/etc/prometheus/rules',
                        'prometheus-data:/prometheus'
                    ],
                    'ports': ['9090:9090'],
                    'command': [
                        '--config.file=/etc/prometheus/prometheus.yml',
                        '--storage.tsdb.path=/prometheus',
                        '--web.console.libraries=/usr/share/prometheus/console_libraries',
                        '--web.console.templates=/usr/share/prometheus/consoles'
                    ]
                },
                'grafana': {
                    'image': 'grafana/grafana:latest',
                    'volumes': [
                        './monitoring/grafana/provisioning:/etc/grafana/provisioning',
                        './monitoring/grafana/dashboards:/var/lib/grafana/dashboards',
                        'grafana-data:/var/lib/grafana'
                    ],
                    'ports': ['3000:3000'],
                    'environment': {
                        'GF_SECURITY_ADMIN_PASSWORD': 'admin',
                        'GF_USERS_ALLOW_SIGN_UP': 'false'
                    }
                },
                'alertmanager': {
                    'image': 'prom/alertmanager:latest',
                    'volumes': [
                        './monitoring/alertmanager.yaml:/etc/alertmanager/alertmanager.yml',
                        'alertmanager-data:/alertmanager'
                    ],
                    'ports': ['9093:9093']
                },
                'node-exporter': {
                    'image': 'prom/node-exporter:latest',
                    'volumes': [
                        '/proc:/host/proc:ro',
                        '/sys:/host/sys:ro',
                        '/:/rootfs:ro'
                    ],
                    'command': [
                        '--path.procfs=/host/proc',
                        '--path.sysfs=/host/sys',
                        '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
                    ],
                    'ports': ['9100:9100']
                },
                'cadvisor': {
                    'image': 'gcr.io/cadvisor/cadvisor:latest',
                    'volumes': [
                        '/:/rootfs:ro',
                        '/var/run:/var/run:ro',
                        '/sys:/sys:ro',
                        '/var/lib/docker/:/var/lib/docker:ro',
                        '/dev/disk/:/dev/disk:ro'
                    ],
                    'ports': ['8080:8080'],
                    'privileged': True
                }
            },
            'volumes': {
                'prometheus-data': {},
                'grafana-data': {},
                'alertmanager-data': {}
            }
        }
        
        compose_file = self.monitoring_dir / "docker-compose.monitoring.yml"
        with open(compose_file, 'w') as f:
            yaml.dump(compose_config, f)
        
        print(f"✅ Docker Compose file saved to {compose_file}")
        
    def setup_application_metrics(self):
        """Setup application metrics collection"""
        print("📊 Setting up application metrics...")
        
        # Create metrics module
        metrics_dir = self.project_root / "app" / "monitoring"
        metrics_dir.mkdir(exist_ok=True)
        
        # Metrics module
        metrics_code = '''"""
Application metrics collection using Prometheus client
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from functools import wraps
import time

# Request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Agent metrics
agent_active_count = Gauge(
    'agent_active_count',
    'Number of active agents'
)

agent_task_duration_seconds = Histogram(
    'agent_task_duration_seconds',
    'Agent task duration in seconds',
    ['agent_type', 'task_type']
)

agent_errors_total = Counter(
    'agent_errors_total',
    'Total agent errors',
    ['agent_type', 'error_type']
)

# Database metrics
db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['query_type']
)

db_connections_active = Gauge(
    'db_connections_active',
    'Number of active database connections'
)

# Cache metrics
cache_hits_total = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_type']
)

cache_misses_total = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['cache_type']
)


def track_request_metrics(func):
    """Decorator to track HTTP request metrics"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            response = await func(*args, **kwargs)
            status = response.status_code
        except Exception as e:
            status = 500
            raise
        finally:
            duration = time.time() - start_time
            
            # Get request info from args
            request = args[0] if args else None
            method = request.method if request else 'UNKNOWN'
            endpoint = request.url.path if request else 'UNKNOWN'
            
            # Record metrics
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status=status
            ).inc()
            
            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
        
        return response
    
    return wrapper


def track_agent_metrics(agent_type: str):
    """Decorator to track agent metrics"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
            except Exception as e:
                agent_errors_total.labels(
                    agent_type=agent_type,
                    error_type=type(e).__name__
                ).inc()
                raise
            finally:
                duration = time.time() - start_time
                
                # Get task type from function name or args
                task_type = func.__name__
                
                agent_task_duration_seconds.labels(
                    agent_type=agent_type,
                    task_type=task_type
                ).observe(duration)
            
            return result
        
        return wrapper
    
    return decorator


async def metrics_endpoint():
    """Endpoint to expose metrics for Prometheus"""
    return generate_latest()
'''
        
        with open(metrics_dir / "__init__.py", 'w') as f:
            f.write(metrics_code)
        
        # FastAPI integration
        fastapi_integration = '''"""
FastAPI integration for metrics
"""
from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse
from .monitoring import (
    metrics_endpoint,
    track_request_metrics,
    http_requests_total,
    http_request_duration_seconds
)
import time

def setup_metrics(app: FastAPI):
    """Setup metrics collection for FastAPI app"""
    
    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next):
        start_time = time.time()
        
        try:
            response = await call_next(request)
            status = response.status_code
        except Exception as e:
            status = 500
            raise
        finally:
            duration = time.time() - start_time
            
            # Record metrics
            http_requests_total.labels(
                method=request.method,
                endpoint=request.url.path,
                status=status
            ).inc()
            
            http_request_duration_seconds.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(duration)
        
        return response
    
    @app.get("/metrics", response_class=PlainTextResponse)
    async def get_metrics():
        """Prometheus metrics endpoint"""
        return await metrics_endpoint()
'''
        
        with open(metrics_dir / "fastapi.py", 'w') as f:
            f.write(fastapi_integration)
        
        print("✅ Application metrics setup complete")
        
    def create_kubernetes_manifests(self, environment: str):
        """Create Kubernetes manifests for monitoring"""
        print("☸️  Creating Kubernetes monitoring manifests...")
        
        k8s_dir = self.monitoring_dir / "k8s"
        k8s_dir.mkdir(exist_ok=True)
        
        # ServiceMonitor for Prometheus Operator
        service_monitor = {
            'apiVersion': 'monitoring.coreos.com/v1',
            'kind': 'ServiceMonitor',
            'metadata': {
                'name': 'agent-api',
                'namespace': environment
            },
            'spec': {
                'selector': {
                    'matchLabels': {
                        'app': 'agent-api'
                    }
                },
                'endpoints': [{
                    'port': 'metrics',
                    'interval': '30s',
                    'path': '/metrics'
                }]
            }
        }
        
        with open(k8s_dir / "service-monitor.yaml", 'w') as f:
            yaml.dump(service_monitor, f)
        
        # PrometheusRule for alerts
        prometheus_rule = {
            'apiVersion': 'monitoring.coreos.com/v1',
            'kind': 'PrometheusRule',
            'metadata': {
                'name': 'agent-api-alerts',
                'namespace': environment
            },
            'spec': {
                'groups': [{
                    'name': 'agent-api',
                    'rules': [
                        {
                            'alert': 'AgentAPIDown',
                            'expr': 'up{job="agent-api"} == 0',
                            'for': '5m',
                            'labels': {
                                'severity': 'critical',
                                'service': 'agent-api'
                            },
                            'annotations': {
                                'summary': 'Agent API is down',
                                'description': 'Agent API has been down for more than 5 minutes'
                            }
                        }
                    ]
                }]
            }
        }
        
        with open(k8s_dir / "prometheus-rule.yaml", 'w') as f:
            yaml.dump(prometheus_rule, f)
        
        print(f"✅ Kubernetes manifests saved to {k8s_dir}")

@click.group()
def cli():
    """Monitoring setup CLI"""
    pass

@cli.command()
@click.argument('environment')
def setup(environment: str):
    """Setup complete monitoring stack"""
    setup = MonitoringSetup()
    
    # Setup all components
    setup.setup_prometheus(environment)
    setup.setup_grafana(environment)
    setup.setup_logging(environment)
    setup.setup_application_metrics()
    setup.create_docker_compose()
    setup.create_kubernetes_manifests(environment)
    
    print("\n✅ Monitoring setup complete!")
    print("\nNext steps:")
    print("1. Start monitoring stack: docker-compose -f monitoring/docker-compose.monitoring.yml up -d")
    print("2. Access Grafana: http://localhost:3000 (admin/admin)")
    print("3. Access Prometheus: http://localhost:9090")
    print("4. Import dashboards from monitoring/grafana/dashboards/")

@cli.command()
@click.argument('component')
@click.argument('environment')
def setup_component(component: str, environment: str):
    """Setup specific monitoring component"""
    setup = MonitoringSetup()
    
    if component == 'prometheus':
        setup.setup_prometheus(environment)
    elif component == 'grafana':
        setup.setup_grafana(environment)
    elif component == 'logging':
        setup.setup_logging(environment)
    elif component == 'metrics':
        setup.setup_application_metrics()
    else:
        print(f"Unknown component: {component}")
        print("Available: prometheus, grafana, logging, metrics")

if __name__ == '__main__':
    cli()
```

---

## 📋 Phase 4: 프로덕션 전환 및 모니터링 (Day 13-21)

### Task 4.1: 성능 모니터링 대시보드

#### SubTask 4.1.1: 메트릭 수집 시스템
**담당자**: 모니터링 엔지니어  
**예상 소요시간**: 4시간

```python
#!/usr/bin/env python3
# scripts/metrics_collector.py

import asyncio
import time
import psutil
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import json
from prometheus_client import CollectorRegistry, Gauge, Counter, Histogram, push_to_gateway
import logging

@dataclass
class SystemMetrics:
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_io_sent_mb: float
    network_io_received_mb: float
    open_files: int
    threads: int

@dataclass
class UvMetrics:
    timestamp: datetime
    cache_size_mb: float
    cache_hits: int
    cache_misses: int
    packages_installed: int
    install_time_seconds: float
    resolution_time_seconds: float
    download_time_seconds: float
    build_time_seconds: float

class MetricsCollector:
    """Collect system and uv-specific metrics"""
    
    def __init__(self, 
                 push_gateway: Optional[str] = None,
                 collection_interval: int = 60):
        self.push_gateway = push_gateway
        self.collection_interval = collection_interval
        self.registry = CollectorRegistry()
        self.logger = logging.getLogger(__name__)
        
        # System metrics
        self.cpu_usage = Gauge('system_cpu_usage_percent', 
                              'CPU usage percentage', 
                              registry=self.registry)
        self.memory_usage = Gauge('system_memory_usage_percent', 
                                 'Memory usage percentage', 
                                 registry=self.registry)
        self.memory_usage_mb = Gauge('system_memory_usage_mb', 
                                    'Memory usage in MB', 
                                    registry=self.registry)
        self.disk_io_read = Gauge('system_disk_io_read_mb', 
                                 'Disk I/O read in MB', 
                                 registry=self.registry)
        self.disk_io_write = Gauge('system_disk_io_write_mb', 
                                  'Disk I/O write in MB', 
                                  registry=self.registry)
        self.network_io_sent = Gauge('system_network_io_sent_mb', 
                                    'Network I/O sent in MB', 
                                    registry=self.registry)
        self.network_io_received = Gauge('system_network_io_received_mb', 
                                        'Network I/O received in MB', 
                                        registry=self.registry)
        
        # uv specific metrics
        self.uv_cache_size = Gauge('uv_cache_size_mb', 
                                  'uv cache size in MB', 
                                  registry=self.registry)
        self.uv_cache_hits = Counter('uv_cache_hits_total', 
                                    'Total uv cache hits', 
                                    registry=self.registry)
        self.uv_cache_misses = Counter('uv_cache_misses_total', 
                                      'Total uv cache misses', 
                                      registry=self.registry)
        self.uv_install_duration = Histogram('uv_install_duration_seconds', 
                                           'uv install duration in seconds',
                                           buckets=(0.1, 0.5, 1, 2, 5, 10, 30, 60),
                                           registry=self.registry)
        self.uv_packages_installed = Counter('uv_packages_installed_total', 
                                           'Total packages installed with uv', 
                                           registry=self.registry)
        
        # Initialize baseline metrics
        self.baseline_disk_io = psutil.disk_io_counters()
        self.baseline_network_io = psutil.net_io_counters()
        
    async def collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        # CPU and Memory
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        # Disk I/O
        current_disk_io = psutil.disk_io_counters()
        disk_read_mb = (current_disk_io.read_bytes - self.baseline_disk_io.read_bytes) / (1024 * 1024)
        disk_write_mb = (current_disk_io.write_bytes - self.baseline_disk_io.write_bytes) / (1024 * 1024)
        
        # Network I/O
        current_network_io = psutil.net_io_counters()
        network_sent_mb = (current_network_io.bytes_sent - self.baseline_network_io.bytes_sent) / (1024 * 1024)
        network_recv_mb = (current_network_io.bytes_recv - self.baseline_network_io.bytes_recv) / (1024 * 1024)
        
        # Process info
        process = psutil.Process()
        
        metrics = SystemMetrics(
            timestamp=datetime.now(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_mb=memory.used / (1024 * 1024),
            disk_io_read_mb=disk_read_mb,
            disk_io_write_mb=disk_write_mb,
            network_io_sent_mb=network_sent_mb,
            network_io_received_mb=network_recv_mb,
            open_files=len(process.open_files()),
            threads=process.num_threads()
        )
        
        # Update Prometheus metrics
        self.cpu_usage.set(metrics.cpu_percent)
        self.memory_usage.set(metrics.memory_percent)
        self.memory_usage_mb.set(metrics.memory_mb)
        self.disk_io_read.set(metrics.disk_io_read_mb)
        self.disk_io_write.set(metrics.disk_io_write_mb)
        self.network_io_sent.set(metrics.network_io_sent_mb)
        self.network_io_received.set(metrics.network_io_received_mb)
        
        # Update baselines
        self.baseline_disk_io = current_disk_io
        self.baseline_network_io = current_network_io
        
        return metrics
    
    async def collect_uv_metrics(self) -> Optional[UvMetrics]:
        """Collect uv-specific metrics"""
        try:
            import subprocess
            import os
            from pathlib import Path
            
            # Get uv cache size
            cache_dir = Path.home() / '.cache' / 'uv'
            cache_size_mb = 0
            
            if cache_dir.exists():
                for path in cache_dir.rglob('*'):
                    if path.is_file():
                        cache_size_mb += path.stat().st_size / (1024 * 1024)
            
            # Parse uv stats if available
            # This would need to be implemented based on uv's actual metrics output
            metrics = UvMetrics(
                timestamp=datetime.now(),
                cache_size_mb=cache_size_mb,
                cache_hits=0,  # Would need actual implementation
                cache_misses=0,
                packages_installed=0,
                install_time_seconds=0,
                resolution_time_seconds=0,
                download_time_seconds=0,
                build_time_seconds=0
            )
            
            # Update Prometheus metrics
            self.uv_cache_size.set(metrics.cache_size_mb)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting uv metrics: {e}")
            return None
    
    async def monitor_uv_command(self, cmd: List[str]) -> Dict[str, Any]:
        """Monitor a uv command execution"""
        start_time = time.time()
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        duration = time.time() - start_time
        
        # Record metrics
        self.uv_install_duration.observe(duration)
        
        if process.returncode == 0:
            # Try to parse package count from output
            output = stdout.decode()
            package_count = self._parse_package_count(output)
            if package_count:
                self.uv_packages_installed.inc(package_count)
        
        return {
            'command': ' '.join(cmd),
            'duration': duration,
            'success': process.returncode == 0,
            'stdout': stdout.decode(),
            'stderr': stderr.decode()
        }
    
    def _parse_package_count(self, output: str) -> int:
        """Parse package count from uv output"""
        # This would need to be implemented based on actual uv output format
        import re
        
        # Example pattern - adjust based on actual output
        match = re.search(r'Successfully installed (\d+) packages', output)
        if match:
            return int(match.group(1))
        
        return 0
    
    async def push_metrics(self):
        """Push metrics to Prometheus push gateway"""
        if self.push_gateway:
            try:
                push_to_gateway(
                    self.push_gateway,
                    job='uv_metrics_collector',
                    registry=self.registry
                )
                self.logger.info("Metrics pushed to gateway")
            except Exception as e:
                self.logger.error(f"Failed to push metrics: {e}")
    
    async def collect_and_store(self, storage_backend: Optional[Any] = None):
        """Collect metrics and optionally store them"""
        system_metrics = await self.collect_system_metrics()
        uv_metrics = await self.collect_uv_metrics()
        
        # Push to Prometheus
        await self.push_metrics()
        
        # Store to backend if provided
        if storage_backend:
            await storage_backend.store({
                'system': asdict(system_metrics),
                'uv': asdict(uv_metrics) if uv_metrics else None
            })
        
        return {
            'system': system_metrics,
            'uv': uv_metrics
        }
    
    async def run_continuous_monitoring(self):
        """Run continuous metrics collection"""
        self.logger.info(f"Starting continuous monitoring (interval: {self.collection_interval}s)")
        
        while True:
            try:
                metrics = await self.collect_and_store()
                self.logger.debug(f"Collected metrics: {metrics}")
                
            except Exception as e:
                self.logger.error(f"Error in metrics collection: {e}")
            
            await asyncio.sleep(self.collection_interval)


class MetricsComparator:
    """Compare pip vs uv metrics"""
    
    def __init__(self):
        self.pip_metrics: List[Dict] = []
        self.uv_metrics: List[Dict] = []
        
    async def benchmark_installation(self, requirements_file: str) -> Dict[str, Any]:
        """Benchmark pip vs uv installation"""
        results = {}
        
        # Benchmark pip
        pip_start = time.time()
        pip_process = await asyncio.create_subprocess_exec(
            'pip', 'install', '-r', requirements_file, '--dry-run',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await pip_process.communicate()
        pip_duration = time.time() - pip_start
        
        # Benchmark uv
        uv_start = time.time()
        uv_process = await asyncio.create_subprocess_exec(
            'uv', 'pip', 'install', '-r', requirements_file, '--dry-run',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await uv_process.communicate()
        uv_duration = time.time() - uv_start
        
        results = {
            'pip': {
                'duration': pip_duration,
                'success': pip_process.returncode == 0
            },
            'uv': {
                'duration': uv_duration,
                'success': uv_process.returncode == 0
            },
            'speedup': pip_duration / uv_duration if uv_duration > 0 else 0
        }
        
        return results
    
    def generate_comparison_report(self) -> str:
        """Generate comparison report between pip and uv"""
        report = """# pip vs uv Performance Comparison

## Summary Statistics

"""
        
        if not self.pip_metrics or not self.uv_metrics:
            return report + "No metrics collected yet.\n"
        
        # Calculate averages
        pip_avg_time = sum(m['duration'] for m in self.pip_metrics) / len(self.pip_metrics)
        uv_avg_time = sum(m['duration'] for m in self.uv_metrics) / len(self.uv_metrics)
        
        report += f"""
| Metric | pip | uv | Improvement |
|--------|-----|-----|-------------|
| Average Install Time | {pip_avg_time:.2f}s | {uv_avg_time:.2f}s | {pip_avg_time/uv_avg_time:.1f}x |
| Success Rate | {sum(m['success'] for m in self.pip_metrics)/len(self.pip_metrics)*100:.1f}% | {sum(m['success'] for m in self.uv_metrics)/len(self.uv_metrics)*100:.1f}% | - |

## Detailed Metrics

### Installation Times Distribution

```
pip:  Min: {min(m['duration'] for m in self.pip_metrics):.2f}s  Max: {max(m['duration'] for m in self.pip_metrics):.2f}s
uv:   Min: {min(m['duration'] for m in self.uv_metrics):.2f}s  Max: {max(m['duration'] for m in self.uv_metrics):.2f}s
```
"""
        
        return report


class MetricsDashboard:
    """Simple metrics dashboard server"""
    
    def __init__(self, collector: MetricsCollector, port: int = 8080):
        self.collector = collector
        self.port = port
        self.app = self._create_app()
        
    def _create_app(self):
        from aiohttp import web
        
        async def index(request):
            html = """
<!DOCTYPE html>
<html>
<head>
    <title>uv Metrics Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .metric { 
            display: inline-block; 
            margin: 10px; 
            padding: 15px; 
            border: 1px solid #ddd; 
            border-radius: 5px;
        }
        .chart-container { 
            width: 45%; 
            display: inline-block; 
            margin: 10px;
        }
    </style>
</head>
<body>
    <h1>uv Performance Metrics</h1>
    
    <div id="metrics">
        <div class="metric">
            <h3>CPU Usage</h3>
            <p id="cpu">-</p>
        </div>
        <div class="metric">
            <h3>Memory Usage</h3>
            <p id="memory">-</p>
        </div>
        <div class="metric">
            <h3>Cache Size</h3>
            <p id="cache">-</p>
        </div>
    </div>
    
    <div class="chart-container">
        <canvas id="performanceChart"></canvas>
    </div>
    
    <div class="chart-container">
        <canvas id="cacheChart"></canvas>
    </div>
    
    <script>
        // Initialize charts
        const perfCtx = document.getElementById('performanceChart').getContext('2d');
        const perfChart = new Chart(perfCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'CPU %',
                    data: [],
                    borderColor: 'rgb(255, 99, 132)',
                    tension: 0.1
                }, {
                    label: 'Memory %',
                    data: [],
                    borderColor: 'rgb(54, 162, 235)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
        
        // Update metrics
        async function updateMetrics() {
            try {
                const response = await fetch('/api/metrics');
                const data = await response.json();
                
                // Update text metrics
                document.getElementById('cpu').textContent = data.system.cpu_percent.toFixed(1) + '%';
                document.getElementById('memory').textContent = data.system.memory_percent.toFixed(1) + '%';
                document.getElementById('cache').textContent = (data.uv?.cache_size_mb || 0).toFixed(1) + ' MB';
                
                // Update charts
                const now = new Date().toLocaleTimeString();
                perfChart.data.labels.push(now);
                perfChart.data.datasets[0].data.push(data.system.cpu_percent);
                perfChart.data.datasets[1].data.push(data.system.memory_percent);
                
                // Keep only last 20 points
                if (perfChart.data.labels.length > 20) {
                    perfChart.data.labels.shift();
                    perfChart.data.datasets.forEach(dataset => dataset.data.shift());
                }
                
                perfChart.update();
                
            } catch (error) {
                console.error('Error fetching metrics:', error);
            }
        }
        
        // Update every 5 seconds
        setInterval(updateMetrics, 5000);
        updateMetrics();
    </script>
</body>
</html>
"""
            return web.Response(text=html, content_type='text/html')
        
        async def api_metrics(request):
            metrics = await self.collector.collect_and_store()
            return web.json_response({
                'system': asdict(metrics['system']),
                'uv': asdict(metrics['uv']) if metrics['uv'] else None
            })
        
        app = web.Application()
        app.router.add_get('/', index)
        app.router.add_get('/api/metrics', api_metrics)
        
        return app
    
    async def start(self):
        """Start the dashboard server"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', self.port)
        await site.start()
        print(f"Dashboard running at http://localhost:{self.port}")


async def main():
    """Main function to run metrics collection"""
    import argparse
    
    parser = argparse.ArgumentParser(description='uv metrics collector')
    parser.add_argument('--push-gateway', help='Prometheus push gateway URL')
    parser.add_argument('--interval', type=int, default=60, help='Collection interval in seconds')
    parser.add_argument('--dashboard', action='store_true', help='Run metrics dashboard')
    parser.add_argument('--benchmark', help='Run benchmark with requirements file')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create collector
    collector = MetricsCollector(
        push_gateway=args.push_gateway,
        collection_interval=args.interval
    )
    
    if args.benchmark:
        # Run benchmark
        comparator = MetricsComparator()
        result = await comparator.benchmark_installation(args.benchmark)
        print(f"\nBenchmark Results:")
        print(f"pip: {result['pip']['duration']:.2f}s")
        print(f"uv: {result['uv']['duration']:.2f}s")
        print(f"Speedup: {result['speedup']:.1f}x")
        
    elif args.dashboard:
        # Run dashboard
        dashboard = MetricsDashboard(collector)
        await dashboard.start()
        
        # Run collector in background
        await collector.run_continuous_monitoring()
        
    else:
        # Run continuous monitoring
        await collector.run_continuous_monitoring()


if __name__ == '__main__':
    asyncio.run(main())
```

#### SubTask 4.1.2: 대시보드 구현
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 4시간

```typescript
// dashboard/src/components/UvMetricsDashboard.tsx
import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, Cell
} from 'recharts';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Activity, HardDrive, Download, Clock, 
  TrendingUp, AlertCircle, CheckCircle 
} from 'lucide-react';

interface MetricData {
  timestamp: string;
  cpu: number;
  memory: number;
  cacheSize: number;
  installTime: number;
  cacheHitRate: number;
}

interface ComparisonData {
  tool: string;
  avgInstallTime: number;
  cacheEfficiency: number;
  resourceUsage: number;
}

const UvMetricsDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<MetricData[]>([]);
  const [comparison, setComparison] = useState<ComparisonData[]>([]);
  const [selectedTimeRange, setSelectedTimeRange] = useState('1h');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch metrics data
  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await fetch(`/api/metrics?range=${selectedTimeRange}`);
        const data = await response.json();
        setMetrics(data.metrics);
        setComparison(data.comparison);
        setIsLoading(false);
      } catch (err) {
        setError('Failed to fetch metrics');
        setIsLoading(false);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000); // Update every 5 seconds

    return () => clearInterval(interval);
  }, [selectedTimeRange]);

  // Calculate statistics
  const stats = metrics.length > 0 ? {
    avgInstallTime: metrics.reduce((sum, m) => sum + m.installTime, 0) / metrics.length,
    avgCacheHitRate: metrics.reduce((sum, m) => sum + m.cacheHitRate, 0) / metrics.length,
    totalCacheSize: metrics[metrics.length - 1]?.cacheSize || 0,
    peakCPU: Math.max(...metrics.map(m => m.cpu)),
    peakMemory: Math.max(...metrics.map(m => m.memory))
  } : null;

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">uv Performance Dashboard</h1>
        <div className="flex gap-2">
          {['1h', '6h', '24h', '7d'].map(range => (
            <button
              key={range}
              onClick={() => setSelectedTimeRange(range)}
              className={`px-4 py-2 rounded ${
                selectedTimeRange === range 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-gray-200'
              }`}
            >
              {range}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <h3 className="text-sm font-medium">Avg Install Time</h3>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats?.avgInstallTime.toFixed(2)}s
            </div>
            <p className="text-xs text-muted-foreground">
              <TrendingUp className="inline h-3 w-3 text-green-500" />
              {' '}85% faster than pip
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <h3 className="text-sm font-medium">Cache Hit Rate</h3>
            <HardDrive className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats?.avgCacheHitRate.toFixed(1)}%
            </div>
            <Badge variant="success">Excellent</Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <h3 className="text-sm font-medium">Cache Size</h3>
            <Download className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {(stats?.totalCacheSize || 0 / 1024).toFixed(1)} GB
            </div>
            <p className="text-xs text-muted-foreground">
              {metrics.length > 1 && 
                `+${((metrics[metrics.length - 1].cacheSize - metrics[0].cacheSize) / 1024).toFixed(1)} GB today`
              }
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <h3 className="text-sm font-medium">Peak CPU</h3>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats?.peakCPU.toFixed(1)}%
            </div>
            <p className="text-xs text-muted-foreground">Last hour</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <h3 className="text-sm font-medium">Peak Memory</h3>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats?.peakMemory.toFixed(1)}%
            </div>
            <p className="text-xs text-muted-foreground">Last hour</p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="performance" className="space-y-4">
        <TabsList>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="comparison">pip vs uv</TabsTrigger>
          <TabsTrigger value="resources">Resources</TabsTrigger>
          <TabsTrigger value="cache">Cache Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="performance" className="space-y-4">
          <Card>
            <CardHeader>
              <h3 className="text-lg font-semibold">Installation Performance</h3>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={metrics}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="timestamp" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="installTime" 
                    stroke="#8884d8" 
                    name="Install Time (s)"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="cacheHitRate" 
                    stroke="#82ca9d" 
                    name="Cache Hit Rate (%)"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="comparison" className="space-y-4">
          <Card>
            <CardHeader>
              <h3 className="text-lg font-semibold">pip vs uv Comparison</h3>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={comparison}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="tool" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="avgInstallTime" fill="#8884d8" name="Avg Install Time (s)" />
                  <Bar dataKey="cacheEfficiency" fill="#82ca9d" name="Cache Efficiency (%)" />
                  <Bar dataKey="resourceUsage" fill="#ffc658" name="Resource Usage (%)" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <h3 className="text-lg font-semibold">Speed Improvement</h3>
              </CardHeader>
              <CardContent>
                <div className="text-center">
                  <div className="text-5xl font-bold text-green-500">12.5x</div>
                  <p className="text-sm text-muted-foreground mt-2">
                    Average speedup compared to pip
                  </p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <h3 className="text-lg font-semibold">Resource Efficiency</h3>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie
                      data={[
                        { name: 'uv CPU', value: 15 },
                        { name: 'pip CPU', value: 45 },
                        { name: 'uv Memory', value: 20 },
                        { name: 'pip Memory', value: 35 }
                      ]}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {comparison.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="resources" className="space-y-4">
          <Card>
            <CardHeader>
              <h3 className="text-lg font-semibold">System Resource Usage</h3>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={metrics}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="timestamp" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="cpu" 
                    stroke="#ff7300" 
                    name="CPU Usage (%)"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="memory" 
                    stroke="#387908" 
                    name="Memory Usage (%)"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="cache" className="space-y-4">
          <Card>
            <CardHeader>
              <h3 className="text-lg font-semibold">Cache Analytics</h3>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={metrics}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="timestamp" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <Tooltip />
                  <Legend />
                  <Line 
                    yAxisId="left"
                    type="monotone" 
                    dataKey="cacheSize" 
                    stroke="#8884d8" 
                    name="Cache Size (MB)"
                  />
                  <Line 
                    yAxisId="right"
                    type="monotone" 
                    dataKey="cacheHitRate" 
                    stroke="#82ca9d" 
                    name="Hit Rate (%)"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Cache Efficiency</span>
                  <CheckCircle className="h-4 w-4 text-green-500" />
                </div>
                <div className="mt-2">
                  <div className="h-2 bg-gray-200 rounded-full">
                    <div 
                      className="h-2 bg-green-500 rounded-full"
                      style={{ width: `${stats?.avgCacheHitRate || 0}%` }}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <p className="text-sm text-muted-foreground">Packages Cached</p>
                  <p className="text-2xl font-bold">1,247</p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <p className="text-sm text-muted-foreground">Cache Savings</p>
                  <p className="text-2xl font-bold">4.2 GB</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default UvMetricsDashboard;
```

```python
# api/metrics_api.py
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import datetime, timedelta
import asyncio
from pydantic import BaseModel

app = FastAPI(title="uv Metrics API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MetricPoint(BaseModel):
    timestamp: str
    cpu: float
    memory: float
    cacheSize: float
    installTime: float
    cacheHitRate: float

class ComparisonData(BaseModel):
    tool: str
    avgInstallTime: float
    cacheEfficiency: float
    resourceUsage: float

class MetricsResponse(BaseModel):
    metrics: List[MetricPoint]
    comparison: List[ComparisonData]

@app.get("/api/metrics", response_model=MetricsResponse)
async def get_metrics(range: str = Query("1h", regex="^(1h|6h|24h|7d)$")):
    """Get metrics for the specified time range"""
    
    # Calculate time range
    now = datetime.now()
    range_map = {
        "1h": timedelta(hours=1),
        "6h": timedelta(hours=6),
        "24h": timedelta(days=1),
        "7d": timedelta(days=7)
    }
    
    start_time = now - range_map[range]
    
    # Fetch metrics from database/collector
    # This is mock data - replace with actual data source
    metrics = []
    for i in range(20):
        timestamp = start_time + timedelta(minutes=i * 3)
        metrics.append(MetricPoint(
            timestamp=timestamp.isoformat(),
            cpu=15 + (i % 5) * 2,
            memory=30 + (i % 3) * 5,
            cacheSize=1024 + i * 50,
            installTime=0.5 + (i % 4) * 0.1,
            cacheHitRate=85 + (i % 3) * 5
        ))
    
    comparison = [
        ComparisonData(
            tool="pip",
            avgInstallTime=6.5,
            cacheEfficiency=45,
            resourceUsage=65
        ),
        ComparisonData(
            tool="uv",
            avgInstallTime=0.5,
            cacheEfficiency=92,
            resourceUsage=25
        )
    ]
    
    return MetricsResponse(metrics=metrics, comparison=comparison)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

#### SubTask 4.1.3: 알림 시스템 구현
**담당자**: 백엔드 개발자  
**예상 소요시간**: 2시간

```python
#!/usr/bin/env python3
# scripts/alerting_system.py

import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertType(Enum):
    PERFORMANCE_DEGRADATION = "performance_degradation"
    HIGH_ERROR_RATE = "high_error_rate"
    CACHE_ISSUE = "cache_issue"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    INSTALLATION_FAILURE = "installation_failure"

@dataclass
class Alert:
    id: str
    type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    timestamp: datetime
    metrics: Dict[str, Any]
    resolved: bool = False
    resolved_at: Optional[datetime] = None

@dataclass
class AlertRule:
    name: str
    type: AlertType
    condition: str
    threshold: float
    duration: timedelta
    severity: AlertSeverity
    
class AlertingSystem:
    """Alert management and notification system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.alerts: Dict[str, Alert] = {}
        self.alert_rules: List[AlertRule] = self._initialize_rules()
        self.logger = logging.getLogger(__name__)
        
    def _initialize_rules(self) -> List[AlertRule]:
        """Initialize default alert rules"""
        return [
            AlertRule(
                name="slow_installation",
                type=AlertType.PERFORMANCE_DEGRADATION,
                condition="avg_install_time > threshold",
                threshold=5.0,  # seconds
                duration=timedelta(minutes=5),
                severity=AlertSeverity.WARNING
            ),
            AlertRule(
                name="high_error_rate",
                type=AlertType.HIGH_ERROR_RATE,
                condition="error_rate > threshold",
                threshold=0.05,  # 5%
                duration=timedelta(minutes=2),
                severity=AlertSeverity.ERROR
            ),
            AlertRule(
                name="low_cache_hit_rate",
                type=AlertType.CACHE_ISSUE,
                condition="cache_hit_rate < threshold",
                threshold=0.7,  # 70%
                duration=timedelta(minutes=10),
                severity=AlertSeverity.WARNING
            ),
            AlertRule(
                name="high_cpu_usage",
                type=AlertType.RESOURCE_EXHAUSTION,
                condition="cpu_usage > threshold",
                threshold=80.0,  # 80%
                duration=timedelta(minutes=5),
                severity=AlertSeverity.WARNING
            ),
            AlertRule(
                name="high_memory_usage",
                type=AlertType.RESOURCE_EXHAUSTION,
                condition="memory_usage > threshold",
                threshold=85.0,  # 85%
                duration=timedelta(minutes=5),
                severity=AlertSeverity.ERROR
            ),
            AlertRule(
                name="installation_failures",
                type=AlertType.INSTALLATION_FAILURE,
                condition="failure_count > threshold",
                threshold=3,  # 3 consecutive failures
                duration=timedelta(minutes=1),
                severity=AlertSeverity.CRITICAL
            )
        ]
    
    async def check_metrics(self, metrics: Dict[str, Any]):
        """Check metrics against alert rules"""
        for rule in self.alert_rules:
            if self._evaluate_rule(rule, metrics):
                await self._trigger_alert(rule, metrics)
            else:
                await self._resolve_alert_if_exists(rule)
    
    def _evaluate_rule(self, rule: AlertRule, metrics: Dict[str, Any]) -> bool:
        """Evaluate if a rule condition is met"""
        try:
            # Simple evaluation - in production, use a proper expression evaluator
            if rule.name == "slow_installation":
                return metrics.get('avg_install_time', 0) > rule.threshold
            elif rule.name == "high_error_rate":
                return metrics.get('error_rate', 0) > rule.threshold
            elif rule.name == "low_cache_hit_rate":
                return metrics.get('cache_hit_rate', 1) < rule.threshold
            elif rule.name == "high_cpu_usage":
                return metrics.get('cpu_usage', 0) > rule.threshold
            elif rule.name == "high_memory_usage":
                return metrics.get('memory_usage', 0) > rule.threshold
            elif rule.name == "installation_failures":
                return metrics.get('failure_count', 0) > rule.threshold
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error evaluating rule {rule.name}: {e}")
            return False
    
    async def _trigger_alert(self, rule: AlertRule, metrics: Dict[str, Any]):
        """Trigger a new alert or update existing one"""
        alert_id = f"{rule.name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Check if similar alert already exists
        existing_alert = self._find_existing_alert(rule)
        if existing_alert and not existing_alert.resolved:
            # Update existing alert
            existing_alert.timestamp = datetime.now()
            existing_alert.metrics = metrics
            return
        
        # Create new alert
        alert = Alert(
            id=alert_id,
            type=rule.type,
            severity=rule.severity,
            title=self._generate_alert_title(rule, metrics),
            message=self._generate_alert_message(rule, metrics),
            timestamp=datetime.now(),
            metrics=metrics
        )
        
        self.alerts[alert_id] = alert
        
        # Send notifications
        await self._send_notifications(alert)
        
    def _find_existing_alert(self, rule: AlertRule) -> Optional[Alert]:
        """Find existing unresolved alert for the same rule"""
        for alert in self.alerts.values():
            if (alert.type == rule.type and 
                not alert.resolved and 
                alert.title.startswith(rule.name)):
                return alert
        return None
    
    async def _resolve_alert_if_exists(self, rule: AlertRule):
        """Resolve alert if condition is no longer met"""
        alert = self._find_existing_alert(rule)
        if alert:
            alert.resolved = True
            alert.resolved_at = datetime.now()
            await self._send_resolution_notification(alert)
    
    def _generate_alert_title(self, rule: AlertRule, metrics: Dict[str, Any]) -> str:
        """Generate alert title"""
        titles = {
            "slow_installation": f"Slow package installation detected ({metrics.get('avg_install_time', 0):.1f}s average)",
            "high_error_rate": f"High error rate detected ({metrics.get('error_rate', 0)*100:.1f}%)",
            "low_cache_hit_rate": f"Low cache hit rate ({metrics.get('cache_hit_rate', 0)*100:.1f}%)",
            "high_cpu_usage": f"High CPU usage ({metrics.get('cpu_usage', 0):.1f}%)",
            "high_memory_usage": f"High memory usage ({metrics.get('memory_usage', 0):.1f}%)",
            "installation_failures": f"Multiple installation failures ({metrics.get('failure_count', 0)} failures)"
        }
        return titles.get(rule.name, f"Alert: {rule.name}")
    
    def _generate_alert_message(self, rule: AlertRule, metrics: Dict[str, Any]) -> str:
        """Generate detailed alert message"""
        messages = {
            "slow_installation": f"""
Package installations are taking longer than expected.
Current average: {metrics.get('avg_install_time', 0):.1f}s
Threshold: {rule.threshold}s
Consider checking network connectivity or cache status.
""",
            "high_error_rate": f"""
Error rate has exceeded acceptable threshold.
Current rate: {metrics.get('error_rate', 0)*100:.1f}%
Threshold: {rule.threshold*100:.1f}%
Recent errors: {metrics.get('recent_errors', [])}
""",
            "low_cache_hit_rate": f"""
Cache hit rate is below optimal level.
Current rate: {metrics.get('cache_hit_rate', 0)*100:.1f}%
Threshold: {rule.threshold*100:.1f}%
This may impact installation performance.
"""
        }
        return messages.get(rule.name, f"Alert condition met: {rule.condition}")
    
    async def _send_notifications(self, alert: Alert):
        """Send alert notifications through configured channels"""
        tasks = []
        
        if self.config.get('slack_webhook'):
            tasks.append(self._send_slack_notification(alert))
        
        if self.config.get('email_enabled'):
            tasks.append(self._send_email_notification(alert))
        
        if self.config.get('webhook_url'):
            tasks.append(self._send_webhook_notification(alert))
        
        if self.config.get('pagerduty_enabled') and alert.severity == AlertSeverity.CRITICAL:
            tasks.append(self._send_pagerduty_notification(alert))
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _send_slack_notification(self, alert: Alert):
        """Send notification to Slack"""
        webhook_url = self.config['slack_webhook']
        
        color_map = {
            AlertSeverity.INFO: "#36a64f",
            AlertSeverity.WARNING: "#ff9800",
            AlertSeverity.ERROR: "#f44336",
            AlertSeverity.CRITICAL: "#d32f2f"
        }
        
        payload = {
            "attachments": [{
                "color": color_map[alert.severity],
                "title": f"{alert.severity.value.upper()}: {alert.title}",
                "text": alert.message,
                "fields": [
                    {
                        "title": "Alert Type",
                        "value": alert.type.value,
                        "short": True
                    },
                    {
                        "title": "Timestamp",
                        "value": alert.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                        "short": True
                    }
                ],
                "footer": "uv Monitoring System",
                "ts": int(alert.timestamp.timestamp())
            }]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=payload) as response:
                if response.status != 200:
                    self.logger.error(f"Failed to send Slack notification: {response.status}")
    
    async def _send_email_notification(self, alert: Alert):
        """Send email notification"""
        if not all(k in self.config for k in ['smtp_host', 'smtp_port', 'email_from', 'email_to']):
            return
        
        msg = MIMEMultipart()
        msg['From'] = self.config['email_from']
        msg['To'] = ', '.join(self.config['email_to'])
        msg['Subject'] = f"[{alert.severity.value.upper()}] {alert.title}"
        
        body = f"""
Alert Details:
--------------
Type: {alert.type.value}
Severity: {alert.severity.value}
Time: {alert.timestamp.strftime("%Y-%m-%d %H:%M:%S")}

Message:
{alert.message}

Metrics:
{json.dumps(alert.metrics, indent=2)}

--
uv Monitoring System
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            with smtplib.SMTP(self.config['smtp_host'], self.config['smtp_port']) as server:
                if self.config.get('smtp_tls'):
                    server.starttls()
                if self.config.get('smtp_user') and self.config.get('smtp_password'):
                    server.login(self.config['smtp_user'], self.config['smtp_password'])
                server.send_message(msg)
        except Exception as e:
            self.logger.error(f"Failed to send email notification: {e}")
    
    async def _send_webhook_notification(self, alert: Alert):
        """Send generic webhook notification"""
        webhook_url = self.config['webhook_url']
        
        payload = {
            "alert_id": alert.id,
            "type": alert.type.value,
            "severity": alert.severity.value,
            "title": alert.title,
            "message": alert.message,
            "timestamp": alert.timestamp.isoformat(),
            "metrics": alert.metrics
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=payload) as response:
                if response.status != 200:
                    self.logger.error(f"Failed to send webhook notification: {response.status}")
    
    async def _send_pagerduty_notification(self, alert: Alert):
        """Send PagerDuty notification for critical alerts"""
        if not self.config.get('pagerduty_routing_key'):
            return
        
        url = "https://events.pagerduty.com/v2/enqueue"
        
        payload = {
            "routing_key": self.config['pagerduty_routing_key'],
            "event_action": "trigger",
            "dedup_key": alert.id,
            "payload": {
                "summary": alert.title,
                "severity": "error",
                "source": "uv-monitoring",
                "custom_details": {
                    "message": alert.message,
                    "metrics": alert.metrics
                }
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status != 202:
                    self.logger.error(f"Failed to send PagerDuty notification: {response.status}")
    
    async def _send_resolution_notification(self, alert: Alert):
        """Send notification when alert is resolved"""
        resolution_message = f"""
Alert Resolved: {alert.title}
Duration: {(alert.resolved_at - alert.timestamp).total_seconds() / 60:.1f} minutes
Resolved at: {alert.resolved_at.strftime("%Y-%m-%d %H:%M:%S")}
"""
        
        # Create a resolution alert
        resolution_alert = Alert(
            id=f"{alert.id}_resolved",
            type=alert.type,
            severity=AlertSeverity.INFO,
            title=f"RESOLVED: {alert.title}",
            message=resolution_message,
            timestamp=alert.resolved_at,
            metrics=alert.metrics,
            resolved=True,
            resolved_at=alert.resolved_at
        )
        
        await self._send_notifications(resolution_alert)
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active (unresolved) alerts"""
        return [alert for alert in self.alerts.values() if not alert.resolved]
    
    def get_alert_history(self, 
                         start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None,
                         severity: Optional[AlertSeverity] = None,
                         alert_type: Optional[AlertType] = None) -> List[Alert]:
        """Get alert history with optional filters"""
        alerts = list(self.alerts.values())
        
        if start_time:
            alerts = [a for a in alerts if a.timestamp >= start_time]
        
        if end_time:
            alerts = [a for a in alerts if a.timestamp <= end_time]
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        if alert_type:
            alerts = [a for a in alerts if a.type == alert_type]
        
        return sorted(alerts, key=lambda a: a.timestamp, reverse=True)
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert statistics"""
        total_alerts = len(self.alerts)
        active_alerts = len(self.get_active_alerts())
        
        severity_counts = {}
        type_counts = {}
        
        for alert in self.alerts.values():
            severity_counts[alert.severity.value] = severity_counts.get(alert.severity.value, 0) + 1
            type_counts[alert.type.value] = type_counts.get(alert.type.value, 0) + 1
        
        # Calculate MTTR (Mean Time To Resolution)
        resolved_alerts = [a for a in self.alerts.values() if a.resolved and a.resolved_at]
        if resolved_alerts:
            total_resolution_time = sum(
                (a.resolved_at - a.timestamp).total_seconds() 
                for a in resolved_alerts
            )
            mttr = total_resolution_time / len(resolved_alerts) / 60  # in minutes
        else:
            mttr = 0
        
        return {
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "resolved_alerts": total_alerts - active_alerts,
            "severity_distribution": severity_counts,
            "type_distribution": type_counts,
            "mean_time_to_resolution_minutes": round(mttr, 2)
        }


# Alert configuration example
ALERT_CONFIG = {
    # Slack
    "slack_webhook": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
    
    # Email
    "email_enabled": True,
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_tls": True,
    "smtp_user": "alerts@example.com",
    "smtp_password": "your-password",
    "email_from": "alerts@example.com",
    "email_to": ["devops@example.com", "oncall@example.com"],
    
    # Generic webhook
    "webhook_url": "https://your-monitoring-system.com/webhooks/alerts",
    
    # PagerDuty
    "pagerduty_enabled": True,
    "pagerduty_routing_key": "YOUR_PAGERDUTY_ROUTING_KEY"
}


# CLI for testing alerts
async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='uv Alert System')
    parser.add_argument('--test', action='store_true', help='Test alert system')
    parser.add_argument('--check-metrics', help='Check metrics from file')
    parser.add_argument('--list-alerts', action='store_true', help='List active alerts')
    parser.add_argument('--stats', action='store_true', help='Show alert statistics')
    
    args = parser.parse_args()
    
    # Initialize alerting system
    alerting = AlertingSystem(ALERT_CONFIG)
    
    if args.test:
        # Test with sample metrics
        test_metrics = {
            "avg_install_time": 7.5,  # Trigger slow installation
            "error_rate": 0.08,       # Trigger high error rate
            "cache_hit_rate": 0.65,   # Trigger low cache hit
            "cpu_usage": 45,
            "memory_usage": 60,
            "failure_count": 1
        }
        
        print("Testing alert system with sample metrics...")
        await alerting.check_metrics(test_metrics)
        
        print("\nActive alerts:")
        for alert in alerting.get_active_alerts():
            print(f"- [{alert.severity.value}] {alert.title}")
        
    elif args.check_metrics:
        # Load metrics from file
        with open(args.check_metrics, 'r') as f:
            metrics = json.load(f)
        
        await alerting.check_metrics(metrics)
        
    elif args.list_alerts:
        # List active alerts
        active_alerts = alerting.get_active_alerts()
        if active_alerts:
            print("Active Alerts:")
            for alert in active_alerts:
                print(f"\nID: {alert.id}")
                print(f"Type: {alert.type.value}")
                print(f"Severity: {alert.severity.value}")
                print(f"Title: {alert.title}")
                print(f"Time: {alert.timestamp}")
        else:
            print("No active alerts")
    
    elif args.stats:
        # Show statistics
        stats = alerting.get_alert_statistics()
        print("Alert Statistics:")
        print(f"Total alerts: {stats['total_alerts']}")
        print(f"Active alerts: {stats['active_alerts']}")
        print(f"Resolved alerts: {stats['resolved_alerts']}")
        print(f"MTTR: {stats['mean_time_to_resolution_minutes']} minutes")
        print("\nSeverity distribution:")
        for severity, count in stats['severity_distribution'].items():
            print(f"  {severity}: {count}")
        print("\nType distribution:")
        for alert_type, count in stats['type_distribution'].items():
            print(f"  {alert_type}: {count}")


if __name__ == '__main__':
    asyncio.run(main())
```

### Task 4.2: 성능 벤치마크 및 최적화

#### SubTask 4.2.1: 벤치마크 스위트 구현
**담당자**: 성능 엔지니어  
**예상 소요시간**: 4시간

```python
#!/usr/bin/env python3
# scripts/benchmark_suite.py

import asyncio
import time
import tempfile
import subprocess
import json
import statistics
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, asdict
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime
import psutil
import numpy as np

@dataclass
class BenchmarkResult:
    tool: str
    operation: str
    duration: float
    cpu_usage: float
    memory_usage: float
    cache_hits: int
    cache_misses: int
    packages_installed: int
    success: bool
    error: Optional[str] = None
    
@dataclass
class BenchmarkScenario:
    name: str
    description: str
    requirements: List[str]
    clean_cache: bool = False
    cold_start: bool = False
    parallel: bool = False
    
class BenchmarkSuite:
    """Comprehensive benchmark suite for pip vs uv"""
    
    def __init__(self, output_dir: str = "./benchmark_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.results: List[BenchmarkResult] = []
        self.scenarios = self._define_scenarios()
        
    def _define_scenarios(self) -> List[BenchmarkScenario]:
        """Define benchmark scenarios"""
        return [
            BenchmarkScenario(
                name="small_project",
                description="Small project with common dependencies",
                requirements=[
                    "requests==2.31.0",
                    "click==8.1.7",
                    "pydantic==2.5.0"
                ]
            ),
            BenchmarkScenario(
                name="medium_project",
                description="Medium project with mixed dependencies",
                requirements=[
                    "fastapi==0.104.1",
                    "sqlalchemy==2.0.23",
                    "pytest==7.4.3",
                    "black==23.11.0",
                    "mypy==1.7.1"
                ]
            ),
            BenchmarkScenario(
                name="large_project",
                description="Large project with many dependencies",
                requirements=[
                    "numpy==1.24.3",
                    "pandas==2.0.3",
                    "scikit-learn==1.3.0",
                    "matplotlib==3.7.2",
                    "jupyter==1.0.0",
                    "tensorflow==2.13.0"
                ]
            ),
            BenchmarkScenario(
                name="cold_cache",
                description="Installation with empty cache",
                requirements=[
                    "django==4.2.7",
                    "celery==5.3.4",
                    "redis==5.0.1"
                ],
                clean_cache=True,
                cold_start=True
            ),
            BenchmarkScenario(
                name="warm_cache",
                description="Installation with populated cache",
                requirements=[
                    "django==4.2.7",
                    "celery==5.3.4",
                    "redis==5.0.1"
                ],
                clean_cache=False
            ),
            BenchmarkScenario(
                name="parallel_install",
                description="Parallel installation test",
                requirements=[
                    "aiohttp==3.9.0",
                    "httpx==0.25.1",
                    "requests==2.31.0",
                    "urllib3==2.1.0"
                ],
                parallel=True
            ),
            BenchmarkScenario(
                name="complex_deps",
                description="Complex dependency resolution",
                requirements=[
                    "apache-airflow==2.7.3",
                    "dask==2023.11.0",
                    "ray==2.8.0"
                ]
            )
        ]
    
    async def run_benchmark(self, tool: str, scenario: BenchmarkScenario) -> BenchmarkResult:
        """Run a single benchmark"""
        # Create temporary directory for isolated environment
        with tempfile.TemporaryDirectory() as tmpdir:
            venv_path = Path(tmpdir) / "venv"
            
            # Clean cache if requested
            if scenario.clean_cache:
                self._clean_cache(tool)
            
            # Create virtual environment
            if tool == "uv":
                await self._run_command(["uv", "venv", str(venv_path)])
                pip_cmd = [str(venv_path / "bin" / "pip")]
                install_cmd = ["uv", "pip", "install", "--python", str(venv_path / "bin" / "python")]
            else:
                await self._run_command(["python", "-m", "venv", str(venv_path)])
                pip_cmd = [str(venv_path / "bin" / "pip")]
                install_cmd = pip_cmd + ["install"]
            
            # Create requirements file
            req_file = Path(tmpdir) / "requirements.txt"
            req_file.write_text("\n".join(scenario.requirements))
            
            # Measure installation
            start_time = time.time()
            process_start = psutil.Process()
            
            try:
                # Run installation
                if scenario.parallel and tool == "uv":
                    # uv supports parallel downloads by default
                    result = await self._run_command(
                        install_cmd + ["-r", str(req_file)],
                        capture_output=True
                    )
                else:
                    result = await self._run_command(
                        install_cmd + ["-r", str(req_file)],
                        capture_output=True
                    )
                
                duration = time.time() - start_time
                
                # Collect metrics
                cpu_percent = process_start.cpu_percent()
                memory_info = process_start.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                
                # Parse output for cache statistics (uv specific)
                cache_hits = 0
                cache_misses = 0
                if tool == "uv" and result.stdout:
                    cache_hits, cache_misses = self._parse_cache_stats(result.stdout)
                
                # Count installed packages
                list_result = await self._run_command(
                    pip_cmd + ["list", "--format=json"],
                    capture_output=True
                )
                packages = json.loads(list_result.stdout) if list_result.stdout else []
                
                return BenchmarkResult(
                    tool=tool,
                    operation=scenario.name,
                    duration=duration,
                    cpu_usage=cpu_percent,
                    memory_usage=memory_mb,
                    cache_hits=cache_hits,
                    cache_misses=cache_misses,
                    packages_installed=len(packages),
                    success=True
                )
                
            except Exception as e:
                return BenchmarkResult(
                    tool=tool,
                    operation=scenario.name,
                    duration=time.time() - start_time,
                    cpu_usage=0,
                    memory_usage=0,
                    cache_hits=0,
                    cache_misses=0,
                    packages_installed=0,
                    success=False,
                    error=str(e)
                )
    
    async def _run_command(self, cmd: List[str], capture_output: bool = False):
        """Run a command asynchronously"""
        if capture_output:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            return type('Result', (), {
                'stdout': stdout.decode() if stdout else '',
                'stderr': stderr.decode() if stderr else '',
                'returncode': process.returncode
            })()
        else:
            process = await asyncio.create_subprocess_exec(*cmd)
            await process.wait()
            return type('Result', (), {'returncode': process.returncode})()
    
    def _clean_cache(self, tool: str):
        """Clean tool cache"""
        if tool == "uv":
            cache_dir = Path.home() / ".cache" / "uv"
        else:
            cache_dir = Path.home() / ".cache" / "pip"
        
        if cache_dir.exists():
            import shutil
            shutil.rmtree(cache_dir)
    
    def _parse_cache_stats(self, output: str) -> Tuple[int, int]:
        """Parse cache statistics from uv output"""
        # This would need to be implemented based on actual uv output
        # For now, return mock data
        import re
        
        hits = len(re.findall(r'Using cached', output))
        misses = len(re.findall(r'Downloading', output))
        
        return hits, misses
    
    async def run_all_benchmarks(self, iterations: int = 3):
        """Run all benchmark scenarios"""
        print(f"Running benchmark suite with {iterations} iterations per scenario...")
        
        for scenario in self.scenarios:
            print(f"\n📊 Scenario: {scenario.name}")
            print(f"   {scenario.description}")
            
            for tool in ["pip", "uv"]:
                tool_results = []
                
                for i in range(iterations):
                    print(f"   Running {tool} iteration {i+1}/{iterations}...")
                    result = await self.run_benchmark(tool, scenario)
                    tool_results.append(result)
                    self.results.append(result)
                    
                    if not result.success:
                        print(f"   ⚠️  Failed: {result.error}")
                
                # Print summary for this tool/scenario
                if tool_results:
                    successful_results = [r for r in tool_results if r.success]
                    if successful_results:
                        avg_duration = statistics.mean(r.duration for r in successful_results)
                        print(f"   {tool}: {avg_duration:.2f}s average")
    
    def analyze_results(self) -> Dict[str, Any]:
        """Analyze benchmark results"""
        if not self.results:
            return {}
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame([asdict(r) for r in self.results])
        
        analysis = {
            "summary": {},
            "by_scenario": {},
            "speedup": {}
        }
        
        # Overall summary
        for tool in ["pip", "uv"]:
            tool_df = df[(df['tool'] == tool) & (df['success'] == True)]
            if not tool_df.empty:
                analysis["summary"][tool] = {
                    "avg_duration": tool_df['duration'].mean(),
                    "median_duration": tool_df['duration'].median(),
                    "std_duration": tool_df['duration'].std(),
                    "min_duration": tool_df['duration'].min(),
                    "max_duration": tool_df['duration'].max(),
                    "avg_cpu": tool_df['cpu_usage'].mean(),
                    "avg_memory": tool_df['memory_usage'].mean(),
                    "success_rate": len(tool_df) / len(df[df['tool'] == tool]) * 100
                }
        
        # Analysis by scenario
        for scenario in df['operation'].unique():
            scenario_df = df[df['operation'] == scenario]
            analysis["by_scenario"][scenario] = {}
            
            for tool in ["pip", "uv"]:
                tool_scenario_df = scenario_df[(scenario_df['tool'] == tool) & (scenario_df['success'] == True)]
                if not tool_scenario_df.empty:
                    analysis["by_scenario"][scenario][tool] = {
                        "avg_duration": tool_scenario_df['duration'].mean(),
                        "avg_cpu": tool_scenario_df['cpu_usage'].mean(),
                        "avg_memory": tool_scenario_df['memory_usage'].mean()
                    }
            
            # Calculate speedup
            if "pip" in analysis["by_scenario"][scenario] and "uv" in analysis["by_scenario"][scenario]:
                pip_time = analysis["by_scenario"][scenario]["pip"]["avg_duration"]
                uv_time = analysis["by_scenario"][scenario]["uv"]["avg_duration"]
                if uv_time > 0:
                    analysis["speedup"][scenario] = pip_time / uv_time
        
        return analysis
    
    def generate_report(self):
        """Generate comprehensive benchmark report"""
        analysis = self.analyze_results()
        
        if not analysis:
            print("No results to analyze")
            return
        
        # Create report
        report_path = self.output_dir / f"benchmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(report_path, 'w') as f:
            f.write("# uv vs pip Benchmark Report\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Summary
            f.write("## Executive Summary\n\n")
            
            if "pip" in analysis["summary"] and "uv" in analysis["summary"]:
                pip_avg = analysis["summary"]["pip"]["avg_duration"]
                uv_avg = analysis["summary"]["uv"]["avg_duration"]
                overall_speedup = pip_avg / uv_avg if uv_avg > 0 else 0
                
                f.write(f"- **Overall speedup**: {overall_speedup:.1f}x\n")
                f.write(f"- **pip average**: {pip_avg:.2f}s\n")
                f.write(f"- **uv average**: {uv_avg:.2f}s\n")
                f.write(f"- **Time saved**: {pip_avg - uv_avg:.2f}s ({(1 - uv_avg/pip_avg)*100:.1f}%)\n\n")
            
            # Detailed results by scenario
            f.write("## Results by Scenario\n\n")
            
            for scenario, data in analysis["by_scenario"].items():
                f.write(f"### {scenario}\n\n")
                
                if "pip" in data and "uv" in data:
                    speedup = analysis["speedup"].get(scenario, 0)
                    f.write(f"**Speedup: {speedup:.1f}x**\n\n")
                    
                    f.write("| Metric | pip | uv | Improvement |\n")
                    f.write("|--------|-----|----|--------------|\n")
                    f.write(f"| Duration | {data['pip']['avg_duration']:.2f}s | {data['uv']['avg_duration']:.2f}s | {speedup:.1f}x |\n")
                    f.write(f"| CPU Usage | {data['pip']['avg_cpu']:.1f}% | {data['uv']['avg_cpu']:.1f}% | {(data['pip']['avg_cpu'] - data['uv']['avg_cpu']) / data['pip']['avg_cpu'] * 100:.1f}% |\n")
                    f.write(f"| Memory | {data['pip']['avg_memory']:.1f}MB | {data['uv']['avg_memory']:.1f}MB | {(data['pip']['avg_memory'] - data['uv']['avg_memory']) / data['pip']['avg_memory'] * 100:.1f}% |\n\n")
            
            # Recommendations
            f.write("## Recommendations\n\n")
            f.write("Based on the benchmark results:\n\n")
            
            if overall_speedup > 5:
                f.write("1. **Strongly recommend** switching to uv for all environments\n")
            elif overall_speedup > 2:
                f.write("1. **Recommend** switching to uv, especially for CI/CD pipelines\n")
            else:
                f.write("1. Consider switching to uv for improved performance\n")
            
            f.write("2. uv shows the most improvement in scenarios with:\n")
            
            # Find scenarios with best improvement
            sorted_speedups = sorted(analysis["speedup"].items(), key=lambda x: x[1], reverse=True)
            for scenario, speedup in sorted_speedups[:3]:
                f.write(f"   - {scenario}: {speedup:.1f}x faster\n")
        
        print(f"\n📄 Report generated: {report_path}")
        
        # Generate visualizations
        self._generate_visualizations(analysis)
    
    def _generate_visualizations(self, analysis: Dict[str, Any]):
        """Generate benchmark visualizations"""
        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('uv vs pip Benchmark Results', fontsize=16)
        
        # 1. Overall comparison bar chart
        ax1 = axes[0, 0]
        tools = ['pip', 'uv']
        durations = [
            analysis["summary"].get(tool, {}).get("avg_duration", 0) 
            for tool in tools
        ]
        bars = ax1.bar(tools, durations, color=['#FF6B6B', '#4ECDC4'])
        ax1.set_ylabel('Average Duration (seconds)')
        ax1.set_title('Overall Performance Comparison')
        
        # Add value labels
        for bar, duration in zip(bars, durations):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    f'{duration:.1f}s', ha='center', va='bottom')
        
        # 2. Speedup by scenario
        ax2 = axes[0, 1]
        scenarios = list(analysis["speedup"].keys())
        speedups = list(analysis["speedup"].values())
        
        bars = ax2.barh(scenarios, speedups, color='#95E1D3')
        ax2.set_xlabel('Speedup Factor')
        ax2.set_title('Speedup by Scenario')
        ax2.axvline(x=1, color='red', linestyle='--', alpha=0.5)
        
        # Add value labels
        for bar, speedup in zip(bars, speedups):
            ax2.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                    f'{speedup:.1f}x', ha='left', va='center')
        
        # 3. Resource usage comparison
        ax3 = axes[1, 0]
        df = pd.DataFrame([asdict(r) for r in self.results if r.success])
        
        if not df.empty:
            resource_data = df.groupby('tool')[['cpu_usage', 'memory_usage']].mean()
            resource_data.plot(kind='bar', ax=ax3, rot=0)
            ax3.set_ylabel('Usage')
            ax3.set_title('Average Resource Usage')
            ax3.legend(['CPU (%)', 'Memory (MB)'])
        
        # 4. Duration distribution
        ax4 = axes[1, 1]
        if not df.empty:
            pip_durations = df[df['tool'] == 'pip']['duration']
            uv_durations = df[df['tool'] == 'uv']['duration']
            
            ax4.hist([pip_durations, uv_durations], label=['pip', 'uv'], 
                    bins=15, alpha=0.7, color=['#FF6B6B', '#4ECDC4'])
            ax4.set_xlabel('Duration (seconds)')
            ax4.set_ylabel('Frequency')
            ax4.set_title('Duration Distribution')
            ax4.legend()
        
        plt.tight_layout()
        
        # Save figure
        plot_path = self.output_dir / f"benchmark_plots_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 Visualizations saved: {plot_path}")
    
    def export_results(self, format: str = "json"):
        """Export results in various formats"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == "json":
            output_file = self.output_dir / f"benchmark_results_{timestamp}.json"
            with open(output_file, 'w') as f:
                json.dump(
                    [asdict(r) for r in self.results],
                    f,
                    indent=2,
                    default=str
                )
        
        elif format == "csv":
            output_file = self.output_dir / f"benchmark_results_{timestamp}.csv"
            df = pd.DataFrame([asdict(r) for r in self.results])
            df.to_csv(output_file, index=False)
        
        print(f"💾 Results exported: {output_file}")


async def main():
    """Run benchmark suite"""
    import argparse
    
    parser = argparse.ArgumentParser(description='uv vs pip benchmark suite')
    parser.add_argument('--iterations', type=int, default=3, 
                       help='Number of iterations per scenario')
    parser.add_argument('--scenarios', nargs='+', 
                       help='Specific scenarios to run')
    parser.add_argument('--output-dir', default='./benchmark_results',
                       help='Output directory for results')
    parser.add_argument('--quick', action='store_true',
                       help='Run quick benchmark with fewer scenarios')
    
    args = parser.parse_args()
    
    # Create benchmark suite
    suite = BenchmarkSuite(output_dir=args.output_dir)
    
    # Filter scenarios if specified
    if args.scenarios:
        suite.scenarios = [s for s in suite.scenarios if s.name in args.scenarios]
    elif args.quick:
        # Quick mode - only run small and medium scenarios
        suite.scenarios = [s for s in suite.scenarios if s.name in ['small_project', 'medium_project']]
    
    # Run benchmarks
    await suite.run_all_benchmarks(iterations=args.iterations)
    
    # Generate report and visualizations
    suite.generate_report()
    
    # Export results
    suite.export_results("json")
    suite.export_results("csv")
    
    print("\n✅ Benchmark suite completed!")


if __name__ == '__main__':
    asyncio.run(main())
```

#### SubTask 4.2.2: 최적화 가이드라인
**담당자**: 성능 엔지니어  
**예상 소요시간**: 2시간

```markdown
# uv Performance Optimization Guide

## 📊 Performance Optimization Best Practices

### 1. Cache Optimization

#### Enable Persistent Cache
```bash
# Set cache directory (default: ~/.cache/uv)
export UV_CACHE_DIR=/path/to/fast/ssd/cache

# Increase cache size limit
export UV_CACHE_SIZE=10GB
```

#### Pre-warm Cache
```python
#!/usr/bin/env python3
# scripts/prewarm_cache.py

import subprocess
import asyncio
from pathlib import Path

async def prewarm_cache(requirements_file: str):
    """Pre-download packages to warm uv cache"""
    
    # Read requirements
    requirements = Path(requirements_file).read_text().splitlines()
    
    # Download without installing
    for req in requirements:
        if req and not req.startswith('#'):
            print(f"Pre-warming cache for: {req}")
            process = await asyncio.create_subprocess_exec(
                'uv', 'pip', 'download', '--no-deps', req,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()

# Usage
asyncio.run(prewarm_cache('requirements.txt'))
```

### 2. Network Optimization

#### Use Local Package Index
```bash
# Configure local PyPI mirror
export UV_INDEX_URL=https://pypi.company.internal/simple/

# Use multiple indexes
export UV_EXTRA_INDEX_URL=https://pypi.org/simple/
```

#### Parallel Downloads
```toml
# pyproject.toml
[tool.uv]
parallel-downloads = 10  # Increase for faster networks
connection-timeout = 30  # Adjust based on network latency
```

### 3. Dependency Resolution

#### Lock Dependencies
```bash
# Generate locked requirements
uv pip compile requirements.in -o requirements.lock

# Install from locked file (faster)
uv pip sync requirements.lock
```

#### Minimize Dependency Tree
```python
# analyze_dependencies.py
import subprocess
import json

def analyze_dependency_tree():
    """Analyze and optimize dependency tree"""
    
    # Get dependency tree
    result = subprocess.run(
        ['uv', 'pip', 'tree', '--json'],
        capture_output=True,
        text=True
    )
    
    tree = json.loads(result.stdout)
    
    # Find duplicate dependencies
    packages = {}
    for pkg in tree['packages']:
        name = pkg['name']
        if name in packages:
            packages[name].append(pkg['version'])
        else:
            packages[name] = [pkg['version']]
    
    # Report duplicates
    duplicates = {k: v for k, v in packages.items() if len(set(v)) > 1}
    
    if duplicates:
        print("⚠️  Duplicate packages with different versions:")
        for pkg, versions in duplicates.items():
            print(f"  {pkg}: {', '.join(set(versions))}")
```

### 4. CI/CD Optimization

#### GitHub Actions
```yaml
name: Optimized CI with uv

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Install uv
      run: |
        curl -LsSf https://astral.sh/uv/install.sh | sh
        echo "$HOME/.cargo/bin" >> $GITHUB_PATH
    
    - name: Cache uv
      uses: actions/cache@v3
      with:
        path: |
          ~/.cache/uv
          .venv
        key: ${{ runner.os }}-uv-${{ hashFiles('**/requirements*.txt') }}
        restore-keys: |
          ${{ runner.os }}-uv-
    
    - name: Install dependencies
      run: |
        uv venv
        source .venv/bin/activate
        uv pip sync requirements.lock  # Use locked deps
```

#### Docker Optimization
```dockerfile
# Multi-stage build with cache mount
FROM python:3.11-slim as builder

RUN pip install uv

# Cache mount for uv
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    uv pip install --prefix=/install -r requirements.txt

FROM python:3.11-slim
COPY --from=builder /install /usr/local
```

### 5. Development Workflow

#### Fast Reinstalls
```bash
# Use --reinstall-package for specific packages
uv pip install --reinstall-package mypackage

# Use --force-reinstall sparingly
uv pip install --force-reinstall -r requirements.txt
```

#### Editable Installs
```bash
# Fast editable installs for development
uv pip install -e ./my-package
uv pip install -e git+https://github.com/user/repo.git#egg=package
```

### 6. Monitoring and Profiling

#### Profile Installation
```python
# profile_install.py
import cProfile
import pstats
import subprocess

def profile_installation():
    """Profile uv installation performance"""
    
    profiler = cProfile.Profile()
    profiler.enable()
    
    subprocess.run(['uv', 'pip', 'install', '-r', 'requirements.txt'])
    
    profiler.disable()
    
    # Analyze results
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 functions
```

#### Monitor Cache Performance
```bash
# Check cache statistics
uv cache stats

# Clean cache selectively
uv cache clean --package requests
uv cache clean --all  # Full clean
```

### 7. Platform-Specific Optimizations

#### Linux
```bash
# Use faster filesystem for cache
mount -t tmpfs -o size=5G tmpfs /tmp/uv-cache
export UV_CACHE_DIR=/tmp/uv-cache

# Increase file descriptors
ulimit -n 4096
```

#### macOS
```bash
# Disable Spotlight indexing for cache
sudo mdutil -i off ~/.cache/uv

# Use APFS features
# Cache is automatically optimized on APFS
```

#### Windows
```powershell
# Use faster drive for cache
$env:UV_CACHE_DIR = "D:\uv-cache"

# Disable Windows Defender for cache folder
Add-MpPreference -ExclusionPath "$env:UV_CACHE_DIR"
```

### 8. Common Performance Issues

#### Issue: Slow Resolution
```bash
# Solution: Use stricter version constraints
# Bad:  package>=1.0
# Good: package>=1.0,<2.0

# Use == for known good versions
package==1.2.3
```

#### Issue: Large Docker Images
```dockerfile
# Solution: Multi-stage builds
FROM python:3.11-slim as builder
# ... build stage ...

FROM python:3.11-slim
# Copy only necessary files
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
```

#### Issue: Redundant Installations
```bash
# Solution: Use workspace installations
uv pip install -e .[dev,test,docs]  # Install all extras at once
```

### 9. Benchmarking Your Setup

```python
#!/usr/bin/env python3
# benchmark_my_setup.py

import time
import subprocess
import statistics

def benchmark_command(cmd, runs=5):
    """Benchmark a command multiple times"""
    times = []
    
    for i in range(runs):
        start = time.time()
        subprocess.run(cmd, shell=True, capture_output=True)
        duration = time.time() - start
        times.append(duration)
        print(f"Run {i+1}: {duration:.2f}s")
    
    print(f"\nAverage: {statistics.mean(times):.2f}s")
    print(f"Median: {statistics.median(times):.2f}s")
    print(f"Std Dev: {statistics.stdev(times):.2f}s")

# Benchmark your requirements
benchmark_command("uv pip install -r requirements.txt --dry-run")
```

### 10. Optimization Checklist

- [ ] **Cache Configuration**
  - [ ] Cache on SSD
  - [ ] Adequate cache size
  - [ ] Persistent cache location

- [ ] **Network Setup**
  - [ ] Local PyPI mirror configured
  - [ ] Appropriate timeout settings
  - [ ] Parallel downloads enabled

- [ ] **Dependencies**
  - [ ] Requirements are locked
  - [ ] No duplicate packages
  - [ ] Minimal dependency tree

- [ ] **CI/CD Pipeline**
  - [ ] Cache properly configured
  - [ ] Using locked dependencies
  - [ ] Multi-stage Docker builds

- [ ] **Development Environment**
  - [ ] Fast filesystem for cache
  - [ ] Antivirus exclusions set
  - [ ] File descriptor limits increased

## 📈 Expected Performance Gains

| Optimization | Typical Improvement | Impact |
|--------------|-------------------|---------|
| Cache on SSD | 2-3x faster | High |
| Locked dependencies | 1.5-2x faster | High |
| Local PyPI mirror | 3-5x faster | High |
| Parallel downloads | 1.5-2x faster | Medium |
| Pre-warmed cache | 10-20x faster | High |
| Docker cache mounts | 2-4x faster | High |

## 🚀 Advanced Optimizations

### Custom Index Server
```python
# Run a local caching proxy
from flask import Flask, request, redirect
import requests

app = Flask(__name__)

@app.route('/<path:package>')
def proxy_package(package):
    """Simple caching proxy for PyPI"""
    # Implementation details...
    pass
```

### Distributed Cache
```yaml
# Share cache across team using Redis
version: '3'
services:
  uv-cache:
    image: redis:alpine
    volumes:
      - uv-cache-data:/data
    ports:
      - "6379:6379"
```

Remember: Always measure before and after optimizations to ensure they provide real benefits in your specific environment.
```

#### SubTask 4.2.3: 성능 모니터링 자동화
**담당자**: 자동화 엔지니어  
**예상 소요시간**: 2시간

```python
#!/usr/bin/env python3
# scripts/performance_monitor.py

import asyncio
import time
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import aiohttp
import schedule
from dataclasses import dataclass, asdict
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import pandas as pd

@dataclass
class PerformanceMetric:
    timestamp: datetime
    operation: str
    tool: str
    duration: float
    packages_count: int
    cache_hit_rate: float
    error_rate: float
    
class PerformanceMonitor:
    """Automated performance monitoring for uv"""
    
    def __init__(self, db_path: str = "performance_metrics.db"):
        self.db_path = db_path
        self._init_database()
        self.alert_thresholds = {
            'duration': 10.0,  # seconds
            'error_rate': 0.05,  # 5%
            'cache_hit_rate': 0.7  # 70%
        }
        
    def _init_database(self):
        """Initialize SQLite database for metrics storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                operation TEXT,
                tool TEXT,
                duration REAL,
                packages_count INTEGER,
                cache_hit_rate REAL,
                error_rate REAL
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON performance_metrics(timestamp)
        ''')
        
        conn.commit()
        conn.close()
    
    async def monitor_installation(self, requirements_file: str) -> PerformanceMetric:
        """Monitor a single installation operation"""
        start_time = time.time()
        cache_hits = 0
        cache_total = 0
        errors = 0
        
        # Create temporary venv
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            venv_path = Path(tmpdir) / "venv"
            
            # Run installation
            process = await asyncio.create_subprocess_exec(
                'uv', 'venv', str(venv_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            
            # Install packages
            process = await asyncio.create_subprocess_exec(
                'uv', 'pip', 'install', '-r', requirements_file,
                '--python', str(venv_path / 'bin' / 'python'),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            duration = time.time() - start_time
            
            # Parse output for metrics
            output = stdout.decode() + stderr.decode()
            
            # Count cache hits (this is simplified - real implementation would parse actual output)
            cache_hits = output.count('Using cached')
            cache_total = output.count('Downloading') + cache_hits
            cache_hit_rate = cache_hits / cache_total if cache_total > 0 else 0
            
            # Check for errors
            error_rate = 1.0 if process.returncode != 0 else 0.0
            
            # Count installed packages
            list_process = await asyncio.create_subprocess_exec(
                str(venv_path / 'bin' / 'pip'), 'list', '--format=json',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            list_stdout, _ = await list_process.communicate()
            
            try:
                packages = json.loads(list_stdout.decode())
                packages_count = len(packages)
            except:
                packages_count = 0
        
        metric = PerformanceMetric(
            timestamp=datetime.now(),
            operation='install',
            tool='uv',
            duration=duration,
            packages_count=packages_count,
            cache_hit_rate=cache_hit_rate,
            error_rate=error_rate
        )
        
        # Store in database
        self._store_metric(metric)
        
        # Check for alerts
        self._check_alerts(metric)
        
        return metric
    
    def _store_metric(self, metric: PerformanceMetric):
        """Store metric in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO performance_metrics 
            (timestamp, operation, tool, duration, packages_count, cache_hit_rate, error_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            metric.timestamp,
            metric.operation,
            metric.tool,
            metric.duration,
            metric.packages_count,
            metric.cache_hit_rate,
            metric.error_rate
        ))
        
        conn.commit()
        conn.close()
    
    def _check_alerts(self, metric: PerformanceMetric):
        """Check if metric triggers any alerts"""
        alerts = []
        
        if metric.duration > self.alert_thresholds['duration']:
            alerts.append(f"High duration: {metric.duration:.1f}s (threshold: {self.alert_thresholds['duration']}s)")
        
        if metric.error_rate > self.alert_thresholds['error_rate']:
            alerts.append(f"High error rate: {metric.error_rate*100:.1f}% (threshold: {self.alert_thresholds['error_rate']*100}%)")
        
        if metric.cache_hit_rate < self.alert_thresholds['cache_hit_rate']:
            alerts.append(f"Low cache hit rate: {metric.cache_hit_rate*100:.1f}% (threshold: {self.alert_thresholds['cache_hit_rate']*100}%)")
        
        if alerts:
            self._send_alerts(alerts, metric)
    
    def _send_alerts(self, alerts: List[str], metric: PerformanceMetric):
        """Send alerts (implement your notification logic here)"""
        print(f"\n⚠️  PERFORMANCE ALERTS at {metric.timestamp}:")
        for alert in alerts:
            print(f"  - {alert}")
    
    def get_metrics(self, 
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None,
                   operation: Optional[str] = None) -> pd.DataFrame:
        """Retrieve metrics from database"""
        conn = sqlite3.connect(self.db_path)
        
        query = "SELECT * FROM performance_metrics WHERE 1=1"
        params = []
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time)
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time)
        
        if operation:
            query += " AND operation = ?"
            params.append(operation)
        
        query += " ORDER BY timestamp"
        
        df = pd.read_sql_query(query, conn, params=params)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        conn.close()
        return df
    
    def generate_report(self, period_days: int = 7):
        """Generate performance report for the specified period"""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=period_days)
        
        df = self.get_metrics(start_time=start_time, end_time=end_time)
        
        if df.empty:
            print("No metrics found for the specified period")
            return
        
        # Calculate statistics
        stats = {
            'total_operations': len(df),
            'avg_duration': df['duration'].mean(),
            'median_duration': df['duration'].median(),
            'max_duration': df['duration'].max(),
            'min_duration': df['duration'].min(),
            'avg_cache_hit_rate': df['cache_hit_rate'].mean(),
            'error_rate': df['error_rate'].mean(),
            'total_packages_installed': df['packages_count'].sum()
        }
        
        # Generate plots
        self._generate_plots(df, period_days)
        
        # Print report
        print(f"\n📊 Performance Report ({period_days} days)")
        print("=" * 50)
        print(f"Total operations: {stats['total_operations']}")
        print(f"Average duration: {stats['avg_duration']:.2f}s")
        print(f"Median duration: {stats['median_duration']:.2f}s")
        print(f"Duration range: {stats['min_duration']:.2f}s - {stats['max_duration']:.2f}s")
        print(f"Average cache hit rate: {stats['avg_cache_hit_rate']*100:.1f}%")
        print(f"Error rate: {stats['error_rate']*100:.2f}%")
        print(f"Total packages installed: {stats['total_packages_installed']}")
        
        # Identify trends
        self._analyze_trends(df)
        
        return stats
    
    def _generate_plots(self, df: pd.DataFrame, period_days: int):
        """Generate performance plots"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'uv Performance Metrics ({period_days} days)', fontsize=16)
        
        # 1. Duration over time
        ax1 = axes[0, 0]
        df.plot(x='timestamp', y='duration', ax=ax1, marker='o', markersize=4)
        ax1.set_ylabel('Duration (seconds)')
        ax1.set_title('Installation Duration Over Time')
        ax1.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
        
        # Add rolling average
        window = min(10, len(df) // 3)
        if window > 1:
            df['duration_ma'] = df['duration'].rolling(window=window).mean()
            df.plot(x='timestamp', y='duration_ma', ax=ax1, color='red', 
                   label=f'{window}-point Moving Average')
        
        # 2. Cache hit rate
        ax2 = axes[0, 1]
        df.plot(x='timestamp', y='cache_hit_rate', ax=ax2, marker='s', markersize=4)
        ax2.set_ylabel('Cache Hit Rate')
        ax2.set_ylim(0, 1.1)
        ax2.set_title('Cache Hit Rate Over Time')
        ax2.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
        
        # Add threshold line
        ax2.axhline(y=self.alert_thresholds['cache_hit_rate'], 
                   color='red', linestyle='--', alpha=0.5, 
                   label=f"Threshold ({self.alert_thresholds['cache_hit_rate']*100}%)")
        
        # 3. Duration distribution
        ax3 = axes[1, 0]
        df['duration'].hist(ax=ax3, bins=20, edgecolor='black')
        ax3.set_xlabel('Duration (seconds)')
        ax3.set_ylabel('Frequency')
        ax3.set_title('Duration Distribution')
        ax3.axvline(x=df['duration'].mean(), color='red', linestyle='--', 
                   label=f'Mean: {df["duration"].mean():.1f}s')
        ax3.legend()
        
        # 4. Daily aggregates
        ax4 = axes[1, 1]
        daily = df.resample('D', on='timestamp').agg({
            'duration': 'mean',
            'cache_hit_rate': 'mean',
            'error_rate': 'mean'
        })
        
        if not daily.empty:
            daily['duration'].plot(ax=ax4, kind='bar')
            ax4.set_ylabel('Average Duration (seconds)')
            ax4.set_title('Daily Average Duration')
            ax4.set_xticklabels([d.strftime('%Y-%m-%d') for d in daily.index], rotation=45)
        
        plt.tight_layout()
        
        # Save plot
        plot_path = f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"\n📈 Plots saved to: {plot_path}")
    
    def _analyze_trends(self, df: pd.DataFrame):
        """Analyze performance trends"""
        print("\n🔍 Trend Analysis:")
        
        # Check for performance degradation
        if len(df) > 10:
            first_half = df.iloc[:len(df)//2]['duration'].mean()
            second_half = df.iloc[len(df)//2:]['duration'].mean()
            
            change = (second_half - first_half) / first_half * 100
            
            if abs(change) > 10:
                trend = "degrading" if change > 0 else "improving"
                print(f"  - Performance is {trend}: {abs(change):.1f}% change")
        
        # Check cache effectiveness
        recent_cache_rate = df.tail(10)['cache_hit_rate'].mean()
        if recent_cache_rate < 0.8:
            print(f"  - Cache hit rate could be improved: {recent_cache_rate*100:.1f}%")
        
        # Check for patterns
        hourly = df.set_index('timestamp').resample('H')['duration'].mean()
        if len(hourly) > 24:
            peak_hour = hourly.idxmax()
            print(f"  - Peak usage hour: {peak_hour.hour}:00")


class ContinuousMonitor:
    """Continuous monitoring service"""
    
    def __init__(self, monitor: PerformanceMonitor, requirements_file: str):
        self.monitor = monitor
        self.requirements_file = requirements_file
        self.is_running = False
        
    async def start(self, interval_minutes: int = 30):
        """Start continuous monitoring"""
        self.is_running = True
        print(f"🚀 Starting continuous monitoring (every {interval_minutes} minutes)")
        
        while self.is_running:
            try:
                # Run monitoring
                metric = await self.monitor.monitor_installation(self.requirements_file)
                
                print(f"\n✅ Monitoring completed at {metric.timestamp}")
                print(f"   Duration: {metric.duration:.2f}s")
                print(f"   Cache hit rate: {metric.cache_hit_rate*100:.1f}%")
                print(f"   Packages: {metric.packages_count}")
                
            except Exception as e:
                print(f"\n❌ Monitoring failed: {e}")
            
            # Wait for next iteration
            await asyncio.sleep(interval_minutes * 60)
    
    def stop(self):
        """Stop monitoring"""
        self.is_running = False
        print("\n🛑 Monitoring stopped")


async def main():
    """Main function for performance monitoring"""
    import argparse
    
    parser = argparse.ArgumentParser(description='uv performance monitor')
    parser.add_argument('requirements', help='Requirements file to monitor')
    parser.add_argument('--continuous', action='store_true', 
                       help='Run continuous monitoring')
    parser.add_argument('--interval', type=int, default=30,
                       help='Monitoring interval in minutes')
    parser.add_argument('--report', action='store_true',
                       help='Generate performance report')
    parser.add_argument('--days', type=int, default=7,
                       help='Number of days for report')
    
    args = parser.parse_args()
    
    # Initialize monitor
    monitor = PerformanceMonitor()
    
    if args.report:
        # Generate report
        monitor.generate_report(period_days=args.days)
        
    elif args.continuous:
        # Start continuous monitoring
        continuous = ContinuousMonitor(monitor, args.requirements)
        
        try:
            await continuous.start(interval_minutes=args.interval)
        except KeyboardInterrupt:
            continuous.stop()
    
    else:
        # Single monitoring run
        metric = await monitor.monitor_installation(args.requirements)
        
        print(f"\nMonitoring Results:")
        print(f"  Timestamp: {metric.timestamp}")
        print(f"  Duration: {metric.duration:.2f}s")
        print(f"  Packages: {metric.packages_count}")
        print(f"  Cache hit rate: {metric.cache_hit_rate*100:.1f}%")
        print(f"  Error rate: {metric.error_rate*100:.1f}%")


if __name__ == '__main__':
    asyncio.run(main())
```

### Task 4.3: 마이그레이션 완료 및 문서화

#### SubTask 4.3.1: 최종 체크리스트
**담당자**: 프로젝트 리더  
**예상 소요시간**: 2시간

```markdown
# uv Migration Final Checklist

## 📋 Pre-Production Checklist

### 1. Infrastructure Readiness
- [ ] **uv Installation**
  - [ ] All development machines have uv installed
  - [ ] CI/CD runners have uv installed
  - [ ] Production Docker images include uv
  - [ ] Version consistency across environments

- [ ] **Cache Configuration**
  - [ ] Cache directories configured on fast storage (SSD)
  - [ ] Cache size limits set appropriately
  - [ ] Cache persistence configured for CI/CD
  - [ ] Backup strategy for cache directories

- [ ] **Network Setup**
  - [ ] Proxy configurations tested (if applicable)
  - [ ] Private PyPI repository accessible
  - [ ] SSL certificates configured
  - [ ] Firewall rules updated

### 2. Code and Configuration
- [ ] **Dependency Files**
  - [ ] All requirements.txt files migrated
  - [ ] pyproject.toml created and validated
  - [ ] Lock files generated (requirements.lock)
  - [ ] Development dependencies separated

- [ ] **Scripts and Automation**
  - [ ] Build scripts updated to use uv
  - [ ] Deployment scripts tested
  - [ ] Makefile targets working
  - [ ] Pre-commit hooks updated

- [ ] **Documentation**
  - [ ] README.md updated with uv instructions
  - [ ] Developer onboarding guide updated
  - [ ] Troubleshooting guide created
  - [ ] API documentation reflects changes

### 3. CI/CD Pipeline
- [ ] **GitHub Actions / GitLab CI**
  - [ ] All workflows updated to use uv
  - [ ] Cache strategy implemented
  - [ ] Build times improved (measure and document)
  - [ ] All tests passing

- [ ] **Docker**
  - [ ] Dockerfiles optimized with uv
  - [ ] Multi-stage builds implemented
  - [ ] Image sizes reduced (measure and document)
  - [ ] Container startup times improved

- [ ] **Deployment**
  - [ ] Staging deployments successful
  - [ ] Rollback procedures tested
  - [ ] Monitoring integrated
  - [ ] Alerts configured

### 4. Testing
- [ ] **Functional Testing**
  - [ ] All unit tests passing
  - [ ] Integration tests passing
  - [ ] End-to-end tests passing
  - [ ] Performance benchmarks completed

- [ ] **Compatibility Testing**
  - [ ] Python version compatibility verified
  - [ ] OS compatibility tested (Linux, macOS, Windows)
  - [ ] Package compatibility confirmed
  - [ ] No regression in functionality

- [ ] **Load Testing**
  - [ ] Installation under load tested
  - [ ] Concurrent builds tested
  - [ ] Cache performance under load verified
  - [ ] Resource usage acceptable

### 5. Team Readiness
- [ ] **Training**
  - [ ] All developers trained on uv
  - [ ] DevOps team familiar with uv operations
  - [ ] Support team briefed on common issues
  - [ ] Documentation accessible to all

- [ ] **Communication**
  - [ ] Migration timeline communicated
  - [ ] Stakeholders informed
  - [ ] Success metrics defined
  - [ ] Feedback channels established

## 🚀 Production Migration Steps

### Phase 1: Pilot (Week 1)
```bash
# 1. Select pilot project
PROJECT="microservice-a"

# 2. Create feature branch
git checkout -b migrate-to-uv

# 3. Update dependencies
cd $PROJECT
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# 4. Run full test suite
make test

# 5. Deploy to staging
make deploy-staging

# 6. Monitor for 24 hours
```

### Phase 2: Gradual Rollout (Week 2-3)
```yaml
# Progressive rollout plan
rollout_schedule:
  week_2:
    - microservice-b
    - microservice-c
    - internal-tools
  week_3:
    - api-gateway
    - worker-services
    - batch-jobs
```

### Phase 3: Full Migration (Week 4)
```bash
# Final migration checklist
for service in $(cat services.txt); do
  echo "Migrating $service..."
  ./scripts/migrate-service.sh $service
  ./scripts/verify-migration.sh $service
done
```

## 📊 Success Metrics

### Performance Metrics
| Metric | Target | Actual | Status |
|--------|--------|---------|---------|
| CI/CD build time reduction | >50% | ___ | ⬜ |
| Docker image build time | >60% | ___ | ⬜ |
| Local development setup | >70% | ___ | ⬜ |
| Cache hit rate | >80% | ___ | ⬜ |

### Operational Metrics
| Metric | Target | Actual | Status |
|--------|--------|---------|---------|
| Installation success rate | >99% | ___ | ⬜ |
| Developer satisfaction | >4/5 | ___ | ⬜ |
| Support tickets | <10/week | ___ | ⬜ |
| Rollback incidents | 0 | ___ | ⬜ |

## 🔄 Rollback Plan

### Immediate Rollback (< 5 minutes)
```bash
#!/bin/bash
# rollback-to-pip.sh

# 1. Stop deployments
kubectl scale deployment --all --replicas=0 -n production

# 2. Revert CI/CD configs
git revert --no-edit HEAD
git push origin main

# 3. Rebuild with pip
docker build -f Dockerfile.pip -t app:rollback .
docker push app:rollback

# 4. Restart services
kubectl set image deployment/app app=app:rollback -n production
kubectl scale deployment --all --replicas=3 -n production
```

### Gradual Rollback
1. Identify affected services
2. Revert configuration service by service
3. Monitor each rollback
4. Document issues for resolution

## 📝 Sign-off Requirements

### Technical Sign-off
- [ ] **Development Lead**: All code changes reviewed and approved
- [ ] **DevOps Lead**: Infrastructure and deployment verified
- [ ] **QA Lead**: All tests passing, no regressions
- [ ] **Security Lead**: No new vulnerabilities introduced

### Business Sign-off
- [ ] **Product Manager**: No impact on product functionality
- [ ] **Engineering Manager**: Team trained and ready
- [ ] **CTO/VP Engineering**: Strategic alignment confirmed

## 🎯 Post-Migration Tasks

### Week 1 After Migration
- [ ] Monitor performance metrics daily
- [ ] Collect developer feedback
- [ ] Address any urgent issues
- [ ] Document lessons learned

### Week 2-4 After Migration
- [ ] Optimize cache settings based on usage
- [ ] Fine-tune CI/CD pipelines
- [ ] Update best practices documentation
- [ ] Plan knowledge sharing session

### Month 2 After Migration
- [ ] Full performance analysis
- [ ] ROI calculation
- [ ] Case study preparation
- [ ] Plan for future optimizations

## ⚠️ Risk Mitigation

### High-Risk Areas
1. **Complex Dependencies**
   - Monitor: TensorFlow, SciPy, NumPy installations
   - Mitigation: Pre-test in isolated environment

2. **Private Packages**
   - Monitor: Internal package resolution
   - Mitigation: Ensure index URLs are correct

3. **Platform-Specific Packages**
   - Monitor: OS-specific wheel installations
   - Mitigation: Test on all target platforms

### Monitoring Alerts
```yaml
alerts:
  - name: high_installation_failure_rate
    condition: failure_rate > 5%
    action: notify_oncall
    
  - name: cache_degradation
    condition: cache_hit_rate < 70%
    action: investigate_cache
    
  - name: performance_regression
    condition: install_time > baseline * 1.5
    action: rollback_consideration
```

## ✅ Final Validation

Run the validation script before marking migration complete:

```bash
#!/bin/bash
# validate-migration.sh

echo "🔍 Validating uv migration..."

# Check all services
for service in $(cat services.txt); do
  echo -n "Checking $service... "
  
  # Verify uv is being used
  if grep -q "uv pip install" $service/Dockerfile; then
    echo "✓"
  else
    echo "✗ Still using pip!"
    exit 1
  fi
done

# Verify CI/CD
echo -n "Checking CI/CD pipelines... "
if grep -q "uv pip" .github/workflows/*.yml; then
  echo "✓"
else
  echo "✗ CI/CD not updated!"
  exit 1
fi

# Performance check
echo -n "Checking performance improvements... "
NEW_TIME=$(make benchmark-ci | grep "Total time" | awk '{print $3}')
OLD_TIME=$(git show main:benchmark-results.txt | grep "Total time" | awk '{print $3}')

if (( $(echo "$NEW_TIME < $OLD_TIME * 0.5" | bc -l) )); then
  echo "✓ ${NEW_TIME}s (was ${OLD_TIME}s)"
else
  echo "✗ Insufficient improvement"
  exit 1
fi

echo ""
echo "✅ All validation checks passed!"
echo "🎉 Migration to uv is complete!"
```

---

**Migration Coordinator Sign-off**

Name: _______________________  
Date: _______________________  
Signature: _______________________

**Notes**: 
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
```

#### SubTask 4.3.2: 사용자 가이드 작성
**담당자**: 기술 문서 작성자  
**예상 소요시간**: 3시간

```markdown
# uv 사용자 가이드

## 목차
1. [시작하기](#시작하기)
2. [기본 사용법](#기본-사용법)
3. [고급 기능](#고급-기능)
4. [문제 해결](#문제-해결)
5. [팁과 트릭](#팁과-트릭)
6. [FAQ](#faq)

---

## 시작하기

### uv란?
uv는 Rust로 작성된 초고속 Python 패키지 매니저입니다. pip보다 10-100배 빠른 성능을 제공하며, 더 나은 의존성 해결과 캐싱을 지원합니다.

### 설치

#### macOS/Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Windows
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### 설치 확인
```bash
uv --version
# uv 0.1.0
```

### 첫 프로젝트 설정

```bash
# 1. 프로젝트 디렉토리 생성
mkdir my-project
cd my-project

# 2. 가상환경 생성
uv venv

# 3. 가상환경 활성화
source .venv/bin/activate  # Unix/macOS
# 또는
.venv\Scripts\activate  # Windows

# 4. 패키지 설치
uv pip install requests pandas flask
```

---

## 기본 사용법

### 패키지 설치

#### 단일 패키지
```bash
uv pip install package_name
uv pip install package_name==1.2.3  # 특정 버전
uv pip install package_name>=1.0,<2.0  # 버전 범위
```

#### requirements.txt에서 설치
```bash
uv pip install -r requirements.txt
```

#### 개발 모드 설치
```bash
uv pip install -e .  # 현재 디렉토리
uv pip install -e /path/to/project  # 특정 경로
```

### 패키지 제거
```bash
uv pip uninstall package_name
uv pip uninstall -r requirements.txt  # 여러 패키지
```

### 패키지 목록 확인
```bash
uv pip list  # 설치된 패키지 목록
uv pip show package_name  # 특정 패키지 정보
uv pip freeze  # requirements.txt 형식으로 출력
```

### 패키지 업그레이드
```bash
uv pip install --upgrade package_name
uv pip install --upgrade -r requirements.txt
```

---

## 고급 기능

### 의존성 컴파일 및 동기화

#### requirements.txt 컴파일
```bash
# requirements.in에서 requirements.txt 생성
uv pip compile requirements.in -o requirements.txt

# 해시 포함 (보안 강화)
uv pip compile --generate-hashes requirements.in -o requirements.txt
```

#### 의존성 동기화
```bash
# 정확히 requirements.txt에 명시된 패키지만 설치
uv pip sync requirements.txt
```

### 캐시 관리

#### 캐시 정보 확인
```bash
uv cache dir  # 캐시 디렉토리 위치
uv cache info  # 캐시 통계
```

#### 캐시 정리
```bash
uv cache clean  # 전체 캐시 삭제
uv cache clean package_name  # 특정 패키지 캐시 삭제
```

### 프로젝트별 설정

#### pyproject.toml 설정
```toml
[project]
name = "my-project"
version = "0.1.0"
dependencies = [
    "fastapi>=0.104.0",
    "pydantic>=2.0.0",
    "sqlalchemy>=2.0.0"
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "black>=23.0.0",
    "mypy>=1.0.0"
]

[tool.uv]
index-url = "https://pypi.org/simple"
find-links = ["https://download.pytorch.org/whl/torch_stable.html"]
```

### 환경 변수

```bash
# 캐시 디렉토리 설정
export UV_CACHE_DIR=/path/to/cache

# 인덱스 URL 설정
export UV_INDEX_URL=https://pypi.company.com/simple

# 타임아웃 설정
export UV_HTTP_TIMEOUT=60

# 병렬 다운로드 수
export UV_CONCURRENT_DOWNLOADS=10
```

---

## 문제 해결

### 일반적인 문제

#### 1. "uv: command not found"
```bash
# PATH에 추가
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

#### 2. SSL 인증서 오류
```bash
# 회사 프록시 환경
export REQUESTS_CA_BUNDLE=/path/to/corporate/cert.pem
export SSL_CERT_FILE=/path/to/corporate/cert.pem
```

#### 3. 패키지 설치 실패
```bash
# 상세 로그 확인
uv pip install problematic-package -v

# 캐시 삭제 후 재시도
uv cache clean problematic-package
uv pip install problematic-package

# 특정 인덱스 사용
uv pip install problematic-package --index-url https://pypi.org/simple
```

#### 4. 메모리 부족
```bash
# 동시 다운로드 수 줄이기
export UV_CONCURRENT_DOWNLOADS=1
uv pip install large-package
```

### 디버깅

#### 상세 로그 출력
```bash
uv pip install package -vvv  # 매우 상세한 로그
```

#### 드라이런 (실제 설치하지 않음)
```bash
uv pip install --dry-run package
```

#### 의존성 트리 확인
```bash
uv pip tree  # 의존성 트리 표시
uv pip tree --reverse package  # 역 의존성 확인
```

---

## 팁과 트릭

### 성능 최적화

#### 1. 로컬 캐시 서버 사용
```bash
# devpi 서버 실행
devpi-server --start --host 0.0.0.0 --port 3141

# uv에서 사용
export UV_INDEX_URL=http://localhost:3141/root/pypi/+simple/
```

#### 2. 사전 다운로드
```bash
# 패키지 미리 다운로드 (캐시에 저장)
uv pip download -r requirements.txt

# 나중에 오프라인 설치
uv pip install --no-index --find-links ./downloads -r requirements.txt
```

#### 3. CI/CD 최적화
```yaml
# GitHub Actions 예제
- name: Cache uv
  uses: actions/cache@v3
  with:
    path: ~/.cache/uv
    key: ${{ runner.os }}-uv-${{ hashFiles('**/requirements.txt') }}
```

### 워크플로우 개선

#### 1. 개발 환경 자동화
```bash
# Makefile
.PHONY: dev-setup
dev-setup:
    uv venv
    . .venv/bin/activate && uv pip install -e ".[dev]"
    . .venv/bin/activate && pre-commit install
```

#### 2. 의존성 업데이트 워크플로우
```bash
# 오래된 패키지 확인
uv pip list --outdated

# 안전한 업데이트
uv pip compile --upgrade-package package_name requirements.in -o requirements.txt
uv pip sync requirements.txt
```

#### 3. 멀티 환경 관리
```bash
# Python 버전별 환경
uv venv --python python3.11 .venv311
uv venv --python python3.12 .venv312

# 환경 전환
source .venv311/bin/activate  # Python 3.11
source .venv312/bin/activate  # Python 3.12
```

---

## FAQ

### Q: pip와 uv를 함께 사용할 수 있나요?
A: 네, 가능합니다. uv는 pip와 호환되므로 같은 가상환경에서 번갈아 사용할 수 있습니다. 하지만 일관성을 위해 하나만 사용하는 것을 권장합니다.

### Q: 기존 requirements.txt를 수정해야 하나요?
A: 아니요, uv는 pip의 requirements.txt 형식을 그대로 사용합니다.

### Q: uv가 지원하지 않는 pip 기능이 있나요?
A: 대부분의 pip 기능을 지원하지만, 일부 고급 기능(예: --user 설치)은 지원하지 않습니다. 전체 목록은 공식 문서를 참조하세요.

### Q: 회사 프록시 뒤에서 사용하려면?
A: 표준 환경 변수를 설정하세요:
```bash
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
export NO_PROXY=localhost,127.0.0.1,.company.com
```

### Q: Docker에서 uv를 사용하는 최선의 방법은?
A: Multi-stage 빌드와 캐시 마운트를 사용하세요:
```dockerfile
# syntax=docker/dockerfile:1.4
FROM python:3.11-slim AS builder
RUN pip install uv
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    uv pip install --prefix=/install -r requirements.txt

FROM python:3.11-slim
COPY --from=builder /install /usr/local
```

### Q: uv 업데이트는 어떻게 하나요?
A: 설치 스크립트를 다시 실행하면 됩니다:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## 추가 리소스

- [공식 문서](https://github.com/astral-sh/uv)
- [성능 벤치마크](./benchmarks.md)
- [마이그레이션 가이드](./migration-guide.md)
- [트러블슈팅 가이드](./troubleshooting.md)

## 지원

문제가 있으신가요?

1. 내부 Slack 채널: #uv-support
2. 이메일: dev-support@company.com
3. 위키: https://wiki.company.com/uv

---

*최종 업데이트: 2024년 12월*
```

#### SubTask 4.3.3: 프로젝트 회고 및 개선사항
**담당자**: 프로젝트 매니저  
**예상 소요시간**: 2시간

```markdown
# uv 마이그레이션 프로젝트 회고

## 📅 프로젝트 개요

- **기간**: 2024년 11월 1일 - 2024년 11월 21일 (3주)
- **팀 규모**: 15명 (개발 10명, DevOps 3명, QA 2명)
- **영향 범위**: 25개 서비스, 100+ 개발자
- **예산**: $50,000

## 🎯 목표 달성도

### 정량적 목표

| 목표 | 목표치 | 실제 달성 | 달성률 |
|------|--------|----------|---------|
| CI/CD 빌드 시간 단축 | 50% | 67% | 134% ✅ |
| Docker 이미지 빌드 시간 | 60% | 72% | 120% ✅ |
| 로컬 개발 환경 설정 시간 | 70% | 85% | 121% ✅ |
| 캐시 적중률 | 80% | 92% | 115% ✅ |
| 설치 성공률 | 99% | 99.7% | 100.7% ✅ |

### 정성적 목표

- ✅ **개발자 경험 개선**: 설문조사 결과 4.6/5.0
- ✅ **유지보수성 향상**: 의존성 관리 이슈 75% 감소
- ✅ **표준화**: 모든 프로젝트가 동일한 도구 사용

## 💡 주요 성과

### 1. 성능 개선
- **평균 패키지 설치 시간**: 180초 → 15초 (12배 개선)
- **CI/CD 파이프라인**: 평균 15분 → 5분
- **Docker 이미지 빌드**: 평균 10분 → 2.5분

### 2. 비용 절감
- **CI/CD 비용**: 월 $3,000 절감 (컴퓨팅 시간 감소)
- **개발자 생산성**: 주당 2시간 절약 × 100명 = 200시간/주
- **연간 예상 절감액**: $250,000

### 3. 기술적 개선
- 의존성 충돌 해결 시간 90% 단축
- 재현 가능한 빌드 100% 달성
- 보안 취약점 스캔 시간 80% 단축

## 📝 교훈 (Lessons Learned)

### 잘된 점 (What Went Well)

1. **단계적 롤아웃 전략**
   - 파일럿 프로젝트로 시작하여 리스크 최소화
   - 각 단계에서 피드백 수집 및 반영
   - 롤백 계획이 잘 작동함

2. **철저한 사전 준비**
   - 포괄적인 벤치마크로 ROI 입증
   - 상세한 마이그레이션 가이드 제작
   - 자동화 스크립트로 수작업 최소화

3. **팀 협업**
   - 개발, DevOps, QA 팀 간 원활한 소통
   - 일일 스탠드업으로 이슈 빠른 해결
   - 지식 공유 세션 효과적

### 개선이 필요했던 점 (What Could Be Improved)

1. **초기 교육 부족**
   - 문제: 일부 개발자가 uv 개념 이해에 어려움
   - 해결: 추가 교육 세션 및 1:1 멘토링 제공
   - 개선안: 사전 교육 자료 더 충실히 준비

2. **Windows 환경 이슈**
   - 문제: Windows 개발자들이 더 많은 이슈 경험
   - 해결: Windows 전용 트러블슈팅 가이드 작성
   - 개선안: 초기부터 모든 OS 동등하게 테스트

3. **모니터링 지연**
   - 문제: 모니터링 대시보드 구축이 마이그레이션 후 진행
   - 해결: 임시 모니터링 스크립트 사용
   - 개선안: 모니터링을 마이그레이션과 동시 진행

## 🔄 개선 사항 및 향후 계획

### 단기 개선 사항 (1개월 내)

1. **문서화 강화**
   ```markdown
   - [ ] 비디오 튜토리얼 제작
   - [ ] 인터랙티브 학습 플랫폼 구축
   - [ ] 팀별 맞춤형 가이드 작성
   ```

2. **도구 개선**
   ```bash
   # uv 헬퍼 스크립트 개발
   uv-helper init  # 프로젝트 초기화
   uv-helper update  # 의존성 업데이트
   uv-helper audit  # 보안 감사
   ```

3. **모니터링 확대**
   - 팀별 대시보드 생성
   - 이상 탐지 알고리즘 구현
   - 성능 회귀 자동 감지

### 중기 계획 (3-6개월)

1. **고급 기능 활용**
   - Workspace 기능 도입
   - 모노레포 최적화
   - 커스텀 인덱스 서버 구축

2. **자동화 확대**
   - 의존성 업데이트 봇
   - 취약점 자동 패치
   - 성능 최적화 제안 시스템

3. **에코시스템 기여**
   - uv 오픈소스 기여
   - 내부 플러그인 개발
   - 커뮤니티 지식 공유

## 📊 ROI 분석

### 투자 대비 수익
- **총 투자**: $50,000 (인건비 + 인프라)
- **연간 절감액**: $250,000
- **투자 회수 기간**: 2.4개월
- **3년 ROI**: 1,400%

### 정성적 이익
- 개발자 만족도 상승
- 신규 개발자 온보딩 시간 50% 단축
- 프로덕션 배포 신뢰성 향상

## 🙏 감사 인사

이 프로젝트의 성공은 모든 팀원들의 헌신적인 노력 덕분입니다.

특별히 감사드립니다:
- **파일럿 팀**: 초기 리스크를 감수하고 피드백 제공
- **DevOps 팀**: 24/7 지원 및 신속한 이슈 해결
- **문서화 팀**: 포괄적인 가이드 작성
- **리더십**: 프로젝트 지원 및 리소스 제공

## 🎉 축하 및 다음 단계

### 성과 축하
- 팀 회식 예정 (11월 25일)
- 우수 기여자 표창
- 성과 보너스 지급

### 지식 공유
- 내부 테크톡: "uv 마이그레이션 성공 스토리" (12월 5일)
- 외부 컨퍼런스 발표 제안서 제출
- 오픈소스 프로젝트로 도구 공개

### 다음 프로젝트
- Poetry → uv 마이그레이션 검토
- Rust 기반 도구 추가 도입 검토
- 패키지 관리 자동화 플랫폼 구축

## 📌 핵심 메시지

> "작은 변화가 큰 차이를 만든다. uv로의 전환은 단순히 도구를 바꾼 것이 아니라, 우리의 개발 문화와 효율성을 한 단계 업그레이드한 것이다."

---

**프로젝트 매니저**: Jane Doe  
**날짜**: 2024년 11월 21일  
**상태**: ✅ 성공적으로 완료
```

---

## 🎯 마무리

이로써 pip에서 uv로의 완전한 마이그레이션 가이드가 완성되었습니다. 이 가이드는 21일 동안의 체계적인 접근을 통해 안전하고 효율적인 전환을 보장합니다.

### 핵심 성공 요소:
1. **단계적 접근**: 급진적 변경보다 점진적 전환
2. **철저한 테스트**: 모든 단계에서 검증
3. **팀 교육**: 모든 구성원의 준비도 확보
4. **자동화**: 수작업 최소화로 오류 방지
5. **모니터링**: 지속적인 성능 추적

uv로의 전환은 단순한 도구 변경이 아닌, 개발 생산성과 팀 효율성을 극대화하는 전략적 투자입니다. 🚀