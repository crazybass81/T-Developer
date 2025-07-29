#!/bin/bash

# T-Developer 디버깅 명령어 모음

echo "🔧 T-Developer Debugging Commands"
echo "================================="

case "$1" in
  "setup")
    echo "Setting up debugging environment..."
    ts-node scripts/setup-debugging.ts
    ;;
    
  "inspect")
    echo "Starting Node.js inspector..."
    node --inspect-brk=0.0.0.0:9229 -r ts-node/register backend/src/main.ts
    ;;
    
  "profile")
    echo "Starting with CPU profiling..."
    node --prof -r ts-node/register backend/src/main.ts
    echo "Profile saved. Run 'npm run debug:analyze-profile' to analyze."
    ;;
    
  "analyze-profile")
    echo "Analyzing CPU profile..."
    node --prof-process isolate-*.log > profile-analysis.txt
    echo "Analysis saved to profile-analysis.txt"
    ;;
    
  "heap")
    echo "Taking heap snapshot..."
    kill -USR2 $(pgrep -f "node.*main.ts")
    echo "Heap snapshot saved to heapdump-*.heapsnapshot"
    ;;
    
  "trace")
    echo "Starting with trace events..."
    node --trace-events-enabled -r ts-node/register backend/src/main.ts
    ;;
    
  "memory")
    echo "Starting with memory monitoring..."
    node --max-old-space-size=4096 --expose-gc -r ts-node/register backend/src/main.ts
    ;;
    
  "agent")
    if [ -z "$2" ]; then
      echo "Usage: npm run debug:agent <agent-name>"
      exit 1
    fi
    echo "Debugging agent: $2"
    node --inspect-brk=9229 -r ts-node/register backend/src/agents/$2-agent.ts
    ;;
    
  "test")
    echo "Debugging tests..."
    node --inspect-brk=9229 node_modules/.bin/jest --runInBand --no-cache
    ;;
    
  "clean")
    echo "Cleaning debug files..."
    rm -f isolate-*.log
    rm -f heapdump-*.heapsnapshot
    rm -f profile-analysis.txt
    rm -f v8.log
    echo "Debug files cleaned."
    ;;
    
  *)
    echo "Available commands:"
    echo "  setup          - Setup debugging environment"
    echo "  inspect        - Start with Node.js inspector"
    echo "  profile        - Start with CPU profiling"
    echo "  analyze-profile - Analyze CPU profile"
    echo "  heap           - Take heap snapshot"
    echo "  trace          - Start with trace events"
    echo "  memory         - Start with memory monitoring"
    echo "  agent <name>   - Debug specific agent"
    echo "  test           - Debug tests"
    echo "  clean          - Clean debug files"
    echo ""
    echo "Usage: npm run debug:<command>"
    ;;
esac