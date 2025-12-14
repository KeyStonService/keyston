import { z } from 'zod';

const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
  PORT: z.coerce.number().min(1).max(65535).default(3000),
  LOG_LEVEL: z.enum(['error', 'warn', 'info', 'debug']).default('info'),
  SERVICE_NAME: z.string().default('contracts-l1'),
  SERVICE_VERSION: z.string().default('1.0.0'),
  DATABASE_URL: z.string().optional(),
  REDIS_URL: z.string().optional(),
  BUILD_SHA: z.string().optional(),
  BUILD_TIME: z.string().optional(),
  WE_TONKE: z.string().optional(),
});

export type Config = z.infer<typeof envSchema>;

function loadConfig(): Config {
  try {
    const parsed = envSchema.parse(process.env);
    console.log('Configuration loaded successfully:', {
      NODE_ENV: parsed.NODE_ENV,
      PORT: parsed.PORT,
      SERVICE_NAME: parsed.SERVICE_NAME,
      sources: {
        env_file: !!process.env.npm_config_env,
        process_env: true,
        defaults_applied: true,
      },
      timestamp: new Date().toISOString(),
    });
    return parsed;
  } catch (error) {
    console.error('Configuration validation failed:', error);
    process.exit(1);
  }
}

export const config: Readonly<Config> = Object.freeze(loadConfig());
export const validateConfig = (env: Record<string, unknown>): Config => envSchema.parse(env);
export default config;
