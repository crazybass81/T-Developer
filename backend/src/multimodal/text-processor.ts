export interface TextProcessingOptions {
  normalize?: boolean;
  maskPii?: boolean;
  translate?: boolean;
  targetLanguage?: string;
  maxTokens?: number;
  generateEmbeddings?: boolean;
}

export interface ProcessedText {
  original: string;
  processed: string;
  tokens: string[];
  tokenCount: number;
  chunks: string[];
  embeddings?: number[][];
  language?: string;
  metadata: Record<string, any>;
}

export class TextProcessor {
  private tokenizers = new Map<string, any>();

  async processText(text: string, options: TextProcessingOptions = {}): Promise<ProcessedText> {
    // 1. 전처리
    let processed = await this.preprocess(text, options);
    
    // 2. 토크나이징
    const tokens = this.tokenize(processed);
    
    // 3. 청킹
    const chunks = this.chunkText(processed, tokens, options.maxTokens || 4096);
    
    // 4. 임베딩 (선택적)
    let embeddings;
    if (options.generateEmbeddings) {
      embeddings = await this.generateEmbeddings(chunks);
    }

    return {
      original: text,
      processed,
      tokens,
      tokenCount: tokens.length,
      chunks,
      embeddings,
      language: await this.detectLanguage(text),
      metadata: {
        processedAt: new Date().toISOString(),
        options
      }
    };
  }

  private async preprocess(text: string, options: TextProcessingOptions): Promise<string> {
    let processed = text;

    // 정규화
    if (options.normalize) {
      processed = this.normalizeText(processed);
    }

    // PII 마스킹
    if (options.maskPii) {
      processed = await this.maskSensitiveInfo(processed);
    }

    // 번역
    if (options.translate && options.targetLanguage) {
      const language = await this.detectLanguage(processed);
      if (language !== options.targetLanguage) {
        processed = await this.translateText(processed, language, options.targetLanguage);
      }
    }

    return processed;
  }

  private normalizeText(text: string): string {
    return text
      .replace(/\s+/g, ' ')
      .replace(/[^\w\s\.\,\!\?\-]/g, '')
      .trim();
  }

  private async maskSensitiveInfo(text: string): Promise<string> {
    // 이메일 마스킹
    text = text.replace(/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g, '[EMAIL]');
    
    // 전화번호 마스킹
    text = text.replace(/\b\d{3}-\d{3}-\d{4}\b/g, '[PHONE]');
    
    // 신용카드 번호 마스킹
    text = text.replace(/\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b/g, '[CARD]');

    return text;
  }

  private tokenize(text: string): string[] {
    // 간단한 토크나이저 (실제로는 더 정교한 토크나이저 사용)
    return text.toLowerCase()
      .split(/\s+/)
      .filter(token => token.length > 0);
  }

  private chunkText(text: string, tokens: string[], maxTokens: number): string[] {
    if (tokens.length <= maxTokens) {
      return [text];
    }

    const chunks: string[] = [];
    const sentences = this.splitSentences(text);
    let currentChunk: string[] = [];
    let currentTokens = 0;

    for (const sentence of sentences) {
      const sentenceTokens = this.tokenize(sentence).length;
      
      if (currentTokens + sentenceTokens > maxTokens && currentChunk.length > 0) {
        chunks.push(currentChunk.join(' '));
        currentChunk = [sentence];
        currentTokens = sentenceTokens;
      } else {
        currentChunk.push(sentence);
        currentTokens += sentenceTokens;
      }
    }

    if (currentChunk.length > 0) {
      chunks.push(currentChunk.join(' '));
    }

    return chunks;
  }

  private splitSentences(text: string): string[] {
    return text.split(/[.!?]+/).filter(s => s.trim().length > 0);
  }

  private async detectLanguage(text: string): Promise<string> {
    // 간단한 언어 감지 (실제로는 더 정교한 라이브러리 사용)
    const koreanPattern = /[ㄱ-ㅎ|ㅏ-ㅣ|가-힣]/;
    const englishPattern = /[a-zA-Z]/;
    
    if (koreanPattern.test(text)) return 'ko';
    if (englishPattern.test(text)) return 'en';
    return 'unknown';
  }

  private async translateText(text: string, from: string, to: string): Promise<string> {
    // 번역 시뮬레이션 (실제로는 번역 API 사용)
    console.log(`Translating from ${from} to ${to}`);
    return text; // 실제 번역 구현 필요
  }

  private async generateEmbeddings(chunks: string[]): Promise<number[][]> {
    // 임베딩 생성 시뮬레이션 (실제로는 임베딩 모델 사용)
    return chunks.map(() => Array.from({ length: 768 }, () => Math.random()));
  }
}