import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import cors from 'cors';
import { logger, metrics } from './utils/monitoring';

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, {
  cors: {
    origin: "http://localhost:3000",
    methods: ["GET", "POST"]
  }
});

// 미들웨어
app.use(cors());
app.use(express.json());

// 헬스 체크
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    services: {
      api: 'running',
      websocket: 'running',
      database: 'pending'
    }
  });
});

// WebSocket 연결
io.on('connection', (socket) => {
  logger.info('Client connected', { socketId: socket.id });
  metrics.increment('websocket.connections');
  
  socket.on('disconnect', () => {
    logger.info('Client disconnected', { socketId: socket.id });
    metrics.increment('websocket.disconnections');
  });
});

const PORT = process.env.PORT || 3002;
httpServer.listen(PORT, () => {
  logger.info(`Development server started on port ${PORT}`);
  console.log(`✅ 개발 서버 실행 중: http://localhost:${PORT}`);
  console.log(`📡 WebSocket 서버 실행 중: ws://localhost:${PORT}`);
  metrics.increment('server.started');
});