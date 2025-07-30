import { Router, Request, Response } from 'express';
import { AuthManager } from './auth-manager';
import { OAuthProvider } from './oauth-provider';
import { RBACManager } from './rbac-manager';
import { SecurityMiddleware } from './security-middleware';

const router = Router();
const authManager = new AuthManager();
const oauthProvider = new OAuthProvider({
  userPoolId: process.env.COGNITO_USER_POOL_ID || '',
  clientId: process.env.COGNITO_CLIENT_ID || '',
  region: process.env.AWS_REGION || 'us-east-1'
});
const rbacManager = new RBACManager();
const security = new SecurityMiddleware();

// Mock user store (in production, use database)
const users = new Map([
  ['admin@example.com', {
    id: 'user_1',
    email: 'admin@example.com',
    password: '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/VcSAg/9qm', // 'password123'
    role: 'admin' as const,
    permissions: ['project:read', 'project:write', 'project:delete', 'agent:execute', 'agent:monitor', 'user:manage', 'system:admin']
  }],
  ['user@example.com', {
    id: 'user_2',
    email: 'user@example.com',
    password: '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/VcSAg/9qm', // 'password123'
    role: 'user' as const,
    permissions: ['project:read', 'project:write', 'agent:execute']
  }]
]);

// Initialize user roles
rbacManager.assignRole('user_1', 'admin');
rbacManager.assignRole('user_2', 'user');

// Login endpoint
router.post('/login', security.rateLimiter({ windowMs: 15 * 60 * 1000, max: 5 }), async (req: Request, res: Response) => {
  try {
    const { email, password } = req.body;
    
    if (!email || !password) {
      return res.status(400).json({ error: 'Email and password required' });
    }
    
    const user = users.get(email);
    if (!user) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    const isValidPassword = await authManager.verifyPassword(password, user.password);
    if (!isValidPassword) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    const tokens = authManager.generateTokens(user);
    
    res.json({
      user: {
        id: user.id,
        email: user.email,
        role: user.role,
        permissions: user.permissions
      },
      tokens
    });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ error: 'Login failed' });
  }
});

// OAuth login
router.post('/oauth/cognito', async (req: Request, res: Response) => {
  try {
    const { username, password } = req.body;
    
    const oauthUser = await oauthProvider.authenticateWithCognito(username, password);
    
    // Create or get user
    const user = {
      id: oauthUser.id,
      email: oauthUser.email,
      role: 'user' as const,
      permissions: ['project:read', 'project:write', 'agent:execute']
    };
    
    const tokens = authManager.generateTokens(user);
    
    res.json({
      user,
      tokens
    });
  } catch (error) {
    console.error('OAuth error:', error);
    res.status(401).json({ error: 'OAuth authentication failed' });
  }
});

// Get current user
router.get('/me', security.authenticate(), (req: Request, res: Response) => {
  const userPermissions = rbacManager.getUserPermissions(req.user!.userId);
  const userRoles = rbacManager.getUserRoles(req.user!.userId);
  
  res.json({
    user: req.user,
    permissions: userPermissions,
    roles: userRoles
  });
});

// Refresh token
router.post('/refresh', (req: Request, res: Response) => {
  try {
    const { refreshToken } = req.body;
    
    if (!refreshToken) {
      return res.status(400).json({ error: 'Refresh token required' });
    }
    
    const payload = authManager.verifyToken(refreshToken);
    const user = users.get(payload.email);
    
    if (!user) {
      return res.status(401).json({ error: 'Invalid refresh token' });
    }
    
    const tokens = authManager.generateTokens(user);
    
    res.json({ tokens });
  } catch (error) {
    res.status(401).json({ error: 'Invalid refresh token' });
  }
});

// Logout
router.post('/logout', security.authenticate(), (req: Request, res: Response) => {
  // In a real implementation, you would blacklist the token
  res.json({ message: 'Logged out successfully' });
});

// Get roles (admin only)
router.get('/roles', security.authenticate(), security.authorize(['user:manage']), (req: Request, res: Response) => {
  const roles = rbacManager.getAllRoles();
  res.json({ roles });
});

// Get permissions (admin only)
router.get('/permissions', security.authenticate(), security.authorize(['user:manage']), (req: Request, res: Response) => {
  const permissions = rbacManager.getAllPermissions();
  res.json({ permissions });
});

export default router;