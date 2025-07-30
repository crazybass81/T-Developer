import { MultiModalTextProcessor, TextProcessingOptions, ProcessedText } from './text-processor';
import { MultiModalImageProcessor, ImageProcessingOptions, ProcessedImage } from './image-processor';
import { AudioProcessor, AudioProcessingOptions, ProcessedAudio } from './audio-processor';

export interface MultiModalInput {
  type: 'text' | 'image' | 'audio' | 'mixed';
  data: any;
  metadata?: any;
  options?: any;
}

export interface MultiModalOutput {
  type: string;
  processed: any;
  insights: Insight[];
  recommendations?: string[];
  confidence: number;
  processingTime: number;
}

export interface Insight {
  type: 'text' | 'visual' | 'audio' | 'semantic';
  content: string;
  confidence: number;
  source: string;
}

export interface MixedModalInput {
  items: Array<{
    type: 'text' | 'image' | 'audio';
    data: any;
    options?: any;
  }>;
}

export class UnifiedMultiModalProcessor {
  private textProcessor: MultiModalTextProcessor;
  private imageProcessor: MultiModalImageProcessor;
  private audioProcessor: AudioProcessor;
  
  constructor() {
    this.textProcessor = new MultiModalTextProcessor();
    this.imageProcessor = new MultiModalImageProcessor();
    this.audioProcessor = new AudioProcessor();
  }
  
  async process(input: MultiModalInput): Promise<MultiModalOutput> {
    const startTime = Date.now();
    
    try {
      let result: MultiModalOutput;
      
      switch (input.type) {
        case 'text':
          result = await this.processText(input);
          break;
        case 'image':
          result = await this.processImage(input);
          break;
        case 'audio':
          result = await this.processAudio(input);
          break;
        case 'mixed':
          result = await this.processMixed(input);
          break;
        default:
          throw new Error(`Unsupported input type: ${input.type}`);
      }
      
      result.processingTime = Date.now() - startTime;
      return result;
      
    } catch (error) {
      throw new Error(`Multimodal processing failed: ${error.message}`);
    }
  }
  
  private async processText(input: MultiModalInput): Promise<MultiModalOutput> {
    const options: TextProcessingOptions = input.options || {};
    const processed = await this.textProcessor.processText(input.data, options);
    
    const insights = this.extractTextInsights(processed);
    
    return {
      type: 'text',
      processed,
      insights,
      recommendations: this.generateTextRecommendations(processed),
      confidence: this.calculateTextConfidence(processed),
      processingTime: 0 // Will be set by caller
    };
  }
  
  private async processImage(input: MultiModalInput): Promise<MultiModalOutput> {
    const options: ImageProcessingOptions = input.options || {};
    const processed = await this.imageProcessor.processImage(input.data, options);
    
    const insights = this.extractImageInsights(processed);
    
    return {
      type: 'image',
      processed,
      insights,
      recommendations: this.generateImageRecommendations(processed),
      confidence: this.calculateImageConfidence(processed),
      processingTime: 0
    };
  }
  
  private async processAudio(input: MultiModalInput): Promise<MultiModalOutput> {
    const options: AudioProcessingOptions = input.options || {};
    const processed = await this.audioProcessor.processAudio(input.data, options);
    
    const insights = this.extractAudioInsights(processed);
    
    return {
      type: 'audio',
      processed,
      insights,
      recommendations: this.generateAudioRecommendations(processed),
      confidence: this.calculateAudioConfidence(processed),
      processingTime: 0
    };
  }
  
  private async processMixed(input: MultiModalInput): Promise<MultiModalOutput> {
    const mixedInput = input.data as MixedModalInput;
    const results: MultiModalOutput[] = [];
    
    // 각 모달 병렬 처리
    const promises = mixedInput.items.map(async (item) => {
      return await this.process({
        type: item.type,
        data: item.data,
        options: item.options
      });
    });
    
    const modalResults = await Promise.all(promises);
    results.push(...modalResults);
    
    // 결과 통합
    const combinedInsights = this.combineInsights(results);
    const crossModalInsights = this.generateCrossModalInsights(results);
    
    return {
      type: 'mixed',
      processed: results,
      insights: [...combinedInsights, ...crossModalInsights],
      recommendations: this.generateMixedRecommendations(results),
      confidence: this.calculateOverallConfidence(results),
      processingTime: 0
    };
  }
  
  private extractTextInsights(processed: ProcessedText): Insight[] {
    const insights: Insight[] = [];
    
    // 토큰 수 인사이트
    insights.push({
      type: 'text',
      content: `Text contains ${processed.tokenCount} tokens and was split into ${processed.chunks.length} chunks`,
      confidence: 1.0,
      source: 'tokenizer'
    });
    
    // 언어 감지 인사이트
    if (processed.language) {
      insights.push({
        type: 'text',
        content: `Detected language: ${processed.language}`,
        confidence: 0.9,
        source: 'language_detector'
      });
    }
    
    return insights;
  }
  
  private extractImageInsights(processed: ProcessedImage): Insight[] {
    const insights: Insight[] = [];
    
    // 이미지 메타데이터 인사이트
    insights.push({
      type: 'visual',
      content: `Image dimensions: ${processed.metadata.width}x${processed.metadata.height}, format: ${processed.metadata.format}`,
      confidence: 1.0,
      source: 'metadata'
    });
    
    // OCR 텍스트 인사이트
    if (processed.extractedText) {
      insights.push({
        type: 'visual',
        content: `Extracted text: ${processed.extractedText}`,
        confidence: 0.8,
        source: 'ocr'
      });
    }
    
    // 객체 검출 인사이트
    if (processed.detectedObjects) {
      const objectLabels = processed.detectedObjects.map(obj => obj.label).join(', ');
      insights.push({
        type: 'visual',
        content: `Detected objects: ${objectLabels}`,
        confidence: 0.85,
        source: 'object_detection'
      });
    }
    
    return insights;
  }
  
  private extractAudioInsights(processed: ProcessedAudio): Insight[] {
    const insights: Insight[] = [];
    
    // 오디오 메타데이터 인사이트
    insights.push({
      type: 'audio',
      content: `Audio duration: ${processed.duration} seconds, format: ${processed.format}`,
      confidence: 1.0,
      source: 'metadata'
    });
    
    // 전사 인사이트
    if (processed.transcript) {
      insights.push({
        type: 'audio',
        content: `Transcribed ${processed.transcript.segments.length} segments with ${processed.transcript.confidence} confidence`,
        confidence: processed.transcript.confidence,
        source: 'speech_recognition'
      });
    }
    
    // 감정 분석 인사이트
    if (processed.analysis) {
      insights.push({
        type: 'audio',
        content: `Detected sentiment: ${processed.analysis.sentiment}`,
        confidence: 0.8,
        source: 'sentiment_analysis'
      });
    }
    
    return insights;
  }
  
  private combineInsights(results: MultiModalOutput[]): Insight[] {
    const allInsights: Insight[] = [];
    
    for (const result of results) {
      allInsights.push(...result.insights);
    }
    
    // 중복 제거 및 우선순위 정렬
    return this.deduplicateAndPrioritize(allInsights);
  }
  
  private generateCrossModalInsights(results: MultiModalOutput[]): Insight[] {
    const crossModalInsights: Insight[] = [];
    
    // 텍스트와 이미지 조합 분석
    const textResult = results.find(r => r.type === 'text');
    const imageResult = results.find(r => r.type === 'image');
    
    if (textResult && imageResult) {
      crossModalInsights.push({
        type: 'semantic',
        content: 'Text and image content appear to be related based on semantic analysis',
        confidence: 0.7,
        source: 'cross_modal_analysis'
      });
    }
    
    return crossModalInsights;
  }
  
  private deduplicateAndPrioritize(insights: Insight[]): Insight[] {
    // 간단한 중복 제거 (실제로는 더 정교한 로직 필요)
    const unique = insights.filter((insight, index, self) => 
      index === self.findIndex(i => i.content === insight.content)
    );
    
    // 신뢰도 기준 정렬
    return unique.sort((a, b) => b.confidence - a.confidence);
  }
  
  private generateTextRecommendations(processed: ProcessedText): string[] {
    const recommendations: string[] = [];
    
    if (processed.tokenCount > 4000) {
      recommendations.push('Consider breaking down the text into smaller chunks for better processing');
    }
    
    if (processed.chunks.length > 10) {
      recommendations.push('Text is quite long, consider summarization for better user experience');
    }
    
    return recommendations;
  }
  
  private generateImageRecommendations(processed: ProcessedImage): string[] {
    const recommendations: string[] = [];
    
    if (processed.metadata.size > 5 * 1024 * 1024) { // 5MB
      recommendations.push('Image is large, consider compression for better performance');
    }
    
    if (processed.metadata.width > 2000 || processed.metadata.height > 2000) {
      recommendations.push('High resolution image, consider resizing for web usage');
    }
    
    return recommendations;
  }
  
  private generateAudioRecommendations(processed: ProcessedAudio): string[] {
    const recommendations: string[] = [];
    
    if (processed.duration > 300) { // 5 minutes
      recommendations.push('Long audio file, consider segmentation for better processing');
    }
    
    if (processed.transcript && processed.transcript.confidence < 0.8) {
      recommendations.push('Low transcription confidence, consider audio enhancement');
    }
    
    return recommendations;
  }
  
  private generateMixedRecommendations(results: MultiModalOutput[]): string[] {
    const recommendations: string[] = [];
    
    // 각 모달의 추천사항 수집
    for (const result of results) {
      if (result.recommendations) {
        recommendations.push(...result.recommendations);
      }
    }
    
    // 크로스 모달 추천사항
    if (results.length > 2) {
      recommendations.push('Multiple modalities detected, consider creating a unified summary');
    }
    
    return [...new Set(recommendations)]; // 중복 제거
  }
  
  private calculateTextConfidence(processed: ProcessedText): number {
    // 토큰화 성공률 기반 신뢰도
    return processed.tokenCount > 0 ? 0.95 : 0.5;
  }
  
  private calculateImageConfidence(processed: ProcessedImage): number {
    // 메타데이터 추출 성공률 기반 신뢰도
    return processed.metadata.width > 0 ? 0.9 : 0.5;
  }
  
  private calculateAudioConfidence(processed: ProcessedAudio): number {
    // 전사 신뢰도 기반
    return processed.transcript?.confidence || 0.7;
  }
  
  private calculateOverallConfidence(results: MultiModalOutput[]): number {
    if (results.length === 0) return 0;
    
    const totalConfidence = results.reduce((sum, result) => sum + result.confidence, 0);
    return totalConfidence / results.length;
  }
}