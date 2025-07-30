import crypto from 'crypto';
import { KMSClient, EncryptCommand, DecryptCommand } from '@aws-sdk/client-kms';

export class EncryptionService {
  private kmsClient: KMSClient;
  private algorithm = 'aes-256-gcm';
  private keyId: string;
  
  constructor() {
    this.kmsClient = new KMSClient({ region: process.env.AWS_REGION });
    this.keyId = process.env.KMS_KEY_ID || 'alias/t-developer-key';
  }
  
  // Encrypt data using AES-256-GCM
  encrypt(plaintext: string, key?: string): string {
    const encryptionKey = key || this.generateKey();
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipheriv(this.algorithm, Buffer.from(encryptionKey, 'hex'), iv);
    
    let encrypted = cipher.update(plaintext, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    
    const authTag = cipher.getAuthTag();
    
    // Combine IV, auth tag, and encrypted data
    return iv.toString('hex') + ':' + authTag.toString('hex') + ':' + encrypted;
  }
  
  // Decrypt data using AES-256-GCM
  decrypt(encryptedData: string, key?: string): string {
    const encryptionKey = key || this.generateKey();
    const parts = encryptedData.split(':');
    
    if (parts.length !== 3) {
      throw new Error('Invalid encrypted data format');
    }
    
    const iv = Buffer.from(parts[0], 'hex');
    const authTag = Buffer.from(parts[1], 'hex');
    const encrypted = parts[2];
    
    const decipher = crypto.createDecipheriv(this.algorithm, Buffer.from(encryptionKey, 'hex'), iv);
    decipher.setAuthTag(authTag);
    
    let decrypted = decipher.update(encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    
    return decrypted;
  }
  
  // Encrypt using AWS KMS
  async encryptWithKMS(plaintext: string): Promise<string> {
    try {
      const command = new EncryptCommand({
        KeyId: this.keyId,
        Plaintext: Buffer.from(plaintext, 'utf8')
      });
      
      const response = await this.kmsClient.send(command);
      
      if (!response.CiphertextBlob) {
        throw new Error('KMS encryption failed');
      }
      
      return Buffer.from(response.CiphertextBlob).toString('base64');
    } catch (error) {
      throw new Error(`KMS encryption failed: ${error.message}`);
    }
  }
  
  // Decrypt using AWS KMS
  async decryptWithKMS(encryptedData: string): Promise<string> {
    try {
      const command = new DecryptCommand({
        CiphertextBlob: Buffer.from(encryptedData, 'base64')
      });
      
      const response = await this.kmsClient.send(command);
      
      if (!response.Plaintext) {
        throw new Error('KMS decryption failed');
      }
      
      return Buffer.from(response.Plaintext).toString('utf8');
    } catch (error) {
      throw new Error(`KMS decryption failed: ${error.message}`);
    }
  }
  
  // Generate random key
  generateKey(): string {
    return crypto.randomBytes(32).toString('hex');
  }
  
  // Generate hash
  hash(data: string, algorithm: string = 'sha256'): string {
    return crypto.createHash(algorithm).update(data).digest('hex');
  }
  
  // Generate HMAC
  hmac(data: string, secret: string, algorithm: string = 'sha256'): string {
    return crypto.createHmac(algorithm, secret).update(data).digest('hex');
  }
  
  // Generate secure random token
  generateToken(length: number = 32): string {
    return crypto.randomBytes(length).toString('base64url');
  }
  
  // Constant-time string comparison
  constantTimeCompare(a: string, b: string): boolean {
    if (a.length !== b.length) {
      return false;
    }
    
    return crypto.timingSafeEqual(Buffer.from(a), Buffer.from(b));
  }
}