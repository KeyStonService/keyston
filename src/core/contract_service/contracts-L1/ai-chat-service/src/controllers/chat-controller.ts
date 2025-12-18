/**
 * AI 對話控制器 - 無人機應用
 * AI Chat Controller for Drone Applications
 */

import type { Request, Response } from 'express';
import { chatRequestSchema, type ChatRequest, type HealthCheckResponse } from '../types.js';
import { OpenAIService } from '../models/openai-service.js';
import pino from 'pino';

const logger = pino({ level: process.env.LOG_LEVEL || 'info' });

/**
 * 聊天控制器類
 * Chat controller class
 */
export class ChatController {
  private aiService: OpenAIService;

  constructor() {
    // Initialize AI service with default configuration
    this.aiService = new OpenAIService({
      providerKey: 'openai',
      modelName: process.env.AI_MODEL || 'gpt-4-turbo-preview',
      apiPath: process.env.OPENAI_API_BASE || 'https://api.openai.com/v1',
      apiKey: process.env.OPENAI_API_KEY,
      maxTokens: 4096,
      supportedFeatures: ['chat', 'streaming', 'drone-context'],
    });

    logger.info('Chat controller initialized');
  }

  /**
   * 處理聊天請求
   * Handle chat request
   */
  async chat(req: Request, res: Response): Promise<void> {
    try {
      // Validate request body
      const validationResult = chatRequestSchema.safeParse(req.body);
      
      if (!validationResult.success) {
        res.status(400).json({
          error: 'Invalid request',
          details: validationResult.error.errors,
        });
        return;
      }

      const chatRequest: ChatRequest = validationResult.data;
      
      logger.info({
        messageCount: chatRequest.messages.length,
        stream: chatRequest.stream,
        vehicleId: chatRequest.droneContext?.vehicleId,
      }, 'Processing chat request');

      // Non-streaming response
      if (!chatRequest.stream) {
        const response = await this.aiService.chat(chatRequest);
        res.json({
          message: response,
          timestamp: new Date().toISOString(),
        });
        return;
      }

      // Streaming response
      res.setHeader('Content-Type', 'text/event-stream');
      res.setHeader('Cache-Control', 'no-cache');
      res.setHeader('Connection', 'keep-alive');

      await this.aiService.chatStream(chatRequest, {
        onMessage: (delta) => {
          if (delta.content) {
            res.write(`data: ${JSON.stringify({ content: delta.content })}\n\n`);
          }
        },
        onComplete: () => {
          res.write('data: [DONE]\n\n');
          res.end();
        },
        onError: (error) => {
          logger.error({ error }, 'Streaming error');
          res.write(`data: ${JSON.stringify({ error: error.message })}\n\n`);
          res.end();
        },
      });
    } catch (error) {
      logger.error({ error }, 'Chat request failed');
      
      if (!res.headersSent) {
        res.status(500).json({
          error: 'Internal server error',
          message: error instanceof Error ? error.message : 'Unknown error',
        });
      }
    }
  }

  /**
   * 獲取服務狀態
   * Get service status
   */
  async status(_req: Request, res: Response): Promise<void> {
    try {
      const aiHealthy = await this.aiService.healthCheck();
      
      const health: HealthCheckResponse = {
        status: aiHealthy ? 'healthy' : 'degraded',
        timestamp: new Date(),
        services: {
          ai: aiHealthy,
          database: true, // Placeholder
          telemetry: true, // Placeholder
        },
        version: '1.0.0',
      };

      const statusCode = health.status === 'healthy' ? 200 : 503;
      res.status(statusCode).json(health);
    } catch (error) {
      logger.error({ error }, 'Status check failed');
      res.status(500).json({
        status: 'unhealthy',
        timestamp: new Date(),
        error: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  }

  /**
   * 處理無人機命令
   * Handle drone commands through AI
   */
  async droneCommand(req: Request, res: Response): Promise<void> {
    try {
      const { command, vehicleId, parameters } = req.body;

      logger.info({ command, vehicleId }, 'Processing drone command');

      // Create AI request with drone command context
      const chatRequest: ChatRequest = {
        messages: [
          {
            role: 'system',
            content: 'You are a drone flight assistant. Parse and validate flight commands.',
          },
          {
            role: 'user',
            content: `Execute command: ${command} with parameters: ${JSON.stringify(parameters)}`,
          },
        ],
        stream: false,
        temperature: 0.7,
        maxTokens: 4096,
        droneContext: {
          vehicleId,
          status: 'armed',
        },
      };

      const response = await this.aiService.chat(chatRequest);

      res.json({
        command,
        vehicleId,
        aiResponse: response,
        timestamp: new Date().toISOString(),
      });
    } catch (error) {
      logger.error({ error }, 'Drone command processing failed');
      res.status(500).json({
        error: 'Command processing failed',
        message: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  }

  /**
   * 獲取模型資訊
   * Get model information
   */
  async modelInfo(_req: Request, res: Response): Promise<void> {
    res.json({
      provider: 'openai',
      model: process.env.AI_MODEL || 'gpt-4-turbo-preview',
      features: ['chat', 'streaming', 'drone-context', 'command-parsing'],
      maxTokens: 4096,
      temperature: 0.7,
    });
  }
}
