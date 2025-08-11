"""
T-Developer Monitoring Setup
Configures comprehensive monitoring for the 9-agent pipeline
"""

import logging
import boto3
import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class AlarmConfiguration:
    """CloudWatch alarm configuration"""
    name: str
    description: str
    metric_name: str
    namespace: str
    statistic: str
    period: int
    evaluation_periods: int
    threshold: float
    comparison_operator: str
    dimensions: Dict[str, str]
    alarm_actions: List[str]

class MonitoringSetup:
    """Setup comprehensive monitoring for T-Developer"""
    
    def __init__(self, environment: str = 'production', region: str = 'us-east-1'):
        self.environment = environment
        self.region = region
        
        # AWS clients
        self.cloudwatch = boto3.client('cloudwatch', region_name=region)
        self.sns = boto3.client('sns', region_name=region)
        self.logs = boto3.client('logs', region_name=region)
        
        # Resource names
        self.cluster_name = f't-developer-cluster-{environment}'
        self.service_name = f't-developer-service-{environment}'
        self.alb_name = f't-developer-alb-{environment}'
        self.sns_topic_name = f't-developer-alerts-{environment}'
        
    def setup_complete_monitoring(self) -> Dict[str, Any]:
        """Setup complete monitoring stack"""
        
        results = {}
        
        try:
            # Create SNS topic for alerts
            topic_arn = self._create_sns_topic()
            results['sns_topic'] = topic_arn
            
            # Create CloudWatch alarms
            alarms = self._create_cloudwatch_alarms(topic_arn)
            results['alarms'] = alarms
            
            # Create custom dashboard
            dashboard_name = self._create_dashboard()
            results['dashboard'] = dashboard_name
            
            # Setup log insights queries
            queries = self._setup_log_insights()
            results['log_queries'] = queries
            
            # Create custom metrics
            self._setup_custom_metrics()
            results['custom_metrics'] = True
            
            logger.info(f"Monitoring setup completed for {self.environment}")
            return results
            
        except Exception as e:
            logger.error(f"Monitoring setup failed: {e}")
            raise
    
    def _create_sns_topic(self) -> str:
        """Create SNS topic for alerts"""
        
        try:
            response = self.sns.create_topic(Name=self.sns_topic_name)
            topic_arn = response['TopicArn']
            
            # Set topic attributes
            self.sns.set_topic_attributes(
                TopicArn=topic_arn,
                AttributeName='DisplayName',
                AttributeValue=f'T-Developer {self.environment.title()} Alerts'
            )
            
            logger.info(f"Created SNS topic: {topic_arn}")
            return topic_arn
            
        except self.sns.exceptions.TopicLimitExceededException:
            # Topic might already exist
            topics = self.sns.list_topics()['Topics']
            for topic in topics:
                if self.sns_topic_name in topic['TopicArn']:
                    return topic['TopicArn']
            raise
    
    def _create_cloudwatch_alarms(self, topic_arn: str) -> List[str]:
        """Create comprehensive CloudWatch alarms"""
        
        alarm_configs = [
            # ECS Service alarms
            AlarmConfiguration(
                name=f't-developer-high-cpu-{self.environment}',
                description='High CPU utilization on ECS service',
                metric_name='CPUUtilization',
                namespace='AWS/ECS',
                statistic='Average',
                period=300,
                evaluation_periods=2,
                threshold=75.0,
                comparison_operator='GreaterThanThreshold',
                dimensions={
                    'ServiceName': self.service_name,
                    'ClusterName': self.cluster_name
                },
                alarm_actions=[topic_arn]
            ),
            
            AlarmConfiguration(
                name=f't-developer-high-memory-{self.environment}',
                description='High memory utilization on ECS service',
                metric_name='MemoryUtilization',
                namespace='AWS/ECS',
                statistic='Average',
                period=300,
                evaluation_periods=2,
                threshold=80.0,
                comparison_operator='GreaterThanThreshold',
                dimensions={
                    'ServiceName': self.service_name,
                    'ClusterName': self.cluster_name
                },
                alarm_actions=[topic_arn]
            ),
            
            AlarmConfiguration(
                name=f't-developer-service-unavailable-{self.environment}',
                description='ECS service has no running tasks',
                metric_name='RunningTaskCount',
                namespace='AWS/ECS',
                statistic='Average',
                period=60,
                evaluation_periods=2,
                threshold=1.0,
                comparison_operator='LessThanThreshold',
                dimensions={
                    'ServiceName': self.service_name,
                    'ClusterName': self.cluster_name
                },
                alarm_actions=[topic_arn]
            ),
            
            # Application Load Balancer alarms
            AlarmConfiguration(
                name=f't-developer-high-response-time-{self.environment}',
                description='High response time on load balancer',
                metric_name='TargetResponseTime',
                namespace='AWS/ApplicationELB',
                statistic='Average',
                period=300,
                evaluation_periods=2,
                threshold=2.0,
                comparison_operator='GreaterThanThreshold',
                dimensions={
                    'LoadBalancer': f'app/{self.alb_name}'
                },
                alarm_actions=[topic_arn]
            ),
            
            AlarmConfiguration(
                name=f't-developer-high-error-rate-{self.environment}',
                description='High 5xx error rate',
                metric_name='HTTPCode_Target_5XX_Count',
                namespace='AWS/ApplicationELB',
                statistic='Sum',
                period=300,
                evaluation_periods=2,
                threshold=10.0,
                comparison_operator='GreaterThanThreshold',
                dimensions={
                    'LoadBalancer': f'app/{self.alb_name}'
                },
                alarm_actions=[topic_arn]
            ),
            
            # Custom pipeline alarms
            AlarmConfiguration(
                name=f't-developer-high-failure-rate-{self.environment}',
                description='High pipeline failure rate',
                metric_name='GenerationFailureRate',
                namespace='T-Developer/Pipeline',
                statistic='Average',
                period=600,
                evaluation_periods=2,
                threshold=0.1,  # 10% failure rate
                comparison_operator='GreaterThanThreshold',
                dimensions={
                    'Environment': self.environment
                },
                alarm_actions=[topic_arn]
            ),
            
            AlarmConfiguration(
                name=f't-developer-slow-pipeline-{self.environment}',
                description='Pipeline execution time is too slow',
                metric_name='PipelineExecutionTime',
                namespace='T-Developer/Pipeline',
                statistic='Average',
                period=600,
                evaluation_periods=2,
                threshold=60.0,  # 60 seconds
                comparison_operator='GreaterThanThreshold',
                dimensions={
                    'Environment': self.environment
                },
                alarm_actions=[topic_arn]
            )
        ]
        
        created_alarms = []
        
        for config in alarm_configs:
            try:
                # Convert dimensions to CloudWatch format
                dimensions = [
                    {'Name': key, 'Value': value}
                    for key, value in config.dimensions.items()
                ]
                
                self.cloudwatch.put_metric_alarm(
                    AlarmName=config.name,
                    AlarmDescription=config.description,
                    ActionsEnabled=True,
                    AlarmActions=config.alarm_actions,
                    MetricName=config.metric_name,
                    Namespace=config.namespace,
                    Statistic=config.statistic,
                    Dimensions=dimensions,
                    Period=config.period,
                    EvaluationPeriods=config.evaluation_periods,
                    Threshold=config.threshold,
                    ComparisonOperator=config.comparison_operator,
                    TreatMissingData='notBreaching'
                )
                
                created_alarms.append(config.name)
                logger.info(f"Created alarm: {config.name}")
                
            except Exception as e:
                logger.error(f"Failed to create alarm {config.name}: {e}")
        
        return created_alarms
    
    def _create_dashboard(self) -> str:
        """Create CloudWatch dashboard"""
        
        dashboard_name = f't-developer-dashboard-{self.environment}'
        
        # Load dashboard configuration
        dashboard_file = os.path.join(
            os.path.dirname(__file__),
            'cloudwatch-dashboard.json'
        )
        
        with open(dashboard_file, 'r') as f:
            dashboard_body = f.read()
        
        # Replace placeholders with actual resource names
        dashboard_body = dashboard_body.replace(
            't-developer-service-production',
            self.service_name
        ).replace(
            't-developer-cluster-production',
            self.cluster_name
        ).replace(
            't-developer-alb-production',
            self.alb_name
        ).replace(
            't-developer-projects-production',
            f't-developer-projects-{self.environment}'
        ).replace(
            't-developer-metadata-production',
            f't-developer-metadata-{self.environment}'
        )
        
        try:
            self.cloudwatch.put_dashboard(
                DashboardName=dashboard_name,
                DashboardBody=dashboard_body
            )
            
            logger.info(f"Created dashboard: {dashboard_name}")
            return dashboard_name
            
        except Exception as e:
            logger.error(f"Failed to create dashboard: {e}")
            raise
    
    def _setup_log_insights(self) -> List[str]:
        """Setup CloudWatch Log Insights queries"""
        
        queries = [
            {
                'name': 'Pipeline Errors',
                'query': '''
                    fields @timestamp, @message
                    | filter @message like /ERROR/
                    | filter @message like /pipeline/
                    | sort @timestamp desc
                    | limit 100
                '''
            },
            {
                'name': 'Slow Agents',
                'query': '''
                    fields @timestamp, @message
                    | filter @message like /execution_time/
                    | parse @message /execution_time:(?<exec_time>\d+\.?\d*)/
                    | filter exec_time > 10
                    | sort @timestamp desc
                '''
            },
            {
                'name': 'Agent Failures',
                'query': '''
                    fields @timestamp, @message
                    | filter @message like /Agent.*failed/
                    | sort @timestamp desc
                    | limit 50
                '''
            },
            {
                'name': 'Cache Performance',
                'query': '''
                    fields @timestamp, @message
                    | filter @message like /cache/
                    | parse @message /cache_hit_rate:(?<hit_rate>\d+\.?\d*)/
                    | stats avg(hit_rate) by bin(5m)
                '''
            },
            {
                'name': 'Memory Usage Tracking',
                'query': '''
                    fields @timestamp, @message
                    | filter @message like /memory_usage/
                    | parse @message /memory_usage:(?<memory>\d+)/
                    | sort @timestamp desc
                '''
            }
        ]
        
        created_queries = []
        
        for query_info in queries:
            # Store query as CloudWatch Insights saved query
            # Note: This requires additional AWS CLI or SDK setup
            created_queries.append(query_info['name'])
            logger.info(f"Query template ready: {query_info['name']}")
        
        return created_queries
    
    def _setup_custom_metrics(self) -> None:
        """Setup custom CloudWatch metrics for the pipeline"""
        
        # Create custom metric namespace
        namespace = 'T-Developer/Pipeline'
        
        # Sample custom metrics to create
        custom_metrics = [
            'GenerationRequests',
            'GenerationSuccess',
            'GenerationFailures',
            'GenerationFailureRate',
            'PipelineExecutionTime',
            'NLInputExecutionTime',
            'UISelectionExecutionTime',
            'ParserExecutionTime',
            'ComponentDecisionExecutionTime',
            'MatchRateExecutionTime',
            'SearchExecutionTime',
            'GenerationExecutionTime',
            'AssemblyExecutionTime',
            'DownloadExecutionTime',
            'CacheHitRate',
            'CacheMissRate',
            'UserSatisfactionScore',
            'ProjectsGenerated',
            'ActiveUsers',
            'AverageProjectSize'
        ]
        
        # Initialize metrics with zero values
        for metric_name in custom_metrics:
            try:
                self.cloudwatch.put_metric_data(
                    Namespace=namespace,
                    MetricData=[
                        {
                            'MetricName': metric_name,
                            'Value': 0.0,
                            'Unit': 'Count',
                            'Dimensions': [
                                {
                                    'Name': 'Environment',
                                    'Value': self.environment
                                }
                            ]
                        }
                    ]
                )
            except Exception as e:
                logger.warning(f"Failed to initialize metric {metric_name}: {e}")
        
        logger.info(f"Custom metrics setup completed for namespace: {namespace}")
    
    def create_composite_alarms(self, topic_arn: str) -> List[str]:
        """Create composite alarms for complex monitoring scenarios"""
        
        composite_alarms = []
        
        # Service Health Composite Alarm
        service_health_alarm = f't-developer-service-unhealthy-{self.environment}'
        
        try:
            self.cloudwatch.put_composite_alarm(
                AlarmName=service_health_alarm,
                AlarmDescription='T-Developer service is unhealthy',
                AlarmRule=f'(ALARM("{self.service_name}-high-cpu-{self.environment}") OR '
                         f'ALARM("{self.service_name}-high-memory-{self.environment}") OR '
                         f'ALARM("{self.service_name}-service-unavailable-{self.environment}"))',
                ActionsEnabled=True,
                AlarmActions=[topic_arn],
                InsufficientDataActions=[topic_arn],
                OKActions=[]
            )
            
            composite_alarms.append(service_health_alarm)
            logger.info(f"Created composite alarm: {service_health_alarm}")
            
        except Exception as e:
            logger.error(f"Failed to create composite alarm: {e}")
        
        return composite_alarms
    
    def setup_anomaly_detection(self) -> List[str]:
        """Setup CloudWatch Anomaly Detection"""
        
        anomaly_detectors = []
        
        # Anomaly detectors for key metrics
        metrics_for_anomaly = [
            {
                'namespace': 'AWS/ApplicationELB',
                'metric_name': 'RequestCount',
                'dimensions': [{'Name': 'LoadBalancer', 'Value': f'app/{self.alb_name}'}]
            },
            {
                'namespace': 'T-Developer/Pipeline',
                'metric_name': 'GenerationRequests',
                'dimensions': [{'Name': 'Environment', 'Value': self.environment}]
            },
            {
                'namespace': 'T-Developer/Pipeline',
                'metric_name': 'PipelineExecutionTime',
                'dimensions': [{'Name': 'Environment', 'Value': self.environment}]
            }
        ]
        
        for metric_config in metrics_for_anomaly:
            try:
                detector_name = f"{metric_config['namespace']}-{metric_config['metric_name']}-anomaly"
                
                self.cloudwatch.put_anomaly_detector(
                    Namespace=metric_config['namespace'],
                    MetricName=metric_config['metric_name'],
                    Dimensions=metric_config['dimensions'],
                    Stat='Average'
                )
                
                anomaly_detectors.append(detector_name)
                logger.info(f"Created anomaly detector: {detector_name}")
                
            except Exception as e:
                logger.error(f"Failed to create anomaly detector: {e}")
        
        return anomaly_detectors

def main():
    """Main function to setup monitoring"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description='Setup T-Developer monitoring')
    parser.add_argument('--environment', default='production', 
                       choices=['development', 'staging', 'production'],
                       help='Target environment')
    parser.add_argument('--region', default='us-east-1',
                       help='AWS region')
    parser.add_argument('--email', help='Email address for SNS notifications')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create monitoring setup
    monitor = MonitoringSetup(
        environment=args.environment,
        region=args.region
    )
    
    try:
        # Setup complete monitoring
        results = monitor.setup_complete_monitoring()
        
        # Subscribe email to SNS topic if provided
        if args.email:
            topic_arn = results.get('sns_topic')
            if topic_arn:
                monitor.sns.subscribe(
                    TopicArn=topic_arn,
                    Protocol='email',
                    Endpoint=args.email
                )
                logger.info(f"Subscribed {args.email} to SNS topic")
        
        # Setup additional features
        if results.get('sns_topic'):
            composite_alarms = monitor.create_composite_alarms(results['sns_topic'])
            results['composite_alarms'] = composite_alarms
        
        anomaly_detectors = monitor.setup_anomaly_detection()
        results['anomaly_detectors'] = anomaly_detectors
        
        # Print summary
        print("\n" + "="*60)
        print(f"T-Developer Monitoring Setup Complete - {args.environment.upper()}")
        print("="*60)
        print(f"SNS Topic: {results.get('sns_topic', 'Not created')}")
        print(f"Alarms Created: {len(results.get('alarms', []))}")
        print(f"Dashboard: {results.get('dashboard', 'Not created')}")
        print(f"Log Queries: {len(results.get('log_queries', []))}")
        print(f"Custom Metrics: {'Enabled' if results.get('custom_metrics') else 'Disabled'}")
        print(f"Composite Alarms: {len(results.get('composite_alarms', []))}")
        print(f"Anomaly Detectors: {len(results.get('anomaly_detectors', []))}")
        print("\nMonitoring dashboard available at:")
        print(f"https://{args.region}.console.aws.amazon.com/cloudwatch/home?region={args.region}#dashboards:name={results.get('dashboard', '')}")
        print("="*60)
        
    except Exception as e:
        logger.error(f"Monitoring setup failed: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())