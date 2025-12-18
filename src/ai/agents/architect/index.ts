import { AgentContext, AgentInsight } from '../../types.js';
import { BaseAgent } from '../base-agent.js';
import { ArchitectAnalyzer } from './analyzer.js';
import { ArchitectOptimizer } from './optimizer.js';
import { ArchitectRecommender } from './recommender.js';

export class ArchitectAgent extends BaseAgent {
  public readonly name = 'ArchitectAgent';
  private readonly analyzer = new ArchitectAnalyzer();
  private readonly optimizer = new ArchitectOptimizer();
  private readonly recommender = new ArchitectRecommender();

  protected async evaluate(context: AgentContext): Promise<AgentInsight[]> {
    const insights = this.analyzer.analyze(context);
    insights.push(this.optimizer.optimize(context));
    insights.push(this.recommender.recommend(context));
    return insights;
  }
}
