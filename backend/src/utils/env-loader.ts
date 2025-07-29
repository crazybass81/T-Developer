import { EnvCrypto } from './crypto';
import fs from 'fs/promises';
import path from 'path';

export class SecureEnvLoader {
  private crypto = new EnvCrypto();
  
  async loadEnvironment(): Promise<void> {
    const envPath = path.join(process.cwd(), '.env');
    const encryptedPath = path.join(process.cwd(), '.env.encrypted');
    
    try {
      // 프로덕션에서는 암호화된 파일 사용
      if (process.env.NODE_ENV === 'production' && await this.fileExists(encryptedPath)) {
        await this.loadEncryptedEnv(encryptedPath);
      } else if (await this.fileExists(envPath)) {
        // 개발 환경에서는 일반 .env 파일 사용
        await this.loadPlainEnv(envPath);
      }
    } catch (error) {
      console.warn('⚠️  환경 변수 로드 실패:', error);
    }
  }
  
  private async loadEncryptedEnv(filePath: string): Promise<void> {
    const content = await fs.readFile(filePath, 'utf8');
    const lines = content.split('\n');
    
    for (const line of lines) {
      if (line.includes('=') && !line.startsWith('#')) {
        const [key, value] = line.split('=', 2);
        
        if (value.startsWith('ENC:')) {
          const decrypted = await this.crypto.decrypt(value.substring(4));
          process.env[key] = decrypted;
        } else {
          process.env[key] = value;
        }
      }
    }
  }
  
  private async loadPlainEnv(filePath: string): Promise<void> {
    const content = await fs.readFile(filePath, 'utf8');
    const lines = content.split('\n');
    
    for (const line of lines) {
      if (line.includes('=') && !line.startsWith('#')) {
        const [key, value] = line.split('=', 2);
        process.env[key] = value;
      }
    }
  }
  
  private async fileExists(filePath: string): Promise<boolean> {
    try {
      await fs.access(filePath);
      return true;
    } catch {
      return false;
    }
  }
}