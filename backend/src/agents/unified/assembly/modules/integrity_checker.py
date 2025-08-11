"""
Integrity Checker Module for Assembly Agent
Verifies project integrity and consistency
"""

from typing import Dict, List, Any, Optional
import asyncio
import hashlib
import os
from dataclasses import dataclass
from datetime import datetime

@dataclass
class IntegrityResult:
    success: bool
    integrity_verified: bool
    checksum_report: Dict[str, str]
    consistency_issues: List[str]
    processing_time: float
    error: str = ""

class IntegrityChecker:
    """Advanced integrity verification system"""
    
    def __init__(self):
        self.version = "1.0.0"
    
    async def verify_integrity(
        self,
        build_artifacts: Dict[str, str],
        context: Dict[str, Any]
    ) -> IntegrityResult:
        """Verify project integrity"""
        
        start_time = datetime.now()
        
        try:
            # Generate checksums
            checksum_report = await self._generate_checksums(build_artifacts)
            
            # Check for consistency issues
            consistency_issues = await self._check_consistency(build_artifacts, context)
            
            # Verify file relationships
            relationship_issues = await self._verify_file_relationships(build_artifacts)
            consistency_issues.extend(relationship_issues)
            
            integrity_verified = len(consistency_issues) == 0
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return IntegrityResult(
                success=True,
                integrity_verified=integrity_verified,
                checksum_report=checksum_report,
                consistency_issues=consistency_issues,
                processing_time=processing_time
            )
            
        except Exception as e:
            return IntegrityResult(
                success=False,
                integrity_verified=False,
                checksum_report={},
                consistency_issues=[],
                processing_time=(datetime.now() - start_time).total_seconds(),
                error=str(e)
            )
    
    async def _generate_checksums(self, build_artifacts: Dict[str, str]) -> Dict[str, str]:
        """Generate checksums for all files"""
        
        checksums = {}
        
        for file_path, content in build_artifacts.items():
            hash_obj = hashlib.sha256()
            hash_obj.update(content.encode('utf-8'))
            checksums[file_path] = hash_obj.hexdigest()[:16]
        
        return checksums
    
    async def _check_consistency(
        self,
        build_artifacts: Dict[str, str],
        context: Dict[str, Any]
    ) -> List[str]:
        """Check for consistency issues"""
        
        issues = []
        framework = context.get('framework', 'react')
        
        # Check for required framework files
        required_files = {
            'react': ['package.json'],
            'vue': ['package.json'],
            'angular': ['package.json', 'angular.json'],
            'express': ['package.json'],
            'fastapi': ['main.py'],
            'django': ['manage.py'],
            'flask': ['app.py']
        }
        
        for required_file in required_files.get(framework, []):
            if required_file not in build_artifacts:
                issues.append(f"Missing required file: {required_file}")
        
        # Check package.json consistency for JavaScript projects
        if 'package.json' in build_artifacts:
            try:
                import json
                package_data = json.loads(build_artifacts['package.json'])
                
                # Check if dependencies exist in node_modules (simulated)
                dependencies = package_data.get('dependencies', {})
                if len(dependencies) == 0:
                    issues.append("No dependencies found in package.json")
                
                # Check scripts
                scripts = package_data.get('scripts', {})
                expected_scripts = ['build', 'test', 'start']
                missing_scripts = [s for s in expected_scripts if s not in scripts]
                if missing_scripts:
                    issues.append(f"Missing package.json scripts: {', '.join(missing_scripts)}")
                
            except json.JSONDecodeError:
                issues.append("Invalid package.json format")
        
        return issues
    
    async def _verify_file_relationships(self, build_artifacts: Dict[str, str]) -> List[str]:
        """Verify file relationships and imports"""
        
        issues = []
        
        # Check for broken imports in JavaScript/TypeScript files
        import re
        
        for file_path, content in build_artifacts.items():
            if file_path.endswith(('.js', '.jsx', '.ts', '.tsx')):
                # Find import statements
                import_pattern = r'import\s+.*\s+from\s+[\'"]([^\'"]+)[\'"]'
                imports = re.findall(import_pattern, content)
                
                for import_path in imports:
                    # Check if imported file exists (simplified check)
                    if import_path.startswith('.'):
                        # Relative import
                        base_dir = os.path.dirname(file_path)
                        full_import_path = os.path.normpath(os.path.join(base_dir, import_path))
                        
                        # Add common extensions
                        possible_paths = [
                            full_import_path + '.js',
                            full_import_path + '.jsx',
                            full_import_path + '.ts',
                            full_import_path + '.tsx',
                            os.path.join(full_import_path, 'index.js'),
                            os.path.join(full_import_path, 'index.ts')
                        ]
                        
                        found = False
                        for path in possible_paths:
                            if path in build_artifacts:
                                found = True
                                break
                        
                        if not found:
                            issues.append(f"Broken import in {file_path}: {import_path}")
        
        return issues