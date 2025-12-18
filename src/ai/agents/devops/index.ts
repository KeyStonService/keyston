import { AgentContext, AgentInsight } from '../../types.js';
import { BaseAgent } from '../base-agent.js';

import { DevOpsDeployer } from './deployer.js';
import { DevOpsMonitor } from './monitor.js';
import { buildPipeline } from './pipelines/build.js';
import { deployPipeline } from './pipelines/deploy.js';
import { testPipeline } from './pipelines/test.js';
import { DevOpsScaler } from './scaler.js';

export class DevOpsAgent extends BaseAgent {
  public readonly name = 'DevOpsAgent';
  private readonly _deployer = new DevOpsDeployer();
  private readonly _monitor = new DevOpsMonitor();
  private readonly _scaler = new DevOpsScaler();

  protected evaluate(context: AgentContext): Promise<AgentInsight[]> {
    return Promise.resolve([
      this._monitor.monitor(context),
      this._scaler.scale(context),
      this._deployer.deploy(context),
      this._pipelineInsight(),
    ]);
  }

  private _pipelineInsight(): AgentInsight {
    return {
      title: 'Pipeline Catalog',
      description: 'Build, test, and deploy pipelines registered.',
      signal: 'info',
      data: {
        build: buildPipeline,
        test: testPipeline,
        deploy: deployPipeline,
      },
    };
  }
}
