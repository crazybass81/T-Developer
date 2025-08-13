#!/usr/bin/env python3
"""
GitHub Actions 로그 조회 스크립트 (API 버전)
GitHub API를 직접 사용하여 워크플로우 실행 상태와 로그를 확인합니다.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

import requests


class GitHubActionsAPI:
    def __init__(self, repo: str = "crazybass81/T-DeveloperMVP", token: Optional[str] = None):
        """
        GitHub Actions API 클라이언트 초기화

        Args:
            repo: GitHub 리포지토리 (예: owner/repo)
            token: GitHub Personal Access Token (선택사항)
        """
        self.repo = repo
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.base_url = f"https://api.github.com/repos/{repo}"
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

    def get_workflows(self) -> List[Dict]:
        """워크플로우 목록 가져오기"""
        url = f"{self.base_url}/actions/workflows"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json().get("workflows", [])
        else:
            print(f"❌ 워크플로우 목록을 가져올 수 없습니다: {response.status_code}")
            return []

    def get_workflow_runs(self, limit: int = 10) -> List[Dict]:
        """최신 워크플로우 실행 목록 가져오기"""
        url = f"{self.base_url}/actions/runs"
        params = {"per_page": limit}
        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code == 200:
            return response.json().get("workflow_runs", [])
        else:
            print(f"❌ 워크플로우 실행 목록을 가져올 수 없습니다: {response.status_code}")
            return []

    def get_run_details(self, run_id: int) -> Dict:
        """특정 워크플로우 실행의 상세 정보 가져오기"""
        url = f"{self.base_url}/actions/runs/{run_id}"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ 워크플로우 실행 상세 정보를 가져올 수 없습니다: {response.status_code}")
            return {}

    def get_run_jobs(self, run_id: int) -> List[Dict]:
        """워크플로우 실행의 작업 목록 가져오기"""
        url = f"{self.base_url}/actions/runs/{run_id}/jobs"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json().get("jobs", [])
        else:
            print(f"❌ 작업 목록을 가져올 수 없습니다: {response.status_code}")
            return []

    def get_job_logs(self, job_id: int) -> str:
        """특정 작업의 로그 가져오기"""
        url = f"{self.base_url}/actions/jobs/{job_id}/logs"
        response = requests.get(url, headers=self.headers, allow_redirects=True)

        if response.status_code == 200:
            return response.text
        else:
            return f"❌ 로그를 가져올 수 없습니다: {response.status_code}"

    def display_runs(self, runs: List[Dict]):
        """워크플로우 실행 목록 표시"""
        if not runs:
            print("📭 실행된 워크플로우가 없습니다.")
            return

        print("\n🔄 최근 GitHub Actions 실행 상태:")
        print("=" * 100)

        for i, run in enumerate(runs, 1):
            status_icon = self._get_status_icon(run["status"], run["conclusion"])
            created = datetime.strptime(run["created_at"], "%Y-%m-%dT%H:%M:%SZ")

            print(f"\n{i}. {status_icon} {run['name']}")
            print(f"   ID: {run['id']}")
            print(f"   Run #: {run['run_number']}")
            print(f"   브랜치: {run['head_branch']}")
            print(f"   커밋: {run['head_sha'][:8]}")
            print(f"   이벤트: {run['event']}")
            print(f"   상태: {run['status']} / {run['conclusion'] or 'In Progress'}")
            print(f"   시작: {created.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            print(f"   URL: {run['html_url']}")

    def _get_status_icon(self, status: str, conclusion: Optional[str]) -> str:
        """상태에 따른 아이콘 반환"""
        if status == "in_progress" or status == "queued":
            return "🔄"
        elif conclusion == "success":
            return "✅"
        elif conclusion == "failure":
            return "❌"
        elif conclusion == "cancelled":
            return "⚪"
        elif conclusion == "skipped":
            return "⏭️"
        else:
            return "❓"

    def analyze_failure(self, run_id: int):
        """실패한 워크플로우 분석"""
        print(f"\n🔍 워크플로우 실행 #{run_id} 분석 중...")

        # 실행 상세 정보 가져오기
        run_details = self.get_run_details(run_id)
        if not run_details:
            return

        print(f"\n📊 실행 정보:")
        print(f"  이름: {run_details['name']}")
        print(f"  상태: {run_details['status']}")
        print(f"  결론: {run_details['conclusion']}")
        print(f"  URL: {run_details['html_url']}")

        # 작업 목록 가져오기
        jobs = self.get_run_jobs(run_id)

        # 실패한 작업 찾기
        failed_jobs = [job for job in jobs if job["conclusion"] == "failure"]

        if failed_jobs:
            print(f"\n❌ 실패한 작업들:")
            for job in failed_jobs:
                print(f"\n  작업: {job['name']}")
                print(f"  ID: {job['id']}")
                print(f"  시작: {job['started_at']}")
                print(f"  종료: {job['completed_at']}")

                # 실패한 단계 찾기
                failed_steps = [
                    step for step in job.get("steps", []) if step["conclusion"] == "failure"
                ]

                if failed_steps:
                    print(f"  실패한 단계:")
                    for step in failed_steps:
                        print(f"    • {step['name']}")
                        print(f"      상태: {step['status']}")
                        print(f"      결론: {step['conclusion']}")

                # 로그 가져오기 (토큰이 있는 경우)
                if self.token:
                    print(f"\n  📋 로그에서 에러 추출 중...")
                    logs = self.get_job_logs(job["id"])

                    # 에러 라인 찾기
                    error_lines = []
                    for line in logs.split("\n"):
                        line_lower = line.lower()
                        if any(
                            keyword in line_lower
                            for keyword in [
                                "error:",
                                "error process",
                                "failed",
                                "failure",
                                "exception",
                                "traceback",
                                "syntaxerror",
                                "typeerror",
                                "attributeerror",
                                "importerror",
                                "❌",
                            ]
                        ):
                            error_lines.append(line)

                    if error_lines:
                        print(f"\n  🔴 발견된 주요 에러 (최대 15줄):")
                        for line in error_lines[:15]:
                            # ANSI 색상 코드 제거
                            clean_line = line.replace("\x1b[0m", "").replace("\x1b[91m", "")
                            clean_line = clean_line.replace("\x1b[31m", "").replace("\x1b[32m", "")
                            print(f"    {clean_line[:200]}")
                else:
                    print("\n  ℹ️ 로그를 보려면 GITHUB_TOKEN 환경변수를 설정하세요.")

    def monitor_latest(self):
        """최신 실행 모니터링"""
        runs = self.get_workflow_runs(5)

        if not runs:
            print("실행된 워크플로우가 없습니다.")
            return

        # 진행 중인 실행 찾기
        in_progress = [r for r in runs if r["status"] in ["in_progress", "queued"]]

        if in_progress:
            print(f"\n⏳ 진행 중인 워크플로우: {len(in_progress)}개")
            for run in in_progress:
                print(f"  - {run['name']} (#{run['run_number']})")
                print(f"    URL: {run['html_url']}")

        # 최근 실패 찾기
        failed = [r for r in runs if r["conclusion"] == "failure"]

        if failed:
            latest_failure = failed[0]
            print(f"\n❌ 최근 실패한 워크플로우:")
            print(f"  {latest_failure['name']} (#{latest_failure['run_number']})")
            print(f"  URL: {latest_failure['html_url']}")

            # 자동으로 분석
            self.analyze_failure(latest_failure["id"])


def main():
    parser = argparse.ArgumentParser(description="GitHub Actions 로그 조회 도구")
    parser.add_argument(
        "--repo",
        default="crazybass81/T-DeveloperMVP",
        help="GitHub 리포지토리 (예: owner/repo)",
    )
    parser.add_argument("--token", help="GitHub Personal Access Token")
    parser.add_argument("--limit", type=int, default=5, help="표시할 실행 개수")
    parser.add_argument("--analyze", type=int, help="특정 실행 ID 분석")
    parser.add_argument("--monitor", action="store_true", help="최신 실행 모니터링 및 실패 자동 분석")

    args = parser.parse_args()

    # 토큰 확인
    token = args.token or os.getenv("GITHUB_TOKEN")
    if not token:
        print("⚠️ 주의: GITHUB_TOKEN이 설정되지 않았습니다.")
        print("  API 제한이 있을 수 있으며, 로그를 볼 수 없습니다.")
        print("  export GITHUB_TOKEN=your_token 으로 설정하세요.\n")

    api = GitHubActionsAPI(args.repo, token)

    if args.analyze:
        # 특정 실행 분석
        api.analyze_failure(args.analyze)
    elif args.monitor:
        # 최신 모니터링
        api.monitor_latest()
    else:
        # 최신 실행 목록 표시
        runs = api.get_workflow_runs(args.limit)
        api.display_runs(runs)

        # 최신 실패 안내
        failed_runs = [r for r in runs if r["conclusion"] == "failure"]
        if failed_runs:
            latest_failure = failed_runs[0]
            print(f"\n💡 최신 실패 분석을 보려면:")
            print(f"   python3 {__file__} --analyze {latest_failure['id']}")
            print(f"\n💡 또는 자동 모니터링:")
            print(f"   python3 {__file__} --monitor")


if __name__ == "__main__":
    main()
