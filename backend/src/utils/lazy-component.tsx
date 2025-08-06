import React from 'react';

// 런타임 코드 스플리팅 컴포넌트
export const LazyComponent = (importFunc: () => Promise<any>) => {
  return React.lazy(async () => {
    const startTime = performance.now();
    
    try {
      const module = await importFunc();
      const loadTime = performance.now() - startTime;
      
      // 로딩 성능 메트릭
      if (typeof window !== 'undefined' && window.performance && window.performance.measure) {
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
        default: () => React.createElement('div', null, 'Failed to load component')
      };
    }
  });
};

// 프리페치 매니저
export class PrefetchManager {
  private prefetchQueue: Set<string> = new Set();
  private observer: IntersectionObserver | null = null;
  
  constructor() {
    if (typeof window !== 'undefined' && 'IntersectionObserver' in window) {
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
  }
  
  async prefetchComponent(componentPath: string): Promise<void> {
    if (this.prefetchQueue.has(componentPath)) {
      return;
    }
    
    this.prefetchQueue.add(componentPath);
    
    try {
      if (typeof window !== 'undefined' && 'requestIdleCallback' in window) {
        (window as any).requestIdleCallback(() => {
          import(componentPath);
        });
      } else {
        setTimeout(() => {
          import(componentPath);
        }, 1);
      }
    } catch (error) {
      console.error(`Failed to prefetch ${componentPath}:`, error);
    }
  }
  
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
  
  observe(element: HTMLElement): void {
    if (this.observer) {
      this.observer.observe(element);
    }
  }
  
  disconnect(): void {
    if (this.observer) {
      this.observer.disconnect();
    }
    this.prefetchQueue.clear();
  }
}