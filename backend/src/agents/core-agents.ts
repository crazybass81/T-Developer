// T-Developer 9 Core Agents using Agno Framework
import { Agent as AgnoAgent } from 'agno';

export class CoreAgents {
  static createNLInputAgent(): AgnoAgent {
    return new AgnoAgent({
      name: 'nl-input',
      role: 'Natural Language Requirements Processor',
      model: 'anthropic.claude-3-sonnet',
      instructions: [
        'Extract technical requirements from natural language',
        'Identify project type and complexity',
        'Determine technology stack preferences'
      ]
    });
  }

  static createUISelectionAgent(): AgnoAgent {
    return new AgnoAgent({
      name: 'ui-selection',
      role: 'UI Framework Selection Specialist',
      model: 'anthropic.claude-3-sonnet',
      instructions: [
        'Recommend optimal UI frameworks',
        'Analyze design system requirements',
        'Select component libraries'
      ]
    });
  }

  static createParsingAgent(): AgnoAgent {
    return new AgnoAgent({
      name: 'parsing',
      role: 'Code Analysis and Parsing Expert',
      model: 'amazon.nova-pro',
      instructions: [
        'Parse codebases and extract patterns',
        'Identify reusable components',
        'Map dependencies and relationships'
      ]
    });
  }

  static createComponentDecisionAgent(): AgnoAgent {
    return new AgnoAgent({
      name: 'component-decision',
      role: 'Architecture Decision Maker',
      model: 'anthropic.claude-3-opus',
      instructions: [
        'Make architectural component decisions',
        'Evaluate component compatibility',
        'Assess technical trade-offs'
      ]
    });
  }

  static createMatchingRateAgent(): AgnoAgent {
    return new AgnoAgent({
      name: 'matching-rate',
      role: 'Component Compatibility Scorer',
      model: 'amazon.nova-lite',
      instructions: [
        'Calculate component compatibility scores',
        'Predict integration complexity',
        'Identify potential conflicts'
      ]
    });
  }

  static createSearchAgent(): AgnoAgent {
    return new AgnoAgent({
      name: 'search',
      role: 'Component Discovery Specialist',
      model: 'amazon.nova-pro',
      instructions: [
        'Search component repositories',
        'Evaluate component quality',
        'Rank search results by relevance'
      ]
    });
  }

  static createGenerationAgent(): AgnoAgent {
    return new AgnoAgent({
      name: 'generation',
      role: 'Code Generation Expert',
      model: 'anthropic.claude-3-opus',
      instructions: [
        'Generate optimized code components',
        'Create tests and documentation',
        'Apply best practices and patterns'
      ]
    });
  }

  static createAssemblyAgent(): AgnoAgent {
    return new AgnoAgent({
      name: 'assembly',
      role: 'Service Integration Orchestrator',
      model: 'amazon.nova-pro',
      instructions: [
        'Integrate components into services',
        'Configure deployment artifacts',
        'Setup monitoring and logging'
      ]
    });
  }

  static createDownloadAgent(): AgnoAgent {
    return new AgnoAgent({
      name: 'download',
      role: 'Project Packaging Specialist',
      model: 'amazon.nova-lite',
      instructions: [
        'Package projects in multiple formats',
        'Create deployment artifacts',
        'Generate installation documentation'
      ]
    });
  }
}