import React from 'react';

// 런타임 코드 스플리팅 컴포넌트
export const LazyComponent = (importFunc: () => Promise<any>) => {
  return React.lazy(async () => {
    const startTime = performance.now();
    
    try {
      const module = await importFunc();
      const loadTime = performance.now() - startTime;
      
      // 로딩 성능 메트릭
      if (window.performance && window.performance.measure) {
        window.performance.measure('component-load', {
          start: startTime,
          duration: loadTime
        });
      }
      
      return module;
    } catch (error) {
      console.error('Failed to load component:', error);
      
      // 폴백 컴포넌트 반환
      return {
        default: () => <div>Failed to load component</div>
      };
    }
  });
};

// 프리페치 매니저
export class PrefetchManager {
  private prefetchQueue: Set<string> = new Set();
  private observer: IntersectionObserver;
  
  constructor() {
    // Intersection Observer로 뷰포트 진입 감지
    this.observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const component = entry.target.getAttribute('data-prefetch');
            if (component) {
              this.prefetchComponent(component);
            }
          }
        });
      },
      { rootMargin: '50px' }
    );
  }
  
  // 컴포넌트 프리페치
  async prefetchComponent(componentPath: string): Promise<void> {
    if (this.prefetchQueue.has(componentPath)) {
      return;
    }
    
    this.prefetchQueue.add(componentPath);
    
    try {
      // 네트워크가 idle 상태일 때 프리페치
      if ('requestIdleCallback' in window) {
        (window as any).requestIdleCallback(() => {
          import(componentPath);
        });
      } else {
        // 폴백: setTimeout 사용
        setTimeout(() => {
          import(componentPath);
        }, 1);
      }
    } catch (error) {
      console.error(`Failed to prefetch ${componentPath}:`, error);
    }
  }
  
  // 라우트 기반 프리페치
  prefetchRoute(route: string): void {
    const routeComponents: Record<string, string[]> = {
      '/dashboard': [
        './features/dashboard/index',
        './features/analytics/index'
      ],
      '/projects': [
        './features/projects/index',
        './features/editor/index'
      ],
      '/components': [
        './features/components/index',
        './features/search/index'
      ]
    };
    
    const components = routeComponents[route] || [];
    components.forEach(comp => this.prefetchComponent(comp));
  }
  
  // 엘리먼트 관찰 시작
  observe(element: HTMLElement): void {
    this.observer.observe(element);
  }
  
  // 정리
  disconnect(): void {
    this.observer.disconnect();
    this.prefetchQueue.clear();
  }
}