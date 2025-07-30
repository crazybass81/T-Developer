import Joi from 'joi';
import { BaseValidator } from './base.validator';
import { User, UserPreferences } from '../models/user.model';

export class UserValidator extends BaseValidator<User> {
  protected schema = Joi.object({
    id: Joi.string().uuid().required(),
    email: Joi.string().email().required(),
    username: Joi.string().alphanum().min(3).max(30).required(),
    role: Joi.string().valid('admin', 'developer', 'viewer').required(),
    preferences: Joi.object({
      theme: Joi.string().valid('light', 'dark').default('light'),
      language: Joi.string().valid('en', 'es', 'fr', 'de', 'ja').default('en'),
      notifications: Joi.object({
        email: Joi.boolean().default(true),
        push: Joi.boolean().default(true),
        sms: Joi.boolean().default(false)
      }).default({}),
      timezone: Joi.string().default('UTC')
    }).default({}),
    isActive: Joi.boolean().default(true),
    lastLoginAt: Joi.date().optional(),
    createdAt: Joi.date().required(),
    updatedAt: Joi.date().required(),
    version: Joi.number().integer().min(1).required()
  });

  validateEmail(email: string): boolean {
    const emailSchema = Joi.string().email();
    return !emailSchema.validate(email).error;
  }

  validateUsername(username: string): boolean {
    const usernameSchema = Joi.string().alphanum().min(3).max(30);
    return !usernameSchema.validate(username).error;
  }

  validatePreferences(preferences: UserPreferences): ValidationResult {
    const preferencesSchema = Joi.object({
      theme: Joi.string().valid('light', 'dark'),
      language: Joi.string().valid('en', 'es', 'fr', 'de', 'ja'),
      notifications: Joi.object({
        email: Joi.boolean(),
        push: Joi.boolean(),
        sms: Joi.boolean()
      }),
      timezone: Joi.string()
    });

    const result = preferencesSchema.validate(preferences);
    return {
      isValid: !result.error,
      errors: result.error?.details.map(detail => ({
        field: detail.path.join('.'),
        message: detail.message,
        code: detail.type
      })) || []
    };
  }
}