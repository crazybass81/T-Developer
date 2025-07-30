export interface Role {
  id: string;
  name: string;
  permissions: string[];
  description?: string;
}

export interface Permission {
  id: string;
  name: string;
  resource: string;
  action: string;
  description?: string;
}

export class RBACManager {
  private roles: Map<string, Role> = new Map();
  private permissions: Map<string, Permission> = new Map();
  private userRoles: Map<string, string[]> = new Map();
  
  constructor() {
    this.initializeDefaultRoles();
  }
  
  // Initialize default roles and permissions
  private initializeDefaultRoles(): void {
    // Define permissions
    const permissions: Permission[] = [
      { id: 'project:read', name: 'Read Projects', resource: 'project', action: 'read' },
      { id: 'project:write', name: 'Write Projects', resource: 'project', action: 'write' },
      { id: 'project:delete', name: 'Delete Projects', resource: 'project', action: 'delete' },
      { id: 'agent:execute', name: 'Execute Agents', resource: 'agent', action: 'execute' },
      { id: 'agent:monitor', name: 'Monitor Agents', resource: 'agent', action: 'monitor' },
      { id: 'user:manage', name: 'Manage Users', resource: 'user', action: 'manage' },
      { id: 'system:admin', name: 'System Admin', resource: 'system', action: 'admin' }
    ];
    
    permissions.forEach(permission => {
      this.permissions.set(permission.id, permission);
    });
    
    // Define roles
    const roles: Role[] = [
      {
        id: 'user',
        name: 'User',
        permissions: ['project:read', 'project:write', 'agent:execute'],
        description: 'Standard user with basic project access'
      },
      {
        id: 'developer',
        name: 'Developer',
        permissions: ['project:read', 'project:write', 'project:delete', 'agent:execute', 'agent:monitor'],
        description: 'Developer with full project access'
      },
      {
        id: 'admin',
        name: 'Administrator',
        permissions: ['project:read', 'project:write', 'project:delete', 'agent:execute', 'agent:monitor', 'user:manage', 'system:admin'],
        description: 'Full system administrator'
      }
    ];
    
    roles.forEach(role => {
      this.roles.set(role.id, role);
    });
  }
  
  // Assign role to user
  assignRole(userId: string, roleId: string): void {
    if (!this.roles.has(roleId)) {
      throw new Error(`Role not found: ${roleId}`);
    }
    
    const userRoles = this.userRoles.get(userId) || [];
    if (!userRoles.includes(roleId)) {
      userRoles.push(roleId);
      this.userRoles.set(userId, userRoles);
    }
  }
  
  // Remove role from user
  removeRole(userId: string, roleId: string): void {
    const userRoles = this.userRoles.get(userId) || [];
    const index = userRoles.indexOf(roleId);
    
    if (index > -1) {
      userRoles.splice(index, 1);
      this.userRoles.set(userId, userRoles);
    }
  }
  
  // Get user roles
  getUserRoles(userId: string): Role[] {
    const roleIds = this.userRoles.get(userId) || [];
    return roleIds.map(roleId => this.roles.get(roleId)!).filter(Boolean);
  }
  
  // Get user permissions
  getUserPermissions(userId: string): string[] {
    const roles = this.getUserRoles(userId);
    const permissions = new Set<string>();
    
    roles.forEach(role => {
      role.permissions.forEach(permission => {
        permissions.add(permission);
      });
    });
    
    return Array.from(permissions);
  }
  
  // Check if user has permission
  hasPermission(userId: string, permission: string): boolean {
    const userPermissions = this.getUserPermissions(userId);
    return userPermissions.includes(permission) || this.isAdmin(userId);
  }
  
  // Check if user is admin
  isAdmin(userId: string): boolean {
    const roles = this.getUserRoles(userId);
    return roles.some(role => role.id === 'admin');
  }
  
  // Create custom role
  createRole(role: Omit<Role, 'id'>): string {
    const id = `custom_${Date.now()}`;
    const newRole: Role = { ...role, id };
    
    // Validate permissions exist
    const invalidPermissions = role.permissions.filter(p => !this.permissions.has(p));
    if (invalidPermissions.length > 0) {
      throw new Error(`Invalid permissions: ${invalidPermissions.join(', ')}`);
    }
    
    this.roles.set(id, newRole);
    return id;
  }
  
  // Create custom permission
  createPermission(permission: Omit<Permission, 'id'>): string {
    const id = `${permission.resource}:${permission.action}`;
    const newPermission: Permission = { ...permission, id };
    
    this.permissions.set(id, newPermission);
    return id;
  }
  
  // Get all roles
  getAllRoles(): Role[] {
    return Array.from(this.roles.values());
  }
  
  // Get all permissions
  getAllPermissions(): Permission[] {
    return Array.from(this.permissions.values());
  }
}