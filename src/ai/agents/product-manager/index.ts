import { AgentContext, AgentInsight } from '../../types.js';
import { BaseAgent } from '../base-agent.js';
import { ProductPrioritizer } from './prioritizer.js';
import { ProductRoadmap } from './roadmap.js';
import { ProductFeedback } from './feedback.js';
import { kpis } from './metrics/kpis.js';
import { analyticsSignals } from './metrics/analytics.js';
import { reportingMatrix } from './metrics/reporting.js';

export class ProductManagerAgent extends BaseAgent {
  public readonly name = 'ProductManagerAgent';
  private readonly prioritizer = new ProductPrioritizer();
  private readonly roadmap = new ProductRoadmap();
  private readonly feedback = new ProductFeedback();

  protected async evaluate(context: AgentContext): Promise<AgentInsight[]> {
    return [
      this.prioritizer.prioritize(context),
      this.roadmap.plan(context),
      this.feedback.analyze(context),
      this.metricInsight(),
    ];
  }

  private metricInsight(): AgentInsight {
    return {
      title: 'Product Metrics',
      description: 'KPIs, analytics signals, and reporting cadence registered.',
      signal: 'info',
      data: { kpis, analyticsSignals, reportingMatrix },
    };
  }
}
