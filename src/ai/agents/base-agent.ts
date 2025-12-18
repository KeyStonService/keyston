import { AgentContext, AgentInsight, AgentModule, AgentReport } from '../types.js';

export abstract class BaseAgent implements AgentModule {
  public abstract readonly name: string;

  public async run(context: AgentContext): Promise<AgentReport> {
    const insights = await this.evaluate(context);
    return {
      agent: this.name,
      insights,
      generatedAt: new Date()
    };
  }

  protected abstract evaluate(context: AgentContext): Promise<AgentInsight[]>;
}
