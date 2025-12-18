/**
 * Run All Self-Healing Examples
 * 
 * Executes all example scripts in sequence and provides a summary
 */

import { basicUsageExample } from './01-basic-usage';
import { customConfigurationExample } from './02-custom-configuration';
import { monitoringGovernanceExample } from './03-monitoring-governance';
import { eventSubscriptionExample } from './04-event-subscription';
import { completeDemoExample } from './05-complete-demo';

interface ExampleResult {
  name: string;
  success: boolean;
  duration: number;
  error?: Error;
}

async function runExample(
  name: string,
  fn: () => Promise<void>
): Promise<ExampleResult> {
  const start = Date.now();
  
  try {
    await fn();
    return {
      name,
      success: true,
      duration: Date.now() - start,
    };
  } catch (error) {
    return {
      name,
      success: false,
      duration: Date.now() - start,
      error: error as Error,
    };
  }
}

async function runAllExamples() {
  console.log('╔════════════════════════════════════════════════════════════╗');
  console.log('║   Running All Self-Healing Examples                       ║');
  console.log('╚════════════════════════════════════════════════════════════╝\n');

  const examples = [
    { name: '01. Basic Usage', fn: basicUsageExample },
    { name: '02. Custom Configuration', fn: customConfigurationExample },
    { name: '03. Monitoring & Governance', fn: monitoringGovernanceExample },
    { name: '04. Event Subscription', fn: eventSubscriptionExample },
    { name: '05. Complete Demo', fn: completeDemoExample },
  ];

  const results: ExampleResult[] = [];

  for (const example of examples) {
    console.log(`\n${'='.repeat(60)}`);
    console.log(`Running: ${example.name}`);
    console.log('='.repeat(60) + '\n');

    const result = await runExample(example.name, example.fn);
    results.push(result);

    if (result.success) {
      console.log(`\n✅ ${example.name} completed in ${result.duration}ms`);
    } else {
      console.log(`\n❌ ${example.name} failed after ${result.duration}ms`);
      console.error('Error:', result.error?.message);
    }
  }

  // Summary
  console.log('\n\n╔════════════════════════════════════════════════════════════╗');
  console.log('║   Examples Summary                                         ║');
  console.log('╚════════════════════════════════════════════════════════════╝\n');

  const successful = results.filter((r) => r.success).length;
  const failed = results.filter((r) => !r.success).length;
  const totalDuration = results.reduce((sum, r) => sum + r.duration, 0);

  console.log(`📊 Results:`);
  console.log(`   - Total examples: ${results.length}`);
  console.log(`   - Successful: ${successful}`);
  console.log(`   - Failed: ${failed}`);
  console.log(`   - Total duration: ${totalDuration}ms`);
  console.log('');

  results.forEach((result) => {
    const status = result.success ? '✅' : '❌';
    console.log(`   ${status} ${result.name} (${result.duration}ms)`);
  });

  if (failed > 0) {
    console.log('\n⚠️  Some examples failed. Review the output above for details.\n');
    process.exit(1);
  } else {
    console.log('\n🎉 All examples completed successfully!\n');
    process.exit(0);
  }
}

// Run if executed directly
if (require.main === module) {
  runAllExamples().catch((error) => {
    console.error('Failed to run examples:', error);
    process.exit(1);
  });
}

export { runAllExamples };
