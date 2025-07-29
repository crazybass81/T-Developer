import { exec } from 'child_process';
import { promisify } from 'util';
import { promises as fs } from 'fs';
import path from 'path';

const execAsync = promisify(exec);

async function generateDocumentation() {
  console.log('📚 문서 생성 시작...');
  
  try {
    // TypeDoc으로 API 문서 생성
    console.log('1️⃣ API 레퍼런스 생성 중...');
    await execAsync('npx typedoc');
    
    // 문서 인덱스 생성
    console.log('2️⃣ 문서 인덱스 생성 중...');
    await generateDocsIndex();
    
    console.log('✅ 문서 생성 완료!');
    console.log('📁 출력 위치: ./docs');
    
  } catch (error) {
    console.error('❌ 문서 생성 실패:', error);
    process.exit(1);
  }
}

async function generateDocsIndex() {
  const docsMetadata = {
    version: process.env.npm_package_version || '1.0.0',
    generated: new Date().toISOString(),
    sections: [
      { path: '/getting-started', title: '시작하기', weight: 1 },
      { path: '/architecture', title: '아키텍처', weight: 2 },
      { path: '/api', title: 'API 레퍼런스', weight: 3 }
    ]
  };
  
  await fs.mkdir('docs', { recursive: true });
  await fs.writeFile(
    path.join('docs/metadata.json'),
    JSON.stringify(docsMetadata, null, 2)
  );
}

if (require.main === module) {
  generateDocumentation();
}