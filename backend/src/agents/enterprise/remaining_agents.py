"""
Remaining Enterprise Agents - Consolidated Implementation
Component Decision, Match Rate, Search, Generation, Assembly, Download Agents
"""

from typing import Dict, Any, Optional, List, Tuple
import asyncio
import json
import re
import hashlib
import zipfile
import io
import os
from datetime import datetime
from pathlib import Path

from .base_agent import EnterpriseBaseAgent, AgentConfig, AgentContext
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic


# ============= Component Decision Agent =============
class EnterpriseComponentDecisionAgent(EnterpriseBaseAgent):
    """
    Decides which components to use based on requirements
    """
    
    def __init__(self):
        config = AgentConfig(
            name="component_decision_agent",
            version="1.0.0",
            timeout=20,
            retries=2,
            cache_ttl=3600
        )
        super().__init__(config)
        
        self.component_library = {
            "authentication": [
                {"name": "JWT Auth", "complexity": "low", "security": "high"},
                {"name": "OAuth2", "complexity": "medium", "security": "very_high"},
                {"name": "Session Auth", "complexity": "low", "security": "medium"}
            ],
            "database": [
                {"name": "PostgreSQL", "type": "relational", "scalability": "high"},
                {"name": "MongoDB", "type": "document", "scalability": "very_high"},
                {"name": "Redis", "type": "cache", "performance": "very_high"}
            ],
            "messaging": [
                {"name": "RabbitMQ", "reliability": "high", "complexity": "medium"},
                {"name": "Kafka", "throughput": "very_high", "complexity": "high"},
                {"name": "Redis PubSub", "simplicity": "high", "throughput": "medium"}
            ]
        }
    
    async def process(self, input_data: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Select optimal components"""
        requirements = input_data.get("requirements", {})
        parsed_data = input_data.get("parsed_data", {})
        
        # Analyze requirements
        component_needs = self._analyze_component_needs(requirements, parsed_data)
        
        # Select components
        selected_components = {}
        for category, needs in component_needs.items():
            selected_components[category] = self._select_best_component(category, needs)
        
        # Generate component configuration
        configuration = self._generate_configuration(selected_components, requirements)
        
        return {
            "selected_components": selected_components,
            "configuration": configuration,
            "dependencies": self._get_dependencies(selected_components),
            "integration_points": self._identify_integration_points(selected_components)
        }
    
    def _analyze_component_needs(self, requirements: Dict, parsed_data: Dict) -> Dict:
        """Analyze what components are needed"""
        needs = {}
        
        features = requirements.get("features", [])
        features_str = " ".join([str(f) for f in features]).lower()
        
        # Authentication needs
        if any(auth in features_str for auth in ["login", "auth", "user", "account"]):
            needs["authentication"] = {
                "required": True,
                "level": "high" if "enterprise" in str(requirements) else "medium"
            }
        
        # Database needs
        needs["database"] = {
            "type": "relational" if "transaction" in features_str else "document",
            "scalability": requirements.get("non_functional_requirements", {}).get("scalability", {})
        }
        
        # Messaging needs
        if any(msg in features_str for msg in ["real-time", "chat", "notification", "queue"]):
            needs["messaging"] = {
                "required": True,
                "throughput": "high" if "real-time" in features_str else "medium"
            }
        
        return needs
    
    def _select_best_component(self, category: str, needs: Dict) -> Dict:
        """Select best component for category"""
        components = self.component_library.get(category, [])
        
        if not components:
            return {"name": "default", "reason": "No components available"}
        
        # Simple scoring based on needs matching
        best_component = components[0]
        best_score = 0
        
        for component in components:
            score = sum(1 for key, value in needs.items() 
                       if key in component and str(component[key]).lower() == str(value).lower())
            if score > best_score:
                best_score = score
                best_component = component
        
        return best_component
    
    def _generate_configuration(self, components: Dict, requirements: Dict) -> Dict:
        """Generate component configuration"""
        config = {}
        
        for category, component in components.items():
            if category == "authentication":
                config[category] = {
                    "type": component.get("name", "JWT"),
                    "token_expiry": "24h",
                    "refresh_token": True
                }
            elif category == "database":
                config[category] = {
                    "type": component.get("name", "PostgreSQL"),
                    "connection_pool": 20,
                    "max_connections": 100
                }
            elif category == "messaging":
                config[category] = {
                    "type": component.get("name", "Redis"),
                    "max_retries": 3,
                    "timeout": 5000
                }
        
        return config
    
    def _get_dependencies(self, components: Dict) -> List[str]:
        """Get required dependencies"""
        deps = []
        
        for category, component in components.items():
            comp_name = component.get("name", "").lower()
            
            if "jwt" in comp_name:
                deps.append("jsonwebtoken")
            elif "oauth" in comp_name:
                deps.append("passport-oauth2")
            elif "postgres" in comp_name:
                deps.append("pg")
            elif "mongo" in comp_name:
                deps.append("mongodb")
            elif "redis" in comp_name:
                deps.append("redis")
            elif "rabbit" in comp_name:
                deps.append("amqplib")
            elif "kafka" in comp_name:
                deps.append("kafkajs")
        
        return deps
    
    def _identify_integration_points(self, components: Dict) -> List[Dict]:
        """Identify where components integrate"""
        integration_points = []
        
        if "authentication" in components:
            integration_points.append({
                "component": "authentication",
                "integrates_with": ["api_gateway", "user_service"],
                "type": "middleware"
            })
        
        if "database" in components:
            integration_points.append({
                "component": "database",
                "integrates_with": ["data_access_layer", "orm"],
                "type": "data_layer"
            })
        
        if "messaging" in components:
            integration_points.append({
                "component": "messaging",
                "integrates_with": ["event_bus", "notification_service"],
                "type": "async_communication"
            })
        
        return integration_points


# ============= Match Rate Agent =============
class EnterpriseMatchRateAgent(EnterpriseBaseAgent):
    """
    Calculates match rates between requirements and existing templates
    """
    
    def __init__(self):
        config = AgentConfig(
            name="match_rate_agent",
            version="1.0.0",
            timeout=15,
            retries=2,
            cache_ttl=3600
        )
        super().__init__(config)
        
        self.template_library = self._load_templates()
    
    def _load_templates(self) -> List[Dict]:
        """Load template library"""
        return [
            {
                "id": "ecommerce_basic",
                "name": "E-commerce Platform",
                "features": ["product", "cart", "checkout", "payment", "user", "order"],
                "tech_stack": ["react", "node", "postgres", "stripe"],
                "complexity": "medium"
            },
            {
                "id": "saas_dashboard",
                "name": "SaaS Dashboard",
                "features": ["dashboard", "analytics", "user", "subscription", "api"],
                "tech_stack": ["react", "python", "postgres", "redis"],
                "complexity": "high"
            },
            {
                "id": "social_platform",
                "name": "Social Platform",
                "features": ["user", "post", "comment", "like", "follow", "notification"],
                "tech_stack": ["react", "node", "mongodb", "redis"],
                "complexity": "high"
            },
            {
                "id": "blog_cms",
                "name": "Blog/CMS",
                "features": ["post", "category", "comment", "user", "admin"],
                "tech_stack": ["nextjs", "node", "postgres"],
                "complexity": "low"
            }
        ]
    
    async def process(self, input_data: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Calculate template match rates"""
        requirements = input_data.get("requirements", {})
        
        # Calculate match scores for each template
        match_results = []
        for template in self.template_library:
            score = self._calculate_match_score(requirements, template)
            match_results.append({
                "template": template,
                "match_score": score,
                "matching_features": self._get_matching_features(requirements, template),
                "missing_features": self._get_missing_features(requirements, template)
            })
        
        # Sort by match score
        match_results.sort(key=lambda x: x["match_score"], reverse=True)
        
        # Select best matches
        best_matches = match_results[:3]
        
        return {
            "best_match": best_matches[0] if best_matches else None,
            "alternatives": best_matches[1:] if len(best_matches) > 1 else [],
            "all_matches": match_results,
            "recommendation": self._generate_recommendation(best_matches, requirements)
        }
    
    def _calculate_match_score(self, requirements: Dict, template: Dict) -> float:
        """Calculate match score between requirements and template"""
        score = 0.0
        weights = {
            "features": 0.4,
            "tech_stack": 0.3,
            "complexity": 0.2,
            "project_type": 0.1
        }
        
        # Feature matching
        req_features = set(str(f).lower() for f in requirements.get("features", []))
        template_features = set(template["features"])
        feature_overlap = len(req_features & template_features) / max(len(req_features | template_features), 1)
        score += feature_overlap * weights["features"]
        
        # Tech stack matching
        req_tech = requirements.get("technical_requirements", {})
        req_frameworks = set(str(f).lower() for f in req_tech.get("frameworks", []))
        template_tech = set(template["tech_stack"])
        tech_overlap = len(req_frameworks & template_tech) / max(len(req_frameworks | template_tech), 1)
        score += tech_overlap * weights["tech_stack"]
        
        # Complexity matching
        req_complexity = requirements.get("estimated_complexity", "medium")
        if req_complexity == template["complexity"]:
            score += weights["complexity"]
        
        # Project type matching
        req_type = requirements.get("project_type", "")
        if any(t in template["name"].lower() for t in req_type.lower().split()):
            score += weights["project_type"]
        
        return round(score * 100, 2)
    
    def _get_matching_features(self, requirements: Dict, template: Dict) -> List[str]:
        """Get matching features"""
        req_features = set(str(f).lower() for f in requirements.get("features", []))
        template_features = set(template["features"])
        return list(req_features & template_features)
    
    def _get_missing_features(self, requirements: Dict, template: Dict) -> List[str]:
        """Get missing features"""
        req_features = set(str(f).lower() for f in requirements.get("features", []))
        template_features = set(template["features"])
        return list(req_features - template_features)
    
    def _generate_recommendation(self, matches: List[Dict], requirements: Dict) -> Dict:
        """Generate recommendation based on matches"""
        if not matches:
            return {
                "action": "create_custom",
                "reason": "No suitable templates found",
                "confidence": 0.0
            }
        
        best = matches[0]
        score = best["match_score"]
        
        if score > 80:
            return {
                "action": "use_template",
                "template": best["template"]["id"],
                "reason": f"High match score ({score}%)",
                "confidence": score / 100
            }
        elif score > 60:
            return {
                "action": "adapt_template",
                "template": best["template"]["id"],
                "reason": f"Moderate match, adaptation needed",
                "confidence": score / 100,
                "adaptations": best["missing_features"]
            }
        else:
            return {
                "action": "create_hybrid",
                "templates": [m["template"]["id"] for m in matches[:2]],
                "reason": "Low match scores, combine templates",
                "confidence": score / 100
            }


# ============= Search Agent =============
class EnterpriseSearchAgent(EnterpriseBaseAgent):
    """
    Searches for code snippets, patterns, and solutions
    """
    
    def __init__(self):
        config = AgentConfig(
            name="search_agent",
            version="1.0.0",
            timeout=25,
            retries=3,
            cache_ttl=7200
        )
        super().__init__(config)
        
        self.code_repository = self._initialize_code_repository()
    
    def _initialize_code_repository(self) -> Dict:
        """Initialize code repository"""
        return {
            "snippets": {
                "auth_jwt": {
                    "language": "javascript",
                    "code": """
const jwt = require('jsonwebtoken');

function generateToken(user) {
    return jwt.sign(
        { id: user.id, email: user.email },
        process.env.JWT_SECRET,
        { expiresIn: '24h' }
    );
}

function verifyToken(token) {
    try {
        return jwt.verify(token, process.env.JWT_SECRET);
    } catch (error) {
        throw new Error('Invalid token');
    }
}
"""
                },
                "db_connection": {
                    "language": "python",
                    "code": """
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
"""
                }
            },
            "patterns": {
                "repository": "Repository pattern for data access",
                "factory": "Factory pattern for object creation",
                "singleton": "Singleton pattern for single instance"
            }
        }
    
    async def process(self, input_data: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Search for relevant code and patterns"""
        search_query = input_data.get("query", "")
        search_type = input_data.get("type", "all")
        requirements = input_data.get("requirements", {})
        
        results = {
            "code_snippets": [],
            "patterns": [],
            "libraries": [],
            "best_practices": []
        }
        
        # Search code snippets
        if search_type in ["all", "code"]:
            results["code_snippets"] = self._search_code_snippets(search_query, requirements)
        
        # Search patterns
        if search_type in ["all", "patterns"]:
            results["patterns"] = self._search_patterns(requirements)
        
        # Search libraries
        if search_type in ["all", "libraries"]:
            results["libraries"] = await self._search_libraries(requirements)
        
        # Search best practices
        if search_type in ["all", "practices"]:
            results["best_practices"] = self._search_best_practices(requirements)
        
        return {
            "results": results,
            "relevance_scores": self._calculate_relevance(results, requirements),
            "recommendations": self._generate_search_recommendations(results, requirements)
        }
    
    def _search_code_snippets(self, query: str, requirements: Dict) -> List[Dict]:
        """Search for relevant code snippets"""
        snippets = []
        
        # Search in repository
        for key, snippet in self.code_repository["snippets"].items():
            if query.lower() in key.lower():
                snippets.append({
                    "id": key,
                    "language": snippet["language"],
                    "code": snippet["code"],
                    "relevance": 0.9
                })
        
        # Add snippets based on requirements
        features = requirements.get("features", [])
        for feature in features:
            feature_str = str(feature).lower()
            if "auth" in feature_str and not snippets:
                snippets.append({
                    "id": "auth_jwt",
                    "language": "javascript",
                    "code": self.code_repository["snippets"]["auth_jwt"]["code"],
                    "relevance": 0.8
                })
        
        return snippets
    
    def _search_patterns(self, requirements: Dict) -> List[Dict]:
        """Search for design patterns"""
        patterns = []
        
        complexity = requirements.get("estimated_complexity", "medium")
        
        if complexity in ["high", "very_high"]:
            patterns.extend([
                {"name": "Repository Pattern", "use_case": "Data access abstraction"},
                {"name": "Service Layer", "use_case": "Business logic encapsulation"},
                {"name": "CQRS", "use_case": "Command Query Responsibility Segregation"}
            ])
        else:
            patterns.extend([
                {"name": "MVC", "use_case": "Model-View-Controller separation"},
                {"name": "Singleton", "use_case": "Single instance management"}
            ])
        
        return patterns
    
    async def _search_libraries(self, requirements: Dict) -> List[Dict]:
        """Search for relevant libraries"""
        libraries = []
        
        tech_reqs = requirements.get("technical_requirements", {})
        languages = tech_reqs.get("languages", [])
        
        library_map = {
            "python": ["fastapi", "sqlalchemy", "pydantic", "celery"],
            "javascript": ["express", "react", "axios", "mongoose"],
            "typescript": ["nestjs", "typeorm", "class-validator"]
        }
        
        for lang in languages:
            if lang in library_map:
                for lib in library_map[lang][:3]:
                    libraries.append({
                        "name": lib,
                        "language": lang,
                        "purpose": self._get_library_purpose(lib)
                    })
        
        return libraries
    
    def _get_library_purpose(self, library: str) -> str:
        """Get library purpose"""
        purposes = {
            "fastapi": "Modern web API framework",
            "express": "Web application framework",
            "react": "UI library",
            "sqlalchemy": "SQL toolkit and ORM",
            "mongoose": "MongoDB object modeling"
        }
        return purposes.get(library, "General purpose library")
    
    def _search_best_practices(self, requirements: Dict) -> List[Dict]:
        """Search for best practices"""
        practices = [
            {"category": "security", "practice": "Use environment variables for secrets"},
            {"category": "performance", "practice": "Implement caching strategy"},
            {"category": "scalability", "practice": "Use horizontal scaling"},
            {"category": "testing", "practice": "Write unit and integration tests"},
            {"category": "documentation", "practice": "Document API endpoints"}
        ]
        
        return practices
    
    def _calculate_relevance(self, results: Dict, requirements: Dict) -> Dict:
        """Calculate relevance scores"""
        return {
            "code_snippets": len(results["code_snippets"]) / 10,
            "patterns": len(results["patterns"]) / 5,
            "libraries": len(results["libraries"]) / 10,
            "best_practices": len(results["best_practices"]) / 5
        }
    
    def _generate_search_recommendations(self, results: Dict, requirements: Dict) -> List[str]:
        """Generate recommendations based on search results"""
        recommendations = []
        
        if results["code_snippets"]:
            recommendations.append("Found relevant code snippets - review and adapt")
        
        if results["patterns"]:
            recommendations.append(f"Implement {results['patterns'][0]['name']} for better architecture")
        
        if results["libraries"]:
            recommendations.append(f"Consider using {results['libraries'][0]['name']} library")
        
        return recommendations


# ============= Generation Agent (CRITICAL) =============
class EnterpriseGenerationAgent(EnterpriseBaseAgent):
    """
    Core agent for generating actual code
    """
    
    def __init__(self):
        config = AgentConfig(
            name="generation_agent",
            version="1.0.0",
            timeout=60,  # Longer timeout for generation
            retries=3,
            cache_ttl=1800
        )
        super().__init__(config)
        
        # AI providers for code generation
        self.openai_client: Optional[AsyncOpenAI] = None
        self.anthropic_client: Optional[AsyncAnthropic] = None
    
    async def _custom_initialize(self):
        """Initialize AI providers"""
        try:
            self.openai_client = AsyncOpenAI(
                api_key=await self._get_secret("OPENAI_API_KEY")
            )
            self.anthropic_client = AsyncAnthropic(
                api_key=await self._get_secret("ANTHROPIC_API_KEY")
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize AI providers: {e}")
    
    async def process(self, input_data: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Generate code based on all previous agent outputs"""
        
        # Extract all relevant data
        requirements = input_data.get("requirements", {})
        ui_framework = input_data.get("ui_framework", {})
        components = input_data.get("components", {})
        patterns = input_data.get("patterns", [])
        
        self.logger.info(
            "Starting code generation",
            project_type=requirements.get("project_type"),
            trace_id=context.trace_id
        )
        
        # Generate project structure
        project_structure = await self._generate_project_structure(requirements, ui_framework)
        
        # Generate core files
        generated_files = {}
        
        # Generate package.json / requirements.txt
        generated_files["package_file"] = await self._generate_package_file(requirements, components)
        
        # Generate main application file
        generated_files["main_app"] = await self._generate_main_app(requirements, ui_framework, components)
        
        # Generate API routes
        if "api" in str(requirements.get("features", [])).lower():
            generated_files["api_routes"] = await self._generate_api_routes(requirements)
        
        # Generate database models
        if components.get("database"):
            generated_files["models"] = await self._generate_models(requirements)
        
        # Generate frontend components
        if ui_framework.get("selected_framework"):
            generated_files["frontend"] = await self._generate_frontend(requirements, ui_framework)
        
        # Generate configuration files
        generated_files["config"] = await self._generate_config_files(requirements, components)
        
        # Generate tests
        generated_files["tests"] = await self._generate_tests(requirements)
        
        # Generate documentation
        generated_files["docs"] = await self._generate_documentation(requirements, project_structure)
        
        return {
            "project_structure": project_structure,
            "generated_files": generated_files,
            "file_count": self._count_files(generated_files),
            "lines_of_code": self._count_lines(generated_files),
            "generation_metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "version": self.config.version,
                "ai_provider": "openai" if self.openai_client else "anthropic"
            }
        }
    
    async def _generate_project_structure(self, requirements: Dict, ui_framework: Dict) -> Dict:
        """Generate project directory structure"""
        
        project_type = requirements.get("project_type", "web_app")
        
        if project_type == "web_app":
            return {
                "root": {
                    "src": {
                        "components": {},
                        "pages": {},
                        "services": {},
                        "utils": {},
                        "styles": {}
                    },
                    "public": {},
                    "tests": {},
                    "config": {},
                    "docs": {}
                }
            }
        elif project_type == "api":
            return {
                "root": {
                    "src": {
                        "routes": {},
                        "controllers": {},
                        "models": {},
                        "services": {},
                        "middleware": {},
                        "utils": {}
                    },
                    "tests": {},
                    "config": {},
                    "docs": {}
                }
            }
        else:
            return {"root": {"src": {}, "tests": {}, "docs": {}}}
    
    async def _generate_package_file(self, requirements: Dict, components: Dict) -> Dict:
        """Generate package.json or requirements.txt"""
        
        tech_reqs = requirements.get("technical_requirements", {})
        languages = tech_reqs.get("languages", ["javascript"])
        
        if "python" in languages:
            return await self._generate_requirements_txt(requirements, components)
        else:
            return await self._generate_package_json(requirements, components)
    
    async def _generate_requirements_txt(self, requirements: Dict, components: Dict) -> Dict:
        """Generate Python requirements.txt"""
        
        deps = [
            "fastapi==0.104.1",
            "uvicorn==0.24.0",
            "sqlalchemy==2.0.23",
            "pydantic==2.5.0",
            "python-jose==3.3.0",
            "passlib==1.7.4",
            "python-multipart==0.0.6",
            "redis==5.0.1",
            "celery==5.3.4",
            "pytest==7.4.3",
            "pytest-asyncio==0.21.1"
        ]
        
        # Add component-specific dependencies
        if components.get("database", {}).get("name") == "PostgreSQL":
            deps.append("psycopg2-binary==2.9.9")
        elif components.get("database", {}).get("name") == "MongoDB":
            deps.append("pymongo==4.6.0")
        
        return {
            "filename": "requirements.txt",
            "content": "\n".join(deps)
        }
    
    async def _generate_package_json(self, requirements: Dict, components: Dict) -> Dict:
        """Generate package.json"""
        
        package = {
            "name": requirements.get("project_name", "my-project").lower().replace(" ", "-"),
            "version": "1.0.0",
            "description": requirements.get("description", "")[:100],
            "main": "src/index.js",
            "scripts": {
                "start": "node src/index.js",
                "dev": "nodemon src/index.js",
                "test": "jest",
                "build": "webpack --mode production"
            },
            "dependencies": {
                "express": "^4.18.2",
                "cors": "^2.8.5",
                "dotenv": "^16.3.1",
                "helmet": "^7.1.0"
            },
            "devDependencies": {
                "nodemon": "^3.0.1",
                "jest": "^29.7.0",
                "eslint": "^8.54.0"
            }
        }
        
        # Add component dependencies
        component_deps = components.get("dependencies", [])
        for dep in component_deps:
            package["dependencies"][dep] = "latest"
        
        return {
            "filename": "package.json",
            "content": json.dumps(package, indent=2)
        }
    
    async def _generate_main_app(self, requirements: Dict, ui_framework: Dict, components: Dict) -> Dict:
        """Generate main application file"""
        
        tech_reqs = requirements.get("technical_requirements", {})
        languages = tech_reqs.get("languages", ["javascript"])
        
        if "python" in languages:
            return await self._generate_python_main(requirements, components)
        else:
            return await self._generate_javascript_main(requirements, components)
    
    async def _generate_python_main(self, requirements: Dict, components: Dict) -> Dict:
        """Generate Python main.py"""
        
        code = '''from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers
from src.routes import api_router
from src.database import engine, Base

# Create tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up...")
    yield
    # Shutdown
    print("Shutting down...")

# Create FastAPI app
app = FastAPI(
    title="''' + requirements.get("project_name", "API") + '''",
    description="''' + requirements.get("description", "")[:200] + '''",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENV") == "development"
    )
'''
        
        return {
            "filename": "src/main.py",
            "content": code
        }
    
    async def _generate_javascript_main(self, requirements: Dict, components: Dict) -> Dict:
        """Generate JavaScript index.js"""
        
        code = '''const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

// Import routes
const apiRoutes = require('./routes/api');

// Create Express app
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.use('/api/v1', apiRoutes);

// Root endpoint
app.get('/', (req, res) => {
    res.json({
        message: 'API is running',
        version: '1.0.0'
    });
});

// Health check
app.get('/health', (req, res) => {
    res.json({ status: 'healthy' });
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({
        error: 'Something went wrong!',
        message: err.message
    });
});

// Start server
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});

module.exports = app;
'''
        
        return {
            "filename": "src/index.js",
            "content": code
        }
    
    async def _generate_api_routes(self, requirements: Dict) -> Dict:
        """Generate API routes"""
        
        features = requirements.get("features", [])
        routes = []
        
        # Generate routes based on features
        for feature in features:
            feature_str = str(feature).lower()
            if "user" in feature_str or "auth" in feature_str:
                routes.append(self._generate_auth_routes())
            elif "product" in feature_str:
                routes.append(self._generate_crud_routes("product"))
            elif "order" in feature_str:
                routes.append(self._generate_crud_routes("order"))
        
        return {
            "filename": "src/routes/api.js",
            "content": "\n\n".join(routes) if routes else self._generate_default_routes()
        }
    
    def _generate_auth_routes(self) -> str:
        """Generate authentication routes"""
        return '''// Authentication routes
router.post('/auth/register', async (req, res) => {
    // Registration logic
    res.json({ message: 'User registered' });
});

router.post('/auth/login', async (req, res) => {
    // Login logic
    res.json({ token: 'jwt-token' });
});

router.post('/auth/logout', async (req, res) => {
    // Logout logic
    res.json({ message: 'Logged out' });
});'''
    
    def _generate_crud_routes(self, entity: str) -> str:
        """Generate CRUD routes for entity"""
        return f'''// {entity.capitalize()} routes
router.get('/{entity}s', async (req, res) => {{
    // Get all {entity}s
    res.json({{ {entity}s: [] }});
}});

router.get('/{entity}s/:id', async (req, res) => {{
    // Get {entity} by ID
    res.json({{ {entity}: {{}} }});
}});

router.post('/{entity}s', async (req, res) => {{
    // Create {entity}
    res.json({{ message: '{entity.capitalize()} created' }});
}});

router.put('/{entity}s/:id', async (req, res) => {{
    // Update {entity}
    res.json({{ message: '{entity.capitalize()} updated' }});
}});

router.delete('/{entity}s/:id', async (req, res) => {{
    // Delete {entity}
    res.json({{ message: '{entity.capitalize()} deleted' }});
}});'''
    
    def _generate_default_routes(self) -> str:
        """Generate default routes"""
        return '''const express = require('express');
const router = express.Router();

// Default route
router.get('/', (req, res) => {
    res.json({ message: 'API v1' });
});

module.exports = router;'''
    
    async def _generate_models(self, requirements: Dict) -> Dict:
        """Generate database models"""
        
        models = []
        features = requirements.get("features", [])
        
        for feature in features:
            feature_str = str(feature).lower()
            if "user" in feature_str:
                models.append(self._generate_user_model())
            elif "product" in feature_str:
                models.append(self._generate_product_model())
        
        return {
            "filename": "src/models/index.js",
            "content": "\n\n".join(models) if models else "// Database models"
        }
    
    def _generate_user_model(self) -> str:
        """Generate user model"""
        return '''// User model
const UserSchema = {
    id: { type: 'UUID', primaryKey: true },
    email: { type: 'String', unique: true, required: true },
    username: { type: 'String', unique: true, required: true },
    passwordHash: { type: 'String', required: true },
    createdAt: { type: 'Date', default: Date.now },
    updatedAt: { type: 'Date', default: Date.now }
};'''
    
    def _generate_product_model(self) -> str:
        """Generate product model"""
        return '''// Product model
const ProductSchema = {
    id: { type: 'UUID', primaryKey: true },
    name: { type: 'String', required: true },
    description: { type: 'String' },
    price: { type: 'Number', required: true },
    stock: { type: 'Number', default: 0 },
    createdAt: { type: 'Date', default: Date.now }
};'''
    
    async def _generate_frontend(self, requirements: Dict, ui_framework: Dict) -> Dict:
        """Generate frontend components"""
        
        framework = ui_framework.get("selected_framework", {}).get("id", "react")
        
        if framework == "react":
            return await self._generate_react_app(requirements)
        elif framework == "vue":
            return await self._generate_vue_app(requirements)
        else:
            return {"filename": "src/App.js", "content": "// Frontend app"}
    
    async def _generate_react_app(self, requirements: Dict) -> Dict:
        """Generate React app"""
        
        code = '''import React from 'react';
import './App.css';

function App() {
    return (
        <div className="App">
            <header className="App-header">
                <h1>''' + requirements.get("project_name", "My App") + '''</h1>
                <p>''' + requirements.get("description", "")[:100] + '''</p>
            </header>
            <main>
                {/* Your components here */}
            </main>
        </div>
    );
}

export default App;'''
        
        return {
            "filename": "src/App.js",
            "content": code
        }
    
    async def _generate_vue_app(self, requirements: Dict) -> Dict:
        """Generate Vue app"""
        
        code = '''<template>
    <div id="app">
        <header>
            <h1>{{ projectName }}</h1>
            <p>{{ description }}</p>
        </header>
        <main>
            <!-- Your components here -->
        </main>
    </div>
</template>

<script>
export default {
    name: 'App',
    data() {
        return {
            projectName: "''' + requirements.get("project_name", "My App") + '''",
            description: "''' + requirements.get("description", "")[:100] + '''"
        }
    }
}
</script>'''
        
        return {
            "filename": "src/App.vue",
            "content": code
        }
    
    async def _generate_config_files(self, requirements: Dict, components: Dict) -> List[Dict]:
        """Generate configuration files"""
        
        configs = []
        
        # .env file
        configs.append({
            "filename": ".env",
            "content": '''# Environment variables
NODE_ENV=development
PORT=3000
DATABASE_URL=postgresql://user:password@localhost/dbname
JWT_SECRET=your-secret-key
REDIS_URL=redis://localhost:6379'''
        })
        
        # .gitignore
        configs.append({
            "filename": ".gitignore",
            "content": '''node_modules/
.env
.env.local
dist/
build/
*.log
.DS_Store
coverage/
.vscode/'''
        })
        
        # Dockerfile
        configs.append({
            "filename": "Dockerfile",
            "content": '''FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 3000
CMD ["npm", "start"]'''
        })
        
        return configs
    
    async def _generate_tests(self, requirements: Dict) -> Dict:
        """Generate test files"""
        
        code = '''// Unit tests
describe('API Tests', () => {
    test('Health check endpoint', async () => {
        const response = await request(app).get('/health');
        expect(response.status).toBe(200);
        expect(response.body.status).toBe('healthy');
    });
    
    test('Root endpoint', async () => {
        const response = await request(app).get('/');
        expect(response.status).toBe(200);
        expect(response.body.message).toBeDefined();
    });
});'''
        
        return {
            "filename": "tests/api.test.js",
            "content": code
        }
    
    async def _generate_documentation(self, requirements: Dict, structure: Dict) -> Dict:
        """Generate README documentation"""
        
        readme = f'''# {requirements.get("project_name", "Project")}

{requirements.get("description", "")}

## Features

{self._format_features(requirements.get("features", []))}

## Tech Stack

{self._format_tech_stack(requirements.get("technical_requirements", {}))}

## Installation

```bash
# Clone repository
git clone https://github.com/username/project.git

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env

# Run development server
npm run dev
```

## Project Structure

```
{self._format_structure(structure)}
```

## API Documentation

See [API.md](docs/API.md) for detailed API documentation.

## Testing

```bash
npm test
```

## Deployment

```bash
npm run build
npm start
```

## License

MIT
'''
        
        return {
            "filename": "README.md",
            "content": readme
        }
    
    def _format_features(self, features: List) -> str:
        """Format features for README"""
        return "\n".join([f"- {feature}" for feature in features])
    
    def _format_tech_stack(self, tech_reqs: Dict) -> str:
        """Format tech stack for README"""
        items = []
        if tech_reqs.get("languages"):
            items.extend([f"- {lang}" for lang in tech_reqs["languages"]])
        if tech_reqs.get("frameworks"):
            items.extend([f"- {fw}" for fw in tech_reqs["frameworks"]])
        return "\n".join(items)
    
    def _format_structure(self, structure: Dict) -> str:
        """Format project structure"""
        lines = []
        
        def traverse(node, prefix=""):
            for key, value in node.items():
                lines.append(f"{prefix}{key}/")
                if isinstance(value, dict):
                    traverse(value, prefix + "  ")
        
        traverse(structure.get("root", {}))
        return "\n".join(lines)
    
    def _count_files(self, generated_files: Dict) -> int:
        """Count generated files"""
        count = 0
        for key, value in generated_files.items():
            if isinstance(value, dict):
                count += 1
            elif isinstance(value, list):
                count += len(value)
        return count
    
    def _count_lines(self, generated_files: Dict) -> int:
        """Count lines of code"""
        lines = 0
        for key, value in generated_files.items():
            if isinstance(value, dict) and "content" in value:
                lines += len(value["content"].split("\n"))
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict) and "content" in item:
                        lines += len(item["content"].split("\n"))
        return lines
    
    async def _get_secret(self, key: str) -> str:
        """Get secret from secure storage"""
        import os
        return os.getenv(key, "")


# ============= Assembly Agent =============
class EnterpriseAssemblyAgent(EnterpriseBaseAgent):
    """
    Assembles all generated code into a complete project
    """
    
    def __init__(self):
        config = AgentConfig(
            name="assembly_agent",
            version="1.0.0",
            timeout=30,
            retries=2,
            cache_ttl=1800
        )
        super().__init__(config)
    
    async def process(self, input_data: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Assemble generated code into project"""
        
        generated_files = input_data.get("generated_files", {})
        project_structure = input_data.get("project_structure", {})
        requirements = input_data.get("requirements", {})
        
        self.logger.info(
            "Assembling project",
            file_count=len(generated_files),
            trace_id=context.trace_id
        )
        
        # Create project layout
        project_layout = await self._create_project_layout(project_structure, generated_files)
        
        # Validate project completeness
        validation_results = await self._validate_project(project_layout, requirements)
        
        # Add missing files if needed
        if validation_results["missing_files"]:
            project_layout = await self._add_missing_files(project_layout, validation_results["missing_files"])
        
        # Optimize project structure
        optimized_layout = await self._optimize_structure(project_layout)
        
        # Generate build scripts
        build_scripts = await self._generate_build_scripts(requirements)
        optimized_layout["build_scripts"] = build_scripts
        
        # Create project manifest
        manifest = await self._create_manifest(optimized_layout, requirements)
        
        return {
            "project_layout": optimized_layout,
            "manifest": manifest,
            "validation": validation_results,
            "statistics": self._calculate_statistics(optimized_layout),
            "ready_for_download": True
        }
    
    async def _create_project_layout(self, structure: Dict, files: Dict) -> Dict:
        """Create complete project layout"""
        
        layout = {}
        
        # Process each generated file
        for category, content in files.items():
            if isinstance(content, dict) and "filename" in content:
                path = content["filename"]
                layout[path] = content["content"]
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and "filename" in item:
                        layout[item["filename"]] = item["content"]
        
        return layout
    
    async def _validate_project(self, layout: Dict, requirements: Dict) -> Dict:
        """Validate project completeness"""
        
        validation = {
            "is_complete": True,
            "missing_files": [],
            "warnings": []
        }
        
        # Check for essential files
        essential_files = ["README.md", ".gitignore"]
        
        project_type = requirements.get("project_type", "")
        if project_type == "web_app":
            essential_files.extend(["package.json", "src/index.js"])
        elif project_type == "api":
            essential_files.extend(["src/main.py", "requirements.txt"])
        
        for file in essential_files:
            if not any(file in path for path in layout.keys()):
                validation["missing_files"].append(file)
                validation["is_complete"] = False
        
        # Check for test files
        if not any("test" in path.lower() for path in layout.keys()):
            validation["warnings"].append("No test files found")
        
        return validation
    
    async def _add_missing_files(self, layout: Dict, missing_files: List[str]) -> Dict:
        """Add missing essential files"""
        
        for file in missing_files:
            if file == "README.md":
                layout[file] = "# Project\n\nGenerated project"
            elif file == ".gitignore":
                layout[file] = "node_modules/\n.env\ndist/"
            elif file == "package.json":
                layout[file] = '{"name": "project", "version": "1.0.0"}'
        
        return layout
    
    async def _optimize_structure(self, layout: Dict) -> Dict:
        """Optimize project structure"""
        
        # Sort files by directory depth for better organization
        optimized = {}
        sorted_paths = sorted(layout.keys(), key=lambda x: x.count('/'))
        
        for path in sorted_paths:
            optimized[path] = layout[path]
        
        return optimized
    
    async def _generate_build_scripts(self, requirements: Dict) -> List[Dict]:
        """Generate build and deployment scripts"""
        
        scripts = []
        
        # Build script
        scripts.append({
            "filename": "build.sh",
            "content": '''#!/bin/bash
echo "Building project..."
npm install
npm run build
echo "Build complete!"'''
        })
        
        # Deploy script
        scripts.append({
            "filename": "deploy.sh",
            "content": '''#!/bin/bash
echo "Deploying project..."
docker build -t app .
docker run -p 3000:3000 app
echo "Deployment complete!"'''
        })
        
        return scripts
    
    async def _create_manifest(self, layout: Dict, requirements: Dict) -> Dict:
        """Create project manifest"""
        
        return {
            "project_name": requirements.get("project_name", "Generated Project"),
            "version": "1.0.0",
            "created_at": datetime.utcnow().isoformat(),
            "description": requirements.get("description", ""),
            "file_count": len(layout),
            "total_size": sum(len(content) for content in layout.values()),
            "tech_stack": requirements.get("technical_requirements", {}),
            "features": requirements.get("features", [])
        }
    
    def _calculate_statistics(self, layout: Dict) -> Dict:
        """Calculate project statistics"""
        
        stats = {
            "total_files": len(layout),
            "total_lines": sum(content.count('\n') + 1 for content in layout.values()),
            "total_size_bytes": sum(len(content.encode()) for content in layout.values()),
            "file_types": {}
        }
        
        # Count file types
        for path in layout.keys():
            ext = Path(path).suffix or "no_extension"
            stats["file_types"][ext] = stats["file_types"].get(ext, 0) + 1
        
        return stats


# ============= Download Agent =============
class EnterpriseDownloadAgent(EnterpriseBaseAgent):
    """
    Packages project for download
    """
    
    def __init__(self):
        config = AgentConfig(
            name="download_agent",
            version="1.0.0",
            timeout=20,
            retries=2,
            cache_ttl=3600
        )
        super().__init__(config)
    
    async def process(self, input_data: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Package project for download"""
        
        project_layout = input_data.get("project_layout", {})
        manifest = input_data.get("manifest", {})
        
        self.logger.info(
            "Packaging project for download",
            file_count=len(project_layout),
            trace_id=context.trace_id
        )
        
        # Create ZIP archive
        zip_buffer = await self._create_zip_archive(project_layout, manifest)
        
        # Generate download metadata
        download_metadata = {
            "filename": f"{manifest.get('project_name', 'project').lower().replace(' ', '-')}.zip",
            "size_bytes": len(zip_buffer),
            "mime_type": "application/zip",
            "checksum": hashlib.sha256(zip_buffer).hexdigest(),
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Store for download (in production, would upload to S3)
        download_url = await self._store_for_download(zip_buffer, download_metadata)
        
        return {
            "download_url": download_url,
            "download_metadata": download_metadata,
            "manifest": manifest,
            "expires_at": (datetime.utcnow().timestamp() + 3600)  # 1 hour expiry
        }
    
    async def _create_zip_archive(self, layout: Dict, manifest: Dict) -> bytes:
        """Create ZIP archive of project"""
        
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add manifest
            zipf.writestr("manifest.json", json.dumps(manifest, indent=2))
            
            # Add all project files
            for path, content in layout.items():
                # Ensure proper directory structure in zip
                zipf.writestr(path, content)
        
        return zip_buffer.getvalue()
    
    async def _store_for_download(self, zip_data: bytes, metadata: Dict) -> str:
        """Store ZIP for download"""
        
        # In production, would upload to S3 or similar
        # For now, return a mock URL
        file_id = hashlib.sha256(zip_data).hexdigest()[:12]
        
        # Save locally (in production, use S3)
        file_path = f"/tmp/{metadata['filename']}"
        with open(file_path, 'wb') as f:
            f.write(zip_data)
        
        return f"/api/v1/download/{file_id}"