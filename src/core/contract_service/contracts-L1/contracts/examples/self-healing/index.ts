/**
 * Self-Healing Examples - Index
 * 
 * Export all example functions for programmatic access
 */

export { basicUsageExample } from './01-basic-usage';
export { customConfigurationExample } from './02-custom-configuration';
export { monitoringGovernanceExample } from './03-monitoring-governance';
export { eventSubscriptionExample } from './04-event-subscription';
export { completeDemoExample } from './05-complete-demo';
export { runAllExamples } from './run-all-examples';

/**
 * Quick reference for running examples:
 * 
 * ```typescript
 * import { 
 *   basicUsageExample,
 *   customConfigurationExample,
 *   monitoringGovernanceExample,
 *   eventSubscriptionExample,
 *   completeDemoExample,
 *   runAllExamples
 * } from './examples/self-healing';
 * 
 * // Run a single example
 * await basicUsageExample();
 * 
 * // Run all examples
 * await runAllExamples();
 * ```
 * 
 * Or run from command line:
 * 
 * ```bash
 * npm run examples:self-healing          # Run all examples
 * npm run example:basic                  # Run basic usage
 * npm run example:config                 # Run custom configuration
 * npm run example:monitoring             # Run monitoring & governance
 * npm run example:events                 # Run event subscription
 * npm run example:demo                   # Run complete demo
 * ```
 */
