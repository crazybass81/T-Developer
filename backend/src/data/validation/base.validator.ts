import Joi from 'joi';

export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
}

export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

export abstract class BaseValidator<T> {
  protected abstract schema: Joi.ObjectSchema;

  validate(data: T): ValidationResult {
    const result = this.schema.validate(data, {
      abortEarly: false,
      stripUnknown: true
    });

    if (result.error) {
      return {
        isValid: false,
        errors: result.error.details.map(detail => ({
          field: detail.path.join('.'),
          message: detail.message,
          code: detail.type
        }))
      };
    }

    return { isValid: true, errors: [] };
  }

  async validateAsync(data: T): Promise<ValidationResult> {
    try {
      await this.schema.validateAsync(data, {
        abortEarly: false,
        stripUnknown: true
      });
      return { isValid: true, errors: [] };
    } catch (error) {
      if (error.isJoi) {
        return {
          isValid: false,
          errors: error.details.map((detail: any) => ({
            field: detail.path.join('.'),
            message: detail.message,
            code: detail.type
          }))
        };
      }
      throw error;
    }
  }

  sanitize(data: T): T {
    const result = this.schema.validate(data, { stripUnknown: true });
    return result.value;
  }
}