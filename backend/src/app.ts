import express from 'express';
import { setupHMRMiddleware } from './dev/hot-reload';
import { securityHeaders, corsOptions, requestId, securityAudit } from './middleware/security';
import { RateLimiter } from './middleware/rate-limiter';
import { AuthMiddleware } from './middleware/auth';

const app = express();

// Security middleware
app.use(securityHeaders);
app.use(corsOptions);
app.use(requestId);
app.use(securityAudit);

// Rate limiting
const rateLimiter = new RateLimiter();
const limits = rateLimiter.apiLimits();
app.use('/api/auth', limits.auth);
app.use('/api/create', limits.create);
app.use('/api/ai', limits.ai);
app.use('/api', limits.general);

// Body parsing
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// HMR in development
if (process.env.NODE_ENV === 'development') {
  setupHMRMiddleware(app);
}

// Health check
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV,
    hmr: process.env.NODE_ENV === 'development' ? 'enabled' : 'disabled'
  });
});

// API routes
const authMiddleware = new AuthMiddleware();
app.use('/api/auth', authMiddleware.authenticate.bind(authMiddleware));

export default app;