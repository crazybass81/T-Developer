/**
 * Validation utilities for T-Developer entities
 * Provides comprehensive validation framework for data integrity
 */

export class ValidationError extends Error {
  public field?: string;
  public code?: string;
  public details?: any;

  constructor(message: string, field?: string, code?: string, details?: any) {
    super(message);
    this.name = 'ValidationError';
    this.field = field;
    this.code = code;
    this.details = details;
  }
}

export interface ValidationRule<T = any> {
  name: string;
  message: string;
  validator: (value: T, entity?: any) => boolean | Promise<boolean>;
}

export interface ValidationSchema {
  [fieldName: string]: ValidationRule[];
}

export class Validator {
  private static emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  private static uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  private static phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;

  /**
   * Validate entity against schema
   */
  public static async validate<T>(
    entity: T,
    schema: ValidationSchema
  ): Promise<ValidationError[]> {
    const errors: ValidationError[] = [];

    for (const [field, rules] of Object.entries(schema)) {
      const value = (entity as any)[field];

      for (const rule of rules) {
        try {
          const isValid = await rule.validator(value, entity);
          if (!isValid) {
            errors.push(new ValidationError(
              rule.message,
              field,
              rule.name,
              { value }
            ));
          }
        } catch (error) {
          errors.push(new ValidationError(
            `Validation error in field ${field}: ${error}`,
            field,
            'VALIDATION_ERROR',
            { error, rule: rule.name }
          ));
        }
      }
    }

    return errors;
  }

  /**
   * Common validation rules
   */
  public static readonly Rules = {
    required: (message: string = 'Field is required'): ValidationRule => ({
      name: 'required',
      message,
      validator: (value) => value !== null && value !== undefined && value !== ''
    }),

    minLength: (min: number, message?: string): ValidationRule => ({
      name: 'minLength',
      message: message || `Must be at least ${min} characters long`,
      validator: (value: string) => !value || value.length >= min
    }),

    maxLength: (max: number, message?: string): ValidationRule => ({
      name: 'maxLength',
      message: message || `Must be no more than ${max} characters long`,
      validator: (value: string) => !value || value.length <= max
    }),

    email: (message: string = 'Invalid email format'): ValidationRule => ({
      name: 'email',
      message,
      validator: (value: string) => !value || Validator.emailRegex.test(value)
    }),

    uuid: (message: string = 'Invalid UUID format'): ValidationRule => ({
      name: 'uuid',
      message,
      validator: (value: string) => !value || Validator.uuidRegex.test(value)
    }),

    phone: (message: string = 'Invalid phone number format'): ValidationRule => ({
      name: 'phone',
      message,
      validator: (value: string) => !value || Validator.phoneRegex.test(value)
    }),

    min: (min: number, message?: string): ValidationRule => ({
      name: 'min',
      message: message || `Must be at least ${min}`,
      validator: (value: number) => value === undefined || value >= min
    }),

    max: (max: number, message?: string): ValidationRule => ({
      name: 'max',
      message: message || `Must be no more than ${max}`,
      validator: (value: number) => value === undefined || value <= max
    }),

    range: (min: number, max: number, message?: string): ValidationRule => ({
      name: 'range',
      message: message || `Must be between ${min} and ${max}`,
      validator: (value: number) => value === undefined || (value >= min && value <= max)
    }),

    oneOf: (values: any[], message?: string): ValidationRule => ({
      name: 'oneOf',
      message: message || `Must be one of: ${values.join(', ')}`,
      validator: (value) => !value || values.includes(value)
    }),

    pattern: (regex: RegExp, message: string = 'Invalid format'): ValidationRule => ({
      name: 'pattern',
      message,
      validator: (value: string) => !value || regex.test(value)
    }),

    url: (message: string = 'Invalid URL format'): ValidationRule => ({
      name: 'url',
      message,
      validator: (value: string) => {
        if (!value) return true;
        try {
          new URL(value);
          return true;
        } catch {
          return false;
        }
      }
    }),

    dateString: (message: string = 'Invalid date format'): ValidationRule => ({
      name: 'dateString',
      message,
      validator: (value: string) => {
        if (!value) return true;
        const date = new Date(value);
        return !isNaN(date.getTime());
      }
    }),

    future: (message: string = 'Date must be in the future'): ValidationRule => ({
      name: 'future',
      message,
      validator: (value: string) => {
        if (!value) return true;
        return new Date(value).getTime() > Date.now();
      }
    }),

    past: (message: string = 'Date must be in the past'): ValidationRule => ({
      name: 'past',
      message,
      validator: (value: string) => {
        if (!value) return true;
        return new Date(value).getTime() < Date.now();
      }
    }),

    json: (message: string = 'Invalid JSON format'): ValidationRule => ({
      name: 'json',
      message,
      validator: (value: string) => {
        if (!value) return true;
        try {
          JSON.parse(value);
          return true;
        } catch {
          return false;
        }
      }
    }),

    array: (message: string = 'Must be an array'): ValidationRule => ({
      name: 'array',
      message,
      validator: (value) => !value || Array.isArray(value)
    }),

    object: (message: string = 'Must be an object'): ValidationRule => ({
      name: 'object',
      message,
      validator: (value) => !value || (typeof value === 'object' && !Array.isArray(value))
    }),

    numeric: (message: string = 'Must be a number'): ValidationRule => ({
      name: 'numeric',
      message,
      validator: (value) => value === undefined || !isNaN(Number(value))
    }),

    integer: (message: string = 'Must be an integer'): ValidationRule => ({
      name: 'integer',
      message,
      validator: (value: number) => value === undefined || Number.isInteger(value)
    }),

    positive: (message: string = 'Must be positive'): ValidationRule => ({
      name: 'positive',
      message,
      validator: (value: number) => value === undefined || value > 0
    }),

    nonNegative: (message: string = 'Must be non-negative'): ValidationRule => ({
      name: 'nonNegative',
      message,
      validator: (value: number) => value === undefined || value >= 0
    }),

    custom: (
      validator: (value: any, entity?: any) => boolean | Promise<boolean>,
      message: string,
      name: string = 'custom'
    ): ValidationRule => ({
      name,
      message,
      validator
    }),

    unique: (
      checkFunction: (value: any, entity?: any) => Promise<boolean>,
      message: string = 'Value must be unique'
    ): ValidationRule => ({
      name: 'unique',
      message,
      validator: checkFunction
    }),

    exists: (
      checkFunction: (value: any, entity?: any) => Promise<boolean>,
      message: string = 'Referenced entity does not exist'
    ): ValidationRule => ({
      name: 'exists',
      message,
      validator: checkFunction
    }),

    conditional: (
      condition: (entity: any) => boolean,
      rule: ValidationRule
    ): ValidationRule => ({
      name: `conditional_${rule.name}`,
      message: rule.message,
      validator: (value, entity) => {
        if (!condition(entity)) return true;
        return rule.validator(value, entity);
      }
    })
  };

  /**
   * Entity-specific validation schemas
   */
  public static readonly Schemas = {
    BaseEntity: {
      EntityId: [
        Validator.Rules.required('Entity ID is required'),
        Validator.Rules.minLength(1, 'Entity ID cannot be empty')
      ],
      EntityType: [
        Validator.Rules.required('Entity type is required'),
        Validator.Rules.oneOf(['USER', 'PROJECT', 'AGENT', 'TASK', 'SESSION'])
      ],
      Status: [
        Validator.Rules.required('Status is required'),
        Validator.Rules.oneOf(['ACTIVE', 'INACTIVE', 'PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 'ARCHIVED', 'DELETED'])
      ],
      CreatedAt: [
        Validator.Rules.required('Created date is required'),
        Validator.Rules.dateString()
      ],
      UpdatedAt: [
        Validator.Rules.required('Updated date is required'),
        Validator.Rules.dateString()
      ],
      Version: [
        Validator.Rules.integer(),
        Validator.Rules.positive()
      ],
      Priority: [
        Validator.Rules.integer(),
        Validator.Rules.range(1, 10, 'Priority must be between 1 and 10')
      ]
    },

    User: {
      username: [
        Validator.Rules.required('Username is required'),
        Validator.Rules.minLength(3, 'Username must be at least 3 characters'),
        Validator.Rules.maxLength(50, 'Username must be no more than 50 characters'),
        Validator.Rules.pattern(/^[a-zA-Z0-9_-]+$/, 'Username can only contain letters, numbers, underscores, and hyphens')
      ],
      email: [
        Validator.Rules.required('Email is required'),
        Validator.Rules.email(),
        Validator.Rules.maxLength(255, 'Email must be no more than 255 characters')
      ],
      fullName: [
        Validator.Rules.maxLength(100, 'Full name must be no more than 100 characters')
      ],
      phoneNumber: [
        Validator.Rules.phone()
      ]
    },

    Project: {
      name: [
        Validator.Rules.required('Project name is required'),
        Validator.Rules.minLength(1, 'Project name cannot be empty'),
        Validator.Rules.maxLength(100, 'Project name must be no more than 100 characters')
      ],
      description: [
        Validator.Rules.maxLength(1000, 'Description must be no more than 1000 characters')
      ],
      ownerId: [
        Validator.Rules.required('Owner ID is required'),
        Validator.Rules.uuid('Invalid owner ID format')
      ],
      visibility: [
        Validator.Rules.required('Visibility is required'),
        Validator.Rules.oneOf(['public', 'private', 'organization'])
      ]
    },

    Agent: {
      name: [
        Validator.Rules.required('Agent name is required'),
        Validator.Rules.minLength(1, 'Agent name cannot be empty'),
        Validator.Rules.maxLength(100, 'Agent name must be no more than 100 characters')
      ],
      type: [
        Validator.Rules.required('Agent type is required'),
        Validator.Rules.oneOf(['NL_INPUT', 'UI_SELECTION', 'PARSER', 'COMPONENT_DECISION', 'MATCH_RATE', 'SEARCH', 'GENERATION', 'ASSEMBLY', 'DOWNLOAD', 'CUSTOM'])
      ],
      version: [
        Validator.Rules.required('Version is required'),
        Validator.Rules.pattern(/^\d+\.\d+\.\d+$/, 'Version must be in semver format (e.g., 1.0.0)')
      ],
      projectId: [
        Validator.Rules.required('Project ID is required'),
        Validator.Rules.uuid('Invalid project ID format')
      ]
    }
  };

  /**
   * Sanitize input data
   */
  public static sanitize = {
    string: (value: string): string => {
      if (typeof value !== 'string') return '';
      return value.trim();
    },

    email: (value: string): string => {
      if (typeof value !== 'string') return '';
      return value.trim().toLowerCase();
    },

    html: (value: string): string => {
      if (typeof value !== 'string') return '';
      return value
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#x27;');
    },

    number: (value: any): number | undefined => {
      const num = Number(value);
      return isNaN(num) ? undefined : num;
    },

    boolean: (value: any): boolean => {
      if (typeof value === 'boolean') return value;
      if (typeof value === 'string') {
        return ['true', '1', 'yes', 'on'].includes(value.toLowerCase());
      }
      return Boolean(value);
    },

    array: (value: any): any[] => {
      if (Array.isArray(value)) return value;
      if (value === null || value === undefined) return [];
      return [value];
    }
  };
}