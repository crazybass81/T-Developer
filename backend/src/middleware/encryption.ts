import { Request, Response, NextFunction } from 'express';
import { EncryptionService, DataMasking } from '../security/encryption';

const encryptionService = new EncryptionService();

// Middleware to encrypt sensitive response fields
export const encryptSensitiveFields = (fieldsToEncrypt: string[]) => {
  return async (req: Request, res: Response, next: NextFunction) => {
    const originalJson = res.json;
    
    res.json = async function(data: any) {
      if (fieldsToEncrypt.length > 0 && data) {
        try {
          const encrypted = await encryptFields(data, fieldsToEncrypt, {
            userId: (req as any).user?.id,
            requestId: (req as any).id
          });
          return originalJson.call(this, encrypted);
        } catch (error) {
          console.error('Encryption error:', error);
          return originalJson.call(this, data);
        }
      }
      return originalJson.call(this, data);
    };
    
    next();
  };
};

// Middleware to mask sensitive data in logs
export const maskSensitiveData = (sensitiveFields: string[]) => {
  return (req: Request, res: Response, next: NextFunction) => {
    // Mask request body for logging
    if (req.body && sensitiveFields.length > 0) {
      (req as any).maskedBody = DataMasking.maskObject(req.body, sensitiveFields);
    }
    
    next();
  };
};

// Helper function to encrypt specific fields in an object
async function encryptFields(
  data: any,
  fields: string[],
  context?: Record<string, string>
): Promise<any> {
  const result = JSON.parse(JSON.stringify(data));
  
  for (const field of fields) {
    const value = getFieldValue(result, field);
    if (value && typeof value === 'string') {
      try {
        const encrypted = await encryptionService.encryptField(value, context);
        setFieldValue(result, field, encrypted);
      } catch (error) {
        console.error(`Failed to encrypt field ${field}:`, error);
      }
    }
  }
  
  return result;
}

function getFieldValue(obj: any, path: string): any {
  const keys = path.split('.');
  let current = obj;
  
  for (const key of keys) {
    if (current[key] === undefined) return undefined;
    current = current[key];
  }
  
  return current;
}

function setFieldValue(obj: any, path: string, value: any): void {
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