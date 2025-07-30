import Joi from 'joi';
import { BaseValidator } from './base.validator';
import { Project, ProjectSettings } from '../models/project.model';

export class ProjectValidator extends BaseValidator<Project> {
  protected schema = Joi.object({
    id: Joi.string().uuid().required(),
    name: Joi.string().min(3).max(100).pattern(/^[a-zA-Z0-9-_\s]+$/).required(),
    description: Joi.string().min(10).max(5000).required(),
    ownerId: Joi.string().uuid().required(),
    status: Joi.string().valid('active', 'archived', 'deleted').required(),
    settings: Joi.object({
      framework: Joi.string().valid('react', 'vue', 'angular', 'svelte', 'nextjs'),
      language: Joi.string().valid('javascript', 'typescript', 'python', 'java', 'go'),
      database: Joi.string().valid('postgres', 'mysql', 'mongodb', 'dynamodb', 'redis'),
      deployment: Joi.object({
        platform: Joi.string().valid('aws', 'vercel', 'netlify', 'heroku'),
        region: Joi.string(),
        autoScale: Joi.boolean().default(false)
      })
    }).default({}),
    progress: Joi.object({
      percentage: Joi.number().min(0).max(100).default(0),
      currentPhase: Joi.string().valid('analysis', 'design', 'development', 'testing', 'deployment'),
      completedTasks: Joi.number().integer().min(0).default(0),
      totalTasks: Joi.number().integer().min(0).default(0)
    }).default({}),
    createdAt: Joi.date().required(),
    updatedAt: Joi.date().required(),
    version: Joi.number().integer().min(1).required()
  });

  validateName(name: string): boolean {
    const nameSchema = Joi.string().min(3).max(100).pattern(/^[a-zA-Z0-9-_\s]+$/);
    return !nameSchema.validate(name).error;
  }

  validateSettings(settings: ProjectSettings): ValidationResult {
    const settingsSchema = Joi.object({
      framework: Joi.string().valid('react', 'vue', 'angular', 'svelte', 'nextjs'),
      language: Joi.string().valid('javascript', 'typescript', 'python', 'java', 'go'),
      database: Joi.string().valid('postgres', 'mysql', 'mongodb', 'dynamodb', 'redis'),
      deployment: Joi.object({
        platform: Joi.string().valid('aws', 'vercel', 'netlify', 'heroku'),
        region: Joi.string(),
        autoScale: Joi.boolean()
      })
    });

    const result = settingsSchema.validate(settings);
    return {
      isValid: !result.error,
      errors: result.error?.details.map(detail => ({
        field: detail.path.join('.'),
        message: detail.message,
        code: detail.type
      })) || []
    };
  }

  validateProgress(percentage: number): boolean {
    return percentage >= 0 && percentage <= 100;
  }
}