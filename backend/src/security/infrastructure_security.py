"""
Infrastructure Security Module
Validates AWS infrastructure security configurations
"""

import logging
import boto3
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import botocore.exceptions

logger = logging.getLogger(__name__)

@dataclass
class SecurityFinding:
    """Infrastructure security finding"""
    resource_id: str
    resource_type: str
    severity: str  # critical, high, medium, low
    finding_type: str
    description: str
    remediation: str
    compliance_frameworks: List[str]

@dataclass
class InfrastructureSecurityReport:
    """Infrastructure security audit report"""
    scan_timestamp: datetime
    findings: List[SecurityFinding]
    security_score: float
    compliant_resources: int
    total_resources: int
    recommendations: List[str]

class InfrastructureSecurityAuditor:
    """AWS infrastructure security auditor"""
    
    def __init__(self):
        self.session = boto3.Session()
        self.findings: List[SecurityFinding] = []
        
    async def audit_infrastructure(self, region: str = 'us-east-1') -> InfrastructureSecurityReport:
        """Perform comprehensive infrastructure security audit"""
        
        scan_start = datetime.now()
        self.findings = []
        
        try:
            # Audit IAM configurations
            await self._audit_iam_security()
            
            # Audit S3 bucket security
            await self._audit_s3_security()
            
            # Audit Lambda security
            await self._audit_lambda_security()
            
            # Audit DynamoDB security
            await self._audit_dynamodb_security()
            
            # Audit ECS/Container security
            await self._audit_container_security()
            
            # Audit VPC and network security
            await self._audit_network_security()
            
            # Calculate security score
            security_score = self._calculate_security_score()
            
            # Generate recommendations
            recommendations = self._generate_recommendations()
            
            return InfrastructureSecurityReport(
                scan_timestamp=scan_start,
                findings=self.findings,
                security_score=security_score,
                compliant_resources=self._count_compliant_resources(),
                total_resources=len(self.findings) if self.findings else 1,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Infrastructure security audit failed: {e}")
            return InfrastructureSecurityReport(
                scan_timestamp=scan_start,
                findings=self.findings,
                security_score=0.0,
                compliant_resources=0,
                total_resources=0,
                recommendations=[f"Audit failed: {str(e)}"]
            )
    
    async def _audit_iam_security(self) -> None:
        """Audit IAM security configurations"""
        
        try:
            iam = self.session.client('iam')
            
            # Check for overly permissive policies
            policies = iam.list_policies(Scope='Local')['Policies']
            
            for policy in policies:
                if 't-developer' in policy['PolicyName'].lower():
                    policy_version = iam.get_policy_version(
                        PolicyArn=policy['Arn'],
                        VersionId=policy['DefaultVersionId']
                    )
                    
                    policy_doc = policy_version['PolicyVersion']['Document']
                    
                    # Check for wildcard permissions
                    if self._has_wildcard_permissions(policy_doc):
                        self.findings.append(SecurityFinding(
                            resource_id=policy['PolicyName'],
                            resource_type='IAM Policy',
                            severity='high',
                            finding_type='overly_permissive_policy',
                            description='Policy contains wildcard permissions',
                            remediation='Apply principle of least privilege, use specific actions',
                            compliance_frameworks=['SOC2', 'ISO27001']
                        ))
                    
                    # Check for admin access
                    if self._has_admin_access(policy_doc):
                        self.findings.append(SecurityFinding(
                            resource_id=policy['PolicyName'],
                            resource_type='IAM Policy',
                            severity='critical',
                            finding_type='admin_access',
                            description='Policy grants administrative access',
                            remediation='Limit administrative access to specific personnel',
                            compliance_frameworks=['SOC2', 'PCI-DSS']
                        ))
            
            # Check for unused access keys
            users = iam.list_users()['Users']
            for user in users:
                if 't-developer' in user['UserName'].lower():
                    access_keys = iam.list_access_keys(UserName=user['UserName'])['AccessKeyMetadata']
                    
                    for key in access_keys:
                        # Check last used
                        try:
                            last_used = iam.get_access_key_last_used(AccessKeyId=key['AccessKeyId'])
                            if not last_used.get('AccessKeyLastUsed', {}).get('LastUsedDate'):
                                self.findings.append(SecurityFinding(
                                    resource_id=f"{user['UserName']}:{key['AccessKeyId']}",
                                    resource_type='IAM Access Key',
                                    severity='medium',
                                    finding_type='unused_access_key',
                                    description='Access key has never been used',
                                    remediation='Remove unused access keys',
                                    compliance_frameworks=['CIS']
                                ))
                        except Exception:
                            pass
                            
        except botocore.exceptions.NoCredentialsError:
            logger.warning("No AWS credentials found for IAM audit")
        except Exception as e:
            logger.error(f"IAM audit failed: {e}")
    
    async def _audit_s3_security(self) -> None:
        """Audit S3 bucket security"""
        
        try:
            s3 = self.session.client('s3')
            
            buckets = s3.list_buckets()['Buckets']
            
            for bucket in buckets:
                bucket_name = bucket['Name']
                
                if 't-developer' in bucket_name.lower():
                    # Check public access
                    try:
                        acl = s3.get_bucket_acl(Bucket=bucket_name)
                        
                        for grant in acl['Grants']:
                            grantee = grant.get('Grantee', {})
                            if grantee.get('URI') and 'AllUsers' in grantee['URI']:
                                self.findings.append(SecurityFinding(
                                    resource_id=bucket_name,
                                    resource_type='S3 Bucket',
                                    severity='critical',
                                    finding_type='public_bucket',
                                    description='Bucket is publicly accessible',
                                    remediation='Remove public access permissions',
                                    compliance_frameworks=['GDPR', 'HIPAA', 'PCI-DSS']
                                ))
                    except Exception:
                        pass
                    
                    # Check encryption
                    try:
                        encryption = s3.get_bucket_encryption(Bucket=bucket_name)
                    except s3.exceptions.ClientError as e:
                        if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
                            self.findings.append(SecurityFinding(
                                resource_id=bucket_name,
                                resource_type='S3 Bucket',
                                severity='high',
                                finding_type='unencrypted_bucket',
                                description='Bucket is not encrypted at rest',
                                remediation='Enable S3 server-side encryption',
                                compliance_frameworks=['GDPR', 'HIPAA', 'SOC2']
                            ))
                    
                    # Check versioning
                    try:
                        versioning = s3.get_bucket_versioning(Bucket=bucket_name)
                        if versioning.get('Status') != 'Enabled':
                            self.findings.append(SecurityFinding(
                                resource_id=bucket_name,
                                resource_type='S3 Bucket',
                                severity='medium',
                                finding_type='versioning_disabled',
                                description='Bucket versioning is disabled',
                                remediation='Enable S3 versioning for data protection',
                                compliance_frameworks=['SOC2']
                            ))
                    except Exception:
                        pass
                        
        except Exception as e:
            logger.error(f"S3 audit failed: {e}")
    
    async def _audit_lambda_security(self) -> None:
        """Audit Lambda function security"""
        
        try:
            lambda_client = self.session.client('lambda')
            
            functions = lambda_client.list_functions()['Functions']
            
            for function in functions:
                function_name = function['FunctionName']
                
                if 't-developer' in function_name.lower():
                    # Check for environment variables with secrets
                    if 'Environment' in function and 'Variables' in function['Environment']:
                        env_vars = function['Environment']['Variables']
                        
                        for var_name, var_value in env_vars.items():
                            if self._looks_like_secret(var_name, var_value):
                                self.findings.append(SecurityFinding(
                                    resource_id=function_name,
                                    resource_type='Lambda Function',
                                    severity='high',
                                    finding_type='hardcoded_secret',
                                    description=f'Environment variable {var_name} may contain secrets',
                                    remediation='Use AWS Secrets Manager or Parameter Store',
                                    compliance_frameworks=['SOC2', 'PCI-DSS']
                                ))
                    
                    # Check VPC configuration
                    if 'VpcConfig' not in function:
                        self.findings.append(SecurityFinding(
                            resource_id=function_name,
                            resource_type='Lambda Function',
                            severity='low',
                            finding_type='no_vpc',
                            description='Lambda function is not in VPC',
                            remediation='Consider placing Lambda in VPC for network isolation',
                            compliance_frameworks=['CIS']
                        ))
                    
                    # Check runtime version
                    runtime = function.get('Runtime', '')
                    if self._is_deprecated_runtime(runtime):
                        self.findings.append(SecurityFinding(
                            resource_id=function_name,
                            resource_type='Lambda Function',
                            severity='medium',
                            finding_type='deprecated_runtime',
                            description=f'Using deprecated runtime: {runtime}',
                            remediation='Update to supported runtime version',
                            compliance_frameworks=['CIS']
                        ))
                        
        except Exception as e:
            logger.error(f"Lambda audit failed: {e}")
    
    async def _audit_dynamodb_security(self) -> None:
        """Audit DynamoDB security configurations"""
        
        try:
            dynamodb = self.session.client('dynamodb')
            
            tables = dynamodb.list_tables()['TableNames']
            
            for table_name in tables:
                if 't-developer' in table_name.lower():
                    table_desc = dynamodb.describe_table(TableName=table_name)['Table']
                    
                    # Check encryption at rest
                    if 'SSEDescription' not in table_desc:
                        self.findings.append(SecurityFinding(
                            resource_id=table_name,
                            resource_type='DynamoDB Table',
                            severity='high',
                            finding_type='unencrypted_table',
                            description='Table is not encrypted at rest',
                            remediation='Enable DynamoDB encryption at rest',
                            compliance_frameworks=['GDPR', 'HIPAA', 'SOC2']
                        ))
                    
                    # Check point-in-time recovery
                    try:
                        backup_desc = dynamodb.describe_continuous_backups(TableName=table_name)
                        if not backup_desc['ContinuousBackupsDescription']['PointInTimeRecoveryDescription']['PointInTimeRecoveryStatus'] == 'ENABLED':
                            self.findings.append(SecurityFinding(
                                resource_id=table_name,
                                resource_type='DynamoDB Table',
                                severity='medium',
                                finding_type='no_point_in_time_recovery',
                                description='Point-in-time recovery is disabled',
                                remediation='Enable point-in-time recovery for data protection',
                                compliance_frameworks=['SOC2']
                            ))
                    except Exception:
                        pass
                        
        except Exception as e:
            logger.error(f"DynamoDB audit failed: {e}")
    
    async def _audit_container_security(self) -> None:
        """Audit ECS and container security"""
        
        try:
            ecs = self.session.client('ecs')
            
            clusters = ecs.list_clusters()['clusterArns']
            
            for cluster_arn in clusters:
                cluster_name = cluster_arn.split('/')[-1]
                
                if 't-developer' in cluster_name.lower():
                    # Get task definitions
                    services = ecs.list_services(cluster=cluster_arn)['serviceArns']
                    
                    for service_arn in services:
                        service_desc = ecs.describe_services(
                            cluster=cluster_arn,
                            services=[service_arn]
                        )['services'][0]
                        
                        task_def_arn = service_desc['taskDefinition']
                        task_def = ecs.describe_task_definition(taskDefinition=task_def_arn)['taskDefinition']
                        
                        # Check for privileged containers
                        for container in task_def.get('containerDefinitions', []):
                            if container.get('privileged'):
                                self.findings.append(SecurityFinding(
                                    resource_id=f"{cluster_name}:{container['name']}",
                                    resource_type='ECS Container',
                                    severity='high',
                                    finding_type='privileged_container',
                                    description='Container runs in privileged mode',
                                    remediation='Remove privileged mode unless absolutely necessary',
                                    compliance_frameworks=['CIS']
                                ))
                            
                            # Check for secrets in environment variables
                            for env_var in container.get('environment', []):
                                if self._looks_like_secret(env_var['name'], env_var['value']):
                                    self.findings.append(SecurityFinding(
                                        resource_id=f"{cluster_name}:{container['name']}",
                                        resource_type='ECS Container',
                                        severity='high',
                                        finding_type='container_secret',
                                        description=f'Container may have secrets in environment variables',
                                        remediation='Use AWS Secrets Manager for sensitive data',
                                        compliance_frameworks=['SOC2', 'PCI-DSS']
                                    ))
                                    
        except Exception as e:
            logger.error(f"Container audit failed: {e}")
    
    async def _audit_network_security(self) -> None:
        """Audit VPC and network security"""
        
        try:
            ec2 = self.session.client('ec2')
            
            # Check security groups
            security_groups = ec2.describe_security_groups()['SecurityGroups']
            
            for sg in security_groups:
                if sg['GroupName'] != 'default' and 't-developer' in sg['GroupName'].lower():
                    
                    # Check for overly permissive inbound rules
                    for rule in sg.get('IpPermissions', []):
                        for ip_range in rule.get('IpRanges', []):
                            if ip_range.get('CidrIp') == '0.0.0.0/0':
                                self.findings.append(SecurityFinding(
                                    resource_id=sg['GroupId'],
                                    resource_type='Security Group',
                                    severity='high',
                                    finding_type='open_security_group',
                                    description=f'Security group allows access from 0.0.0.0/0 on port {rule.get("FromPort", "all")}',
                                    remediation='Restrict access to specific IP ranges',
                                    compliance_frameworks=['CIS', 'PCI-DSS']
                                ))
            
            # Check NACLs
            nacls = ec2.describe_network_acls()['NetworkAcls']
            
            for nacl in nacls:
                if not nacl['IsDefault']:
                    # Check for overly permissive NACL rules
                    for entry in nacl.get('Entries', []):
                        if not entry.get('Egress') and entry.get('CidrBlock') == '0.0.0.0/0' and entry.get('RuleAction') == 'allow':
                            self.findings.append(SecurityFinding(
                                resource_id=nacl['NetworkAclId'],
                                resource_type='Network ACL',
                                severity='medium',
                                finding_type='permissive_nacl',
                                description='Network ACL allows unrestricted inbound access',
                                remediation='Implement restrictive NACL rules',
                                compliance_frameworks=['CIS']
                            ))
                            
        except Exception as e:
            logger.error(f"Network audit failed: {e}")
    
    def _has_wildcard_permissions(self, policy_doc: Dict[str, Any]) -> bool:
        """Check if policy has wildcard permissions"""
        
        statements = policy_doc.get('Statement', [])
        if not isinstance(statements, list):
            statements = [statements]
            
        for statement in statements:
            if statement.get('Effect') == 'Allow':
                actions = statement.get('Action', [])
                if not isinstance(actions, list):
                    actions = [actions]
                    
                resources = statement.get('Resource', [])
                if not isinstance(resources, list):
                    resources = [resources]
                
                # Check for wildcard in actions or resources
                if '*' in actions or '*' in resources:
                    return True
                    
        return False
    
    def _has_admin_access(self, policy_doc: Dict[str, Any]) -> bool:
        """Check if policy grants administrative access"""
        
        admin_patterns = ['*:*', 'iam:*', 'sts:AssumeRole']
        
        statements = policy_doc.get('Statement', [])
        if not isinstance(statements, list):
            statements = [statements]
            
        for statement in statements:
            if statement.get('Effect') == 'Allow':
                actions = statement.get('Action', [])
                if not isinstance(actions, list):
                    actions = [actions]
                    
                for action in actions:
                    if any(pattern in str(action) for pattern in admin_patterns):
                        return True
                        
        return False
    
    def _looks_like_secret(self, name: str, value: str) -> bool:
        """Check if environment variable looks like a secret"""
        
        secret_keywords = ['password', 'secret', 'key', 'token', 'credential']
        
        name_lower = name.lower()
        if any(keyword in name_lower for keyword in secret_keywords):
            # Check if value looks like a real secret (not placeholder)
            if len(value) > 10 and not any(placeholder in value.lower() for placeholder in ['placeholder', 'example', 'dummy', 'test']):
                return True
                
        return False
    
    def _is_deprecated_runtime(self, runtime: str) -> bool:
        """Check if Lambda runtime is deprecated"""
        
        deprecated_runtimes = [
            'nodejs8.10', 'nodejs10.x', 'python2.7', 'python3.6',
            'dotnetcore2.0', 'dotnetcore2.1', 'go1.x'
        ]
        
        return runtime in deprecated_runtimes
    
    def _calculate_security_score(self) -> float:
        """Calculate infrastructure security score"""
        
        if not self.findings:
            return 100.0
            
        severity_weights = {
            'critical': 25,
            'high': 15,
            'medium': 8,
            'low': 3
        }
        
        total_penalty = sum(
            severity_weights.get(finding.severity, 5)
            for finding in self.findings
        )
        
        return max(0, 100 - min(total_penalty, 100))
    
    def _count_compliant_resources(self) -> int:
        """Count resources without critical or high findings"""
        
        critical_high_resources = {
            finding.resource_id for finding in self.findings
            if finding.severity in ['critical', 'high']
        }
        
        total_resources = len({finding.resource_id for finding in self.findings})
        
        return max(0, total_resources - len(critical_high_resources))
    
    def _generate_recommendations(self) -> List[str]:
        """Generate infrastructure security recommendations"""
        
        recommendations = []
        
        # Count findings by type
        finding_types = {}
        for finding in self.findings:
            finding_types[finding.finding_type] = finding_types.get(finding.finding_type, 0) + 1
        
        # Priority recommendations
        if finding_types.get('public_bucket', 0) > 0:
            recommendations.append("CRITICAL: Review and secure public S3 buckets immediately")
        
        if finding_types.get('admin_access', 0) > 0:
            recommendations.append("CRITICAL: Review and limit administrative IAM permissions")
        
        if finding_types.get('hardcoded_secret', 0) > 0:
            recommendations.append("HIGH: Move hardcoded secrets to AWS Secrets Manager")
        
        if finding_types.get('unencrypted_bucket', 0) > 0 or finding_types.get('unencrypted_table', 0) > 0:
            recommendations.append("HIGH: Enable encryption at rest for all data stores")
        
        if finding_types.get('open_security_group', 0) > 0:
            recommendations.append("HIGH: Restrict security group rules to specific IP ranges")
        
        # General recommendations
        if len(self.findings) > 20:
            recommendations.append("Consider implementing AWS Config for continuous compliance monitoring")
        
        if any(f.severity == 'critical' for f in self.findings):
            recommendations.append("Perform immediate remediation of critical security findings")
        
        return recommendations
    
    def generate_infrastructure_report(self, report: InfrastructureSecurityReport) -> str:
        """Generate infrastructure security report"""
        
        output = f"""
# Infrastructure Security Audit Report

**Scan Date**: {report.scan_timestamp.strftime('%Y-%m-%d %H:%M:%S')}
**Security Score**: {report.security_score:.1f}/100
**Compliant Resources**: {report.compliant_resources}/{report.total_resources}

## Findings Summary

Total Findings: {len(report.findings)}

By Severity:
- Critical: {len([f for f in report.findings if f.severity == 'critical'])}
- High: {len([f for f in report.findings if f.severity == 'high'])}
- Medium: {len([f for f in report.findings if f.severity == 'medium'])}
- Low: {len([f for f in report.findings if f.severity == 'low'])}

## Priority Recommendations

"""
        
        for i, rec in enumerate(report.recommendations[:5], 1):
            output += f"{i}. {rec}\n"
        
        if report.findings:
            output += "\n## Critical Findings\n\n"
            
            critical_findings = [f for f in report.findings if f.severity == 'critical']
            for finding in critical_findings[:5]:
                output += f"**{finding.resource_type}**: {finding.resource_id}\n"
                output += f"- Issue: {finding.description}\n"
                output += f"- Remediation: {finding.remediation}\n\n"
        
        return output