import express from 'express';
import { securityHeaders, corsOptions, requestId, securityAudit } from './middleware/security';
import { RateLimitConfig } from './middleware/rate-limit-config';
import authRoutes from './routes/auth';

const app = express();
const rateLimitConfig = new RateLimitConfig();

// Security middleware (순서 중요)
app.use(securityHeaders);
app.use(corsOptions);
app.use(requestId);
app.use(securityAudit);

// Rate limiting
app.use(rateLimitConfig.ipBasedLimiter);

// Body parsing
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    requestId: req.id
  });
});

// Routes
app.use('/api/auth', authRoutes);

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    error: 'Not Found',
    path: req.originalUrl,
    requestId: req.id
  });
});

// Error handler
app.use((err: any, req: any, res: any, next: any) => {
  console.error('Error:', err);
  
  res.status(err.status || 500).json({
    error: process.env.NODE_ENV === 'production' ? 'Internal Server Error' : err.message,
    requestId: req.id
  });
});

export default app;