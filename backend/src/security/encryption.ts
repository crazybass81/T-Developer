import crypto from 'crypto';
import { Request, Response, NextFunction } from 'express';

const ENCRYPTION_ALGORITHM = 'aes-256-gcm';
const IV_LENGTH = 16;
const TAG_LENGTH = 16;
const SALT_LENGTH = 32;
const KEY_LENGTH = 32;
const ITERATIONS = 100000;

export class EncryptionService {
  // 필드 레벨 암호화 (간단한 버전)
  encryptField(plaintext: string, password: string = process.env.ENCRYPTION_KEY || 'default-key'): string {
    const salt = crypto.randomBytes(SALT_LENGTH);
    const key = crypto.pbkdf2Sync(password, salt, ITERATIONS, KEY_LENGTH, 'sha256');
    const iv = crypto.randomBytes(IV_LENGTH);
    
    const cipher = crypto.createCipheriv(ENCRYPTION_ALGORITHM, key, iv);
    const encrypted = Buffer.concat([
      cipher.update(plaintext, 'utf8'),
      cipher.final()
    ]);
    
    const tag = cipher.getAuthTag();
    const combined = Buffer.concat([salt, iv, tag, encrypted]);
    
    return combined.toString('base64');
  }
  
  // 필드 복호화
  decryptField(encryptedData: string, password: string = process.env.ENCRYPTION_KEY || 'default-key'): string {
    const combined = Buffer.from(encryptedData, 'base64');
    
    const salt = combined.slice(0, SALT_LENGTH);
    const iv = combined.slice(SALT_LENGTH, SALT_LENGTH + IV_LENGTH);
    const tag = combined.slice(SALT_LENGTH + IV_LENGTH, SALT_LENGTH + IV_LENGTH + TAG_LENGTH);
    const encrypted = combined.slice(SALT_LENGTH + IV_LENGTH + TAG_LENGTH);
    
    const key = crypto.pbkdf2Sync(password, salt, ITERATIONS, KEY_LENGTH, 'sha256');
    
    const decipher = crypto.createDecipheriv(ENCRYPTION_ALGORITHM, key, iv);
    decipher.setAuthTag(tag);
    
    const decrypted = Buffer.concat([
      decipher.update(encrypted),
      decipher.final()
    ]);
    
    return decrypted.toString('utf8');
  }
  
  // 해시 생성
  hash(data: string): string {
    return crypto.createHash('sha256').update(data).digest('hex');
  }
  
  // 안전한 토큰 생성
  generateSecureToken(length: number = 32): string {
    return crypto.randomBytes(length).toString('base64url');
  }
}

// PII 데이터 마스킹
export class DataMasking {
  static maskEmail(email: string): string {
    const [local, domain] = email.split('@');
    if (!domain) return '***';
    
    const maskedLocal = local.length > 2 
      ? local[0] + '*'.repeat(local.length - 2) + local[local.length - 1]
      : '*'.repeat(local.length);
    
    return `${maskedLocal}@${domain}`;
  }
  
  static maskPhone(phone: string): string {
    const digits = phone.replace(/\D/g, '');
    if (digits.length < 4) return '*'.repeat(digits.length);
    
    return digits.slice(0, -4).replace(/./g, '*') + digits.slice(-4);
  }
  
  static maskCreditCard(cardNumber: string): string {
    const digits = cardNumber.replace(/\D/g, '');
    if (digits.length < 4) return '*'.repeat(digits.length);
    
    return '*'.repeat(digits.length - 4) + digits.slice(-4);
  }
  
  static maskObject(obj: any, sensitiveFields: string[]): any {
    const masked = JSON.parse(JSON.stringify(obj));
    
    const maskField = (target: any, path: string) => {
      const keys = path.split('.');
      let current = target;
      
      for (let i = 0; i < keys.length - 1; i++) {
        if (current[keys[i]] === undefined) return;
        current = current[keys[i]];
      }
      
      const lastKey = keys[keys.length - 1];
      if (current[lastKey] !== undefined && typeof current[lastKey] === 'string') {
        if (lastKey.toLowerCase().includes('email')) {
          current[lastKey] = this.maskEmail(current[lastKey]);
        } else if (lastKey.toLowerCase().includes('phone')) {
          current[lastKey] = this.maskPhone(current[lastKey]);
        } else if (lastKey.toLowerCase().includes('card')) {
          current[lastKey] = this.maskCreditCard(current[lastKey]);
        } else {
          current[lastKey] = '*'.repeat(current[lastKey].length);
        }
      }
    };
    
    sensitiveFields.forEach(field => maskField(masked, field));
    return masked;
  }
}

// 암호화 미들웨어
export class EncryptionMiddleware {
  private static encryptionService = new EncryptionService();
  
  static encryptResponse(fieldsToEncrypt: string[]) {
    return async (req: Request, res: Response, next: NextFunction) => {
      const originalJson = res.json;
      
      res.json = function(data: any) {
        if (fieldsToEncrypt.length > 0 && data) {
          const encrypted = EncryptionMiddleware.encryptFields(data, fieldsToEncrypt);
          return originalJson.call(this, encrypted);
        }
        return originalJson.call(this, data);
      };
      
      next();
    };
  }
  
  private static encryptFields(data: any, fields: string[]): any {
    const result = JSON.parse(JSON.stringify(data));
    
    for (const field of fields) {
      const value = this.getFieldValue(result, field);
      if (value && typeof value === 'string') {
        const encrypted = this.encryptionService.encryptField(value);
        this.setFieldValue(result, field, encrypted);
      }
    }
    
    return result;
  }
  
  private static getFieldValue(obj: any, path: string): any {
    return path.split('.').reduce((current, key) => current?.[key], obj);
  }
  
  private static setFieldValue(obj: any, path: string, value: any): void {
    const keys = path.split('.');
    const lastKey = keys.pop()!;
    const target = keys.reduce((current, key) => current[key], obj);
    target[lastKey] = value;
  }
}