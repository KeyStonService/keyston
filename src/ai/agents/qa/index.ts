import { AgentContext, AgentInsight } from '../../types.js';
import { BaseAgent } from '../base-agent.js';
import { QATester } from './tester.js';
import { QAValidator } from './validator.js';
import { QAReporter } from './reporter.js';
import { unitStrategy } from './strategies/unit.js';
import { integrationStrategy } from './strategies/integration.js';
import { e2eStrategy } from './strategies/e2e.js';

export class QAAgent extends BaseAgent {
  public readonly name = 'QAAgent';
  private readonly tester = new QATester();
  private readonly validator = new QAValidator();
  private readonly reporter = new QAReporter();

  protected async evaluate(context: AgentContext): Promise<AgentInsight[]> {
    return [
      this.tester.execute(context),
      this.validator.validate(context),
      this.reporter.report(context),
      this.strategyInsight()
    ];
  }

  private strategyInsight(): AgentInsight {
    return {
      title: 'QA Strategies',
      description: 'Unit, integration, and e2e strategies available.',
      signal: 'info',
      data: {
        unit: unitStrategy,
        integration: integrationStrategy,
        e2e: e2eStrategy
      }
    };
  }
}
