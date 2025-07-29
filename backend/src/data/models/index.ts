// backend/src/data/models/index.ts
export interface BaseModel {
  id: string;
  createdAt: string;
  updatedAt: string;
}

export interface Project extends BaseModel {
  name: string;
  description: string;
  userId: string;
  status: 'analyzing' | 'building' | 'completed' | 'error';
  requirements?: any;
  components?: any[];
  metadata?: Record<string, any>;
}

export interface Agent extends BaseModel {
  name: string;
  type: string;
  status: 'idle' | 'busy' | 'error';
  capabilities: string[];
  metadata?: Record<string, any>;
}

export interface User extends BaseModel {
  email: string;
  name: string;
  role: 'user' | 'admin';
  preferences?: Record<string, any>;
}
