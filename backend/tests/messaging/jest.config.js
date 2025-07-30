// Jest configuration for messaging tests
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>'],
  testMatch: ['**/*.test.ts'],
  setupFilesAfterEnv: ['<rootDir>/setup.ts'],
  collectCoverageFrom: [
    '../../src/messaging/**/*.ts',
    '!../../src/messaging/**/*.d.ts'
  ],
  coverageDirectory: '../coverage/messaging',
  coverageReporters: ['text', 'lcov', 'html'],
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/../../src/$1'
  }
};