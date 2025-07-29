import { NodeTracerProvider } from '@opentelemetry/sdk-trace-node';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';
import { JaegerExporter } from '@opentelemetry/exporter-jaeger';
import { BatchSpanProcessor } from '@opentelemetry/sdk-trace-base';
import { registerInstrumentations } from '@opentelemetry/instrumentation';
import { HttpInstrumentation } from '@opentelemetry/instrumentation-http';
import { ExpressInstrumentation } from '@opentelemetry/instrumentation-express';
import { trace, context, SpanStatusCode } from '@opentelemetry/api';
import { Request, Response, NextFunction } from 'express';

const provider = new NodeTracerProvider({
  resource: new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: 't-developer',
    [SemanticResourceAttributes.SERVICE_VERSION]: process.env.npm_package_version || '1.0.0',
    [SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: process.env.NODE_ENV || 'development'
  })
});

const jaegerExporter = new JaegerExporter({
  endpoint: process.env.JAEGER_ENDPOINT || 'http://localhost:14268/api/traces'
});

provider.addSpanProcessor(new BatchSpanProcessor(jaegerExporter));
provider.register();

registerInstrumentations({
  instrumentations: [
    new HttpInstrumentation(),
    new ExpressInstrumentation()
  ]
});

export const tracer = trace.getTracer('t-developer', '1.0.0');

export class TracingHelper {
  static async traceAgentExecution<T>(
    agentName: string,
    projectId: string,
    operation: () => Promise<T>
  ): Promise<T> {
    return tracer.startActiveSpan(`agent.${agentName}.execute`, async (span) => {
      span.setAttributes({
        'agent.name': agentName,
        'project.id': projectId,
        'agent.start_time': new Date().toISOString()
      });
      
      try {
        const result = await operation();
        span.setStatus({ code: SpanStatusCode.OK });
        span.setAttributes({
          'agent.success': true,
          'agent.end_time': new Date().toISOString()
        });
        return result;
      } catch (error) {
        span.recordException(error as Error);
        span.setStatus({
          code: SpanStatusCode.ERROR,
          message: error instanceof Error ? error.message : 'Unknown error'
        });
        throw error;
      } finally {
        span.end();
      }
    });
  }
  
  static async traceExternalCall<T>(
    serviceName: string,
    endpoint: string,
    operation: () => Promise<T>
  ): Promise<T> {
    return tracer.startActiveSpan(`external.${serviceName}`, async (span) => {
      span.setAttributes({
        'external.service': serviceName,
        'external.endpoint': endpoint,
        'external.timestamp': new Date().toISOString()
      });
      
      try {
        const result = await operation();
        span.setStatus({ code: SpanStatusCode.OK });
        return result;
      } catch (error) {
        span.recordException(error as Error);
        span.setStatus({
          code: SpanStatusCode.ERROR,
          message: error instanceof Error ? error.message : 'Unknown error'
        });
        throw error;
      } finally {
        span.end();
      }
    });
  }
  
  static async traceDatabaseOperation<T>(
    operation: string,
    table: string,
    query: () => Promise<T>
  ): Promise<T> {
    return tracer.startActiveSpan(`db.${operation}`, async (span) => {
      span.setAttributes({
        'db.operation': operation,
        'db.table': table,
        'db.system': 'dynamodb'
      });
      
      const startTime = Date.now();
      
      try {
        const result = await query();
        const duration = Date.now() - startTime;
        
        span.setAttributes({
          'db.duration_ms': duration,
          'db.success': true
        });
        span.setStatus({ code: SpanStatusCode.OK });
        
        return result;
      } catch (error) {
        span.recordException(error as Error);
        span.setStatus({
          code: SpanStatusCode.ERROR,
          message: error instanceof Error ? error.message : 'Unknown error'
        });
        throw error;
      } finally {
        span.end();
      }
    });
  }
}

export function tracingMiddleware() {
  return (req: Request, res: Response, next: NextFunction) => {
    const span = tracer.startSpan(`http ${req.method} ${req.path}`);
    
    context.with(trace.setSpan(context.active(), span), () => {
      span.setAttributes({
        'http.request_id': req.requestId,
        'http.user_agent': req.headers['user-agent'] || 'unknown'
      });
      
      res.on('finish', () => {
        span.setAttributes({
          'http.status_code': res.statusCode,
          'http.response_size': res.get('content-length') || 0
        });
        span.setStatus({
          code: res.statusCode >= 400 ? SpanStatusCode.ERROR : SpanStatusCode.OK
        });
        span.end();
      });
      
      next();
    });
  };
}