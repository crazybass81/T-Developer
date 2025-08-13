"""
Configuration Generator Module for Generation Agent
Generates framework-specific configuration files and environment settings
"""

from typing import Dict, List, Any, Optional, Union
import asyncio
import json
import yaml
import os
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from pathlib import Path


class ConfigType(Enum):
    BUILD_CONFIG = "build_config"
    DEV_CONFIG = "dev_config"
    PROD_CONFIG = "prod_config"
    TEST_CONFIG = "test_config"
    LINT_CONFIG = "lint_config"
    FORMAT_CONFIG = "format_config"
    ENV_CONFIG = "env_config"
    DATABASE_CONFIG = "database_config"
    DEPLOYMENT_CONFIG = "deployment_config"
    SECURITY_CONFIG = "security_config"


@dataclass
class ConfigurationFile:
    filename: str
    content: str
    config_type: ConfigType
    framework: str
    language: str
    description: str = ""
    is_secret: bool = False
    environment: str = "all"  # all, development, production, test


@dataclass
class ConfigurationResult:
    success: bool
    configuration_files: Dict[str, ConfigurationFile]
    total_configs: int
    processing_time: float
    metadata: Dict[str, Any]
    error: str = ""


class ConfigurationGenerator:
    """Advanced configuration file generator"""

    def __init__(self):
        self.version = "1.0.0"

        # Framework-specific configuration templates
        self.config_templates = {
            "react": self._get_react_configs,
            "vue": self._get_vue_configs,
            "angular": self._get_angular_configs,
            "svelte": self._get_svelte_configs,
            "express": self._get_express_configs,
            "fastapi": self._get_fastapi_configs,
            "django": self._get_django_configs,
            "flask": self._get_flask_configs,
            "next.js": self._get_nextjs_configs,
            "nuxt.js": self._get_nuxtjs_configs,
        }

        # Common configurations
        self.common_configs = {
            "git": self._get_git_configs,
            "docker": self._get_docker_configs,
            "github_actions": self._get_github_actions_configs,
            "vscode": self._get_vscode_configs,
            "prettier": self._get_prettier_configs,
            "editorconfig": self._get_editorconfig_configs,
        }

        # Environment variable templates
        self.env_templates = {
            "development": self._get_development_env,
            "production": self._get_production_env,
            "test": self._get_test_env,
        }

        # Security configurations
        self.security_configs = {
            "cors": self._get_cors_config,
            "helmet": self._get_helmet_config,
            "rate_limiting": self._get_rate_limiting_config,
            "auth": self._get_auth_config,
        }

    async def generate_configs(
        self, context: Dict[str, Any], output_path: str
    ) -> ConfigurationResult:
        """Generate all configuration files for the project"""

        start_time = datetime.now()

        try:
            framework = context.get("target_framework", "react")
            language = context.get("target_language", "javascript")
            project_name = context.get("project_name", "generated-project")

            configuration_files = {}

            # Generate framework-specific configurations
            if framework in self.config_templates:
                framework_configs = await self.config_templates[framework](context)
                configuration_files.update(framework_configs)

            # Generate common configurations
            common_configs = await self._generate_common_configs(context)
            configuration_files.update(common_configs)

            # Generate environment configurations
            env_configs = await self._generate_environment_configs(context)
            configuration_files.update(env_configs)

            # Generate security configurations
            if context.get("include_security", True):
                security_configs = await self._generate_security_configs(context)
                configuration_files.update(security_configs)

            # Generate build and deployment configurations
            build_configs = await self._generate_build_configs(context)
            configuration_files.update(build_configs)

            # Write configuration files to disk
            if output_path:
                await self._write_config_files(configuration_files, output_path)

            processing_time = (datetime.now() - start_time).total_seconds()

            return ConfigurationResult(
                success=True,
                configuration_files=configuration_files,
                total_configs=len(configuration_files),
                processing_time=processing_time,
                metadata={
                    "framework": framework,
                    "language": language,
                    "project_name": project_name,
                    "output_path": output_path,
                    "configs_by_type": self._count_configs_by_type(configuration_files),
                },
            )

        except Exception as e:
            return ConfigurationResult(
                success=False,
                configuration_files={},
                total_configs=0,
                processing_time=(datetime.now() - start_time).total_seconds(),
                metadata={},
                error=str(e),
            )

    async def _generate_common_configs(
        self, context: Dict[str, Any]
    ) -> Dict[str, ConfigurationFile]:
        """Generate common configuration files"""

        configs = {}

        for config_type, generator in self.common_configs.items():
            config_files = await generator(context)
            configs.update(config_files)

        return configs

    async def _generate_environment_configs(
        self, context: Dict[str, Any]
    ) -> Dict[str, ConfigurationFile]:
        """Generate environment-specific configuration files"""

        configs = {}

        for env, generator in self.env_templates.items():
            config_files = await generator(context)
            configs.update(config_files)

        return configs

    async def _generate_security_configs(
        self, context: Dict[str, Any]
    ) -> Dict[str, ConfigurationFile]:
        """Generate security configuration files"""

        configs = {}

        framework = context.get("target_framework", "react")

        # Only generate security configs for server-side frameworks
        if framework in ["express", "fastapi", "django", "flask"]:
            for config_type, generator in self.security_configs.items():
                config_files = await generator(context)
                configs.update(config_files)

        return configs

    async def _generate_build_configs(
        self, context: Dict[str, Any]
    ) -> Dict[str, ConfigurationFile]:
        """Generate build and deployment configuration files"""

        configs = {}

        framework = context.get("target_framework", "react")
        include_deployment = context.get("include_deployment", True)

        if include_deployment:
            # Docker configurations
            docker_configs = await self._get_docker_configs(context)
            configs.update(docker_configs)

            # CI/CD configurations
            cicd_configs = await self._get_github_actions_configs(context)
            configs.update(cicd_configs)

        return configs

    # React configurations
    async def _get_react_configs(
        self, context: Dict[str, Any]
    ) -> Dict[str, ConfigurationFile]:
        """Generate React-specific configurations"""

        configs = {}

        # Vite configuration
        vite_config = f"""import {{ defineConfig }} from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({{
  plugins: [react()],
  server: {{
    port: 3000,
    open: true
  }},
  build: {{
    outDir: 'build',
    sourcemap: true
  }},
  resolve: {{
    alias: {{
      '@': '/src'
    }}
  }}
}})"""

        configs["vite.config.ts"] = ConfigurationFile(
            filename="vite.config.ts",
            content=vite_config,
            config_type=ConfigType.BUILD_CONFIG,
            framework="react",
            language="typescript",
            description="Vite build configuration",
        )

        # TypeScript configuration
        tsconfig = {
            "compilerOptions": {
                "target": "ES2020",
                "useDefineForClassFields": True,
                "lib": ["ES2020", "DOM", "DOM.Iterable"],
                "module": "ESNext",
                "skipLibCheck": True,
                "moduleResolution": "bundler",
                "allowImportingTsExtensions": True,
                "resolveJsonModule": True,
                "isolatedModules": True,
                "noEmit": True,
                "jsx": "react-jsx",
                "strict": True,
                "noUnusedLocals": True,
                "noUnusedParameters": True,
                "noFallthroughCasesInSwitch": True,
                "baseUrl": ".",
                "paths": {"@/*": ["src/*"]},
            },
            "include": ["src"],
            "references": [{"path": "./tsconfig.node.json"}],
        }

        configs["tsconfig.json"] = ConfigurationFile(
            filename="tsconfig.json",
            content=json.dumps(tsconfig, indent=2),
            config_type=ConfigType.BUILD_CONFIG,
            framework="react",
            language="typescript",
            description="TypeScript configuration",
        )

        # ESLint configuration
        eslint_config = {
            "root": True,
            "env": {"browser": True, "es2020": True},
            "extends": [
                "eslint:recommended",
                "@typescript-eslint/recommended",
                "plugin:react-hooks/recommended",
            ],
            "ignorePatterns": ["dist", ".eslintrc.cjs"],
            "parser": "@typescript-eslint/parser",
            "plugins": ["react-refresh"],
            "rules": {
                "react-refresh/only-export-components": [
                    "warn",
                    {"allowConstantExport": True},
                ]
            },
        }

        configs[".eslintrc.json"] = ConfigurationFile(
            filename=".eslintrc.json",
            content=json.dumps(eslint_config, indent=2),
            config_type=ConfigType.LINT_CONFIG,
            framework="react",
            language="typescript",
            description="ESLint configuration",
        )

        return configs

    # Vue configurations
    async def _get_vue_configs(
        self, context: Dict[str, Any]
    ) -> Dict[str, ConfigurationFile]:
        """Generate Vue-specific configurations"""

        configs = {}

        # Vite configuration for Vue
        vite_config = f"""import {{ defineConfig }} from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({{
  plugins: [vue()],
  server: {{
    port: 3000,
    open: true
  }},
  build: {{
    outDir: 'dist',
    sourcemap: true
  }},
  resolve: {{
    alias: {{
      '@': '/src'
    }}
  }}
}})"""

        configs["vite.config.ts"] = ConfigurationFile(
            filename="vite.config.ts",
            content=vite_config,
            config_type=ConfigType.BUILD_CONFIG,
            framework="vue",
            language="typescript",
            description="Vite build configuration for Vue",
        )

        return configs

    # Angular configurations
    async def _get_angular_configs(
        self, context: Dict[str, Any]
    ) -> Dict[str, ConfigurationFile]:
        """Generate Angular-specific configurations"""

        configs = {}

        # Angular configuration
        angular_json = {
            "$schema": "./node_modules/@angular/cli/lib/config/schema.json",
            "version": 1,
            "newProjectRoot": "projects",
            "projects": {
                context.get("project_name", "app"): {
                    "projectType": "application",
                    "schematics": {"@schematics/angular:component": {"style": "css"}},
                    "root": "",
                    "sourceRoot": "src",
                    "prefix": "app",
                    "architect": {
                        "build": {
                            "builder": "@angular-devkit/build-angular:browser",
                            "options": {
                                "outputPath": "dist",
                                "index": "src/index.html",
                                "main": "src/main.ts",
                                "polyfills": "src/polyfills.ts",
                                "tsConfig": "tsconfig.app.json",
                                "assets": ["src/favicon.ico", "src/assets"],
                                "styles": ["src/styles.css"],
                                "scripts": [],
                            },
                        }
                    },
                }
            },
        }

        configs["angular.json"] = ConfigurationFile(
            filename="angular.json",
            content=json.dumps(angular_json, indent=2),
            config_type=ConfigType.BUILD_CONFIG,
            framework="angular",
            language="typescript",
            description="Angular CLI configuration",
        )

        return configs

    # Express configurations
    async def _get_express_configs(
        self, context: Dict[str, Any]
    ) -> Dict[str, ConfigurationFile]:
        """Generate Express-specific configurations"""

        configs = {}

        # TypeScript configuration for Node.js
        tsconfig = {
            "compilerOptions": {
                "target": "ES2020",
                "module": "commonjs",
                "lib": ["ES2020"],
                "allowJs": True,
                "outDir": "./dist",
                "rootDir": "./src",
                "strict": True,
                "moduleResolution": "node",
                "baseUrl": ".",
                "paths": {"@/*": ["src/*"]},
                "esModuleInterop": True,
                "skipLibCheck": True,
                "forceConsistentCasingInFileNames": True,
                "resolveJsonModule": True,
                "declaration": True,
                "declarationMap": True,
                "sourceMap": True,
            },
            "include": ["src/**/*"],
            "exclude": ["node_modules", "dist"],
        }

        configs["tsconfig.json"] = ConfigurationFile(
            filename="tsconfig.json",
            content=json.dumps(tsconfig, indent=2),
            config_type=ConfigType.BUILD_CONFIG,
            framework="express",
            language="typescript",
            description="TypeScript configuration for Node.js",
        )

        # Nodemon configuration
        nodemon_config = {
            "watch": ["src"],
            "ext": "ts,js,json",
            "ignore": ["src/**/*.spec.ts"],
            "exec": "ts-node src/index.ts",
        }

        configs["nodemon.json"] = ConfigurationFile(
            filename="nodemon.json",
            content=json.dumps(nodemon_config, indent=2),
            config_type=ConfigType.DEV_CONFIG,
            framework="express",
            language="typescript",
            description="Nodemon development configuration",
        )

        return configs

    # FastAPI configurations
    async def _get_fastapi_configs(
        self, context: Dict[str, Any]
    ) -> Dict[str, ConfigurationFile]:
        """Generate FastAPI-specific configurations"""

        configs = {}

        # Uvicorn configuration
        uvicorn_config = f"""# Uvicorn ASGI server configuration
import os
from uvicorn import run

if __name__ == "__main__":
    run(
        "main:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENVIRONMENT") == "development",
        workers=int(os.getenv("WORKERS", 1))
    )"""

        configs["uvicorn_config.py"] = ConfigurationFile(
            filename="uvicorn_config.py",
            content=uvicorn_config,
            config_type=ConfigType.DEV_CONFIG,
            framework="fastapi",
            language="python",
            description="Uvicorn server configuration",
        )

        # Alembic configuration (database migrations)
        alembic_ini = f"""# A generic, single database configuration.

[alembic]
# path to migration scripts
script_location = alembic

# template used to generate migration files
# file_template = %%(rev)s_%%(slug)s

# sys.path path, will be prepended to sys.path if present.
# defaults to the current working directory.
prepend_sys_path = .

# timezone to use when rendering the date within the migration file
# as well as the filename.
# If specified, requires the python-dateutil library that can be
# installed by adding `alembic[tz]` to the pip requirements
# string value is passed to dateutil.tz.gettz()
# leave blank for localtime
# timezone =

# max length of characters to apply to the
# "slug" field
# max_rev_id_length = 40

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
# revision_environment = false

sqlalchemy.url = driver://user:pass@localhost/dbname

[post_write_hooks]
# post_write_hooks defines scripts or Python functions that are run
# on newly generated revision scripts.

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S"""

        configs["alembic.ini"] = ConfigurationFile(
            filename="alembic.ini",
            content=alembic_ini,
            config_type=ConfigType.DATABASE_CONFIG,
            framework="fastapi",
            language="python",
            description="Alembic database migration configuration",
        )

        return configs

    # Common configurations
    async def _get_git_configs(
        self, context: Dict[str, Any]
    ) -> Dict[str, ConfigurationFile]:
        """Generate Git configuration files"""

        configs = {}

        # .gitignore
        gitignore_content = f"""# Dependencies
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
pip-log.txt
pip-delete-this-directory.txt
.env
venv/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Build outputs
dist/
build/
*.tgz
*.tar.gz

# Test coverage
coverage/
*.lcov
.nyc_output

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Optional npm cache directory
.npm

# Optional REPL history
.node_repl_history

# Output of 'npm pack'
*.tgz

# Yarn Integrity file
.yarn-integrity

# dotenv environment variables file
.env
.env.test

# parcel-bundler cache (https://parceljs.org/)
.cache
.parcel-cache

# next.js build output
.next

# nuxt.js build output
.nuxt

# vuepress build output
.vuepress/dist

# Serverless directories
.serverless

# FuseBox cache
.fusebox/

# DynamoDB Local files
.dynamodb/"""

        configs[".gitignore"] = ConfigurationFile(
            filename=".gitignore",
            content=gitignore_content,
            config_type=ConfigType.BUILD_CONFIG,
            framework="common",
            language="text",
            description="Git ignore file",
        )

        return configs

    async def _get_docker_configs(
        self, context: Dict[str, Any]
    ) -> Dict[str, ConfigurationFile]:
        """Generate Docker configuration files"""

        configs = {}
        framework = context.get("target_framework", "react")

        if framework in ["react", "vue", "angular"]:
            # Frontend Dockerfile
            dockerfile = f"""# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets from builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]"""

        elif framework in ["express", "fastapi", "django", "flask"]:
            # Backend Dockerfile
            if framework == "express":
                dockerfile = f"""FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]"""
            else:  # Python frameworks
                dockerfile = f"""FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]"""

        configs["Dockerfile"] = ConfigurationFile(
            filename="Dockerfile",
            content=dockerfile,
            config_type=ConfigType.DEPLOYMENT_CONFIG,
            framework=framework,
            language="docker",
            description="Docker container configuration",
        )

        # Docker Compose
        if framework in ["express", "fastapi", "django", "flask"]:
            docker_compose = {
                "version": "3.8",
                "services": {
                    "app": {
                        "build": ".",
                        "ports": ["8000:8000"],
                        "environment": ["ENVIRONMENT=development"],
                        "volumes": [".:/app"],
                    },
                    "db": {
                        "image": "postgres:13",
                        "environment": [
                            "POSTGRES_DB=app_db",
                            "POSTGRES_USER=user",
                            "POSTGRES_PASSWORD=password",
                        ],
                        "ports": ["5432:5432"],
                        "volumes": ["postgres_data:/var/lib/postgresql/data"],
                    },
                },
                "volumes": {"postgres_data": None},
            }

            configs["docker-compose.yml"] = ConfigurationFile(
                filename="docker-compose.yml",
                content=yaml.dump(docker_compose, default_flow_style=False),
                config_type=ConfigType.DEPLOYMENT_CONFIG,
                framework=framework,
                language="yaml",
                description="Docker Compose configuration",
            )

        return configs

    async def _get_github_actions_configs(
        self, context: Dict[str, Any]
    ) -> Dict[str, ConfigurationFile]:
        """Generate GitHub Actions CI/CD configurations"""

        configs = {}
        framework = context.get("target_framework", "react")

        workflow = {
            "name": "CI/CD Pipeline",
            "on": {
                "push": {"branches": ["main", "develop"]},
                "pull_request": {"branches": ["main"]},
            },
            "jobs": {
                "test": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {"uses": "actions/checkout@v3"},
                        {
                            "name": "Setup Node.js"
                            if framework in ["react", "vue", "angular", "express"]
                            else "Setup Python",
                            "uses": "actions/setup-node@v3"
                            if framework in ["react", "vue", "angular", "express"]
                            else "actions/setup-python@v3",
                            "with": {
                                "node-version": "18"
                                if framework in ["react", "vue", "angular", "express"]
                                else None,
                                "python-version": "3.9"
                                if framework
                                not in ["react", "vue", "angular", "express"]
                                else None,
                            },
                        },
                        {
                            "name": "Install dependencies",
                            "run": "npm ci"
                            if framework in ["react", "vue", "angular", "express"]
                            else "pip install -r requirements.txt",
                        },
                        {
                            "name": "Run tests",
                            "run": "npm test"
                            if framework in ["react", "vue", "angular", "express"]
                            else "pytest",
                        },
                        {
                            "name": "Build",
                            "run": "npm run build"
                            if framework in ["react", "vue", "angular", "express"]
                            else "python -m build",
                        },
                    ],
                }
            },
        }

        # Clean up None values
        if framework in ["react", "vue", "angular", "express"]:
            del workflow["jobs"]["test"]["steps"][1]["with"]["python-version"]
        else:
            del workflow["jobs"]["test"]["steps"][1]["with"]["node-version"]

        configs[".github/workflows/ci.yml"] = ConfigurationFile(
            filename=".github/workflows/ci.yml",
            content=yaml.dump(workflow, default_flow_style=False),
            config_type=ConfigType.DEPLOYMENT_CONFIG,
            framework=framework,
            language="yaml",
            description="GitHub Actions CI/CD workflow",
        )

        return configs

    # Environment configurations
    async def _get_development_env(
        self, context: Dict[str, Any]
    ) -> Dict[str, ConfigurationFile]:
        """Generate development environment configuration"""

        configs = {}
        framework = context.get("target_framework", "react")

        if framework in ["express", "fastapi", "django", "flask"]:
            env_content = f"""# Development Environment Variables
NODE_ENV=development
PORT=3000
HOST=localhost

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=app_dev
DB_USER=dev_user
DB_PASSWORD=dev_password

# API Configuration
API_URL=http://localhost:3000/api
JWT_SECRET=development_jwt_secret_key

# External Services
REDIS_URL=redis://localhost:6379

# Logging
LOG_LEVEL=debug

# Features
ENABLE_CORS=true
ENABLE_SWAGGER=true"""

        elif framework in ["react", "vue", "angular"]:
            env_content = f"""# Development Environment Variables
VITE_API_URL=http://localhost:8000/api
VITE_APP_NAME={context.get('project_name', 'Generated Project')}
VITE_APP_VERSION=1.0.0
VITE_ENABLE_DEV_TOOLS=true

# Feature Flags
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_LOGGING=true"""

        configs[".env.development"] = ConfigurationFile(
            filename=".env.development",
            content=env_content,
            config_type=ConfigType.ENV_CONFIG,
            framework=framework,
            language="text",
            description="Development environment variables",
            is_secret=True,
            environment="development",
        )

        return configs

    async def _get_production_env(
        self, context: Dict[str, Any]
    ) -> Dict[str, ConfigurationFile]:
        """Generate production environment configuration"""

        configs = {}
        framework = context.get("target_framework", "react")

        if framework in ["express", "fastapi", "django", "flask"]:
            env_content = f"""# Production Environment Variables
NODE_ENV=production
PORT=${PORT:-8000}
HOST=0.0.0.0

# Database Configuration (use environment variables)
DB_HOST=${DB_HOST}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}

# API Configuration
API_URL=${API_URL}
JWT_SECRET=${JWT_SECRET}

# External Services
REDIS_URL=${REDIS_URL}

# Logging
LOG_LEVEL=info

# Features
ENABLE_CORS=false
ENABLE_SWAGGER=false

# Monitoring
SENTRY_DSN=${SENTRY_DSN}"""

        elif framework in ["react", "vue", "angular"]:
            env_content = f"""# Production Environment Variables
VITE_API_URL=${VITE_API_URL}
VITE_APP_NAME={context.get('project_name', 'Generated Project')}
VITE_APP_VERSION=${APP_VERSION:-1.0.0}
VITE_ENABLE_DEV_TOOLS=false

# Feature Flags
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_LOGGING=false

# Monitoring
VITE_SENTRY_DSN=${SENTRY_DSN}"""

        configs[".env.production"] = ConfigurationFile(
            filename=".env.production",
            content=env_content,
            config_type=ConfigType.ENV_CONFIG,
            framework=framework,
            language="text",
            description="Production environment variables",
            is_secret=True,
            environment="production",
        )

        return configs

    async def _write_config_files(
        self, configuration_files: Dict[str, ConfigurationFile], output_path: str
    ):
        """Write configuration files to disk"""

        for filename, config_file in configuration_files.items():
            file_path = os.path.join(output_path, filename)

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Write file content
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(config_file.content)

    def _count_configs_by_type(
        self, configuration_files: Dict[str, ConfigurationFile]
    ) -> Dict[str, int]:
        """Count configuration files by type"""

        counts = {}

        for config_file in configuration_files.values():
            config_type = config_file.config_type.value
            counts[config_type] = counts.get(config_type, 0) + 1

        return counts

    # Additional framework-specific methods (simplified)
    async def _get_svelte_configs(
        self, context: Dict[str, Any]
    ) -> Dict[str, ConfigurationFile]:
        """Generate Svelte-specific configurations"""
        return {}

    async def _get_nextjs_configs(
        self, context: Dict[str, Any]
    ) -> Dict[str, ConfigurationFile]:
        """Generate Next.js-specific configurations"""
        return {}

    async def _get_nuxtjs_configs(
        self, context: Dict[str, Any]
    ) -> Dict[str, ConfigurationFile]:
        """Generate Nuxt.js-specific configurations"""
        return {}

    async def _get_django_configs(
        self, context: Dict[str, Any]
    ) -> Dict[str, ConfigurationFile]:
        """Generate Django-specific configurations"""
        return {}

    async def _get_flask_configs(
        self, context: Dict[str, Any]
    ) -> Dict[str, ConfigurationFile]:
        """Generate Flask-specific configurations"""
        return {}

    async def _get_vscode_configs(
        self, context: Dict[str, Any]
    ) -> Dict[str, ConfigurationFile]:
        """Generate VS Code workspace configurations"""
        return {}

    async def _get_prettier_configs(
        self, context: Dict[str, Any]
    ) -> Dict[str, ConfigurationFile]:
        """Generate Prettier formatting configurations"""
        return {}

    async def _get_editorconfig_configs(
        self, context: Dict[str, Any]
    ) -> Dict[str, ConfigurationFile]:
        """Generate EditorConfig configurations"""
        return {}

    async def _get_test_env(
        self, context: Dict[str, Any]
    ) -> Dict[str, ConfigurationFile]:
        """Generate test environment configuration"""
        return {}

    # Security configuration methods (simplified)
    async def _get_cors_config(
        self, context: Dict[str, Any]
    ) -> Dict[str, ConfigurationFile]:
        """Generate CORS configuration"""
        return {}

    async def _get_helmet_config(
        self, context: Dict[str, Any]
    ) -> Dict[str, ConfigurationFile]:
        """Generate Helmet security configuration"""
        return {}

    async def _get_rate_limiting_config(
        self, context: Dict[str, Any]
    ) -> Dict[str, ConfigurationFile]:
        """Generate rate limiting configuration"""
        return {}

    async def _get_auth_config(
        self, context: Dict[str, Any]
    ) -> Dict[str, ConfigurationFile]:
        """Generate authentication configuration"""
        return {}
