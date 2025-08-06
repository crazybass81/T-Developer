export interface Decision {
  agentName: string;
  confidence: number;
  reasoning: string;
  alternativeAgents?: string[];
}

export interface Intent {
  description: string;
  type: string;
  priority: number;
  context: Record<string, any>;
}

export class DecisionEngine {
  private decisionHistory: Map<string, Decision[]> = new Map();
  private rules: Array<{ pattern: RegExp; agents: string[]; confidence: number }>;

  constructor() {
    this.initializeRules();
  }

  async determineAgents(intent: Intent): Promise<Decision[]> {
    // 1. Rule-based matching
    const ruleBasedAgents = this.matchByRules(intent);
    
    // 2. Historical pattern analysis
    const historicalPatterns = this.analyzeHistory(intent);
    
    // 3. Combine decisions
    const combinedDecisions = this.combineDecisions(ruleBasedAgents, historicalPatterns);
    
    // 4. Store decision for learning
    this.decisionHistory.set(intent.description, combinedDecisions);
    
    return combinedDecisions;
  }

  private matchByRules(intent: Intent): Decision[] {
    const decisions: Decision[] = [];

    for (const rule of this.rules) {
      if (rule.pattern.test(intent.description)) {
        for (const agent of rule.agents) {
          decisions.push({
            agentName: agent,
            confidence: rule.confidence,
            reasoning: `Rule-based match: ${rule.pattern.source}`
          });
        }
      }
    }

    return decisions;
  }

  private analyzeHistory(intent: Intent): Decision[] {
    const historicalDecisions: Decision[] = [];
    
    // Find similar past intents
    for (const [pastIntent, decisions] of this.decisionHistory) {
      const similarity = this.calculateSimilarity(intent.description, pastIntent);
      
      if (similarity > 0.7) {
        for (const decision of decisions) {
          historicalDecisions.push({
            ...decision,
            confidence: decision.confidence * similarity,
            reasoning: `Historical pattern match (${(similarity * 100).toFixed(1)}% similar)`
          });
        }
      }
    }

    return historicalDecisions;
  }

  private combineDecisions(
    ruleBasedAgents: Decision[],
    historicalPatterns: Decision[]
  ): Decision[] {
    const agentScores = new Map<string, { confidence: number; reasoning: string[] }>();

    // Process rule-based decisions
    for (const decision of ruleBasedAgents) {
      const existing = agentScores.get(decision.agentName) || { confidence: 0, reasoning: [] };
      existing.confidence += decision.confidence * 0.7; // Rule-based weight
      existing.reasoning.push(decision.reasoning);
      agentScores.set(decision.agentName, existing);
    }

    // Process historical decisions
    for (const decision of historicalPatterns) {
      const existing = agentScores.get(decision.agentName) || { confidence: 0, reasoning: [] };
      existing.confidence += decision.confidence * 0.3; // Historical weight
      existing.reasoning.push(decision.reasoning);
      agentScores.set(decision.agentName, existing);
    }

    // Convert to Decision array and sort by confidence
    const finalDecisions: Decision[] = Array.from(agentScores.entries())
      .map(([agentName, data]) => ({
        agentName,
        confidence: Math.min(data.confidence, 1.0), // Cap at 1.0
        reasoning: data.reasoning.join('; ')
      }))
      .sort((a, b) => b.confidence - a.confidence);

    return finalDecisions;
  }

  private calculateSimilarity(text1: string, text2: string): number {
    // Simple word-based similarity calculation
    const words1 = text1.toLowerCase().split(/\s+/);
    const words2 = text2.toLowerCase().split(/\s+/);
    
    const set1 = new Set(words1);
    const set2 = new Set(words2);
    
    const intersection = new Set([...set1].filter(x => set2.has(x)));
    const union = new Set([...set1, ...set2]);
    
    return intersection.size / union.size;
  }

  private initializeRules(): void {
    this.rules = [
      {
        pattern: /code|implement|develop|program|build/i,
        agents: ['GenerationAgent', 'AssemblyAgent'],
        confidence: 0.9
      },
      {
        pattern: /test|verify|validate|check/i,
        agents: ['ParserAgent'],
        confidence: 0.8
      },
      {
        pattern: /design|architect|structure|layout/i,
        agents: ['UISelectionAgent', 'ComponentDecisionAgent'],
        confidence: 0.85
      },
      {
        pattern: /security|secure|protect|vulnerability/i,
        agents: ['ParserAgent'],
        confidence: 0.9
      },
      {
        pattern: /search|find|look|discover/i,
        agents: ['SearchAgent', 'MatchRateAgent'],
        confidence: 0.8
      },
      {
        pattern: /download|package|deploy|deliver/i,
        agents: ['DownloadAgent', 'AssemblyAgent'],
        confidence: 0.9
      },
      {
        pattern: /analyze|parse|understand|interpret/i,
        agents: ['NLInputAgent', 'ParserAgent'],
        confidence: 0.85
      },
      {
        pattern: /ui|interface|frontend|component/i,
        agents: ['UISelectionAgent', 'ComponentDecisionAgent'],
        confidence: 0.8
      }
    ];
  }

  getDecisionHistory(): Map<string, Decision[]> {
    return new Map(this.decisionHistory);
  }

  clearHistory(): void {
    this.decisionHistory.clear();
  }
}