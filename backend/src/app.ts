import express from 'express';
// import { initializeConfig } from './config';

const app = express();
const PORT = process.env.PORT || 3004;

app.use(express.json());

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    service: 'ui-selection-agent',
    version: '1.0.0'
  });
});

// UI Selection endpoint
app.post('/v1/agents/ui-selection/select', (req, res) => {
  const { projectType, requirements } = req.body;
  
  // Mock response for now
  res.json({
    selected_framework: 'react',
    reasoning: `Best choice for ${projectType} project based on requirements`,
    confidence: 0.95,
    alternatives: ['vue', 'angular'],
    implementation_guide: 'https://reactjs.org/docs/getting-started.html'
  });
});

export async function start() {
  // await initializeConfig();
  
  app.listen(PORT, () => {
    console.log(`🚀 UI Selection Agent running on port ${PORT}`);
  });
}

export default app;