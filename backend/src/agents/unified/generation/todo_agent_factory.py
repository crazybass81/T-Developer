"""
Todo App Agent Factory using Agno Framework
Dynamically generates agents for Todo app functionality at runtime
"""

from typing import Dict, List, Any
import json
from src.agno.agno_integration import AgnoFrameworkManager
from src.agno.agno_client import AgnoClient
from src.agno.runtime_executor import TodoAppRuntime
from src.agno.agent_registry import agent_registry

class TodoAgentFactory:
    """Factory to create Todo app specific agents using Agno"""
    
    def __init__(self):
        self.agno_manager = AgnoFrameworkManager()
        self.agno_client = AgnoClient()
        self.created_agents = {}
    
    async def analyze_and_create_agents(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze Todo app requirements and dynamically create necessary agents
        
        Args:
            requirements: Parsed requirements from Parser agent
            
        Returns:
            Dict containing created agents and their configurations
        """
        
        # Extract features from requirements
        features = requirements.get('features', [])
        entities = requirements.get('entities', {})
        specifications = requirements.get('specifications', {})
        
        # Define agent blueprints based on analysis
        agent_blueprints = self._generate_agent_blueprints(features, entities, specifications)
        
        # Create agents using Agno
        created_agents = {}
        for blueprint in agent_blueprints:
            agent = await self._create_agno_agent(blueprint)
            if agent:
                created_agents[blueprint['name']] = agent
                self.created_agents[blueprint['name']] = agent
        
        # Create runtime for executing agents
        self.runtime = TodoAppRuntime(created_agents)
        
        return {
            'agents_created': len(created_agents),
            'agent_names': list(created_agents.keys()),
            'agents': created_agents,
            'blueprints': agent_blueprints,
            'runtime': self.runtime
        }
    
    def _generate_agent_blueprints(
        self, 
        features: List[str], 
        entities: Dict, 
        specifications: Dict
    ) -> List[Dict[str, Any]]:
        """Generate agent blueprints based on requirements analysis"""
        
        blueprints = []
        
        # Core CRUD agent for tasks
        if any('task' in f.lower() or 'todo' in f.lower() for f in features):
            blueprints.append({
                'name': 'TodoCRUDAgent',
                'type': 'data_manager',
                'config': {
                    'entity': 'Task',
                    'operations': ['create', 'read', 'update', 'delete', 'list'],
                    'fields': {
                        'id': 'string',
                        'title': 'string',
                        'description': 'string',
                        'completed': 'boolean',
                        'priority': 'number',
                        'dueDate': 'date',
                        'category': 'string',
                        'tags': 'array'
                    },
                    'validation_rules': {
                        'title': {'required': True, 'minLength': 1, 'maxLength': 200},
                        'priority': {'min': 1, 'max': 5}
                    }
                }
            })
        
        # Priority management agent
        if any('priority' in f.lower() for f in features):
            blueprints.append({
                'name': 'TaskPriorityAgent',
                'type': 'business_logic',
                'config': {
                    'methods': {
                        'setPriority': {'params': ['taskId', 'priority']},
                        'sortByPriority': {'params': ['tasks', 'order']},
                        'getHighPriorityTasks': {'params': ['threshold']},
                        'autoAssignPriority': {'params': ['task', 'rules']}
                    },
                    'priority_levels': {
                        'critical': 5,
                        'high': 4,
                        'medium': 3,
                        'low': 2,
                        'minimal': 1
                    }
                }
            })
        
        # Filter and search agent
        if any('filter' in f.lower() or 'search' in f.lower() for f in features):
            blueprints.append({
                'name': 'TaskFilterAgent',
                'type': 'query_processor',
                'config': {
                    'filters': {
                        'status': ['all', 'active', 'completed'],
                        'priority': ['high', 'medium', 'low'],
                        'category': 'dynamic',
                        'dateRange': 'custom'
                    },
                    'search': {
                        'fields': ['title', 'description', 'tags'],
                        'fuzzy': True,
                        'highlighting': True
                    },
                    'sort_options': ['priority', 'dueDate', 'createdAt', 'title']
                }
            })
        
        # Persistence agent for local storage
        if any('storage' in f.lower() or 'persist' in f.lower() for f in features):
            blueprints.append({
                'name': 'TaskPersistenceAgent',
                'type': 'storage_manager',
                'config': {
                    'storage_type': 'localStorage',
                    'backup': 'indexedDB',
                    'methods': {
                        'save': {'debounce': 500},
                        'load': {'cache': True},
                        'export': {'formats': ['json', 'csv']},
                        'import': {'validation': True},
                        'sync': {'interval': 30000}
                    },
                    'encryption': False,
                    'compression': True
                }
            })
        
        # Statistics and analytics agent
        if any('statistic' in f.lower() or 'dashboard' in f.lower() for f in features):
            blueprints.append({
                'name': 'TaskStatisticsAgent',
                'type': 'analytics',
                'config': {
                    'metrics': {
                        'completionRate': 'percentage',
                        'averageCompletionTime': 'duration',
                        'overdueTasks': 'count',
                        'tasksByCategory': 'distribution',
                        'productivityTrend': 'timeseries'
                    },
                    'reports': {
                        'daily': ['completed', 'added', 'overdue'],
                        'weekly': ['productivity', 'categories'],
                        'monthly': ['trends', 'achievements']
                    }
                }
            })
        
        # UI state management agent
        if any('ui' in f.lower() or 'interface' in f.lower() for f in features):
            blueprints.append({
                'name': 'TaskUIAgent',
                'type': 'ui_controller',
                'config': {
                    'themes': {
                        'light': 'default',
                        'dark': 'enabled',
                        'auto': 'system'
                    },
                    'views': {
                        'list': 'default',
                        'grid': 'optional',
                        'calendar': 'optional',
                        'kanban': 'optional'
                    },
                    'animations': {
                        'enabled': True,
                        'duration': 300,
                        'easing': 'ease-in-out'
                    },
                    'shortcuts': {
                        'n': 'new_task',
                        'd': 'delete_task',
                        'e': 'edit_task',
                        '/': 'search',
                        'space': 'toggle_complete'
                    }
                }
            })
        
        # Notification agent
        if any('notification' in f.lower() or 'reminder' in f.lower() for f in features):
            blueprints.append({
                'name': 'TaskNotificationAgent',
                'type': 'notification_service',
                'config': {
                    'channels': ['browser', 'email', 'push'],
                    'triggers': {
                        'dueDate': 'before',
                        'overdue': 'immediate',
                        'reminder': 'custom'
                    },
                    'settings': {
                        'sound': True,
                        'vibration': True,
                        'badge': True
                    }
                }
            })
        
        return blueprints
    
    async def _create_agno_agent(self, blueprint: Dict[str, Any]) -> Any:
        """Create an agent using Agno Framework"""
        
        try:
            # Import the real Agno Agent Generator
            from src.agno.agent_generator import create_agent_from_blueprint
            
            # Use the actual Agno Agent Generator for ultra-fast creation
            agent = await create_agent_from_blueprint(blueprint)
            
            # Store blueprint with agent for code generation
            agent.blueprint = blueprint
            
            # Generate code for the agent
            agent_code = self.generate_agent_code(blueprint['name'])
            
            # Register in the global agent registry
            agent_id = await agent_registry.register_agent(
                agent=agent,
                blueprint=blueprint,
                generated_code=agent_code
            )
            
            # Store agent ID for reference
            agent.registry_id = agent_id
            
            # Also register with Agno Manager for management
            self.created_agents[blueprint['name']] = agent
            
            print(f"✅ Agent {blueprint['name']} created and registered (ID: {agent_id})")
            
            return agent
            
        except Exception as e:
            print(f"Failed to create agent {blueprint['name']}: {e}")
            return None
    
    def generate_agent_code(self, agent_name: str) -> str:
        """Generate JavaScript/TypeScript code for a specific agent"""
        
        if agent_name not in self.created_agents:
            return ""
        
        agent = self.created_agents[agent_name]
        blueprint = agent.blueprint
        
        # Generate appropriate code based on agent type
        if blueprint['type'] == 'data_manager':
            return self._generate_crud_code(blueprint)
        elif blueprint['type'] == 'business_logic':
            return self._generate_business_logic_code(blueprint)
        elif blueprint['type'] == 'query_processor':
            return self._generate_filter_code(blueprint)
        elif blueprint['type'] == 'storage_manager':
            return self._generate_storage_code(blueprint)
        elif blueprint['type'] == 'analytics':
            return self._generate_statistics_code(blueprint)
        elif blueprint['type'] == 'ui_controller':
            return self._generate_ui_code(blueprint)
        elif blueprint['type'] == 'notification_service':
            return self._generate_notification_code(blueprint)
        else:
            return ""
    
    def _generate_crud_code(self, blueprint: Dict) -> str:
        """Generate CRUD operations code"""
        
        fields = blueprint['config']['fields']
        validation = blueprint['config'].get('validation_rules', {})
        
        return f"""
// {blueprint['name']} - Auto-generated by Agno Framework
class {blueprint['name']} {{
    constructor() {{
        this.tasks = JSON.parse(localStorage.getItem('tasks') || '[]');
        this.nextId = this.tasks.length > 0 ? 
            Math.max(...this.tasks.map(t => parseInt(t.id))) + 1 : 1;
    }}
    
    create(task) {{
        // Validation
        {self._generate_validation_code(validation)}
        
        const newTask = {{
            id: String(this.nextId++),
            ...task,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
        }};
        
        this.tasks.push(newTask);
        this.save();
        return newTask;
    }}
    
    read(id) {{
        return this.tasks.find(t => t.id === id);
    }}
    
    update(id, updates) {{
        const index = this.tasks.findIndex(t => t.id === id);
        if (index !== -1) {{
            this.tasks[index] = {{
                ...this.tasks[index],
                ...updates,
                updatedAt: new Date().toISOString()
            }};
            this.save();
            return this.tasks[index];
        }}
        return null;
    }}
    
    delete(id) {{
        const index = this.tasks.findIndex(t => t.id === id);
        if (index !== -1) {{
            const deleted = this.tasks.splice(index, 1)[0];
            this.save();
            return deleted;
        }}
        return null;
    }}
    
    list(filter = {{}}) {{
        let result = [...this.tasks];
        
        if (filter.completed !== undefined) {{
            result = result.filter(t => t.completed === filter.completed);
        }}
        
        if (filter.category) {{
            result = result.filter(t => t.category === filter.category);
        }}
        
        return result;
    }}
    
    save() {{
        localStorage.setItem('tasks', JSON.stringify(this.tasks));
    }}
}}

export default {blueprint['name']};
"""
    
    def _generate_validation_code(self, rules: Dict) -> str:
        """Generate validation code"""
        code = []
        for field, rule in rules.items():
            if rule.get('required'):
                code.append(f"if (!task.{field}) throw new Error('{field} is required');")
            if 'minLength' in rule:
                code.append(f"if (task.{field} && task.{field}.length < {rule['minLength']}) throw new Error('{field} is too short');")
            if 'maxLength' in rule:
                code.append(f"if (task.{field} && task.{field}.length > {rule['maxLength']}) throw new Error('{field} is too long');")
        return '\n        '.join(code)
    
    def _generate_business_logic_code(self, blueprint: Dict) -> str:
        """Generate business logic code"""
        # Implementation for other agent types...
        return f"// {blueprint['name']} implementation"
    
    def _generate_filter_code(self, blueprint: Dict) -> str:
        """Generate filter/search code"""
        return f"// {blueprint['name']} implementation"
    
    def _generate_storage_code(self, blueprint: Dict) -> str:
        """Generate storage management code"""
        return f"// {blueprint['name']} implementation"
    
    def _generate_statistics_code(self, blueprint: Dict) -> str:
        """Generate statistics code"""
        return f"// {blueprint['name']} implementation"
    
    def _generate_ui_code(self, blueprint: Dict) -> str:
        """Generate UI state management code"""
        return f"// {blueprint['name']} implementation"
    
    def _generate_notification_code(self, blueprint: Dict) -> str:
        """Generate notification code"""
        return f"// {blueprint['name']} implementation"
    
    async def test_generated_agents(self, test_input: str = "Create a test task") -> Dict[str, Any]:
        """
        Test the dynamically generated agents with a sample workflow
        """
        if not hasattr(self, 'runtime'):
            return {'error': 'Runtime not initialized. Call analyze_and_create_agents first.'}
        
        # Run complete workflow with runtime
        result = await self.runtime.run_complete_workflow(test_input)
        
        return {
            'test_input': test_input,
            'workflow_result': result,
            'agents_used': list(self.created_agents.keys()),
            'performance': self.runtime.executor.get_performance_metrics()
        }