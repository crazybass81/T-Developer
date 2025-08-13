#!/bin/bash
# T-Developer 일일 작업 검증 편의 스크립트

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 프로젝트 루트 디렉토리
PROJECT_ROOT="/home/ec2-user/T-DeveloperMVP"
cd "$PROJECT_ROOT"

# 함수: 현재 Day 계산
calculate_current_day() {
    START_DATE="2024-11-14"
    CURRENT_DATE=$(date +%Y-%m-%d)
    DAYS_DIFF=$(( ($(date -d "$CURRENT_DATE" +%s) - $(date -d "$START_DATE" +%s)) / 86400 + 1 ))
    
    if [ $DAYS_DIFF -gt 80 ]; then
        DAYS_DIFF=80
    elif [ $DAYS_DIFF -lt 1 ]; then
        DAYS_DIFF=1
    fi
    
    echo $DAYS_DIFF
}

# 함수: 작업 검증
validate_day() {
    local day=$1
    echo -e "${BLUE}🔍 Day $day 작업 검증 시작...${NC}"
    
    # Python 스크립트 실행
    if python backend/scripts/daily_workflow.py --day $day --skip-git; then
        echo -e "${GREEN}✅ Day $day 검증 성공!${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️ Day $day 검증 실패${NC}"
        return 1
    fi
}

# 함수: 작업 완료
complete_day() {
    local day=$1
    echo -e "${BLUE}🚀 Day $day 작업 완료 프로세스 시작...${NC}"
    
    # 1. 검증
    echo -e "${BLUE}1단계: 작업 검증${NC}"
    python backend/scripts/daily_workflow.py --day $day --skip-git
    
    # 2. 미완료 작업 수정
    echo -e "${BLUE}2단계: 미완료 작업 자동 수정${NC}"
    python backend/scripts/daily_workflow.py --day $day --auto-fix --skip-git
    
    # 3. 문서 업데이트 및 Git 커밋
    echo -e "${BLUE}3단계: 문서 업데이트 및 Git 커밋${NC}"
    python backend/scripts/daily_workflow.py --day $day
    
    echo -e "${GREEN}✅ Day $day 작업 완료!${NC}"
}

# 함수: 상태 표시
show_status() {
    local day=$1
    local phase=$(( (day - 1) / 20 + 1 ))
    local week=$(( (day - 1) / 7 + 1 ))
    
    echo -e "${BLUE}╔══════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║   T-Developer Progress Status        ║${NC}"
    echo -e "${BLUE}╠══════════════════════════════════════╣${NC}"
    echo -e "${BLUE}║${NC} 📅 Day:    ${GREEN}$day / 80${NC}                   ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC} 📊 Phase:  ${GREEN}$phase / 4${NC}                    ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC} 📆 Week:   ${GREEN}$week / 12${NC}                   ${BLUE}║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════╝${NC}"
}

# 메인 로직
main() {
    case "${1:-}" in
        validate)
            DAY=${2:-$(calculate_current_day)}
            show_status $DAY
            validate_day $DAY
            ;;
        complete)
            DAY=${2:-$(calculate_current_day)}
            show_status $DAY
            complete_day $DAY
            ;;
        status)
            DAY=$(calculate_current_day)
            show_status $DAY
            ;;
        fix)
            DAY=${2:-$(calculate_current_day)}
            echo -e "${BLUE}🔧 Day $DAY 미완료 작업 수정...${NC}"
            python backend/scripts/daily_workflow.py --day $DAY --auto-fix --skip-git
            ;;
        *)
            echo "Usage: $0 {validate|complete|status|fix} [day_number]"
            echo ""
            echo "Commands:"
            echo "  validate [day]  - Validate day's work (default: current day)"
            echo "  complete [day]  - Complete day's work with validation and git"
            echo "  status          - Show current progress status"
            echo "  fix [day]       - Fix incomplete tasks for a day"
            echo ""
            echo "Examples:"
            echo "  $0 validate      # Validate current day"
            echo "  $0 validate 3    # Validate day 3"
            echo "  $0 complete 3    # Complete day 3 with all steps"
            echo "  $0 status        # Show current status"
            exit 1
            ;;
    esac
}

main "$@"