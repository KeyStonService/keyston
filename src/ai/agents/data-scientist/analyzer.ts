import { AgentContext, AgentInsight } from '../../types.js';

export class DataScientistAnalyzer {
  analyze(context: AgentContext): AgentInsight {
    const datasets = this.resolveDatasets(context);
    return {
      title: 'Data Audit',
      description: `Ready to process ${datasets.length} datasets`,
      signal: datasets.length === 0 ? 'warn' : 'info',
      data: { datasets },
    };
  }

  private resolveDatasets(context: AgentContext): string[] {
    const payload = context.payload ?? {};
    const datasets = payload['datasets'];
    if (Array.isArray(datasets)) {
      return datasets.filter((dataset): dataset is string => typeof dataset === 'string');
    }
    return [];
  }
}
