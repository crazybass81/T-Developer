# backend/src/agents/implementations/ui_selection/boilerplate_generator.py
from typing import Dict, List, Optional, Any
import json

class BoilerplateGenerator:
    """보일러플레이트 설정 생성기"""
    
    FRAMEWORK_CONFIGS = {
        'react': {
            'package_json': {
                'scripts': {
                    'start': 'react-scripts start',
                    'build': 'react-scripts build',
                    'test': 'react-scripts test',
                    'eject': 'react-scripts eject'
                },
                'dependencies': {
                    'react': '^18.2.0',
                    'react-dom': '^18.2.0',
                    'react-scripts': '5.0.1'
                }
            },
            'tsconfig': {
                'compilerOptions': {
                    'target': 'es5',
                    'lib': ['dom', 'dom.iterable', 'es6'],
                    'allowJs': True,
                    'skipLibCheck': True,
                    'esModuleInterop': True,
                    'allowSyntheticDefaultImports': True,
                    'strict': True,
                    'forceConsistentCasingInFileNames': True,
                    'noFallthroughCasesInSwitch': True,
                    'module': 'esnext',
                    'moduleResolution': 'node',
                    'resolveJsonModule': True,
                    'isolatedModules': True,
                    'noEmit': True,
                    'jsx': 'react-jsx'
                }
            }
        },
        'vue': {
            'package_json': {
                'scripts': {
                    'serve': 'vue-cli-service serve',
                    'build': 'vue-cli-service build',
                    'test:unit': 'vue-cli-service test:unit',
                    'lint': 'vue-cli-service lint'
                },
                'dependencies': {
                    'vue': '^3.2.13',
                    'vue-router': '^4.0.3',
                    'vuex': '^4.0.0'
                }
            },
            'tsconfig': {
                'compilerOptions': {
                    'target': 'esnext',
                    'module': 'esnext',
                    'strict': True,
                    'jsx': 'preserve',
                    'importHelpers': True,
                    'moduleResolution': 'node',
                    'skipLibCheck': True,
                    'esModuleInterop': True,
                    'allowSyntheticDefaultImports': True,
                    'sourceMap': True,
                    'baseUrl': '.',
                    'types': ['webpack-env']
                }
            }
        },
        'nextjs': {
            'package_json': {
                'scripts': {
                    'dev': 'next dev',
                    'build': 'next build',
                    'start': 'next start',
                    'lint': 'next lint'
                },
                'dependencies': {
                    'next': '13.4.0',
                    'react': '^18.2.0',
                    'react-dom': '^18.2.0'
                }
            },
            'next_config': {
                'experimental': {
                    'appDir': True
                },
                'images': {
                    'domains': []
                }
            }
        }
    }
    
    DESIGN_SYSTEM_CONFIGS = {
        'material-ui': {
            'dependencies': {
                '@mui/material': '^5.13.0',
                '@emotion/react': '^11.11.0',
                '@emotion/styled': '^11.11.0'
            },
            'theme_template': '''
import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});
'''
        },
        'tailwind-ui': {
            'dependencies': {
                'tailwindcss': '^3.3.0',
                'autoprefixer': '^10.4.14',
                'postcss': '^8.4.24'
            },
            'config_template': '''
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
'''
        },
        'chakra-ui': {
            'dependencies': {
                '@chakra-ui/react': '^2.7.0',
                '@emotion/react': '^11.11.0',
                '@emotion/styled': '^11.11.0',
                'framer-motion': '^10.12.0'
            },
            'theme_template': '''
import { extendTheme } from '@chakra-ui/react';

const theme = extendTheme({
  colors: {
    brand: {
      100: "#f7fafc",
      900: "#1a202c",
    },
  },
});

export default theme;
'''
        }
    }

    async def generate_config(
        self,
        framework: str,
        design_system: str,
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """보일러플레이트 설정 생성"""
        
        config = {
            'framework': framework,
            'design_system': design_system,
            'files': {},
            'dependencies': {},
            'scripts': {},
            'setup_commands': []
        }
        
        # 프레임워크 기본 설정
        framework_config = self.FRAMEWORK_CONFIGS.get(framework, {})
        if framework_config:
            config['files']['package.json'] = self._merge_package_json(
                framework_config.get('package_json', {}),
                requirements
            )
            
            if 'tsconfig' in framework_config:
                config['files']['tsconfig.json'] = framework_config['tsconfig']
            
            if 'next_config' in framework_config:
                config['files']['next.config.js'] = framework_config['next_config']
        
        # 디자인 시스템 설정
        design_config = self.DESIGN_SYSTEM_CONFIGS.get(design_system, {})
        if design_config:
            # 의존성 병합
            config['dependencies'].update(design_config.get('dependencies', {}))
            
            # 테마/설정 파일
            if 'theme_template' in design_config:
                config['files']['theme.js'] = design_config['theme_template']
            
            if 'config_template' in design_config:
                if design_system == 'tailwind-ui':
                    config['files']['tailwind.config.js'] = design_config['config_template']
        
        # TypeScript 설정
        if requirements.get('typescript', False):
            config['dependencies']['typescript'] = '^5.0.0'
            config['dependencies']['@types/react'] = '^18.2.0'
            config['dependencies']['@types/react-dom'] = '^18.2.0'
        
        # 테스트 설정
        if requirements.get('testing', False):
            config['dependencies']['@testing-library/react'] = '^13.4.0'
            config['dependencies']['@testing-library/jest-dom'] = '^5.16.0'
            config['dependencies']['@testing-library/user-event'] = '^14.4.0'
        
        # ESLint/Prettier 설정
        if requirements.get('linting', True):
            config['dependencies']['eslint'] = '^8.42.0'
            config['dependencies']['prettier'] = '^2.8.0'
            config['files']['.eslintrc.js'] = self._generate_eslint_config(framework)
            config['files']['.prettierrc'] = self._generate_prettier_config()
        
        # 설치 명령어 생성
        config['setup_commands'] = self._generate_setup_commands(
            framework, design_system, requirements
        )
        
        return config

    def _merge_package_json(
        self,
        base_config: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """package.json 병합"""
        
        merged = base_config.copy()
        
        # 프로젝트 정보
        merged.update({
            'name': requirements.get('project_name', 'my-app'),
            'version': '0.1.0',
            'private': True
        })
        
        return merged

    def _generate_eslint_config(self, framework: str) -> str:
        """ESLint 설정 생성"""
        
        configs = {
            'react': '''
module.exports = {
  env: {
    browser: true,
    es2021: true,
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
    ecmaVersion: 'latest',
    sourceType: 'module',
  },
  plugins: ['react', '@typescript-eslint'],
  rules: {
    'react/react-in-jsx-scope': 'off',
  },
};
''',
            'vue': '''
module.exports = {
  env: {
    node: true,
  },
  extends: [
    'eslint:recommended',
    '@vue/typescript/recommended',
    'plugin:vue/vue3-recommended',
  ],
  parserOptions: {
    ecmaVersion: 2020,
  },
  rules: {
    'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
  },
};
'''
        }
        
        return configs.get(framework, configs['react'])

    def _generate_prettier_config(self) -> str:
        """Prettier 설정 생성"""
        
        return json.dumps({
            'semi': True,
            'trailingComma': 'es5',
            'singleQuote': True,
            'printWidth': 80,
            'tabWidth': 2
        }, indent=2)

    def _generate_setup_commands(
        self,
        framework: str,
        design_system: str,
        requirements: Dict[str, Any]
    ) -> List[str]:
        """설치 명령어 생성"""
        
        commands = []
        
        # 프로젝트 생성
        if framework == 'react':
            commands.append('npx create-react-app my-app --template typescript')
        elif framework == 'vue':
            commands.append('vue create my-app')
        elif framework == 'nextjs':
            commands.append('npx create-next-app@latest my-app --typescript --tailwind --eslint')
        
        # 디자인 시스템 설치
        if design_system == 'material-ui':
            commands.append('npm install @mui/material @emotion/react @emotion/styled')
        elif design_system == 'tailwind-ui':
            commands.append('npm install -D tailwindcss postcss autoprefixer')
            commands.append('npx tailwindcss init -p')
        elif design_system == 'chakra-ui':
            commands.append('npm install @chakra-ui/react @emotion/react @emotion/styled framer-motion')
        
        # 추가 도구 설치
        if requirements.get('testing', False):
            commands.append('npm install --save-dev @testing-library/react @testing-library/jest-dom')
        
        if requirements.get('linting', True):
            commands.append('npm install --save-dev eslint prettier')
        
        return commands

    async def generate_starter_files(
        self,
        framework: str,
        design_system: str
    ) -> Dict[str, str]:
        """스타터 파일 생성"""
        
        files = {}
        
        # App 컴포넌트
        if framework == 'react':
            files['src/App.tsx'] = self._generate_react_app(design_system)
            files['src/index.tsx'] = self._generate_react_index(design_system)
        elif framework == 'vue':
            files['src/App.vue'] = self._generate_vue_app(design_system)
            files['src/main.ts'] = self._generate_vue_main(design_system)
        
        return files

    def _generate_react_app(self, design_system: str) -> str:
        """React App 컴포넌트 생성"""
        
        if design_system == 'material-ui':
            return '''
import React from 'react';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { theme } from './theme';
import './App.css';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <div className="App">
        <h1>Welcome to your new app!</h1>
      </div>
    </ThemeProvider>
  );
}

export default App;
'''
        elif design_system == 'chakra-ui':
            return '''
import React from 'react';
import { ChakraProvider } from '@chakra-ui/react';
import theme from './theme';
import './App.css';

function App() {
  return (
    <ChakraProvider theme={theme}>
      <div className="App">
        <h1>Welcome to your new app!</h1>
      </div>
    </ChakraProvider>
  );
}

export default App;
'''
        else:
            return '''
import React from 'react';
import './App.css';

function App() {
  return (
    <div className="App">
      <h1>Welcome to your new app!</h1>
    </div>
  );
}

export default App;
'''

    def _generate_react_index(self, design_system: str) -> str:
        """React index 파일 생성"""
        
        return '''
import React from 'react';
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
);
'''