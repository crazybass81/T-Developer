import { Router } from 'express';
import { authController } from '../../controllers/auth.controller';
import { authenticate } from '../../middlewares/auth.middleware';
import { rateLimiter } from '../../middlewares/rateLimiter';

const router = Router();

// Public routes
router.post('/register', rateLimiter('register'), authController.register);
router.post('/login', rateLimiter('login'), authController.login);
router.post('/refresh-token', authController.refreshToken);

// Protected routes
router.use(authenticate);
router.post('/logout', authController.logout);
router.get('/me', authController.getCurrentUser);
router.put('/password', authController.updatePassword);

export const authRoutes = router;