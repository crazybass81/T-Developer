import express, { Express } from 'express';
import { Server } from 'http';
import { AddressInfo } from 'net';

export class TestServer {
  private app: Express;
  private server?: Server;
  
  constructor() {
    this.app = express();
    this.setupMiddleware();
  }
  
  private setupMiddleware(): void {
    this.app.use(express.json());
    this.app.use(express.urlencoded({ extended: true }));
  }
  
  async start(): Promise<number> {
    return new Promise((resolve) => {
      this.server = this.app.listen(0, () => {
        const port = (this.server!.address() as AddressInfo).port;
        resolve(port);
      });
    });
  }
  
  async stop(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.server) {
        this.server.close((err) => {
          if (err) reject(err);
          else resolve();
        });
      } else {
        resolve();
      }
    });
  }
  
  getApp(): Express {
    return this.app;
  }
  
  getUrl(port: number): string {
    return `http://localhost:${port}`;
  }
}

// API 테스트 클라이언트
export class TestClient {
  constructor(private baseURL: string) {}
  
  async get(path: string, headers?: Record<string, string>) {
    const response = await fetch(`${this.baseURL}${path}`, {
      method: 'GET',
      ...(headers && { headers })
    });
    
    let body;
    try {
      body = await response.json();
    } catch {
      body = await response.text();
    }
    
    return {
      status: response.status,
      body
    };
  }
  
  async post(path: string, data?: any, headers?: Record<string, string>) {
    const response = await fetch(`${this.baseURL}${path}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...headers
      },
      body: JSON.stringify(data)
    });
    
    let body;
    try {
      body = await response.json();
    } catch {
      body = await response.text();
    }
    
    return {
      status: response.status,
      body
    };
  }
}