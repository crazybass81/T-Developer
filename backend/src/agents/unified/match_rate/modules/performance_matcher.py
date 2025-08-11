"""
Performance Matcher Module
Evaluates performance characteristics matching
"""

from typing import Dict, List, Any, Optional
import math


class PerformanceMatcher:
    """Evaluates performance matching"""
    
    def __init__(self):
        self.performance_benchmarks = self._build_performance_benchmarks()
        
    async def evaluate(
        self,
        components: List[Dict[str, Any]],
        requirements: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """Evaluate performance matching"""
        
        performance_results = {}
        
        # Extract performance requirements
        perf_requirements = self._extract_performance_requirements(requirements)
        
        for component in components:
            component_id = component.get('id', component.get('name'))
            
            # Extract component performance characteristics
            perf_characteristics = self._extract_performance_characteristics(component)
            
            # Evaluate different performance aspects
            evaluations = {
                'response_time': self._evaluate_response_time(perf_characteristics, perf_requirements),
                'throughput': self._evaluate_throughput(perf_characteristics, perf_requirements),
                'scalability': self._evaluate_scalability(perf_characteristics, perf_requirements),
                'resource_efficiency': self._evaluate_resource_efficiency(perf_characteristics, perf_requirements),
                'reliability': self._evaluate_reliability(perf_characteristics, perf_requirements)
            }
            
            # Calculate overall performance score
            performance_score = self._calculate_performance_score(evaluations)
            
            performance_results[component_id] = {
                'performance_score': performance_score,
                'detailed_evaluations': evaluations,
                'benchmarks': self._compare_to_benchmarks(perf_characteristics),
                'bottlenecks': self._identify_bottlenecks(perf_characteristics, perf_requirements),
                'optimization_suggestions': self._suggest_optimizations(evaluations)
            }
        
        return performance_results
    
    def _extract_performance_requirements(self, requirements: Dict) -> Dict[str, Any]:
        """Extract performance requirements"""
        
        return {
            'response_time_ms': requirements.get('max_response_time', 1000),
            'throughput_rps': requirements.get('min_throughput', 100),
            'concurrent_users': requirements.get('concurrent_users', 1000),
            'uptime_percentage': requirements.get('uptime_requirement', 99.9),
            'memory_limit_mb': requirements.get('memory_limit', 1024),
            'cpu_limit_cores': requirements.get('cpu_limit', 2)
        }
    
    def _extract_performance_characteristics(self, component: Dict) -> Dict[str, Any]:
        """Extract component performance characteristics"""
        
        # Extract from component metadata
        characteristics = {
            'typical_response_time_ms': component.get('response_time', 500),
            'max_throughput_rps': component.get('throughput', 200),
            'scalability_factor': component.get('scalability', 1.0),
            'memory_usage_mb': component.get('memory_usage', 512),
            'cpu_usage_percent': component.get('cpu_usage', 50),
            'uptime_percentage': component.get('uptime', 99.5)
        }
        
        return characteristics
    
    def _evaluate_response_time(self, characteristics: Dict, requirements: Dict) -> Dict[str, Any]:
        """Evaluate response time performance"""
        
        actual_time = characteristics.get('typical_response_time_ms', 1000)
        required_time = requirements.get('response_time_ms', 1000)
        
        # Calculate performance ratio
        ratio = required_time / max(actual_time, 1)
        score = min(1.0, ratio)
        
        return {
            'score': score,
            'actual_ms': actual_time,
            'required_ms': required_time,
            'meets_requirement': actual_time <= required_time,
            'performance_margin': required_time - actual_time
        }
    
    def _evaluate_throughput(self, characteristics: Dict, requirements: Dict) -> Dict[str, Any]:
        """Evaluate throughput performance"""
        
        actual_throughput = characteristics.get('max_throughput_rps', 100)
        required_throughput = requirements.get('throughput_rps', 100)
        
        # Calculate performance ratio
        ratio = actual_throughput / max(required_throughput, 1)
        score = min(1.0, ratio)
        
        return {
            'score': score,
            'actual_rps': actual_throughput,
            'required_rps': required_throughput,
            'meets_requirement': actual_throughput >= required_throughput,
            'capacity_margin': actual_throughput - required_throughput
        }
    
    def _evaluate_scalability(self, characteristics: Dict, requirements: Dict) -> Dict[str, Any]:
        """Evaluate scalability characteristics"""
        
        scalability_factor = characteristics.get('scalability_factor', 1.0)
        concurrent_users = requirements.get('concurrent_users', 1000)
        
        # Estimate scalability capacity
        estimated_capacity = scalability_factor * 1000  # Base capacity
        scalability_score = min(1.0, estimated_capacity / concurrent_users)
        
        return {
            'score': scalability_score,
            'scalability_factor': scalability_factor,
            'estimated_capacity': estimated_capacity,
            'required_capacity': concurrent_users,
            'scaling_method': self._determine_scaling_method(characteristics)
        }
    
    def _determine_scaling_method(self, characteristics: Dict) -> str:
        """Determine scaling method based on characteristics"""
        
        # Simple heuristic
        scalability = characteristics.get('scalability_factor', 1.0)
        
        if scalability >= 2.0:
            return 'horizontal'
        elif scalability >= 1.5:
            return 'hybrid'
        else:
            return 'vertical'
    
    def _evaluate_resource_efficiency(self, characteristics: Dict, requirements: Dict) -> Dict[str, Any]:
        """Evaluate resource efficiency"""
        
        memory_usage = characteristics.get('memory_usage_mb', 512)
        memory_limit = requirements.get('memory_limit_mb', 1024)
        
        cpu_usage = characteristics.get('cpu_usage_percent', 50)
        cpu_limit = requirements.get('cpu_limit_cores', 2) * 100  # Convert to percentage
        
        # Calculate efficiency scores
        memory_efficiency = min(1.0, memory_limit / max(memory_usage, 1))
        cpu_efficiency = min(1.0, cpu_limit / max(cpu_usage, 1))
        
        overall_efficiency = (memory_efficiency + cpu_efficiency) / 2
        
        return {
            'score': overall_efficiency,
            'memory_efficiency': memory_efficiency,
            'cpu_efficiency': cpu_efficiency,
            'memory_usage_mb': memory_usage,
            'cpu_usage_percent': cpu_usage,
            'within_limits': memory_usage <= memory_limit and cpu_usage <= cpu_limit
        }
    
    def _evaluate_reliability(self, characteristics: Dict, requirements: Dict) -> Dict[str, Any]:
        """Evaluate reliability characteristics"""
        
        actual_uptime = characteristics.get('uptime_percentage', 99.0)
        required_uptime = requirements.get('uptime_percentage', 99.9)
        
        # Calculate reliability score
        uptime_score = min(1.0, actual_uptime / required_uptime)
        
        return {
            'score': uptime_score,
            'actual_uptime': actual_uptime,
            'required_uptime': required_uptime,
            'meets_sla': actual_uptime >= required_uptime,
            'downtime_difference': self._calculate_downtime_difference(actual_uptime, required_uptime)
        }
    
    def _calculate_downtime_difference(self, actual: float, required: float) -> float:
        """Calculate downtime difference in hours per year"""
        
        hours_per_year = 8760
        actual_downtime = hours_per_year * (100 - actual) / 100
        required_downtime = hours_per_year * (100 - required) / 100
        
        return actual_downtime - required_downtime
    
    def _calculate_performance_score(self, evaluations: Dict[str, Dict]) -> float:
        """Calculate overall performance score"""
        
        weights = {
            'response_time': 0.25,
            'throughput': 0.25,
            'scalability': 0.2,
            'resource_efficiency': 0.15,
            'reliability': 0.15
        }
        
        total_score = sum(
            evaluations[category]['score'] * weights[category]
            for category in weights.keys()
            if category in evaluations
        )
        
        return min(1.0, max(0.0, total_score))
    
    def _compare_to_benchmarks(self, characteristics: Dict) -> Dict[str, str]:
        """Compare performance to industry benchmarks"""
        
        benchmarks = {}
        
        # Response time benchmark
        response_time = characteristics.get('typical_response_time_ms', 1000)
        if response_time < 100:
            benchmarks['response_time'] = 'excellent'
        elif response_time < 500:
            benchmarks['response_time'] = 'good'
        elif response_time < 1000:
            benchmarks['response_time'] = 'acceptable'
        else:
            benchmarks['response_time'] = 'poor'
        
        # Throughput benchmark
        throughput = characteristics.get('max_throughput_rps', 100)
        if throughput > 1000:
            benchmarks['throughput'] = 'excellent'
        elif throughput > 500:
            benchmarks['throughput'] = 'good'
        elif throughput > 100:
            benchmarks['throughput'] = 'acceptable'
        else:
            benchmarks['throughput'] = 'poor'
        
        return benchmarks
    
    def _identify_bottlenecks(self, characteristics: Dict, requirements: Dict) -> List[str]:
        """Identify performance bottlenecks"""
        
        bottlenecks = []
        
        # Response time bottleneck
        if characteristics.get('typical_response_time_ms', 0) > requirements.get('response_time_ms', 1000):
            bottlenecks.append('Response time exceeds requirements')
        
        # Throughput bottleneck
        if characteristics.get('max_throughput_rps', 0) < requirements.get('throughput_rps', 100):
            bottlenecks.append('Throughput below requirements')
        
        # Memory bottleneck
        if characteristics.get('memory_usage_mb', 0) > requirements.get('memory_limit_mb', 1024):
            bottlenecks.append('Memory usage exceeds limits')
        
        # CPU bottleneck
        cpu_limit = requirements.get('cpu_limit_cores', 2) * 50  # 50% per core
        if characteristics.get('cpu_usage_percent', 0) > cpu_limit:
            bottlenecks.append('CPU usage exceeds limits')
        
        return bottlenecks
    
    def _suggest_optimizations(self, evaluations: Dict) -> List[str]:
        """Suggest performance optimizations"""
        
        suggestions = []
        
        for category, evaluation in evaluations.items():
            score = evaluation.get('score', 1.0)
            
            if score < 0.6:
                if category == 'response_time':
                    suggestions.append('Consider caching strategies to improve response time')
                elif category == 'throughput':
                    suggestions.append('Implement load balancing or horizontal scaling')
                elif category == 'scalability':
                    suggestions.append('Redesign for better horizontal scaling')
                elif category == 'resource_efficiency':
                    suggestions.append('Optimize memory and CPU usage')
                elif category == 'reliability':
                    suggestions.append('Implement redundancy and failover mechanisms')
        
        if not suggestions:
            suggestions.append('Performance meets requirements - consider monitoring for optimization opportunities')
        
        return suggestions
    
    def _build_performance_benchmarks(self) -> Dict[str, Dict]:
        """Build performance benchmarks"""
        
        return {
            'web_applications': {
                'response_time_ms': {'excellent': 100, 'good': 300, 'acceptable': 1000},
                'throughput_rps': {'excellent': 1000, 'good': 500, 'acceptable': 100}
            },
            'apis': {
                'response_time_ms': {'excellent': 50, 'good': 200, 'acceptable': 500},
                'throughput_rps': {'excellent': 5000, 'good': 1000, 'acceptable': 200}
            },
            'databases': {
                'response_time_ms': {'excellent': 10, 'good': 50, 'acceptable': 200},
                'throughput_rps': {'excellent': 10000, 'good': 1000, 'acceptable': 100}
            }
        }
