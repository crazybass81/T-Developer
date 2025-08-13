"""
Project Scaffolder Module
Creates project structure and scaffolding for different frameworks
"""

from typing import Dict, List, Any, Optional, Tuple
import os
import json
from datetime import datetime
from pathlib import Path


class ProjectScaffolder:
    """Advanced project scaffolding system"""

    def __init__(self):
        # Framework-specific structures
        self.structures = {
            "react": self._get_react_structure,
            "vue": self._get_vue_structure,
            "angular": self._get_angular_structure,
            "express": self._get_express_structure,
            "fastapi": self._get_fastapi_structure,
            "django": self._get_django_structure,
            "flask": self._get_flask_structure,
            "next.js": self._get_nextjs_structure,
            "nuxt.js": self._get_nuxt_structure,
            "svelte": self._get_svelte_structure,
        }

        # Common directory patterns
        self.common_patterns = {
            "frontend": [
                "src",
                "public",
                "assets",
                "components",
                "pages",
                "utils",
                "styles",
            ],
            "backend": [
                "src",
                "routes",
                "models",
                "controllers",
                "middleware",
                "utils",
                "config",
            ],
            "fullstack": ["frontend", "backend", "shared", "docs", "scripts"],
            "mobile": [
                "src",
                "assets",
                "components",
                "screens",
                "navigation",
                "utils",
                "services",
            ],
            "library": ["src", "lib", "types", "utils", "examples", "docs"],
            "cli": ["src", "bin", "commands", "utils", "templates"],
        }

        # File templates
        self.file_templates = {
            "gitignore": self._get_gitignore_template,
            "readme": self._get_readme_template,
            "license": self._get_license_template,
            "editorconfig": self._get_editorconfig_template,
            "eslintrc": self._get_eslintrc_template,
            "prettierrc": self._get_prettierrc_template,
            "dockerfile": self._get_dockerfile_template,
            "docker_compose": self._get_docker_compose_template,
        }

    async def create_structure(
        self, context: Dict[str, Any], output_path: str
    ) -> "ScaffolderResult":
        """Create complete project structure"""

        try:
            framework = context.get("target_framework", "react")
            language = context.get("target_language", "javascript")
            generation_mode = context.get("generation_mode", "full")

            # Create base directory structure
            structure = await self._create_base_structure(
                framework, context, output_path
            )

            # Create framework-specific structure
            framework_structure = await self._create_framework_structure(
                framework, context, output_path
            )

            # Create common configuration files
            config_files = await self._create_config_files(context, output_path)

            # Create development tools setup
            dev_tools = await self._create_dev_tools(context, output_path)

            # Create documentation structure
            docs_structure = await self._create_docs_structure(context, output_path)

            # Create testing structure
            test_structure = await self._create_test_structure(context, output_path)

            # Create deployment structure
            deploy_structure = await self._create_deployment_structure(
                context, output_path
            )

            # Combine all structures
            complete_structure = {
                **structure,
                **framework_structure,
                **config_files,
                **dev_tools,
                **docs_structure,
                **test_structure,
                **deploy_structure,
            }

            # Create .gitkeep files for empty directories
            await self._create_gitkeep_files(output_path, complete_structure)

            return ScaffolderResult(
                success=True,
                data={
                    "structure": complete_structure,
                    "directories_created": len(
                        [k for k, v in complete_structure.items() if v == "directory"]
                    ),
                    "files_created": len(
                        [k for k, v in complete_structure.items() if v != "directory"]
                    ),
                    "framework": framework,
                    "language": language,
                },
            )

        except Exception as e:
            return ScaffolderResult(False, {}, str(e))

    async def _create_base_structure(
        self, framework: str, context: Dict[str, Any], output_path: str
    ) -> Dict[str, str]:
        """Create base project structure"""

        structure = {}

        # Determine project type
        project_type = self._determine_project_type(framework, context)

        # Get common directories for project type
        common_dirs = self.common_patterns.get(project_type, ["src"])

        # Create base directories
        for dir_name in common_dirs:
            dir_path = os.path.join(output_path, dir_name)
            os.makedirs(dir_path, exist_ok=True)
            structure[dir_name] = "directory"

        # Create additional common directories
        additional_dirs = ["assets", "public", "dist", "build", "temp", "logs"]

        for dir_name in additional_dirs:
            if context.get("generation_mode", "full") != "minimal":
                dir_path = os.path.join(output_path, dir_name)
                os.makedirs(dir_path, exist_ok=True)
                structure[dir_name] = "directory"

        return structure

    async def _create_framework_structure(
        self, framework: str, context: Dict[str, Any], output_path: str
    ) -> Dict[str, str]:
        """Create framework-specific structure"""

        if framework not in self.structures:
            return {}

        structure_func = self.structures[framework]
        return await structure_func(context, output_path)

    async def _get_react_structure(
        self, context: Dict[str, Any], output_path: str
    ) -> Dict[str, str]:
        """Create React project structure"""

        structure = {}

        # React-specific directories
        directories = [
            "src/components",
            "src/hooks",
            "src/pages",
            "src/utils",
            "src/services",
            "src/context",
            "src/types",
            "src/styles",
            "src/assets/images",
            "src/assets/icons",
            "public",
            "public/images",
            "public/icons",
        ]

        for dir_path in directories:
            full_path = os.path.join(output_path, dir_path)
            os.makedirs(full_path, exist_ok=True)
            structure[dir_path] = "directory"

        # React-specific files
        files = {
            "public/index.html": self._get_react_index_html(context),
            "public/manifest.json": self._get_react_manifest(context),
            "public/robots.txt": "User-agent: *\nDisallow:",
            "src/index.css": self._get_react_index_css(),
            "src/App.css": self._get_react_app_css(),
            "src/setupTests.js": self._get_react_setup_tests(),
            "src/reportWebVitals.js": self._get_react_report_web_vitals(),
        }

        for file_path, content in files.items():
            full_path = os.path.join(output_path, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            structure[file_path] = "file"

        return structure

    async def _get_vue_structure(
        self, context: Dict[str, Any], output_path: str
    ) -> Dict[str, str]:
        """Create Vue project structure"""

        structure = {}

        # Vue-specific directories
        directories = [
            "src/components",
            "src/views",
            "src/router",
            "src/store",
            "src/composables",
            "src/utils",
            "src/services",
            "src/types",
            "src/assets/css",
            "src/assets/images",
            "public",
        ]

        for dir_path in directories:
            full_path = os.path.join(output_path, dir_path)
            os.makedirs(full_path, exist_ok=True)
            structure[dir_path] = "directory"

        # Vue-specific files
        files = {
            "public/index.html": self._get_vue_index_html(context),
            "src/style.css": self._get_vue_style_css(),
            "vite.config.js": self._get_vue_vite_config(),
        }

        for file_path, content in files.items():
            full_path = os.path.join(output_path, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            structure[file_path] = "file"

        return structure

    async def _get_angular_structure(
        self, context: Dict[str, Any], output_path: str
    ) -> Dict[str, str]:
        """Create Angular project structure"""

        structure = {}

        # Angular-specific directories
        directories = [
            "src/app/components",
            "src/app/services",
            "src/app/models",
            "src/app/guards",
            "src/app/pipes",
            "src/app/directives",
            "src/assets",
            "src/environments",
        ]

        for dir_path in directories:
            full_path = os.path.join(output_path, dir_path)
            os.makedirs(full_path, exist_ok=True)
            structure[dir_path] = "directory"

        return structure

    async def _get_express_structure(
        self, context: Dict[str, Any], output_path: str
    ) -> Dict[str, str]:
        """Create Express project structure"""

        structure = {}

        # Express-specific directories
        directories = [
            "src/routes",
            "src/controllers",
            "src/models",
            "src/middleware",
            "src/services",
            "src/utils",
            "src/config",
            "src/types",
            "public",
            "uploads",
            "logs",
        ]

        for dir_path in directories:
            full_path = os.path.join(output_path, dir_path)
            os.makedirs(full_path, exist_ok=True)
            structure[dir_path] = "directory"

        return structure

    async def _get_fastapi_structure(
        self, context: Dict[str, Any], output_path: str
    ) -> Dict[str, str]:
        """Create FastAPI project structure"""

        structure = {}

        # FastAPI-specific directories
        directories = [
            "app/api/v1",
            "app/core",
            "app/crud",
            "app/db",
            "app/models",
            "app/schemas",
            "app/services",
            "app/utils",
            "app/tests",
            "alembic/versions",
            "scripts",
            "docs",
        ]

        for dir_path in directories:
            full_path = os.path.join(output_path, dir_path)
            os.makedirs(full_path, exist_ok=True)
            structure[dir_path] = "directory"

        # FastAPI-specific files
        files = {
            "requirements.txt": self._get_fastapi_requirements(),
            "alembic.ini": self._get_alembic_config(),
            ".env.example": self._get_fastapi_env_example(),
        }

        for file_path, content in files.items():
            full_path = os.path.join(output_path, file_path)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            structure[file_path] = "file"

        return structure

    async def _get_django_structure(
        self, context: Dict[str, Any], output_path: str
    ) -> Dict[str, str]:
        """Create Django project structure"""

        structure = {}

        project_name = context.get("project_name", "myproject")

        # Django-specific directories
        directories = [
            f"{project_name}/{project_name}",
            f"{project_name}/apps",
            f"{project_name}/static",
            f"{project_name}/media",
            f"{project_name}/templates",
            f"{project_name}/locale",
            "requirements",
            "scripts",
            "docs",
        ]

        for dir_path in directories:
            full_path = os.path.join(output_path, dir_path)
            os.makedirs(full_path, exist_ok=True)
            structure[dir_path] = "directory"

        return structure

    async def _get_flask_structure(
        self, context: Dict[str, Any], output_path: str
    ) -> Dict[str, str]:
        """Create Flask project structure"""

        structure = {}

        # Flask-specific directories
        directories = [
            "app/main",
            "app/auth",
            "app/api",
            "app/models",
            "app/templates",
            "app/static/css",
            "app/static/js",
            "app/static/images",
            "migrations",
            "tests",
            "config",
        ]

        for dir_path in directories:
            full_path = os.path.join(output_path, dir_path)
            os.makedirs(full_path, exist_ok=True)
            structure[dir_path] = "directory"

        return structure

    async def _get_nextjs_structure(
        self, context: Dict[str, Any], output_path: str
    ) -> Dict[str, str]:
        """Create Next.js project structure"""

        structure = {}

        # Next.js-specific directories
        directories = [
            "pages/api",
            "pages/_app",
            "components",
            "lib",
            "utils",
            "hooks",
            "styles",
            "public/images",
            "public/icons",
            ".next",
        ]

        for dir_path in directories:
            full_path = os.path.join(output_path, dir_path)
            os.makedirs(full_path, exist_ok=True)
            structure[dir_path] = "directory"

        return structure

    async def _get_nuxt_structure(
        self, context: Dict[str, Any], output_path: str
    ) -> Dict[str, str]:
        """Create Nuxt.js project structure"""

        structure = {}

        # Nuxt-specific directories
        directories = [
            "pages",
            "components",
            "layouts",
            "middleware",
            "plugins",
            "store",
            "assets",
            "static",
            ".nuxt",
        ]

        for dir_path in directories:
            full_path = os.path.join(output_path, dir_path)
            os.makedirs(full_path, exist_ok=True)
            structure[dir_path] = "directory"

        return structure

    async def _get_svelte_structure(
        self, context: Dict[str, Any], output_path: str
    ) -> Dict[str, str]:
        """Create Svelte project structure"""

        structure = {}

        # Svelte-specific directories
        directories = ["src/lib", "src/routes", "src/app.html", "static", "build"]

        for dir_path in directories:
            full_path = os.path.join(output_path, dir_path)
            os.makedirs(full_path, exist_ok=True)
            structure[dir_path] = "directory"

        return structure

    async def _create_config_files(
        self, context: Dict[str, Any], output_path: str
    ) -> Dict[str, str]:
        """Create common configuration files"""

        structure = {}

        config_files = {
            ".gitignore": self.file_templates["gitignore"](context),
            "README.md": self.file_templates["readme"](context),
            ".editorconfig": self.file_templates["editorconfig"](context),
        }

        # Add language-specific configs
        language = context.get("target_language", "javascript")
        framework = context.get("target_framework", "react")

        if language in ["javascript", "typescript"] or framework in [
            "react",
            "vue",
            "angular",
        ]:
            config_files[".eslintrc.js"] = self.file_templates["eslintrc"](context)
            config_files[".prettierrc"] = self.file_templates["prettierrc"](context)

        # Add Docker files if requested
        if context.get("include_docker", True):
            config_files["Dockerfile"] = self.file_templates["dockerfile"](context)
            config_files["docker-compose.yml"] = self.file_templates["docker_compose"](
                context
            )

        # Write files
        for file_path, content in config_files.items():
            full_path = os.path.join(output_path, file_path)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            structure[file_path] = "file"

        return structure

    async def _create_dev_tools(
        self, context: Dict[str, Any], output_path: str
    ) -> Dict[str, str]:
        """Create development tools and scripts"""

        structure = {}

        # Create scripts directory
        scripts_dir = os.path.join(output_path, "scripts")
        os.makedirs(scripts_dir, exist_ok=True)
        structure["scripts"] = "directory"

        # Development scripts
        dev_scripts = {
            "scripts/setup.sh": self._get_setup_script(context),
            "scripts/build.sh": self._get_build_script(context),
            "scripts/test.sh": self._get_test_script(context),
            "scripts/deploy.sh": self._get_deploy_script(context),
        }

        for script_path, content in dev_scripts.items():
            full_path = os.path.join(output_path, script_path)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            # Make scripts executable
            os.chmod(full_path, 0o755)
            structure[script_path] = "executable"

        return structure

    async def _create_docs_structure(
        self, context: Dict[str, Any], output_path: str
    ) -> Dict[str, str]:
        """Create documentation structure"""

        structure = {}

        if not context.get("include_docs", True):
            return structure

        # Documentation directories
        docs_dirs = ["docs", "docs/api", "docs/guides", "docs/examples", "docs/assets"]

        for dir_path in docs_dirs:
            full_path = os.path.join(output_path, dir_path)
            os.makedirs(full_path, exist_ok=True)
            structure[dir_path] = "directory"

        # Documentation files
        docs_files = {
            "docs/README.md": self._get_docs_readme(context),
            "docs/API.md": self._get_api_docs(context),
            "docs/CONTRIBUTING.md": self._get_contributing_docs(context),
            "docs/DEPLOYMENT.md": self._get_deployment_docs(context),
        }

        for file_path, content in docs_files.items():
            full_path = os.path.join(output_path, file_path)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            structure[file_path] = "file"

        return structure

    async def _create_test_structure(
        self, context: Dict[str, Any], output_path: str
    ) -> Dict[str, str]:
        """Create testing structure"""

        structure = {}

        if not context.get("include_tests", True):
            return structure

        # Test directories
        test_dirs = [
            "tests",
            "tests/unit",
            "tests/integration",
            "tests/e2e",
            "tests/fixtures",
            "tests/utils",
        ]

        for dir_path in test_dirs:
            full_path = os.path.join(output_path, dir_path)
            os.makedirs(full_path, exist_ok=True)
            structure[dir_path] = "directory"

        # Test configuration files
        framework = context.get("target_framework", "react")
        language = context.get("target_language", "javascript")

        test_files = {}

        if framework in ["react", "vue", "angular"]:
            test_files["jest.config.js"] = self._get_jest_config(context)
            test_files["tests/setupTests.js"] = self._get_test_setup(context)
        elif framework in ["fastapi", "django", "flask"]:
            test_files["pytest.ini"] = self._get_pytest_config(context)
            test_files["tests/conftest.py"] = self._get_pytest_conftest(context)

        for file_path, content in test_files.items():
            full_path = os.path.join(output_path, file_path)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            structure[file_path] = "file"

        return structure

    async def _create_deployment_structure(
        self, context: Dict[str, Any], output_path: str
    ) -> Dict[str, str]:
        """Create deployment structure"""

        structure = {}

        if not context.get("include_deployment", True):
            return structure

        # Deployment directories
        deploy_dirs = [
            "deploy",
            "deploy/k8s",
            "deploy/docker",
            "deploy/terraform",
            ".github/workflows",
        ]

        for dir_path in deploy_dirs:
            full_path = os.path.join(output_path, dir_path)
            os.makedirs(full_path, exist_ok=True)
            structure[dir_path] = "directory"

        # Deployment files
        deploy_files = {
            ".github/workflows/ci.yml": self._get_github_actions_ci(context),
            ".github/workflows/deploy.yml": self._get_github_actions_deploy(context),
            "deploy/k8s/deployment.yaml": self._get_k8s_deployment(context),
            "deploy/k8s/service.yaml": self._get_k8s_service(context),
        }

        for file_path, content in deploy_files.items():
            full_path = os.path.join(output_path, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            structure[file_path] = "file"

        return structure

    async def _create_gitkeep_files(self, output_path: str, structure: Dict[str, str]):
        """Create .gitkeep files for empty directories"""

        for path, file_type in structure.items():
            if file_type == "directory":
                full_path = os.path.join(output_path, path)
                if os.path.isdir(full_path) and not os.listdir(full_path):
                    gitkeep_path = os.path.join(full_path, ".gitkeep")
                    with open(gitkeep_path, "w") as f:
                        f.write("")

    def _determine_project_type(self, framework: str, context: Dict[str, Any]) -> str:
        """Determine project type based on framework"""

        frontend_frameworks = [
            "react",
            "vue",
            "angular",
            "svelte",
            "next.js",
            "nuxt.js",
        ]
        backend_frameworks = ["express", "fastapi", "django", "flask"]

        if framework in frontend_frameworks:
            return "frontend"
        elif framework in backend_frameworks:
            return "backend"
        else:
            return "fullstack"

    # File template methods
    def _get_gitignore_template(self, context: Dict[str, Any]) -> str:
        framework = context.get("target_framework", "react")

        base_gitignore = """# Dependencies
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Build outputs
dist/
build/
*.egg-info/
.eggs/

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local
"""

        if framework in ["react", "vue", "angular", "next.js"]:
            base_gitignore += """
# React/Vue/Angular specific
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.npm
.yarn-integrity
lerna-debug.log*

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/
*.lcov

# nyc test coverage
.nyc_output

# Dependency directories
jspm_packages/

# Optional npm cache directory
.npm

# Optional eslint cache
.eslintcache

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
.serverless/

# FuseBox cache
.fusebox/

# DynamoDB Local files
.dynamodb/

# TernJS port file
.tern-port
"""

        return base_gitignore

    def _get_readme_template(self, context: Dict[str, Any]) -> str:
        project_name = context.get("project_name", "My Project")
        framework = context.get("target_framework", "react")

        return f"""# {project_name}

A {framework} application generated with T-Developer.

## Getting Started

### Prerequisites

- Node.js (version 14 or higher)
- npm or yarn

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd {project_name.lower().replace(' ', '-')}
```

2. Install dependencies
```bash
npm install
# or
yarn install
```

3. Start the development server
```bash
npm run dev
# or
yarn dev
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run test` - Run tests
- `npm run lint` - Run ESLint

## Project Structure

```
{project_name.lower().replace(' ', '-')}/
├── src/
│   ├── components/
│   ├── pages/
│   ├── utils/
│   └── styles/
├── public/
├── tests/
└── docs/
```

## Contributing

Please read [CONTRIBUTING.md](docs/CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
"""

    def _get_license_template(self, context: Dict[str, Any]) -> str:
        return """MIT License

Copyright (c) 2024 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

    def _get_editorconfig_template(self, context: Dict[str, Any]) -> str:
        return """root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.{js,jsx,ts,tsx,vue}]
indent_style = space
indent_size = 2

[*.{py}]
indent_style = space
indent_size = 4

[*.{json,yml,yaml}]
indent_style = space
indent_size = 2

[*.md]
trim_trailing_whitespace = false
"""

    def _get_eslintrc_template(self, context: Dict[str, Any]) -> str:
        framework = context.get("target_framework", "react")

        if framework == "react":
            return """module.exports = {
  env: {
    browser: true,
    es2021: true,
    node: true,
  },
  extends: [
    'eslint:recommended',
    '@typescript-eslint/recommended',
    'plugin:react/recommended',
    'plugin:react-hooks/recommended',
  ],
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaFeatures: {
      jsx: true,
    },
    ecmaVersion: 12,
    sourceType: 'module',
  },
  plugins: [
    'react',
    '@typescript-eslint',
  ],
  rules: {
    'react/react-in-jsx-scope': 'off',
    '@typescript-eslint/explicit-module-boundary-types': 'off',
  },
  settings: {
    react: {
      version: 'detect',
    },
  },
};
"""
        else:
            return """module.exports = {
  env: {
    browser: true,
    es2021: true,
    node: true,
  },
  extends: [
    'eslint:recommended',
    '@typescript-eslint/recommended',
  ],
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaVersion: 12,
    sourceType: 'module',
  },
  plugins: [
    '@typescript-eslint',
  ],
  rules: {
    '@typescript-eslint/explicit-module-boundary-types': 'off',
  },
};
"""

    def _get_prettierrc_template(self, context: Dict[str, Any]) -> str:
        return """{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2,
  "useTabs": false
}
"""

    def _get_dockerfile_template(self, context: Dict[str, Any]) -> str:
        framework = context.get("target_framework", "react")

        if framework in ["react", "vue", "angular"]:
            return """# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

COPY --from=builder /app/build /usr/share/nginx/html
COPY --from=builder /app/nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
"""
        elif framework in ["fastapi", "flask"]:
            return """FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
        else:
            return """FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
"""

    def _get_docker_compose_template(self, context: Dict[str, Any]) -> str:
        project_name = context.get("project_name", "myapp")

        return f"""version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    volumes:
      - .:/app
      - /app/node_modules
    restart: unless-stopped

  database:
    image: postgres:13
    environment:
      - POSTGRES_DB={project_name}
      - POSTGRES_USER=admin
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
"""

    # React-specific templates
    def _get_react_index_html(self, context: Dict[str, Any]) -> str:
        project_name = context.get("project_name", "React App")

        return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="{project_name} - Created with T-Developer" />
    <link rel="apple-touch-icon" href="%PUBLIC_URL%/logo192.png" />
    <link rel="manifest" href="%PUBLIC_URL%/manifest.json" />
    <title>{project_name}</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
"""

    def _get_react_manifest(self, context: Dict[str, Any]) -> str:
        project_name = context.get("project_name", "React App")

        return json.dumps(
            {
                "short_name": project_name,
                "name": f"{project_name} - Created with T-Developer",
                "icons": [
                    {
                        "src": "favicon.ico",
                        "sizes": "64x64 32x32 24x24 16x16",
                        "type": "image/x-icon",
                    }
                ],
                "start_url": ".",
                "display": "standalone",
                "theme_color": "#000000",
                "background_color": "#ffffff",
            },
            indent=2,
        )

    def _get_react_index_css(self) -> str:
        return """body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}

* {
  box-sizing: border-box;
}
"""

    def _get_react_app_css(self) -> str:
        return """.App {
  text-align: center;
}

.App-header {
  background-color: #282c34;
  padding: 20px;
  color: white;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-size: calc(10px + 2vmin);
}

.App-link {
  color: #61dafb;
}
"""

    def _get_react_setup_tests(self) -> str:
        return """import '@testing-library/jest-dom';
"""

    def _get_react_report_web_vitals(self) -> str:
        return """const reportWebVitals = onPerfEntry => {
  if (onPerfEntry && onPerfEntry instanceof Function) {
    import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
      getCLS(onPerfEntry);
      getFID(onPerfEntry);
      getFCP(onPerfEntry);
      getLCP(onPerfEntry);
      getTTFB(onPerfEntry);
    });
  }
};

export default reportWebVitals;
"""

    # Vue-specific templates
    def _get_vue_index_html(self, context: Dict[str, Any]) -> str:
        project_name = context.get("project_name", "Vue App")

        return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{project_name}</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>
"""

    def _get_vue_style_css(self) -> str:
        return """#app {
  max-width: 1280px;
  margin: 0 auto;
  padding: 2rem;
  text-align: center;
}

body {
  margin: 0;
  display: flex;
  place-items: center;
  min-width: 320px;
  min-height: 100vh;
}

h1 {
  font-size: 3.2em;
  line-height: 1.1;
}
"""

    def _get_vue_vite_config(self) -> str:
        return """import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000
  }
})
"""

    # FastAPI-specific templates
    def _get_fastapi_requirements(self) -> str:
        return """fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.4.2
pydantic-settings==2.0.3
sqlalchemy==2.0.23
alembic==1.12.1
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
"""

    def _get_alembic_config(self) -> str:
        return """[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = postgresql://user:password@localhost/dbname

[post_write_hooks]

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
datefmt = %H:%M:%S
"""

    def _get_fastapi_env_example(self) -> str:
        return """# Database
DATABASE_URL=postgresql://user:password@localhost/dbname

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=development

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
"""

    # Additional template methods for scripts, documentation, etc.
    def _get_setup_script(self, context: Dict[str, Any]) -> str:
        framework = context.get("target_framework", "react")

        if framework in ["react", "vue", "angular"]:
            return """#!/bin/bash

echo "Setting up the project..."

# Install dependencies
npm install

# Create environment file
if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env file from .env.example"
fi

echo "Setup complete! Run 'npm run dev' to start development server."
"""
        else:
            return """#!/bin/bash

echo "Setting up the project..."

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

echo "Setup complete!"
"""

    def _get_build_script(self, context: Dict[str, Any]) -> str:
        framework = context.get("target_framework", "react")

        if framework in ["react", "vue", "angular"]:
            return """#!/bin/bash

echo "Building the project..."

npm run build

echo "Build complete!"
"""
        else:
            return """#!/bin/bash

echo "Building the project..."

# Add build commands here

echo "Build complete!"
"""

    def _get_test_script(self, context: Dict[str, Any]) -> str:
        framework = context.get("target_framework", "react")

        if framework in ["react", "vue", "angular"]:
            return """#!/bin/bash

echo "Running tests..."

npm test

echo "Tests complete!"
"""
        else:
            return """#!/bin/bash

echo "Running tests..."

pytest

echo "Tests complete!"
"""

    def _get_deploy_script(self, context: Dict[str, Any]) -> str:
        return """#!/bin/bash

echo "Deploying the project..."

# Build the project
./scripts/build.sh

# Deploy to production
echo "Add deployment commands here"

echo "Deployment complete!"
"""

    # Documentation templates
    def _get_docs_readme(self, context: Dict[str, Any]) -> str:
        project_name = context.get("project_name", "My Project")

        return f"""# {project_name} Documentation

Welcome to the {project_name} documentation!

## Table of Contents

- [API Documentation](API.md)
- [Contributing Guidelines](CONTRIBUTING.md)
- [Deployment Guide](DEPLOYMENT.md)

## Getting Started

This documentation will help you understand and work with {project_name}.

### Prerequisites

Make sure you have the required dependencies installed as described in the main README.

### Development

For development guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).

### API Reference

For API documentation, see [API.md](API.md).

### Deployment

For deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).
"""

    def _get_api_docs(self, context: Dict[str, Any]) -> str:
        project_name = context.get("project_name", "My Project")

        return f"""# {project_name} API Documentation

This document describes the API endpoints available in {project_name}.

## Base URL

```
http://localhost:3000/api
```

## Authentication

All API requests require authentication. Include your API key in the header:

```
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### GET /api/health

Health check endpoint.

**Response:**
```json
{{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z"
}}
```

### GET /api/version

Get API version information.

**Response:**
```json
{{
  "version": "1.0.0",
  "build": "12345"
}}
```

## Error Handling

All errors follow this format:

```json
{{
  "error": {{
    "code": "ERROR_CODE",
    "message": "Human readable error message"
  }}
}}
```

## Rate Limiting

API requests are limited to 100 requests per minute per IP address.
"""

    def _get_contributing_docs(self, context: Dict[str, Any]) -> str:
        project_name = context.get("project_name", "My Project")

        return f"""# Contributing to {project_name}

Thank you for your interest in contributing to {project_name}!

## Development Setup

1. Fork the repository
2. Clone your fork
3. Install dependencies
4. Create a feature branch
5. Make your changes
6. Run tests
7. Submit a pull request

## Code Style

We use ESLint and Prettier for code formatting. Make sure your code passes:

```bash
npm run lint
npm run format
```

## Testing

Run the test suite before submitting your PR:

```bash
npm test
```

## Commit Messages

Use conventional commit messages:

- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `style:` for formatting changes
- `refactor:` for code refactoring
- `test:` for adding tests
- `chore:` for maintenance tasks

## Pull Request Process

1. Ensure your code passes all tests
2. Update documentation as needed
3. Add tests for new functionality
4. Submit your pull request
5. Wait for code review

## Code of Conduct

Please be respectful and professional in all interactions.
"""

    def _get_deployment_docs(self, context: Dict[str, Any]) -> str:
        project_name = context.get("project_name", "My Project")

        return f"""# {project_name} Deployment Guide

This guide covers how to deploy {project_name} to various environments.

## Prerequisites

- Docker (optional)
- Node.js 18+ (for Node.js projects)
- Python 3.9+ (for Python projects)

## Local Development

```bash
npm install
npm run dev
```

## Production Build

```bash
npm run build
```

## Docker Deployment

1. Build the Docker image:
```bash
docker build -t {project_name.lower().replace(' ', '-')} .
```

2. Run the container:
```bash
docker run -p 3000:3000 {project_name.lower().replace(' ', '-')}
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```
NODE_ENV=production
API_URL=https://api.yourdomain.com
DATABASE_URL=postgresql://user:pass@host:port/db
```

## Health Checks

The application exposes a health check endpoint at `/health`.

## Monitoring

Consider setting up monitoring and logging for production deployments.
"""

    # Test configuration templates
    def _get_jest_config(self, context: Dict[str, Any]) -> str:
        return """module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/tests/setupTests.js'],
  moduleNameMapping: {
    '\\.(css|less|scss)$': 'identity-obj-proxy',
  },
  transform: {
    '^.+\\.(js|jsx|ts|tsx)$': ['babel-jest', { presets: ['next/babel'] }],
  },
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/index.js',
  ],
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70,
    },
  },
};
"""

    def _get_test_setup(self, context: Dict[str, Any]) -> str:
        return """import '@testing-library/jest-dom';

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});
"""

    def _get_pytest_config(self, context: Dict[str, Any]) -> str:
        return """[tool:pytest]
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
addopts =
    --strict-markers
    --strict-config
    --verbose
    --tb=short
    --cov=app
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
    --cov-fail-under=80
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
"""

    def _get_pytest_conftest(self, context: Dict[str, Any]) -> str:
        return """import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test-token"}
"""

    # GitHub Actions templates
    def _get_github_actions_ci(self, context: Dict[str, Any]) -> str:
        framework = context.get("target_framework", "react")

        if framework in ["react", "vue", "angular"]:
            return """name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [16.x, 18.x]

    steps:
    - uses: actions/checkout@v3

    - name: Use Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v3
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'

    - run: npm ci
    - run: npm run build --if-present
    - run: npm test

  lint:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'

    - run: npm ci
    - run: npm run lint
"""
        else:
            return """name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run tests
      run: |
        pytest
"""

    def _get_github_actions_deploy(self, context: Dict[str, Any]) -> str:
        project_name = context.get("project_name", "myapp")

        return f"""name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Build Docker image
      run: docker build -t {project_name.lower().replace(' ', '-')} .

    - name: Deploy to production
      run: |
        echo "Add deployment commands here"
        # Example: docker push, kubectl apply, etc.
"""

    # Kubernetes templates
    def _get_k8s_deployment(self, context: Dict[str, Any]) -> str:
        project_name = context.get("project_name", "myapp")
        app_name = project_name.lower().replace(" ", "-")

        return f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {app_name}
  labels:
    app: {app_name}
spec:
  replicas: 3
  selector:
    matchLabels:
      app: {app_name}
  template:
    metadata:
      labels:
        app: {app_name}
    spec:
      containers:
      - name: {app_name}
        image: {app_name}:latest
        ports:
        - containerPort: 3000
        env:
        - name: NODE_ENV
          value: "production"
        resources:
          limits:
            cpu: 500m
            memory: 512Mi
          requests:
            cpu: 200m
            memory: 256Mi
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
"""

    def _get_k8s_service(self, context: Dict[str, Any]) -> str:
        project_name = context.get("project_name", "myapp")
        app_name = project_name.lower().replace(" ", "-")

        return f"""apiVersion: v1
kind: Service
metadata:
  name: {app_name}-service
  labels:
    app: {app_name}
spec:
  selector:
    app: {app_name}
  ports:
    - protocol: TCP
      port: 80
      targetPort: 3000
  type: ClusterIP
"""


class ScaffolderResult:
    """Result of scaffolding operation"""

    def __init__(self, success: bool, data: Dict[str, Any], error: str = ""):
        self.success = success
        self.data = data
        self.error = error
