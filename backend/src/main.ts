import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import path from 'path';
import fs from 'fs';
import { HybridConfigManager } from './config/config-manager';
import { NLInputAgent } from './agents/nl-input-agent';
import { UISelectionAgent } from './agents/ui-selection-agent';
import { ParserAgent } from './agents/parser-agent';
import { ComponentDecisionAgent } from './agents/component-decision-agent';
import { MatchRateAgent } from './agents/match-rate-agent';
import { SearchAgent } from './agents/search-agent';
import { GenerationAgent } from './agents/generation-agent';
import { AssemblyAgent } from './agents/assembly-agent';
import { DownloadAgent } from './agents/download-agent';
import { LambdaIntegration } from './lambda-integration';

const app = express();
const configManager = new HybridConfigManager();

async function startServer() {
  try {
    // Initialize configuration from AWS
    console.log('🔐 Initializing configuration from AWS...');
    await configManager.initialize();
    
    const PORT = process.env.PORT || 8000;
    const environment = process.env.NODE_ENV || 'development';
    
    // Middleware
    app.use(helmet({
      contentSecurityPolicy: false,
    }));
    app.use(cors({
      origin: '*',
      credentials: true
    }));
    app.use(express.json());
    app.use(express.urlencoded({ extended: true }));
    
    // Serve frontend static files (but not for API routes)
    const frontendPath = path.join(__dirname, '../../frontend/dist');
    app.use((req, res, next) => {
      // Skip static file serving for API routes
      if (req.path.startsWith('/api/')) {
        return next();
      }
      express.static(frontendPath)(req, res, next);
    });

    // Health check endpoint
    app.get('/health', (req, res) => {
      res.json({ 
        status: 'ok', 
        timestamp: new Date().toISOString(),
        service: 'T-Developer Backend',
        environment: environment,
        version: '1.0.0'
      });
    });

    // Natural Language API endpoint
    app.post('/api/v1/generate', async (req, res) => {
      try {
        const { query, framework } = req.body;
        
        if (!query) {
          return res.status(400).json({ 
            error: 'Query is required',
            message: 'Please provide a natural language description of what you want to build'
          });
        }

        console.log('[Agent Pipeline] Starting 9-agent processing pipeline...');
        
        // Check if Lambda functions are available
        const useLambda = process.env.USE_LAMBDA === 'true';
        
        if (useLambda) {
          console.log('[Agent Pipeline] Using Lambda functions...');
          const lambdaIntegration = new LambdaIntegration();
          const lambdaResult = await lambdaIntegration.executePipeline(query, framework);
          
          // Transform Lambda result to match expected response format
          const response = {
            status: 'success',
            query: query,
            framework: lambdaResult.nlInput.requirements?.technologyPreferences?.framework || 'react',
            message: 'Complete 9-agent Lambda pipeline processing completed',
            timestamp: new Date().toISOString(),
            projectName: lambdaResult.download.project_name,
            result: {
              projectGenerated: true,
              downloadReady: true,
              downloadUrl: lambdaResult.download.download_url,
              packageSize: lambdaResult.download.package_size,
              estimatedInstallTime: lambdaResult.download.estimated_install_time,
              components: lambdaResult.componentDecision.components,
              totalFiles: lambdaResult.assembly.total_files,
              validationScore: lambdaResult.assembly.validation_score,
              qualityScore: lambdaResult.assembly.quality_score,
              buildCommands: lambdaResult.generation.build_commands,
              framework: lambdaResult.uiSelection.framework,
              confidence: lambdaResult.nlInput.confidence
            }
          };
          
          return res.json(response);
        }

        // Step 1: NL Input Agent - 자연어 분석
        console.log('[Agent Pipeline] Step 1/9 - NL Input Agent');
        const nlInputAgent = new NLInputAgent();
        const requirements = await nlInputAgent.processInput(query, framework);
        
        // Step 2: UI Selection Agent - UI 기술 스택 선택
        console.log('[Agent Pipeline] Step 2/9 - UI Selection Agent');
        const uiSelectionAgent = new UISelectionAgent();
        const uiSelection = await uiSelectionAgent.selectUIStack(requirements);
        
        // Step 3: Parser Agent - 프로젝트 구조 파싱
        console.log('[Agent Pipeline] Step 3/9 - Parser Agent');
        const parserAgent = new ParserAgent();
        const projectStructure = await parserAgent.parseProjectStructure(uiSelection, requirements);
        
        // Step 4: Component Decision Agent - 컴포넌트 상세 설계
        console.log('[Agent Pipeline] Step 4/9 - Component Decision Agent');
        const componentDecisionAgent = new ComponentDecisionAgent();
        const componentDecisions = await componentDecisionAgent.makeComponentDecisions(
          projectStructure, uiSelection, requirements
        );
        
        // Step 5: Match Rate Agent - 컴포넌트 매칭률 계산
        console.log('[Agent Pipeline] Step 5/9 - Match Rate Agent');
        const matchRateAgent = new MatchRateAgent();
        const matchRateResults = await matchRateAgent.calculateMatchRates(componentDecisions, uiSelection);
        
        // Step 6: Search Agent - 코드 템플릿 검색
        console.log('[Agent Pipeline] Step 6/9 - Search Agent');
        const searchAgent = new SearchAgent();
        const searchResults = await searchAgent.searchCodeTemplates(matchRateResults, componentDecisions);
        
        // Step 7: Generation Agent - 프로젝트 코드 생성
        console.log('[Agent Pipeline] Step 7/9 - Generation Agent');
        const generationAgent = new GenerationAgent();
        const projectName = query.includes('QR') ? 'qr-attendance-system' : 
                           query.includes('블로그') ? 'blog-website' : 'web-application';
        const generatedProject = await generationAgent.generateProject(
          searchResults, projectStructure, uiSelection, projectName
        );
        
        // Step 8: Assembly Agent - 프로젝트 조립 및 검증
        console.log('[Agent Pipeline] Step 8/9 - Assembly Agent');
        const assemblyAgent = new AssemblyAgent();
        const assembledProject = await assemblyAgent.assembleProject(generatedProject);
        
        // Step 9: Download Agent - 다운로드 패키지 생성
        console.log('[Agent Pipeline] Step 9/9 - Download Agent');
        const downloadAgent = new DownloadAgent();
        const downloadPackage = await downloadAgent.createDownloadPackage(assembledProject);
        
        console.log('[Agent Pipeline] All 9 agents completed successfully!');
        
        const response = {
          status: 'success',
          query: query,
          framework: requirements.technologyPreferences.framework || 'react',
          message: 'Complete 9-agent pipeline processing completed',
          timestamp: new Date().toISOString(),
          projectName: downloadPackage.projectName,
          agentResults: {
            step1_nlInput: {
              projectType: requirements.projectType,
              functionalRequirements: requirements.functionalRequirements,
              extractedEntities: requirements.extractedEntities,
              confidence: requirements.confidenceScore
            },
            step2_uiSelection: {
              framework: uiSelection.framework,
              componentLibrary: uiSelection.componentLibrary,
              stylingApproach: uiSelection.stylingApproach,
              stateManagement: uiSelection.stateManagement,
              estimatedComplexity: uiSelection.estimatedComplexity
            },
            step3_parser: {
              totalFiles: projectStructure.totalFiles,
              directories: projectStructure.directories.length,
              estimatedSize: projectStructure.estimatedSize
            },
            step4_componentDecision: {
              totalComponents: componentDecisions.length,
              componentTypes: componentDecisions.map(cd => cd.componentName)
            },
            step5_matchRate: {
              averageMatchScore: matchRateResults.reduce((sum, mr) => sum + mr.matchScore, 0) / matchRateResults.length,
              recommendedActions: matchRateResults.map(mr => mr.recommendedAction)
            },
            step6_search: {
              totalSearchResults: searchResults.length,
              averageSearchScore: searchResults.reduce((sum, sr) => sum + sr.searchScore, 0) / searchResults.length
            },
            step7_generation: {
              totalFiles: generatedProject.totalFiles,
              estimatedSize: generatedProject.estimatedSize,
              buildInstructions: generatedProject.buildInstructions.length
            },
            step8_assembly: {
              validationScore: assembledProject.validation.score,
              qualityMetrics: assembledProject.qualityMetrics,
              totalValidatedFiles: assembledProject.files.length
            },
            step9_download: {
              packageSize: downloadPackage.size,
              downloadUrl: downloadPackage.downloadUrl,
              format: downloadPackage.format,
              checksum: downloadPackage.checksum
            }
          },
          result: {
            projectGenerated: true,
            downloadReady: true,
            downloadUrl: downloadPackage.downloadUrl,
            packageSize: `${Math.round(downloadPackage.size / 1024)} KB`,
            estimatedInstallTime: downloadPackage.metadata.estimatedInstallTime,
            components: componentDecisions.map(cd => cd.componentName),
            totalFiles: assembledProject.files.length,
            validationScore: assembledProject.validation.score,
            qualityScore: assembledProject.qualityMetrics.maintainabilityIndex,
            buildCommands: generatedProject.buildInstructions,
            framework: uiSelection.framework,
            confidence: requirements.confidenceScore
          }
        };

        res.json(response);
      } catch (error) {
        console.error('Error processing NL query:', error);
        res.status(500).json({ 
          error: 'Internal server error',
          message: 'Failed to process natural language query'
        });
      }
    });

    // List available frameworks
    app.get('/api/v1/frameworks', (req, res) => {
      res.json({
        frameworks: [
          { id: 'react', name: 'React', version: '18.x' },
          { id: 'vue', name: 'Vue.js', version: '3.x' },
          { id: 'angular', name: 'Angular', version: '17.x' },
          { id: 'nextjs', name: 'Next.js', version: '14.x' },
          { id: 'svelte', name: 'Svelte', version: '4.x' }
        ]
      });
    });

    // Download endpoint for generated packages
    app.get('/api/v1/download/:filename', (req, res) => {
      const { filename } = req.params;
      const downloadsPath = path.join(__dirname, '../downloads');
      const filePath = path.join(downloadsPath, filename);
      
      // Security: Prevent directory traversal
      if (!filePath.startsWith(downloadsPath)) {
        return res.status(400).json({ error: 'Invalid filename' });
      }
      
      // Check if file exists
      if (!fs.existsSync(filePath)) {
        return res.status(404).json({ error: 'File not found' });
      }
      
      // Set appropriate headers for download
      res.setHeader('Content-Type', 'application/zip');
      res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
      
      // Stream the file to the client
      const stream = fs.createReadStream(filePath);
      stream.pipe(res);
      
      stream.on('error', (error) => {
        console.error('Download stream error:', error);
        if (!res.headersSent) {
          res.status(500).json({ error: 'Failed to download file' });
        }
      });
    });

    // Config endpoint (only in development)
    if (environment === 'development') {
      app.get('/api/config', (req, res) => {
        res.json({
          environment: environment,
          port: PORT,
          features: {
            nlProcessing: true,
            codeGeneration: true,
            multiFramework: true
          }
        });
      });
    }

    // 404 handler
    app.use((req, res) => {
      res.status(404).json({ 
        error: 'Not Found',
        message: `Cannot ${req.method} ${req.url}`
      });
    });

    // Error handler
    app.use((err: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
      console.error('Error:', err);
      res.status(err.status || 500).json({
        error: err.message || 'Internal Server Error',
        ...(environment === 'development' && { stack: err.stack })
      });
    });

    app.listen(PORT, () => {
      console.log(`✅ T-Developer Backend running on port ${PORT}`);
      console.log(`🌍 Environment: ${environment}`);
      console.log(`🔗 Health check: http://localhost:${PORT}/health`);
      console.log(`🤖 NL API: http://localhost:${PORT}/api/v1/generate`);
      console.log(`📦 Frameworks: http://localhost:${PORT}/api/v1/frameworks`);
      
      if (environment === 'development') {
        console.log(`⚙️ Config endpoint: http://localhost:${PORT}/api/config`);
      }
    });
  } catch (error) {
    console.error('❌ Failed to start server:', error);
    // In development, start without AWS config
    if (process.env.NODE_ENV === 'development') {
      console.log('⚠️ Starting in local mode without AWS configuration...');
      startLocalServer();
    } else {
      process.exit(1);
    }
  }
}

// Fallback local server without AWS
function startLocalServer() {
  const PORT = 8000;
  
  // Basic middleware
  app.use(cors({
    origin: '*'
  }));
  app.use(express.json());
  
  // Serve frontend static files (but not for API routes)
  const frontendPath = path.join(__dirname, '../../frontend/dist');
  app.use((req, res, next) => {
    // Skip static file serving for API routes
    if (req.path.startsWith('/api/')) {
      return next();
    }
    express.static(frontendPath)(req, res, next);
  });

  // Request logging middleware
  app.use((req, res, next) => {
    console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
    next();
  });

  // Health check
  app.get('/health', (req, res) => {
    res.json({ 
      status: 'ok', 
      mode: 'local',
      timestamp: new Date().toISOString()
    });
  });

  // Natural Language API
  app.post('/api/v1/generate', async (req, res) => {
    try {
      const { query, framework } = req.body;
      console.log(`[${new Date().toISOString()}] NL API Request:`, { query, framework });
      
      console.log('[Agent Pipeline LOCAL] Starting 9-agent processing pipeline...');

      // Step 1: NL Input Agent - 자연어 분석
      console.log('[Agent Pipeline LOCAL] Step 1/9 - NL Input Agent');
      const nlInputAgent = new NLInputAgent();
      const requirements = await nlInputAgent.processInput(query, framework);
      
      // Step 2: UI Selection Agent - UI 기술 스택 선택
      console.log('[Agent Pipeline LOCAL] Step 2/9 - UI Selection Agent');
      const uiSelectionAgent = new UISelectionAgent();
      const uiSelection = await uiSelectionAgent.selectUIStack(requirements);
      
      // Step 3: Parser Agent - 프로젝트 구조 파싱
      console.log('[Agent Pipeline LOCAL] Step 3/9 - Parser Agent');
      const parserAgent = new ParserAgent();
      const projectStructure = await parserAgent.parseProjectStructure(uiSelection, requirements);
      
      // Step 4: Component Decision Agent - 컴포넌트 상세 설계
      console.log('[Agent Pipeline LOCAL] Step 4/9 - Component Decision Agent');
      const componentDecisionAgent = new ComponentDecisionAgent();
      const componentDecisions = await componentDecisionAgent.makeComponentDecisions(
        projectStructure, uiSelection, requirements
      );
      
      // Step 5: Match Rate Agent - 컴포넌트 매칭률 계산
      console.log('[Agent Pipeline LOCAL] Step 5/9 - Match Rate Agent');
      const matchRateAgent = new MatchRateAgent();
      const matchRateResults = await matchRateAgent.calculateMatchRates(componentDecisions, uiSelection);
      
      // Step 6: Search Agent - 코드 템플릿 검색
      console.log('[Agent Pipeline LOCAL] Step 6/9 - Search Agent');
      const searchAgent = new SearchAgent();
      const searchResults = await searchAgent.searchCodeTemplates(matchRateResults, componentDecisions);
      
      // Step 7: Generation Agent - 프로젝트 코드 생성
      console.log('[Agent Pipeline LOCAL] Step 7/9 - Generation Agent');
      const generationAgent = new GenerationAgent();
      const projectName = query.includes('QR') ? 'qr-attendance-system' : 
                         query.includes('블로그') ? 'blog-website' : 'web-application';
      const generatedProject = await generationAgent.generateProject(
        searchResults, projectStructure, uiSelection, projectName
      );
      
      // Step 8: Assembly Agent - 프로젝트 조립 및 검증
      console.log('[Agent Pipeline LOCAL] Step 8/9 - Assembly Agent');
      const assemblyAgent = new AssemblyAgent();
      const assembledProject = await assemblyAgent.assembleProject(generatedProject);
      
      // Step 9: Download Agent - 다운로드 패키지 생성
      console.log('[Agent Pipeline LOCAL] Step 9/9 - Download Agent');
      const downloadAgent = new DownloadAgent();
      const downloadPackage = await downloadAgent.createDownloadPackage(assembledProject);
      
      console.log('[Agent Pipeline LOCAL] All 9 agents completed successfully!');
      
      res.json({
        status: 'success',
        mode: 'local',
        query: query,
        framework: requirements.technologyPreferences.framework || 'react',
        message: 'Complete 9-agent pipeline processing completed in local mode',
        timestamp: new Date().toISOString(),
        projectName: downloadPackage.projectName,
        agentResults: {
          step1_nlInput: {
            projectType: requirements.projectType,
            functionalRequirements: requirements.functionalRequirements,
            extractedEntities: requirements.extractedEntities,
            confidence: requirements.confidenceScore
          },
          step2_uiSelection: {
            framework: uiSelection.framework,
            componentLibrary: uiSelection.componentLibrary,
            stylingApproach: uiSelection.stylingApproach,
            stateManagement: uiSelection.stateManagement,
            estimatedComplexity: uiSelection.estimatedComplexity
          },
          step3_parser: {
            totalFiles: projectStructure.totalFiles,
            directories: projectStructure.directories.length,
            estimatedSize: projectStructure.estimatedSize
          },
          step4_componentDecision: {
            totalComponents: componentDecisions.length,
            componentTypes: componentDecisions.map(cd => cd.componentName)
          },
          step5_matchRate: {
            averageMatchScore: matchRateResults.reduce((sum, mr) => sum + mr.matchScore, 0) / matchRateResults.length,
            recommendedActions: matchRateResults.map(mr => mr.recommendedAction)
          },
          step6_search: {
            totalSearchResults: searchResults.length,
            averageSearchScore: searchResults.reduce((sum, sr) => sum + sr.searchScore, 0) / searchResults.length
          },
          step7_generation: {
            totalFiles: generatedProject.totalFiles,
            estimatedSize: generatedProject.estimatedSize,
            buildInstructions: generatedProject.buildInstructions.length
          },
          step8_assembly: {
            validationScore: assembledProject.validation.score,
            qualityMetrics: assembledProject.qualityMetrics,
            totalValidatedFiles: assembledProject.files.length
          },
          step9_download: {
            packageSize: downloadPackage.size,
            downloadUrl: downloadPackage.downloadUrl,
            format: downloadPackage.format,
            checksum: downloadPackage.checksum
          }
        },
        result: {
          projectGenerated: true,
          downloadReady: true,
          downloadUrl: downloadPackage.downloadUrl,
          packageSize: `${Math.round(downloadPackage.size / 1024)} KB`,
          estimatedInstallTime: downloadPackage.metadata.estimatedInstallTime,
          components: componentDecisions.map(cd => cd.componentName),
          totalFiles: assembledProject.files.length,
          validationScore: assembledProject.validation.score,
          qualityScore: assembledProject.qualityMetrics.maintainabilityIndex,
          buildCommands: generatedProject.buildInstructions,
          framework: uiSelection.framework,
          confidence: requirements.confidenceScore
        }
      });
    } catch (error) {
      console.error('Error in local mode agent pipeline:', error);
      res.status(500).json({
        status: 'error',
        mode: 'local',
        message: 'Failed to process request in local mode',
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  });

  // List available frameworks
  app.get('/api/v1/frameworks', (req, res) => {
    res.json({
      frameworks: [
        { id: 'react', name: 'React', version: '18.x' },
        { id: 'vue', name: 'Vue.js', version: '3.x' },
        { id: 'angular', name: 'Angular', version: '17.x' },
        { id: 'nextjs', name: 'Next.js', version: '14.x' },
        { id: 'svelte', name: 'Svelte', version: '4.x' }
      ]
    });
  });

  // Download endpoint for generated packages
  app.get('/api/v1/download/:filename', (req, res) => {
    const { filename } = req.params;
    const downloadsPath = path.join(__dirname, '../downloads');
    const filePath = path.join(downloadsPath, filename);
    
    // Security: Prevent directory traversal
    if (!filePath.startsWith(downloadsPath)) {
      return res.status(400).json({ error: 'Invalid filename' });
    }
    
    // Check if file exists
    if (!fs.existsSync(filePath)) {
      return res.status(404).json({ error: 'File not found' });
    }
    
    // Set appropriate headers for download
    res.setHeader('Content-Type', 'application/zip');
    res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
    
    // Stream the file to the client
    const stream = fs.createReadStream(filePath);
    stream.pipe(res);
    
    stream.on('error', (error) => {
      console.error('Download stream error:', error);
      if (!res.headersSent) {
        res.status(500).json({ error: 'Failed to download file' });
      }
    });
  });

  // Catch-all route for SPA
  app.get('*', (req, res) => {
    const indexPath = path.join(__dirname, '../../frontend/dist/index.html');
    if (require('fs').existsSync(indexPath)) {
      res.sendFile(indexPath);
    } else {
      res.status(200).send(`
        <!DOCTYPE html>
        <html>
        <head>
          <title>T-Developer</title>
          <style>
            body { font-family: Arial; padding: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
            .container { max-width: 600px; margin: 0 auto; text-align: center; }
            a { color: white; text-decoration: underline; }
          </style>
        </head>
        <body>
          <div class="container">
            <h1>🚀 T-Developer Backend</h1>
            <p>서버가 실행 중입니다!</p>
            <p>API Endpoints:</p>
            <ul style="list-style: none; padding: 0;">
              <li>GET /health - 헬스체크</li>
              <li>POST /api/v1/generate - 자연어 처리</li>
              <li>GET /api/v1/frameworks - 프레임워크 목록</li>
            </ul>
            <p style="margin-top: 30px;">프론트엔드를 빌드하려면:</p>
            <code style="background: rgba(0,0,0,0.3); padding: 10px; display: block; margin: 10px 0;">
              cd frontend && npm run build
            </code>
          </div>
        </body>
        </html>
      `);
    }
  });

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`✅ Server running in LOCAL mode on port ${PORT}`);
    console.log(`🔗 Local: http://localhost:${PORT}`);
    console.log(`🌐 Network: http://100.25.70.173:${PORT}`);
    console.log(`📱 Frontend will be served from the same port`);
  });
}

// Start the server
startServer();