export abstract class BaseError extends Error {
  abstract statusCode: number;
  abstract code: string;

  constructor(message: string) {
    super(message);
    Object.setPrototypeOf(this, BaseError.prototype);
  }

  abstract serializeErrors(): { message: string; field?: string }[];
}

export class NotFoundError extends BaseError {
  statusCode = 404;
  code = 'NOT_FOUND';

  constructor(public resource: string) {
    super(`Resource not found: ${resource}`);
    Object.setPrototypeOf(this, NotFoundError.prototype);
  }

  serializeErrors() {
    return [{ message: this.message }];
  }
}

export class ValidationError extends BaseError {
  statusCode = 400;
  code = 'VALIDATION_ERROR';

  constructor(public errors: Array<{ field: string; message: string }>) {
    super('Validation failed');
    Object.setPrototypeOf(this, ValidationError.prototype);
  }

  serializeErrors() {
    return this.errors;
  }
}

export class AgentError extends BaseError {
  statusCode = 500;
  code = 'AGENT_ERROR';

  constructor(public agentName: string, message: string) {
    super(`Agent ${agentName} error: ${message}`);
    Object.setPrototypeOf(this, AgentError.prototype);
  }

  serializeErrors() {
    return [{ message: this.message, field: 'agent' }];
  }
}
