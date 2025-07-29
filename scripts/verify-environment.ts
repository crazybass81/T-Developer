import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs/promises';
import chalk from 'chalk';

const execAsync = promisify(exec);

interface VerificationResult {
  component: string;
  status: 'pass' | 'fail' | 'warning';
  message: string;
  details?: any;
}

class EnvironmentVerifier {
  private results: VerificationResult[] = [];
  
  async verify(): Promise<void> {
    console.log(chalk.blue('🔍 T-Developer 환경 검증 시작...\n'));
    
    await this.verifyNodeEnvironment();
    await this.verifyProjectStructure();
    await this.verifyDevelopmentTools();
    await this.verifySecuritySettings();
    
    this.printResults();
  }
  
  private async verifyNodeEnvironment(): Promise<void> {
    try {
      const { stdout: nodeVersion } = await execAsync('node --version');
      const { stdout: npmVersion } = await execAsync('npm --version');
      
      const nodeMatch = nodeVersion.match(/v(\d+)\.(\d+)/);
      if (nodeMatch) {
        const majorVersion = parseInt(nodeMatch[1]);
        if (majorVersion >= 18) {
          this.addResult('Node.js', 'pass', `버전 ${nodeVersion.trim()} 확인`);
        } else {
          this.addResult('Node.js', 'fail', `버전 18 이상 필요 (현재: ${nodeVersion.trim()})`);
        }
      }
      
      this.addResult('npm', 'pass', `버전 ${npmVersion.trim()} 확인`);
      
      const packageJson = JSON.parse(await fs.readFile('package.json', 'utf-8'));
      const requiredPackages = [
        '@aws-sdk/client-bedrock-runtime',
        '@aws-sdk/client-dynamodb',
        'express',
        'typescript',
        'jest'
      ];
      
      const missingPackages = requiredPackages.filter(
        pkg => !packageJson.dependencies?.[pkg] && !packageJson.devDependencies?.[pkg]
      );
      
      if (missingPackages.length === 0) {
        this.addResult('필수 패키지', 'pass', '모든 필수 패키지 설치됨');
      } else {
        this.addResult('필수 패키지', 'fail', `누락된 패키지: ${missingPackages.join(', ')}`);
      }
      
    } catch (error) {
      this.addResult('Node.js 환경', 'fail', '확인 실패', error);
    }
  }
  
  private async verifyProjectStructure(): Promise<void> {
    const requiredDirs = [
      'backend',
      'scripts',
      'docs',
      '.husky'
    ];
    
    for (const dir of requiredDirs) {
      try {
        await fs.access(dir);
        this.addResult(`디렉토리: ${dir}`, 'pass', '존재함');
      } catch {
        this.addResult(`디렉토리: ${dir}`, 'fail', '존재하지 않음');
      }
    }
    
    const requiredFiles = [
      'package.json',
      'tsconfig.json',
      '.gitignore',
      'commitlint.config.js'
    ];
    
    for (const file of requiredFiles) {
      try {
        await fs.access(file);
        this.addResult(`파일: ${file}`, 'pass', '존재함');
      } catch {
        this.addResult(`파일: ${file}`, 'fail', '존재하지 않음');
      }
    }
  }
  
  private async verifyDevelopmentTools(): Promise<void> {
    const tools = [
      { cmd: 'git --version', name: 'Git' },
      { cmd: 'docker --version', name: 'Docker', optional: true }
    ];
    
    for (const tool of tools) {
      try {
        const { stdout } = await execAsync(tool.cmd);
        this.addResult(tool.name, 'pass', stdout.trim().split('\n')[0]);
      } catch {
        if (tool.optional) {
          this.addResult(tool.name, 'warning', '설치되지 않음 (선택사항)');
        } else {
          this.addResult(tool.name, 'fail', '설치되지 않음');
        }
      }
    }
  }
  
  private async verifySecuritySettings(): Promise<void> {
    try {
      const stats = await fs.stat('.env.example');
      this.addResult('.env.example', 'pass', '환경 변수 템플릿 존재');
    } catch {
      this.addResult('.env.example', 'fail', '.env.example 파일이 없습니다');
    }
    
    try {
      await fs.access('.gitignore');
      const gitignore = await fs.readFile('.gitignore', 'utf-8');
      if (gitignore.includes('.env') && gitignore.includes('node_modules')) {
        this.addResult('.gitignore', 'pass', '적절한 파일들이 무시됨');
      } else {
        this.addResult('.gitignore', 'warning', '일부 중요 파일이 누락될 수 있음');
      }
    } catch {
      this.addResult('.gitignore', 'fail', '.gitignore 파일이 없습니다');
    }
  }
  
  private addResult(component: string, status: VerificationResult['status'], message: string, details?: any): void {
    this.results.push({ component, status, message, details });
  }
  
  private printResults(): void {
    console.log('\n' + chalk.blue('='.repeat(60)));
    console.log(chalk.blue.bold('검증 결과 요약'));
    console.log(chalk.blue('='.repeat(60)) + '\n');
    
    const statusIcons = {
      pass: chalk.green('✅'),
      fail: chalk.red('❌'),
      warning: chalk.yellow('⚠️')
    };
    
    const maxComponentLength = Math.max(...this.results.map(r => r.component.length));
    
    for (const result of this.results) {
      const icon = statusIcons[result.status];
      const component = result.component.padEnd(maxComponentLength + 2);
      const statusColor = result.status === 'pass' ? chalk.green :
                         result.status === 'fail' ? chalk.red : chalk.yellow;
      
      console.log(`${icon} ${chalk.white(component)} ${statusColor(result.message)}`);
    }
    
    const stats = {
      pass: this.results.filter(r => r.status === 'pass').length,
      fail: this.results.filter(r => r.status === 'fail').length,
      warning: this.results.filter(r => r.status === 'warning').length
    };
    
    console.log('\n' + chalk.blue('-'.repeat(60)));
    console.log(chalk.white('통계:'), 
      chalk.green(`성공: ${stats.pass}`),
      chalk.red(`실패: ${stats.fail}`),
      chalk.yellow(`경고: ${stats.warning}`)
    );
    
    if (stats.fail > 0) {
      console.log('\n' + chalk.red.bold('⚠️  일부 검증이 실패했습니다. 위의 실패 항목을 확인하세요.'));
      process.exit(1);
    } else if (stats.warning > 0) {
      console.log('\n' + chalk.yellow.bold('ℹ️  일부 경고가 있지만 개발을 시작할 수 있습니다.'));
    } else {
      console.log('\n' + chalk.green.bold('🎉 모든 검증을 통과했습니다! 개발 환경이 준비되었습니다.'));
    }
  }
}

if (require.main === module) {
  const verifier = new EnvironmentVerifier();
  verifier.verify().catch(console.error);
}

export { EnvironmentVerifier };