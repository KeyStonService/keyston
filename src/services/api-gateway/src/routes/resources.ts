import { Router } from 'express';
import { logger } from '../config/logger';

export const resourcesRouter = Router();

// Mock resource database
const resources = new Map();

resourcesRouter.get('/', (req, res) => {
  const { limit = 10, offset = 0, sort = 'createdAt', order = 'desc' } = req.query;
  
  const allResources = Array.from(resources.values());
  const paginatedResources = allResources.slice(Number(offset), Number(offset) + Number(limit));

  res.json({
    data: paginatedResources,
    pagination: {
      total: allResources.length,
      limit: Number(limit),
      offset: Number(offset),
      hasMore: (Number(offset) + Number(limit)) < allResources.length
    }
  });
});

resourcesRouter.post('/', (req, res) => {
  const { name, type, config } = req.body;

  if (!name || !type) {
    return res.status(400).json({ error: 'Name and type are required' });
  }

  const id = String(resources.size + 1);
  const resource = {
    id,
    name,
    type,
    config: config || {},
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  };

  resources.set(id, resource);
  logger.info(`Resource created: ${id}`);

  res.status(201).json(resource);
});

resourcesRouter.get('/:id', (req, res) => {
  const { id } = req.params;
  const resource = resources.get(id);

  if (!resource) {
    return res.status(404).json({ error: 'Resource not found' });
  }

  res.json(resource);
});

resourcesRouter.put('/:id', (req, res) => {
  const { id } = req.params;
  const resource = resources.get(id);

  if (!resource) {
    return res.status(404).json({ error: 'Resource not found' });
  }

  const updatedResource = {
    ...resource,
    ...req.body,
    id, // Prevent ID change
    updatedAt: new Date().toISOString()
  };

  resources.set(id, updatedResource);
  logger.info(`Resource updated: ${id}`);

  res.json(updatedResource);
});

resourcesRouter.delete('/:id', (req, res) => {
  const { id } = req.params;

  if (!resources.has(id)) {
    return res.status(404).json({ error: 'Resource not found' });
  }

  resources.delete(id);
  logger.info(`Resource deleted: ${id}`);

  res.status(204).send();
});
