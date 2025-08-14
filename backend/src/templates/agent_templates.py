"""
Agent Templates - Code generation templates
Size: < 6.5KB | Performance: < 3μs
Day 22: Phase 2 - Meta Agents
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class AgentTemplate:
    """Agent code template"""

    name: str
    type: str
    base_code: str
    imports: List[str]
    methods: Dict[str, str]


class TemplateLibrary:
    """Library of agent templates"""

    def __init__(self):
        self.templates = self._initialize_templates()

    def _initialize_templates(self):
        """Initialize template library"""
        return {
            "generic": self._generic_template(),
            "microservice": self._microservice_template(),
            "event_processor": self._event_processor_template(),
            "crud_handler": self._crud_template(),
            "data_processor": self._data_processor_template(),
        }

    def _generic_template(self):
        """Generic agent template"""
        return AgentTemplate(
            name="GenericAgent",
            type="generic",
            base_code='''
class {agent_name}:
    """Auto-generated agent"""

    def __init__(self):
        self.config = {{}}
        self.initialized = False

    async def execute(self, input_data):
        """Execute agent logic"""
        if not self.initialized:
            await self._initialize()

        validated = await self.validate(input_data)
        if not validated:
            return {{"status": "error", "message": "Validation failed"}}

        result = await self._process(input_data)
        return {{"status": "success", "data": result}}

    async def validate(self, input_data):
        """Validate input"""
        return input_data is not None

    async def _initialize(self):
        """Initialize agent"""
        self.initialized = True

    async def _process(self, input_data):
        """Process input"""
        return input_data
''',
            imports=["asyncio", "typing"],
            methods={
                "execute": "Main execution method",
                "validate": "Input validation",
                "_initialize": "Lazy initialization",
                "_process": "Core processing logic",
            },
        )

    def _microservice_template(self):
        """Microservice agent template"""
        return AgentTemplate(
            name="MicroserviceAgent",
            type="microservice",
            base_code='''
class {agent_name}:
    """Microservice agent"""

    def __init__(self):
        self.service_name = "{service_name}"
        self.port = {port}
        self.health_check_enabled = True

    async def start(self):
        """Start microservice"""
        await self._register_service()
        await self._setup_endpoints()
        return True

    async def stop(self):
        """Stop microservice"""
        await self._deregister_service()
        return True

    async def health_check(self):
        """Health check endpoint"""
        return {{"status": "healthy", "service": self.service_name}}

    async def process_request(self, request):
        """Process incoming request"""
        validated = await self.validate_request(request)
        if not validated:
            return {{"status": 400, "error": "Invalid request"}}

        result = await self._handle_request(request)
        return {{"status": 200, "data": result}}

    async def validate_request(self, request):
        """Validate request"""
        return "method" in request and "data" in request

    async def _register_service(self):
        """Register with service discovery"""
        pass

    async def _deregister_service(self):
        """Deregister from service discovery"""
        pass

    async def _setup_endpoints(self):
        """Setup API endpoints"""
        pass

    async def _handle_request(self, request):
        """Handle business logic"""
        return request.get("data")
''',
            imports=["asyncio", "typing", "aiohttp"],
            methods={
                "start": "Start service",
                "stop": "Stop service",
                "health_check": "Health check",
                "process_request": "Request handler",
                "validate_request": "Request validation",
            },
        )

    def _event_processor_template(self):
        """Event processor agent template"""
        return AgentTemplate(
            name="EventProcessorAgent",
            type="event_processor",
            base_code='''
class {agent_name}:
    """Event processor agent"""

    def __init__(self):
        self.event_types = []
        self.handlers = {{}}
        self.queue = None

    async def subscribe(self, event_type):
        """Subscribe to event type"""
        self.event_types.append(event_type)
        return True

    async def process_event(self, event):
        """Process incoming event"""
        event_type = event.get("type")

        if event_type not in self.event_types:
            return {{"status": "ignored", "reason": "Not subscribed"}}

        handler = self.handlers.get(event_type, self._default_handler)
        result = await handler(event)

        return {{"status": "processed", "result": result}}

    async def _default_handler(self, event):
        """Default event handler"""
        return {{"processed": True, "event_id": event.get("id")}}

    def register_handler(self, event_type, handler):
        """Register event handler"""
        self.handlers[event_type] = handler
''',
            imports=["asyncio", "typing", "json"],
            methods={
                "subscribe": "Subscribe to events",
                "process_event": "Process event",
                "register_handler": "Register handler",
                "_default_handler": "Default handler",
            },
        )

    def _crud_template(self):
        """CRUD handler agent template"""
        return AgentTemplate(
            name="CRUDAgent",
            type="crud_handler",
            base_code='''
class {agent_name}:
    """CRUD operations agent"""

    def __init__(self):
        self.model_name = "{model}"
        self.data_store = {{}}

    async def create(self, data):
        """Create entity"""
        entity_id = self._generate_id()
        self.data_store[entity_id] = data
        return {{"id": entity_id, "data": data}}

    async def read(self, entity_id):
        """Read entity"""
        data = self.data_store.get(entity_id)
        if not data:
            return {{"error": "Not found"}}
        return {{"id": entity_id, "data": data}}

    async def update(self, entity_id, data):
        """Update entity"""
        if entity_id not in self.data_store:
            return {{"error": "Not found"}}
        self.data_store[entity_id] = data
        return {{"id": entity_id, "data": data}}

    async def delete(self, entity_id):
        """Delete entity"""
        if entity_id not in self.data_store:
            return {{"error": "Not found"}}
        del self.data_store[entity_id]
        return {{"id": entity_id, "deleted": True}}

    async def list(self, filters=None):
        """List entities"""
        results = list(self.data_store.values())
        return {{"count": len(results), "data": results}}

    def _generate_id(self):
        """Generate unique ID"""
        import uuid
        return str(uuid.uuid4())
''',
            imports=["asyncio", "typing", "uuid"],
            methods={
                "create": "Create entity",
                "read": "Read entity",
                "update": "Update entity",
                "delete": "Delete entity",
                "list": "List entities",
            },
        )

    def _data_processor_template(self):
        """Data processor agent template"""
        return AgentTemplate(
            name="DataProcessorAgent",
            type="data_processor",
            base_code='''
class {agent_name}:
    """Data processing agent"""

    def __init__(self):
        self.pipeline = []
        self.validators = []
        self.transformers = []

    async def process(self, data):
        """Process data through pipeline"""
        # Validate
        for validator in self.validators:
            if not await validator(data):
                return {{"status": "error", "stage": "validation"}}

        # Transform
        for transformer in self.transformers:
            data = await transformer(data)

        # Process through pipeline
        for step in self.pipeline:
            data = await step(data)

        return {{"status": "success", "data": data}}

    def add_validator(self, validator):
        """Add data validator"""
        self.validators.append(validator)

    def add_transformer(self, transformer):
        """Add data transformer"""
        self.transformers.append(transformer)

    def add_pipeline_step(self, step):
        """Add pipeline step"""
        self.pipeline.append(step)

    async def validate_schema(self, data):
        """Validate data schema"""
        return isinstance(data, dict)

    async def clean_data(self, data):
        """Clean data"""
        if isinstance(data, dict):
            return {{k: v for k, v in data.items() if v is not None}}
        return data
''',
            imports=["asyncio", "typing", "json"],
            methods={
                "process": "Main processing",
                "add_validator": "Add validator",
                "add_transformer": "Add transformer",
                "add_pipeline_step": "Add pipeline step",
                "validate_schema": "Schema validation",
                "clean_data": "Data cleaning",
            },
        )

    def get_template(self, template_type):
        """Get template by type"""
        return self.templates.get(template_type, self.templates["generic"])

    def list_templates(self):
        """List available templates"""
        return list(self.templates.keys())

    def create_custom_template(self, name, base_code, imports, methods):
        """Create custom template"""
        template = AgentTemplate(
            name=name, type="custom", base_code=base_code, imports=imports, methods=methods
        )
        self.templates[name] = template
        return template


# Global instance
library = None


def get_library():
    """Get template library instance"""
    global library
    if not library:
        library = TemplateLibrary()
    return library


def main():
    """Test template library"""
    lib = get_library()

    print("Available templates:")
    for template_name in lib.list_templates():
        template = lib.get_template(template_name)
        print(f"  - {template_name}: {template.type}")
        print(f"    Methods: {list(template.methods.keys())}")


if __name__ == "__main__":
    main()
