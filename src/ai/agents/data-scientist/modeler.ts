import { AgentContext, AgentInsight } from '../../types.js';
import { regressionModel } from './models/regression.js';
import { classificationModel } from './models/classification.js';
import { clusteringModel } from './models/clustering.js';

export class DataScientistModeler {
  model(context: AgentContext): AgentInsight {
    const objective = this.resolveObjective(context);
    return {
      title: 'Model Selection',
      description: `Primary objective ${objective}`,
      signal: 'info',
      data: {
        regression: regressionModel,
        classification: classificationModel,
        clustering: clusteringModel,
      },
    };
  }

  private resolveObjective(context: AgentContext): string {
    const payload = context.payload ?? {};
    const objective = payload['mlObjective'];
    if (typeof objective === 'string') {
      return objective;
    }
    return 'forecasting';
  }
}
