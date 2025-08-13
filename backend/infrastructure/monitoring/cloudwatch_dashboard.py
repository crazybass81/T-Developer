#!/usr/bin/env python3
"""
CloudWatch Dashboard Configuration for T-Developer
Creates and manages CloudWatch dashboards for monitoring
"""

import boto3
import json
from datetime import datetime
from typing import Dict, List, Any


class CloudWatchDashboardManager:
    """Manage CloudWatch dashboards"""
    
    def __init__(self, region: str = 'us-east-1', environment: str = 'dev'):
        self.region = region
        self.environment = environment
        self.cloudwatch = boto3.client('cloudwatch', region_name=region)
        
    def create_main_dashboard(self) -> bool:
        """Create main monitoring dashboard"""
        
        dashboard_name = f'TDeveloper-{self.environment.capitalize()}-Main'
        
        dashboard_body = {
            "widgets": [
                # Agent Performance Metrics
                {
                    "type": "metric",
                    "x": 0,
                    "y": 0,
                    "width": 12,
                    "height": 6,
                    "properties": {
                        "metrics": [
                            ["TDeveloper", "AgentExecutions", {"stat": "Sum", "label": "Total Executions"}],
                            [".", "AgentSuccesses", {"stat": "Sum", "label": "Successful"}],
                            [".", "AgentFailures", {"stat": "Sum", "label": "Failed"}],
                            [".", "AgentTimeouts", {"stat": "Sum", "label": "Timeouts"}]
                        ],
                        "view": "timeSeries",
                        "stacked": False,
                        "region": self.region,
                        "title": "Agent Execution Status",
                        "period": 300,
                        "yAxis": {
                            "left": {
                                "min": 0
                            }
                        }
                    }
                },
                
                # AI Token Usage
                {
                    "type": "metric",
                    "x": 12,
                    "y": 0,
                    "width": 12,
                    "height": 6,
                    "properties": {
                        "metrics": [
                            ["TDeveloper", "AITokensUsed", {"stat": "Sum", "label": "Total Tokens"}],
                            [".", "OpenAITokens", {"stat": "Sum", "label": "OpenAI"}],
                            [".", "AnthropicTokens", {"stat": "Sum", "label": "Anthropic"}],
                            [".", "BedrockTokens", {"stat": "Sum", "label": "AWS Bedrock"}]
                        ],
                        "view": "timeSeries",
                        "stacked": True,
                        "region": self.region,
                        "title": "AI Token Usage",
                        "period": 300,
                        "yAxis": {
                            "left": {
                                "min": 0
                            }
                        }
                    }
                },
                
                # Evolution Metrics
                {
                    "type": "metric",
                    "x": 0,
                    "y": 6,
                    "width": 8,
                    "height": 6,
                    "properties": {
                        "metrics": [
                            ["TDeveloper", "EvolutionGeneration", {"stat": "Maximum", "label": "Current Generation"}],
                            [".", "EvolutionFitness", {"stat": "Average", "label": "Avg Fitness"}],
                            [".", "EvolutionBestFitness", {"stat": "Maximum", "label": "Best Fitness"}]
                        ],
                        "view": "timeSeries",
                        "stacked": False,
                        "region": self.region,
                        "title": "Evolution Progress",
                        "period": 3600,
                        "yAxis": {
                            "left": {
                                "min": 0,
                                "max": 1
                            }
                        }
                    }
                },
                
                # Workflow Execution
                {
                    "type": "metric",
                    "x": 8,
                    "y": 6,
                    "width": 8,
                    "height": 6,
                    "properties": {
                        "metrics": [
                            ["TDeveloper", "WorkflowExecutions", {"stat": "Sum"}],
                            [".", "WorkflowCompletions", {"stat": "Sum"}],
                            [".", "WorkflowFailures", {"stat": "Sum"}]
                        ],
                        "view": "timeSeries",
                        "stacked": False,
                        "region": self.region,
                        "title": "Workflow Execution Status",
                        "period": 300
                    }
                },
                
                # API Response Times
                {
                    "type": "metric",
                    "x": 16,
                    "y": 6,
                    "width": 8,
                    "height": 6,
                    "properties": {
                        "metrics": [
                            ["TDeveloper", "APIResponseTime", {"stat": "Average", "label": "Avg Response Time"}],
                            [".", ".", {"stat": "p95", "label": "P95"}],
                            [".", ".", {"stat": "p99", "label": "P99"}]
                        ],
                        "view": "timeSeries",
                        "stacked": False,
                        "region": self.region,
                        "title": "API Response Times (ms)",
                        "period": 300,
                        "yAxis": {
                            "left": {
                                "min": 0
                            }
                        }
                    }
                },
                
                # System Resources
                {
                    "type": "metric",
                    "x": 0,
                    "y": 12,
                    "width": 12,
                    "height": 6,
                    "properties": {
                        "metrics": [
                            ["AWS/ECS", "CPUUtilization", {"stat": "Average", "dimensions": {"ServiceName": f"t-developer-{self.environment}"}}],
                            [".", "MemoryUtilization", {"stat": "Average", "dimensions": {"ServiceName": f"t-developer-{self.environment}"}}]
                        ],
                        "view": "timeSeries",
                        "stacked": False,
                        "region": self.region,
                        "title": "ECS Resource Utilization",
                        "period": 300,
                        "yAxis": {
                            "left": {
                                "min": 0,
                                "max": 100
                            }
                        }
                    }
                },
                
                # Database Connections
                {
                    "type": "metric",
                    "x": 12,
                    "y": 12,
                    "width": 12,
                    "height": 6,
                    "properties": {
                        "metrics": [
                            ["AWS/RDS", "DatabaseConnections", {"stat": "Average", "dimensions": {"DBClusterIdentifier": f"t-developer-{self.environment}"}}],
                            [".", "CPUUtilization", {"stat": "Average", "dimensions": {"DBClusterIdentifier": f"t-developer-{self.environment}"}}],
                            [".", "FreeableMemory", {"stat": "Average", "dimensions": {"DBClusterIdentifier": f"t-developer-{self.environment}"}}]
                        ],
                        "view": "timeSeries",
                        "stacked": False,
                        "region": self.region,
                        "title": "Database Metrics",
                        "period": 300
                    }
                },
                
                # Error Rate
                {
                    "type": "metric",
                    "x": 0,
                    "y": 18,
                    "width": 8,
                    "height": 6,
                    "properties": {
                        "metrics": [
                            ["TDeveloper", "Errors", {"stat": "Sum"}],
                            [".", "Warnings", {"stat": "Sum"}]
                        ],
                        "view": "timeSeries",
                        "stacked": True,
                        "region": self.region,
                        "title": "Error and Warning Count",
                        "period": 300,
                        "yAxis": {
                            "left": {
                                "min": 0
                            }
                        }
                    }
                },
                
                # Cost Metrics
                {
                    "type": "metric",
                    "x": 8,
                    "y": 18,
                    "width": 8,
                    "height": 6,
                    "properties": {
                        "metrics": [
                            ["TDeveloper", "AICostUSD", {"stat": "Sum", "label": "AI API Costs"}],
                            [".", "ComputeCostUSD", {"stat": "Sum", "label": "Compute Costs"}],
                            [".", "StorageCostUSD", {"stat": "Sum", "label": "Storage Costs"}]
                        ],
                        "view": "timeSeries",
                        "stacked": True,
                        "region": self.region,
                        "title": "Cost Breakdown (USD)",
                        "period": 3600
                    }
                },
                
                # Active Users
                {
                    "type": "metric",
                    "x": 16,
                    "y": 18,
                    "width": 8,
                    "height": 6,
                    "properties": {
                        "metrics": [
                            ["TDeveloper", "ActiveUsers", {"stat": "Maximum"}],
                            [".", "UniqueUsers", {"stat": "Sum"}],
                            [".", "APIRequests", {"stat": "Sum"}]
                        ],
                        "view": "timeSeries",
                        "stacked": False,
                        "region": self.region,
                        "title": "User Activity",
                        "period": 300
                    }
                }
            ]
        }
        
        try:
            # Create or update dashboard
            response = self.cloudwatch.put_dashboard(
                DashboardName=dashboard_name,
                DashboardBody=json.dumps(dashboard_body)
            )
            
            print(f"✓ Created/Updated dashboard: {dashboard_name}")
            return True
            
        except Exception as e:
            print(f"✗ Failed to create dashboard: {e}")
            return False
    
    def create_alarms(self) -> Dict[str, bool]:
        """Create CloudWatch alarms"""
        
        alarms = [
            {
                'AlarmName': f't-developer-{self.environment}-high-error-rate',
                'ComparisonOperator': 'GreaterThanThreshold',
                'EvaluationPeriods': 2,
                'MetricName': 'Errors',
                'Namespace': 'TDeveloper',
                'Period': 300,
                'Statistic': 'Sum',
                'Threshold': 10.0,
                'ActionsEnabled': True,
                'AlarmDescription': 'Alarm when error rate is too high',
                'TreatMissingData': 'notBreaching'
            },
            {
                'AlarmName': f't-developer-{self.environment}-api-response-time',
                'ComparisonOperator': 'GreaterThanThreshold',
                'EvaluationPeriods': 3,
                'MetricName': 'APIResponseTime',
                'Namespace': 'TDeveloper',
                'Period': 300,
                'Statistic': 'Average',
                'Threshold': 1000.0,  # 1 second
                'ActionsEnabled': True,
                'AlarmDescription': 'Alarm when API response time exceeds 1 second',
                'TreatMissingData': 'notBreaching'
            },
            {
                'AlarmName': f't-developer-{self.environment}-evolution-stalled',
                'ComparisonOperator': 'LessThanThreshold',
                'EvaluationPeriods': 6,
                'MetricName': 'EvolutionGeneration',
                'Namespace': 'TDeveloper',
                'Period': 3600,
                'Statistic': 'Maximum',
                'Threshold': 1.0,
                'ActionsEnabled': True,
                'AlarmDescription': 'Alarm when evolution is not progressing',
                'TreatMissingData': 'breaching'
            },
            {
                'AlarmName': f't-developer-{self.environment}-high-ai-cost',
                'ComparisonOperator': 'GreaterThanThreshold',
                'EvaluationPeriods': 1,
                'MetricName': 'AICostUSD',
                'Namespace': 'TDeveloper',
                'Period': 3600,
                'Statistic': 'Sum',
                'Threshold': 100.0,  # $100 per hour
                'ActionsEnabled': True,
                'AlarmDescription': 'Alarm when AI costs exceed $100/hour',
                'TreatMissingData': 'notBreaching'
            }
        ]
        
        results = {}
        
        for alarm_config in alarms:
            try:
                self.cloudwatch.put_metric_alarm(**alarm_config)
                results[alarm_config['AlarmName']] = True
                print(f"✓ Created alarm: {alarm_config['AlarmName']}")
            except Exception as e:
                results[alarm_config['AlarmName']] = False
                print(f"✗ Failed to create alarm {alarm_config['AlarmName']}: {e}")
        
        return results
    
    def send_test_metrics(self) -> bool:
        """Send test metrics to CloudWatch"""
        
        try:
            # Send test metrics
            self.cloudwatch.put_metric_data(
                Namespace='TDeveloper',
                MetricData=[
                    {
                        'MetricName': 'AgentExecutions',
                        'Value': 10,
                        'Unit': 'Count',
                        'Timestamp': datetime.utcnow()
                    },
                    {
                        'MetricName': 'AgentSuccesses',
                        'Value': 8,
                        'Unit': 'Count',
                        'Timestamp': datetime.utcnow()
                    },
                    {
                        'MetricName': 'AgentFailures',
                        'Value': 2,
                        'Unit': 'Count',
                        'Timestamp': datetime.utcnow()
                    },
                    {
                        'MetricName': 'AITokensUsed',
                        'Value': 1500,
                        'Unit': 'Count',
                        'Timestamp': datetime.utcnow()
                    },
                    {
                        'MetricName': 'APIResponseTime',
                        'Value': 250,
                        'Unit': 'Milliseconds',
                        'Timestamp': datetime.utcnow()
                    }
                ]
            )
            
            print("✓ Test metrics sent successfully")
            return True
            
        except Exception as e:
            print(f"✗ Failed to send test metrics: {e}")
            return False


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Setup CloudWatch monitoring')
    parser.add_argument('--environment', '-e',
                       choices=['dev', 'staging', 'prod'],
                       default='dev',
                       help='Environment')
    parser.add_argument('--region', '-r',
                       default='us-east-1',
                       help='AWS region')
    parser.add_argument('--test-metrics', '-t',
                       action='store_true',
                       help='Send test metrics')
    
    args = parser.parse_args()
    
    # Initialize manager
    manager = CloudWatchDashboardManager(
        region=args.region,
        environment=args.environment
    )
    
    # Create dashboard
    print(f"Creating CloudWatch dashboard for {args.environment}...")
    dashboard_success = manager.create_main_dashboard()
    
    # Create alarms
    print(f"\nCreating CloudWatch alarms...")
    alarm_results = manager.create_alarms()
    
    # Send test metrics if requested
    if args.test_metrics:
        print(f"\nSending test metrics...")
        manager.send_test_metrics()
    
    # Summary
    successful_alarms = sum(1 for v in alarm_results.values() if v)
    print(f"\n{'='*50}")
    print(f"Dashboard created: {dashboard_success}")
    print(f"Alarms created: {successful_alarms}/{len(alarm_results)}")


if __name__ == "__main__":
    main()