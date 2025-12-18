export type JobType = 'cron' | 'once' | 'interval';
export type JobPriority = 'low' | 'normal' | 'high' | 'critical';
export type JobStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

export interface Job {
  id: string;
  name: string;
  type: JobType;
  cronExpression?: string;
  executeAt?: Date;
  interval?: number;
  handler: () => Promise<void>;
  enabled: boolean;
  priority: JobPriority;
  maxRetries: number;
  timeout: number;
  timezone: string;
  metadata: Record<string, any>;
  createdAt: Date;
  lastExecutedAt: Date | null;
  nextExecutionAt: Date | null;
}

export interface JobOptions {
  timezone?: string;
  priority?: JobPriority;
  maxRetries?: number;
  retryDelay?: number;
  timeout?: number;
  enabled?: boolean;
  metadata?: Record<string, any>;
  onSuccess?: (result: any) => void;
  onFailure?: (error: Error) => void;
}

export interface JobExecution {
  jobId: string;
  status: JobStatus;
  executedAt: Date;
  error?: string;
}
