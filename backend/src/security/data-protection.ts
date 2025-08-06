import { EncryptionService, DataMasking } from './encryption';
import { Request, Response, NextFunction } from 'express';

interface DataProtectionConfig {
  encryptedFields: string[];
  maskedFields: string[];
  piiFields: string[];
  retentionDays: number;
  anonymizeAfterDays: number;
}

export class DataProtectionService {
  private encryptionService: EncryptionService;
  private config: DataProtectionConfig;
  
  constructor(config: DataProtectionConfig) {
    this.encryptionService = new EncryptionService();
    this.config = config;
  }
  
  // 데이터 저장 시 자동 암호화
  async protectData(data: any, context?: Record<string, string>): Promise<any> {
    const protectedData = JSON.parse(JSON.stringify(data));
    
    // 암호화 필드 처리
    for (const field of this.config.encryptedFields) {
      const value = this.getFieldValue(protectedData, field);
      if (value && typeof value === 'string') {
        const encrypted = await this.encryptionService.encryptField(value, context);
        this.setFieldValue(protectedData, field, encrypted);
      }
    }
    
    // 데이터 보호 메타데이터 추가
    protectedData._dataProtection = {
      encrypted: this.config.encryptedFields,
      createdAt: new Date().toISOString(),
      retentionUntil: new Date(Date.now() + this.config.retentionDays * 24 * 60 * 60 * 1000).toISOString()
    };
    
    return protectedData;
  }
  
  // 데이터 조회 시 자동 복호화
  async unprotectData(data: any, context?: Record<string, string>): Promise<any> {
    if (!data._dataProtection) return data;
    
    const unprotected = JSON.parse(JSON.stringify(data));
    
    // 복호화 필드 처리
    for (const field of data._dataProtection.encrypted || []) {
      const value = this.getFieldValue(unprotected, field);
      if (value && typeof value === 'string') {
        try {
          const decrypted = await this.encryptionService.decryptField(value, context);
          this.setFieldValue(unprotected, field, decrypted);
        } catch (error) {
          console.error(`Failed to decrypt field ${field}:`, error);
          // 복호화 실패 시 마스킹 처리
          this.setFieldValue(unprotected, field, '[ENCRYPTED]');
        }
      }
    }
    
    // 메타데이터 제거
    delete unprotected._dataProtection;
    
    return unprotected;
  }
  
  // 응답 데이터 마스킹
  maskResponseData(data: any): any {
    return DataMasking.maskObject(data, this.config.maskedFields);
  }
  
  // PII 데이터 익명화
  anonymizeData(data: any): any {
    const anonymized = JSON.parse(JSON.stringify(data));
    
    for (const field of this.config.piiFields) {
      const value = this.getFieldValue(anonymized, field);
      if (value) {
        // 필드 타입에 따른 익명화
        if (typeof value === 'string') {
          if (field.includes('email')) {
            this.setFieldValue(anonymized, field, `anonymous${Math.random().toString(36).substr(2, 5)}@example.com`);
          } else if (field.includes('name')) {
            this.setFieldValue(anonymized, field, `User${Math.random().toString(36).substr(2, 5)}`);
          } else {
            this.setFieldValue(anonymized, field, '[ANONYMIZED]');
          }
        }
      }
    }
    
    return anonymized;
  }
  
  // 데이터 보존 정책 확인
  shouldRetainData(data: any): boolean {
    if (!data._dataProtection?.retentionUntil) return true;
    
    const retentionDate = new Date(data._dataProtection.retentionUntil);
    return new Date() < retentionDate;
  }
  
  // 데이터 익명화 필요 여부 확인
  shouldAnonymizeData(data: any): boolean {
    if (!data._dataProtection?.createdAt) return false;
    
    const createdDate = new Date(data._dataProtection.createdAt);
    const anonymizeDate = new Date(createdDate.getTime() + this.config.anonymizeAfterDays * 24 * 60 * 60 * 1000);
    
    return new Date() > anonymizeDate;
  }
  
  private getFieldValue(obj: any, path: string): any {
    const keys = path.split('.');
    let current = obj;
    
    for (const key of keys) {
      if (current[key] === undefined) return undefined;
      current = current[key];
    }
    
    return current;
  }
  
  private setFieldValue(obj: any, path: string, value: any): void {
    const keys = path.split('.');
    let current = obj;
    
    for (let i = 0; i < keys.length - 1; i++) {
      if (current[keys[i]] === undefined) {
        current[keys[i]] = {};
      }
      current = current[keys[i]];
    }
    
    current[keys[keys.length - 1]] = value;
  }
}

// 데이터 보호 미들웨어
export function dataProtectionMiddleware(config: DataProtectionConfig) {
  const protectionService = new DataProtectionService(config);
  
  return async (req: Request, res: Response, next: NextFunction) => {
    // 요청 데이터 보호
    if (req.body && req.method !== 'GET') {
      try {
        req.body = await protectionService.protectData(req.body, {
          userId: (req as any).user?.id,
          requestId: (req as any).id
        });
      } catch (error) {
        console.error('Data protection error:', error);
      }
    }
    
    // 응답 데이터 처리
    const originalJson = res.json.bind(res);
    res.json = function(data: any) {
      if (data) {
        // 데이터 보호 해제
        protectionService.unprotectData(data, {
          userId: (req as any).user?.id,
          requestId: (req as any).id
        }).then(unprotected => {
          // 응답 데이터 마스킹
          const masked = protectionService.maskResponseData(unprotected);
          originalJson(masked);
        }).catch(error => {
          console.error('Data unprotection error:', error);
          originalJson(data);
        });
        return this;
      }
      return originalJson(data);
    };
    
    next();
  };
}

// GDPR 준수 도구
export class GDPRComplianceService {
  private protectionService: DataProtectionService;
  
  constructor(config: DataProtectionConfig) {
    this.protectionService = new DataProtectionService(config);
  }
  
  // 개인 데이터 내보내기 (GDPR Article 20)
  async exportPersonalData(userId: string): Promise<any> {
    // 사용자의 모든 개인 데이터 수집
    const userData = await this.collectUserData(userId);
    
    // 복호화 및 정리
    const decrypted = await this.protectionService.unprotectData(userData, { userId });
    
    return {
      exportedAt: new Date().toISOString(),
      userId,
      data: decrypted,
      format: 'JSON',
      rights: {
        portability: 'This data is provided in a structured, commonly used format',
        accuracy: 'You have the right to rectify inaccurate personal data',
        erasure: 'You have the right to request deletion of this data'
      }
    };
  }
  
  // 개인 데이터 삭제 (GDPR Article 17)
  async deletePersonalData(userId: string): Promise<void> {
    // 사용자 데이터 익명화
    const userData = await this.collectUserData(userId);
    const anonymized = this.protectionService.anonymizeData(userData);
    
    // 원본 데이터 삭제 및 익명화된 데이터로 교체
    await this.replaceUserData(userId, anonymized);
  }
  
  // 데이터 처리 동의 철회
  async revokeConsent(userId: string, consentType: string): Promise<void> {
    // 특정 유형의 데이터 처리 중단
    await this.updateConsentStatus(userId, consentType, false);
    
    // 해당 데이터 익명화 또는 삭제
    if (consentType === 'marketing') {
      await this.anonymizeMarketingData(userId);
    } else if (consentType === 'analytics') {
      await this.anonymizeAnalyticsData(userId);
    }
  }
  
  private async collectUserData(userId: string): Promise<any> {
    // 실제 구현에서는 데이터베이스에서 사용자 데이터 수집
    return {};
  }
  
  private async replaceUserData(userId: string, data: any): Promise<void> {
    // 실제 구현에서는 데이터베이스 업데이트
  }
  
  private async updateConsentStatus(userId: string, consentType: string, status: boolean): Promise<void> {
    // 동의 상태 업데이트
  }
  
  private async anonymizeMarketingData(userId: string): Promise<void> {
    // 마케팅 데이터 익명화
  }
  
  private async anonymizeAnalyticsData(userId: string): Promise<void> {
    // 분석 데이터 익명화
  }
}