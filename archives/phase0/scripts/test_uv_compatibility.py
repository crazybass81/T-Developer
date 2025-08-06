#!/usr/bin/env python3
# scripts/test_uv_compatibility.py

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
            
            # uv로 설치 시도 (dry-run)
            result = subprocess.run(
                ['/home/ec2-user/.local/bin/uv', 'pip', 'install', '--dry-run', package],
                capture_output=True,
                text=True
            )
            
            elapsed = time.time() - start_time
            
            if result.returncode == 0:
                self.results['successful'].append(package)
                self.results['timing'][package] = elapsed
                print(f"  ✅ Success ({elapsed:.2f}s)")
            else:
                self.results['failed'].append({
                    'package': package,
                    'error': result.stderr,
                    'stdout': result.stdout
                })
                print(f"  ❌ Failed: {result.stderr[:50]}...")
                
                # 대체 방법 시도
                self._try_alternative_install(package)
    
    def _try_alternative_install(self, package):
        """실패한 패키지에 대한 대체 설치 방법 시도"""
        # --pre 옵션으로 시도
        result = subprocess.run(
            ['/home/ec2-user/.local/bin/uv', 'pip', 'install', '--dry-run', '--pre', package],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            self.results['warnings'].append({
                'package': package,
                'message': 'Requires --pre flag',
                'solution': f'uv pip install --pre {package}'
            })
            print(f"  ⚠️  Works with --pre flag")
    
    def test_bulk_installation(self):
        """전체 requirements 파일로 한번에 설치 테스트"""
        print("\n🔄 Bulk installation test...")
        
        start_time = time.time()
        result = subprocess.run(
            ['/home/ec2-user/.local/bin/uv', 'pip', 'install', '--dry-run', '-r', self.requirements_file],
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
        
        if result.returncode == 0:
            print(f"  ✅ Bulk install successful ({elapsed:.2f}s)")
        else:
            print(f"  ❌ Bulk install failed: {result.stderr[:100]}...")
    
    def compare_with_pip(self):
        """pip과 성능 비교"""
        print("\n⚡ Performance comparison...")
        
        # pip 설치 시간 (dry-run)
        start_time = time.time()
        pip_result = subprocess.run(
            ['pip', 'install', '--dry-run', '-r', self.requirements_file],
            capture_output=True,
            text=True
        )
        pip_time = time.time() - start_time
        
        # uv 설치 시간 (dry-run)
        start_time = time.time()
        uv_result = subprocess.run(
            ['/home/ec2-user/.local/bin/uv', 'pip', 'install', '--dry-run', '-r', self.requirements_file],
            capture_output=True,
            text=True
        )
        uv_time = time.time() - start_time
        
        self.results['performance'] = {
            'pip_time': pip_time,
            'uv_time': uv_time,
            'speedup': pip_time / uv_time if uv_time > 0 else 0,
            'pip_success': pip_result.returncode == 0,
            'uv_success': uv_result.returncode == 0
        }
        
        print(f"  pip time: {pip_time:.2f}s")
        print(f"  uv time: {uv_time:.2f}s")
        if uv_time > 0:
            print(f"  Speedup: {pip_time / uv_time:.1f}x")
    
    def generate_report(self):
        """상세 보고서 생성"""
        success_rate = len(self.results['successful']) / self.results['total_packages'] * 100 if self.results['total_packages'] > 0 else 0
        
        # JSON 형식으로 저장
        with open('uv_compatibility_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # 요약 출력
        print(f"\n📊 Test Summary:")
        print(f"  Total packages: {self.results['total_packages']}")
        print(f"  Successful: {len(self.results['successful'])} ({success_rate:.1f}%)")
        print(f"  Failed: {len(self.results['failed'])}")
        print(f"  Warnings: {len(self.results['warnings'])}")
        
        if 'performance' in self.results:
            perf = self.results['performance']
            print(f"  Performance: {perf['speedup']:.1f}x faster than pip")

if __name__ == '__main__':
    tester = UvCompatibilityTester('requirements.txt')
    tester.test_individual_packages()
    tester.test_bulk_installation()
    tester.compare_with_pip()
    tester.generate_report()