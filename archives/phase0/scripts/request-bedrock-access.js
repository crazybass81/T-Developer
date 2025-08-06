#!/usr/bin/env node
const { BedrockClient, ListFoundationModelsCommand } = require('@aws-sdk/client-bedrock');

async function checkBedrockAccess() {
  const client = new BedrockClient({ region: 'us-east-1' });
  
  try {
    console.log('🔍 Bedrock 모델 액세스 확인 중...');
    const command = new ListFoundationModelsCommand({});
    const response = await client.send(command);
    
    console.log('✅ Bedrock 액세스 확인됨');
    console.log(`📊 총 ${response.modelSummaries?.length || 0}개 모델 사용 가능\n`);
    
    // 주요 모델들만 표시
    const keyModels = [
      'anthropic.claude-3-5-sonnet',
      'anthropic.claude-3-sonnet',
      'anthropic.claude-3-opus',
      'amazon.nova-pro',
      'amazon.nova-lite',
      'amazon.titan-text'
    ];
    
    console.log('🎯 T-Developer 핵심 모델:');
    response.modelSummaries?.forEach(model => {
      if (keyModels.some(key => model.modelId?.includes(key))) {
        console.log(`✅ ${model.modelId}: ${model.modelName}`);
      }
    });
    
    console.log('\n📋 전체 사용 가능 모델:');
    response.modelSummaries?.forEach(model => {
      console.log(`- ${model.modelId}: ${model.modelName}`);
    });
    
  } catch (error) {
    console.error('❌ Bedrock 액세스 오류:', error.message);
    console.log('\n📋 Bedrock 모델 액세스 요청 방법:');
    console.log('1. AWS Console > Bedrock 서비스로 이동');
    console.log('2. Model access 메뉴 클릭');
    console.log('3. 다음 모델들에 대해 액세스 요청:');
    console.log('   - Anthropic Claude 3.5 Sonnet');
    console.log('   - Anthropic Claude 3 Sonnet');
    console.log('   - Anthropic Claude 3 Opus');
    console.log('   - Amazon Nova Pro');
    console.log('   - Amazon Nova Lite');
    console.log('   - Amazon Titan Text');
  }
}

if (require.main === module) {
  checkBedrockAccess().catch(console.error);
}