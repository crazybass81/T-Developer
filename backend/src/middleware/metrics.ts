import { Request, Response, NextFunction } from 'express';
import { metrics, MetricsHelper } from '../config/metrics';

// 메트릭 수집 미들웨어
export function collectMetrics(req: Request, res: Response, next: NextFunction): void {
  const start = Date.now();
  
  // 응답 완료 시 메트릭 기록
  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    const route = req.route?.path || req.path;
    
    // HTTP 메트릭 기록
    const labels = {
      method: req.method,
      route: route.replace(/\/:\w+/g, '/:id'), // 파라미터 정규화
      status_code: res.statusCode.toString()
    };
    
    metrics.httpRequestDuration.observe(labels, duration);
    metrics.httpRequestTotal.inc(labels);
    
    // API 키 사용량 추적
    if (req.headers.authorization) {
      const userId = (req as any).user?.id || 'anonymous';
      metrics.apiKeyUsage.inc({
        user_id: userId,
        endpoint: route
      });
    }
  });
  
  next();
}

// 에이전트 메트릭 데코레이터
export function trackAgentExecution(agentName: string) {
  return function(target: any, propertyName: string, descriptor: PropertyDescriptor) {
    const method = descriptor.value;
    
    descriptor.value = async function(...args: any[]) {
      const start = Date.now();
      let status: 'success' | 'failure' = 'success';
      
      try {
        const result = await method.apply(this, args);
        return result;
      } catch (error) {
        status = 'failure';
        throw error;
      } finally {
        const duration = (Date.now() - start) / 1000;
        MetricsHelper.recordAgentExecution(agentName, duration, status);
      }
    };
    
    return descriptor;
  };
}

// 프로젝트 생성 추적
export function trackProjectCreation(projectType: string) {
  return function(target: any, propertyName: string, descriptor: PropertyDescriptor) {
    const method = descriptor.value;
    
    descriptor.value = async function(...args: any[]) {
      const start = Date.now();
      let status: 'success' | 'failure' = 'success';
      
      try {
        const result = await method.apply(this, args);
        return result;
      } catch (error) {
        status = 'failure';
        throw error;
      } finally {
        const duration = (Date.now() - start) / 1000;
        MetricsHelper.recordProjectCreation(projectType, duration, status);
      }
    };
    
    return descriptor;
  };
}