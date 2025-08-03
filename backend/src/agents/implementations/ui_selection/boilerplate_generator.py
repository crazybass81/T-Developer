# backend/src/agents/implementations/ui_selection/boilerplate_generator.py
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class BoilerplateTemplate:
    framework: str
    template_name: str
    files: Dict[str, str]
    dependencies: List[str]
    dev_dependencies: List[str]
    scripts: Dict[str, str]
    setup_instructions: List[str]

class BoilerplateGenerator:
    """보일러플레이트 코드 생성기"""

    def __init__(self):
        self.templates = self._initialize_templates()

    def _initialize_templates(self) -> Dict[str, Dict[str, Any]]:
        """템플릿 초기화"""
        return {
            'react': {
                'basic': self._react_basic_template(),
                'typescript': self._react_typescript_template(),
                'nextjs': self._nextjs_template()
            },
            'vue': {
                'basic': self._vue_basic_template(),
                'typescript': self._vue_typescript_template(),
                'nuxt': self._nuxt_template()
            },
            'angular': {
                'basic': self._angular_basic_template()
            }
        }

    async def generate_boilerplate(
        self,
        framework: str,
        template_type: str = 'basic',
        project_name: str = 'my-app',
        options: Optional[Dict[str, Any]] = None
    ) -> BoilerplateTemplate:
        """보일러플레이트 생성"""
        
        template_config = self.templates.get(framework, {}).get(template_type)
        
        if not template_config:
            raise ValueError(f"Template {template_type} not found for {framework}")
        
        # 프로젝트명으로 치환
        files = {}
        for file_path, content in template_config['files'].items():
            processed_content = content.replace('{{PROJECT_NAME}}', project_name)
            processed_content = processed_content.replace('{{FRAMEWORK}}', framework)
            files[file_path] = processed_content
        
        # 옵션 적용
        if options:
            files = self._apply_options(files, options)
        
        return BoilerplateTemplate(
            framework=framework,
            template_name=template_type,
            files=files,
            dependencies=template_config['dependencies'],
            dev_dependencies=template_config['dev_dependencies'],
            scripts=template_config['scripts'],
            setup_instructions=template_config['setup_instructions']
        )

    def _react_basic_template(self) -> Dict[str, Any]:
        """React 기본 템플릿"""
        return {
            'files': {
                'package.json': '''{
  "name": "{{PROJECT_NAME}}",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": ["react-app", "react-app/jest"]
  },
  "browserslist": {
    "production": [">0.2%", "not dead", "not op_mini all"],
    "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
  }
}''',
                'public/index.html': '''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="{{PROJECT_NAME}} - Built with React" />
    <title>{{PROJECT_NAME}}</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>''',
                'src/index.js': '''import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);''',
                'src/App.js': '''import React from 'react';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Welcome to {{PROJECT_NAME}}</h1>
        <p>Built with React</p>
      </header>
    </div>
  );
}

export default App;''',
                'src/App.css': '''.App {
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
}''',
                'src/index.css': '''body {
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
}'''
            },
            'dependencies': ['react', 'react-dom', 'react-scripts'],
            'dev_dependencies': [],
            'scripts': {
                'start': 'react-scripts start',
                'build': 'react-scripts build',
                'test': 'react-scripts test'
            },
            'setup_instructions': [
                'npm install',
                'npm start'
            ]
        }

    def _react_typescript_template(self) -> Dict[str, Any]:
        """React TypeScript 템플릿"""
        return {
            'files': {
                'package.json': '''{
  "name": "{{PROJECT_NAME}}",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "typescript": "^4.9.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test"
  }
}''',
                'tsconfig.json': '''{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "es6"],
    "allowJs": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noFallthroughCasesInSwitch": true,
    "module": "esnext",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx"
  },
  "include": ["src"]
}''',
                'src/App.tsx': '''import React from 'react';
import './App.css';

const App: React.FC = () => {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Welcome to {{PROJECT_NAME}}</h1>
        <p>Built with React & TypeScript</p>
      </header>
    </div>
  );
};

export default App;''',
                'src/index.tsx': '''import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);'''
            },
            'dependencies': ['react', 'react-dom', 'react-scripts'],
            'dev_dependencies': ['@types/react', '@types/react-dom', 'typescript'],
            'scripts': {
                'start': 'react-scripts start',
                'build': 'react-scripts build',
                'test': 'react-scripts test'
            },
            'setup_instructions': [
                'npm install',
                'npm start'
            ]
        }

    def _vue_basic_template(self) -> Dict[str, Any]:
        """Vue 기본 템플릿"""
        return {
            'files': {
                'package.json': '''{
  "name": "{{PROJECT_NAME}}",
  "version": "0.0.0",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.3.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^4.2.0",
    "vite": "^4.3.0"
  }
}''',
                'index.html': '''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <link rel="icon" href="/favicon.ico">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{PROJECT_NAME}}</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>''',
                'vite.config.js': '''import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
})''',
                'src/main.js': '''import { createApp } from 'vue'
import './style.css'
import App from './App.vue'

createApp(App).mount('#app')''',
                'src/App.vue': '''<template>
  <div id="app">
    <header>
      <h1>Welcome to {{PROJECT_NAME}}</h1>
      <p>Built with Vue.js</p>
    </header>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
#app {
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

header {
  background-color: #42b883;
  padding: 20px;
  color: white;
}
</style>''',
                'src/style.css': '''body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
}'''
            },
            'dependencies': ['vue'],
            'dev_dependencies': ['@vitejs/plugin-vue', 'vite'],
            'scripts': {
                'dev': 'vite',
                'build': 'vite build',
                'preview': 'vite preview'
            },
            'setup_instructions': [
                'npm install',
                'npm run dev'
            ]
        }

    def _nextjs_template(self) -> Dict[str, Any]:
        """Next.js 템플릿"""
        return {
            'files': {
                'package.json': '''{
  "name": "{{PROJECT_NAME}}",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "13.4.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "eslint": "8.42.0",
    "eslint-config-next": "13.4.0"
  }
}''',
                'next.config.js': '''/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
}

module.exports = nextConfig''',
                'pages/index.js': '''import Head from 'next/head'

export default function Home() {
  return (
    <>
      <Head>
        <title>{{PROJECT_NAME}}</title>
        <meta name="description" content="Built with Next.js" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main>
        <h1>Welcome to {{PROJECT_NAME}}</h1>
        <p>Built with Next.js</p>
      </main>
    </>
  )
}''',
                'pages/_app.js': '''import '@/styles/globals.css'

export default function App({ Component, pageProps }) {
  return <Component {...pageProps} />
}''',
                'styles/globals.css': '''html,
body {
  padding: 0;
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen,
    Ubuntu, Cantarell, Fira Sans, Droid Sans, Helvetica Neue, sans-serif;
}

main {
  min-height: 100vh;
  padding: 4rem 0;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}'''
            },
            'dependencies': ['next', 'react', 'react-dom'],
            'dev_dependencies': ['eslint', 'eslint-config-next'],
            'scripts': {
                'dev': 'next dev',
                'build': 'next build',
                'start': 'next start'
            },
            'setup_instructions': [
                'npm install',
                'npm run dev'
            ]
        }

    def _apply_options(self, files: Dict[str, str], options: Dict[str, Any]) -> Dict[str, str]:
        """옵션 적용"""
        
        # PWA 옵션
        if options.get('pwa', False):
            files = self._add_pwa_support(files)
        
        # ESLint 옵션
        if options.get('eslint', False):
            files = self._add_eslint_config(files)
        
        # Prettier 옵션
        if options.get('prettier', False):
            files = self._add_prettier_config(files)
        
        return files

    def _add_pwa_support(self, files: Dict[str, str]) -> Dict[str, str]:
        """PWA 지원 추가"""
        
        files['public/manifest.json'] = '''{
  "short_name": "App",
  "name": "{{PROJECT_NAME}}",
  "icons": [
    {
      "src": "favicon.ico",
      "sizes": "64x64 32x32 24x24 16x16",
      "type": "image/x-icon"
    }
  ],
  "start_url": ".",
  "display": "standalone",
  "theme_color": "#000000",
  "background_color": "#ffffff"
}'''
        
        return files

    def _add_eslint_config(self, files: Dict[str, str]) -> Dict[str, str]:
        """ESLint 설정 추가"""
        
        files['.eslintrc.json'] = '''{
  "extends": ["next/core-web-vitals"],
  "rules": {
    "no-unused-vars": "warn",
    "no-console": "warn"
  }
}'''
        
        return files

    def _add_prettier_config(self, files: Dict[str, str]) -> Dict[str, str]:
        """Prettier 설정 추가"""
        
        files['.prettierrc'] = '''{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2
}'''
        
        return files