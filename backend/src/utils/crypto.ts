import crypto from 'crypto';
import fs from 'fs/promises';
import path from 'path';

export class EnvCrypto {
  private algorithm = 'aes-256-gcm';
  private keyPath = path.join(process.cwd(), '.env.key');
  
  async generateKey(): Promise<string> {
    const key = crypto.randomBytes(32).toString('hex');
    await fs.writeFile(this.keyPath, key, { mode: 0o600 });
    console.log('✅ 암호화 키가 생성되었습니다: .env.key');
    console.log('⚠️  이 파일을 안전하게 보관하고 절대 커밋하지 마세요!');
    return key;
  }
  
  async encrypt(text: string): Promise<string> {
    const key = await this.getKey();
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipheriv(this.algorithm, Buffer.from(key, 'hex'), iv) as crypto.CipherGCM;
    
    let encrypted = cipher.update(text, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    
    const authTag = cipher.getAuthTag();
    
    return iv.toString('hex') + ':' + authTag.toString('hex') + ':' + encrypted;
  }
  
  async decrypt(encryptedText: string): Promise<string> {
    const key = await this.getKey();
    const parts = encryptedText.split(':');
    const iv = Buffer.from(parts[0], 'hex');
    const authTag = Buffer.from(parts[1], 'hex');
    const encrypted = parts[2];
    
    const decipher = crypto.createDecipheriv(this.algorithm, Buffer.from(key, 'hex'), iv) as crypto.DecipherGCM;
    decipher.setAuthTag(authTag);
    
    let decrypted = decipher.update(encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    
    return decrypted;
  }
  
  private async getKey(): Promise<string> {
    try {
      return await fs.readFile(this.keyPath, 'utf8');
    } catch (error) {
      throw new Error('암호화 키를 찾을 수 없습니다. generateKey()를 먼저 실행하세요.');
    }
  }
}

// 환경 변수 암호화 스크립트
export async function encryptEnvFile(): Promise<void> {
  const crypto = new EnvCrypto();
  const envPath = path.join(process.cwd(), '.env');
  const encryptedPath = path.join(process.cwd(), '.env.encrypted');
  
  const envContent = await fs.readFile(envPath, 'utf8');
  const lines = envContent.split('\n');
  
  const encryptedLines = await Promise.all(lines.map(async (line) => {
    if (line.includes('=') && !line.startsWith('#')) {
      const [key, value] = line.split('=', 2);
      if (key.includes('SECRET') || key.includes('KEY') || key.includes('PASSWORD')) {
        const encrypted = await crypto.encrypt(value);
        return `${key}=ENC:${encrypted}`;
      }
    }
    return line;
  }));
  
  await fs.writeFile(encryptedPath, encryptedLines.join('\n'));
  console.log('✅ 환경 변수가 암호화되었습니다: .env.encrypted');
}