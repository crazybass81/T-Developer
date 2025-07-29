import crypto from 'crypto';
import { KMSClient, EncryptCommand, DecryptCommand, GenerateDataKeyCommand } from '@aws-sdk/client-kms';
import { Request, Response, NextFunction } from 'express';

const ENCRYPTION_ALGORITHM = 'aes-256-gcm';
const IV_LENGTH = 16;
const TAG_LENGTH = 16;
const SALT_LENGTH = 32;
const KEY_LENGTH = 32;
const ITERATIONS = 100000;

export class EncryptionService {
  private kmsClient: KMSClient;
  private masterKeyId: string;
  
  constructor() {
    this.kmsClient = new KMSClient({ region: process.env.AWS_REGION });
    this.masterKeyId = process.env.KMS_MASTER_KEY_ID!;
  }
  
  async encryptField(plaintext: string, context?: Record<string, string>): Promise<string> {
    const dataKeyResponse = await this.kmsClient.send(new GenerateDataKeyCommand({
      KeyId: this.masterKeyId,
      KeySpec: 'AES_256',
      EncryptionContext: context
    }));
    
    const plaintextKey = dataKeyResponse.Plaintext!;
    const encryptedKey = dataKeyResponse.CiphertextBlob!;
    
    const iv = crypto.randomBytes(IV_LENGTH);
    const cipher = crypto.createCipheriv(ENCRYPTION_ALGORITHM, plaintextKey, iv);
    
    const encrypted = Buffer.concat([cipher.update(plaintext, 'utf8'), cipher.final()]);
    const tag = cipher.getAuthTag();
    
    const combined = Buffer.concat([
      Buffer.from([encryptedKey.length >> 8, encryptedKey.length & 0xff]),
      encryptedKey, iv, tag, encrypted
    ]);
    
    crypto.randomFillSync(plaintextKey);
    return combined.toString('base64');
  }
  
  async decryptField(encryptedData: string, context?: Record<string, string>): Promise<string> {
    const combined = Buffer.from(encryptedData, 'base64');
    
    const keyLength = (combined[0] << 8) | combined[1];
    const encryptedKey = combined.slice(2, 2 + keyLength);
    const iv = combined.slice(2 + keyLength, 2 + keyLength + IV_LENGTH);
    const tag = combined.slice(2 + keyLength + IV_LENGTH, 2 + keyLength + IV_LENGTH + TAG_LENGTH);
    const encrypted = combined.slice(2 + keyLength + IV_LENGTH + TAG_LENGTH);
    
    const decryptResponse = await this.kmsClient.send(new DecryptCommand({
      CiphertextBlob: encryptedKey,
      EncryptionContext: context
    }));
    
    const plaintextKey = decryptResponse.Plaintext!;
    const decipher = crypto.createDecipheriv(ENCRYPTION_ALGORITHM, plaintextKey, iv);
    decipher.setAuthTag(tag);
    
    const decrypted = Buffer.concat([decipher.update(encrypted), decipher.final()]);
    crypto.randomFillSync(plaintextKey);
    
    return decrypted.toString('utf8');
  }
  
  encryptSymmetric(plaintext: string, password: string): string {
    const salt = crypto.randomBytes(SALT_LENGTH);
    const key = crypto.pbkdf2Sync(password, salt, ITERATIONS, KEY_LENGTH, 'sha256');
    const iv = crypto.randomBytes(IV_LENGTH);
    
    const cipher = crypto.createCipheriv(ENCRYPTION_ALGORITHM, key, iv);
    const encrypted = Buffer.concat([cipher.update(plaintext, 'utf8'), cipher.final()]);
    const tag = cipher.getAuthTag();
    
    return Buffer.concat([salt, iv, tag, encrypted]).toString('base64');
  }
  
  decryptSymmetric(encryptedData: string, password: string): string {
    const combined = Buffer.from(encryptedData, 'base64');
    
    const salt = combined.slice(0, SALT_LENGTH);
    const iv = combined.slice(SALT_LENGTH, SALT_LENGTH + IV_LENGTH);
    const tag = combined.slice(SALT_LENGTH + IV_LENGTH, SALT_LENGTH + IV_LENGTH + TAG_LENGTH);
    const encrypted = combined.slice(SALT_LENGTH + IV_LENGTH + TAG_LENGTH);
    
    const key = crypto.pbkdf2Sync(password, salt, ITERATIONS, KEY_LENGTH, 'sha256');
    const decipher = crypto.createDecipheriv(ENCRYPTION_ALGORITHM, key, iv);
    decipher.setAuthTag(tag);
    
    return Buffer.concat([decipher.update(encrypted), decipher.final()]).toString('utf8');
  }
  
  hash(data: string): string {
    return crypto.createHash('sha256').update(data).digest('hex');
  }
  
  generateSecureToken(length: number = 32): string {
    return crypto.randomBytes(length).toString('base64url');
  }
}

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

export class EncryptionMiddleware {
  private static encryptionService = new EncryptionService();
  
  static encryptResponse(fieldsToEncrypt: string[]) {
    return async (req: Request, res: Response, next: NextFunction) => {
      const originalJson = res.json;
      
      res.json = async function(data: any) {
        if (fieldsToEncrypt.length > 0 && data) {
          const encrypted = await EncryptionMiddleware.encryptFields(
            data, fieldsToEncrypt, { userId: req.user?.id }
          );
          return originalJson.call(this, encrypted);
        }
        return originalJson.call(this, data);
      };
      
      next();
    };
  }
  
  static decryptRequest(fieldsToDecrypt: string[]) {
    return async (req: Request, res: Response, next: NextFunction) => {
      if (fieldsToDecrypt.length > 0 && req.body) {
        try {
          req.body = await EncryptionMiddleware.decryptFields(
            req.body, fieldsToDecrypt, { userId: req.user?.id }
          );
        } catch (error) {
          return res.status(400).json({
            error: 'Failed to decrypt request data',
            code: 'DECRYPTION_ERROR'
          });
        }
      }
      next();
    };
  }
  
  private static async encryptFields(data: any, fields: string[], context?: Record<string, string>): Promise<any> {
    const result = JSON.parse(JSON.stringify(data));
    
    for (const field of fields) {
      const value = this.getFieldValue(result, field);
      if (value && typeof value === 'string') {
        const encrypted = await this.encryptionService.encryptField(value, context);
        this.setFieldValue(result, field, encrypted);
      }
    }
    
    return result;
  }
  
  private static async decryptFields(data: any, fields: string[], context?: Record<string, string>): Promise<any> {
    const result = JSON.parse(JSON.stringify(data));
    
    for (const field of fields) {
      const value = this.getFieldValue(result, field);
      if (value && typeof value === 'string') {
        const decrypted = await this.encryptionService.decryptField(value, context);
        this.setFieldValue(result, field, decrypted);
      }
    }
    
    return result;
  }
  
  private static getFieldValue(obj: any, path: string): any {
    const keys = path.split('.');
    let current = obj;
    
    for (const key of keys) {
      if (current[key] === undefined) return undefined;
      current = current[key];
    }
    
    return current;
  }
  
  private static setFieldValue(obj: any, path: string, value: any): void {
    const keys = path.split('.');
    let current = obj;
    
    for (let i = 0; i < keys.length - 1; i++) {
      if (current[keys[i]] === undefined) {
        current[keys[i]] = {};
      }
      current = current[keys[i]];
    }
    
    current[keys[keys.length - 1]] = value;
  }
}