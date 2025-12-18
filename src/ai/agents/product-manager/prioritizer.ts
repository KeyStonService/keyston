import { AgentContext, AgentInsight } from '../../types.js';

export class ProductPrioritizer {
  prioritize(context: AgentContext): AgentInsight {
    const backlog = this._extractBacklog(context);
    return {
      title: 'Backlog Prioritization',
      description: `Scored ${backlog.length} backlog entries`,
      signal: backlog.length === 0 ? 'warn' : 'info',
      data: { backlog },
    };
  }

  private _extractBacklog(context: AgentContext): Array<{ id: string; score: number }> {
    const payload = context.payload ?? {};
    const items = payload['backlog'];
    if (!Array.isArray(items)) {
      return [];
    }
    return items
      .filter((item): item is { id: string; score: number } => this._isBacklogItem(item))
      .map((item) => ({ id: item.id, score: item.score }));
  }

  private _isBacklogItem(value: unknown): value is { id: string; score: number } {
    if (typeof value !== 'object' || value === null) {
      return false;
    }
    const candidate = value as { id?: unknown; score?: unknown };
    return typeof candidate.id === 'string' && typeof candidate.score === 'number';
  }
}
