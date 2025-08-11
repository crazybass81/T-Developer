"""
Asset Optimizer Module for Assembly Agent
Optimizes assets for better performance and smaller bundle sizes
"""

from typing import Dict, List, Any, Optional
import asyncio
import os
import base64
from dataclasses import dataclass
from datetime import datetime

@dataclass
class OptimizationResult:
    success: bool
    optimized_files: Dict[str, str]
    optimization_report: Dict[str, Any]
    optimizations_applied: int
    size_savings: int
    processing_time: float
    error: str = ""

class AssetOptimizer:
    """Advanced asset optimization system"""
    
    def __init__(self):
        self.version = "1.0.0"
    
    async def optimize_assets(
        self,
        resolved_files: Dict[str, str],
        context: Dict[str, Any]
    ) -> OptimizationResult:
        """Optimize all project assets"""
        
        start_time = datetime.now()
        
        try:
            optimized_files = {}
            total_optimizations = 0
            total_savings = 0
            
            for file_path, content in resolved_files.items():
                optimized_content, savings, optimizations = await self._optimize_file(
                    file_path, content, context
                )
                optimized_files[file_path] = optimized_content
                total_savings += savings
                total_optimizations += optimizations
            
            optimization_report = {
                'total_files_processed': len(resolved_files),
                'optimizations_applied': total_optimizations,
                'size_savings_bytes': total_savings,
                'optimization_timestamp': datetime.now().isoformat()
            }
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return OptimizationResult(
                success=True,
                optimized_files=optimized_files,
                optimization_report=optimization_report,
                optimizations_applied=total_optimizations,
                size_savings=total_savings,
                processing_time=processing_time
            )
            
        except Exception as e:
            return OptimizationResult(
                success=False,
                optimized_files={},
                optimization_report={},
                optimizations_applied=0,
                size_savings=0,
                processing_time=(datetime.now() - start_time).total_seconds(),
                error=str(e)
            )
    
    async def _optimize_file(
        self, 
        file_path: str, 
        content: str, 
        context: Dict[str, Any]
    ) -> tuple[str, int, int]:
        """Optimize a single file"""
        
        original_size = len(content)
        optimized_content = content
        optimizations = 0
        
        # CSS optimization
        if file_path.endswith('.css'):
            optimized_content = self._optimize_css(optimized_content)
            optimizations += 1
        
        # JavaScript optimization
        elif file_path.endswith(('.js', '.jsx', '.ts', '.tsx')):
            optimized_content = self._optimize_javascript(optimized_content)
            optimizations += 1
        
        # HTML optimization
        elif file_path.endswith('.html'):
            optimized_content = self._optimize_html(optimized_content)
            optimizations += 1
        
        # JSON optimization
        elif file_path.endswith('.json'):
            optimized_content = self._optimize_json(optimized_content)
            optimizations += 1
        
        size_savings = original_size - len(optimized_content)
        return optimized_content, size_savings, optimizations
    
    def _optimize_css(self, content: str) -> str:
        """Optimize CSS content"""
        import re
        
        # Remove comments
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r';\s*}', '}', content)
        content = re.sub(r'{\s*', '{', content)
        content = re.sub(r';\s*', ';', content)
        
        return content.strip()
    
    def _optimize_javascript(self, content: str) -> str:
        """Optimize JavaScript content"""
        import re
        
        # Remove single-line comments
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        
        # Remove multi-line comments (but preserve license comments)
        content = re.sub(r'/\*(?![*!]).*?\*/', '', content, flags=re.DOTALL)
        
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r';\s*', ';', content)
        content = re.sub(r'{\s*', '{', content)
        content = re.sub(r'}\s*', '}', content)
        
        return content.strip()
    
    def _optimize_html(self, content: str) -> str:
        """Optimize HTML content"""
        import re
        
        # Remove HTML comments
        content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        
        # Remove extra whitespace between tags
        content = re.sub(r'>\s+<', '><', content)
        
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content)
        
        return content.strip()
    
    def _optimize_json(self, content: str) -> str:
        """Optimize JSON content"""
        try:
            import json
            data = json.loads(content)
            return json.dumps(data, separators=(',', ':'))
        except:
            return content