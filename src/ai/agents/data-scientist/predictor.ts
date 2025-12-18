import { AgentContext, AgentInsight } from '../../types.js';

export class DataScientistPredictor {
  predict(context: AgentContext): AgentInsight {
    const horizon = this.resolveHorizon(context);
    const accuracy = this.estimateAccuracy(horizon);
    return {
      title: 'Prediction Forecast',
      description: `Forecast horizon ${horizon} hours`,
      signal: accuracy < 0.7 ? 'warn' : 'info',
      data: { horizonHours: horizon, expectedAccuracy: accuracy },
    };
  }

  private resolveHorizon(context: AgentContext): number {
    const payload = context.payload ?? {};
    const horizon = payload['forecastHours'];
    if (typeof horizon === 'number') {
      return Math.max(1, Math.min(72, horizon));
    }
    return 24;
  }

  private estimateAccuracy(horizon: number): number {
    return Math.max(0.5, 0.95 - horizon * 0.002);
  }
}
