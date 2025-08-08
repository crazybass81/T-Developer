/**
 * UI Selection Agent - UI 프레임워크 및 컴포넌트 라이브러리 선택
 * NL Input Agent의 결과를 받아 최적의 UI 기술 스택을 선택
 */

import { ProjectRequirements } from './nl-input-agent';

export interface UISelectionResult {
  framework: string;
  componentLibrary: string;
  stylingApproach: string;
  stateManagement?: string;
  routing?: string;
  buildTool: string;
  dependencies: string[];
  rationale: string;
  estimatedComplexity: 'low' | 'medium' | 'high';
}

export class UISelectionAgent {
  private name = 'UI Selection Agent';

  /**
   * 프로젝트 요구사항을 기반으로 최적의 UI 기술 스택 선택
   */
  async selectUIStack(requirements: ProjectRequirements): Promise<UISelectionResult> {
    console.log(`[${this.name}] Selecting UI stack for project type: ${requirements.projectType}`);

    const framework = this.selectFramework(requirements);
    const componentLibrary = this.selectComponentLibrary(framework, requirements);
    const stylingApproach = this.selectStylingApproach(requirements);
    const stateManagement = this.selectStateManagement(framework, requirements);
    const routing = this.selectRouting(framework);
    const buildTool = this.selectBuildTool(framework);
    const dependencies = this.gatherDependencies(framework, componentLibrary, stateManagement);
    const complexity = this.estimateComplexity(requirements);

    return {
      framework,
      componentLibrary,
      stylingApproach,
      stateManagement,
      routing,
      buildTool,
      dependencies,
      rationale: this.generateRationale(framework, requirements),
      estimatedComplexity: complexity
    };
  }

  private selectFramework(requirements: ProjectRequirements): string {
    const { technologyPreferences, projectType, functionalRequirements } = requirements;
    
    // 사용자가 명시적으로 프레임워크를 지정한 경우
    if (technologyPreferences.framework) {
      return technologyPreferences.framework;
    }

    // 프로젝트 타입별 추천
    switch (projectType) {
      case 'e-commerce':
      case 'blog':
        return 'nextjs'; // SEO가 중요한 경우
      case 'dashboard':
      case 'admin-panel':
        return 'react'; // 복잡한 상태 관리가 필요한 경우
      case 'landing-page':
        return 'vue'; // 간단하고 빠른 개발
      case 'attendance-system':
        return 'react'; // 실시간 업데이트 필요
      default:
        return 'react'; // 기본값
    }
  }

  private selectComponentLibrary(framework: string, requirements: ProjectRequirements): string {
    const projectType = requirements.projectType;

    if (framework === 'react' || framework === 'nextjs') {
      if (projectType === 'dashboard' || projectType === 'admin-panel') {
        return 'antd'; // Ant Design for admin interfaces
      } else if (projectType === 'e-commerce') {
        return 'mui'; // Material-UI for e-commerce
      } else {
        return 'chakra-ui'; // Chakra UI for modern applications
      }
    } else if (framework === 'vue') {
      return 'vuetify'; // Vuetify for Vue
    } else if (framework === 'angular') {
      return 'angular-material'; // Angular Material
    }

    return 'native'; // No component library
  }

  private selectStylingApproach(requirements: ProjectRequirements): string {
    const { technologyPreferences, nonFunctionalRequirements } = requirements;

    if (technologyPreferences.styling) {
      return technologyPreferences.styling;
    }

    // 반응형 디자인이 필요한 경우
    if (nonFunctionalRequirements.includes('Responsive design')) {
      return 'tailwind';
    }

    // 빠른 개발이 필요한 경우
    if (requirements.constraints.includes('Quick implementation')) {
      return 'bootstrap';
    }

    return 'styled-components'; // 기본값
  }

  private selectStateManagement(framework: string, requirements: ProjectRequirements): string | undefined {
    const { functionalRequirements, projectType } = requirements;

    // 간단한 프로젝트는 상태 관리 라이브러리 불필요
    if (projectType === 'landing-page' || requirements.constraints.includes('Keep it simple')) {
      return undefined;
    }

    if (framework === 'react' || framework === 'nextjs') {
      // 복잡한 상태 관리가 필요한 경우
      if (projectType === 'dashboard' || projectType === 'admin-panel' || projectType === 'e-commerce') {
        return 'redux-toolkit';
      }
      // 중간 복잡도
      return 'zustand';
    } else if (framework === 'vue') {
      return 'pinia';
    } else if (framework === 'angular') {
      return 'ngrx';
    }

    return undefined;
  }

  private selectRouting(framework: string): string {
    switch (framework) {
      case 'react':
        return 'react-router-dom';
      case 'nextjs':
        return 'nextjs-app-router';
      case 'vue':
        return 'vue-router';
      case 'angular':
        return 'angular-router';
      default:
        return 'none';
    }
  }

  private selectBuildTool(framework: string): string {
    switch (framework) {
      case 'react':
      case 'vue':
        return 'vite';
      case 'nextjs':
        return 'nextjs';
      case 'angular':
        return 'angular-cli';
      default:
        return 'vite';
    }
  }

  private gatherDependencies(framework: string, componentLibrary: string, stateManagement?: string): string[] {
    const deps: string[] = [];

    // Framework dependencies
    switch (framework) {
      case 'react':
        deps.push('react', 'react-dom');
        break;
      case 'nextjs':
        deps.push('next', 'react', 'react-dom');
        break;
      case 'vue':
        deps.push('vue');
        break;
      case 'angular':
        deps.push('@angular/core', '@angular/common');
        break;
    }

    // Component library dependencies
    switch (componentLibrary) {
      case 'mui':
        deps.push('@mui/material', '@emotion/react', '@emotion/styled');
        break;
      case 'antd':
        deps.push('antd');
        break;
      case 'chakra-ui':
        deps.push('@chakra-ui/react', '@emotion/react', '@emotion/styled');
        break;
      case 'vuetify':
        deps.push('vuetify');
        break;
    }

    // State management
    if (stateManagement) {
      switch (stateManagement) {
        case 'redux-toolkit':
          deps.push('@reduxjs/toolkit', 'react-redux');
          break;
        case 'zustand':
          deps.push('zustand');
          break;
        case 'pinia':
          deps.push('pinia');
          break;
      }
    }

    return deps;
  }

  private estimateComplexity(requirements: ProjectRequirements): 'low' | 'medium' | 'high' {
    const { functionalRequirements, extractedEntities } = requirements;
    
    const totalFeatures = functionalRequirements.length;
    const totalPages = extractedEntities.pages?.length || 0;
    const totalComponents = extractedEntities.components?.length || 0;

    const score = totalFeatures + totalPages + totalComponents;

    if (score < 10) return 'low';
    if (score < 20) return 'medium';
    return 'high';
  }

  private generateRationale(framework: string, requirements: ProjectRequirements): string {
    const reasons: string[] = [];

    if (requirements.technologyPreferences.framework) {
      reasons.push(`User specifically requested ${framework}`);
    } else {
      switch (requirements.projectType) {
        case 'e-commerce':
        case 'blog':
          reasons.push(`Selected ${framework} for better SEO capabilities`);
          break;
        case 'dashboard':
          reasons.push(`Selected ${framework} for complex state management`);
          break;
        default:
          reasons.push(`Selected ${framework} as the most versatile option`);
      }
    }

    return reasons.join('. ');
  }
}