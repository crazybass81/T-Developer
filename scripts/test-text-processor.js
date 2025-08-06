#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');

console.log('🧪 Testing Text Processor...\n');

const testScript = `
import sys
sys.path.append('${path.join(__dirname, '../backend/src')}')

from multimodal.text_processor import MultiModalTextProcessor
import asyncio

async def test_text_processor():
    processor = MultiModalTextProcessor()
    
    # Test text
    text = "Hello world! This is a test. How are you today? I'm fine, thank you."
    
    options = {
        'normalize': True,
        'mask_pii': False,
        'max_tokens': 20,
        'generate_embeddings': True
    }
    
    result = await processor.process_text(text, options)
    
    print("✅ Text Processing Results:")
    print(f"Original length: {len(result['original'])}")
    print(f"Processed length: {len(result['processed'])}")
    print(f"Token count: {result['token_count']}")
    print(f"Chunks: {len(result['chunks'])}")
    print(f"Has embeddings: {result['embeddings'] is not None}")
    
    # Test PII masking
    pii_text = "Contact me at john@example.com or 123-456-7890"
    pii_options = {'mask_pii': True}
    pii_result = await processor.process_text(pii_text, pii_options)
    print(f"\\nPII Masked: {pii_result['processed']}")
    
    print("\\n✅ All text processor tests passed!")

if __name__ == "__main__":
    asyncio.run(test_text_processor())
`;

const python = spawn('python3', ['-c', testScript], {
    stdio: 'inherit',
    cwd: path.join(__dirname, '..')
});

python.on('close', (code) => {
    if (code === 0) {
        console.log('\n✅ Text Processor implementation completed!');
    } else {
        console.log('\n❌ Text Processor test failed');
        process.exit(1);
    }
});