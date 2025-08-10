"""
Enhanced Code Generator for Production Pipeline
Generates comprehensive, production-ready code for various frameworks
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime


class EnhancedCodeGenerator:
    """Production-grade code generator with complete implementations"""
    
    @staticmethod
    def generate_react_todo_app(project_name: str, description: str, features: List[str] = None) -> Dict[str, str]:
        """Generate a complete React Todo application"""
        
        features = features or []
        use_typescript = 'typescript' in features
        use_tailwind = 'tailwind' in features
        ext = 'tsx' if use_typescript else 'jsx'
        
        files = {}
        
        # Package.json
        files['package.json'] = json.dumps({
            "name": project_name,
            "version": "1.0.0",
            "private": True,
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "uuid": "^9.0.0"
            },
            "devDependencies": {
                "@types/react": "^18.2.0" if use_typescript else None,
                "@types/react-dom": "^18.2.0" if use_typescript else None,
                "@types/uuid": "^9.0.0" if use_typescript else None,
                "typescript": "^5.0.0" if use_typescript else None,
                "@vitejs/plugin-react": "^4.0.0",
                "vite": "^4.4.0",
                "tailwindcss": "^3.3.0" if use_tailwind else None,
                "autoprefixer": "^10.4.14" if use_tailwind else None,
                "postcss": "^8.4.27" if use_tailwind else None
            },
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview"
            }
        }, indent=2)
        
        # Main App Component
        app_content = f"""import React, {{ useState, useEffect }} from 'react';
{f"import {{ v4 as uuidv4 }} from 'uuid';" if use_typescript else "import { v4 as uuidv4 } from 'uuid';"}
import './App.css';

{"interface Todo {" if use_typescript else "// Todo Item"}
{f"  id: string;" if use_typescript else ""}
{f"  text: string;" if use_typescript else ""}
{f"  completed: boolean;" if use_typescript else ""}
{f"  createdAt: Date;" if use_typescript else ""}
{"}" if use_typescript else ""}

function App() {{
  const [todos, setTodos] = useState{"<Todo[]>" if use_typescript else ""}([]);
  const [inputValue, setInputValue] = useState('');
  const [filter, setFilter] = useState('all');

  // Load todos from localStorage on mount
  useEffect(() => {{
    const savedTodos = localStorage.getItem('todos');
    if (savedTodos) {{
      setTodos(JSON.parse(savedTodos));
    }}
  }}, []);

  // Save todos to localStorage whenever they change
  useEffect(() => {{
    localStorage.setItem('todos', JSON.stringify(todos));
  }}, [todos]);

  const addTodo = () => {{
    if (inputValue.trim()) {{
      const newTodo{": Todo" if use_typescript else ""} = {{
        id: uuidv4(),
        text: inputValue,
        completed: false,
        createdAt: new Date()
      }};
      setTodos([...todos, newTodo]);
      setInputValue('');
    }}
  }};

  const toggleTodo = (id{": string" if use_typescript else ""}) => {{
    setTodos(todos.map(todo =>
      todo.id === id ? {{ ...todo, completed: !todo.completed }} : todo
    ));
  }};

  const deleteTodo = (id{": string" if use_typescript else ""}) => {{
    setTodos(todos.filter(todo => todo.id !== id));
  }};

  const clearCompleted = () => {{
    setTodos(todos.filter(todo => !todo.completed));
  }};

  const filteredTodos = todos.filter(todo => {{
    if (filter === 'active') return !todo.completed;
    if (filter === 'completed') return todo.completed;
    return true;
  }});

  const todosLeft = todos.filter(todo => !todo.completed).length;

  return (
    <div className="{f"min-h-screen bg-gray-100" if use_tailwind else "App"}">
      <div className="{f"container mx-auto max-w-2xl p-4" if use_tailwind else "container"}">
        <header className="{f"text-center py-8" if use_tailwind else "header"}">
          <h1 className="{f"text-4xl font-bold text-gray-800 mb-2" if use_tailwind else "title"}">{project_name}</h1>
          <p className="{f"text-gray-600" if use_tailwind else "subtitle"}">{description}</p>
        </header>

        <div className="{f"bg-white rounded-lg shadow-lg p-6" if use_tailwind else "todo-container"}">
          {/* Input Section */}
          <div className="{f"flex gap-2 mb-6" if use_tailwind else "input-section"}">
            <input
              type="text"
              value={{inputValue}}
              onChange={{(e) => setInputValue(e.target.value)}}
              onKeyPress={{(e) => e.key === 'Enter' && addTodo()}}
              placeholder="What needs to be done?"
              className="{f"flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" if use_tailwind else "todo-input"}"
            />
            <button
              onClick={{addTodo}}
              className="{f"px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors" if use_tailwind else "add-button"}"
            >
              Add
            </button>
          </div>

          {/* Filter Buttons */}
          <div className="{f"flex justify-center gap-2 mb-4" if use_tailwind else "filter-buttons"}">
            {{['all', 'active', 'completed'].map(filterType => (
              <button
                key={{filterType}}
                onClick={{() => setFilter(filterType)}}
                className={{`${{
                  filter === filterType
                    ? '{f"px-4 py-1 bg-blue-500 text-white rounded" if use_tailwind else "filter-active"}'
                    : '{f"px-4 py-1 bg-gray-200 text-gray-700 rounded hover:bg-gray-300" if use_tailwind else "filter-inactive"}'
                }}`}}
              >
                {{filterType.charAt(0).toUpperCase() + filterType.slice(1)}}
              </button>
            ))}}
          </div>

          {/* Todo List */}
          <ul className="{f"space-y-2 mb-4" if use_tailwind else "todo-list"}">
            {{filteredTodos.map(todo => (
              <li
                key={{todo.id}}
                className="{f"flex items-center gap-2 p-2 hover:bg-gray-50 rounded" if use_tailwind else "todo-item"}"
              >
                <input
                  type="checkbox"
                  checked={{todo.completed}}
                  onChange={{() => toggleTodo(todo.id)}}
                  className="{f"w-5 h-5" if use_tailwind else "todo-checkbox"}"
                />
                <span
                  className={{`${{
                    todo.completed
                      ? '{f"flex-1 text-gray-400 line-through" if use_tailwind else "todo-text completed"}'
                      : '{f"flex-1 text-gray-800" if use_tailwind else "todo-text"}'
                  }}`}}
                >
                  {{todo.text}}
                </span>
                <button
                  onClick={{() => deleteTodo(todo.id)}}
                  className="{f"px-3 py-1 text-red-500 hover:bg-red-50 rounded" if use_tailwind else "delete-button"}"
                >
                  Delete
                </button>
              </li>
            ))}}
          </ul>

          {/* Footer */}
          <div className="{f"flex justify-between items-center pt-4 border-t" if use_tailwind else "footer"}">
            <span className="{f"text-gray-600" if use_tailwind else "todos-left"}">
              {{todosLeft}} item{{todosLeft !== 1 ? 's' : ''}} left
            </span>
            <button
              onClick={{clearCompleted}}
              className="{f"text-gray-600 hover:text-gray-800" if use_tailwind else "clear-button"}"
            >
              Clear completed
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}}

export default App;"""
        
        files[f'src/App.{ext}'] = app_content
        
        # Main entry file
        files[f'src/main.{ext}'] = f"""import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root'){"!" if use_typescript else ""}).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);"""
        
        # Index.html
        files['index.html'] = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{project_name}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.{ext}"></script>
  </body>
</html>"""
        
        # CSS files
        if use_tailwind:
            files['src/index.css'] = """@tailwind base;
@tailwind components;
@tailwind utilities;"""
            
            files['tailwind.config.js'] = """/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}"""
            
            files['postcss.config.js'] = """export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}"""
        else:
            files['src/index.css'] = """* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  background-color: #f5f5f5;
  color: #333;
}

.App {
  min-height: 100vh;
  padding: 20px;
}

.container {
  max-width: 600px;
  margin: 0 auto;
}

.header {
  text-align: center;
  padding: 40px 0;
}

.title {
  font-size: 48px;
  color: #2c3e50;
  margin-bottom: 10px;
}

.subtitle {
  color: #7f8c8d;
  font-size: 16px;
}

.todo-container {
  background: white;
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.input-section {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
}

.todo-input {
  flex: 1;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.todo-input:focus {
  outline: none;
  border-color: #3498db;
}

.add-button {
  padding: 12px 24px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.add-button:hover {
  background-color: #2980b9;
}

.filter-buttons {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-bottom: 20px;
}

.filter-buttons button {
  padding: 6px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.filter-active {
  background-color: #3498db;
  color: white;
}

.filter-inactive {
  background-color: #ecf0f1;
  color: #2c3e50;
}

.filter-inactive:hover {
  background-color: #d5dbdd;
}

.todo-list {
  list-style: none;
  margin-bottom: 20px;
}

.todo-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border-radius: 4px;
}

.todo-item:hover {
  background-color: #f8f9fa;
}

.todo-checkbox {
  width: 20px;
  height: 20px;
  cursor: pointer;
}

.todo-text {
  flex: 1;
  font-size: 16px;
}

.todo-text.completed {
  color: #95a5a6;
  text-decoration: line-through;
}

.delete-button {
  padding: 4px 12px;
  background-color: transparent;
  color: #e74c3c;
  border: 1px solid #e74c3c;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.delete-button:hover {
  background-color: #e74c3c;
  color: white;
}

.footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 20px;
  border-top: 1px solid #ecf0f1;
  color: #7f8c8d;
  font-size: 14px;
}

.clear-button {
  background: none;
  border: none;
  color: #7f8c8d;
  cursor: pointer;
  font-size: 14px;
}

.clear-button:hover {
  color: #2c3e50;
  text-decoration: underline;
}"""
        
        files['src/App.css'] = ""
        
        # Vite config
        vite_config = f"""import {{ defineConfig }} from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({{
  plugins: [react()],
  server: {{
    port: 3000,
    open: true
  }}
}});"""
        
        files['vite.config.{}'.format('ts' if use_typescript else 'js')] = vite_config
        
        # TypeScript config if needed
        if use_typescript:
            files['tsconfig.json'] = json.dumps({
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
                    "noFallthroughCasesInSwitch": True
                },
                "include": ["src"],
                "references": [{"path": "./tsconfig.node.json"}]
            }, indent=2)
            
            files['tsconfig.node.json'] = json.dumps({
                "compilerOptions": {
                    "composite": True,
                    "skipLibCheck": True,
                    "module": "ESNext",
                    "moduleResolution": "bundler",
                    "allowSyntheticDefaultImports": True
                },
                "include": ["vite.config.ts"]
            }, indent=2)
        
        # README
        files['README.md'] = f"""# {project_name}

{description}

## Features

- ✅ Add, toggle, and delete todos
- 🔍 Filter todos (All, Active, Completed)
- 💾 LocalStorage persistence
- 📱 Responsive design
{"- 🎨 Tailwind CSS styling" if use_tailwind else "- 🎨 Custom CSS styling"}
{"- 📝 TypeScript support" if use_typescript else ""}

## Getting Started

### Prerequisites

- Node.js 16+ and npm

### Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

### Build for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Technologies Used

- React 18
- Vite
{"- TypeScript" if use_typescript else "- JavaScript"}
{"- Tailwind CSS" if use_tailwind else "- CSS3"}
- UUID for unique IDs
- LocalStorage API

## Project Structure

```
{project_name}/
├── src/
│   ├── App.{ext}      # Main application component
│   ├── main.{ext}     # Application entry point
│   ├── App.css        # Component styles
│   └── index.css      # Global styles
├── index.html         # HTML template
├── package.json       # Dependencies and scripts
├── vite.config.{f'ts' if use_typescript else 'js'}   # Vite configuration
{"├── tsconfig.json      # TypeScript configuration" if use_typescript else ""}
└── README.md          # This file
```

## License

MIT

---

Generated by T-Developer MVP with Production Pipeline
"""
        
        # .gitignore
        files['.gitignore'] = """# Dependencies
node_modules/
.pnp
.pnp.js

# Production
/dist
/build

# Misc
.DS_Store
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
*.swp
*.swo
*~

# Testing
/coverage

# TypeScript
*.tsbuildinfo"""
        
        return files
    
    @staticmethod
    def generate_project_files(project_type: str, project_name: str, description: str, features: List[str] = None) -> Dict[str, str]:
        """Generate project files based on type"""
        
        if project_type in ['react', 'todo', 'web']:
            return EnhancedCodeGenerator.generate_react_todo_app(project_name, description, features)
        else:
            # Default to React for now
            return EnhancedCodeGenerator.generate_react_todo_app(project_name, description, features)