import Joi from 'joi';
import { BaseValidator } from './base.validator';
import { Agent, AgentConfiguration, AgentMetrics } from '../models/agent.model';

export class AgentValidator extends BaseValidator<Agent> {
  protected schema = Joi.object({
    id: Joi.string().uuid().required(),
    name: Joi.string().min(3).max(50).required(),
    type: Joi.string().valid(
      'nl-input', 'ui-selection', 'parsing', 'component-decision',
      'matching-rate', 'search', 'generation', 'assembly', 'download'
    ).required(),
    projectId: Joi.string().uuid().required(),
    status: Joi.string().valid('idle', 'running', 'completed', 'failed', 'paused').required(),
    configuration: Joi.object({
      timeout: Joi.number().integer().min(1000).max(300000).default(30000),
      retries: Joi.number().integer().min(0).max(5).default(3),
      priority: Joi.string().valid('low', 'normal', 'high', 'critical').default('normal'),
      resources: Joi.object({
        memory: Joi.number().integer().min(1).max(1024).default(64),
        cpu: Joi.number().min(0.1).max(4).default(1)
      }).default({})
    }).default({}),
    metrics: Joi.object({
      executionCount: Joi.number().integer().min(0).default(0),
      successCount: Joi.number().integer().min(0).default(0),
      failureCount: Joi.number().integer().min(0).default(0),
      averageExecutionTime: Joi.number().min(0).default(0),
      lastExecutionTime: Joi.number().min(0).default(0)
    }).default({}),
    createdAt: Joi.date().required(),
    updatedAt: Joi.date().required(),
    version: Joi.number().integer().min(1).required()
  });

  validateAgentType(type: string): boolean {
    const validTypes = [
      'nl-input', 'ui-selection', 'parsing', 'component-decision',
      'matching-rate', 'search', 'generation', 'assembly', 'download'
    ];
    return validTypes.includes(type);
  }

  validateConfiguration(config: AgentConfiguration): ValidationResult {
    const configSchema = Joi.object({
      timeout: Joi.number().integer().min(1000).max(300000),
      retries: Joi.number().integer().min(0).max(5),
      priority: Joi.string().valid('low', 'normal', 'high', 'critical'),
      resources: Joi.object({
        memory: Joi.number().integer().min(1).max(1024),
        cpu: Joi.number().min(0.1).max(4)
      })
    });

    const result = configSchema.validate(config);
    return {
      isValid: !result.error,
      errors: result.error?.details.map(detail => ({
        field: detail.path.join('.'),
        message: detail.message,
        code: detail.type
      })) || []
    };
  }

  validateMetrics(metrics: AgentMetrics): ValidationResult {
    const metricsSchema = Joi.object({
      executionCount: Joi.number().integer().min(0),
      successCount: Joi.number().integer().min(0),
      failureCount: Joi.number().integer().min(0),
      averageExecutionTime: Joi.number().min(0),
      lastExecutionTime: Joi.number().min(0)
    }).custom((value, helpers) => {
      if (value.successCount + value.failureCount > value.executionCount) {
        return helpers.error('metrics.invalid');
      }
      return value;
    });

    const result = metricsSchema.validate(metrics);
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