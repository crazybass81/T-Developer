import { initializeConfig } from './config';

async function bootstrap() {
  // AWS에서 설정 로드
  await initializeConfig();
  
  // 애플리케이션 시작
  const app = await import('./app');
  await app.start();
}

bootstrap().catch(console.error);