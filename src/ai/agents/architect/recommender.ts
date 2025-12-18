import { AgentContext, AgentInsight } from '../../types.js';
import { layeredPattern } from './patterns/layered.js';
import { eventDrivenPattern } from './patterns/event-driven.js';
import { microservicesPattern } from './patterns/microservices.js';

export class ArchitectRecommender {
  recommend(context: AgentContext): AgentInsight {
    const cadence = this.detectDeploymentCadence(context);
    const pattern = cadence > 20 ? microservicesPattern : eventDrivenPattern;
    const alternative = cadence > 50 ? layeredPattern : microservicesPattern;
    return {
      title: 'Architecture Recommendation',
      description: `${pattern.name} suits current cadence; keep ${alternative.name} as contingency.`,
      signal: 'info',
      data: {
        cadencePerWeek: cadence,
        primaryPattern: pattern,
        contingencyPattern: alternative
      }
    };
  }

  private detectDeploymentCadence(context: AgentContext): number {
    const payload = context.payload ?? {};
    const cadence = payload['deploymentsPerWeek'];
    if (typeof cadence === 'number') {
      return cadence;
    }
    return 10;
  }
}
