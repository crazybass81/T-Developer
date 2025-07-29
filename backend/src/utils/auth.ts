import jwt from 'jsonwebtoken';
import bcrypt from 'bcrypt';

export interface TokenPayload {
  userId: string;
  email: string;
  role: 'user' | 'admin';
}

export class AuthManager {
  private readonly accessTokenSecret: string;
  private readonly refreshTokenSecret: string;
  private readonly accessTokenExpiry = '15m';
  private readonly refreshTokenExpiry = '7d';
  
  constructor() {
    this.accessTokenSecret = process.env.JWT_ACCESS_SECRET || 'dev-access-secret';
    this.refreshTokenSecret = process.env.JWT_REFRESH_SECRET || 'dev-refresh-secret';
    
    if (process.env.NODE_ENV === 'production' && this.accessTokenSecret === 'dev-access-secret') {
      throw new Error('JWT secrets must be set in production');
    }
  }
  
  async generateTokens(payload: TokenPayload): Promise<{
    accessToken: string;
    refreshToken: string;
  }> {
    const accessToken = jwt.sign(payload, this.accessTokenSecret, {
      expiresIn: this.accessTokenExpiry,
      issuer: 't-developer',
      audience: 'api'
    });
    
    const refreshToken = jwt.sign(
      { userId: payload.userId }, 
      this.refreshTokenSecret, 
      {
        expiresIn: this.refreshTokenExpiry,
        issuer: 't-developer',
        audience: 'refresh'
      }
    );
    
    return { accessToken, refreshToken };
  }
  
  async verifyAccessToken(token: string): Promise<TokenPayload> {
    try {
      return jwt.verify(token, this.accessTokenSecret, {
        issuer: 't-developer',
        audience: 'api'
      }) as TokenPayload;
    } catch (error) {
      throw new Error('Invalid access token');
    }
  }
  
  async verifyRefreshToken(token: string): Promise<{ userId: string }> {
    try {
      return jwt.verify(token, this.refreshTokenSecret, {
        issuer: 't-developer',
        audience: 'refresh'
      }) as { userId: string };
    } catch (error) {
      throw new Error('Invalid refresh token');
    }
  }
  
  async hashPassword(password: string): Promise<string> {
    return bcrypt.hash(password, 12);
  }
  
  async verifyPassword(password: string, hash: string): Promise<boolean> {
    return bcrypt.compare(password, hash);
  }
}