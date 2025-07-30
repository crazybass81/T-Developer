declare namespace Express {
  interface Request {
    user?: {
      id: string;
      scopes: string[];
      authMethod: 'api_key' | 'hmac' | 'jwt';
      permissions?: string[];
      role?: string;
    };
    id?: string;
  }
}