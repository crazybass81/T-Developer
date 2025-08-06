import express from 'express';
import { AgnoMonitoringIntegration, MockAgentPool } from './agno';

const app = express();
app.use(express.json());

// Initialize Agno monitoring
const agentPool = new MockAgentPool();
const agnoMonitoring = new AgnoMonitoringIntegration();

// Agno monitoring endpoints
app.get('/api/agno/metrics', async (req, res) => {
  try {
    const metrics = await agnoMonitoring.collectMetrics(agentPool);
    res.json({
      success: true,
      metrics,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

app.post('/api/agno/events', async (req, res) => {
  try {
    const { eventType, agentId, metadata } = req.body;
    await agnoMonitoring.recordAgentEvent(eventType, agentId, metadata);
    res.json({ success: true });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

app.get('/api/agno/pool/stats', (req, res) => {
  const stats = agentPool.getStats();
  res.json({
    success: true,
    stats,
    timestamp: new Date().toISOString()
  });
});

app.post('/api/agno/pool/simulate', (req, res) => {
  agentPool.simulateActivity();
  const stats = agentPool.getStats();
  res.json({
    success: true,
    message: 'Agent pool activity simulated',
    stats
  });
});

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    services: {
      agno_monitoring: 'running',
      agent_pool: 'running'
    }
  });
});

const PORT = process.env.PORT || 3002;

if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`🚀 Server running on port ${PORT}`);
    console.log(`📊 Agno monitoring endpoints available at:`);
    console.log(`   GET  /api/agno/metrics`);
    console.log(`   POST /api/agno/events`);
    console.log(`   GET  /api/agno/pool/stats`);
    console.log(`   POST /api/agno/pool/simulate`);
  });
}

export default app;