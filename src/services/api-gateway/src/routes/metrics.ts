import { Router } from 'express';

export const metricsRouter = Router();

metricsRouter.get('/timeseries', (req, res) => {
  const { metric, start, end, interval = '1m' } = req.query;

  // Mock time series data
  const dataPoints = [];
  const now = Date.now();
  for (let i = 60; i >= 0; i--) {
    dataPoints.push({
      timestamp: new Date(now - i * 60000).toISOString(),
      value: Math.random() * 100
    });
  }

  res.json({
    metric: metric || 'cpu_usage',
    interval,
    dataPoints
  });
});

metricsRouter.get('/logs', (req, res) => {
  const { level, service, limit = 100 } = req.query;

  // Mock log entries
  const logs = Array.from({ length: Number(limit) }, (_, i) => ({
    timestamp: new Date(Date.now() - i * 1000).toISOString(),
    level: level || 'info',
    service: service || 'api-gateway',
    message: `Log entry ${i + 1}`
  }));

  res.json({ logs });
});

metricsRouter.get('/events', (req, res) => {
  const { type, limit = 50 } = req.query;

  // Mock events
  const events = Array.from({ length: Number(limit) }, (_, i) => ({
    id: String(i + 1),
    type: type || 'system',
    timestamp: new Date(Date.now() - i * 5000).toISOString(),
    description: `Event ${i + 1}`,
    severity: ['info', 'warning', 'error'][Math.floor(Math.random() * 3)]
  }));

  res.json({ events });
});

metricsRouter.get('/alerts', (req, res) => {
  const { status = 'active' } = req.query;

  // Mock alerts
  const alerts = [
    {
      id: '1',
      title: 'High CPU Usage',
      description: 'CPU usage exceeded 90%',
      severity: 'warning',
      status,
      createdAt: new Date(Date.now() - 300000).toISOString()
    },
    {
      id: '2',
      title: 'Database Connection Lost',
      description: 'Failed to connect to primary database',
      severity: 'critical',
      status,
      createdAt: new Date(Date.now() - 600000).toISOString()
    }
  ];

  res.json({ alerts });
});
