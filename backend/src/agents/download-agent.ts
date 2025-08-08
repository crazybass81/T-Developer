/**
 * Download Agent - 최종 프로젝트 패키징 및 다운로드 준비
 * Assembly Agent의 결과를 받아 다운로드 가능한 형태로 패키징
 */

import { AssembledProject, AssembledFile } from './assembly-agent';
import { createWriteStream, promises as fs } from 'fs';
import * as path from 'path';
import archiver from 'archiver';

export interface DownloadPackage {
  projectName: string;
  version: string;
  format: 'zip' | 'tar' | 'tar.gz';
  packagePath: string;
  size: number;
  checksum: string;
  downloadUrl: string;
  expiresAt: Date;
  metadata: PackageMetadata;
  instructions: InstallationInstructions;
}

export interface PackageMetadata {
  generatedAt: Date;
  generator: string;
  framework: string;
  totalFiles: number;
  estimatedInstallTime: string;
  requiredNodeVersion: string;
  additionalNotes: string[];
}

export interface InstallationInstructions {
  steps: InstallationStep[];
  prerequisites: string[];
  troubleshooting: TroubleshootingItem[];
  supportedPlatforms: string[];
}

export interface InstallationStep {
  step: number;
  title: string;
  command?: string;
  description: string;
  expected: string;
  troubleshoot?: string;
}

export interface TroubleshootingItem {
  problem: string;
  solution: string;
  commonCause: string;
}

export interface PackageOptions {
  format: 'zip' | 'tar' | 'tar.gz';
  includeNodeModules: boolean;
  includeDotFiles: boolean;
  compression: 'none' | 'fast' | 'balanced' | 'best';
  excludePatterns: string[];
}

export class DownloadAgent {
  private name = 'Download Agent';
  private tempDir: string;
  private outputDir: string;

  constructor() {
    this.tempDir = path.join(process.cwd(), 'temp');
    this.outputDir = path.join(process.cwd(), 'downloads');
  }

  /**
   * 조립된 프로젝트를 다운로드 패키지로 변환
   */
  async createDownloadPackage(
    assembledProject: AssembledProject,
    options: PackageOptions = this.getDefaultOptions()
  ): Promise<DownloadPackage> {
    console.log(`[${this.name}] Creating download package for ${assembledProject.projectName}`);

    // 1. 임시 디렉토리 준비
    const tempProjectDir = await this.prepareTempDirectory(assembledProject.projectName);

    // 2. 프로젝트 파일들을 임시 디렉토리에 생성
    await this.writeProjectFiles(assembledProject, tempProjectDir);

    // 3. 추가 파일들 생성 (설치 가이드, 메타데이터 등)
    await this.createAdditionalFiles(assembledProject, tempProjectDir);

    // 4. 패키지 압축
    const packagePath = await this.compressProject(
      assembledProject.projectName,
      tempProjectDir,
      options
    );

    // 5. 패키지 메타데이터 생성
    const metadata = this.createPackageMetadata(assembledProject);

    // 6. 설치 가이드 생성
    const instructions = this.createInstallationInstructions(assembledProject);

    // 7. 다운로드 URL 및 만료 시간 설정
    const downloadUrl = this.generateDownloadUrl(packagePath);
    const expiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000); // 24시간 후 만료

    // 8. 체크섬 계산
    const checksum = await this.calculateFileChecksum(packagePath);

    // 9. 파일 크기 계산
    const stats = await fs.stat(packagePath);

    // 10. 임시 디렉토리 정리
    await this.cleanupTempDirectory(tempProjectDir);

    const downloadPackage: DownloadPackage = {
      projectName: assembledProject.projectName,
      version: assembledProject.version,
      format: options.format,
      packagePath,
      size: stats.size,
      checksum,
      downloadUrl,
      expiresAt,
      metadata,
      instructions
    };

    console.log(`[${this.name}] Package created: ${path.basename(packagePath)} (${this.formatBytes(stats.size)})`);
    return downloadPackage;
  }

  private async prepareTempDirectory(projectName: string): Promise<string> {
    const tempProjectDir = path.join(this.tempDir, `${projectName}-${Date.now()}`);
    
    try {
      await fs.mkdir(tempProjectDir, { recursive: true });
      return tempProjectDir;
    } catch (error) {
      throw new Error(`Failed to create temp directory: ${error}`);
    }
  }

  private async writeProjectFiles(
    assembledProject: AssembledProject,
    tempDir: string
  ): Promise<void> {
    console.log(`[${this.name}] Writing ${assembledProject.files.length} project files`);

    for (const file of assembledProject.files) {
      await this.writeFile(file, tempDir);
    }

    // package.json 특별 처리
    const packageJsonPath = path.join(tempDir, 'package.json');
    const packageJsonContent = await this.generatePackageJson(assembledProject);
    await fs.writeFile(packageJsonPath, packageJsonContent, 'utf8');
  }

  private async writeFile(file: AssembledFile, baseDir: string): Promise<void> {
    const fullPath = path.join(baseDir, file.path);
    const dir = path.dirname(fullPath);

    // 디렉토리가 없으면 생성
    await fs.mkdir(dir, { recursive: true });

    // 파일 쓰기
    await fs.writeFile(fullPath, file.content, file.encoding);
  }

  private async generatePackageJson(assembledProject: AssembledProject): Promise<string> {
    const packageJson = {
      name: assembledProject.projectName.toLowerCase().replace(/\s+/g, '-'),
      version: assembledProject.version,
      description: `Generated by T-Developer - ${assembledProject.metadata.framework} application`,
      main: "src/main.tsx",
      scripts: this.createPackageScripts(assembledProject),
      dependencies: this.extractDependencies(assembledProject),
      devDependencies: this.extractDevDependencies(assembledProject),
      keywords: [
        "t-developer",
        "generated",
        assembledProject.metadata.framework || "react",
        "web-app"
      ],
      author: assembledProject.metadata.author || "T-Developer",
      license: assembledProject.metadata.license || "MIT",
      repository: assembledProject.metadata.repository,
      engines: {
        node: `>=${assembledProject.metadata.nodeVersion || '16.0.0'}`
      },
      browserslist: {
        production: [
          ">0.2%",
          "not dead",
          "not op_mini all"
        ],
        development: [
          "last 1 chrome version",
          "last 1 firefox version",
          "last 1 safari version"
        ]
      }
    };

    return JSON.stringify(packageJson, null, 2);
  }

  private createPackageScripts(assembledProject: AssembledProject): Record<string, string> {
    const scripts: Record<string, string> = {};

    assembledProject.buildSystem.commands.forEach(command => {
      // npm run을 제거하고 실제 명령어만 저장
      const actualCommand = command.command.replace(/^npm run /, '');
      
      switch (command.name) {
        case 'dev':
          scripts.dev = 'vite';
          break;
        case 'build':
          scripts.build = 'vite build';
          break;
        case 'test':
          scripts.test = 'vitest';
          break;
        case 'lint':
          scripts.lint = 'eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0';
          break;
        default:
          scripts[command.name] = actualCommand;
      }
    });

    // 추가 유용한 스크립트들
    scripts.preview = 'vite preview';
    scripts['type-check'] = 'tsc --noEmit';
    scripts.clean = 'rm -rf dist node_modules/.vite';

    return scripts;
  }

  private extractDependencies(assembledProject: AssembledProject): Record<string, string> {
    const deps: Record<string, string> = {};

    // 기본 의존성들
    if (assembledProject.metadata.framework === 'react') {
      deps.react = '^18.2.0';
      deps['react-dom'] = '^18.2.0';
    }

    // 프로젝트 파일들에서 사용된 의존성들 추출
    const usedDependencies = new Set<string>();
    assembledProject.files.forEach(file => {
      file.dependencies.forEach(dep => {
        if (!dep.startsWith('.') && !dep.startsWith('/')) {
          usedDependencies.add(dep);
        }
      });
    });

    // 버전 정보와 함께 의존성 추가
    usedDependencies.forEach(dep => {
      deps[dep] = this.getLatestVersion(dep);
    });

    return deps;
  }

  private extractDevDependencies(assembledProject: AssembledProject): Record<string, string> {
    const devDeps: Record<string, string> = {
      'typescript': '^5.2.2',
      'vite': '^5.0.8',
      '@vitejs/plugin-react': '^4.2.1',
      'eslint': '^8.55.0',
      'eslint-plugin-react-hooks': '^4.6.0',
      'eslint-plugin-react-refresh': '^0.4.5',
      '@typescript-eslint/eslint-plugin': '^6.14.0',
      '@typescript-eslint/parser': '^6.14.0',
      'vitest': '^1.1.0',
      '@testing-library/react': '^14.1.2',
      '@testing-library/jest-dom': '^6.1.6',
      '@types/react': '^18.2.43',
      '@types/react-dom': '^18.2.17'
    };

    return devDeps;
  }

  private getLatestVersion(packageName: string): string {
    // 실제로는 npm registry API를 호출해야 하지만, 여기서는 기본값 사용
    const knownVersions: Record<string, string> = {
      'axios': '^1.6.2',
      'lodash': '^4.17.21',
      'moment': '^2.29.4',
      'react-router-dom': '^6.20.1',
      '@reduxjs/toolkit': '^2.0.1',
      'react-redux': '^9.0.4',
      'zustand': '^4.4.7',
      'antd': '^5.12.8',
      '@mui/material': '^5.15.4',
      '@emotion/react': '^11.11.1',
      '@emotion/styled': '^11.11.0',
      '@chakra-ui/react': '^2.8.2'
    };

    return knownVersions[packageName] || '^1.0.0';
  }

  private async createAdditionalFiles(
    assembledProject: AssembledProject,
    tempDir: string
  ): Promise<void> {
    // README.md 생성 (기존에 없다면)
    const readmePath = path.join(tempDir, 'README.md');
    const readmeExists = await fs.access(readmePath).then(() => true).catch(() => false);
    
    if (!readmeExists) {
      const readme = await this.generateDetailedReadme(assembledProject);
      await fs.writeFile(readmePath, readme, 'utf8');
    }

    // INSTALLATION.md 생성
    const installationGuide = this.generateInstallationGuide(assembledProject);
    await fs.writeFile(path.join(tempDir, 'INSTALLATION.md'), installationGuide, 'utf8');

    // CHANGELOG.md 생성
    const changelog = this.generateChangelog(assembledProject);
    await fs.writeFile(path.join(tempDir, 'CHANGELOG.md'), changelog, 'utf8');

    // .env.example 파일 (없다면)
    const envExamplePath = path.join(tempDir, '.env.example');
    const envExists = await fs.access(envExamplePath).then(() => true).catch(() => false);
    
    if (!envExists) {
      const envExample = this.generateEnvExample(assembledProject);
      await fs.writeFile(envExamplePath, envExample, 'utf8');
    }

    // T-Developer 메타데이터 파일
    const metadata = {
      generatedBy: 'T-Developer',
      version: '1.0.0',
      generatedAt: new Date().toISOString(),
      project: {
        name: assembledProject.projectName,
        framework: assembledProject.metadata.framework,
        structure: assembledProject.structure,
        validation: assembledProject.validation,
        qualityMetrics: assembledProject.qualityMetrics
      }
    };
    await fs.writeFile(
      path.join(tempDir, '.t-developer.json'),
      JSON.stringify(metadata, null, 2),
      'utf8'
    );
  }

  private async generateDetailedReadme(assembledProject: AssembledProject): Promise<string> {
    const { projectName, metadata, qualityMetrics, buildSystem } = assembledProject;
    
    return `# ${projectName}

Generated with ❤️ by **T-Developer** - The AI-powered full-stack development assistant

## 🚀 Quick Start

\`\`\`bash
# Install dependencies
npm install

# Start development server
npm run dev

# Open your browser
# Your app will be running at http://localhost:5173
\`\`\`

## 📊 Project Quality

- **Code Quality Score**: ${qualityMetrics.maintainabilityIndex}/100
- **Test Coverage**: ${qualityMetrics.testCoverage}%
- **Security Score**: ${qualityMetrics.securityScore}/100
- **Performance Score**: ${qualityMetrics.performanceScore}/100

## 🛠 Tech Stack

- **Framework**: ${metadata.framework}
- **Build Tool**: ${metadata.buildTool}
- **Node Version**: ${metadata.nodeVersion}
- **License**: ${metadata.license}

## 📦 Available Scripts

${buildSystem.commands.map(cmd => 
  `- \`npm run ${cmd.name}\` - ${cmd.description}`
).join('\n')}

## 🏗 Project Structure

\`\`\`
${assembledProject.structure.tree}
\`\`\`

## 🧪 Testing

This project includes comprehensive testing setup:

\`\`\`bash
# Run tests
npm test

# Run tests with coverage
npm run test:coverage
\`\`\`

## 📈 Performance Optimization

The project includes several performance optimizations:

${buildSystem.optimizations.filter(opt => opt.enabled).map(opt => 
  `- **${opt.name}**: Enabled`
).join('\n')}

## 🚀 Deployment

### Recommended Platforms

${assembledProject.deploymentConfig.platform.map(platform => 
  `- [${platform}](https://www.${platform}.com)`
).join('\n')}

### Quick Deploy

${assembledProject.deploymentConfig.scripts.map(script => 
  `**${script.platform}**: \`${script.command}\``
).join('\n\n')}

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: \`git checkout -b feature/amazing-feature\`
3. Commit your changes: \`git commit -m 'Add amazing feature'\`
4. Push to the branch: \`git push origin feature/amazing-feature\`
5. Open a Pull Request

## 📄 License

This project is licensed under the ${metadata.license} License.

## 🙏 Acknowledgments

- Generated by [T-Developer](https://t-developer.ai)
- Built with modern web technologies
- Optimized for performance and scalability

---

**Need help?** Check out our [Installation Guide](./INSTALLATION.md) or [Troubleshooting Guide](./TROUBLESHOOTING.md)`;
  }

  private generateInstallationGuide(assembledProject: AssembledProject): string {
    return `# Installation Guide

## Prerequisites

- Node.js ${assembledProject.metadata.nodeVersion} or higher
- npm or yarn package manager
- Modern web browser

## Step-by-Step Installation

### 1. Extract the Project

\`\`\`bash
# Extract the downloaded package
unzip ${assembledProject.projectName}.zip
cd ${assembledProject.projectName}
\`\`\`

### 2. Install Dependencies

\`\`\`bash
# Using npm (recommended)
npm install

# Or using yarn
yarn install
\`\`\`

### 3. Environment Setup

\`\`\`bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
# Add your API keys and configuration
\`\`\`

### 4. Start Development Server

\`\`\`bash
# Start the development server
npm run dev

# Your app will be available at:
# http://localhost:5173
\`\`\`

### 5. Verify Installation

Open your browser and navigate to \`http://localhost:5173\`. You should see your application running.

## Troubleshooting

### Common Issues

**Node version error**
\`\`\`bash
# Check your Node version
node --version

# If version is too old, update Node.js
# Visit https://nodejs.org for the latest version
\`\`\`

**Port already in use**
\`\`\`bash
# Kill process using the port
npx kill-port 5173

# Or change the port in vite.config.ts
\`\`\`

**Module not found errors**
\`\`\`bash
# Clear npm cache and reinstall
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
\`\`\`

## Next Steps

1. **Customize**: Modify components in \`src/components/\`
2. **Style**: Update styles in \`src/styles/\`
3. **Test**: Run tests with \`npm test\`
4. **Build**: Create production build with \`npm run build\`
5. **Deploy**: Follow deployment guides for your platform

## Getting Help

- Check the main README.md for general information
- Visit our documentation at https://docs.t-developer.ai
- Join our community at https://discord.gg/t-developer`;
  }

  private generateChangelog(assembledProject: AssembledProject): string {
    return `# Changelog

All notable changes to this project will be documented in this file.

## [${assembledProject.version}] - ${new Date().toISOString().split('T')[0]}

### Added
- Initial project generation with T-Developer
- ${assembledProject.metadata.framework} application setup
- Component structure and basic styling
- Build system configuration
- Testing framework setup
- Development and production scripts

### Generated Components
${assembledProject.files
  .filter(f => f.type === 'component')
  .map(f => `- ${path.basename(f.path, path.extname(f.path))}`)
  .join('\n')}

### Build System
- Build Tool: ${assembledProject.metadata.buildTool}
- Optimizations: ${assembledProject.buildSystem.optimizations.filter(o => o.enabled).map(o => o.name).join(', ')}

### Quality Metrics
- Code Quality: ${assembledProject.qualityMetrics.maintainabilityIndex}/100
- Test Coverage: ${assembledProject.qualityMetrics.testCoverage}%
- Security Score: ${assembledProject.qualityMetrics.securityScore}/100

---

## How to Update

When making changes to your project:

1. Update the version in \`package.json\`
2. Document changes in this file
3. Create a git tag: \`git tag v1.0.1\`
4. Push changes: \`git push --tags\`

## Version Schema

This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)`;
  }

  private generateEnvExample(assembledProject: AssembledProject): string {
    return `# Environment Variables Template
# Copy this file to .env and fill in your values

# Application Settings
VITE_APP_NAME="${assembledProject.projectName}"
VITE_APP_VERSION="${assembledProject.version}"

# API Configuration
# VITE_API_BASE_URL=http://localhost:3000/api
# VITE_API_TIMEOUT=10000

# Authentication (if using auth)
# VITE_AUTH_DOMAIN=your-auth-domain
# VITE_AUTH_CLIENT_ID=your-client-id

# Third-party Services
# VITE_GOOGLE_MAPS_API_KEY=your-google-maps-key
# VITE_STRIPE_PUBLIC_KEY=your-stripe-public-key

# Development Settings
VITE_DEBUG=true
VITE_LOG_LEVEL=info

# Analytics (if using)
# VITE_GOOGLE_ANALYTICS_ID=GA-XXXXXXXXX
# VITE_MIXPANEL_TOKEN=your-mixpanel-token

# Feature Flags
VITE_ENABLE_PWA=false
VITE_ENABLE_OFFLINE=false

# Security
# Don't commit sensitive values to git
# Add .env to your .gitignore file`;
  }

  private async compressProject(
    projectName: string,
    sourceDir: string,
    options: PackageOptions
  ): Promise<string> {
    // 출력 디렉토리 확인/생성
    await fs.mkdir(this.outputDir, { recursive: true });

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T')[0];
    const fileName = `${projectName}-${timestamp}.${options.format}`;
    const outputPath = path.join(this.outputDir, fileName);

    if (options.format === 'zip') {
      return this.createZipPackage(sourceDir, outputPath, options);
    } else {
      return this.createTarPackage(sourceDir, outputPath, options);
    }
  }

  private async createZipPackage(
    sourceDir: string,
    outputPath: string,
    options: PackageOptions
  ): Promise<string> {
    return new Promise((resolve, reject) => {
      const output = createWriteStream(outputPath);
      const archive = archiver('zip', {
        zlib: { level: this.getCompressionLevel(options.compression) }
      });

      output.on('close', () => {
        resolve(outputPath);
      });

      archive.on('error', (err: any) => {
        reject(err);
      });

      archive.pipe(output);

      // 패키지에 포함할 파일들 추가
      archive.directory(sourceDir, false);

      archive.finalize();
    });
  }

  private async createTarPackage(
    sourceDir: string,
    outputPath: string,
    options: PackageOptions
  ): Promise<string> {
    // 실제 구현에서는 tar 라이브러리 사용
    throw new Error('Tar packaging not implemented yet');
  }

  private getCompressionLevel(compression: string): number {
    switch (compression) {
      case 'none': return 0;
      case 'fast': return 1;
      case 'balanced': return 6;
      case 'best': return 9;
      default: return 6;
    }
  }

  private async calculateFileChecksum(filePath: string): Promise<string> {
    try {
      const crypto = await import('crypto');
      const fileBuffer = await fs.readFile(filePath);
      const hashSum = crypto.createHash('sha256');
      hashSum.update(fileBuffer);
      return hashSum.digest('hex');
    } catch (error) {
      return 'checksum-unavailable';
    }
  }

  private generateDownloadUrl(packagePath: string): string {
    const fileName = path.basename(packagePath);
    return `/api/v1/download/${fileName}`;
  }

  private createPackageMetadata(assembledProject: AssembledProject): PackageMetadata {
    return {
      generatedAt: new Date(),
      generator: 'T-Developer',
      framework: assembledProject.metadata.framework || 'react',
      totalFiles: assembledProject.files.length,
      estimatedInstallTime: this.estimateInstallTime(assembledProject),
      requiredNodeVersion: assembledProject.metadata.nodeVersion || '16.0.0',
      additionalNotes: [
        'Generated project is production-ready',
        'Includes comprehensive testing setup',
        'Optimized for modern browsers',
        'Follows industry best practices'
      ]
    };
  }

  private estimateInstallTime(assembledProject: AssembledProject): string {
    const totalFiles = assembledProject.files.length;
    
    if (totalFiles < 20) return '2-3 minutes';
    if (totalFiles < 50) return '3-5 minutes';
    if (totalFiles < 100) return '5-8 minutes';
    return '8-12 minutes';
  }

  private createInstallationInstructions(assembledProject: AssembledProject): InstallationInstructions {
    const steps: InstallationStep[] = [
      {
        step: 1,
        title: 'Extract Package',
        command: `unzip ${assembledProject.projectName}.zip`,
        description: 'Extract the downloaded package to your desired location',
        expected: 'Project files extracted successfully'
      },
      {
        step: 2,
        title: 'Navigate to Project',
        command: `cd ${assembledProject.projectName}`,
        description: 'Change to the project directory',
        expected: 'You are now in the project directory'
      },
      {
        step: 3,
        title: 'Install Dependencies',
        command: 'npm install',
        description: 'Install all required dependencies',
        expected: 'Dependencies installed without errors',
        troubleshoot: 'If you see permission errors, try using sudo or check your Node.js installation'
      },
      {
        step: 4,
        title: 'Start Development Server',
        command: 'npm run dev',
        description: 'Start the development server',
        expected: 'Server running on http://localhost:5173',
        troubleshoot: 'If port 5173 is busy, the server will automatically use the next available port'
      },
      {
        step: 5,
        title: 'Open in Browser',
        description: 'Navigate to the URL shown in terminal',
        expected: 'Your application loads successfully'
      }
    ];

    const prerequisites = [
      `Node.js ${assembledProject.metadata.nodeVersion} or higher`,
      'npm (comes with Node.js) or yarn',
      'Modern web browser (Chrome, Firefox, Safari, Edge)',
      'Text editor or IDE (VS Code recommended)'
    ];

    const troubleshooting: TroubleshootingItem[] = [
      {
        problem: 'npm install fails with permission errors',
        solution: 'Use a Node version manager like nvm, or fix npm permissions',
        commonCause: 'Global npm packages installed with sudo'
      },
      {
        problem: 'Development server fails to start',
        solution: 'Check if port is already in use, or restart your terminal',
        commonCause: 'Another development server is running on the same port'
      },
      {
        problem: 'Browser shows blank page',
        solution: 'Check browser console for errors, ensure all dependencies installed',
        commonCause: 'JavaScript errors or missing dependencies'
      },
      {
        problem: 'Build command fails',
        solution: 'Clear node_modules and reinstall: rm -rf node_modules && npm install',
        commonCause: 'Corrupted node_modules or version conflicts'
      }
    ];

    return {
      steps,
      prerequisites,
      troubleshooting,
      supportedPlatforms: ['Windows 10+', 'macOS 10.15+', 'Linux (Ubuntu 18.04+)']
    };
  }

  private async cleanupTempDirectory(tempDir: string): Promise<void> {
    try {
      await fs.rm(tempDir, { recursive: true, force: true });
    } catch (error) {
      console.warn(`[${this.name}] Failed to cleanup temp directory: ${error}`);
    }
  }

  private formatBytes(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  private getDefaultOptions(): PackageOptions {
    return {
      format: 'zip',
      includeNodeModules: false,
      includeDotFiles: true,
      compression: 'balanced',
      excludePatterns: [
        'node_modules',
        '.git',
        'dist',
        '.DS_Store',
        'Thumbs.db'
      ]
    };
  }

  /**
   * 다운로드 패키지 정리 (만료된 파일들 삭제)
   */
  async cleanupExpiredPackages(): Promise<void> {
    try {
      const files = await fs.readdir(this.outputDir);
      const now = new Date();

      for (const file of files) {
        const filePath = path.join(this.outputDir, file);
        const stats = await fs.stat(filePath);
        const ageInHours = (now.getTime() - stats.mtime.getTime()) / (1000 * 60 * 60);

        // 24시간 이상 된 파일들 삭제
        if (ageInHours > 24) {
          await fs.rm(filePath);
          console.log(`[${this.name}] Cleaned up expired package: ${file}`);
        }
      }
    } catch (error) {
      console.warn(`[${this.name}] Cleanup failed: ${error}`);
    }
  }

  /**
   * 특정 패키지 삭제
   */
  async deletePackage(packagePath: string): Promise<boolean> {
    try {
      await fs.rm(packagePath);
      return true;
    } catch (error) {
      console.error(`[${this.name}] Failed to delete package: ${error}`);
      return false;
    }
  }
}