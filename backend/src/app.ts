import express from 'express';
import cors from 'cors';
import { APISecurityMiddleware, DynamicRateLimiter } from './security/api-security';
import projectsRouter from './routes/projects';
import agentsRouter from './routes/agents';
import secureDataRouter from './routes/secure-data.example';

const app = express();

// Basic middleware
app.use(express.json());
app.use(cors());

// Security middleware
app.use('/api', APISecurityMiddleware.securityHeaders());
app.use('/api', DynamicRateLimiter.middleware());

// Protected routes
app.use('/api/protected', APISecurityMiddleware.apiKeyAuth(['projects:read']));

// Health check (public)
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Route handlers
app.use('/api/projects', projectsRouter);
app.use('/api/agents', agentsRouter);
app.use('/api/secure', secureDataRouter);

const PORT = process.env.PORT || 8000;
app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
});

export default app;