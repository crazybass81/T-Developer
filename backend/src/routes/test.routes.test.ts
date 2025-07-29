import request from 'supertest';
import express from 'express';
import testRouter from './testing';

const app = express();
app.use(express.json());
app.use('/test', testRouter);

describe('Test Routes', () => {
  it('should execute agent', async () => {
    const response = await request(app)
      .get('/test/agent/test-agent?projectId=test-project')
      .expect(200);
    
    expect(response.body).toHaveProperty('agentName', 'test-agent');
    expect(response.body).toHaveProperty('projectId', 'test-project');
  });

  it('should call bedrock', async () => {
    const response = await request(app)
      .get('/test/bedrock')
      .expect(200);
    
    expect(response.body).toHaveProperty('model', 'claude-3');
    expect(response.body).toHaveProperty('response');
  });

  it('should query dynamodb', async () => {
    const response = await request(app)
      .get('/test/db')
      .expect(200);
    
    expect(response.body).toHaveProperty('table', 'test-table');
    expect(response.body).toHaveProperty('data');
  });
});