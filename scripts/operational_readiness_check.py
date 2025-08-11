#!/usr/bin/env python3
"""
T-Developer Operational Readiness Check
Comprehensive validation of production readiness
"""

import logging
import boto3
import json
import os
import sys
import subprocess
import requests
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import concurrent.futures

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class CheckResult:
    """Individual check result"""
    name: str
    passed: bool
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    severity: str = "medium"  # low, medium, high, critical

@dataclass
class ReadinessReport:
    """Overall readiness report"""
    timestamp: datetime
    environment: str
    overall_status: str
    checks: List[CheckResult]
    recommendations: List[str]
    score: float

class OperationalReadinessChecker:
    """Comprehensive operational readiness checker"""
    
    def __init__(self, environment: str = 'production', region: str = 'us-east-1'):
        self.environment = environment
        self.region = region
        
        # AWS clients
        self.ecs = boto3.client('ecs', region_name=region)
        self.cloudwatch = boto3.client('cloudwatch', region_name=region)
        self.elbv2 = boto3.client('elbv2', region_name=region)
        self.s3 = boto3.client('s3', region_name=region)
        self.dynamodb = boto3.client('dynamodb', region_name=region)
        self.logs = boto3.client('logs', region_name=region)
        self.secretsmanager = boto3.client('secretsmanager', region_name=region)
        
        # Resource names
        self.cluster_name = f't-developer-cluster-{environment}'
        self.service_name = f't-developer-service-{environment}'
        self.bucket_name = f't-developer-projects-{environment}'
        self.table_name = f't-developer-metadata-{environment}'
        
        self.checks: List[CheckResult] = []
    
    def run_comprehensive_check(self) -> ReadinessReport:
        """Run all operational readiness checks"""
        
        logger.info(f"Starting operational readiness check for {self.environment}")
        start_time = time.time()
        
        # List of all check methods
        check_methods = [
            self.check_ecs_service_health,
            self.check_load_balancer_health,
            self.check_database_health,
            self.check_storage_health,
            self.check_monitoring_setup,
            self.check_security_configuration,
            self.check_backup_configuration,
            self.check_api_endpoints,
            self.check_performance_baselines,
            self.check_disaster_recovery,
            self.check_documentation,
            self.check_operational_procedures
        ]
        
        # Run checks in parallel where possible
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(check_method) for check_method in check_methods]
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result(timeout=30)
                    if result:
                        self.checks.append(result)
                except Exception as e:
                    logger.error(f"Check failed: {e}")
                    self.checks.append(CheckResult(
                        name="Unknown Check",
                        passed=False,
                        message=f"Check execution failed: {str(e)}",
                        severity="high"
                    ))
        
        # Generate report
        report = self._generate_report()
        
        execution_time = time.time() - start_time
        logger.info(f"Readiness check completed in {execution_time:.2f} seconds")
        
        return report
    
    def check_ecs_service_health(self) -> CheckResult:
        """Check ECS service health and configuration"""
        
        try:
            response = self.ecs.describe_services(
                cluster=self.cluster_name,
                services=[self.service_name]
            )
            
            if not response['services']:
                return CheckResult(
                    name="ECS Service Health",
                    passed=False,
                    message="ECS service not found",
                    severity="critical"
                )
            
            service = response['services'][0]
            
            # Check service status
            if service['status'] != 'ACTIVE':
                return CheckResult(
                    name="ECS Service Health",
                    passed=False,
                    message=f"Service status is {service['status']}, expected ACTIVE",
                    details={'status': service['status']},
                    severity="critical"
                )
            
            # Check running tasks
            running_count = service['runningCount']
            desired_count = service['desiredCount']
            
            if running_count < desired_count:
                return CheckResult(
                    name="ECS Service Health",
                    passed=False,
                    message=f"Only {running_count}/{desired_count} tasks running",
                    details={
                        'running_count': running_count,
                        'desired_count': desired_count
                    },
                    severity="high"
                )
            
            # Check deployment status
            deployments = service['deployments']
            primary_deployment = next(
                (d for d in deployments if d['status'] == 'PRIMARY'), None
            )
            
            if not primary_deployment or primary_deployment['runningCount'] != primary_deployment['desiredCount']:
                return CheckResult(
                    name="ECS Service Health",
                    passed=False,
                    message="Service deployment is not stable",
                    details={'deployments': len(deployments)},
                    severity="medium"
                )
            
            return CheckResult(
                name="ECS Service Health",
                passed=True,
                message=f"Service healthy: {running_count} tasks running",
                details={
                    'running_count': running_count,
                    'desired_count': desired_count,
                    'cpu': service['taskDefinition'].split('/')[-1]
                }
            )
            
        except Exception as e:
            return CheckResult(
                name="ECS Service Health",
                passed=False,
                message=f"Failed to check ECS service: {str(e)}",
                severity="critical"
            )
    
    def check_load_balancer_health(self) -> CheckResult:
        """Check load balancer health and target groups"""
        
        try:
            # List load balancers
            response = self.elbv2.describe_load_balancers()
            alb = None
            
            for lb in response['LoadBalancers']:
                if f't-developer-alb-{self.environment}' in lb['LoadBalancerName']:
                    alb = lb
                    break
            
            if not alb:
                return CheckResult(
                    name="Load Balancer Health",
                    passed=False,
                    message="Application Load Balancer not found",
                    severity="critical"
                )
            
            # Check ALB state
            if alb['State']['Code'] != 'active':
                return CheckResult(
                    name="Load Balancer Health",
                    passed=False,
                    message=f"Load balancer state is {alb['State']['Code']}",
                    details={'state': alb['State']},
                    severity="critical"
                )
            
            # Check target groups
            target_groups = self.elbv2.describe_target_groups(
                LoadBalancerArn=alb['LoadBalancerArn']
            )
            
            healthy_targets = 0
            total_targets = 0
            
            for tg in target_groups['TargetGroups']:
                health = self.elbv2.describe_target_health(
                    TargetGroupArn=tg['TargetGroupArn']
                )
                
                for target in health['TargetHealthDescriptions']:
                    total_targets += 1
                    if target['TargetHealth']['State'] == 'healthy':
                        healthy_targets += 1
            
            if healthy_targets == 0:
                return CheckResult(
                    name="Load Balancer Health",
                    passed=False,
                    message="No healthy targets in target groups",
                    details={'healthy': healthy_targets, 'total': total_targets},
                    severity="critical"
                )
            
            if healthy_targets < total_targets:
                return CheckResult(
                    name="Load Balancer Health",
                    passed=False,
                    message=f"Only {healthy_targets}/{total_targets} targets healthy",
                    details={'healthy': healthy_targets, 'total': total_targets},
                    severity="medium"
                )
            
            return CheckResult(
                name="Load Balancer Health",
                passed=True,
                message=f"Load balancer healthy: {healthy_targets} targets",
                details={
                    'dns_name': alb['DNSName'],
                    'healthy_targets': healthy_targets,
                    'total_targets': total_targets
                }
            )
            
        except Exception as e:
            return CheckResult(
                name="Load Balancer Health",
                passed=False,
                message=f"Failed to check load balancer: {str(e)}",
                severity="critical"
            )
    
    def check_database_health(self) -> CheckResult:
        """Check DynamoDB health and configuration"""
        
        try:
            response = self.dynamodb.describe_table(TableName=self.table_name)
            table = response['Table']
            
            # Check table status
            if table['TableStatus'] != 'ACTIVE':
                return CheckResult(
                    name="Database Health",
                    passed=False,
                    message=f"DynamoDB table status is {table['TableStatus']}",
                    details={'status': table['TableStatus']},
                    severity="critical"
                )
            
            # Check encryption
            if 'SSEDescription' not in table:
                return CheckResult(
                    name="Database Health",
                    passed=False,
                    message="DynamoDB table is not encrypted",
                    severity="high"
                )
            
            # Check point-in-time recovery
            backup_desc = self.dynamodb.describe_continuous_backups(
                TableName=self.table_name
            )
            
            pitr_enabled = backup_desc['ContinuousBackupsDescription']['PointInTimeRecoveryDescription']['PointInTimeRecoveryStatus'] == 'ENABLED'
            
            if not pitr_enabled:
                return CheckResult(
                    name="Database Health",
                    passed=False,
                    message="Point-in-time recovery is not enabled",
                    severity="medium"
                )
            
            # Test basic operations
            try:
                self.dynamodb.scan(
                    TableName=self.table_name,
                    Limit=1
                )
            except Exception as e:
                return CheckResult(
                    name="Database Health",
                    passed=False,
                    message=f"Database read test failed: {str(e)}",
                    severity="high"
                )
            
            return CheckResult(
                name="Database Health",
                passed=True,
                message="DynamoDB table healthy and properly configured",
                details={
                    'status': table['TableStatus'],
                    'encryption': 'SSEDescription' in table,
                    'pitr_enabled': pitr_enabled,
                    'item_count': table.get('ItemCount', 0)
                }
            )
            
        except Exception as e:
            return CheckResult(
                name="Database Health",
                passed=False,
                message=f"Failed to check database: {str(e)}",
                severity="critical"
            )
    
    def check_storage_health(self) -> CheckResult:
        """Check S3 bucket health and configuration"""
        
        try:
            # Check bucket exists and is accessible
            self.s3.head_bucket(Bucket=self.bucket_name)
            
            # Check encryption
            try:
                encryption = self.s3.get_bucket_encryption(Bucket=self.bucket_name)
                encrypted = True
            except self.s3.exceptions.ClientError as e:
                if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
                    encrypted = False
                else:
                    raise
            
            if not encrypted:
                return CheckResult(
                    name="Storage Health",
                    passed=False,
                    message="S3 bucket is not encrypted",
                    severity="high"
                )
            
            # Check versioning
            versioning = self.s3.get_bucket_versioning(Bucket=self.bucket_name)
            versioning_enabled = versioning.get('Status') == 'Enabled'
            
            if not versioning_enabled:
                return CheckResult(
                    name="Storage Health",
                    passed=False,
                    message="S3 bucket versioning is not enabled",
                    severity="medium"
                )
            
            # Check lifecycle policy
            try:
                lifecycle = self.s3.get_bucket_lifecycle_configuration(Bucket=self.bucket_name)
                lifecycle_configured = True
            except self.s3.exceptions.ClientError as e:
                if e.response['Error']['Code'] == 'NoSuchLifecycleConfiguration':
                    lifecycle_configured = False
                else:
                    raise
            
            # Get bucket size
            response = self.s3.list_objects_v2(Bucket=self.bucket_name, MaxKeys=1)
            object_count = response.get('KeyCount', 0)
            
            return CheckResult(
                name="Storage Health",
                passed=True,
                message="S3 bucket healthy and properly configured",
                details={
                    'encrypted': encrypted,
                    'versioning_enabled': versioning_enabled,
                    'lifecycle_configured': lifecycle_configured,
                    'object_count': object_count
                }
            )
            
        except Exception as e:
            return CheckResult(
                name="Storage Health",
                passed=False,
                message=f"Failed to check S3 bucket: {str(e)}",
                severity="critical"
            )
    
    def check_monitoring_setup(self) -> CheckResult:
        """Check CloudWatch monitoring setup"""
        
        try:
            # Check alarms
            alarms = self.cloudwatch.describe_alarms(
                AlarmNamePrefix=f't-developer-{self.environment}'
            )
            
            alarm_count = len(alarms['MetricAlarms'])
            
            if alarm_count == 0:
                return CheckResult(
                    name="Monitoring Setup",
                    passed=False,
                    message="No CloudWatch alarms configured",
                    severity="high"
                )
            
            # Check alarm states
            alarm_states = {}
            for alarm in alarms['MetricAlarms']:
                alarm_states[alarm['StateValue']] = alarm_states.get(alarm['StateValue'], 0) + 1
            
            # Check dashboard
            try:
                dashboards = self.cloudwatch.list_dashboards(
                    DashboardNamePrefix=f't-developer-dashboard-{self.environment}'
                )
                dashboard_exists = len(dashboards['DashboardEntries']) > 0
            except Exception:
                dashboard_exists = False
            
            # Check log groups
            log_groups = self.logs.describe_log_groups(
                logGroupNamePrefix='/ecs/t-developer'
            )
            log_group_count = len(log_groups['logGroups'])
            
            return CheckResult(
                name="Monitoring Setup",
                passed=True,
                message=f"Monitoring configured: {alarm_count} alarms, dashboard: {dashboard_exists}",
                details={
                    'alarm_count': alarm_count,
                    'alarm_states': alarm_states,
                    'dashboard_exists': dashboard_exists,
                    'log_groups': log_group_count
                }
            )
            
        except Exception as e:
            return CheckResult(
                name="Monitoring Setup",
                passed=False,
                message=f"Failed to check monitoring: {str(e)}",
                severity="high"
            )
    
    def check_security_configuration(self) -> CheckResult:
        """Check security configuration"""
        
        issues = []
        details = {}
        
        try:
            # Check secrets management
            try:
                secrets = self.secretsmanager.list_secrets()
                secret_count = len([
                    s for s in secrets['SecretList'] 
                    if 't-developer' in s['Name'] and self.environment in s['Name']
                ])
                details['secrets_configured'] = secret_count > 0
                
                if secret_count == 0:
                    issues.append("No secrets configured in Secrets Manager")
                    
            except Exception as e:
                issues.append(f"Failed to check secrets: {str(e)}")
            
            # Check ECS task execution role
            try:
                task_def = self.ecs.describe_task_definition(
                    taskDefinition=f'{self.service_name}:ACTIVE'
                )
                
                execution_role = task_def['taskDefinition'].get('executionRoleArn')
                task_role = task_def['taskDefinition'].get('taskRoleArn')
                
                details['execution_role_configured'] = execution_role is not None
                details['task_role_configured'] = task_role is not None
                
                if not execution_role:
                    issues.append("No execution role configured for ECS tasks")
                if not task_role:
                    issues.append("No task role configured for ECS tasks")
                    
            except Exception as e:
                issues.append(f"Failed to check IAM roles: {str(e)}")
            
            if issues:
                return CheckResult(
                    name="Security Configuration",
                    passed=False,
                    message=f"Security issues found: {', '.join(issues)}",
                    details=details,
                    severity="high"
                )
            
            return CheckResult(
                name="Security Configuration",
                passed=True,
                message="Security configuration validated",
                details=details
            )
            
        except Exception as e:
            return CheckResult(
                name="Security Configuration",
                passed=False,
                message=f"Failed security check: {str(e)}",
                severity="high"
            )
    
    def check_backup_configuration(self) -> CheckResult:
        """Check backup and disaster recovery configuration"""
        
        details = {}
        issues = []
        
        try:
            # Check DynamoDB backups
            backups = self.dynamodb.list_backups(TableName=self.table_name)
            backup_count = len(backups['BackupSummaries'])
            details['dynamodb_backups'] = backup_count
            
            if backup_count == 0:
                issues.append("No DynamoDB backups found")
            
            # Check S3 versioning (already checked in storage health)
            versioning = self.s3.get_bucket_versioning(Bucket=self.bucket_name)
            versioning_enabled = versioning.get('Status') == 'Enabled'
            details['s3_versioning'] = versioning_enabled
            
            if not versioning_enabled:
                issues.append("S3 versioning not enabled")
            
            # Check lifecycle policies
            try:
                lifecycle = self.s3.get_bucket_lifecycle_configuration(Bucket=self.bucket_name)
                lifecycle_rules = len(lifecycle['Rules'])
                details['lifecycle_rules'] = lifecycle_rules
            except self.s3.exceptions.ClientError:
                details['lifecycle_rules'] = 0
                issues.append("No S3 lifecycle policies configured")
            
            if issues:
                return CheckResult(
                    name="Backup Configuration",
                    passed=False,
                    message=f"Backup issues: {', '.join(issues)}",
                    details=details,
                    severity="medium"
                )
            
            return CheckResult(
                name="Backup Configuration",
                passed=True,
                message="Backup configuration validated",
                details=details
            )
            
        except Exception as e:
            return CheckResult(
                name="Backup Configuration",
                passed=False,
                message=f"Failed backup check: {str(e)}",
                severity="medium"
            )
    
    def check_api_endpoints(self) -> CheckResult:
        """Check API endpoint health"""
        
        try:
            # Get load balancer DNS
            albs = self.elbv2.describe_load_balancers()
            alb_dns = None
            
            for lb in albs['LoadBalancers']:
                if f't-developer-alb-{self.environment}' in lb['LoadBalancerName']:
                    alb_dns = lb['DNSName']
                    break
            
            if not alb_dns:
                return CheckResult(
                    name="API Endpoints",
                    passed=False,
                    message="Could not find load balancer DNS",
                    severity="critical"
                )
            
            base_url = f"http://{alb_dns}"
            endpoints_to_test = [
                "/health",
                "/api/v1/status"
            ]
            
            results = {}
            
            for endpoint in endpoints_to_test:
                try:
                    response = requests.get(
                        f"{base_url}{endpoint}",
                        timeout=10
                    )
                    results[endpoint] = {
                        'status_code': response.status_code,
                        'response_time': response.elapsed.total_seconds(),
                        'healthy': response.status_code == 200
                    }
                except requests.exceptions.RequestException as e:
                    results[endpoint] = {
                        'status_code': None,
                        'response_time': None,
                        'healthy': False,
                        'error': str(e)
                    }
            
            healthy_endpoints = sum(1 for r in results.values() if r['healthy'])
            total_endpoints = len(results)
            
            if healthy_endpoints == 0:
                return CheckResult(
                    name="API Endpoints",
                    passed=False,
                    message="No API endpoints responding",
                    details=results,
                    severity="critical"
                )
            
            if healthy_endpoints < total_endpoints:
                return CheckResult(
                    name="API Endpoints",
                    passed=False,
                    message=f"Only {healthy_endpoints}/{total_endpoints} endpoints healthy",
                    details=results,
                    severity="high"
                )
            
            avg_response_time = sum(
                r['response_time'] for r in results.values() 
                if r['response_time'] is not None
            ) / healthy_endpoints
            
            return CheckResult(
                name="API Endpoints",
                passed=True,
                message=f"All {total_endpoints} endpoints healthy (avg {avg_response_time:.2f}s)",
                details=results
            )
            
        except Exception as e:
            return CheckResult(
                name="API Endpoints",
                passed=False,
                message=f"Failed to check API endpoints: {str(e)}",
                severity="critical"
            )
    
    def check_performance_baselines(self) -> CheckResult:
        """Check performance baselines are met"""
        
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=1)
            
            # Check average response time
            response_time_metrics = self.cloudwatch.get_metric_statistics(
                Namespace='AWS/ApplicationELB',
                MetricName='TargetResponseTime',
                Dimensions=[
                    {
                        'Name': 'LoadBalancer',
                        'Value': f'app/t-developer-alb-{self.environment}'
                    }
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,
                Statistics=['Average']
            )
            
            if response_time_metrics['Datapoints']:
                avg_response_time = sum(
                    dp['Average'] for dp in response_time_metrics['Datapoints']
                ) / len(response_time_metrics['Datapoints'])
            else:
                avg_response_time = 0
            
            # Check error rate
            error_metrics = self.cloudwatch.get_metric_statistics(
                Namespace='AWS/ApplicationELB',
                MetricName='HTTPCode_Target_5XX_Count',
                Dimensions=[
                    {
                        'Name': 'LoadBalancer',
                        'Value': f'app/t-developer-alb-{self.environment}'
                    }
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,
                Statistics=['Sum']
            )
            
            total_errors = sum(
                dp['Sum'] for dp in error_metrics['Datapoints']
            ) if error_metrics['Datapoints'] else 0
            
            # SLO thresholds
            max_response_time = 2.0  # 2 seconds
            max_error_count = 10
            
            issues = []
            if avg_response_time > max_response_time:
                issues.append(f"High response time: {avg_response_time:.2f}s > {max_response_time}s")
            
            if total_errors > max_error_count:
                issues.append(f"High error count: {total_errors} > {max_error_count}")
            
            details = {
                'avg_response_time': avg_response_time,
                'total_errors': total_errors,
                'slo_response_time': max_response_time,
                'slo_max_errors': max_error_count
            }
            
            if issues:
                return CheckResult(
                    name="Performance Baselines",
                    passed=False,
                    message=f"Performance issues: {', '.join(issues)}",
                    details=details,
                    severity="medium"
                )
            
            return CheckResult(
                name="Performance Baselines",
                passed=True,
                message=f"Performance within SLO: {avg_response_time:.2f}s response, {total_errors} errors",
                details=details
            )
            
        except Exception as e:
            return CheckResult(
                name="Performance Baselines",
                passed=False,
                message=f"Failed to check performance: {str(e)}",
                severity="medium"
            )
    
    def check_disaster_recovery(self) -> CheckResult:
        """Check disaster recovery readiness"""
        
        try:
            # Check if infrastructure is defined as code
            cloudformation_exists = os.path.exists('/home/ec2-user/T-DeveloperMVP/infrastructure/aws/cloudformation-template.yml')
            
            # Check if deployment scripts exist
            deploy_script_exists = os.path.exists('/home/ec2-user/T-DeveloperMVP/scripts/deploy.sh')
            
            # Check if backup procedures are documented
            runbook_exists = os.path.exists('/home/ec2-user/T-DeveloperMVP/docs/operations/operations-runbook.md')
            
            # Check multi-AZ deployment
            try:
                response = self.ecs.describe_services(
                    cluster=self.cluster_name,
                    services=[self.service_name]
                )
                service = response['services'][0]
                subnets = service['networkConfiguration']['awsvpcConfiguration']['subnets']
                multi_az = len(subnets) > 1
            except Exception:
                multi_az = False
            
            details = {
                'infrastructure_as_code': cloudformation_exists,
                'deployment_automation': deploy_script_exists,
                'runbook_exists': runbook_exists,
                'multi_az_deployment': multi_az
            }
            
            issues = []
            if not cloudformation_exists:
                issues.append("Infrastructure not defined as code")
            if not deploy_script_exists:
                issues.append("Deployment automation missing")
            if not runbook_exists:
                issues.append("Operations runbook missing")
            if not multi_az:
                issues.append("Not deployed across multiple AZs")
            
            if issues:
                return CheckResult(
                    name="Disaster Recovery",
                    passed=False,
                    message=f"DR readiness issues: {', '.join(issues)}",
                    details=details,
                    severity="high"
                )
            
            return CheckResult(
                name="Disaster Recovery",
                passed=True,
                message="Disaster recovery readiness validated",
                details=details
            )
            
        except Exception as e:
            return CheckResult(
                name="Disaster Recovery",
                passed=False,
                message=f"Failed DR check: {str(e)}",
                severity="high"
            )
    
    def check_documentation(self) -> CheckResult:
        """Check documentation completeness"""
        
        required_docs = [
            '/home/ec2-user/T-DeveloperMVP/docs/api/complete-api-documentation.md',
            '/home/ec2-user/T-DeveloperMVP/docs/developer-guide/complete-developer-guide.md',
            '/home/ec2-user/T-DeveloperMVP/docs/user-guide/user-guide.md',
            '/home/ec2-user/T-DeveloperMVP/docs/operations/operations-runbook.md',
            '/home/ec2-user/T-DeveloperMVP/README.md'
        ]
        
        missing_docs = []
        existing_docs = []
        
        for doc_path in required_docs:
            if os.path.exists(doc_path):
                existing_docs.append(os.path.basename(doc_path))
            else:
                missing_docs.append(os.path.basename(doc_path))
        
        details = {
            'required_docs': len(required_docs),
            'existing_docs': len(existing_docs),
            'missing_docs': missing_docs
        }
        
        if missing_docs:
            return CheckResult(
                name="Documentation",
                passed=False,
                message=f"Missing documentation: {', '.join(missing_docs)}",
                details=details,
                severity="medium"
            )
        
        return CheckResult(
            name="Documentation",
            passed=True,
            message=f"All {len(required_docs)} required documents present",
            details=details
        )
    
    def check_operational_procedures(self) -> CheckResult:
        """Check operational procedures are in place"""
        
        procedures = [
            ('/home/ec2-user/T-DeveloperMVP/scripts/deploy.sh', 'Deployment script'),
            ('/home/ec2-user/T-DeveloperMVP/monitoring/setup_monitoring.py', 'Monitoring setup'),
            ('/home/ec2-user/T-DeveloperMVP/.github/workflows/deploy.yml', 'CI/CD pipeline')
        ]
        
        missing_procedures = []
        existing_procedures = []
        
        for script_path, description in procedures:
            if os.path.exists(script_path):
                existing_procedures.append(description)
            else:
                missing_procedures.append(description)
        
        details = {
            'total_procedures': len(procedures),
            'existing_procedures': len(existing_procedures),
            'missing_procedures': missing_procedures
        }
        
        if missing_procedures:
            return CheckResult(
                name="Operational Procedures",
                passed=False,
                message=f"Missing procedures: {', '.join(missing_procedures)}",
                details=details,
                severity="medium"
            )
        
        return CheckResult(
            name="Operational Procedures",
            passed=True,
            message=f"All {len(procedures)} operational procedures in place",
            details=details
        )
    
    def _generate_report(self) -> ReadinessReport:
        """Generate comprehensive readiness report"""
        
        # Calculate scores
        total_checks = len(self.checks)
        passed_checks = sum(1 for check in self.checks if check.passed)
        
        if total_checks == 0:
            score = 0.0
            overall_status = "UNKNOWN"
        else:
            score = (passed_checks / total_checks) * 100
            
            if score >= 95:
                overall_status = "READY"
            elif score >= 80:
                overall_status = "MOSTLY_READY"
            elif score >= 60:
                overall_status = "NEEDS_WORK"
            else:
                overall_status = "NOT_READY"
        
        # Generate recommendations
        recommendations = []
        
        critical_failures = [c for c in self.checks if not c.passed and c.severity == "critical"]
        high_failures = [c for c in self.checks if not c.passed and c.severity == "high"]
        
        if critical_failures:
            recommendations.append(f"URGENT: Fix {len(critical_failures)} critical issues before production deployment")
        
        if high_failures:
            recommendations.append(f"HIGH PRIORITY: Address {len(high_failures)} high-severity issues")
        
        if score < 95:
            recommendations.append("Complete all readiness checks before production launch")
        
        if not any(c.name == "Performance Baselines" and c.passed for c in self.checks):
            recommendations.append("Establish performance baselines and SLO monitoring")
        
        if not any(c.name == "Disaster Recovery" and c.passed for c in self.checks):
            recommendations.append("Complete disaster recovery testing and documentation")
        
        return ReadinessReport(
            timestamp=datetime.now(),
            environment=self.environment,
            overall_status=overall_status,
            checks=self.checks,
            recommendations=recommendations,
            score=score
        )
    
    def generate_report_output(self, report: ReadinessReport) -> str:
        """Generate human-readable report"""
        
        output = []
        output.append("=" * 80)
        output.append(f"T-DEVELOPER OPERATIONAL READINESS REPORT")
        output.append("=" * 80)
        output.append(f"Environment: {report.environment.upper()}")
        output.append(f"Timestamp: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        output.append(f"Overall Status: {report.overall_status}")
        output.append(f"Readiness Score: {report.score:.1f}%")
        output.append("")
        
        # Summary by status
        passed = sum(1 for check in report.checks if check.passed)
        failed = len(report.checks) - passed
        
        output.append(f"CHECK SUMMARY:")
        output.append(f"  ✅ Passed: {passed}")
        output.append(f"  ❌ Failed: {failed}")
        output.append(f"  📊 Total:  {len(report.checks)}")
        output.append("")
        
        # Failed checks by severity
        if failed > 0:
            output.append("FAILED CHECKS:")
            severities = ["critical", "high", "medium", "low"]
            
            for severity in severities:
                severity_checks = [c for c in report.checks if not c.passed and c.severity == severity]
                if severity_checks:
                    emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "⚪"}[severity]
                    output.append(f"  {emoji} {severity.upper()}:")
                    for check in severity_checks:
                        output.append(f"    - {check.name}: {check.message}")
            output.append("")
        
        # All check details
        output.append("DETAILED RESULTS:")
        for check in report.checks:
            status_emoji = "✅" if check.passed else "❌"
            severity_info = f"[{check.severity.upper()}]" if not check.passed else ""
            
            output.append(f"  {status_emoji} {check.name} {severity_info}")
            output.append(f"      {check.message}")
            
            if check.details:
                for key, value in check.details.items():
                    output.append(f"      {key}: {value}")
            output.append("")
        
        # Recommendations
        if report.recommendations:
            output.append("RECOMMENDATIONS:")
            for i, rec in enumerate(report.recommendations, 1):
                output.append(f"  {i}. {rec}")
            output.append("")
        
        # Status-based guidance
        output.append("GUIDANCE:")
        if report.overall_status == "READY":
            output.append("  🎉 System is ready for production deployment!")
        elif report.overall_status == "MOSTLY_READY":
            output.append("  ⚠️  System is mostly ready. Address remaining issues before production.")
        elif report.overall_status == "NEEDS_WORK":
            output.append("  🔧 System needs significant work before production readiness.")
        else:
            output.append("  🚨 System is NOT ready for production. Critical issues must be resolved.")
        
        output.append("=" * 80)
        
        return "\n".join(output)

def main():
    """Main entry point"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description='T-Developer Operational Readiness Check')
    parser.add_argument('--environment', default='production',
                       choices=['development', 'staging', 'production'],
                       help='Target environment to check')
    parser.add_argument('--region', default='us-east-1',
                       help='AWS region')
    parser.add_argument('--output-file', help='Output file for report')
    parser.add_argument('--json-output', action='store_true',
                       help='Output report in JSON format')
    
    args = parser.parse_args()
    
    # Initialize checker
    checker = OperationalReadinessChecker(
        environment=args.environment,
        region=args.region
    )
    
    try:
        # Run comprehensive check
        report = checker.run_comprehensive_check()
        
        # Generate output
        if args.json_output:
            import json
            output = json.dumps({
                'timestamp': report.timestamp.isoformat(),
                'environment': report.environment,
                'overall_status': report.overall_status,
                'score': report.score,
                'checks': [
                    {
                        'name': c.name,
                        'passed': c.passed,
                        'message': c.message,
                        'severity': c.severity,
                        'details': c.details
                    }
                    for c in report.checks
                ],
                'recommendations': report.recommendations
            }, indent=2)
        else:
            output = checker.generate_report_output(report)
        
        # Write output
        if args.output_file:
            with open(args.output_file, 'w') as f:
                f.write(output)
            print(f"Report written to: {args.output_file}")
        else:
            print(output)
        
        # Exit with appropriate code
        if report.overall_status in ["READY", "MOSTLY_READY"]:
            return 0
        else:
            return 1
    
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return 2

if __name__ == '__main__':
    exit(main())