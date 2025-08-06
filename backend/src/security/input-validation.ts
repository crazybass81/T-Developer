import Joi from 'joi';
import DOMPurify from 'isomorphic-dompurify';
import { Request, Response, NextFunction } from 'express';


// 커스텀 Joi 확장
const customJoi = Joi.extend((joi) => ({
  type: 'string',
  base: joi.string(),
  messages: {
    'string.noSQL': '{{#label}} contains potential SQL injection',
    'string.noXSS': '{{#label}} contains potential XSS attack'
  },
  rules: {
    noSQL: {
      validate(value, helpers) {
        const sqlPatterns = [
          /(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER|CREATE)\b)/i,
          /(--|\/\*|\*\/|xp_|sp_)/i,
          /(\bOR\b\s*\d+\s*=\s*\d+)/i,
          /(\bAND\b\s*\d+\s*=\s*\d+)/i
        ];
        
        for (const pattern of sqlPatterns) {
          if (pattern.test(value)) {
            return helpers.error('string.noSQL');
          }
        }
        return value;
      }
    },
    noXSS: {
      validate(value, helpers) {
        const xssPatterns = [
          /<script[^>]*>.*?<\/script>/gi,
          /<iframe[^>]*>.*?<\/iframe>/gi,
          /javascript:/gi,
          /on\w+\s*=/gi
        ];
        
        for (const pattern of xssPatterns) {
          if (pattern.test(value)) {
            return helpers.error('string.noXSS');
          }
        }
        return value;
      }
    }
  }
}));

// 검증 스키마 정의
export const validationSchemas = {
  createProject: customJoi.object({
    name: customJoi.string()
      .min(3)
      .max(100)
      .pattern(/^[a-zA-Z0-9-_\s]+$/)
      .noSQL()
      .noXSS()
      .required(),
    
    description: customJoi.string()
      .min(10)
      .max(5000)
      .noSQL()
      .noXSS()
      .required(),
    
    projectType: customJoi.string()
      .valid('web', 'api', 'mobile', 'desktop', 'cli')
      .required()
  }),
  
  registerUser: customJoi.object({
    email: customJoi.string()
      .email({ tlds: { allow: false } })
      .max(255)
      .noSQL()
      .required(),
    
    password: customJoi.string()
      .min(8)
      .max(128)
      .pattern(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/)
      .required(),
    
    name: customJoi.string()
      .min(2)
      .max(100)
      .pattern(/^[a-zA-Z\s'-]+$/)
      .noSQL()
      .noXSS()
      .required()
  })
};

// HTML 살균 함수
export function sanitizeInput(input: any): any {
  if (typeof input === 'string') {
    return DOMPurify.sanitize(input, {
      ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'p', 'br'],
      ALLOWED_ATTR: [],
      ALLOW_DATA_ATTR: false
    });
  } else if (Array.isArray(input)) {
    return input.map(item => sanitizeInput(item));
  } else if (input !== null && typeof input === 'object') {
    const sanitized: any = {};
    for (const key in input) {
      if (input.hasOwnProperty(key)) {
        sanitized[key] = sanitizeInput(input[key]);
      }
    }
    return sanitized;
  }
  return input;
}

// 검증 미들웨어
export function validate(schema: Joi.ObjectSchema) {
  return async (req: Request, res: Response, next: NextFunction) => {
    try {
      req.body = sanitizeInput(req.body);
      const validated = await schema.validateAsync(req.body, {
        abortEarly: false,
        stripUnknown: true
      });
      req.body = validated;
      next();
    } catch (error) {
      if (error instanceof Joi.ValidationError) {
        const errors = error.details.map(detail => ({
          field: detail.path.join('.'),
          message: detail.message
        }));
        
        return res.status(400).json({
          error: 'Validation failed',
          details: errors
        });
      }
      next(error);
    }
  };
}

// 파일 업로드 검증
export function validateFileUpload(options: {
  maxSize?: number;
  allowedTypes?: string[];
}) {
  const {
    maxSize = 10 * 1024 * 1024, // 10MB
    allowedTypes = ['image/jpeg', 'image/png', 'application/pdf']
  } = options;
  
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.file) {
      return next();
    }
    
    if (req.file.size > maxSize) {
      return res.status(400).json({
        error: 'File too large',
        maxSize: `${maxSize / 1024 / 1024}MB`
      });
    }
    
    if (!allowedTypes.includes(req.file.mimetype)) {
      return res.status(400).json({
        error: 'Invalid file type',
        allowedTypes
      });
    }
    
    next();
  };
}