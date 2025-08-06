const express = require('express');
const crypto = require('crypto');

const router = express.Router();

// 간단한 암호화 서비스
class EncryptionService {
  constructor() {
    this.algorithm = 'aes-256-gcm';
    this.keyLength = 32;
    this.ivLength = 16;
    this.saltLength = 32;
    this.iterations = 100000;
  }
  
  encryptField(plaintext, password = process.env.ENCRYPTION_KEY || 'default-key') {
    const salt = crypto.randomBytes(this.saltLength);
    const key = crypto.pbkdf2Sync(password, salt, this.iterations, this.keyLength, 'sha256');
    const iv = crypto.randomBytes(this.ivLength);
    
    const cipher = crypto.createCipheriv(this.algorithm, key, iv);
    const encrypted = Buffer.concat([
      cipher.update(plaintext, 'utf8'),
      cipher.final()
    ]);
    
    const tag = cipher.getAuthTag();
    const combined = Buffer.concat([salt, iv, tag, encrypted]);
    
    return combined.toString('base64');
  }
  
  decryptField(encryptedData, password = process.env.ENCRYPTION_KEY || 'default-key') {
    const combined = Buffer.from(encryptedData, 'base64');
    
    const salt = combined.slice(0, this.saltLength);
    const iv = combined.slice(this.saltLength, this.saltLength + this.ivLength);
    const tag = combined.slice(this.saltLength + this.ivLength, this.saltLength + this.ivLength + 16);
    const encrypted = combined.slice(this.saltLength + this.ivLength + 16);
    
    const key = crypto.pbkdf2Sync(password, salt, this.iterations, this.keyLength, 'sha256');
    
    const decipher = crypto.createDecipheriv(this.algorithm, key, iv);
    decipher.setAuthTag(tag);
    
    const decrypted = Buffer.concat([
      decipher.update(encrypted),
      decipher.final()
    ]);
    
    return decrypted.toString('utf8');
  }
  
  hash(data) {
    return crypto.createHash('sha256').update(data).digest('hex');
  }
  
  generateSecureToken(length = 32) {
    return crypto.randomBytes(length).toString('base64url');
  }
}

// 데이터 마스킹
class DataMasking {
  static maskEmail(email) {
    const [local, domain] = email.split('@');
    if (!domain) return '***';
    
    const maskedLocal = local.length > 2 
      ? local[0] + '*'.repeat(local.length - 2) + local[local.length - 1]
      : '*'.repeat(local.length);
    
    return `${maskedLocal}@${domain}`;
  }
  
  static maskPhone(phone) {
    const digits = phone.replace(/\D/g, '');
    if (digits.length < 4) return '*'.repeat(digits.length);
    
    return digits.slice(0, -4).replace(/./g, '*') + digits.slice(-4);
  }
  
  static maskObject(obj, sensitiveFields) {
    const masked = JSON.parse(JSON.stringify(obj));
    
    const maskField = (target, path) => {
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
        } else {
          current[lastKey] = '*'.repeat(current[lastKey].length);
        }
      }
    };
    
    sensitiveFields.forEach(field => maskField(masked, field));
    return masked;
  }
}

const encryptionService = new EncryptionService();

// 암호화 데모 엔드포인트
router.post('/encrypt', (req, res) => {
  try {
    const { data } = req.body;
    
    if (!data) {
      return res.status(400).json({ error: 'Data is required' });
    }
    
    const encrypted = encryptionService.encryptField(data);
    const hash = encryptionService.hash(data);
    
    res.json({
      success: true,
      original: data,
      encrypted: encrypted,
      hash: hash,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ error: 'Encryption failed', message: error.message });
  }
});

// 복호화 데모 엔드포인트
router.post('/decrypt', (req, res) => {
  try {
    const { encryptedData } = req.body;
    
    if (!encryptedData) {
      return res.status(400).json({ error: 'Encrypted data is required' });
    }
    
    const decrypted = encryptionService.decryptField(encryptedData);
    
    res.json({
      success: true,
      encrypted: encryptedData,
      decrypted: decrypted,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ error: 'Decryption failed', message: error.message });
  }
});

// 데이터 마스킹 데모 엔드포인트
router.post('/mask', (req, res) => {
  try {
    const { data, sensitiveFields } = req.body;
    
    if (!data) {
      return res.status(400).json({ error: 'Data is required' });
    }
    
    const fields = sensitiveFields || ['email', 'phone', 'password'];
    const masked = DataMasking.maskObject(data, fields);
    
    res.json({
      success: true,
      original: data,
      masked: masked,
      sensitiveFields: fields,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ error: 'Masking failed', message: error.message });
  }
});

// 토큰 생성 엔드포인트
router.get('/token', (req, res) => {
  try {
    const length = parseInt(req.query.length) || 32;
    const token = encryptionService.generateSecureToken(length);
    
    res.json({
      success: true,
      token: token,
      length: length,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ error: 'Token generation failed', message: error.message });
  }
});

// 해시 생성 엔드포인트
router.post('/hash', (req, res) => {
  try {
    const { data } = req.body;
    
    if (!data) {
      return res.status(400).json({ error: 'Data is required' });
    }
    
    const hash = encryptionService.hash(data);
    
    res.json({
      success: true,
      original: data,
      hash: hash,
      algorithm: 'SHA-256',
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ error: 'Hashing failed', message: error.message });
  }
});

module.exports = router;