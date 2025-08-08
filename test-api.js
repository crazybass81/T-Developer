const axios = require('axios');

async function testAPI() {
  try {
    console.log('Testing T-Developer API...');
    
    const response = await axios.post('http://localhost:8000/api/v1/generate', {
      query: '간단한 할일 목록 앱을 만들어줘',
      framework: 'react'
    }, {
      timeout: 30000 // 30초 타임아웃
    });
    
    console.log('Response Status:', response.status);
    console.log('Response Data:', JSON.stringify(response.data, null, 2));
    
    if (response.data.status === 'success') {
      console.log('✅ API Test Successful!');
      console.log('Project Name:', response.data.projectName);
      console.log('Download URL:', response.data.result?.downloadUrl);
    } else {
      console.log('❌ API returned error:', response.data.message);
    }
  } catch (error) {
    console.error('❌ API Test Failed:', error.message);
    if (error.response) {
      console.error('Response Data:', error.response.data);
    }
  }
}

testAPI();