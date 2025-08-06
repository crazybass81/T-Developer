import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';

interface SecurityScanResult {
  vulnerabilities: {
    high: number;
    medium: number;
    low: number;
  };
  details: Array<{
    type: string;
    severity: string;
    description: string;
    file?: string;
    line?: number;
  }>;
}

export class SecurityScanner {
  async scanProject(projectPath: string): Promise<SecurityScanResult> {
    const result: SecurityScanResult = {
      vulnerabilities: { high: 0, medium: 0, low: 0 },
      details: []
    };

    // 1. npm audit 실행
    await this.runNpmAudit(projectPath, result);
    
    // 2. 하드코딩된 시크릿 검사
    await this.scanForSecrets(projectPath, result);
    
    // 3. 취약한 패턴 검사
    await this.scanForVulnerablePatterns(projectPath, result);

    return result;
  }

  private async runNpmAudit(projectPath: string, result: SecurityScanResult): Promise<void> {
    try {
      const auditOutput = execSync('npm audit --json', { 
        cwd: path.join(projectPath, 'backend'),
        encoding: 'utf8'
      });
      
      const audit = JSON.parse(auditOutput);
      if (audit.metadata?.vulnerabilities) {
        result.vulnerabilities.high += audit.metadata.vulnerabilities.high || 0;
        result.vulnerabilities.medium += audit.metadata.vulnerabilities.moderate || 0;
        result.vulnerabilities.low += audit.metadata.vulnerabilities.low || 0;
      }
    } catch (error) {
      // npm audit 실패는 무시 (의존성 문제일 수 있음)
    }
  }

  private async scanForSecrets(projectPath: string, result: SecurityScanResult): Promise<void> {
    const secretPatterns = [
      { pattern: /sk_[a-zA-Z0-9]{32,}/, type: 'API Key' },
      { pattern: /AKIA[0-9A-Z]{16}/, type: 'AWS Access Key' },
      { pattern: /password\s*=\s*["'][^"']+["']/i, type: 'Hardcoded Password' }
    ];

    const scanDir = (dir: string) => {
      const files = fs.readdirSync(dir);
      
      for (const file of files) {
        const filePath = path.join(dir, file);
        const stat = fs.statSync(filePath);
        
        if (stat.isDirectory() && !file.startsWith('.') && file !== 'node_modules') {
          scanDir(filePath);
        } else if (stat.isFile() && (file.endsWith('.ts') || file.endsWith('.js'))) {
          const content = fs.readFileSync(filePath, 'utf8');
          
          for (const { pattern, type } of secretPatterns) {
            if (pattern.test(content)) {
              result.vulnerabilities.high++;
              result.details.push({
                type: 'Secret Exposure',
                severity: 'high',
                description: `Potential ${type} found in code`,
                file: filePath
              });
            }
          }
        }
      }
    };

    scanDir(projectPath);
  }

  private async scanForVulnerablePatterns(projectPath: string, result: SecurityScanResult): Promise<void> {
    const vulnerablePatterns = [
      { pattern: /eval\s*\(/, type: 'Code Injection', severity: 'high' },
      { pattern: /innerHTML\s*=/, type: 'XSS Risk', severity: 'medium' },
      { pattern: /document\.write\s*\(/, type: 'XSS Risk', severity: 'medium' }
    ];

    const scanDir = (dir: string) => {
      const files = fs.readdirSync(dir);
      
      for (const file of files) {
        const filePath = path.join(dir, file);
        const stat = fs.statSync(filePath);
        
        if (stat.isDirectory() && !file.startsWith('.') && file !== 'node_modules') {
          scanDir(filePath);
        } else if (stat.isFile() && (file.endsWith('.ts') || file.endsWith('.js'))) {
          const content = fs.readFileSync(filePath, 'utf8');
          const lines = content.split('\n');
          
          for (const { pattern, type, severity } of vulnerablePatterns) {
            lines.forEach((line, index) => {
              if (pattern.test(line)) {
                result.vulnerabilities[severity as keyof typeof result.vulnerabilities]++;
                result.details.push({
                  type,
                  severity,
                  description: `Vulnerable pattern detected: ${type}`,
                  file: filePath,
                  line: index + 1
                });
              }
            });
          }
        }
      }
    };

    scanDir(projectPath);
  }

  generateReport(result: SecurityScanResult): string {
    const total = result.vulnerabilities.high + result.vulnerabilities.medium + result.vulnerabilities.low;
    
    let report = `Security Scan Report\n`;
    report += `===================\n\n`;
    report += `Total Vulnerabilities: ${total}\n`;
    report += `- High: ${result.vulnerabilities.high}\n`;
    report += `- Medium: ${result.vulnerabilities.medium}\n`;
    report += `- Low: ${result.vulnerabilities.low}\n\n`;
    
    if (result.details.length > 0) {
      report += `Details:\n`;
      report += `--------\n`;
      
      result.details.forEach((detail, index) => {
        report += `${index + 1}. [${detail.severity.toUpperCase()}] ${detail.type}\n`;
        report += `   ${detail.description}\n`;
        if (detail.file) {
          report += `   File: ${detail.file}`;
          if (detail.line) {
            report += `:${detail.line}`;
          }
          report += `\n`;
        }
        report += `\n`;
      });
    }
    
    return report;
  }
}