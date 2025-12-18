import { Router } from 'express';
import { logger } from '../config/logger';

export const tasksRouter = Router();

// Mock task database
const tasks = new Map();

tasksRouter.get('/', (req, res) => {
  const { status, limit = 10, offset = 0 } = req.query;
  
  let allTasks = Array.from(tasks.values());
  
  if (status) {
    allTasks = allTasks.filter(task => task.status === status);
  }

  const paginatedTasks = allTasks.slice(Number(offset), Number(offset) + Number(limit));

  res.json({
    data: paginatedTasks,
    pagination: {
      total: allTasks.length,
      limit: Number(limit),
      offset: Number(offset)
    }
  });
});

tasksRouter.post('/', (req, res) => {
  const { name, type, config } = req.body;

  if (!name || !type) {
    return res.status(400).json({ error: 'Name and type are required' });
  }

  const id = String(tasks.size + 1);
  const task = {
    id,
    name,
    type,
    config: config || {},
    status: 'pending',
    createdAt: new Date().toISOString(),
    startedAt: null,
    completedAt: null,
    logs: []
  };

  tasks.set(id, task);
  logger.info(`Task created: ${id}`);

  res.status(201).json(task);
});

tasksRouter.get('/:id', (req, res) => {
  const { id } = req.params;
  const task = tasks.get(id);

  if (!task) {
    return res.status(404).json({ error: 'Task not found' });
  }

  res.json(task);
});

tasksRouter.put('/:id/cancel', (req, res) => {
  const { id } = req.params;
  const task = tasks.get(id);

  if (!task) {
    return res.status(404).json({ error: 'Task not found' });
  }

  if (task.status === 'completed' || task.status === 'cancelled') {
    return res.status(400).json({ error: 'Task already finished' });
  }

  task.status = 'cancelled';
  task.completedAt = new Date().toISOString();
  tasks.set(id, task);
  logger.info(`Task cancelled: ${id}`);

  res.json(task);
});

tasksRouter.get('/:id/logs', (req, res) => {
  const { id } = req.params;
  const task = tasks.get(id);

  if (!task) {
    return res.status(404).json({ error: 'Task not found' });
  }

  res.json({
    taskId: id,
    logs: task.logs || []
  });
});
