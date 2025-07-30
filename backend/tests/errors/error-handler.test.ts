import { ErrorHandler, AppError, ErrorCode } from '../../src/errors/error-handler';

describe('ErrorHandler', () => {
  let mockReq: any;
  let mockRes: any;
  let mockNext: jest.Mock;

  beforeEach(() => {
    mockReq = { url: '/test', method: 'GET' };
    mockRes = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };
    mockNext = jest.fn();
  });

  test('handles operational errors', () => {
    const error = new AppError('Test error', ErrorCode.VALIDATION_ERROR, 400);
    
    ErrorHandler.handle(error, mockReq, mockRes, mockNext);
    
    expect(mockRes.status).toHaveBeenCalledWith(400);
    expect(mockRes.json).toHaveBeenCalledWith({
      success: false,
      error: {
        code: ErrorCode.VALIDATION_ERROR,
        message: 'Test error'
      }
    });
  });

  test('creates errors with correct status codes', () => {
    const error = ErrorHandler.createError(ErrorCode.AUTHENTICATION_ERROR, 'Auth failed');
    
    expect(error.code).toBe(ErrorCode.AUTHENTICATION_ERROR);
    expect(error.statusCode).toBe(401);
    expect(error.message).toBe('Auth failed');
  });
});