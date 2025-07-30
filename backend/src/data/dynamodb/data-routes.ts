import { Router, Request, Response } from 'express';
import { SingleTableDesign, DynamoDBQueryOptimizer, TransactionManager } from './index';
import { SecurityMiddleware } from '../../security/security-middleware';

const router = Router();
const security = new SecurityMiddleware();

// Mock data for testing
let singleTable: SingleTableDesign;
let queryOptimizer: DynamoDBQueryOptimizer;
let transactionManager: TransactionManager;

// Initialize with DI
export function initializeDataRoutes(
  table: SingleTableDesign,
  optimizer: DynamoDBQueryOptimizer,
  txManager: TransactionManager
) {
  singleTable = table;
  queryOptimizer = optimizer;
  transactionManager = txManager;
  return router;
}

// Create item
router.post('/items', security.authenticate(), security.authorize(['project:write']), async (req: Request, res: Response) => {
  try {
    const { entityType, entityId, data } = req.body;
    
    if (!entityType || !entityId || !data) {
      return res.status(400).json({ error: 'entityType, entityId, and data are required' });
    }
    
    const keys = singleTable.generateKeys(entityType, entityId);
    const gsiKeys = singleTable.generateGSIKeys({
      ...data,
      entityType,
      userId: req.user?.userId
    });
    
    const item = {
      ...keys,
      ...gsiKeys,
      entityType,
      data,
      createdBy: req.user?.userId
    };
    
    await singleTable.putItem(item);
    
    res.json({
      success: true,
      item: {
        entityType,
        entityId,
        keys
      }
    });
  } catch (error: any) {
    console.error('Create item error:', error);
    res.status(500).json({ error: 'Failed to create item' });
  }
});

// Get item
router.get('/items/:entityType/:entityId', security.authenticate(), security.authorize(['project:read']), async (req: Request, res: Response) => {
  try {
    const { entityType, entityId } = req.params;
    const keys = singleTable.generateKeys(entityType, entityId);
    
    const item = await singleTable.getItem(keys);
    
    if (!item) {
      return res.status(404).json({ error: 'Item not found' });
    }
    
    res.json({
      success: true,
      item
    });
  } catch (error: any) {
    console.error('Get item error:', error);
    res.status(500).json({ error: 'Failed to get item' });
  }
});

// Update item
router.put('/items/:entityType/:entityId', security.authenticate(), security.authorize(['project:write']), async (req: Request, res: Response) => {
  try {
    const { entityType, entityId } = req.params;
    const { data } = req.body;
    
    if (!data) {
      return res.status(400).json({ error: 'data is required' });
    }
    
    const keys = singleTable.generateKeys(entityType, entityId);
    await singleTable.updateItem(keys, { data });
    
    res.json({
      success: true,
      message: 'Item updated successfully'
    });
  } catch (error: any) {
    console.error('Update item error:', error);
    res.status(500).json({ error: 'Failed to update item' });
  }
});

// Delete item
router.delete('/items/:entityType/:entityId', security.authenticate(), security.authorize(['project:delete']), async (req: Request, res: Response) => {
  try {
    const { entityType, entityId } = req.params;
    const keys = singleTable.generateKeys(entityType, entityId);
    
    await singleTable.deleteItem(keys);
    
    res.json({
      success: true,
      message: 'Item deleted successfully'
    });
  } catch (error: any) {
    console.error('Delete item error:', error);
    res.status(500).json({ error: 'Failed to delete item' });
  }
});

// Get user items
router.get('/users/:userId/items', security.authenticate(), security.authorize(['project:read']), async (req: Request, res: Response) => {
  try {
    const { userId } = req.params;
    const { entityType } = req.query;
    
    // Check if user can access other user's data
    if (userId !== req.user?.userId && req.user?.role !== 'admin') {
      return res.status(403).json({ error: 'Access denied' });
    }
    
    const items = await singleTable.getItemsByUser(userId, entityType as string);
    
    res.json({
      success: true,
      items,
      count: items.length
    });
  } catch (error: any) {
    console.error('Get user items error:', error);
    res.status(500).json({ error: 'Failed to get user items' });
  }
});

// Execute transaction
router.post('/transactions', security.authenticate(), security.authorize(['project:write']), async (req: Request, res: Response) => {
  try {
    const { items } = req.body;
    
    if (!Array.isArray(items) || items.length === 0) {
      return res.status(400).json({ error: 'items array is required' });
    }
    
    await transactionManager.executeTransaction(items);
    
    res.json({
      success: true,
      message: 'Transaction executed successfully',
      itemCount: items.length
    });
  } catch (error: any) {
    console.error('Transaction error:', error);
    res.status(500).json({ error: 'Transaction failed' });
  }
});

export default router;