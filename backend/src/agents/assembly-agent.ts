/**
 * Assembly Agent - 프로젝트 조립 및 최종 검증
 * Generation Agent의 결과를 받아 프로젝트를 조립하고 최종 검증 수행
 */

import { GeneratedProject, GeneratedFile } from './generation-agent';

export interface AssembledProject {
  projectName: string;
  version: string;
  structure: ProjectStructure;
  files: AssembledFile[];
  metadata: ProjectMetadata;
  validation: ValidationResult;
  buildSystem: BuildSystemConfig;
  deploymentConfig: DeploymentConfig;
  qualityMetrics: QualityMetrics;
}

export interface AssembledFile extends GeneratedFile {
  validated: boolean;
  minified?: boolean;
  compressed?: boolean;
  checksum?: string;
  dependencies: string[];
  exports: string[];
}

export interface ProjectStructure {
  directories: DirectoryInfo[];
  totalFiles: number;
  totalSize: string;
  tree: string;
}

export interface DirectoryInfo {
  path: string;
  files: number;
  size: string;
  purpose: string;
}

export interface ProjectMetadata {
  createdAt: string;
  generator: string;
  generatorVersion: string;
  framework: string;
  componentLibrary?: string;
  stateManagement?: string;
  buildTool: string;
  nodeVersion: string;
  npmVersion?: string;
  author?: string;
  license: string;
  repository?: string;
}

export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
  score: number;
  passed: number;
  failed: number;
  skipped: number;
}

export interface ValidationError {
  type: 'syntax' | 'dependency' | 'structure' | 'configuration';
  file: string;
  line?: number;
  column?: number;
  message: string;
  severity: 'error' | 'warning';
  fixable: boolean;
}

export interface ValidationWarning {
  type: 'performance' | 'accessibility' | 'security' | 'best-practice';
  file: string;
  message: string;
  suggestion: string;
}

export interface BuildSystemConfig {
  tool: string;
  version: string;
  commands: BuildCommand[];
  hooks: BuildHook[];
  optimizations: BuildOptimization[];
}

export interface BuildCommand {
  name: string;
  command: string;
  description: string;
  environment: 'development' | 'production' | 'test' | 'all';
}

export interface BuildHook {
  phase: 'pre-build' | 'post-build' | 'pre-test' | 'post-test';
  command: string;
  description: string;
}

export interface BuildOptimization {
  name: string;
  enabled: boolean;
  config: Record<string, any>;
}

export interface DeploymentConfig {
  platform: string[];
  environment: Record<string, string>;
  scripts: DeploymentScript[];
  healthChecks: HealthCheck[];
}

export interface DeploymentScript {
  name: string;
  command: string;
  platform: string;
  description: string;
}

export interface HealthCheck {
  name: string;
  url: string;
  method: 'GET' | 'POST';
  expectedStatus: number;
  timeout: number;
}

export interface QualityMetrics {
  codeComplexity: number;
  maintainabilityIndex: number;
  testCoverage: number;
  duplicatedCode: number;
  technicalDebt: number;
  securityScore: number;
  performanceScore: number;
  accessibilityScore: number;
}

export class AssemblyAgent {
  private name = 'Assembly Agent';
  private validators: Map<string, Function>;

  constructor() {
    this.validators = this.initializeValidators();
  }

  /**
   * Generated Project를 최종 조립 및 검증
   */
  async assembleProject(generatedProject: GeneratedProject): Promise<AssembledProject> {
    console.log(`[${this.name}] Assembling project: ${generatedProject.projectName}`);

    // 1. 파일들 처리 및 검증
    const assembledFiles = await this.processFiles(generatedProject.files);

    // 2. 프로젝트 구조 분석
    const structure = await this.analyzeStructure(assembledFiles);

    // 3. 프로젝트 메타데이터 생성
    const metadata = this.generateMetadata(generatedProject);

    // 4. 전체 프로젝트 검증
    const validation = await this.validateProject(assembledFiles, generatedProject);

    // 5. 빌드 시스템 구성
    const buildSystem = this.configureBuildSystem(generatedProject);

    // 6. 배포 구성 생성
    const deploymentConfig = this.generateDeploymentConfig(generatedProject);

    // 7. 품질 메트릭 계산
    const qualityMetrics = await this.calculateQualityMetrics(assembledFiles);

    const assembledProject: AssembledProject = {
      projectName: generatedProject.projectName,
      version: '1.0.0',
      structure,
      files: assembledFiles,
      metadata,
      validation,
      buildSystem,
      deploymentConfig,
      qualityMetrics
    };

    console.log(`[${this.name}] Assembly completed with ${validation.score}% validation score`);
    return assembledProject;
  }

  private async processFiles(files: GeneratedFile[]): Promise<AssembledFile[]> {
    const processedFiles: AssembledFile[] = [];

    for (const file of files) {
      const assembledFile = await this.processFile(file);
      processedFiles.push(assembledFile);
    }

    return processedFiles;
  }

  private async processFile(file: GeneratedFile): Promise<AssembledFile> {
    // 파일 검증
    const validated = await this.validateFile(file);

    // 의존성 분석
    const dependencies = this.extractDependencies(file.content);

    // Export 분석
    const exports = this.extractExports(file.content);

    // 체크섬 생성
    const checksum = this.generateChecksum(file.content);

    return {
      ...file,
      validated,
      dependencies,
      exports,
      checksum
    };
  }

  private async validateFile(file: GeneratedFile): Promise<boolean> {
    const extension = this.getFileExtension(file.path);
    const validator = this.validators.get(extension);

    if (validator) {
      try {
        return await validator(file.content);
      } catch (error) {
        console.warn(`[${this.name}] Validation failed for ${file.path}:`, error);
        return false;
      }
    }

    return true; // 검증기가 없는 파일은 기본적으로 유효하다고 가정
  }

  private extractDependencies(content: string): string[] {
    const dependencies: string[] = [];
    
    // import 문에서 의존성 추출
    const importRegex = /import\s+.*?\s+from\s+['"`]([^'"`]+)['"`]/g;
    let match;

    while ((match = importRegex.exec(content)) !== null) {
      const dep = match[1];
      if (!dep.startsWith('.') && !dep.startsWith('/')) {
        dependencies.push(dep);
      }
    }

    // require 문에서 의존성 추출
    const requireRegex = /require\(['"`]([^'"`]+)['"`]\)/g;
    while ((match = requireRegex.exec(content)) !== null) {
      const dep = match[1];
      if (!dep.startsWith('.') && !dep.startsWith('/')) {
        dependencies.push(dep);
      }
    }

    return [...new Set(dependencies)];
  }

  private extractExports(content: string): string[] {
    const exports: string[] = [];
    
    // export 문 추출
    const exportRegex = /export\s+(?:default\s+)?(?:class|function|const|let|var|interface|type)\s+(\w+)/g;
    let match;

    while ((match = exportRegex.exec(content)) !== null) {
      exports.push(match[1]);
    }

    // export default 추출
    if (content.includes('export default')) {
      exports.push('default');
    }

    return [...new Set(exports)];
  }

  private generateChecksum(content: string): string {
    // 간단한 체크섬 생성 (실제로는 crypto 모듈 사용 권장)
    let hash = 0;
    for (let i = 0; i < content.length; i++) {
      const char = content.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // 32비트 정수로 변환
    }
    return Math.abs(hash).toString(16);
  }

  private async analyzeStructure(files: AssembledFile[]): Promise<ProjectStructure> {
    const directories = new Map<string, { files: number; size: number; purpose: string }>();
    let totalSize = 0;

    files.forEach(file => {
      const dir = file.path.substring(0, file.path.lastIndexOf('/')) || '/';
      totalSize += file.size;

      if (!directories.has(dir)) {
        directories.set(dir, { files: 0, size: 0, purpose: this.getDirectoryPurpose(dir) });
      }

      const dirInfo = directories.get(dir)!;
      dirInfo.files++;
      dirInfo.size += file.size;
    });

    const directoryInfos: DirectoryInfo[] = Array.from(directories.entries()).map(([path, info]) => ({
      path,
      files: info.files,
      size: this.formatSize(info.size),
      purpose: info.purpose
    }));

    const tree = this.generateProjectTree(files);

    return {
      directories: directoryInfos,
      totalFiles: files.length,
      totalSize: this.formatSize(totalSize),
      tree
    };
  }

  private getDirectoryPurpose(path: string): string {
    if (path.includes('/components')) return 'Reusable UI components';
    if (path.includes('/pages')) return 'Application pages/routes';
    if (path.includes('/services')) return 'API and business logic';
    if (path.includes('/utils')) return 'Utility functions';
    if (path.includes('/hooks')) return 'Custom React hooks';
    if (path.includes('/store')) return 'State management';
    if (path.includes('/styles')) return 'Styling and themes';
    if (path.includes('/types')) return 'TypeScript definitions';
    if (path.includes('/tests') || path.includes('__tests__')) return 'Test files';
    if (path.includes('/assets')) return 'Static assets';
    if (path === '/') return 'Root configuration files';
    return 'Project files';
  }

  private formatSize(bytes: number): string {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  private generateProjectTree(files: AssembledFile[]): string {
    // 파일들을 디렉토리별로 그룹화
    const tree = new Map<string, string[]>();
    
    files.forEach(file => {
      const dir = file.path.substring(0, file.path.lastIndexOf('/')) || '/';
      const fileName = file.path.substring(file.path.lastIndexOf('/') + 1);
      
      if (!tree.has(dir)) {
        tree.set(dir, []);
      }
      tree.get(dir)!.push(fileName);
    });

    // 트리 문자열 생성
    let treeStr = '';
    const sortedDirs = Array.from(tree.keys()).sort();
    
    sortedDirs.forEach(dir => {
      const depth = (dir.match(/\//g) || []).length - 1;
      const indent = '  '.repeat(depth);
      const dirName = dir === '/' ? '' : dir.split('/').pop();
      
      if (dirName) {
        treeStr += `${indent}📁 ${dirName}/\n`;
      }
      
      const sortedFiles = tree.get(dir)!.sort();
      sortedFiles.forEach(file => {
        const fileIndent = '  '.repeat(depth + (dirName ? 1 : 0));
        const icon = this.getFileIcon(file);
        treeStr += `${fileIndent}${icon} ${file}\n`;
      });
    });

    return treeStr;
  }

  private generateMetadata(generatedProject: GeneratedProject): ProjectMetadata {
    return {
      createdAt: new Date().toISOString(),
      generator: 'T-Developer',
      generatorVersion: '1.0.0',
      framework: 'react', // 추후 동적으로 결정
      buildTool: 'vite', // 추후 동적으로 결정
      nodeVersion: process.version || '18.0.0',
      license: 'MIT',
      author: 'T-Developer Generator'
    };
  }

  private async validateProject(
    files: AssembledFile[],
    generatedProject: GeneratedProject
  ): Promise<ValidationResult> {
    const errors: ValidationError[] = [];
    const warnings: ValidationWarning[] = [];
    let passed = 0;
    let failed = 0;

    // 파일별 검증
    for (const file of files) {
      try {
        if (file.validated) {
          passed++;
        } else {
          failed++;
          errors.push({
            type: 'syntax',
            file: file.path,
            message: 'File validation failed',
            severity: 'error',
            fixable: false
          });
        }
      } catch (error) {
        failed++;
        errors.push({
          type: 'syntax',
          file: file.path,
          message: `Validation error: ${error}`,
          severity: 'error',
          fixable: false
        });
      }
    }

    // 구조 검증
    this.validateProjectStructure(files, errors, warnings);

    // 의존성 검증
    this.validateDependencies(files, generatedProject, errors, warnings);

    const total = passed + failed;
    const score = total > 0 ? Math.round((passed / total) * 100) : 0;

    return {
      isValid: errors.filter(e => e.severity === 'error').length === 0,
      errors,
      warnings,
      score,
      passed,
      failed,
      skipped: 0
    };
  }

  private validateProjectStructure(
    files: AssembledFile[],
    errors: ValidationError[],
    warnings: ValidationWarning[]
  ): void {
    // 필수 파일 확인
    const requiredFiles = ['package.json', 'src/App.tsx', 'src/main.tsx'];
    
    requiredFiles.forEach(requiredFile => {
      const found = files.some(f => f.path.endsWith(requiredFile));
      if (!found) {
        errors.push({
          type: 'structure',
          file: requiredFile,
          message: `Required file ${requiredFile} is missing`,
          severity: 'error',
          fixable: true
        });
      }
    });

    // src 디렉토리 구조 확인
    const hasSrcDir = files.some(f => f.path.startsWith('/src/'));
    if (!hasSrcDir) {
      errors.push({
        type: 'structure',
        file: '/src',
        message: 'Source directory /src is missing',
        severity: 'error',
        fixable: true
      });
    }
  }

  private validateDependencies(
    files: AssembledFile[],
    generatedProject: GeneratedProject,
    errors: ValidationError[],
    warnings: ValidationWarning[]
  ): void {
    // 사용된 의존성과 package.json의 의존성 비교
    const usedDependencies = new Set<string>();
    
    files.forEach(file => {
      file.dependencies.forEach(dep => usedDependencies.add(dep));
    });

    // package.json에서 선언된 의존성 추출 (간단한 구현)
    const packageJsonFile = files.find(f => f.path.endsWith('package.json'));
    if (packageJsonFile) {
      try {
        const packageJson = JSON.parse(packageJsonFile.content);
        const declaredDeps = new Set([
          ...Object.keys(packageJson.dependencies || {}),
          ...Object.keys(packageJson.devDependencies || {})
        ]);

        // 사용되지만 선언되지 않은 의존성
        usedDependencies.forEach(dep => {
          if (!declaredDeps.has(dep) && !dep.startsWith('@types/')) {
            warnings.push({
              type: 'best-practice',
              file: 'package.json',
              message: `Dependency '${dep}' is used but not declared in package.json`,
              suggestion: `Add '${dep}' to dependencies in package.json`
            });
          }
        });
      } catch (error) {
        errors.push({
          type: 'configuration',
          file: 'package.json',
          message: 'Invalid package.json format',
          severity: 'error',
          fixable: false
        });
      }
    }
  }

  private configureBuildSystem(generatedProject: GeneratedProject): BuildSystemConfig {
    const commands: BuildCommand[] = [
      {
        name: 'dev',
        command: 'npm run dev',
        description: 'Start development server',
        environment: 'development'
      },
      {
        name: 'build',
        command: 'npm run build',
        description: 'Build for production',
        environment: 'production'
      },
      {
        name: 'test',
        command: 'npm test',
        description: 'Run tests',
        environment: 'test'
      },
      {
        name: 'lint',
        command: 'npm run lint',
        description: 'Run linter',
        environment: 'all'
      }
    ];

    const hooks: BuildHook[] = [
      {
        phase: 'pre-build',
        command: 'npm run lint',
        description: 'Run linter before build'
      },
      {
        phase: 'post-build',
        command: 'npm run test',
        description: 'Run tests after build'
      }
    ];

    const optimizations: BuildOptimization[] = [
      {
        name: 'minification',
        enabled: true,
        config: { terser: true }
      },
      {
        name: 'tree-shaking',
        enabled: true,
        config: { sideEffects: false }
      },
      {
        name: 'code-splitting',
        enabled: true,
        config: { chunks: 'all' }
      }
    ];

    return {
      tool: 'vite',
      version: '5.0.0',
      commands,
      hooks,
      optimizations
    };
  }

  private generateDeploymentConfig(generatedProject: GeneratedProject): DeploymentConfig {
    const scripts: DeploymentScript[] = [
      {
        name: 'deploy-netlify',
        command: 'npm run build && npx netlify deploy --prod',
        platform: 'netlify',
        description: 'Deploy to Netlify'
      },
      {
        name: 'deploy-vercel',
        command: 'npm run build && npx vercel --prod',
        platform: 'vercel',
        description: 'Deploy to Vercel'
      }
    ];

    const healthChecks: HealthCheck[] = [
      {
        name: 'main-page',
        url: '/',
        method: 'GET',
        expectedStatus: 200,
        timeout: 5000
      },
      {
        name: 'health-endpoint',
        url: '/health',
        method: 'GET',
        expectedStatus: 200,
        timeout: 3000
      }
    ];

    return {
      platform: ['netlify', 'vercel', 'aws-s3'],
      environment: {
        NODE_ENV: 'production',
        PUBLIC_URL: '/'
      },
      scripts,
      healthChecks
    };
  }

  private async calculateQualityMetrics(files: AssembledFile[]): Promise<QualityMetrics> {
    let codeComplexity = 0;
    let totalLinesOfCode = 0;
    let duplicatedLines = 0;

    files.forEach(file => {
      const lines = file.content.split('\n').length;
      totalLinesOfCode += lines;
      
      // 간단한 복잡도 계산 (실제로는 더 정교한 분석 필요)
      const complexity = this.calculateFileComplexity(file.content);
      codeComplexity += complexity;
    });

    const avgComplexity = files.length > 0 ? codeComplexity / files.length : 0;
    
    return {
      codeComplexity: Math.round(avgComplexity),
      maintainabilityIndex: Math.max(0, 100 - avgComplexity * 2),
      testCoverage: this.calculateTestCoverage(files),
      duplicatedCode: Math.round((duplicatedLines / totalLinesOfCode) * 100),
      technicalDebt: this.calculateTechnicalDebt(files),
      securityScore: this.calculateSecurityScore(files),
      performanceScore: 85, // 기본값
      accessibilityScore: 80 // 기본값
    };
  }

  private calculateFileComplexity(content: string): number {
    // 간단한 순환 복잡도 계산
    let complexity = 1; // 기본 복잡도
    
    // 조건문, 루프, 함수 등의 수를 세어 복잡도 증가
    const patterns = [
      /\bif\b/g,
      /\belse\b/g,
      /\bfor\b/g,
      /\bwhile\b/g,
      /\bswitch\b/g,
      /\bcase\b/g,
      /\bcatch\b/g,
      /\b&&\b/g,
      /\b\|\|\b/g
    ];

    patterns.forEach(pattern => {
      const matches = content.match(pattern);
      if (matches) {
        complexity += matches.length;
      }
    });

    return complexity;
  }

  private calculateTestCoverage(files: AssembledFile[]): number {
    const testFiles = files.filter(f => 
      f.path.includes('.test.') || 
      f.path.includes('.spec.') || 
      f.path.includes('__tests__')
    );
    
    const sourceFiles = files.filter(f => 
      (f.path.includes('.tsx') || f.path.includes('.ts')) && 
      !f.path.includes('.test.') && 
      !f.path.includes('.spec.')
    );

    if (sourceFiles.length === 0) return 0;
    
    // 간단한 계산: 테스트 파일 수 / 소스 파일 수 * 100
    return Math.min(100, Math.round((testFiles.length / sourceFiles.length) * 100));
  }

  private calculateTechnicalDebt(files: AssembledFile[]): number {
    let debtScore = 0;
    
    files.forEach(file => {
      // TODO 주석 개수
      const todoMatches = file.content.match(/TODO|FIXME|HACK/gi);
      if (todoMatches) {
        debtScore += todoMatches.length;
      }
      
      // 긴 함수 (50줄 이상)
      const functionMatches = file.content.match(/function\s+\w+[^}]*{[^}]{50,}}/g);
      if (functionMatches) {
        debtScore += functionMatches.length * 2;
      }
    });

    return debtScore;
  }

  private calculateSecurityScore(files: AssembledFile[]): number {
    let securityIssues = 0;
    
    files.forEach(file => {
      // 보안 문제 패턴들
      const securityPatterns = [
        /eval\s*\(/g,
        /innerHTML\s*=/g,
        /document\.write/g,
        /localStorage\.setItem.*password/gi,
        /sessionStorage\.setItem.*password/gi
      ];
      
      securityPatterns.forEach(pattern => {
        const matches = file.content.match(pattern);
        if (matches) {
          securityIssues += matches.length;
        }
      });
    });

    return Math.max(0, 100 - securityIssues * 10);
  }

  private getFileIcon(filename: string): string {
    const ext = filename.split('.').pop()?.toLowerCase();
    
    switch (ext) {
      case 'tsx': case 'jsx': return '⚛️';
      case 'ts': case 'js': return '📜';
      case 'css': case 'scss': return '🎨';
      case 'json': return '📋';
      case 'md': return '📖';
      case 'html': return '🌐';
      default: return '📄';
    }
  }

  private getFileExtension(path: string): string {
    return path.split('.').pop() || '';
  }

  private initializeValidators(): Map<string, Function> {
    const validators = new Map<string, Function>();

    // TypeScript/JavaScript 검증기
    validators.set('tsx', this.validateTSX.bind(this));
    validators.set('ts', this.validateTS.bind(this));
    validators.set('jsx', this.validateJSX.bind(this));
    validators.set('js', this.validateJS.bind(this));
    validators.set('json', this.validateJSON.bind(this));
    validators.set('css', this.validateCSS.bind(this));

    return validators;
  }

  private async validateTSX(content: string): Promise<boolean> {
    // 기본적인 TSX 구문 검증
    try {
      // JSX 태그가 올바르게 열리고 닫히는지 확인
      const openTags = content.match(/<\w+[^>]*>/g) || [];
      const closeTags = content.match(/<\/\w+>/g) || [];
      const selfClosingTags = content.match(/<\w+[^>]*\/>/g) || [];
      
      // 간단한 검증: 여는 태그와 닫는 태그 + 자체 닫힘 태그의 수가 맞는지
      return openTags.length >= closeTags.length;
    } catch (error) {
      return false;
    }
  }

  private async validateTS(content: string): Promise<boolean> {
    // TypeScript 기본 구문 검증
    try {
      // 괄호 균형 확인
      const openBraces = (content.match(/{/g) || []).length;
      const closeBraces = (content.match(/}/g) || []).length;
      return openBraces === closeBraces;
    } catch (error) {
      return false;
    }
  }

  private async validateJSX(content: string): Promise<boolean> {
    return this.validateTSX(content);
  }

  private async validateJS(content: string): Promise<boolean> {
    return this.validateTS(content);
  }

  private async validateJSON(content: string): Promise<boolean> {
    try {
      JSON.parse(content);
      return true;
    } catch (error) {
      return false;
    }
  }

  private async validateCSS(content: string): Promise<boolean> {
    // CSS 기본 구문 검증
    try {
      const openBraces = (content.match(/{/g) || []).length;
      const closeBraces = (content.match(/}/g) || []).length;
      return openBraces === closeBraces;
    } catch (error) {
      return false;
    }
  }
}