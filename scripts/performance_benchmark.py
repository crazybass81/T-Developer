#!/usr/bin/env python3
import subprocess
import time
import statistics
import json

class PerformanceBenchmark:
    def __init__(self):
        self.results = {'pip': [], 'uv': []}
        
    def run_benchmark(self, tool, venv_path, iterations=3):
        """Run benchmark for specified tool"""
        times = []
        
        for i in range(iterations):
            print(f"  Run {i+1}/{iterations} for {tool}...")
            
            # Clean environment
            subprocess.run(['rm', '-rf', venv_path], capture_output=True)
            
            if tool == 'pip':
                subprocess.run(['python3', '-m', 'venv', venv_path], capture_output=True)
                cmd = f"source {venv_path}/bin/activate && pip install -r requirements.txt"
            else:
                subprocess.run(['/home/ec2-user/.local/bin/uv', 'venv', venv_path], capture_output=True)
                cmd = f"source {venv_path}/bin/activate && /home/ec2-user/.local/bin/uv pip install -r requirements.txt"
            
            start = time.time()
            result = subprocess.run(['bash', '-c', cmd], capture_output=True)
            duration = time.time() - start
            
            if result.returncode == 0:
                times.append(duration)
                print(f"    ✅ {duration:.2f}s")
            else:
                print(f"    ❌ Failed")
        
        return times
    
    def run_all_benchmarks(self):
        print("🏃 Running performance benchmarks...")
        
        # pip benchmark
        print("\n📦 Testing pip...")
        pip_times = self.run_benchmark('pip', '.venv-bench-pip')
        
        # uv benchmark  
        print("\n⚡ Testing uv...")
        uv_times = self.run_benchmark('uv', '.venv-bench-uv')
        
        # Results
        if pip_times and uv_times:
            pip_avg = statistics.mean(pip_times)
            uv_avg = statistics.mean(uv_times)
            speedup = pip_avg / uv_avg
            
            results = {
                'pip': {
                    'times': pip_times,
                    'average': pip_avg,
                    'std_dev': statistics.stdev(pip_times) if len(pip_times) > 1 else 0
                },
                'uv': {
                    'times': uv_times,
                    'average': uv_avg,
                    'std_dev': statistics.stdev(uv_times) if len(uv_times) > 1 else 0
                },
                'speedup': speedup
            }
            
            with open('benchmark_results.json', 'w') as f:
                json.dump(results, f, indent=2)
            
            print(f"\n📊 Results:")
            print(f"  pip average: {pip_avg:.2f}s")
            print(f"  uv average: {uv_avg:.2f}s")
            print(f"  Speedup: {speedup:.1f}x")

if __name__ == '__main__':
    benchmark = PerformanceBenchmark()
    benchmark.run_all_benchmarks()