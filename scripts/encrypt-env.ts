#!/usr/bin/env ts-node

import { EnvCrypto } from '../backend/src/utils/crypto';
import fs from 'fs/promises';
import path from 'path';

async function encryptEnvFile(): Promise<void> {
  const crypto = new EnvCrypto();
  const envPath = path.join(process.cwd(), '.env');
  const encryptedPath = path.join(process.cwd(), '.env.encrypted');
  
  try {
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
  } catch (error) {
    console.error('❌ 암호화 실패:', error);
  }
}

if (require.main === module) {
  encryptEnvFile();
}