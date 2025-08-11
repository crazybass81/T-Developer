"""Validation Engine Module for Assembly Agent
Validates project integrity and quality gates
"""

from typing import Dict, List, Any, Optional
import asyncio
import os
import json
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ValidationIssue:
    level: str  # error, warning, info
    message: str
    file_path: str
    line_number: int
    rule_id: str

@dataclass
class ValidationResult:
    success: bool
    validated_files: Dict[str, str]
    passed_quality_gates: bool
    issues: List[ValidationIssue]
    validation_report: Dict[str, Any]
    validations_passed: int
    processing_time: float
    error: str = ""

class ValidationEngine:
    """Advanced project validation system"""
    
    def __init__(self):
        self.version = "1.0.0"
        
        self.quality_gates = {
            'required_files': {
                'react': ['package.json', 'src/App.tsx', 'public/index.html'],
                'vue': ['package.json', 'src/App.vue', 'public/index.html'],
                'angular': ['package.json', 'src/main.ts', 'angular.json'],
                'express': ['package.json', 'src/app.ts'],
                'fastapi': ['main.py', 'requirements.txt'],
                'django': ['manage.py', 'requirements.txt'],
                'flask': ['app.py', 'requirements.txt']
            },
            'forbidden_patterns': [
                r'console\.log\(',  # No console.log in production
                r'debugger;',       # No debugger statements
                r'TODO:',           # No unresolved TODOs
                r'FIXME:',          # No unresolved FIXMEs
            ],
            'file_size_limits': {
                'max_file_size': 1024 * 1024,  # 1MB
                'max_line_length': 120
            }
        }
    
    async def validate_project(
        self,
        optimized_files: Dict[str, str],
        context: Dict[str, Any]
    ) -> ValidationResult:
        """Validate complete project"""
        
        start_time = datetime.now()
        issues = []
        
        try:
            framework = context.get('framework', 'react')
            
            # Required files validation
            required_files_issues = await self._validate_required_files(
                optimized_files, framework
            )
            issues.extend(required_files_issues)
            
            # Code quality validation
            quality_issues = await self._validate_code_quality(
                optimized_files, context
            )
            issues.extend(quality_issues)
            
            # Security validation
            security_issues = await self._validate_security(
                optimized_files, context
            )
            issues.extend(security_issues)
            
            # Performance validation
            performance_issues = await self._validate_performance(
                optimized_files, context
            )
            issues.extend(performance_issues)
            
            # Check if quality gates are passed
            critical_issues = [i for i in issues if i.level == 'error']
            passed_quality_gates = len(critical_issues) == 0
            
            # Generate validation report
            validation_report = {
                'total_files': len(optimized_files),
                'issues_by_level': {
                    'error': len([i for i in issues if i.level == 'error']),
                    'warning': len([i for i in issues if i.level == 'warning']),
                    'info': len([i for i in issues if i.level == 'info'])
                },
                'quality_gates_passed': passed_quality_gates,
                'validation_timestamp': datetime.now().isoformat()
            }
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ValidationResult(
                success=True,
                validated_files=optimized_files,
                passed_quality_gates=passed_quality_gates,
                issues=issues,
                validation_report=validation_report,
                validations_passed=len(optimized_files) - len(critical_issues),
                processing_time=processing_time
            )
            
        except Exception as e:
            return ValidationResult(
                success=False,
                validated_files={},
                passed_quality_gates=False,
                issues=[],
                validation_report={},
                validations_passed=0,
                processing_time=(datetime.now() - start_time).total_seconds(),
                error=str(e)
            )
    
    async def _validate_required_files(
        self,
        files: Dict[str, str],
        framework: str
    ) -> List[ValidationIssue]:
        """Validate required files are present"""
        
        issues = []
        required_files = self.quality_gates['required_files'].get(framework, [])
        
        for required_file in required_files:
            if required_file not in files:
                issues.append(ValidationIssue(
                    level='error',
                    message=f"Missing required file: {required_file}",
                    file_path=required_file,
                    line_number=0,
                    rule_id='required_files'
                ))
        
        return issues
    
    async def _validate_code_quality(
        self,
        files: Dict[str, str],
        context: Dict[str, Any]
    ) -> List[ValidationIssue]:
        """Validate code quality"""
        
        issues = []
        
        for file_path, content in files.items():
            # Check file size
            if len(content) > self.quality_gates['file_size_limits']['max_file_size']:
                issues.append(ValidationIssue(
                    level='warning',
                    message=f"File too large: {len(content)} bytes",
                    file_path=file_path,
                    line_number=0,
                    rule_id='file_size'
                ))
            
            # Check line length
            lines = content.split('\n')
            max_length = self.quality_gates['file_size_limits']['max_line_length']
            
            for line_num, line in enumerate(lines, 1):
                if len(line) > max_length:
                    issues.append(ValidationIssue(
                        level='info',
                        message=f"Line too long: {len(line)} characters",
                        file_path=file_path,
                        line_number=line_num,
                        rule_id='line_length'
                    ))
            
            # Check forbidden patterns
            import re
            for pattern in self.quality_gates['forbidden_patterns']:
                matches = re.finditer(pattern, content, re.MULTILINE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    issues.append(ValidationIssue(
                        level='warning',
                        message=f"Forbidden pattern found: {pattern}",
                        file_path=file_path,
                        line_number=line_num,
                        rule_id='forbidden_patterns'
                    ))
        
        return issues
    
    async def _validate_security(
        self,
        files: Dict[str, str],
        context: Dict[str, Any]
    ) -> List[ValidationIssue]:
        """Validate security aspects"""
        
        issues = []
        
        security_patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', 'Hardcoded password'),
            (r'api_key\s*=\s*["\'][^"\']+["\']', 'Hardcoded API key'),
            (r'secret\s*=\s*["\'][^"\']+["\']', 'Hardcoded secret'),
            (r'eval\(', 'Use of eval() function'),
            (r'innerHTML\s*=', 'Potential XSS vulnerability')
        ]
        
        import re
        for file_path, content in files.items():
            for pattern, description in security_patterns:
                matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    issues.append(ValidationIssue(
                        level='error',
                        message=f"Security issue: {description}",
                        file_path=file_path,
                        line_number=line_num,
                        rule_id='security'
                    ))
        
        return issues
    
    async def _validate_performance(
        self,
        files: Dict[str, str],
        context: Dict[str, Any]
    ) -> List[ValidationIssue]:
        """Validate performance aspects"""
        
        issues = []
        
        performance_patterns = [
            (r'for\s*\(.*\.length.*\)', 'Inefficient loop - cache length'),
            (r'document\.getElementById', 'Consider using more efficient selectors'),
            (r'setInterval\(.*,\s*[1-9]\)', 'High frequency interval')
        ]
        
        import re
        for file_path, content in files.items():
            for pattern, description in performance_patterns:
                matches = re.finditer(pattern, content, re.MULTILINE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    issues.append(ValidationIssue(
                        level='info',
                        message=f"Performance suggestion: {description}",
                        file_path=file_path,
                        line_number=line_num,
                        rule_id='performance'
                    ))
        
        return issues