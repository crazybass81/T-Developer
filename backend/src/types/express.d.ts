/**
 * Express Type Definitions
 * Extend Express Request interface
 */

import { User } from '@prisma/client';

declare global {
  namespace Express {
    interface Request {
      user?: User;
    }
  }
}