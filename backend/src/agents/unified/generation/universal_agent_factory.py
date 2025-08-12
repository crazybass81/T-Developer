"""
Universal Agent Factory
어떤 요청이든 분석해서 필요한 최소 기능 에이전트들을 생성
"""

from typing import Dict, List, Any, Optional
import json
import re
from src.agno.agent_generator import AgnoAgentGenerator, AgentBlueprint

class UniversalAgentFactory:
    """범용 에이전트 팩토리 - 모든 종류의 앱에 대응"""
    
    def __init__(self):
        self.agent_generator = AgnoAgentGenerator()
        self.created_agents = {}
        
        # 기능 키워드와 필요한 에이전트 매핑
        self.feature_agent_mapping = {
            # 데이터 관련
            'crud': ['DataManager', 'ValidationService'],
            'database': ['DataManager', 'QueryProcessor', 'StorageManager'],
            'storage': ['StorageManager', 'CacheService'],
            
            # 사용자 관련
            'user': ['UserManager', 'AuthService', 'ProfileManager'],
            'auth': ['AuthService', 'TokenManager', 'SessionManager'],
            'login': ['AuthService', 'PasswordManager'],
            'profile': ['ProfileManager', 'AvatarService'],
            
            # 커뮤니케이션
            'chat': ['MessageManager', 'SocketService', 'NotificationService'],
            'message': ['MessageManager', 'QueueService'],
            'notification': ['NotificationService', 'AlertManager'],
            'email': ['EmailService', 'TemplateManager'],
            
            # 콘텐츠
            'blog': ['PostManager', 'CommentService', 'TagManager'],
            'article': ['ContentManager', 'EditorService'],
            'comment': ['CommentService', 'ModerationService'],
            'media': ['MediaManager', 'UploadService', 'ImageProcessor'],
            
            # 커머스
            'shop': ['ProductManager', 'CartService', 'OrderManager', 'PaymentService'],
            'product': ['ProductManager', 'InventoryService'],
            'cart': ['CartService', 'CheckoutService'],
            'payment': ['PaymentService', 'InvoiceManager'],
            'order': ['OrderManager', 'ShippingService'],
            
            # 분석
            'analytics': ['AnalyticsService', 'MetricsCollector'],
            'report': ['ReportGenerator', 'DataAggregator'],
            'dashboard': ['DashboardService', 'WidgetManager'],
            
            # UI/UX
            'form': ['FormBuilder', 'ValidationService'],
            'table': ['TableManager', 'PaginationService'],
            'search': ['SearchService', 'IndexManager'],
            'filter': ['FilterService', 'QueryBuilder'],
            
            # 작업 관리
            'task': ['TaskManager', 'SchedulerService'],
            'todo': ['TaskManager', 'PriorityService'],
            'calendar': ['CalendarService', 'EventManager'],
            'schedule': ['SchedulerService', 'CronManager'],
            
            # 실시간
            'realtime': ['WebSocketService', 'PubSubManager'],
            'live': ['StreamingService', 'BroadcastManager'],
            'socket': ['WebSocketService', 'ConnectionManager']
        }
    
    async def analyze_and_create_agents(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        요청을 분석하고 필요한 에이전트들을 동적으로 생성
        
        Args:
            requirements: 파싱된 요구사항
            
        Returns:
            생성된 에이전트들과 설정
        """
        
        # 1. 요구사항에서 필요한 에이전트 도출
        needed_agents = self._extract_needed_agents(requirements)
        
        # 2. 에이전트 블루프린트 생성
        blueprints = self._generate_blueprints(needed_agents, requirements)
        
        # 3. Agno를 사용해 에이전트 생성
        created_agents = {}
        for blueprint in blueprints:
            agent = await self._create_agent(blueprint)
            if agent:
                created_agents[blueprint['name']] = agent
                self.created_agents[blueprint['name']] = agent
        
        # 4. 에이전트별 코드 생성
        generated_code = {}
        for agent_name, agent in created_agents.items():
            code = self.generate_agent_code(agent_name, agent.blueprint if hasattr(agent, 'blueprint') else blueprints[0])
            generated_code[agent_name] = code
        
        return {
            'agents_created': len(created_agents),
            'agent_names': list(created_agents.keys()),
            'agents': created_agents,
            'blueprints': blueprints,
            'generated_code': generated_code
        }
    
    def _extract_needed_agents(self, requirements: Dict[str, Any]) -> List[str]:
        """요구사항에서 필요한 에이전트 추출"""
        
        needed_agents = set()
        
        # 사용자 입력 분석
        user_input = requirements.get('user_input', '').lower()
        description = requirements.get('description', '').lower()
        features = requirements.get('features', [])
        
        # 모든 텍스트 합치기
        all_text = f"{user_input} {description} {' '.join(features)}".lower()
        
        # 키워드 매칭으로 필요한 에이전트 찾기
        for keyword, agents in self.feature_agent_mapping.items():
            if keyword in all_text:
                needed_agents.update(agents)
        
        # 기본 에이전트 추가
        if not needed_agents:
            needed_agents.update(['DataManager', 'UIController', 'BusinessLogic'])
        
        return list(needed_agents)
    
    def _generate_blueprints(self, agent_names: List[str], requirements: Dict[str, Any]) -> List[Dict]:
        """에이전트 블루프린트 생성"""
        
        blueprints = []
        
        for agent_name in agent_names:
            blueprint = {
                'name': agent_name,
                'type': self._get_agent_type(agent_name),
                'config': self._get_agent_config(agent_name, requirements)
            }
            blueprints.append(blueprint)
        
        return blueprints
    
    def _get_agent_type(self, agent_name: str) -> str:
        """에이전트 이름에서 타입 추론"""
        
        if 'Manager' in agent_name or 'CRUD' in agent_name:
            return 'data_manager'
        elif 'Service' in agent_name:
            return 'business_logic'
        elif 'Query' in agent_name or 'Search' in agent_name:
            return 'query_processor'
        elif 'Storage' in agent_name or 'Cache' in agent_name:
            return 'storage_manager'
        elif 'Analytics' in agent_name or 'Metrics' in agent_name:
            return 'analytics'
        elif 'UI' in agent_name or 'Widget' in agent_name:
            return 'ui_controller'
        elif 'Notification' in agent_name or 'Alert' in agent_name:
            return 'notification_service'
        else:
            return 'business_logic'
    
    def _get_agent_config(self, agent_name: str, requirements: Dict[str, Any]) -> Dict:
        """에이전트별 설정 생성"""
        
        config = {
            'name': agent_name,
            'version': '1.0.0',
            'enabled': True
        }
        
        # 에이전트별 특수 설정
        if 'Auth' in agent_name:
            config['methods'] = ['login', 'logout', 'register', 'verify']
            config['token_type'] = 'JWT'
        elif 'Message' in agent_name:
            config['methods'] = ['send', 'receive', 'broadcast']
            config['max_message_size'] = 1024
        elif 'Product' in agent_name:
            config['fields'] = ['id', 'name', 'price', 'description', 'stock']
            config['operations'] = ['create', 'read', 'update', 'delete', 'search']
        elif 'Cart' in agent_name:
            config['methods'] = ['add_item', 'remove_item', 'update_quantity', 'checkout']
        
        return config
    
    async def _create_agent(self, blueprint: Dict) -> Any:
        """Agno를 사용해 에이전트 생성"""
        
        try:
            # AgentBlueprint 객체 생성
            agent_blueprint = AgentBlueprint(
                name=blueprint['name'],
                type=blueprint['type'],
                config=blueprint['config'],
                methods={}  # 메서드는 동적으로 생성됨
            )
            
            # Agno Generator로 에이전트 생성
            agent = await self.agent_generator.generate_agent(agent_blueprint)
            agent.blueprint = blueprint
            
            print(f"✅ Agent {blueprint['name']} created")
            return agent
            
        except Exception as e:
            print(f"❌ Failed to create agent {blueprint['name']}: {e}")
            return None
    
    def generate_agent_code(self, agent_name: str, blueprint: Dict) -> str:
        """에이전트 코드 생성"""
        
        agent_type = blueprint.get('type', 'business_logic')
        config = blueprint.get('config', {})
        
        # 기본 클래스 구조
        code = f"""
// {agent_name} - Auto-generated by Agno Framework
class {agent_name} {{
    constructor() {{
        this.name = '{agent_name}';
        this.version = '{config.get('version', '1.0.0')}';
        this.config = {json.dumps(config, indent=8)};
    }}
"""
        
        # 타입별 메서드 추가
        if agent_type == 'data_manager':
            code += self._generate_data_methods(config)
        elif agent_type == 'business_logic':
            code += self._generate_business_methods(config)
        elif agent_type == 'query_processor':
            code += self._generate_query_methods(config)
        elif agent_type == 'storage_manager':
            code += self._generate_storage_methods(config)
        elif agent_type == 'ui_controller':
            code += self._generate_ui_methods(config)
        elif agent_type == 'notification_service':
            code += self._generate_notification_methods(config)
        
        code += """
}

export default """ + agent_name + ";"
        
        return code
    
    def _generate_data_methods(self, config: Dict) -> str:
        """데이터 관리 메서드 생성"""
        
        operations = config.get('operations', ['create', 'read', 'update', 'delete'])
        fields = config.get('fields', ['id', 'name', 'data'])
        
        methods = ""
        
        if 'create' in operations:
            methods += f"""
    
    create(data) {{
        const id = Date.now().toString();
        const item = {{ id, ...data, createdAt: new Date() }};
        this.save(item);
        return item;
    }}
"""
        
        if 'read' in operations:
            methods += f"""
    
    read(id) {{
        return this.load(id);
    }}
"""
        
        if 'update' in operations:
            methods += f"""
    
    update(id, updates) {{
        const item = this.load(id);
        if (item) {{
            Object.assign(item, updates);
            item.updatedAt = new Date();
            this.save(item);
            return item;
        }}
        return null;
    }}
"""
        
        if 'delete' in operations:
            methods += f"""
    
    delete(id) {{
        return this.remove(id);
    }}
"""
        
        # 헬퍼 메서드
        methods += f"""
    
    save(item) {{
        if (typeof window !== 'undefined' && window.localStorage) {{
            const items = JSON.parse(localStorage.getItem('{config.get('name', 'items')}') || '{{}}');
            items[item.id] = item;
            localStorage.setItem('{config.get('name', 'items')}', JSON.stringify(items));
        }}
    }}
    
    load(id) {{
        if (typeof window !== 'undefined' && window.localStorage) {{
            const items = JSON.parse(localStorage.getItem('{config.get('name', 'items')}') || '{{}}');
            return items[id];
        }}
        return null;
    }}
    
    remove(id) {{
        if (typeof window !== 'undefined' && window.localStorage) {{
            const items = JSON.parse(localStorage.getItem('{config.get('name', 'items')}') || '{{}}');
            const item = items[id];
            delete items[id];
            localStorage.setItem('{config.get('name', 'items')}', JSON.stringify(items));
            return item;
        }}
        return null;
    }}
"""
        
        return methods
    
    def _generate_business_methods(self, config: Dict) -> str:
        """비즈니스 로직 메서드 생성"""
        
        methods = config.get('methods', ['process', 'validate'])
        code = ""
        
        for method in methods:
            code += f"""
    
    {method}(data) {{
        // {method} implementation
        console.log('{method} called with:', data);
        return {{ success: true, data }};
    }}
"""
        
        return code
    
    def _generate_query_methods(self, config: Dict) -> str:
        """쿼리 처리 메서드 생성"""
        
        return """
    
    search(query) {
        // Search implementation
        const results = [];
        // Add search logic here
        return results;
    }
    
    filter(items, criteria) {
        return items.filter(item => {
            for (const key in criteria) {
                if (item[key] !== criteria[key]) {
                    return false;
                }
            }
            return true;
        });
    }
    
    sort(items, field, order = 'asc') {
        return items.sort((a, b) => {
            if (order === 'asc') {
                return a[field] > b[field] ? 1 : -1;
            } else {
                return a[field] < b[field] ? 1 : -1;
            }
        });
    }
"""
    
    def _generate_storage_methods(self, config: Dict) -> str:
        """스토리지 메서드 생성"""
        
        return """
    
    store(key, value) {
        if (typeof window !== 'undefined' && window.localStorage) {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        }
        return false;
    }
    
    retrieve(key) {
        if (typeof window !== 'undefined' && window.localStorage) {
            const data = localStorage.getItem(key);
            return data ? JSON.parse(data) : null;
        }
        return null;
    }
    
    clear(key) {
        if (typeof window !== 'undefined' && window.localStorage) {
            localStorage.removeItem(key);
            return true;
        }
        return false;
    }
"""
    
    def _generate_ui_methods(self, config: Dict) -> str:
        """UI 컨트롤러 메서드 생성"""
        
        return """
    
    render(data) {
        // UI rendering logic
        return `<div>${JSON.stringify(data)}</div>`;
    }
    
    update(element, data) {
        if (element) {
            element.innerHTML = this.render(data);
        }
    }
    
    handleEvent(event, callback) {
        // Event handling logic
        if (callback && typeof callback === 'function') {
            callback(event);
        }
    }
"""
    
    def _generate_notification_methods(self, config: Dict) -> str:
        """알림 서비스 메서드 생성"""
        
        return """
    
    notify(message, type = 'info') {
        // Notification logic
        console.log(`[${type.toUpperCase()}] ${message}`);
        
        if (typeof window !== 'undefined' && window.Notification) {
            if (Notification.permission === 'granted') {
                new Notification(message);
            }
        }
    }
    
    alert(message) {
        this.notify(message, 'alert');
    }
    
    success(message) {
        this.notify(message, 'success');
    }
    
    error(message) {
        this.notify(message, 'error');
    }
"""


# 글로벌 인스턴스
universal_factory = UniversalAgentFactory()