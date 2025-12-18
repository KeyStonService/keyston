import cron from 'node-cron';
import { Queue, Worker, Job as BullJob } from 'bullmq';
import Redis from 'ioredis';
import { config } from './config';
import { logger } from './config/logger';
import { Job, JobOptions, JobExecution, JobStatus } from './types';

class Scheduler {
  private jobs: Map<string, Job>;
  private cronTasks: Map<string, cron.ScheduledTask>;
  private queue: Queue;
  private worker: Worker;
  private redis: Redis;
  private executionHistory: Map<string, JobExecution[]>;

  constructor() {
    this.jobs = new Map();
    this.cronTasks = new Map();
    this.executionHistory = new Map();

    // Initialize Redis connection
    this.redis = new Redis({
      host: config.redisHost,
      port: config.redisPort,
      maxRetriesPerRequest: null
    });

    // Initialize BullMQ queue
    this.queue = new Queue('scheduled-jobs', {
      connection: this.redis
    });

    // Initialize worker
    this.worker = new Worker(
      'scheduled-jobs',
      async (job: BullJob) => {
        return await this.executeJob(job.name, job.data);
      },
      {
        connection: this.redis,
        concurrency: config.maxConcurrentJobs
      }
    );

    this.setupWorkerHandlers();
    logger.info('Scheduler initialized');
  }

  private setupWorkerHandlers(): void {
    this.worker.on('completed', (job: BullJob) => {
      logger.info(`Job ${job.name} completed successfully`);
      this.recordExecution(job.name, 'completed', null);
    });

    this.worker.on('failed', (job: BullJob | undefined, error: Error) => {
      if (job) {
        logger.error(`Job ${job.name} failed: ${error.message}`);
        this.recordExecution(job.name, 'failed', error);
      }
    });
  }

  /**
   * Schedule a job with cron expression
   */
  public schedule(
    name: string,
    cronExpression: string,
    handler: () => Promise<void>,
    options: JobOptions = {}
  ): void {
    if (!cron.validate(cronExpression)) {
      throw new Error(`Invalid cron expression: ${cronExpression}`);
    }

    const job: Job = {
      id: name,
      name,
      type: 'cron',
      cronExpression,
      handler,
      enabled: options.enabled !== false,
      priority: options.priority || 'normal',
      maxRetries: options.maxRetries || 3,
      timeout: options.timeout || config.jobTimeout,
      timezone: options.timezone || 'UTC',
      metadata: options.metadata || {},
      createdAt: new Date(),
      lastExecutedAt: null,
      nextExecutionAt: null
    };

    this.jobs.set(name, job);

    if (job.enabled) {
      const task = cron.schedule(
        cronExpression,
        async () => {
          await this.queue.add(name, {}, {
            priority: this.getPriorityValue(job.priority),
            attempts: job.maxRetries,
            backoff: { type: 'exponential', delay: 5000 }
          });
        },
        {
          scheduled: true,
          timezone: job.timezone
        }
      );

      this.cronTasks.set(name, task);
      logger.info(`Scheduled job: ${name} with cron: ${cronExpression}`);
    }
  }

  /**
   * Schedule a one-time job
   */
  public scheduleOnce(
    name: string,
    executeAt: Date,
    handler: () => Promise<void>,
    options: JobOptions = {}
  ): void {
    const job: Job = {
      id: name,
      name,
      type: 'once',
      executeAt,
      handler,
      enabled: true,
      priority: options.priority || 'normal',
      maxRetries: options.maxRetries || 3,
      timeout: options.timeout || config.jobTimeout,
      timezone: options.timezone || 'UTC',
      metadata: options.metadata || {},
      createdAt: new Date(),
      lastExecutedAt: null,
      nextExecutionAt: executeAt
    };

    this.jobs.set(name, job);

    const delay = executeAt.getTime() - Date.now();
    if (delay > 0) {
      this.queue.add(name, {}, {
        delay,
        priority: this.getPriorityValue(job.priority),
        attempts: job.maxRetries
      });
      logger.info(`Scheduled one-time job: ${name} at ${executeAt.toISOString()}`);
    }
  }

  /**
   * Schedule a job with interval
   */
  public scheduleInterval(
    name: string,
    intervalMs: number,
    handler: () => Promise<void>,
    options: JobOptions = {}
  ): void {
    const job: Job = {
      id: name,
      name,
      type: 'interval',
      interval: intervalMs,
      handler,
      enabled: options.enabled !== false,
      priority: options.priority || 'normal',
      maxRetries: options.maxRetries || 3,
      timeout: options.timeout || config.jobTimeout,
      timezone: options.timezone || 'UTC',
      metadata: options.metadata || {},
      createdAt: new Date(),
      lastExecutedAt: null,
      nextExecutionAt: new Date(Date.now() + intervalMs)
    };

    this.jobs.set(name, job);

    if (job.enabled) {
      this.queue.add(name, {}, {
        repeat: { every: intervalMs },
        priority: this.getPriorityValue(job.priority)
      });
      logger.info(`Scheduled interval job: ${name} every ${intervalMs}ms`);
    }
  }

  /**
   * Execute a job
   */
  private async executeJob(name: string, data: any): Promise<any> {
    const job = this.jobs.get(name);
    if (!job) {
      throw new Error(`Job not found: ${name}`);
    }

    const startTime = Date.now();
    job.lastExecutedAt = new Date();

    try {
      logger.info(`Executing job: ${name}`);
      const result = await Promise.race([
        job.handler(),
        new Promise((_, reject) =>
          setTimeout(() => reject(new Error('Job timeout')), job.timeout)
        )
      ]);

      const executionTime = Date.now() - startTime;
      logger.info(`Job ${name} completed in ${executionTime}ms`);

      return result;
    } catch (error) {
      logger.error(`Job ${name} failed:`, error);
      throw error;
    }
  }

  /**
   * Pause a job
   */
  public pauseJob(name: string): void {
    const job = this.jobs.get(name);
    if (!job) {
      throw new Error(`Job not found: ${name}`);
    }

    job.enabled = false;
    const cronTask = this.cronTasks.get(name);
    if (cronTask) {
      cronTask.stop();
    }

    logger.info(`Job paused: ${name}`);
  }

  /**
   * Resume a job
   */
  public resumeJob(name: string): void {
    const job = this.jobs.get(name);
    if (!job) {
      throw new Error(`Job not found: ${name}`);
    }

    job.enabled = true;
    const cronTask = this.cronTasks.get(name);
    if (cronTask) {
      cronTask.start();
    }

    logger.info(`Job resumed: ${name}`);
  }

  /**
   * Delete a job
   */
  public deleteJob(name: string): void {
    const cronTask = this.cronTasks.get(name);
    if (cronTask) {
      cronTask.stop();
      this.cronTasks.delete(name);
    }

    this.jobs.delete(name);
    logger.info(`Job deleted: ${name}`);
  }

  /**
   * Get job details
   */
  public getJob(name: string): Job | undefined {
    return this.jobs.get(name);
  }

  /**
   * List all jobs
   */
  public listJobs(): Job[] {
    return Array.from(this.jobs.values());
  }

  /**
   * Get job execution history
   */
  public getJobHistory(name: string, options: { limit?: number } = {}): JobExecution[] {
    const history = this.executionHistory.get(name) || [];
    const limit = options.limit || 100;
    return history.slice(0, limit);
  }

  /**
   * Record job execution
   */
  private recordExecution(name: string, status: JobStatus, error: Error | null): void {
    const execution: JobExecution = {
      jobId: name,
      status,
      executedAt: new Date(),
      error: error?.message
    };

    if (!this.executionHistory.has(name)) {
      this.executionHistory.set(name, []);
    }

    const history = this.executionHistory.get(name)!;
    history.unshift(execution);

    // Keep only recent executions
    const MAX_HISTORY_SIZE = 1000;
    if (history.length > MAX_HISTORY_SIZE) {
      history.pop();
    }
  }

  /**
   * Get priority value for BullMQ
   */
  private getPriorityValue(priority: string): number {
    const PRIORITY_VALUES: Record<string, number> = {
      critical: 1,
      high: 2,
      normal: 3,
      low: 4
    };
    const DEFAULT_PRIORITY = PRIORITY_VALUES.normal;
    return PRIORITY_VALUES[priority] || DEFAULT_PRIORITY;
  }

  /**
   * Cleanup and shutdown
   */
  public async shutdown(): Promise<void> {
    logger.info('Shutting down scheduler...');

    // Stop all cron tasks
    for (const task of this.cronTasks.values()) {
      task.stop();
    }

    // Close worker and queue
    await this.worker.close();
    await this.queue.close();
    await this.redis.quit();

    logger.info('Scheduler shutdown complete');
  }
}

// Create singleton instance
export const scheduler = new Scheduler();

// Graceful shutdown
process.on('SIGINT', async () => {
  await scheduler.shutdown();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  await scheduler.shutdown();
  process.exit(0);
});
