import { configManager } from './aws-config-manager';

// 애플리케이션 시작 시 AWS에서 설정 로드
export async function initializeConfig(): Promise<void> {
  try {
    await configManager.loadAllConfig();
    console.log('✅ Configuration loaded from AWS');
  } catch (error) {
    console.warn('⚠️ Failed to load AWS config, using local .env:', error);
  }
}

// 설정 값 가져오기 헬퍼 함수
export async function getConfig(key: string): Promise<string> {
  // 먼저 환경변수 확인
  if (process.env[key]) {
    return process.env[key]!;
  }
  
  // AWS Parameter Store에서 가져오기
  const environment = process.env.NODE_ENV || 'development';
  const parameterName = `/t-developer/${environment}/${key.toLowerCase()}`;
  
  return await configManager.getParameter(parameterName);
}

// 민감한 정보 가져오기
export async function getSecret(key: string): Promise<string> {
  const environment = process.env.NODE_ENV || 'development';
  const secrets = await configManager.getSecret(`t-developer/${environment}/secrets`);
  
  return secrets[key] || process.env[key] || '';
}

export { configManager };