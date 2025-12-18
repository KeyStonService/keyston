/**
 * ============================================================================
 * API 速率限制中介軟體 (Rate Limiting Middleware)
 * ============================================================================
 * 實現基於 IP 和 API Key 的速率限制，防止濫用和 DDoS 攻擊
 * ============================================================================
 */

import { Request, Response, NextFunction } from 'express';

/**
 * 速率限制配置
 */
interface RateLimitConfig {
  windowMs: number; // 時間窗口 (毫秒)
  maxRequests: number; // 最大請求數
  message?: string; // 超限錯誤訊息
  statusCode?: number; // HTTP 狀態碼
  keyGenerator?: (req: Request) => string; // 生成限制鍵的函數
  skip?: (req: Request) => boolean; // 跳過限制的條件
  onLimitReached?: (req: Request) => void; // 達到限制時的回調
}

/**
 * 速率限制存儲
 */
interface RateLimitStore {
  get(key: string): Promise<number | null>;
  increment(key: string, windowMs: number): Promise<number>;
  reset(key: string): Promise<void>;
}

/**
 * Redis 客戶端接口
 * 定義與 Redis 客戶端交互所需的最小方法集，支持多種 Redis 客戶端實現
 * (如 ioredis, node-redis 等)
 */
interface RedisClientInterface {
  get(key: string): Promise<string | null>;
  multi(): RedisMultiInterface;
  del(key: string): Promise<number>;
}

/**
 * Redis Multi/Pipeline 接口
 * 用於批量執行 Redis 命令的事務或管道操作
 */
interface RedisMultiInterface {
  incr(key: string): RedisMultiInterface;
  pexpire(key: string, milliseconds: number): RedisMultiInterface;
  exec(): Promise<Array<[Error | null, unknown]>>;
}

/**
 * 內存存儲實現 (適用於單機部署)
 */
class MemoryStore implements RateLimitStore {
  private store: Map<string, { count: number; resetTime: number }> = new Map();

  async get(key: string): Promise<number | null> {
    const record = this.store.get(key);
    if (!record) {
      return null;
    }

    // 檢查是否過期
    if (Date.now() > record.resetTime) {
      this.store.delete(key);
      return null;
    }

    return record.count;
  }

  async increment(key: string, windowMs: number): Promise<number> {
    const now = Date.now();
    const record = this.store.get(key);

    if (!record || now > record.resetTime) {
      // 新記錄或已過期
      this.store.set(key, {
        count: 1,
        resetTime: now + windowMs,
      });
      return 1;
    }

    // 增加計數
    record.count++;
    return record.count;
  }

  async reset(key: string): Promise<void> {
    this.store.delete(key);
  }

  // 清理過期記錄
  cleanup(): void {
    const now = Date.now();
    for (const [key, record] of this.store.entries()) {
      if (now > record.resetTime) {
        this.store.delete(key);
      }
    }
  }
}

/**
 * Redis 存儲實現 (適用於分布式部署)
 */
class RedisStore implements RateLimitStore {
  constructor(private redisClient: RedisClientInterface) {}

  async get(key: string): Promise<number | null> {
    const value = await this.redisClient.get(key);
    return value ? parseInt(value, 10) : null;
  }

  async increment(key: string, windowMs: number): Promise<number> {
    const multi = this.redisClient.multi();
    multi.incr(key);
    multi.pexpire(key, windowMs);

    const results = await multi.exec();
    // 錯誤檢查與型別驗證
    if (!results || results.length === 0) {
      throw new Error('Redis multi command returned no results');
    }
    const [error, value] = results[0];
    if (error) {
      throw new Error(`Redis incr failed: ${error.message}`);
    }
    if (typeof value !== 'number') {
      throw new Error(`Unexpected Redis incr result type: ${typeof value}`);
    }
    return value;
  }

  async reset(key: string): Promise<void> {
    await this.redisClient.del(key);
  }
}

/**
 * 預設配置
 */
const defaultConfig: Required<Omit<RateLimitConfig, 'onLimitReached'>> = {
  windowMs: 60 * 1000, // 1 分鐘
  maxRequests: 100, // 100 請求
  message: 'Too many requests, please try again later.',
  statusCode: 429,
  keyGenerator: (req: Request) => {
    // 預設使用 IP 地址
    return req.ip || req.connection.remoteAddress || 'unknown';
  },
  skip: () => false,
};

/**
 * 創建速率限制中介軟體
 */
export function createRateLimiter(
  config: RateLimitConfig,
  store?: RateLimitStore
): (req: Request, res: Response, next: NextFunction) => Promise<void> {
  const finalConfig = { ...defaultConfig, ...config };
  const rateLimitStore = store || new MemoryStore();

  // 定期清理內存存儲 (使用弱引用避免記憶體洩漏)
  let cleanupInterval: NodeJS.Timeout | null = null;
  if (rateLimitStore instanceof MemoryStore) {
    cleanupInterval = setInterval(() => {
      rateLimitStore.cleanup();
    }, 60 * 1000); // 每分鐘清理一次

    // 允許 Node.js 進程退出時清理
    if (cleanupInterval.unref) {
      cleanupInterval.unref();
    }
  }

  return async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      // 檢查是否跳過限制
      if (finalConfig.skip(req)) {
        return next();
      }

      // 生成限制鍵
      const key = `rate_limit:${finalConfig.keyGenerator(req)}`;

      // 獲取當前計數
      const currentCount = await rateLimitStore.increment(key, finalConfig.windowMs);

      // 設置回應標頭
      res.setHeader('X-RateLimit-Limit', finalConfig.maxRequests.toString());
      res.setHeader(
        'X-RateLimit-Remaining',
        Math.max(0, finalConfig.maxRequests - currentCount).toString()
      );
      res.setHeader('X-RateLimit-Reset', new Date(Date.now() + finalConfig.windowMs).toISOString());

      // 檢查是否超過限制
      if (currentCount > finalConfig.maxRequests) {
        // 回調
        if (config.onLimitReached) {
          config.onLimitReached(req);
        }

        // 返回錯誤
        res.status(finalConfig.statusCode).json({
          error: 'Rate limit exceeded',
          message: finalConfig.message,
          retryAfter: Math.ceil(finalConfig.windowMs / 1000),
        });
        return;
      }

      next();
    } catch (error) {
      console.error('Rate limit error:', error);
      // 發生錯誤時允許請求通過（寬鬆模式）
      next();
    }
  };
}

/**
 * 預定義的速率限制配置
 */
export const rateLimitPresets = {
  /**
   * 嚴格限制 - 用於敏感端點
   */
  strict: {
    windowMs: 15 * 60 * 1000, // 15 分鐘
    maxRequests: 10, // 10 請求
    message: 'Too many requests from this IP, please try again after 15 minutes.',
  },

  /**
   * 標準限制 - 用於一般 API
   */
  standard: {
    windowMs: 60 * 1000, // 1 分鐘
    maxRequests: 60, // 60 請求
  },

  /**
   * 寬鬆限制 - 用於公共端點
   */
  lenient: {
    windowMs: 60 * 1000, // 1 分鐘
    maxRequests: 200, // 200 請求
  },

  /**
   * 基於 API Key 的限制
   */
  apiKey: {
    windowMs: 60 * 1000, // 1 分鐘
    maxRequests: 1000, // 1000 請求
    keyGenerator: (req: Request) => {
      const apiKey = req.headers['x-api-key'] as string;
      return apiKey || req.ip || 'unknown';
    },
  },
};

/**
 * 智能速率限制 - 根據請求類型自動選擇策略
 */
export function createSmartRateLimiter(store?: RateLimitStore) {
  return (req: Request, res: Response, next: NextFunction): void => {
    // 根據路徑選擇策略
    let config: RateLimitConfig;

    if (req.path.includes('/auth/') || req.path.includes('/admin/')) {
      config = rateLimitPresets.strict;
    } else if (req.path.startsWith('/api/v1/')) {
      // 檢查是否有 API Key
      const hasApiKey = !!req.headers['x-api-key'];
      config = hasApiKey ? rateLimitPresets.apiKey : rateLimitPresets.standard;
    } else {
      config = rateLimitPresets.lenient;
    }

    const limiter = createRateLimiter(config, store);
    limiter(req, res, next);
  };
}

// 導出存儲類
export { MemoryStore, RedisStore };
