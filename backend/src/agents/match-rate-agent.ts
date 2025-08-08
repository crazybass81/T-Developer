/**
 * Match Rate Agent - 컴포넌트 매칭 및 재사용성 평가
 * Component Decision Agent의 결과를 받아 기존 템플릿/라이브러리와의 매칭률 계산
 */

import { ComponentDecision } from './component-decision-agent';
import { UISelectionResult } from './ui-selection-agent';

export interface MatchRateResult {
  componentName: string;
  matches: ComponentMatch[];
  bestMatch: ComponentMatch | null;
  recommendedAction: 'use-library' | 'use-template' | 'generate-custom';
  matchScore: number;
  reuseability: number;
}

export interface ComponentMatch {
  source: 'library' | 'template' | 'snippet';
  name: string;
  library?: string;
  matchScore: number;
  compatibility: number;
  features: string[];
  missingFeatures: string[];
  installCommand?: string;
  importStatement?: string;
}

export interface TemplateLibrary {
  id: string;
  name: string;
  components: TemplateComponent[];
  framework: string;
  version: string;
}

export interface TemplateComponent {
  name: string;
  type: string;
  props: string[];
  features: string[];
  code?: string;
}

export class MatchRateAgent {
  private name = 'Match Rate Agent';
  private templateLibraries: TemplateLibrary[];

  constructor() {
    this.templateLibraries = this.initializeTemplateLibraries();
  }

  /**
   * 컴포넌트 결정사항을 기반으로 매칭률 계산
   */
  async calculateMatchRates(
    componentDecisions: ComponentDecision[],
    uiSelection: UISelectionResult
  ): Promise<MatchRateResult[]> {
    console.log(`[${this.name}] Calculating match rates for ${componentDecisions.length} components`);

    const results: MatchRateResult[] = [];

    for (const decision of componentDecisions) {
      const result = await this.calculateMatchRateForComponent(decision, uiSelection);
      results.push(result);
    }

    return results;
  }

  private async calculateMatchRateForComponent(
    decision: ComponentDecision,
    uiSelection: UISelectionResult
  ): Promise<MatchRateResult> {
    const matches = this.findMatches(decision, uiSelection);
    const bestMatch = this.selectBestMatch(matches);
    const recommendedAction = this.determineAction(bestMatch);
    const matchScore = bestMatch ? bestMatch.matchScore : 0;
    const reuseability = this.calculateReuseability(decision, matches);

    return {
      componentName: decision.componentName,
      matches,
      bestMatch,
      recommendedAction,
      matchScore,
      reuseability
    };
  }

  private findMatches(
    decision: ComponentDecision,
    uiSelection: UISelectionResult
  ): ComponentMatch[] {
    const matches: ComponentMatch[] = [];

    // 1. Component library에서 매칭 찾기
    const libraryMatches = this.findLibraryMatches(decision, uiSelection);
    matches.push(...libraryMatches);

    // 2. Template library에서 매칭 찾기
    const templateMatches = this.findTemplateMatches(decision, uiSelection);
    matches.push(...templateMatches);

    // 3. Code snippets에서 매칭 찾기
    const snippetMatches = this.findSnippetMatches(decision);
    matches.push(...snippetMatches);

    return matches.sort((a, b) => b.matchScore - a.matchScore);
  }

  private findLibraryMatches(
    decision: ComponentDecision,
    uiSelection: UISelectionResult
  ): ComponentMatch[] {
    const matches: ComponentMatch[] = [];
    const { componentLibrary } = uiSelection;

    // Ant Design 컴포넌트 매칭
    if (componentLibrary === 'antd') {
      const antdMatch = this.matchAntDesignComponent(decision);
      if (antdMatch) matches.push(antdMatch);
    }

    // Material-UI 컴포넌트 매칭
    if (componentLibrary === 'mui') {
      const muiMatch = this.matchMaterialUIComponent(decision);
      if (muiMatch) matches.push(muiMatch);
    }

    // Chakra UI 컴포넌트 매칭
    if (componentLibrary === 'chakra-ui') {
      const chakraMatch = this.matchChakraUIComponent(decision);
      if (chakraMatch) matches.push(chakraMatch);
    }

    return matches;
  }

  private matchAntDesignComponent(decision: ComponentDecision): ComponentMatch | null {
    const antdComponents: Record<string, ComponentMatch> = {
      'Button': {
        source: 'library',
        name: 'Button',
        library: 'antd',
        matchScore: 0.95,
        compatibility: 1.0,
        features: ['onClick', 'type', 'disabled', 'loading', 'icon'],
        missingFeatures: [],
        installCommand: 'npm install antd',
        importStatement: "import { Button } from 'antd';"
      },
      'Form': {
        source: 'library',
        name: 'Form',
        library: 'antd',
        matchScore: 0.90,
        compatibility: 0.95,
        features: ['onSubmit', 'initialValues', 'validation', 'layout'],
        missingFeatures: [],
        installCommand: 'npm install antd',
        importStatement: "import { Form, Input } from 'antd';"
      },
      'Table': {
        source: 'library',
        name: 'Table',
        library: 'antd',
        matchScore: 0.92,
        compatibility: 0.98,
        features: ['dataSource', 'columns', 'pagination', 'sorting', 'filtering'],
        missingFeatures: [],
        installCommand: 'npm install antd',
        importStatement: "import { Table } from 'antd';"
      },
      'Card': {
        source: 'library',
        name: 'Card',
        library: 'antd',
        matchScore: 0.88,
        compatibility: 0.95,
        features: ['title', 'extra', 'actions', 'bordered'],
        missingFeatures: [],
        installCommand: 'npm install antd',
        importStatement: "import { Card } from 'antd';"
      }
    };

    return antdComponents[decision.componentName] || null;
  }

  private matchMaterialUIComponent(decision: ComponentDecision): ComponentMatch | null {
    const muiComponents: Record<string, ComponentMatch> = {
      'Button': {
        source: 'library',
        name: 'Button',
        library: '@mui/material',
        matchScore: 0.93,
        compatibility: 0.98,
        features: ['onClick', 'variant', 'disabled', 'color', 'size'],
        missingFeatures: [],
        installCommand: 'npm install @mui/material @emotion/react @emotion/styled',
        importStatement: "import Button from '@mui/material/Button';"
      },
      'Table': {
        source: 'library',
        name: 'Table',
        library: '@mui/material',
        matchScore: 0.85,
        compatibility: 0.90,
        features: ['rows', 'columns', 'pagination'],
        missingFeatures: ['built-in sorting'],
        installCommand: 'npm install @mui/material',
        importStatement: "import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';"
      }
    };

    return muiComponents[decision.componentName] || null;
  }

  private matchChakraUIComponent(decision: ComponentDecision): ComponentMatch | null {
    const chakraComponents: Record<string, ComponentMatch> = {
      'Button': {
        source: 'library',
        name: 'Button',
        library: '@chakra-ui/react',
        matchScore: 0.91,
        compatibility: 0.96,
        features: ['onClick', 'colorScheme', 'isDisabled', 'isLoading', 'leftIcon'],
        missingFeatures: [],
        installCommand: 'npm install @chakra-ui/react @emotion/react @emotion/styled',
        importStatement: "import { Button } from '@chakra-ui/react';"
      },
      'Form': {
        source: 'library',
        name: 'FormControl',
        library: '@chakra-ui/react',
        matchScore: 0.87,
        compatibility: 0.92,
        features: ['isRequired', 'isInvalid', 'label', 'helperText'],
        missingFeatures: ['built-in validation'],
        installCommand: 'npm install @chakra-ui/react',
        importStatement: "import { FormControl, FormLabel, Input } from '@chakra-ui/react';"
      }
    };

    return chakraComponents[decision.componentName] || null;
  }

  private findTemplateMatches(
    decision: ComponentDecision,
    uiSelection: UISelectionResult
  ): ComponentMatch[] {
    const matches: ComponentMatch[] = [];
    
    // Find matching templates from our library
    for (const library of this.templateLibraries) {
      if (library.framework !== uiSelection.framework) continue;
      
      for (const template of library.components) {
        const matchScore = this.calculateTemplateMatchScore(decision, template);
        if (matchScore > 0.5) {
          matches.push({
            source: 'template',
            name: template.name,
            library: library.name,
            matchScore,
            compatibility: this.calculateCompatibility(decision, template),
            features: template.features,
            missingFeatures: this.findMissingFeatures(decision, template),
            importStatement: `// Custom template from ${library.name}`
          });
        }
      }
    }

    return matches;
  }

  private findSnippetMatches(decision: ComponentDecision): ComponentMatch[] {
    const snippets: ComponentMatch[] = [];

    // Basic component snippets
    const basicSnippets: Record<string, ComponentMatch> = {
      'Button': {
        source: 'snippet',
        name: 'BasicButton',
        matchScore: 0.60,
        compatibility: 0.80,
        features: ['onClick', 'className'],
        missingFeatures: ['variants', 'loading state'],
        importStatement: '// Basic button implementation'
      },
      'Form': {
        source: 'snippet',
        name: 'BasicForm',
        matchScore: 0.55,
        compatibility: 0.75,
        features: ['onSubmit', 'basic validation'],
        missingFeatures: ['advanced validation', 'field arrays'],
        importStatement: '// Basic form implementation'
      },
      'Table': {
        source: 'snippet',
        name: 'BasicTable',
        matchScore: 0.50,
        compatibility: 0.70,
        features: ['data display'],
        missingFeatures: ['sorting', 'pagination', 'filtering'],
        importStatement: '// Basic table implementation'
      }
    };

    const snippet = basicSnippets[decision.componentName];
    if (snippet) {
      snippets.push(snippet);
    }

    return snippets;
  }

  private calculateTemplateMatchScore(
    decision: ComponentDecision,
    template: TemplateComponent
  ): number {
    let score = 0;
    const totalFeatures = decision.props.length + decision.methods.length;
    
    // Check prop matching
    const matchingProps = decision.props.filter(prop => 
      template.props.includes(prop.name)
    ).length;
    
    // Check feature matching
    const requiredFeatures = [
      ...decision.props.map(p => p.name),
      ...decision.methods.map(m => m.name)
    ];
    
    const matchingFeatures = requiredFeatures.filter(feature =>
      template.features.includes(feature)
    ).length;
    
    score = (matchingProps + matchingFeatures) / (totalFeatures * 2);
    
    return Math.min(score, 1.0);
  }

  private calculateCompatibility(
    decision: ComponentDecision,
    template: TemplateComponent
  ): number {
    // Base compatibility score
    let compatibility = 0.7;
    
    // Check if component types match
    if (decision.componentType === 'functional' && template.type === 'functional') {
      compatibility += 0.2;
    }
    
    // Check prop compatibility
    const requiredProps = decision.props.filter(p => p.required);
    const hasAllRequired = requiredProps.every(prop => 
      template.props.includes(prop.name)
    );
    
    if (hasAllRequired) {
      compatibility += 0.1;
    }
    
    return Math.min(compatibility, 1.0);
  }

  private findMissingFeatures(
    decision: ComponentDecision,
    template: TemplateComponent
  ): string[] {
    const requiredFeatures = [
      ...decision.props.filter(p => p.required).map(p => p.name),
      ...decision.methods.map(m => m.name)
    ];
    
    return requiredFeatures.filter(feature => 
      !template.features.includes(feature)
    );
  }

  private selectBestMatch(matches: ComponentMatch[]): ComponentMatch | null {
    if (matches.length === 0) return null;
    
    // Prefer library components over templates and snippets
    const libraryMatches = matches.filter(m => m.source === 'library');
    if (libraryMatches.length > 0) {
      return libraryMatches[0];
    }
    
    // Then templates
    const templateMatches = matches.filter(m => m.source === 'template');
    if (templateMatches.length > 0) {
      return templateMatches[0];
    }
    
    // Finally snippets
    return matches[0];
  }

  private determineAction(match: ComponentMatch | null): 'use-library' | 'use-template' | 'generate-custom' {
    if (!match) return 'generate-custom';
    
    if (match.source === 'library' && match.matchScore > 0.85) {
      return 'use-library';
    }
    
    if (match.source === 'template' && match.matchScore > 0.70) {
      return 'use-template';
    }
    
    return 'generate-custom';
  }

  private calculateReuseability(
    decision: ComponentDecision,
    matches: ComponentMatch[]
  ): number {
    if (matches.length === 0) return 0;
    
    const bestMatch = matches[0];
    
    // Calculate reusability based on match score and missing features
    let reusability = bestMatch.matchScore;
    
    // Penalty for missing features
    const missingCount = bestMatch.missingFeatures.length;
    const totalFeatures = decision.props.length + decision.methods.length;
    
    if (totalFeatures > 0) {
      reusability *= (1 - (missingCount / totalFeatures) * 0.5);
    }
    
    return Math.max(0, Math.min(reusability, 1.0));
  }

  private initializeTemplateLibraries(): TemplateLibrary[] {
    return [
      {
        id: 'react-templates',
        name: 'React Component Templates',
        framework: 'react',
        version: '18.0',
        components: [
          {
            name: 'FormTemplate',
            type: 'functional',
            props: ['onSubmit', 'initialValues', 'validation'],
            features: ['validation', 'error handling', 'field management'],
            code: '// Template code here'
          },
          {
            name: 'TableTemplate',
            type: 'functional',
            props: ['data', 'columns', 'onSort'],
            features: ['sorting', 'pagination'],
            code: '// Template code here'
          }
        ]
      },
      {
        id: 'vue-templates',
        name: 'Vue Component Templates',
        framework: 'vue',
        version: '3.0',
        components: [
          {
            name: 'FormTemplate',
            type: 'composition',
            props: ['modelValue', 'rules'],
            features: ['v-model', 'validation'],
            code: '// Template code here'
          }
        ]
      }
    ];
  }
}