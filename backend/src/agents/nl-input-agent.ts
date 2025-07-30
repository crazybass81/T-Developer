import { BaseAgent } from './base-agent';
import { BedrockRuntimeClient, InvokeModelCommand } from '@aws-sdk/client-bedrock-runtime';
import { config } from '../config/environment';

export class NLInputAgent extends BaseAgent {
  private bedrockClient: BedrockRuntimeClient;

  constructor() {
    super('nl-input', 'processing');
  }

  protected async setup(): Promise<void> {
    this.bedrockClient = new BedrockRuntimeClient({
      region: config.aws.bedrockRegion,
      credentials: {
        accessKeyId: config.aws.accessKeyId!,
        secretAccessKey: config.aws.secretAccessKey!
      }
    });
  }

  protected validateInput(input: any): void {
    if (!input.description) {
      throw new Error('Project description is required');
    }
  }

  protected async process(input: any): Promise<any> {
    const { description, requirements = [] } = input;

    // Use Claude 3 Sonnet for natural language processing
    const prompt = `Analyze this project description and extract structured requirements:

Project Description: ${description}
Additional Requirements: ${requirements.join(', ')}

Please provide a JSON response with:
1. projectType (web, mobile, desktop, api, etc.)
2. targetPlatforms (array)
3. technicalRequirements (array)
4. functionalRequirements (array)
5. nonFunctionalRequirements (array)
6. suggestedTechnologies (object with categories)
7. complexity (low, medium, high)
8. estimatedTimeframe (string)

Respond only with valid JSON.`;

    const command = new InvokeModelCommand({
      modelId: 'anthropic.claude-3-sonnet-20240229-v1:0',
      body: JSON.stringify({
        anthropic_version: 'bedrock-2023-05-31',
        max_tokens: 2000,
        messages: [{
          role: 'user',
          content: prompt
        }]
      }),
      contentType: 'application/json'
    });

    const response = await this.bedrockClient.send(command);
    const responseBody = JSON.parse(new TextDecoder().decode(response.body));
    
    let analysisResult;
    try {
      analysisResult = JSON.parse(responseBody.content[0].text);
    } catch (error) {
      // Fallback parsing if JSON is malformed
      analysisResult = this.fallbackAnalysis(description, requirements);
    }

    return {
      projectType: analysisResult.projectType || 'web',
      targetPlatforms: analysisResult.targetPlatforms || ['web'],
      requirements: {
        technical: analysisResult.technicalRequirements || [],
        functional: analysisResult.functionalRequirements || [],
        nonFunctional: analysisResult.nonFunctionalRequirements || []
      },
      suggestedTechnologies: analysisResult.suggestedTechnologies || {},
      complexity: analysisResult.complexity || 'medium',
      estimatedTimeframe: analysisResult.estimatedTimeframe || '2-4 weeks',
      originalDescription: description,
      processedAt: new Date().toISOString()
    };
  }

  private fallbackAnalysis(description: string, requirements: string[]): any {
    // Simple keyword-based analysis as fallback
    const isWeb = /web|website|frontend|react|vue|angular/i.test(description);
    const isMobile = /mobile|app|ios|android|react native/i.test(description);
    const isAPI = /api|backend|server|microservice/i.test(description);

    let projectType = 'web';
    if (isMobile) projectType = 'mobile';
    else if (isAPI) projectType = 'api';

    return {
      projectType,
      targetPlatforms: projectType === 'mobile' ? ['ios', 'android'] : ['web'],
      technicalRequirements: requirements,
      functionalRequirements: ['User interface', 'Data processing'],
      nonFunctionalRequirements: ['Performance', 'Security'],
      suggestedTechnologies: {
        frontend: projectType === 'web' ? ['React', 'TypeScript'] : ['React Native'],
        backend: ['Node.js', 'Express'],
        database: ['PostgreSQL']
      },
      complexity: 'medium',
      estimatedTimeframe: '2-4 weeks'
    };
  }
}