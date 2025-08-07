/**
 * User Routes
 * Phase 1: User API endpoints routing
 */

import { Router } from 'express';
import { userController } from '../../controllers/user.controller';

const router = Router();

// User CRUD routes
router.post('/', userController.createUser);
router.get('/', userController.listUsers);
router.get('/profile', userController.getUserProfile);
router.get('/:id', userController.getUser);
router.put('/:id', userController.updateUser);
router.delete('/:id', userController.deleteUser);

export const userRoutes = router;