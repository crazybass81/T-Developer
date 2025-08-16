# T-Developer v2 Operations Runbook

## System Overview

T-Developer v2 is an autonomous self-evolving system. This runbook covers operational procedures for monitoring, maintaining, and troubleshooting the system.

## Daily Operations

### Morning Checklist (9 AM)

```bash
# 1. Check system health
python scripts/health_check.py --full

# 2. Review overnight evolution cycles
python scripts/show_evolution_history.py --since yesterday

# 3. Check pending PRs
gh pr list --label "auto-evolution"

# 4. Review metrics trends
python scripts/show_metrics.py --trend --days 7

# 5. Check cost dashboard
python scripts/show_costs.py --date yesterday
```

### Evening Checklist (6 PM)

```bash
# 1. Review day's evolution cycles
python scripts/show_evolution_history.py --since today

# 2. Check for stuck processes
python scripts/check_stuck_processes.py

# 3. Clean up temporary resources
python scripts/cleanup.py --temp --older-than 24h

# 4. Backup evolution history
python scripts/backup_history.py --date today
```

## Monitoring

### Key Metrics to Watch

| Metric | Normal Range | Alert Threshold | Action |
|--------|--------------|-----------------|--------|
| Evolution Success Rate | >85% | <70% | Check logs for failures |
| Cycle Time | <4 hours | >6 hours | Investigate bottlenecks |
| Cost per Cycle | <$10 | >$20 | Review resource usage |
| PR Merge Rate | >90% | <75% | Check quality gates |
| Error Rate | <5% | >10% | Review error logs |

### CloudWatch Dashboards

1. **Main Dashboard**: Overall system health
2. **Agent Dashboard**: Individual agent performance
3. **Cost Dashboard**: Resource consumption and costs
4. **Security Dashboard**: Security events and scans

### Alerts Configuration

```yaml
alerts:
  - name: EvolutionFailure
    metric: EvolutionSuccessRate
    threshold: 70
    period: 3600
    action: notify-oncall
    
  - name: HighCost
    metric: CostPerCycle
    threshold: 20
    period: 1800
    action: notify-team
    
  - name: SecurityViolation
    metric: SecurityGateFailures
    threshold: 1
    period: 300
    action: page-security
```

## Common Procedures

### Starting an Evolution Cycle

```bash
# 1. Verify system ready
python scripts/pre_evolution_check.py

# 2. Set parameters
export EVOLUTION_TARGET="packages/agents"
export EVOLUTION_CYCLES=1
export EVOLUTION_FOCUS="quality"

# 3. Start evolution
python scripts/run_evolution.py \
  --target $EVOLUTION_TARGET \
  --cycles $EVOLUTION_CYCLES \
  --focus $EVOLUTION_FOCUS \
  --monitor

# 4. Monitor progress
tail -f evolution_history/current.log
```

### Stopping a Runaway Evolution

```bash
# 1. Identify the runaway process
python scripts/show_active_evolutions.py

# 2. Graceful stop
python scripts/stop_evolution.py --id <evolution_id> --graceful

# 3. If graceful fails, force stop
python scripts/stop_evolution.py --id <evolution_id> --force

# 4. Clean up resources
python scripts/cleanup.py --evolution <evolution_id>

# 5. Analyze what went wrong
python scripts/analyze_failure.py --id <evolution_id>
```

### Rolling Back Changes

```bash
# 1. Identify the problematic PR
gh pr list --state merged --limit 10

# 2. Create revert PR
gh pr revert <pr_number>

# 3. Or manual git revert
git revert <commit_hash>
git push origin main

# 4. Re-run metrics to confirm fix
python scripts/check_metrics.py --all

# 5. Add pattern to prevent recurrence
python scripts/add_prevention_pattern.py --from-pr <pr_number>
```

### Investigating Failures

```bash
# 1. Get failure details
python scripts/show_failure.py --id <task_id>

# 2. Check agent logs
aws logs tail /aws/lambda/research-agent --since 1h
aws logs tail /aws/lambda/planner-agent --since 1h

# 3. Check MCP server logs
cat ~/.mcp/logs/server.log | grep ERROR

# 4. Trace the execution
python scripts/trace_execution.py --trace-id <trace_id>

# 5. Generate failure report
python scripts/generate_failure_report.py --id <task_id> --output report.md
```

## Troubleshooting

### Agent Not Responding

**Symptoms**: Agent timeout, no output

**Check**:
```bash
# 1. Check agent health
curl -X GET https://agentcore.region.amazonaws.com/agents/<agent_id>/health

# 2. Check Lambda/ECS status
aws lambda get-function --function-name <agent_name>
aws ecs describe-services --cluster <cluster> --services <service>

# 3. Check resource limits
python scripts/check_resource_usage.py --agent <agent_name>
```

**Fix**:
```bash
# Restart agent
python scripts/restart_agent.py --name <agent_name>

# Scale up if needed
python scripts/scale_agent.py --name <agent_name> --instances 3
```

### MCP Connection Issues

**Symptoms**: "MCP server not found", file operations failing

**Check**:
```bash
# 1. Test MCP servers
python -m mcp.test all

# 2. Check server processes
ps aux | grep mcp-server

# 3. Verify configuration
cat packages/mcp/clients/claude.mcp.json
```

**Fix**:
```bash
# Restart MCP servers
python scripts/restart_mcp.py --all

# Reset configuration
python scripts/init_evolution.py --reset-mcp
```

### Quality Gates Failing

**Symptoms**: PRs consistently blocked

**Check**:
```bash
# 1. Check current metrics
python scripts/check_metrics.py --verbose

# 2. Review gate configuration
cat .github/workflows/ci.yml

# 3. Check recent changes
git log --oneline -10 .github/
```

**Fix**:
```bash
# Adjust thresholds if needed
python scripts/adjust_gates.py --metric docstring --threshold 75

# Or fix the underlying issues
python scripts/run_evolution.py --focus quality --force
```

### High Costs

**Symptoms**: Cost alerts, budget exceeded

**Check**:
```bash
# 1. Identify cost drivers
python scripts/cost_analysis.py --breakdown

# 2. Check for stuck resources
aws lambda list-functions | grep -i stuck
aws ecs list-tasks --cluster <cluster> | grep RUNNING

# 3. Review recent usage
aws ce get-cost-and-usage --time-period Start=2024-01-01,End=2024-01-31
```

**Fix**:
```bash
# 1. Set cost limits
python scripts/set_cost_limits.py --daily 100 --per-cycle 10

# 2. Optimize resource usage
python scripts/optimize_resources.py --aggressive

# 3. Clean up unused resources
python scripts/cleanup.py --all --force
```

## Maintenance

### Weekly Tasks

```bash
# Monday: Review and merge dependabot PRs
gh pr list --label dependencies

# Tuesday: Update patterns database
python scripts/update_patterns.py --source evolution_history/

# Wednesday: Performance analysis
python scripts/analyze_performance.py --week

# Thursday: Security audit
python scripts/security_audit.py --full

# Friday: Backup and cleanup
python scripts/weekly_maintenance.py
```

### Monthly Tasks

```bash
# Update dependencies
uv pip install --upgrade -r requirements.txt

# Rotate secrets
python scripts/rotate_secrets.py --all

# Archive old logs
python scripts/archive_logs.py --older-than 30d

# Generate monthly report
python scripts/generate_monthly_report.py
```

## Disaster Recovery

### Backup Procedures

```bash
# Daily backup
0 2 * * * python scripts/backup.py --daily

# Weekly full backup  
0 3 * * 0 python scripts/backup.py --full

# Backup locations:
# - S3: s3://t-developer-backups/
# - Local: /backups/t-developer/
```

### Recovery Procedures

```bash
# 1. Stop all agents
python scripts/stop_all_agents.py

# 2. Restore from backup
python scripts/restore.py --date 2024-01-15 --confirm

# 3. Verify restoration
python scripts/verify_restore.py

# 4. Restart agents
python scripts/start_all_agents.py

# 5. Run health check
python scripts/health_check.py --post-recovery
```

## Contact Information

### Escalation Path

1. **Level 1**: On-call engineer (PagerDuty)
2. **Level 2**: Team lead
3. **Level 3**: Platform team
4. **Level 4**: Security team (for security issues)

### Key Contacts

- **On-call**: See PagerDuty schedule
- **Team Slack**: #t-developer-ops
- **Emergency**: security@company.com

## Appendix

### Useful Commands

```bash
# Show all agent statuses
python scripts/agent_status.py --all

# Force garbage collection
python scripts/gc.py --aggressive

# Export metrics
python scripts/export_metrics.py --format prometheus

# Generate SLA report
python scripts/sla_report.py --month 2024-01

# Test disaster recovery
python scripts/dr_test.py --simulate
```

### Environment Variables

```bash
# Override defaults for debugging
export DEBUG=true
export LOG_LEVEL=DEBUG
export EVOLUTION_DRY_RUN=true
export MAX_CYCLES=1
export TIMEOUT_SECONDS=300
```

### Log Locations

- Application logs: `/var/log/t-developer/`
- Evolution history: `./evolution_history/`
- Agent logs: CloudWatch Logs
- MCP logs: `~/.mcp/logs/`
- System logs: `/var/log/syslog`