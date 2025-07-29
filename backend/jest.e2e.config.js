module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/tests/e2e'],
  testMatch: ['**/*.e2e.test.ts'],
  transform: {
    '^.+\\.ts$': 'ts-jest'
  },
  testTimeout: 60000, // 60초 타임아웃 (Docker 컨테이너 시작 시간 고려)
  maxWorkers: 1, // E2E 테스트는 순차 실행
  setupFilesAfterEnv: ['<rootDir>/tests/setup.ts'],
  clearMocks: true,
  restoreMocks: true,
  verbose: true
};