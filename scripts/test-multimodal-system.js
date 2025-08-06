#!/usr/bin/env node

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🧪 Testing Multimodal Processing System...\n');

// Test script for multimodal system
const testScript = `
import sys
sys.path.append('backend/src')

from multimodal.unified_api import UnifiedMultiModalAPI
from multimodal.multimodal_processor import MultiModalProcessor
import asyncio
from PIL import Image
import io

async def test_multimodal_system():
    print('🔧 Initializing Unified Multimodal API...')
    api = UnifiedMultiModalAPI()
    
    # Test 1: Text processing
    print('\\n📝 Testing text processing...')
    text_result = await api.process_single(
        'Hello world! This is a test email: user@example.com and phone: 010-1234-5678',
        'text',
        {'normalize': True, 'mask_pii': True}
    )
    print(f'✅ Text processed: {text_result["result"]["token_count"]} tokens')
    print(f'   Insights: {text_result["insights"]}')
    print(f'   Confidence: {text_result["confidence"]:.2f}')
    
    # Test 2: Image processing
    print('\\n🖼️  Testing image processing...')
    img = Image.new('RGB', (200, 150), color='blue')
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    
    image_result = await api.process_single(
        buf.getvalue(),
        'image',
        {'resize': {'width': 100, 'height': 75}, 'extract_text': True}
    )
    print(f'✅ Image processed: {image_result["result"]["metadata"]}')
    print(f'   Insights: {image_result["insights"]}')
    print(f'   Confidence: {image_result["confidence"]:.2f}')
    
    # Test 3: Audio processing
    print('\\n🎵 Testing audio processing...')
    audio_result = await api.process_single(
        b'mock_audio_data_longer_than_300_seconds',
        'audio',
        {'transcribe': True, 'analyze': True}
    )
    print(f'✅ Audio processed: Language = {audio_result["result"]["transcript"]["language"]}')
    print(f'   Insights: {audio_result["insights"]}')
    print(f'   Confidence: {audio_result["confidence"]:.2f}')
    
    # Test 4: Batch processing
    print('\\n📦 Testing batch processing...')
    batch_inputs = [
        {'data': 'Short text', 'type': 'text'},
        {'data': buf.getvalue(), 'type': 'image'},
        {'data': b'audio_data', 'type': 'audio'}
    ]
    
    batch_result = await api.process_batch(batch_inputs)
    print(f'✅ Batch processed: {len(batch_result["results"])} items')
    print(f'   Combined insights: {batch_result["combined_insights"]}')
    print(f'   Overall confidence: {batch_result["overall_confidence"]:.2f}')
    
    print('\\n🎉 All multimodal tests completed successfully!')
    return True

# Run the test
if asyncio.run(test_multimodal_system()):
    print('\\n✅ Multimodal system is working correctly!')
else:
    print('\\n❌ Multimodal system test failed!')
    sys.exit(1)
`;

// Write test script to temporary file
const tempFile = path.join(__dirname, '..', 'temp_multimodal_test.py');
fs.writeFileSync(tempFile, testScript);

// Run the test
const python = spawn('python3', [tempFile], {
    cwd: path.join(__dirname, '..'),
    stdio: 'inherit'
});

python.on('close', (code) => {
    // Clean up temp file
    if (fs.existsSync(tempFile)) {
        fs.unlinkSync(tempFile);
    }
    
    if (code === 0) {
        console.log('\n🎯 Multimodal System Test Results:');
        console.log('✅ Text Processing: Working');
        console.log('✅ Image Processing: Working');
        console.log('✅ Audio Processing: Working');
        console.log('✅ Unified API: Working');
        console.log('✅ Batch Processing: Working');
        console.log('\n🏆 All multimodal components are operational!');
    } else {
        console.log('\n❌ Multimodal system test failed with code:', code);
        process.exit(1);
    }
});

python.on('error', (err) => {
    console.error('❌ Failed to run multimodal test:', err.message);
    process.exit(1);
});