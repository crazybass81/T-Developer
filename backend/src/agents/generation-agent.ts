/**
 * Generation Agent - 실제 코드 생성
 * Search Agent의 결과를 받아 완전한 프로젝트 코드를 생성
 */

import { SearchResult } from './search-agent';
import { ProjectStructure } from './parser-agent';
import { UISelectionResult } from './ui-selection-agent';

export interface GeneratedProject {
  projectName: string;
  structure: GeneratedStructure;
  files: GeneratedFile[];
  packageJson: string;
  configFiles: GeneratedFile[];
  readme: string;
  totalFiles: number;
  estimatedSize: string;
  buildInstructions: string[];
}

export interface GeneratedStructure {
  directories: string[];
  tree: string;
}

export interface GeneratedFile {
  path: string;
  content: string;
  type: 'component' | 'page' | 'service' | 'util' | 'config' | 'style' | 'test' | 'doc' | 'type';
  size: number;
  encoding: 'utf-8' | 'binary';
}

export interface CodeOptimization {
  minifyCode: boolean;
  removeComments: boolean;
  optimizeImports: boolean;
  treeshake: boolean;
}

export class GenerationAgent {
  private name = 'Generation Agent';
  private optimization: CodeOptimization;

  constructor() {
    this.optimization = {
      minifyCode: false,
      removeComments: false,
      optimizeImports: true,
      treeshake: true
    };
  }

  /**
   * Search 결과를 기반으로 완전한 프로젝트 생성
   */
  async generateProject(
    searchResults: SearchResult[],
    projectStructure: ProjectStructure,
    uiSelection: UISelectionResult,
    projectName: string
  ): Promise<GeneratedProject> {
    console.log(`[${this.name}] Generating complete project: ${projectName}`);

    // 1. 파일 생성
    const files = await this.generateAllFiles(searchResults, projectStructure, uiSelection);

    // 2. 패키지.json 생성
    const packageJsonContent = this.generatePackageJson(projectStructure.packageJson, projectName);

    // 3. 설정 파일들 생성
    const configFiles = await this.generateConfigFiles(projectStructure.configFiles, uiSelection);

    // 4. README 생성
    const readme = await this.generateReadme(projectName, uiSelection, searchResults);

    // 5. 프로젝트 구조 생성
    const structure = this.generateProjectStructure(files, configFiles);

    // 6. 빌드 지시사항 생성
    const buildInstructions = this.generateBuildInstructions(uiSelection);

    const generatedProject: GeneratedProject = {
      projectName,
      structure,
      files,
      packageJson: packageJsonContent,
      configFiles,
      readme,
      totalFiles: files.length + configFiles.length + 1, // +1 for package.json
      estimatedSize: this.calculateProjectSize(files, configFiles, packageJsonContent),
      buildInstructions
    };

    console.log(`[${this.name}] Generated project with ${generatedProject.totalFiles} files`);
    return generatedProject;
  }

  private async generateAllFiles(
    searchResults: SearchResult[],
    projectStructure: ProjectStructure,
    uiSelection: UISelectionResult
  ): Promise<GeneratedFile[]> {
    const files: GeneratedFile[] = [];

    // 1. 컴포넌트 파일들 생성
    for (const searchResult of searchResults) {
      const componentFiles = await this.generateComponentFiles(searchResult, uiSelection);
      files.push(...componentFiles);
    }

    // 2. 메인 애플리케이션 파일들 생성
    const appFiles = await this.generateAppFiles(uiSelection, searchResults);
    files.push(...appFiles);

    // 3. 유틸리티 및 서비스 파일들 생성
    const utilFiles = await this.generateUtilityFiles(searchResults);
    files.push(...utilFiles);

    // 4. 스타일 파일들 생성
    const styleFiles = await this.generateStyleFiles(uiSelection, searchResults);
    files.push(...styleFiles);

    return files;
  }

  private async generateComponentFiles(
    searchResult: SearchResult,
    uiSelection: UISelectionResult
  ): Promise<GeneratedFile[]> {
    const files: GeneratedFile[] = [];
    const { componentName, codeTemplate, relatedFiles } = searchResult;

    // 메인 컴포넌트 파일
    const extension = this.getFileExtension(uiSelection.framework);
    const componentPath = `/src/components/${componentName}/${componentName}.${extension}`;
    
    files.push({
      path: componentPath,
      content: this.optimizeCode(codeTemplate),
      type: 'component',
      size: codeTemplate.length,
      encoding: 'utf-8'
    });

    // 관련 파일들
    for (const relatedFile of relatedFiles) {
      files.push({
        path: relatedFile.path,
        content: this.optimizeCode(relatedFile.content),
        type: relatedFile.type,
        size: relatedFile.content.length,
        encoding: 'utf-8'
      });
    }

    // 인덱스 파일 (컴포넌트 export용)
    const indexContent = `export { default } from './${componentName}';
export type { ${componentName}Props } from './${componentName}.types';`;
    
    files.push({
      path: `/src/components/${componentName}/index.${extension}`,
      content: indexContent,
      type: 'component',
      size: indexContent.length,
      encoding: 'utf-8'
    });

    return files;
  }

  private async generateAppFiles(
    uiSelection: UISelectionResult,
    searchResults: SearchResult[]
  ): Promise<GeneratedFile[]> {
    const files: GeneratedFile[] = [];
    const extension = this.getFileExtension(uiSelection.framework);

    // App.tsx/App.vue
    const appContent = this.generateAppComponent(uiSelection, searchResults);
    files.push({
      path: `/src/App.${extension}`,
      content: appContent,
      type: 'component',
      size: appContent.length,
      encoding: 'utf-8'
    });

    // main.tsx/index.tsx
    const mainContent = this.generateMainFile(uiSelection);
    files.push({
      path: `/src/main.${extension}`,
      content: mainContent,
      type: 'component',
      size: mainContent.length,
      encoding: 'utf-8'
    });

    // 라우터 파일 (필요한 경우)
    if (uiSelection.routing && uiSelection.routing !== 'none') {
      const routerContent = this.generateRouterFile(uiSelection, searchResults);
      files.push({
        path: `/src/router/index.${extension}`,
        content: routerContent,
        type: 'config',
        size: routerContent.length,
        encoding: 'utf-8'
      });
    }

    // 상태 관리 파일 (필요한 경우)
    if (uiSelection.stateManagement) {
      const storeContent = this.generateStoreFile(uiSelection);
      files.push({
        path: `/src/store/index.${extension}`,
        content: storeContent,
        type: 'service',
        size: storeContent.length,
        encoding: 'utf-8'
      });
    }

    return files;
  }

  private generateAppComponent(
    uiSelection: UISelectionResult,
    searchResults: SearchResult[]
  ): string {
    const { framework, componentLibrary, routing, stateManagement } = uiSelection;

    if (framework === 'react' || framework === 'nextjs') {
      let imports = [`import React from 'react';`];
      let providers = [''];
      let content = '';

      // 컴포넌트 라이브러리 Provider 추가
      if (componentLibrary === 'antd') {
        imports.push(`import { ConfigProvider } from 'antd';`);
        providers.push('ConfigProvider');
      } else if (componentLibrary === 'mui') {
        imports.push(`import { ThemeProvider, createTheme } from '@mui/material/styles';`);
        imports.push(`import CssBaseline from '@mui/material/CssBaseline';`);
        content += `\nconst theme = createTheme();`;
        providers.push('ThemeProvider', 'CssBaseline');
      } else if (componentLibrary === 'chakra-ui') {
        imports.push(`import { ChakraProvider } from '@chakra-ui/react';`);
        providers.push('ChakraProvider');
      }

      // 라우터 추가
      if (routing === 'react-router-dom') {
        imports.push(`import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';`);
      }

      // 상태 관리 추가
      if (stateManagement === 'redux-toolkit') {
        imports.push(`import { Provider } from 'react-redux';`);
        imports.push(`import { store } from './store';`);
      }

      // 컴포넌트 imports
      const componentImports = searchResults
        .filter(sr => sr.componentName.endsWith('Page'))
        .map(sr => `import ${sr.componentName} from './pages/${sr.componentName}';`);
      imports.push(...componentImports);

      return `${imports.join('\n')}
import './App.css';${content}

function App() {
  return (
    ${this.wrapWithProviders(providers, `
    <div className="App">
      ${routing === 'react-router-dom' ? this.generateRoutes(searchResults) : '<header className="App-header"><h1>Welcome to Your App</h1></header>'}
    </div>
    `, stateManagement)}
  );
}

export default App;`;
    } else if (framework === 'vue') {
      return `<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'App'
});
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}
</style>`;
    }

    return '// App component';
  }

  private wrapWithProviders(providers: string[], content: string, stateManagement?: string): string {
    let wrapped = content;
    
    if (stateManagement === 'redux-toolkit') {
      wrapped = `<Provider store={store}>${wrapped}</Provider>`;
    }

    if (providers.includes('ChakraProvider')) {
      wrapped = `<ChakraProvider>${wrapped}</ChakraProvider>`;
    }

    if (providers.includes('ConfigProvider')) {
      wrapped = `<ConfigProvider>${wrapped}</ConfigProvider>`;
    }

    if (providers.includes('ThemeProvider')) {
      wrapped = `<ThemeProvider theme={theme}><CssBaseline />${wrapped}</ThemeProvider>`;
    }

    return wrapped;
  }

  private generateRoutes(searchResults: SearchResult[]): string {
    const pageComponents = searchResults.filter(sr => sr.componentName.endsWith('Page'));
    
    if (pageComponents.length === 0) {
      return '<div>No pages found</div>';
    }

    const routes = pageComponents.map(page => {
      const route = page.componentName.replace('Page', '').toLowerCase();
      return `        <Route path="/${route === 'home' ? '' : route}" element={<${page.componentName} />} />`;
    }).join('\n');

    return `<Router>
      <Routes>
${routes}
      </Routes>
    </Router>`;
  }

  private generateMainFile(uiSelection: UISelectionResult): string {
    const { framework } = uiSelection;

    if (framework === 'react' || framework === 'nextjs') {
      return `import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);`;
    } else if (framework === 'vue') {
      return `import { createApp } from 'vue';
import App from './App.vue';
import router from './router';

const app = createApp(App);
app.use(router);
app.mount('#app');`;
    }

    return '// Main entry point';
  }

  private generateRouterFile(uiSelection: UISelectionResult, searchResults: SearchResult[]): string {
    if (uiSelection.framework === 'vue') {
      const routes = searchResults
        .filter(sr => sr.componentName.endsWith('Page'))
        .map(page => {
          const routeName = page.componentName.replace('Page', '');
          const routePath = routeName.toLowerCase() === 'home' ? '/' : `/${routeName.toLowerCase()}`;
          return `  {
    path: '${routePath}',
    name: '${routeName}',
    component: () => import('../pages/${page.componentName}.vue')
  }`;
        }).join(',\n');

      return `import { createRouter, createWebHistory } from 'vue-router';

const routes = [
${routes}
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;`;
    }

    return '// Router configuration';
  }

  private generateStoreFile(uiSelection: UISelectionResult): string {
    if (uiSelection.stateManagement === 'redux-toolkit') {
      return `import { configureStore } from '@reduxjs/toolkit';

export const store = configureStore({
  reducer: {
    // Add your reducers here
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;`;
    } else if (uiSelection.stateManagement === 'zustand') {
      return `import { create } from 'zustand';

interface AppState {
  // Define your state here
}

export const useAppStore = create<AppState>()((set) => ({
  // Define your state and actions here
}));`;
    } else if (uiSelection.stateManagement === 'pinia') {
      return `import { defineStore } from 'pinia';

export const useMainStore = defineStore('main', {
  state: () => ({
    // Define your state here
  }),
  
  getters: {
    // Define your getters here
  },
  
  actions: {
    // Define your actions here
  }
});`;
    }

    return '// State management';
  }

  private async generateUtilityFiles(searchResults: SearchResult[]): Promise<GeneratedFile[]> {
    const files: GeneratedFile[] = [];

    // API 유틸리티
    const apiUtilContent = `import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = \`Bearer \${token}\`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;`;

    files.push({
      path: '/src/utils/api.ts',
      content: apiUtilContent,
      type: 'util',
      size: apiUtilContent.length,
      encoding: 'utf-8'
    });

    // 상수들
    const constantsContent = `export const API_ENDPOINTS = {
  AUTH: '/auth',
  USERS: '/users',
  // Add more endpoints as needed
};

export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  DASHBOARD: '/dashboard',
  // Add more routes as needed
};

export const STORAGE_KEYS = {
  TOKEN: 'token',
  USER: 'user',
  // Add more keys as needed
};`;

    files.push({
      path: '/src/constants/index.ts',
      content: constantsContent,
      type: 'util',
      size: constantsContent.length,
      encoding: 'utf-8'
    });

    return files;
  }

  private async generateStyleFiles(
    uiSelection: UISelectionResult,
    searchResults: SearchResult[]
  ): Promise<GeneratedFile[]> {
    const files: GeneratedFile[] = [];

    // Global styles
    const globalStylesContent = this.generateGlobalStyles(uiSelection);
    const styleExtension = uiSelection.stylingApproach === 'sass' ? 'scss' : 'css';
    
    files.push({
      path: `/src/index.${styleExtension}`,
      content: globalStylesContent,
      type: 'style',
      size: globalStylesContent.length,
      encoding: 'utf-8'
    });

    // App styles
    const appStylesContent = this.generateAppStyles(uiSelection);
    files.push({
      path: `/src/App.${styleExtension}`,
      content: appStylesContent,
      type: 'style',
      size: appStylesContent.length,
      encoding: 'utf-8'
    });

    return files;
  }

  private generateGlobalStyles(uiSelection: UISelectionResult): string {
    const baseStyles = `* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  line-height: 1.6;
  color: #333;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}`;

    if (uiSelection.stylingApproach === 'tailwind') {
      return `@tailwind base;
@tailwind components;
@tailwind utilities;

${baseStyles}`;
    }

    return baseStyles;
  }

  private generateAppStyles(uiSelection: UISelectionResult): string {
    return `.App {
  text-align: center;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.App-header {
  background-color: #282c34;
  padding: 20px;
  color: white;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.App-header h1 {
  margin-bottom: 20px;
  font-size: 2.5rem;
}`;
  }

  private async generateConfigFiles(
    configFiles: any[],
    uiSelection: UISelectionResult
  ): Promise<GeneratedFile[]> {
    const files: GeneratedFile[] = [];

    for (const config of configFiles) {
      files.push({
        path: config.path,
        content: config.content,
        type: 'config',
        size: config.content.length,
        encoding: 'utf-8'
      });
    }

    // Environment 파일들
    const envContent = this.generateEnvFile();
    files.push({
      path: '/.env.example',
      content: envContent,
      type: 'config',
      size: envContent.length,
      encoding: 'utf-8'
    });

    // .gitignore
    const gitignoreContent = this.generateGitignore();
    files.push({
      path: '/.gitignore',
      content: gitignoreContent,
      type: 'config',
      size: gitignoreContent.length,
      encoding: 'utf-8'
    });

    return files;
  }

  private generateEnvFile(): string {
    return `# Environment Variables
REACT_APP_API_URL=http://localhost:3000/api
REACT_APP_APP_NAME="Your App Name"

# Remove these comments in your actual .env file
# Add your API keys and sensitive information here`;
  }

  private generateGitignore(): string {
    return `# Dependencies
node_modules/
.pnp
.pnp.js

# Testing
coverage/

# Production
build/
dist/

# Environment variables
.env.local
.env.development.local
.env.test.local
.env.production.local

# Logs
npm-debug.log*
yarn-debug.log*
yarn-error.log*
lerna-debug.log*

# Editor directories and files
.vscode/
.idea/
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db`;
  }

  private async generateReadme(
    projectName: string,
    uiSelection: UISelectionResult,
    searchResults: SearchResult[]
  ): Promise<string> {
    const components = searchResults.map(sr => sr.componentName).join(', ');
    
    return `# ${projectName}

A ${uiSelection.framework} application built with T-Developer.

## 🚀 Features

- Built with ${uiSelection.framework}
- UI Components: ${uiSelection.componentLibrary}
- Styling: ${uiSelection.stylingApproach}
${uiSelection.stateManagement ? `- State Management: ${uiSelection.stateManagement}` : ''}
${uiSelection.routing ? `- Routing: ${uiSelection.routing}` : ''}

## 📦 Components

${components}

## 🛠 Installation

\`\`\`bash
npm install
\`\`\`

## 🏃 Running the Application

\`\`\`bash
npm run dev
\`\`\`

## 🧪 Testing

\`\`\`bash
npm test
\`\`\`

## 🏗 Building for Production

\`\`\`bash
npm run build
\`\`\`

## 📝 Project Structure

\`\`\`
src/
├── components/     # Reusable components
├── pages/         # Application pages
├── services/      # API services
├── utils/         # Utility functions
├── styles/        # Global styles
└── types/         # TypeScript types
\`\`\`

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (\`git checkout -b feature/amazing-feature\`)
3. Commit your changes (\`git commit -m 'Add some amazing feature'\`)
4. Push to the branch (\`git push origin feature/amazing-feature\`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

---

Generated with ❤️ by T-Developer`;
  }

  private generatePackageJson(packageJsonTemplate: any, projectName: string): string {
    const packageJson = {
      ...packageJsonTemplate,
      name: projectName.toLowerCase().replace(/\s+/g, '-'),
      description: `A modern web application built with T-Developer`,
      author: "Generated by T-Developer",
      license: "MIT",
      keywords: [
        "react",
        "typescript",
        "web-app",
        "t-developer"
      ]
    };

    return JSON.stringify(packageJson, null, 2);
  }

  private generateProjectStructure(
    files: GeneratedFile[],
    configFiles: GeneratedFile[]
  ): GeneratedStructure {
    const allFiles = [...files, ...configFiles];
    const directories = new Set<string>();
    
    // Extract directories
    allFiles.forEach(file => {
      const parts = file.path.split('/');
      for (let i = 1; i < parts.length - 1; i++) {
        const dirPath = parts.slice(0, i + 1).join('/');
        directories.add(dirPath);
      }
    });

    const sortedDirs = Array.from(directories).sort();
    const tree = this.generateDirectoryTree(allFiles);

    return {
      directories: sortedDirs,
      tree
    };
  }

  private generateDirectoryTree(files: GeneratedFile[]): string {
    const tree = new Map<string, string[]>();
    
    files.forEach(file => {
      const parts = file.path.split('/');
      const filename = parts[parts.length - 1];
      const dirPath = parts.slice(0, -1).join('/') || '/';
      
      if (!tree.has(dirPath)) {
        tree.set(dirPath, []);
      }
      tree.get(dirPath)!.push(filename);
    });

    let treeStr = 'Project Structure:\n';
    const sortedPaths = Array.from(tree.keys()).sort();
    
    sortedPaths.forEach(path => {
      const depth = (path.match(/\//g) || []).length - 1;
      const indent = '  '.repeat(depth);
      const folderName = path === '/' ? '/' : path.split('/').pop();
      
      if (path !== '/') {
        treeStr += `${indent}📁 ${folderName}/\n`;
      }
      
      const files = tree.get(path)!.sort();
      files.forEach(file => {
        const fileIndent = '  '.repeat(depth + 1);
        const icon = this.getFileIcon(file);
        treeStr += `${fileIndent}${icon} ${file}\n`;
      });
    });

    return treeStr;
  }

  private getFileIcon(filename: string): string {
    const ext = filename.split('.').pop()?.toLowerCase();
    
    switch (ext) {
      case 'tsx':
      case 'jsx':
        return '⚛️';
      case 'ts':
      case 'js':
        return '📜';
      case 'css':
      case 'scss':
      case 'sass':
        return '🎨';
      case 'json':
        return '📋';
      case 'md':
        return '📖';
      case 'html':
        return '🌐';
      case 'test':
        return '🧪';
      default:
        return '📄';
    }
  }

  private generateBuildInstructions(uiSelection: UISelectionResult): string[] {
    const instructions: string[] = [
      '1. Install dependencies: npm install',
      `2. Start development server: npm run dev`,
      '3. Open http://localhost:3000 in your browser'
    ];

    if (uiSelection.buildTool === 'nextjs') {
      instructions[1] = '2. Start development server: npm run dev';
      instructions[2] = '3. Open http://localhost:3000 in your browser';
    }

    instructions.push('4. Build for production: npm run build');
    
    if (uiSelection.buildTool === 'nextjs') {
      instructions.push('5. Start production server: npm start');
    }

    return instructions;
  }

  private getFileExtension(framework: string): string {
    switch (framework) {
      case 'vue':
        return 'vue';
      case 'react':
      case 'nextjs':
      default:
        return 'tsx';
    }
  }

  private optimizeCode(code: string): string {
    let optimized = code;

    if (this.optimization.optimizeImports) {
      optimized = this.optimizeImports(optimized);
    }

    if (this.optimization.removeComments) {
      optimized = this.removeComments(optimized);
    }

    return optimized;
  }

  private optimizeImports(code: string): string {
    // Remove duplicate imports
    const lines = code.split('\n');
    const importLines = lines.filter(line => line.trim().startsWith('import'));
    const uniqueImports = [...new Set(importLines)];
    
    const nonImportLines = lines.filter(line => !line.trim().startsWith('import'));
    
    return [...uniqueImports, '', ...nonImportLines].join('\n');
  }

  private removeComments(code: string): string {
    // Remove single line comments
    return code.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');
  }

  private calculateProjectSize(
    files: GeneratedFile[],
    configFiles: GeneratedFile[],
    packageJson: string
  ): string {
    const totalBytes = files.reduce((sum, file) => sum + file.size, 0) +
                      configFiles.reduce((sum, file) => sum + file.size, 0) +
                      packageJson.length;

    if (totalBytes < 1024) return `${totalBytes} B`;
    if (totalBytes < 1024 * 1024) return `${(totalBytes / 1024).toFixed(1)} KB`;
    return `${(totalBytes / (1024 * 1024)).toFixed(1)} MB`;
  }
}