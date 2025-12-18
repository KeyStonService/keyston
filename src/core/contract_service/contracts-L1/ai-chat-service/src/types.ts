/**
 * 無人機 AI 對話服務類型定義
 * Type definitions for Drone AI Chat Service
 */

import { z } from 'zod';

/**
 * 訊息角色類型
 * Message role types
 */
export type MessageRole = 'user' | 'assistant' | 'system' | 'drone';

/**
 * 訊息結構
 * Message structure
 */
export interface ChatMessage {
  role: MessageRole;
  content: string;
  timestamp?: Date;
  metadata?: Record<string, unknown>;
}

/**
 * 聊天請求 Schema
 * Chat request validation schema
 */
export const chatRequestSchema = z.object({
  messages: z.array(z.object({
    role: z.enum(['user', 'assistant', 'system', 'drone']),
    content: z.string().min(1).max(10000),
    timestamp: z.string().datetime().optional(),
    metadata: z.record(z.unknown()).optional(),
  })),
  model: z.string().optional(),
  stream: z.boolean().optional().default(true),
  temperature: z.number().min(0).max(2).optional().default(0.7),
  maxTokens: z.number().min(1).max(8192).optional().default(4096),
  droneContext: z.object({
    missionId: z.string().optional(),
    vehicleId: z.string().optional(),
    location: z.object({
      lat: z.number(),
      lon: z.number(),
      alt: z.number(),
    }).optional(),
    status: z.enum(['idle', 'armed', 'flying', 'landing', 'emergency']).optional(),
  }).optional(),
});

export type ChatRequest = z.infer<typeof chatRequestSchema>;

/**
 * 流式回應選項
 * Streaming response options
 */
export interface StreamOptions {
  onMessage?: (delta: { content?: string; reasoning_content?: string }) => void;
  onComplete?: () => void;
  onError?: (error: Error) => void;
}

/**
 * LLM 服務介面
 * LLM service interface
 */
export interface LLMService {
  chat(request: ChatRequest): Promise<string>;
  chatStream?(request: ChatRequest, options?: StreamOptions): Promise<string>;
}

/**
 * 模型配置
 * Model configuration
 */
export interface ModelConfig {
  providerKey: string;
  modelName: string;
  apiPath: string;
  apiKey?: string;
  maxTokens: number;
  supportedFeatures: string[];
}

/**
 * 無人機命令類型
 * Drone command types
 */
export enum DroneCommand {
  TAKEOFF = 'takeoff',
  LAND = 'land',
  GOTO = 'goto',
  ORBIT = 'orbit',
  RETURN_HOME = 'return_to_home',
  EMERGENCY_STOP = 'emergency_stop',
  STATUS_CHECK = 'status_check',
}

/**
 * 命令驗證 Schema
 * Command validation schema
 */
export const droneCommandSchema = z.object({
  command: z.nativeEnum(DroneCommand),
  parameters: z.record(z.unknown()).optional(),
  vehicleId: z.string(),
  authorization: z.string(),
});

export type DroneCommandRequest = z.infer<typeof droneCommandSchema>;

/**
 * 遙測數據結構
 * Telemetry data structure
 */
export interface TelemetryData {
  vehicleId: string;
  timestamp: Date;
  position: {
    lat: number;
    lon: number;
    alt: number;
  };
  velocity: {
    vx: number;
    vy: number;
    vz: number;
  };
  attitude: {
    roll: number;
    pitch: number;
    yaw: number;
  };
  battery: {
    voltage: number;
    current: number;
    percentage: number;
  };
  status: string;
}

/**
 * 服務健康檢查回應
 * Service health check response
 */
export interface HealthCheckResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: Date;
  services: {
    ai: boolean;
    database: boolean;
    telemetry: boolean;
  };
  version: string;
}
