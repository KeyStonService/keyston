/**
 * OpenAI 服務適配器 - 無人機/自動駕駛應用
 * OpenAI Service Adapter for Drone/Autonomous Systems
 */

import OpenAI from 'openai';
import type { LLMService, ChatRequest, StreamOptions, ModelConfig } from '../types.js';
import pino from 'pino';

const logger = pino({ level: process.env.LOG_LEVEL || 'info' });

/**
 * OpenAI 服務實現
 * OpenAI service implementation
 */
export class OpenAIService implements LLMService {
  private client: OpenAI;
  private config: ModelConfig;

  constructor(config: ModelConfig) {
    this.config = config;
    this.client = new OpenAI({
      baseURL: config.apiPath,
      apiKey: config.apiKey || process.env.OPENAI_API_KEY,
    });

    logger.info({
      provider: config.providerKey,
      model: config.modelName,
    }, 'OpenAI service initialized');
  }

  /**
   * 執行聊天請求
   * Execute chat request
   * 
   * @param request - Chat request parameters
   * @returns Promise resolving to response string
   */
  async chat(request: ChatRequest): Promise<string> {
    if (request.stream) {
      return this.chatStream(request);
    }
    return this.chatBatch(request);
  }

  /**
   * 批次聊天請求（非串流）
   * Batch chat request (non-streaming)
   * 
   * @param request - Chat request parameters
   * @returns Promise resolving to complete response
   */
  private async chatBatch(request: ChatRequest): Promise<string> {
    try {
      logger.debug({ messageCount: request.messages.length }, 'Starting batch chat request');

      const completion = await this.client.chat.completions.create({
        model: request.model || this.config.modelName,
        messages: request.messages.map(msg => ({
          role: msg.role === 'drone' ? 'system' : msg.role,
          content: this.enrichContent(msg.content, request),
        })),
        stream: false,
        temperature: request.temperature,
        max_tokens: request.maxTokens,
      });

      const response = completion.choices[0]?.message?.content || '';
      logger.info({ 
        tokens: completion.usage?.total_tokens,
        responseLength: response.length 
      }, 'Chat request completed');

      return response;
    } catch (error) {
      logger.error({ error }, 'Chat request failed');
      throw new Error(`OpenAI request failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * 串流聊天請求
   * Streaming chat request
   * 
   * @param request - Chat request parameters
   * @param options - Streaming options (optional)
   * @returns Promise resolving when stream completes
   */
  async chatStream(request: ChatRequest, options?: StreamOptions): Promise<string> {
    try {
      logger.debug({ messageCount: request.messages.length }, 'Starting streaming chat request');

      const completion = await this.client.chat.completions.create({
        model: request.model || this.config.modelName,
        messages: request.messages.map(msg => ({
          role: msg.role === 'drone' ? 'system' : msg.role,
          content: this.enrichContent(msg.content, request),
        })),
        stream: true,
        temperature: request.temperature,
        max_tokens: request.maxTokens,
      });

      let fullResponse = '';

      for await (const chunk of completion) {
        const delta = chunk.choices[0]?.delta;
        if (!delta) continue;

        if (delta.content) {
          fullResponse += delta.content;
          options?.onMessage?.({ content: delta.content });
        }
      }

      options?.onComplete?.();
      logger.info({ responseLength: fullResponse.length }, 'Streaming chat completed');

      return fullResponse;
    } catch (error) {
      logger.error({ error }, 'Streaming chat failed');
      options?.onError?.(error instanceof Error ? error : new Error(String(error)));
      throw new Error(`OpenAI streaming failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * 豐富內容，加入無人機上下文
   * Enrich content with drone context
   * 
   * @param content - Original message content
   * @param request - Full chat request for context
   * @returns Enriched content string
   */
  private enrichContent(content: string, request: ChatRequest): string {
    if (!request.droneContext) {
      return content;
    }

    const context = request.droneContext;
    let enrichedContent = content;

    // Add drone context information
    const contextInfo: string[] = [];
    
    if (context.vehicleId) {
      contextInfo.push(`Vehicle ID: ${context.vehicleId}`);
    }
    
    if (context.missionId) {
      contextInfo.push(`Mission ID: ${context.missionId}`);
    }
    
    if (context.location) {
      contextInfo.push(
        `Location: Lat ${context.location.lat.toFixed(6)}, ` +
        `Lon ${context.location.lon.toFixed(6)}, ` +
        `Alt ${context.location.alt.toFixed(2)}m`
      );
    }
    
    if (context.status) {
      contextInfo.push(`Status: ${context.status}`);
    }

    if (contextInfo.length > 0) {
      enrichedContent = `[Drone Context: ${contextInfo.join(', ')}]\n\n${content}`;
    }

    return enrichedContent;
  }

  /**
   * 驗證服務連接
   * Validate service connection
   * 
   * @returns Promise resolving to boolean indicating health
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await this.client.chat.completions.create({
        model: this.config.modelName,
        messages: [{ role: 'user', content: 'ping' }],
        max_tokens: 5,
      });
      return response.choices.length > 0;
    } catch (error) {
      logger.error({ error }, 'Health check failed');
      return false;
    }
  }
}
