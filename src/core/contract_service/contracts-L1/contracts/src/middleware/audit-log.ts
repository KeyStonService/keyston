/**
 * ============================================================================
 * 審計日誌中介軟體 (Audit Logging Middleware)
 * ============================================================================
 * 記錄所有 API 請求和響應，用於安全審計和合規性
 * ============================================================================
 */

import crypto from 'crypto';

import { Request, Response, NextFunction } from 'express';

/**
 * 擴展的 Request 類型，包含可選的用戶資訊
 */
interface AuthenticatedRequest extends Request {
  user?: {
    id: string;
    [key: string]: unknown;
  };
}

/**
 * 審計日誌條目
 */
interface AuditLogEntry {
  id: string; // 唯一標識符
  timestamp: string; // ISO 8601 時間戳
  traceId: string; // 追蹤 ID
  userId?: string; // 用戶 ID (如果已認證)
  ipAddress: string; // 客戶端 IP
  userAgent: string; // User Agent
  method: string; // HTTP 方法
  path: string; // 請求路徑
  query?: Record<string, unknown>; // 查詢參數
  body?: unknown; // 請求主體 (已清理敏感數據)
  statusCode?: number; // 回應狀態碼
  responseTime?: number; // 回應時間 (ms)
  error?: string; // 錯誤訊息
  action?: string; // 動作類型 (CREATE, READ, UPDATE, DELETE)
  resource?: string; // 資源類型
  result?: 'SUCCESS' | 'FAILURE'; // 結果
  metadata?: Record<string, unknown>; // 額外元數據
}

/**
 * 審計日誌配置
 */
interface AuditLogConfig {
  // 是否啟用審計日誌
  enabled?: boolean;

  // 敏感欄位列表 (將被遮罩)
  sensitiveFields?: string[];

  // 是否記錄請求主體
  logRequestBody?: boolean;

  // 是否記錄回應主體
  logResponseBody?: boolean;

  // 最大主體大小 (bytes)
  maxBodySize?: number;

  // 跳過日誌的路徑模式
  skipPaths?: RegExp[];

  // 自定義日誌處理器
  logHandler?: (entry: AuditLogEntry) => Promise<void> | void;
}

/**
 * 預設配置
 */
const defaultConfig: Required<Omit<AuditLogConfig, 'logHandler'>> = {
  enabled: true,
  sensitiveFields: [
    'password',
    'token',
    'secret',
    'api_key',
    'apiKey',
    'authorization',
    'credit_card',
    'ssn',
  ],
  logRequestBody: true,
  logResponseBody: false,
  maxBodySize: 10240, // 10KB
  skipPaths: [/\/health/i, /\/metrics/i, /\/favicon.ico/i],
};

/**
 * 清理敏感數據
 */
function sanitizeData(data: unknown, sensitiveFields: string[]): unknown {
  if (!data || typeof data !== 'object') {
    return data;
  }

  if (Array.isArray(data)) {
    return data.map((item) => sanitizeData(item, sensitiveFields));
  }

  // 僅處理純物件，排除特殊物件 (Date, Map, Set, 類別實例等)
  if (Object.getPrototypeOf(data) !== Object.prototype) {
    return data;
  }
  const sanitized: Record<string, unknown> = { ...(data as Record<string, unknown>) };

  for (const key in sanitized) {
    if (Object.prototype.hasOwnProperty.call(sanitized, key)) {
      // 檢查是否為敏感欄位
      if (sensitiveFields.some((field) => key.toLowerCase().includes(field.toLowerCase()))) {
        sanitized[key] = '***REDACTED***';
      } else if (typeof sanitized[key] === 'object' && sanitized[key] !== null) {
        // 遞歸清理嵌套對象
        sanitized[key] = sanitizeData(sanitized[key], sensitiveFields);
      }
    }
  }

  return sanitized;
}

/**
 * 判斷 HTTP 方法對應的動作
 */
function getActionFromMethod(method: string): string {
  const methodMap: Record<string, string> = {
    GET: 'READ',
    POST: 'CREATE',
    PUT: 'UPDATE',
    PATCH: 'UPDATE',
    DELETE: 'DELETE',
  };
  return methodMap[method.toUpperCase()] || 'UNKNOWN';
}

/**
 * 從路徑提取資源類型
 */
function extractResourceFromPath(path: string): string {
  // 簡單的資源提取邏輯
  const match = path.match(/\/api\/v\d+\/([^/?]+)/);
  return match ? match[1] : 'unknown';
}

/**
 * 預設日誌處理器 - 輸出到控制台
 */
function defaultLogHandler(entry: AuditLogEntry): void {
  const logLevel = entry.result === 'FAILURE' ? 'error' : 'info';
  console.log(
    JSON.stringify({
      level: logLevel,
      type: 'audit',
      ...entry,
    })
  );
}

/**
 * 創建審計日誌中介軟體
 */
export function createAuditLogger(
  config: AuditLogConfig = {}
): (req: Request, res: Response, next: NextFunction) => void {
  const finalConfig = { ...defaultConfig, ...config };
  const logHandler = config.logHandler || defaultLogHandler;

  // 如果未啟用，返回空中介軟體
  if (!finalConfig.enabled) {
    return (_req: Request, _res: Response, next: NextFunction) => next();
  }

  return (req: Request, res: Response, next: NextFunction): void => {
    // 檢查是否跳過此路徑
    if (finalConfig.skipPaths.some((pattern) => pattern.test(req.path))) {
      return next();
    }

    const startTime = Date.now();

    // 生成追蹤 ID
    const traceId = (req.headers['x-trace-id'] as string) || crypto.randomUUID();

    // 設置追蹤 ID 到請求和回應
    req.headers['x-trace-id'] = traceId;
    res.setHeader('X-Trace-Id', traceId);

    // 創建基礎日誌條目
    const logEntry: Partial<AuditLogEntry> = {
      id: crypto.randomUUID(),
      timestamp: new Date().toISOString(),
      traceId,
      ipAddress:
        (req.headers['x-forwarded-for'] as string)?.split(',')[0]?.trim() ||
        req.ip ||
        req.connection.remoteAddress ||
        'unknown',
      userAgent: req.headers['user-agent'] || 'unknown',
      method: req.method,
      path: req.path,
      query: Object.keys(req.query).length > 0 ? req.query : undefined,
      action: getActionFromMethod(req.method),
      resource: extractResourceFromPath(req.path),
    };

    // 記錄用戶 ID (如果已認證)
    const authReq = req as AuthenticatedRequest;
    if (authReq.user?.id) {
      logEntry.userId = authReq.user.id;
    }

    // 記錄請求主體
    if (finalConfig.logRequestBody && req.body && Object.keys(req.body).length > 0) {
      const bodySize = JSON.stringify(req.body).length;
      if (bodySize <= finalConfig.maxBodySize) {
        logEntry.body = sanitizeData(req.body, finalConfig.sensitiveFields);
      } else {
        logEntry.metadata = {
          ...logEntry.metadata,
          bodyTooLarge: true,
          bodySize,
        };
      }
    }

    // 攔截 res.json 以記錄回應
    const originalJson = res.json.bind(res);
    res.json = function (body: unknown): Response {
      logEntry.statusCode = res.statusCode;
      logEntry.responseTime = Date.now() - startTime;
      logEntry.result = res.statusCode < 400 ? 'SUCCESS' : 'FAILURE';

      // 記錄錯誤訊息
      if (res.statusCode >= 400 && body && typeof body === 'object' && 'error' in body) {
        const errorBody = body as { error: unknown };
        logEntry.error =
          typeof errorBody.error === 'string' ? errorBody.error : JSON.stringify(errorBody.error);
      }

      // 記錄回應主體 (可選)
      if (finalConfig.logResponseBody && body) {
        const responseSize = JSON.stringify(body).length;
        if (responseSize <= finalConfig.maxBodySize) {
          logEntry.metadata = {
            ...logEntry.metadata,
            response: sanitizeData(body, finalConfig.sensitiveFields),
          };
        }
      }

      // 寫入審計日誌
      Promise.resolve(logHandler(logEntry as AuditLogEntry)).catch((err) => {
        console.error('Failed to write audit log:', err);
      });

      return originalJson(body);
    };

    // 處理錯誤情況
    res.on('finish', () => {
      // 如果回應已結束但未調用 res.json，仍然記錄
      if (!logEntry.statusCode) {
        logEntry.statusCode = res.statusCode;
        logEntry.responseTime = Date.now() - startTime;
        logEntry.result = res.statusCode < 400 ? 'SUCCESS' : 'FAILURE';

        Promise.resolve(logHandler(logEntry as AuditLogEntry)).catch((err) => {
          console.error('Failed to write audit log:', err);
        });
      }
    });

    next();
  };
}

/**
 * 審計日誌查詢助手
 */
export class AuditLogQuery {
  /**
   * 根據用戶 ID 查詢審計日誌
   */
  static async findByUserId(_userId: string, _limit: number = 100): Promise<AuditLogEntry[]> {
    // 實現依賴於實際的存儲後端
    // 這裡提供接口定義
    throw new Error('Not implemented - requires storage backend');
  }

  /**
   * 根據時間範圍查詢審計日誌
   */
  static async findByTimeRange(
    _startTime: Date,
    _endTime: Date,
    _limit: number = 100
  ): Promise<AuditLogEntry[]> {
    throw new Error('Not implemented - requires storage backend');
  }

  /**
   * 根據動作類型查詢審計日誌
   */
  static async findByAction(_action: string, _limit: number = 100): Promise<AuditLogEntry[]> {
    throw new Error('Not implemented - requires storage backend');
  }

  /**
   * 根據資源類型查詢審計日誌
   */
  static async findByResource(_resource: string, _limit: number = 100): Promise<AuditLogEntry[]> {
    throw new Error('Not implemented - requires storage backend');
  }
}

/**
 * 導出類型和工具
 */
export type { AuditLogEntry, AuditLogConfig };
export { sanitizeData };
