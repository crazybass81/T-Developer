import { TextProcessor, TextProcessingOptions, ProcessedText } from './text-processor';
import { ImageProcessor, ImageProcessingOptions, ProcessedImage } from './image-processor';
import { AudioProcessor, AudioProcessingOptions, ProcessedAudio } from './audio-processor';
import { EventEmitter } from 'events';

export type MediaType = 'text' | 'image' | 'audio';

export interface MultimodalInput {
  type: MediaType;
  data: string | Buffer;
  options?: TextProcessingOptions | ImageProcessingOptions | AudioProcessingOptions;
}

export interface MultimodalOutput {
  type: MediaType;
  processed: ProcessedText | ProcessedImage | ProcessedAudio;
  processingTime: number;
  metadata: {
    inputSize: number;
    outputSize: number;
    timestamp: string;
  };
}

export interface CrossModalAnalysis {
  textImageAlignment?: number;
  audioTextAlignment?: number;
  overallCoherence?: number;
  insights: string[];
}

export class MultimodalProcessor extends EventEmitter {
  private textProcessor: TextProcessor;
  private imageProcessor: ImageProcessor;
  private audioProcessor: AudioProcessor;

  constructor() {
    super();
    this.textProcessor = new TextProcessor();
    this.imageProcessor = new ImageProcessor();
    this.audioProcessor = new AudioProcessor();
  }

  async processSingle(input: MultimodalInput): Promise<MultimodalOutput> {
    const startTime = performance.now();
    const inputSize = this.getInputSize(input.data);

    let processed: ProcessedText | ProcessedImage | ProcessedAudio;

    switch (input.type) {
      case 'text':
        processed = await this.textProcessor.processText(
          input.data as string,
          input.options as TextProcessingOptions
        );
        break;

      case 'image':
        processed = await this.imageProcessor.processImage(
          input.data as Buffer,
          input.options as ImageProcessingOptions
        );
        break;

      case 'audio':
        processed = await this.audioProcessor.processAudio(
          input.data as Buffer,
          input.options as AudioProcessingOptions
        );
        break;

      default:
        throw new Error(`Unsupported media type: ${input.type}`);
    }

    const processingTime = performance.now() - startTime;
    const outputSize = this.getOutputSize(processed);

    this.emit('processed', { type: input.type, processingTime });

    return {
      type: input.type,
      processed,
      processingTime,
      metadata: {
        inputSize,
        outputSize,
        timestamp: new Date().toISOString()
      }
    };
  }

  async processMultiple(inputs: MultimodalInput[]): Promise<MultimodalOutput[]> {
    const startTime = performance.now();
    
    // 병렬 처리
    const promises = inputs.map(input => this.processSingle(input));
    const results = await Promise.all(promises);
    
    const totalTime = performance.now() - startTime;
    
    this.emit('batchProcessed', {
      count: inputs.length,
      totalTime,
      averageTime: totalTime / inputs.length
    });

    return results;
  }

  async analyzeCrossModal(outputs: MultimodalOutput[]): Promise<CrossModalAnalysis> {
    const analysis: CrossModalAnalysis = {
      insights: []
    };

    const textOutputs = outputs.filter(o => o.type === 'text');
    const imageOutputs = outputs.filter(o => o.type === 'image');
    const audioOutputs = outputs.filter(o => o.type === 'audio');

    // 텍스트-이미지 정렬 분석
    if (textOutputs.length > 0 && imageOutputs.length > 0) {
      analysis.textImageAlignment = await this.analyzeTextImageAlignment(
        textOutputs[0].processed as ProcessedText,
        imageOutputs[0].processed as ProcessedImage
      );
      
      if (analysis.textImageAlignment > 0.8) {
        analysis.insights.push('High text-image semantic alignment detected');
      }
    }

    // 오디오-텍스트 정렬 분석
    if (audioOutputs.length > 0 && textOutputs.length > 0) {
      analysis.audioTextAlignment = await this.analyzeAudioTextAlignment(
        audioOutputs[0].processed as ProcessedAudio,
        textOutputs[0].processed as ProcessedText
      );
      
      if (analysis.audioTextAlignment > 0.7) {
        analysis.insights.push('Strong audio-text content correlation found');
      }
    }

    // 전체 일관성 분석
    analysis.overallCoherence = this.calculateOverallCoherence(analysis);

    return analysis;
  }

  private async analyzeTextImageAlignment(text: ProcessedText, image: ProcessedImage): Promise<number> {
    // 텍스트와 이미지 간 의미적 정렬 분석
    const textKeywords = text.tokens.slice(0, 10); // 상위 10개 토큰
    const imageObjects = image.detectedObjects?.map(obj => obj.label) || [];
    
    const commonConcepts = textKeywords.filter(keyword => 
      imageObjects.some(obj => obj.toLowerCase().includes(keyword.toLowerCase()))
    );
    
    return commonConcepts.length / Math.max(textKeywords.length, imageObjects.length);
  }

  private async analyzeAudioTextAlignment(audio: ProcessedAudio, text: ProcessedText): Promise<number> {
    // 오디오 전사와 텍스트 간 유사도 분석
    if (!audio.transcription) return 0;
    
    const audioTokens = audio.transcription.toLowerCase().split(/\s+/);
    const textTokens = text.tokens;
    
    const commonTokens = audioTokens.filter(token => textTokens.includes(token));
    
    return commonTokens.length / Math.max(audioTokens.length, textTokens.length);
  }

  private calculateOverallCoherence(analysis: CrossModalAnalysis): number {
    const scores = [
      analysis.textImageAlignment,
      analysis.audioTextAlignment
    ].filter(score => score !== undefined) as number[];
    
    if (scores.length === 0) return 0;
    
    return scores.reduce((sum, score) => sum + score, 0) / scores.length;
  }

  private getInputSize(data: string | Buffer): number {
    if (typeof data === 'string') {
      return Buffer.byteLength(data, 'utf8');
    }
    return data.length;
  }

  private getOutputSize(processed: ProcessedText | ProcessedImage | ProcessedAudio): number {
    if ('processed' in processed && Buffer.isBuffer(processed.processed)) {
      return processed.processed.length;
    }
    return JSON.stringify(processed).length;
  }

  // 스트리밍 처리
  async processStream(inputStream: AsyncIterable<MultimodalInput>): Promise<AsyncIterable<MultimodalOutput>> {
    const processor = this;
    
    return {
      async *[Symbol.asyncIterator]() {
        for await (const input of inputStream) {
          yield await processor.processSingle(input);
        }
      }
    };
  }

  // 배치 최적화
  async processBatch(inputs: MultimodalInput[], batchSize = 10): Promise<MultimodalOutput[]> {
    const results: MultimodalOutput[] = [];
    
    for (let i = 0; i < inputs.length; i += batchSize) {
      const batch = inputs.slice(i, i + batchSize);
      const batchResults = await this.processMultiple(batch);
      results.push(...batchResults);
      
      // 배치 간 짧은 대기 (메모리 관리)
      if (i + batchSize < inputs.length) {
        await new Promise(resolve => setTimeout(resolve, 100));
      }
    }
    
    return results;
  }

  // 성능 통계
  getPerformanceStats(): {
    processedCount: number;
    averageProcessingTime: number;
    throughput: number;
  } {
    // 실제로는 내부 메트릭 수집 필요
    return {
      processedCount: 0,
      averageProcessingTime: 0,
      throughput: 0
    };
  }
}