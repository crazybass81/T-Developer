#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}T-Developer Service Monitor${NC}"
echo "============================="

# Check if service is running
echo -n "Checking T-Developer service status: "
if systemctl is-active --quiet t-developer; then
  echo -e "${GREEN}RUNNING${NC}"
  
  # Get service uptime
  STARTED_AT=$(systemctl show t-developer -p ActiveEnterTimestamp | cut -d= -f2)
  echo "Service started at: $STARTED_AT"
  
  # Get memory usage
  PID=$(systemctl show t-developer -p MainPID | cut -d= -f2)
  if [ "$PID" != "0" ]; then
    MEM_USAGE=$(ps -o rss= -p $PID | awk '{print $1/1024 " MB"}')
    CPU_USAGE=$(ps -o %cpu= -p $PID)
    echo "Memory usage: $MEM_USAGE"
    echo "CPU usage: $CPU_USAGE%"
  fi
else
  echo -e "${RED}NOT RUNNING${NC}"
  echo "Checking service logs for errors:"
  journalctl -u t-developer -n 10 --no-pager
fi

# Check API health
echo -n "Checking API health: "
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ "$HEALTH_STATUS" == "200" ]; then
  echo -e "${GREEN}OK (200)${NC}"
  
  # Get detailed health info
  HEALTH_INFO=$(curl -s http://localhost:8000/health/detailed)
  echo "API Version: $(echo $HEALTH_INFO | jq -r .version)"
  echo "Projects: $(echo $HEALTH_INFO | jq -r .projects)"
  echo "Tasks: $(echo $HEALTH_INFO | jq -r .tasks.total) ($(echo $HEALTH_INFO | jq -r .tasks.completed) completed, $(echo $HEALTH_INFO | jq -r .tasks.error) errors)"
else
  echo -e "${RED}FAILED ($HEALTH_STATUS)${NC}"
fi

# Check Lambda functions
echo -e "\n${GREEN}Lambda Functions Status${NC}"
echo "========================"

check_lambda() {
  local name=$1
  echo -n "Checking $name: "
  if aws lambda get-function --function-name $name --region $(aws configure get region) &>/dev/null; then
    CONFIG=$(aws lambda get-function --function-name $name --region $(aws configure get region))
    LAST_MODIFIED=$(echo $CONFIG | jq -r .Configuration.LastModified)
    RUNTIME=$(echo $CONFIG | jq -r .Configuration.Runtime)
    MEMORY=$(echo $CONFIG | jq -r .Configuration.MemorySize)
    echo -e "${GREEN}DEPLOYED${NC}"
    echo "  Last modified: $LAST_MODIFIED"
    echo "  Runtime: $RUNTIME"
    echo "  Memory: $MEMORY MB"
    
    # Check recent invocations
    METRICS=$(aws cloudwatch get-metric-statistics --namespace AWS/Lambda --metric-name Invocations --start-time $(date -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) --end-time $(date +%Y-%m-%dT%H:%M:%S) --period 3600 --statistics Sum --dimensions Name=FunctionName,Value=$name --region $(aws configure get region))
    INVOCATIONS=$(echo $METRICS | jq -r '.Datapoints[0].Sum // 0')
    echo "  Invocations (last hour): $INVOCATIONS"
  else
    echo -e "${YELLOW}NOT DEPLOYED${NC}"
  fi
}

check_lambda "t-developer-slack-notifier"
check_lambda "t-developer-test-executor"
check_lambda "t-developer-code-generator"

echo -e "\n${GREEN}System Resources${NC}"
echo "================="
echo "CPU Load: $(uptime | awk -F'load average:' '{ print $2 }' | tr -d ',')"
echo "Memory Usage:"
free -h | grep "Mem:" | awk '{print "  Total: " $2 "  Used: " $3 "  Free: " $4}'
echo "Disk Usage:"
df -h / | tail -n 1 | awk '{print "  Total: " $2 "  Used: " $3 "  Free: " $4 "  Usage: " $5}'