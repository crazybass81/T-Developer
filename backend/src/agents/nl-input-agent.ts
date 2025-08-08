/**
 * NL Input Agent - 자연어 입력 처리 에이전트
 * 사용자의 자연어 설명을 분석하고 프로젝트 요구사항을 추출
 */

export interface ProjectRequirements {
  description: string;
  projectType: string;
  functionalRequirements: string[];
  nonFunctionalRequirements: string[];
  technologyPreferences: {
    framework?: string;
    database?: string;
    styling?: string;
    features?: string[];
  };
  constraints: string[];
  extractedEntities: {
    pages?: string[];
    components?: string[];
    actions?: string[];
    dataModels?: string[];
  };
  confidenceScore: number;
}

export class NLInputAgent {
  private name = 'NL Input Agent';
  
  /**
   * 자연어 입력을 분석하여 구조화된 요구사항 추출
   */
  async processInput(query: string, framework?: string): Promise<ProjectRequirements> {
    console.log(`[${this.name}] Processing: ${query}`);
    
    // 프로젝트 타입 결정
    const projectType = this.detectProjectType(query);
    
    // 기능 요구사항 추출
    const functionalReqs = this.extractFunctionalRequirements(query);
    
    // 비기능 요구사항 추출
    const nonFunctionalReqs = this.extractNonFunctionalRequirements(query);
    
    // 기술 선호사항 추출
    const techPrefs = this.extractTechnologyPreferences(query, framework);
    
    // 엔티티 추출 (페이지, 컴포넌트, 액션 등)
    const entities = this.extractEntities(query);
    
    // 제약사항 추출
    const constraints = this.extractConstraints(query);
    
    // 신뢰도 점수 계산
    const confidenceScore = this.calculateConfidence(query, functionalReqs);
    
    return {
      description: query,
      projectType,
      functionalRequirements: functionalReqs,
      nonFunctionalRequirements: nonFunctionalReqs,
      technologyPreferences: techPrefs,
      constraints,
      extractedEntities: entities,
      confidenceScore
    };
  }
  
  private detectProjectType(query: string): string {
    const lowerQuery = query.toLowerCase();
    
    if (lowerQuery.includes('블로그') || lowerQuery.includes('blog')) {
      return 'blog';
    } else if (lowerQuery.includes('쇼핑') || lowerQuery.includes('이커머스') || lowerQuery.includes('shop')) {
      return 'e-commerce';
    } else if (lowerQuery.includes('대시보드') || lowerQuery.includes('dashboard')) {
      return 'dashboard';
    } else if (lowerQuery.includes('랜딩') || lowerQuery.includes('landing')) {
      return 'landing-page';
    } else if (lowerQuery.includes('관리') || lowerQuery.includes('admin')) {
      return 'admin-panel';
    } else if (lowerQuery.includes('todo') || lowerQuery.includes('할일')) {
      return 'todo-app';
    } else if (lowerQuery.includes('근태') || lowerQuery.includes('출퇴근')) {
      return 'attendance-system';
    } else if (lowerQuery.includes('채팅') || lowerQuery.includes('chat')) {
      return 'chat-app';
    }
    
    return 'web-application';
  }
  
  private extractFunctionalRequirements(query: string): string[] {
    const requirements: string[] = [];
    const lowerQuery = query.toLowerCase();
    
    // CRUD 작업 감지
    if (lowerQuery.includes('작성') || lowerQuery.includes('쓰기') || lowerQuery.includes('생성')) {
      requirements.push('Create functionality');
    }
    if (lowerQuery.includes('읽기') || lowerQuery.includes('보기') || lowerQuery.includes('조회')) {
      requirements.push('Read/View functionality');
    }
    if (lowerQuery.includes('수정') || lowerQuery.includes('편집') || lowerQuery.includes('업데이트')) {
      requirements.push('Update/Edit functionality');
    }
    if (lowerQuery.includes('삭제') || lowerQuery.includes('제거')) {
      requirements.push('Delete functionality');
    }
    
    // 인증 관련
    if (lowerQuery.includes('로그인') || lowerQuery.includes('login')) {
      requirements.push('User authentication');
    }
    if (lowerQuery.includes('회원가입') || lowerQuery.includes('signup')) {
      requirements.push('User registration');
    }
    
    // 검색 기능
    if (lowerQuery.includes('검색') || lowerQuery.includes('search')) {
      requirements.push('Search functionality');
    }
    
    // 파일 업로드
    if (lowerQuery.includes('업로드') || lowerQuery.includes('upload')) {
      requirements.push('File upload');
    }
    
    // QR 코드
    if (lowerQuery.includes('qr')) {
      requirements.push('QR code generation/scanning');
    }
    
    // 데이터베이스
    if (lowerQuery.includes('데이터베이스') || lowerQuery.includes('db') || lowerQuery.includes('디비')) {
      requirements.push('Database integration');
    }
    
    return requirements.length > 0 ? requirements : ['Basic web functionality'];
  }
  
  private extractNonFunctionalRequirements(query: string): string[] {
    const requirements: string[] = [];
    const lowerQuery = query.toLowerCase();
    
    if (lowerQuery.includes('반응형') || lowerQuery.includes('responsive')) {
      requirements.push('Responsive design');
    }
    if (lowerQuery.includes('실시간') || lowerQuery.includes('real-time')) {
      requirements.push('Real-time updates');
    }
    if (lowerQuery.includes('보안') || lowerQuery.includes('secure')) {
      requirements.push('Security features');
    }
    if (lowerQuery.includes('빠른') || lowerQuery.includes('fast')) {
      requirements.push('Performance optimization');
    }
    if (lowerQuery.includes('모바일')) {
      requirements.push('Mobile-friendly');
    }
    
    return requirements;
  }
  
  private extractTechnologyPreferences(query: string, framework?: string): any {
    const prefs: any = {};
    const lowerQuery = query.toLowerCase();
    
    // Framework
    if (framework && framework !== 'auto-detect') {
      prefs.framework = framework;
    } else if (lowerQuery.includes('react')) {
      prefs.framework = 'react';
    } else if (lowerQuery.includes('vue')) {
      prefs.framework = 'vue';
    } else if (lowerQuery.includes('angular')) {
      prefs.framework = 'angular';
    } else {
      prefs.framework = 'react'; // 기본값
    }
    
    // Database
    if (lowerQuery.includes('mysql')) {
      prefs.database = 'mysql';
    } else if (lowerQuery.includes('postgres')) {
      prefs.database = 'postgresql';
    } else if (lowerQuery.includes('mongodb')) {
      prefs.database = 'mongodb';
    } else if (lowerQuery.includes('데이터베이스') || lowerQuery.includes('db')) {
      prefs.database = 'sqlite'; // 기본값
    }
    
    // Styling
    if (lowerQuery.includes('tailwind')) {
      prefs.styling = 'tailwind';
    } else if (lowerQuery.includes('bootstrap')) {
      prefs.styling = 'bootstrap';
    } else if (lowerQuery.includes('material')) {
      prefs.styling = 'material-ui';
    } else {
      prefs.styling = 'css';
    }
    
    // Features
    prefs.features = [];
    if (lowerQuery.includes('인증') || lowerQuery.includes('auth')) {
      prefs.features.push('authentication');
    }
    if (lowerQuery.includes('api')) {
      prefs.features.push('api-integration');
    }
    if (lowerQuery.includes('차트') || lowerQuery.includes('chart')) {
      prefs.features.push('charts');
    }
    
    return prefs;
  }
  
  private extractEntities(query: string): any {
    const entities: any = {};
    const lowerQuery = query.toLowerCase();
    
    // Pages
    entities.pages = [];
    if (lowerQuery.includes('홈') || lowerQuery.includes('메인')) {
      entities.pages.push('HomePage');
    }
    if (lowerQuery.includes('로그인')) {
      entities.pages.push('LoginPage');
    }
    if (lowerQuery.includes('회원가입')) {
      entities.pages.push('SignupPage');
    }
    if (lowerQuery.includes('대시보드')) {
      entities.pages.push('DashboardPage');
    }
    if (lowerQuery.includes('프로필')) {
      entities.pages.push('ProfilePage');
    }
    
    // Components
    entities.components = [];
    if (lowerQuery.includes('헤더')) {
      entities.components.push('Header');
    }
    if (lowerQuery.includes('푸터')) {
      entities.components.push('Footer');
    }
    if (lowerQuery.includes('사이드바')) {
      entities.components.push('Sidebar');
    }
    if (lowerQuery.includes('네비게이션')) {
      entities.components.push('Navigation');
    }
    if (lowerQuery.includes('폼') || lowerQuery.includes('form')) {
      entities.components.push('Form');
    }
    if (lowerQuery.includes('테이블') || lowerQuery.includes('목록')) {
      entities.components.push('Table');
    }
    if (lowerQuery.includes('카드')) {
      entities.components.push('Card');
    }
    if (lowerQuery.includes('버튼')) {
      entities.components.push('Button');
    }
    if (lowerQuery.includes('qr')) {
      entities.components.push('QRScanner', 'QRDisplay');
    }
    
    // Actions
    entities.actions = [];
    if (lowerQuery.includes('로그인')) {
      entities.actions.push('login');
    }
    if (lowerQuery.includes('로그아웃')) {
      entities.actions.push('logout');
    }
    if (lowerQuery.includes('저장')) {
      entities.actions.push('save');
    }
    if (lowerQuery.includes('삭제')) {
      entities.actions.push('delete');
    }
    if (lowerQuery.includes('검색')) {
      entities.actions.push('search');
    }
    if (lowerQuery.includes('출근')) {
      entities.actions.push('checkIn');
    }
    if (lowerQuery.includes('퇴근')) {
      entities.actions.push('checkOut');
    }
    
    // Data Models
    entities.dataModels = [];
    if (lowerQuery.includes('사용자') || lowerQuery.includes('유저')) {
      entities.dataModels.push('User');
    }
    if (lowerQuery.includes('포스트') || lowerQuery.includes('글')) {
      entities.dataModels.push('Post');
    }
    if (lowerQuery.includes('상품') || lowerQuery.includes('제품')) {
      entities.dataModels.push('Product');
    }
    if (lowerQuery.includes('주문')) {
      entities.dataModels.push('Order');
    }
    if (lowerQuery.includes('근태') || lowerQuery.includes('출퇴근')) {
      entities.dataModels.push('Attendance');
    }
    if (lowerQuery.includes('직원')) {
      entities.dataModels.push('Employee');
    }
    
    return entities;
  }
  
  private extractConstraints(query: string): string[] {
    const constraints: string[] = [];
    const lowerQuery = query.toLowerCase();
    
    if (lowerQuery.includes('간단한') || lowerQuery.includes('simple')) {
      constraints.push('Keep it simple');
    }
    if (lowerQuery.includes('빠르게') || lowerQuery.includes('quickly')) {
      constraints.push('Quick implementation');
    }
    if (lowerQuery.includes('기본')) {
      constraints.push('Basic features only');
    }
    if (lowerQuery.includes('무료')) {
      constraints.push('Use free resources only');
    }
    
    return constraints;
  }
  
  private calculateConfidence(query: string, requirements: string[]): number {
    // 쿼리 길이와 추출된 요구사항 수를 기반으로 신뢰도 계산
    const queryWords = query.split(' ').length;
    const reqCount = requirements.length;
    
    let confidence = 0.5; // 기본 신뢰도
    
    if (queryWords > 10) confidence += 0.2;
    if (queryWords > 20) confidence += 0.1;
    if (reqCount > 3) confidence += 0.15;
    if (reqCount > 5) confidence += 0.05;
    
    return Math.min(confidence, 1.0);
  }
}