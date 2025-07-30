import { RBACManager } from '../../src/security/rbac-manager';

describe('RBACManager', () => {
  let rbacManager: RBACManager;
  
  beforeEach(() => {
    rbacManager = new RBACManager();
  });
  
  describe('Role Management', () => {
    test('should assign role to user', () => {
      rbacManager.assignRole('user123', 'user');
      
      const roles = rbacManager.getUserRoles('user123');
      expect(roles).toHaveLength(1);
      expect(roles[0].id).toBe('user');
    });
    
    test('should remove role from user', () => {
      rbacManager.assignRole('user123', 'user');
      rbacManager.removeRole('user123', 'user');
      
      const roles = rbacManager.getUserRoles('user123');
      expect(roles).toHaveLength(0);
    });
    
    test('should get user permissions', () => {
      rbacManager.assignRole('user123', 'user');
      
      const permissions = rbacManager.getUserPermissions('user123');
      expect(permissions).toContain('project:read');
      expect(permissions).toContain('project:write');
      expect(permissions).toContain('agent:execute');
    });
  });
  
  describe('Permission Checking', () => {
    test('should check user permission correctly', () => {
      rbacManager.assignRole('user123', 'user');
      
      expect(rbacManager.hasPermission('user123', 'project:read')).toBe(true);
      expect(rbacManager.hasPermission('user123', 'user:manage')).toBe(false);
    });
    
    test('should recognize admin permissions', () => {
      rbacManager.assignRole('admin123', 'admin');
      
      expect(rbacManager.hasPermission('admin123', 'user:manage')).toBe(true);
      expect(rbacManager.isAdmin('admin123')).toBe(true);
    });
  });
  
  describe('Custom Roles', () => {
    test('should create custom role', () => {
      const roleId = rbacManager.createRole({
        name: 'Custom Role',
        permissions: ['project:read'],
        description: 'Test custom role'
      });
      
      expect(roleId).toBeDefined();
      expect(roleId.startsWith('custom_')).toBe(true);
      
      const roles = rbacManager.getAllRoles();
      const customRole = roles.find(r => r.id === roleId);
      expect(customRole).toBeDefined();
      expect(customRole?.name).toBe('Custom Role');
    });
    
    test('should create custom permission', () => {
      const permissionId = rbacManager.createPermission({
        name: 'Custom Permission',
        resource: 'custom',
        action: 'test',
        description: 'Test custom permission'
      });
      
      expect(permissionId).toBe('custom:test');
      
      const permissions = rbacManager.getAllPermissions();
      const customPermission = permissions.find(p => p.id === permissionId);
      expect(customPermission).toBeDefined();
    });
  });
});