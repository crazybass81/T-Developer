#!/usr/bin/env ts-node
import { BedrockClient, ListFoundationModelsCommand } from '@aws-sdk/client-bedrock';

async function checkBedrockAccess() {
  console.log('🔧 Bedrock 모델 액세스 확인 중...');
  
  const client = new BedrockClient({ region: 'us-east-1' });
  
  try {
    const command = new ListFoundationModelsCommand({});
    const response = await (client as any).send(command);
    
    console.log('✅ Bedrock 액세스 확인됨');
    console.log('\n📋 사용 가능한 모델:');
    
    response.modelSummaries?.forEach((model: any) => {
      console.log(`- ${model.modelId}: ${model.modelName}`);
    });
    
  } catch (error: any) {
    console.error('❌ Bedrock 액세스 오류:', error.message);
    console.log('\n📋 Bedrock 모델 액세스 요청 방법:');
    console.log('1. AWS Console > Bedrock 서비스로 이동');
    console.log('2. Model access 메뉴 클릭');
    console.log('3. 다음 모델들에 대해 액세스 요청:');
    console.log('   - Anthropic Claude 3 Sonnet');
    console.log('   - Anthropic Claude 3 Opus');
    console.log('   - Amazon Nova Pro');
    console.log('   - Amazon Nova Lite');
    console.log('4. 승인 후 다시 이 스크립트 실행');
  }
}

if (require.main === module) {
  checkBedrockAccess().catch(console.error);
}