#!/usr/bin/env python3
"""
GitHub Actions 로그 조회 스크립트
GitHub CLI를 사용하여 최신 워크플로우 실행 상태와 로그를 확인합니다.
"""

import subprocess
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional
import argparse


class GitHubActionsMonitor:
    def __init__(self, repo: str = None):
        """
        GitHub Actions 모니터 초기화

        Args:
            repo: GitHub 리포지토리 (예: owner/repo)
        """
        self.repo = repo or self._get_current_repo()

    def _get_current_repo(self) -> str:
        """현재 Git 리포지토리 정보 가져오기"""
        try:
            result = subprocess.run(
                ["gh", "repo", "view", "--json", "owner,name"],
                capture_output=True,
                text=True,
                check=True,
            )
            data = json.loads(result.stdout)
            return f"{data['owner']['login']}/{data['name']}"
        except subprocess.CalledProcessError:
            print("❌ GitHub 리포지토리 정보를 가져올 수 없습니다.")
            sys.exit(1)

    def get_latest_runs(self, limit: int = 5) -> List[Dict]:
        """최신 워크플로우 실행 목록 가져오기"""
        try:
            result = subprocess.run(
                [
                    "gh",
                    "run",
                    "list",
                    "--repo",
                    self.repo,
                    "--limit",
                    str(limit),
                    "--json",
                    "databaseId,name,status,conclusion,startedAt,event,headBranch,workflowName",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"❌ 워크플로우 실행 목록을 가져올 수 없습니다: {e}")
            return []

    def get_run_details(self, run_id: str) -> Dict:
        """특정 워크플로우 실행의 상세 정보 가져오기"""
        try:
            result = subprocess.run(
                [
                    "gh",
                    "run",
                    "view",
                    run_id,
                    "--repo",
                    self.repo,
                    "--json",
                    "jobs,status,conclusion,startedAt,updatedAt",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"❌ 워크플로우 실행 상세 정보를 가져올 수 없습니다: {e}")
            return {}

    def get_job_logs(self, run_id: str, job_name: Optional[str] = None) -> str:
        """워크플로우 작업 로그 가져오기"""
        try:
            # 먼저 작업 목록 가져오기
            details = self.get_run_details(run_id)
            if not details or "jobs" not in details:
                return "작업 정보를 찾을 수 없습니다."

            # 실패한 작업 찾기
            failed_jobs = [
                job for job in details["jobs"] if job["conclusion"] == "failure"
            ]

            if job_name:
                # 특정 작업 로그 가져오기
                cmd = ["gh", "run", "view", run_id, "--repo", self.repo, "--log-failed"]
            else:
                # 전체 로그 가져오기
                cmd = ["gh", "run", "view", run_id, "--repo", self.repo, "--log"]

            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.stdout

        except subprocess.CalledProcessError as e:
            return f"❌ 로그를 가져올 수 없습니다: {e}"

    def display_runs(self, runs: List[Dict]):
        """워크플로우 실행 목록 표시"""
        if not runs:
            print("📭 실행된 워크플로우가 없습니다.")
            return

        print("\n🔄 최근 GitHub Actions 실행 상태:")
        print("=" * 80)

        for i, run in enumerate(runs, 1):
            status_icon = self._get_status_icon(run["status"], run["conclusion"])
            started = datetime.fromisoformat(run["startedAt"].replace("Z", "+00:00"))

            print(f"\n{i}. {status_icon} {run['workflowName']}")
            print(f"   ID: {run['databaseId']}")
            print(f"   브랜치: {run['headBranch']}")
            print(f"   이벤트: {run['event']}")
            print(f"   상태: {run['status']} / {run['conclusion'] or 'N/A'}")
            print(f"   시작: {started.strftime('%Y-%m-%d %H:%M:%S')}")

    def _get_status_icon(self, status: str, conclusion: Optional[str]) -> str:
        """상태에 따른 아이콘 반환"""
        if status == "in_progress":
            return "🔄"
        elif conclusion == "success":
            return "✅"
        elif conclusion == "failure":
            return "❌"
        elif conclusion == "cancelled":
            return "⚪"
        else:
            return "❓"

    def analyze_failure(self, run_id: str):
        """실패한 워크플로우 분석"""
        print(f"\n🔍 워크플로우 실행 #{run_id} 분석 중...")

        details = self.get_run_details(run_id)
        if not details:
            return

        # 실패한 작업 찾기
        failed_jobs = [
            job for job in details.get("jobs", []) if job["conclusion"] == "failure"
        ]

        if failed_jobs:
            print(f"\n❌ 실패한 작업들:")
            for job in failed_jobs:
                print(f"  - {job['name']}")

                # 실패한 단계 찾기
                failed_steps = [
                    step
                    for step in job.get("steps", [])
                    if step["conclusion"] == "failure"
                ]

                if failed_steps:
                    print(f"    실패한 단계:")
                    for step in failed_steps:
                        print(f"      • {step['name']}")

        # 로그에서 에러 찾기
        print(f"\n📋 에러 로그 추출 중...")
        logs = self.get_job_logs(run_id)

        # 에러 패턴 찾기
        error_lines = []
        for line in logs.split("\n"):
            if any(
                keyword in line.lower()
                for keyword in ["error:", "failed", "exception", "traceback", "❌"]
            ):
                error_lines.append(line)

        if error_lines:
            print("\n🔴 발견된 에러:")
            for line in error_lines[:20]:  # 처음 20개 에러만 표시
                print(f"  {line[:150]}")  # 각 줄 150자까지만 표시


def main():
    parser = argparse.ArgumentParser(description="GitHub Actions 로그 조회 도구")
    parser.add_argument("--repo", help="GitHub 리포지토리 (예: owner/repo)")
    parser.add_argument("--limit", type=int, default=5, help="표시할 실행 개수")
    parser.add_argument("--analyze", type=str, help="특정 실행 ID 분석")
    parser.add_argument("--logs", type=str, help="특정 실행 ID의 로그 보기")

    args = parser.parse_args()

    monitor = GitHubActionsMonitor(args.repo)

    if args.analyze:
        # 특정 실행 분석
        monitor.analyze_failure(args.analyze)
    elif args.logs:
        # 로그 보기
        logs = monitor.get_job_logs(args.logs)
        print(logs)
    else:
        # 최신 실행 목록 표시
        runs = monitor.get_latest_runs(args.limit)
        monitor.display_runs(runs)

        # 최신 실패 찾기
        failed_runs = [r for r in runs if r["conclusion"] == "failure"]
        if failed_runs:
            latest_failure = failed_runs[0]
            print(f"\n💡 최신 실패 분석을 보려면:")
            print(f"   python {__file__} --analyze {latest_failure['databaseId']}")


if __name__ == "__main__":
    main()
