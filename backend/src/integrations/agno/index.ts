// Agno 통합 모듈 인덱스
export * from './monitoring-config';

// 기본 설정
export const DEFAULT_AGNO_CONFIG = {
  endpoint: 'https://api.agno.com',
  batchSize: 100,
  flushInterval: 10000, // 10초
  environment: process.env.NODE_ENV || 'development'
};