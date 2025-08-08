/**
 * Project Generator
 * 실제 프로젝트 파일을 생성하는 핵심 엔진
 */

import * as fs from 'fs-extra';
import * as path from 'path';
import { execSync } from 'child_process';

export interface ProjectConfig {
  name: string;
  type: 'react' | 'vue' | 'nextjs' | 'express' | 'fastapi';
  description: string;
  features: string[];
  dependencies?: Record<string, string>;
}

export class ProjectGenerator {
  private templatesPath: string;
  private outputPath: string;

  constructor() {
    this.templatesPath = path.join(__dirname, '../templates');
    this.outputPath = path.join(__dirname, '../../../generated');
    
    // 출력 디렉토리 생성
    fs.ensureDirSync(this.outputPath);
  }

  /**
   * 프로젝트 생성
   */
  async generateProject(config: ProjectConfig): Promise<string> {
    const projectPath = path.join(this.outputPath, config.name);
    
    // 기존 프로젝트 삭제
    if (fs.existsSync(projectPath)) {
      fs.removeSync(projectPath);
    }
    
    // 프로젝트 디렉토리 생성
    fs.ensureDirSync(projectPath);
    
    // 프로젝트 타입별 생성
    switch (config.type) {
      case 'react':
        await this.generateReactProject(projectPath, config);
        break;
      case 'vue':
        await this.generateVueProject(projectPath, config);
        break;
      case 'nextjs':
        await this.generateNextProject(projectPath, config);
        break;
      default:
        throw new Error(`Unsupported project type: ${config.type}`);
    }
    
    return projectPath;
  }

  /**
   * React 프로젝트 생성
   */
  private async generateReactProject(projectPath: string, config: ProjectConfig) {
    // package.json 생성
    const packageJson = {
      name: config.name,
      version: "0.1.0",
      private: true,
      description: config.description,
      dependencies: {
        "react": "^18.2.0",
        "react-dom": "^18.2.0",
        "react-scripts": "5.0.1",
        "web-vitals": "^2.1.4",
        ...config.dependencies
      },
      scripts: {
        "start": "react-scripts start",
        "build": "react-scripts build",
        "test": "react-scripts test",
        "eject": "react-scripts eject"
      },
      eslintConfig: {
        extends: ["react-app", "react-app/jest"]
      },
      browserslist: {
        production: [">0.2%", "not dead", "not op_mini all"],
        development: ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
      }
    };
    
    fs.writeJsonSync(path.join(projectPath, 'package.json'), packageJson, { spaces: 2 });
    
    // public 디렉토리 생성
    const publicPath = path.join(projectPath, 'public');
    fs.ensureDirSync(publicPath);
    
    // index.html 생성
    const indexHtml = `<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="${config.description}" />
    <title>${config.name}</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>`;
    
    fs.writeFileSync(path.join(publicPath, 'index.html'), indexHtml);
    
    // src 디렉토리 생성
    const srcPath = path.join(projectPath, 'src');
    fs.ensureDirSync(srcPath);
    
    // App.js 생성
    const appJs = this.generateReactAppComponent(config);
    fs.writeFileSync(path.join(srcPath, 'App.js'), appJs);
    
    // index.js 생성
    const indexJs = `import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);`;
    
    fs.writeFileSync(path.join(srcPath, 'index.js'), indexJs);
    
    // index.css 생성
    const indexCss = `body {
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
}`;
    
    fs.writeFileSync(path.join(srcPath, 'index.css'), indexCss);
    
    // App.css 생성
    const appCss = `.App {
  text-align: center;
  padding: 20px;
}

.App-header {
  background-color: #282c34;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-size: calc(10px + 2vmin);
  color: white;
}`;
    
    fs.writeFileSync(path.join(srcPath, 'App.css'), appCss);
    
    // README.md 생성
    const readme = `# ${config.name}

${config.description}

## Getting Started

\`\`\`bash
npm install
npm start
\`\`\`

## Features

${config.features.map(f => `- ${f}`).join('\n')}

## Available Scripts

- \`npm start\`: Runs the app in development mode
- \`npm test\`: Launches the test runner
- \`npm run build\`: Builds the app for production

Generated by T-Developer`;
    
    fs.writeFileSync(path.join(projectPath, 'README.md'), readme);
    
    // .gitignore 생성
    const gitignore = `node_modules
.env.local
.env.development.local
.env.test.local
.env.production.local
npm-debug.log*
yarn-debug.log*
yarn-error.log*
/build
/.vscode`;
    
    fs.writeFileSync(path.join(projectPath, '.gitignore'), gitignore);
  }

  /**
   * React App 컴포넌트 생성
   */
  private generateReactAppComponent(config: ProjectConfig): string {
    const hasRouter = config.features.includes('routing');
    const hasState = config.features.includes('state-management');
    
    let imports = `import React${hasState ? ', { useState }' : ''} from 'react';
import './App.css';`;
    
    if (hasRouter) {
      imports += `\nimport { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';`;
    }
    
    let component = `
function App() {`;
    
    if (hasState) {
      component += `
  const [count, setCount] = useState(0);`;
    }
    
    component += `
  
  return (
    <div className="App">
      <header className="App-header">
        <h1>${config.name}</h1>
        <p>${config.description}</p>`;
    
    if (hasState) {
      component += `
        <div>
          <p>Count: {count}</p>
          <button onClick={() => setCount(count + 1)}>Increment</button>
        </div>`;
    }
    
    if (config.features.includes('todo')) {
      component += `
        <TodoList />`;
    }
    
    component += `
      </header>
    </div>
  );
}`;
    
    // Todo 컴포넌트 추가 (필요한 경우)
    if (config.features.includes('todo')) {
      component += `

function TodoList() {
  const [todos, setTodos] = React.useState([]);
  const [input, setInput] = React.useState('');
  
  const addTodo = () => {
    if (input.trim()) {
      setTodos([...todos, { id: Date.now(), text: input, done: false }]);
      setInput('');
    }
  };
  
  const toggleTodo = (id) => {
    setTodos(todos.map(todo => 
      todo.id === id ? { ...todo, done: !todo.done } : todo
    ));
  };
  
  const deleteTodo = (id) => {
    setTodos(todos.filter(todo => todo.id !== id));
  };
  
  return (
    <div className="todo-list">
      <h2>Todo List</h2>
      <div>
        <input 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && addTodo()}
          placeholder="Add a todo..."
        />
        <button onClick={addTodo}>Add</button>
      </div>
      <ul>
        {todos.map(todo => (
          <li key={todo.id}>
            <span 
              style={{ textDecoration: todo.done ? 'line-through' : 'none' }}
              onClick={() => toggleTodo(todo.id)}
            >
              {todo.text}
            </span>
            <button onClick={() => deleteTodo(todo.id)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}`;
    }
    
    component += `

export default App;`;
    
    return imports + component;
  }

  /**
   * Vue 프로젝트 생성
   */
  private async generateVueProject(projectPath: string, config: ProjectConfig) {
    // package.json 생성
    const packageJson = {
      name: config.name,
      version: "0.1.0",
      private: true,
      description: config.description,
      scripts: {
        "serve": "vue-cli-service serve",
        "build": "vue-cli-service build",
        "lint": "vue-cli-service lint"
      },
      dependencies: {
        "core-js": "^3.8.3",
        "vue": "^3.2.13",
        ...config.dependencies
      },
      devDependencies: {
        "@vue/cli-plugin-babel": "~5.0.0",
        "@vue/cli-plugin-eslint": "~5.0.0",
        "@vue/cli-service": "~5.0.0"
      }
    };
    
    fs.writeJsonSync(path.join(projectPath, 'package.json'), packageJson, { spaces: 2 });
    
    // Vue 프로젝트 구조 생성
    // ... (Vue 특화 구조)
  }

  /**
   * Next.js 프로젝트 생성
   */
  private async generateNextProject(projectPath: string, config: ProjectConfig) {
    // package.json 생성
    const packageJson = {
      name: config.name,
      version: "0.1.0",
      private: true,
      description: config.description,
      scripts: {
        "dev": "next dev",
        "build": "next build",
        "start": "next start",
        "lint": "next lint"
      },
      dependencies: {
        "next": "14.0.0",
        "react": "^18",
        "react-dom": "^18",
        ...config.dependencies
      }
    };
    
    fs.writeJsonSync(path.join(projectPath, 'package.json'), packageJson, { spaces: 2 });
    
    // Next.js 프로젝트 구조 생성
    // ... (Next.js 특화 구조)
  }
}

export const projectGenerator = new ProjectGenerator();