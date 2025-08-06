import app from './app';

const PORT = process.env.PORT || 3002;

const server = app.listen(PORT, () => {
  console.log(`🚀 T-Developer API 서버 시작됨: http://localhost:${PORT}`);
  console.log(`📊 헬스 체크: http://localhost:${PORT}/health`);
  console.log(`📈 메트릭: http://localhost:${PORT}/metrics`);
  console.log(`🔍 Jaeger UI: http://localhost:16686`);
});

// 우아한 종료
process.on('SIGTERM', () => {
  console.log('SIGTERM 신호 수신, 서버 종료 중...');
  server.close(() => {
    console.log('서버가 종료되었습니다.');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  console.log('SIGINT 신호 수신, 서버 종료 중...');
  server.close(() => {
    console.log('서버가 종료되었습니다.');
    process.exit(0);
  });
});

export default server;