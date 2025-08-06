import express from 'express';

const app = express();
const PORT = process.env.PORT || 8000;

app.use(express.json());

app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    service: 'T-Developer Backend'
  });
});

app.listen(PORT, () => {
  console.log(`✅ T-Developer Backend running on port ${PORT}`);
  console.log(`🔗 Health check: http://localhost:${PORT}/health`);
});