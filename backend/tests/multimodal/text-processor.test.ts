// backend/tests/multimodal/text-processor.test.ts
import { MultiModalTextProcessor } from '../../src/multimodal/text-processor';

// Mock tiktoken - removed since not installed

// Mock agno TextProcessor
jest.mock('agno', () => ({
  TextProcessor: jest.fn().mockImplementation(() => ({}))
}));

describe('MultiModalTextProcessor', () => {
  let processor: MultiModalTextProcessor;

  beforeEach(() => {
    processor = new MultiModalTextProcessor();
  });

  test('should process basic text', async () => {
    const text = 'Hello world! This is a test.';
    const result = await processor.processText(text);

    expect(result.original).toBe(text);
    expect(result.processed).toBe(text);
    expect(result.tokenCount).toBeGreaterThan(0);
    expect(result.chunks).toHaveLength(1);
  });

  test('should normalize text when option is enabled', async () => {
    const text = 'Hello   world!\n\n\nThis  is   a test.';
    const result = await processor.processText(text, { normalize: true });

    expect(result.processed).toBe('Hello world! This is a test.');
  });

  test('should mask PII when option is enabled', async () => {
    const text = 'Contact me at john@example.com or 123-456-7890';
    const result = await processor.processText(text, { maskPII: true });

    expect(result.processed).toContain('[EMAIL]');
    expect(result.processed).toContain('[PHONE]');
    expect(result.processed).not.toContain('john@example.com');
    expect(result.processed).not.toContain('123-456-7890');
  });

  test('should chunk long text', async () => {
    const longText = 'This is sentence one. '.repeat(100);
    const result = await processor.processText(longText, { maxTokens: 50 });

    expect(result.chunks.length).toBeGreaterThan(1);
  });

  test('should generate embeddings when requested', async () => {
    const text = 'Test text for embeddings';
    const result = await processor.processText(text, { generateEmbeddings: true });

    expect(result.embeddings).toBeDefined();
    expect(result.embeddings!.length).toBeGreaterThan(0);
    expect(result.embeddings![0]).toHaveLength(1536);
  });
});