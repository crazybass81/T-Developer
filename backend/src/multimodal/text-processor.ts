// import { TextProcessor } from 'agno'; // Mock for testing
class TextProcessor {}
// import tiktoken from 'tiktoken'; // Commented out for testing

export interface TextProcessingOptions {
  model?: string;
  maxTokens?: number;
  normalize?: boolean;
  maskPII?: boolean;
  translate?: boolean;
  targetLanguage?: string;
  generateEmbeddings?: boolean;
}

export interface ProcessedText {
  original: string;
  processed: string;
  tokens: number[];
  tokenCount: number;
  chunks: string[];
  embeddings?: number[][];
  language?: string;
}

export class MultiModalTextProcessor {
  private processor: TextProcessor;
  private tokenizers: Map<string, any>;
  
  constructor() {
    this.processor = new TextProcessor();
    this.tokenizers = new Map();
    this.initializeTokenizers();
  }
  
  private initializeTokenizers(): void {
    // Mock tokenizers for testing
    const mockTokenizer = {
      encode: (text: string) => Array.from({ length: Math.ceil(text.length / 4) }, (_, i) => i)
    };
    
    this.tokenizers.set('gpt-4', mockTokenizer);
    this.tokenizers.set('gpt-3.5-turbo', mockTokenizer);
    this.tokenizers.set('claude-3', mockTokenizer);
  }
  
  async processText(
    text: string,
    options: TextProcessingOptions = {}
  ): Promise<ProcessedText> {
    // 1. 전처리
    const cleaned = await this.preprocess(text, options);
    
    // 2. 토크나이징
    const tokens = this.tokenize(cleaned, options.model || 'gpt-4');
    
    // 3. 청킹
    const chunks = this.chunkText(cleaned, tokens, options.maxTokens || 4096);
    
    // 4. 임베딩 생성 (선택적)
    let embeddings: number[][] | undefined;
    if (options.generateEmbeddings) {
      embeddings = await this.generateEmbeddings(chunks);
    }
    
    return {
      original: text,
      processed: cleaned,
      tokens,
      tokenCount: tokens.length,
      chunks,
      embeddings
    };
  }
  
  private async preprocess(
    text: string,
    options: TextProcessingOptions
  ): Promise<string> {
    let processed = text;
    
    // 정규화
    if (options.normalize) {
      processed = this.normalizeText(processed);
    }
    
    // PII 마스킹
    if (options.maskPII) {
      processed = this.maskSensitiveInfo(processed);
    }
    
    return processed;
  }
  
  private normalizeText(text: string): string {
    return text
      .replace(/\s+/g, ' ')
      .replace(/\n+/g, '\n')
      .trim();
  }
  
  private maskSensitiveInfo(text: string): string {
    // 이메일 마스킹
    text = text.replace(/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g, '[EMAIL]');
    
    // 전화번호 마스킹
    text = text.replace(/\b\d{3}-\d{3}-\d{4}\b/g, '[PHONE]');
    
    // 신용카드 번호 마스킹
    text = text.replace(/\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b/g, '[CARD]');
    
    return text;
  }
  
  private tokenize(text: string, model: string): number[] {
    const tokenizer = this.tokenizers.get(model) || this.tokenizers.get('gpt-4');
    return tokenizer.encode(text);
  }
  
  private chunkText(text: string, tokens: number[], maxTokens: number): string[] {
    if (tokens.length <= maxTokens) {
      return [text];
    }
    
    const chunks: string[] = [];
    const sentences = text.split(/[.!?]+/).filter(s => s.trim());
    
    let currentChunk = '';
    let currentTokens = 0;
    
    for (const sentence of sentences) {
      const sentenceTokens = this.tokenize(sentence, 'gpt-4').length;
      
      if (currentTokens + sentenceTokens > maxTokens && currentChunk) {
        chunks.push(currentChunk.trim());
        currentChunk = sentence;
        currentTokens = sentenceTokens;
      } else {
        currentChunk += (currentChunk ? '. ' : '') + sentence;
        currentTokens += sentenceTokens;
      }
    }
    
    if (currentChunk) {
      chunks.push(currentChunk.trim());
    }
    
    return chunks;
  }
  
  private async generateEmbeddings(chunks: string[]): Promise<number[][]> {
    // OpenAI Embeddings API 호출 (실제 구현에서는 API 키 필요)
    const embeddings: number[][] = [];
    
    for (const chunk of chunks) {
      // 임시로 랜덤 임베딩 생성 (실제로는 API 호출)
      const embedding = Array.from({ length: 1536 }, () => Math.random());
      embeddings.push(embedding);
    }
    
    return embeddings;
  }
}