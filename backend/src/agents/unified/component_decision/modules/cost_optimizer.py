"""
Cost Optimizer Module
Optimizes infrastructure and operational costs
"""

from typing import Dict, List, Any, Optional
from enum import Enum


class CostCategory(Enum):
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"
    MONITORING = "monitoring"
    SUPPORT = "support"


class CostOptimizer:
    """Optimizes costs across infrastructure"""
    
    def __init__(self):
        self.cost_models = self._build_cost_models()
        self.optimization_strategies = self._build_optimization_strategies()
        
    async def optimize(
        self,
        requirements: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize costs based on requirements"""
        
        # Analyze current costs
        current_costs = self._analyze_current_costs(requirements)
        
        # Identify optimization opportunities
        opportunities = self._identify_opportunities(current_costs, requirements)
        
        # Generate optimization plan
        optimization_plan = self._generate_optimization_plan(opportunities, constraints)
        
        # Calculate potential savings
        savings = self._calculate_savings(current_costs, optimization_plan)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(optimization_plan, savings)
        
        # Create cost forecast
        forecast = self._create_cost_forecast(current_costs, optimization_plan)
        
        return {
            'current_costs': current_costs,
            'optimization_opportunities': opportunities,
            'optimization_plan': optimization_plan,
            'potential_savings': savings,
            'recommendations': recommendations,
            'forecast': forecast,
            'roi_analysis': self._calculate_roi(optimization_plan, savings)
        }
    
    def _analyze_current_costs(self, requirements: Dict) -> Dict:
        """Analyze current or projected costs"""
        
        # Base cost calculation
        users = requirements.get('expected_users', 1000)
        data_volume = requirements.get('data_volume_gb', 100)
        transactions = requirements.get('transactions_per_day', 10000)
        
        costs = {
            CostCategory.COMPUTE.value: self._calculate_compute_costs(users, transactions),
            CostCategory.STORAGE.value: self._calculate_storage_costs(data_volume),
            CostCategory.NETWORK.value: self._calculate_network_costs(users, data_volume),
            CostCategory.DATABASE.value: self._calculate_database_costs(transactions, data_volume),
            CostCategory.MONITORING.value: self._calculate_monitoring_costs(users),
            CostCategory.SUPPORT.value: self._calculate_support_costs(requirements)
        }
        
        return {
            'breakdown': costs,
            'monthly_total': sum(costs.values()),
            'yearly_total': sum(costs.values()) * 12,
            'cost_per_user': sum(costs.values()) / max(users, 1),
            'cost_per_transaction': sum(costs.values()) / max(transactions, 1)
        }
    
    def _calculate_compute_costs(self, users: int, transactions: int) -> float:
        """Calculate compute costs"""
        
        # Simplified model
        base_cost = 100
        user_cost = users * 0.01
        transaction_cost = transactions * 0.0001
        
        return base_cost + user_cost + transaction_cost
    
    def _calculate_storage_costs(self, data_volume: float) -> float:
        """Calculate storage costs"""
        
        # S3: $0.023/GB, EBS: $0.10/GB
        object_storage_cost = data_volume * 0.023
        block_storage_cost = data_volume * 0.10 * 0.2  # Assuming 20% on block storage
        
        return object_storage_cost + block_storage_cost
    
    def _calculate_network_costs(self, users: int, data_volume: float) -> float:
        """Calculate network costs"""
        
        # Data transfer: $0.09/GB
        monthly_transfer = users * 0.1  # 100MB per user
        transfer_cost = monthly_transfer * 0.09
        
        # Load balancer: $20/month + $0.008/GB
        lb_cost = 20 + (monthly_transfer * 0.008)
        
        return transfer_cost + lb_cost
    
    def _calculate_database_costs(self, transactions: int, data_volume: float) -> float:
        """Calculate database costs"""
        
        # RDS instance cost
        instance_cost = 200  # t3.medium
        
        # Storage cost
        storage_cost = data_volume * 0.115  # gp2 storage
        
        # I/O cost
        io_cost = transactions * 0.0001
        
        return instance_cost + storage_cost + io_cost
    
    def _calculate_monitoring_costs(self, users: int) -> float:
        """Calculate monitoring costs"""
        
        # CloudWatch metrics: $0.30 per metric
        metrics = 20
        metric_cost = metrics * 0.30
        
        # Logs: $0.50 per GB
        log_volume = users * 0.001  # 1MB per user
        log_cost = log_volume * 0.50
        
        # Dashboards: $3 per dashboard
        dashboard_cost = 3 * 5  # 5 dashboards
        
        return metric_cost + log_cost + dashboard_cost
    
    def _calculate_support_costs(self, requirements: Dict) -> float:
        """Calculate support costs"""
        
        if requirements.get('enterprise_support'):
            return 500  # Enterprise support
        elif requirements.get('business_support'):
            return 100  # Business support
        else:
            return 0  # Basic support (free)
    
    def _identify_opportunities(self, costs: Dict, requirements: Dict) -> List[Dict]:
        """Identify cost optimization opportunities"""
        
        opportunities = []
        
        # Compute optimizations
        if costs['breakdown'][CostCategory.COMPUTE.value] > 200:
            opportunities.append({
                'category': CostCategory.COMPUTE.value,
                'type': 'reserved_instances',
                'description': 'Use Reserved Instances for predictable workloads',
                'potential_savings': costs['breakdown'][CostCategory.COMPUTE.value] * 0.3,
                'effort': 'low',
                'risk': 'low'
            })
            
            opportunities.append({
                'category': CostCategory.COMPUTE.value,
                'type': 'spot_instances',
                'description': 'Use Spot Instances for batch processing',
                'potential_savings': costs['breakdown'][CostCategory.COMPUTE.value] * 0.7,
                'effort': 'medium',
                'risk': 'medium'
            })
        
        # Storage optimizations
        if costs['breakdown'][CostCategory.STORAGE.value] > 50:
            opportunities.append({
                'category': CostCategory.STORAGE.value,
                'type': 's3_lifecycle',
                'description': 'Implement S3 lifecycle policies',
                'potential_savings': costs['breakdown'][CostCategory.STORAGE.value] * 0.4,
                'effort': 'low',
                'risk': 'low'
            })
        
        # Database optimizations
        if costs['breakdown'][CostCategory.DATABASE.value] > 150:
            opportunities.append({
                'category': CostCategory.DATABASE.value,
                'type': 'read_replicas',
                'description': 'Use read replicas to reduce main DB load',
                'potential_savings': costs['breakdown'][CostCategory.DATABASE.value] * 0.2,
                'effort': 'medium',
                'risk': 'low'
            })
        
        # Auto-scaling
        opportunities.append({
            'category': 'general',
            'type': 'auto_scaling',
            'description': 'Implement auto-scaling to match demand',
            'potential_savings': costs['monthly_total'] * 0.15,
            'effort': 'medium',
            'risk': 'low'
        })
        
        return opportunities
    
    def _generate_optimization_plan(self, opportunities: List[Dict], constraints: Dict) -> Dict:
        """Generate optimization plan"""
        
        # Filter opportunities based on constraints
        budget = constraints.get('optimization_budget', 10000)
        risk_tolerance = constraints.get('risk_tolerance', 'medium')
        
        selected_opportunities = []
        total_cost = 0
        
        # Sort by ROI (savings/effort)
        sorted_opps = sorted(
            opportunities,
            key=lambda x: x['potential_savings'] / (1 if x['effort'] == 'low' else 2 if x['effort'] == 'medium' else 3),
            reverse=True
        )
        
        for opp in sorted_opps:
            if self._is_acceptable_risk(opp['risk'], risk_tolerance):
                implementation_cost = self._estimate_implementation_cost(opp)
                if total_cost + implementation_cost <= budget:
                    selected_opportunities.append(opp)
                    total_cost += implementation_cost
        
        return {
            'selected_optimizations': selected_opportunities,
            'implementation_cost': total_cost,
            'timeline': self._estimate_timeline(selected_opportunities),
            'phases': self._create_implementation_phases(selected_opportunities)
        }
    
    def _is_acceptable_risk(self, risk: str, tolerance: str) -> bool:
        """Check if risk is acceptable"""
        
        risk_levels = {'low': 1, 'medium': 2, 'high': 3}
        return risk_levels.get(risk, 3) <= risk_levels.get(tolerance, 2)
    
    def _estimate_implementation_cost(self, opportunity: Dict) -> float:
        """Estimate implementation cost"""
        
        effort_costs = {
            'low': 500,
            'medium': 2000,
            'high': 5000
        }
        
        return effort_costs.get(opportunity['effort'], 2000)
    
    def _estimate_timeline(self, opportunities: List[Dict]) -> Dict:
        """Estimate implementation timeline"""
        
        effort_days = {
            'low': 5,
            'medium': 15,
            'high': 30
        }
        
        total_days = sum(effort_days.get(opp['effort'], 15) for opp in opportunities)
        
        return {
            'total_days': total_days,
            'parallel_execution': total_days // 2,  # Assuming some parallelization
            'phases': len(opportunities)
        }
    
    def _create_implementation_phases(self, opportunities: List[Dict]) -> List[Dict]:
        """Create implementation phases"""
        
        phases = []
        
        # Group by effort/risk
        for i, opp in enumerate(opportunities):
            phases.append({
                'phase': i + 1,
                'name': opp['type'],
                'duration': '1-2 weeks',
                'optimization': opp,
                'dependencies': []
            })
        
        return phases
    
    def _calculate_savings(self, current_costs: Dict, plan: Dict) -> Dict:
        """Calculate potential savings"""
        
        total_savings = sum(
            opp['potential_savings']
            for opp in plan['selected_optimizations']
        )
        
        return {
            'monthly_savings': total_savings,
            'yearly_savings': total_savings * 12,
            'percentage_reduction': (total_savings / current_costs['monthly_total']) * 100,
            'breakeven_months': plan['implementation_cost'] / total_savings if total_savings > 0 else float('inf')
        }
    
    def _generate_recommendations(self, plan: Dict, savings: Dict) -> List[Dict]:
        """Generate cost optimization recommendations"""
        
        recommendations = []
        
        # Priority recommendations based on selected optimizations
        for opp in plan['selected_optimizations']:
            recommendations.append({
                'priority': 'high' if opp['potential_savings'] > 100 else 'medium',
                'category': opp['category'],
                'action': opp['description'],
                'impact': f"${opp['potential_savings']:.2f}/month savings",
                'effort': opp['effort'],
                'timeline': '1-2 weeks'
            })
        
        # Additional general recommendations
        recommendations.extend([
            {
                'priority': 'medium',
                'category': 'general',
                'action': 'Regular cost reviews and optimization',
                'impact': 'Continuous improvement',
                'effort': 'low',
                'timeline': 'ongoing'
            },
            {
                'priority': 'low',
                'category': 'general',
                'action': 'Implement cost allocation tags',
                'impact': 'Better cost visibility',
                'effort': 'low',
                'timeline': '1 week'
            }
        ])
        
        return recommendations
    
    def _create_cost_forecast(self, current_costs: Dict, plan: Dict) -> Dict:
        """Create cost forecast"""
        
        monthly_costs = []
        current_monthly = current_costs['monthly_total']
        
        # 12-month forecast
        for month in range(12):
            # Apply optimizations progressively
            if month < 3:
                cost = current_monthly
            elif month < 6:
                # 50% of optimizations implemented
                savings = sum(opp['potential_savings'] * 0.5 for opp in plan['selected_optimizations'])
                cost = current_monthly - savings
            else:
                # Full optimizations implemented
                savings = sum(opp['potential_savings'] for opp in plan['selected_optimizations'])
                cost = current_monthly - savings
            
            # Add growth factor
            growth_rate = 0.05  # 5% monthly growth
            cost *= (1 + growth_rate) ** month
            
            monthly_costs.append({
                'month': month + 1,
                'cost': cost,
                'cumulative': sum(c['cost'] for c in monthly_costs) + cost
            })
        
        return {
            'monthly_forecast': monthly_costs,
            'year_1_total': sum(c['cost'] for c in monthly_costs),
            'year_2_projection': sum(c['cost'] for c in monthly_costs) * 1.2,
            'year_3_projection': sum(c['cost'] for c in monthly_costs) * 1.4
        }
    
    def _calculate_roi(self, plan: Dict, savings: Dict) -> Dict:
        """Calculate ROI for optimization plan"""
        
        investment = plan['implementation_cost']
        annual_return = savings['yearly_savings']
        
        return {
            'roi_percentage': ((annual_return - investment) / investment) * 100 if investment > 0 else 0,
            'payback_period_months': savings['breakeven_months'],
            'net_present_value': self._calculate_npv(investment, annual_return, 3),
            'internal_rate_of_return': self._calculate_irr(investment, annual_return, 3)
        }
    
    def _calculate_npv(self, investment: float, annual_return: float, years: int) -> float:
        """Calculate Net Present Value"""
        
        discount_rate = 0.1  # 10% discount rate
        npv = -investment
        
        for year in range(1, years + 1):
            npv += annual_return / ((1 + discount_rate) ** year)
        
        return npv
    
    def _calculate_irr(self, investment: float, annual_return: float, years: int) -> float:
        """Calculate Internal Rate of Return (simplified)"""
        
        # Simplified IRR calculation
        if investment == 0:
            return 0
        
        return (annual_return / investment) - 1
    
    def _build_cost_models(self) -> Dict:
        """Build cost models catalog"""
        
        return {
            'aws': {
                'ec2': {'on_demand': 0.10, 'reserved': 0.07, 'spot': 0.03},
                's3': {'standard': 0.023, 'ia': 0.0125, 'glacier': 0.004},
                'rds': {'instance': 200, 'storage': 0.115},
                'lambda': {'requests': 0.20, 'gb_seconds': 0.0000166667}
            }
        }
    
    def _build_optimization_strategies(self) -> Dict:
        """Build optimization strategies catalog"""
        
        return {
            'compute': [
                'Reserved Instances',
                'Spot Instances',
                'Auto-scaling',
                'Right-sizing'
            ],
            'storage': [
                'Lifecycle policies',
                'Compression',
                'Deduplication',
                'Tiered storage'
            ],
            'database': [
                'Read replicas',
                'Caching',
                'Query optimization',
                'Connection pooling'
            ]
        }
