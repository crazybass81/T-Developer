import AWS from 'aws-sdk';

const lambda = new AWS.Lambda({
  region: process.env.AWS_REGION || 'us-east-1'
});

export class LambdaIntegration {
  private stackName: string;

  constructor(stackName: string = 't-developer-lambda-prod') {
    this.stackName = stackName;
  }

  async invokeLambda(functionName: string, payload: any) {
    const params = {
      FunctionName: `${this.stackName}-${functionName}`,
      InvocationType: 'RequestResponse',
      Payload: JSON.stringify(payload)
    };

    try {
      const result = await lambda.invoke(params).promise();
      if (result.Payload) {
        return JSON.parse(result.Payload.toString());
      }
      return null;
    } catch (error) {
      console.error(`Error invoking Lambda ${functionName}:`, error);
      throw error;
    }
  }

  async invokeNLInputAgent(userInput: string, context: any) {
    return this.invokeLambda('nl-input-agent-development', {
      body: JSON.stringify({
        user_input: userInput,
        context
      })
    });
  }

  async invokeUISelectionAgent(requirements: any) {
    return this.invokeLambda('ui-selection-agent-development', {
      body: JSON.stringify({
        requirements
      })
    });
  }

  async invokeParserAgent(uiSelection: any, requirements: any) {
    return this.invokeLambda('parser-agent-development', {
      body: JSON.stringify({
        ui_selection: uiSelection,
        requirements
      })
    });
  }

  async invokeComponentDecisionAgent(projectStructure: any, uiSelection: any, requirements: any) {
    return this.invokeLambda('component-decision-agent-development', {
      body: JSON.stringify({
        project_structure: projectStructure,
        ui_selection: uiSelection,
        requirements
      })
    });
  }

  async invokeMatchRateAgent(componentDecisions: any, uiSelection: any) {
    return this.invokeLambda('match-rate-agent-development', {
      body: JSON.stringify({
        component_decisions: componentDecisions,
        ui_selection: uiSelection
      })
    });
  }

  async invokeSearchAgent(matchRateResults: any, componentDecisions: any) {
    return this.invokeLambda('search-agent-development', {
      body: JSON.stringify({
        match_rate_results: matchRateResults,
        component_decisions: componentDecisions
      })
    });
  }

  async invokeGenerationAgent(searchResults: any, projectStructure: any, uiSelection: any, projectName: string) {
    return this.invokeLambda('generation-agent-development', {
      body: JSON.stringify({
        search_results: searchResults,
        project_structure: projectStructure,
        ui_selection: uiSelection,
        project_name: projectName
      })
    });
  }

  async invokeAssemblyAgent(generatedProject: any) {
    return this.invokeLambda('assembly-agent-development', {
      body: JSON.stringify({
        generated_project: generatedProject
      })
    });
  }

  async invokeDownloadAgent(assembledProject: any) {
    return this.invokeLambda('download-agent-development', {
      body: JSON.stringify({
        assembled_project: assembledProject
      })
    });
  }

  async executePipeline(query: string, framework?: string) {
    console.log('[Lambda Pipeline] Starting 9-agent Lambda pipeline...');
    
    try {
      // Step 1: NL Input Agent
      console.log('[Lambda Pipeline] Step 1/9 - NL Input Agent');
      const nlResult = await this.invokeNLInputAgent(query, { framework });
      const nlData = JSON.parse(nlResult.body);
      
      // Step 2: UI Selection Agent  
      console.log('[Lambda Pipeline] Step 2/9 - UI Selection Agent');
      const uiResult = await this.invokeUISelectionAgent(nlData);
      const uiData = JSON.parse(uiResult.body);
      
      // Step 3: Parser Agent
      console.log('[Lambda Pipeline] Step 3/9 - Parser Agent');
      const parserResult = await this.invokeParserAgent(uiData, nlData.requirements);
      const parserData = JSON.parse(parserResult.body);
      
      // Step 4: Component Decision Agent
      console.log('[Lambda Pipeline] Step 4/9 - Component Decision Agent');
      const componentResult = await this.invokeComponentDecisionAgent(
        parserData, uiData, nlData.requirements
      );
      const componentData = JSON.parse(componentResult.body);
      
      // Step 5: Match Rate Agent
      console.log('[Lambda Pipeline] Step 5/9 - Match Rate Agent');
      const matchResult = await this.invokeMatchRateAgent(componentData, uiData);
      const matchData = JSON.parse(matchResult.body);
      
      // Step 6: Search Agent
      console.log('[Lambda Pipeline] Step 6/9 - Search Agent');
      const searchResult = await this.invokeSearchAgent(matchData, componentData);
      const searchData = JSON.parse(searchResult.body);
      
      // Step 7: Generation Agent
      console.log('[Lambda Pipeline] Step 7/9 - Generation Agent');
      const projectName = query.includes('QR') ? 'qr-attendance-system' : 
                         query.includes('블로그') ? 'blog-website' : 'web-application';
      const generationResult = await this.invokeGenerationAgent(
        searchData, parserData, uiData, projectName
      );
      const generationData = JSON.parse(generationResult.body);
      
      // Step 8: Assembly Agent
      console.log('[Lambda Pipeline] Step 8/9 - Assembly Agent');
      const assemblyResult = await this.invokeAssemblyAgent(generationData);
      const assemblyData = JSON.parse(assemblyResult.body);
      
      // Step 9: Download Agent
      console.log('[Lambda Pipeline] Step 9/9 - Download Agent');
      const downloadResult = await this.invokeDownloadAgent(assemblyData);
      const downloadData = JSON.parse(downloadResult.body);
      
      console.log('[Lambda Pipeline] All 9 agents completed successfully!');
      
      return {
        success: true,
        nlInput: nlData,
        uiSelection: uiData,
        parser: parserData,
        componentDecision: componentData,
        matchRate: matchData,
        search: searchData,
        generation: generationData,
        assembly: assemblyData,
        download: downloadData
      };
    } catch (error) {
      console.error('[Lambda Pipeline] Error:', error);
      throw error;
    }
  }
}