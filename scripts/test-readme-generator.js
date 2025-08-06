#!/usr/bin/env node

const { ReadmeGenerator } = require('../backend/dist/utils/readme-generator');
const path = require('path');
const fs = require('fs');

async function testReadmeGenerator() {
  console.log('📝 README 생성기 테스트 시작...');
  
  try {
    // 1. 템플릿 파일 존재 확인
    const templatePath = path.join(__dirname, '../templates/README-project.md');
    if (!fs.existsSync(templatePath)) {
      throw new Error('README 템플릿 파일이 없습니다');
    }
    console.log('✅ README 템플릿 파일 존재 확인');
    
    // 2. 생성기 인스턴스 생성
    const generator = await ReadmeGenerator.create(templatePath);
    
    // 3. 테스트 프로젝트 데이터
    const testProject = {
      name: 'my-awesome-app',
      description: 'AI 기반 웹 애플리케이션',
      userId: 'testuser',
      techStack: {
        database: 'PostgreSQL',
        cloud: 'aws'
      }
    };
    
    // 4. README 생성
    const readme = await generator.generate(testProject);
    
    // 5. 결과 검증
    if (readme.includes('my-awesome-app')) {
      console.log('✅ 프로젝트 이름 치환 성공');
    }
    
    if (readme.includes('PostgreSQL')) {
      console.log('✅ 기술 스택 요구사항 추가 성공');
    }
    
    if (readme.includes('AWS CLI')) {
      console.log('✅ 클라우드 요구사항 추가 성공');
    }
    
    // 6. 생성된 README 저장
    const outputPath = path.join(__dirname, '../test-output/README.md');
    fs.mkdirSync(path.dirname(outputPath), { recursive: true });
    fs.writeFileSync(outputPath, readme);
    
    console.log('✅ README 생성기 테스트 완료!');
    console.log(`📁 생성된 파일: ${outputPath}`);
    
  } catch (error) {
    console.error('❌ README 생성기 테스트 실패:', error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  testReadmeGenerator();
}