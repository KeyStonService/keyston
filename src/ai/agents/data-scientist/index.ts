import { AgentContext, AgentInsight } from '../../types.js';
import { BaseAgent } from '../base-agent.js';
import { DataScientistAnalyzer } from './analyzer.js';
import { DataScientistModeler } from './modeler.js';
import { DataScientistPredictor } from './predictor.js';

export class DataScientistAgent extends BaseAgent {
  public readonly name = 'DataScientistAgent';
  private readonly analyzer = new DataScientistAnalyzer();
  private readonly modeler = new DataScientistModeler();
  private readonly predictor = new DataScientistPredictor();

  protected async evaluate(context: AgentContext): Promise<AgentInsight[]> {
    return [
      this.analyzer.analyze(context),
      this.modeler.model(context),
      this.predictor.predict(context),
    ];
  }
}
