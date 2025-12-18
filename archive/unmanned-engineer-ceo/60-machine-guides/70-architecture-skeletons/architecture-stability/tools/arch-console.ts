#!/usr/bin/env node
/**
 * Architecture Debug Console
 * 提供統一的偵錯與診斷入口
 */

import * as fs from 'fs'
import * as path from 'path'
import ArchitectureLinter from './arch-lint'

interface ConsoleOptions {
  config?: string
  output?: string
  format?: 'table' | 'json'
}

interface Summary {
  total: number
  byRule: Record<string, number>
  bySeverity: Record<string, number>
}

type CommandName = 'lint' | 'report' | 'list' | 'help'

const DEFAULT_CONFIG_PATH = path.resolve(__dirname, 'arch-lint.config.yml')
const DIAGNOSTICS_DIR = path.resolve(__dirname, '..', 'diagnostics')
const SKELETON_ROOT = path.resolve(__dirname, '..', '..')

async function runLint(options: ConsoleOptions): Promise<number> {
  const configPath = options.config ?? DEFAULT_CONFIG_PATH
  const linter = new ArchitectureLinter(configPath)
  const violations = await linter.lint()
  const summary = buildSummary(violations)

  printSummary('Architecture Lint Summary', summary)
  printViolations(violations, options.format ?? 'table')

  return summary.total === 0 ? 0 : 1
}

async function runReport(options: ConsoleOptions): Promise<number> {
  const configPath = options.config ?? DEFAULT_CONFIG_PATH
  const outputPath = options.output ?? path.resolve(DIAGNOSTICS_DIR, 'arch-report.json')

  const linter = new ArchitectureLinter(configPath)
  const violations = await linter.lint()
  const summary = buildSummary(violations)

  ensureDir(path.dirname(outputPath))
  const payload = {
    generatedAt: new Date().toISOString(),
    configPath,
    summary,
    violations
  }

  fs.writeFileSync(outputPath, JSON.stringify(payload, null, 2), 'utf8')
  console.log(`📄 Report saved to ${outputPath}`)

  return summary.total === 0 ? 0 : 1
}

function runList(options: ConsoleOptions): number {
  const entries = fs
    .readdirSync(SKELETON_ROOT, { withFileTypes: true })
    .filter(entry => entry.isDirectory())
    .map(entry => {
      const skeletonPath = path.join(SKELETON_ROOT, entry.name)
      const files = fs.readdirSync(skeletonPath, { withFileTypes: true })
      const hasTools = files.some(file => file.isDirectory() && file.name === 'tools')
      const hasDocs = files.some(file => file.isDirectory() && file.name === 'docs')
      const hasConfig = files.some(file => file.name.endsWith('.yaml') || file.name.endsWith('.yml'))

      return {
        name: entry.name,
        hasTools,
        hasDocs,
        hasConfig,
        fileCount: files.length
      }
    })

  if ((options.format ?? 'table') === 'json') {
    console.log(JSON.stringify(entries, null, 2))
  } else {
    console.log('\n骨架清單:')
    entries.forEach(item => {
      console.log(`- ${item.name}`)
      console.log(`  files: ${item.fileCount}, tools: ${item.hasTools ? 'yes' : 'no'}, docs: ${item.hasDocs ? 'yes' : 'no'}, config: ${item.hasConfig ? 'yes' : 'no'}`)
    })
    console.log('')
  }

  return 0
}

function buildSummary(violations: Array<{ rule: string; severity: string }>): Summary {
  return violations.reduce<Summary>((acc, violation) => {
    acc.total += 1
    acc.byRule[violation.rule] = (acc.byRule[violation.rule] ?? 0) + 1
    acc.bySeverity[violation.severity] = (acc.bySeverity[violation.severity] ?? 0) + 1
    return acc
  }, {
    total: 0,
    byRule: {},
    bySeverity: {}
  })
}

function printSummary(title: string, summary: Summary): void {
  console.log(`\n${title}`)
  console.log('='.repeat(title.length))
  console.log(`Total Violations: ${summary.total}`)
  Object.entries(summary.byRule).forEach(([rule, count]) => {
    console.log(`- ${rule}: ${count}`)
  })
  console.log('')
}

function printViolations(violations: Array<{ rule: string; severity: string; file: string; message: string }>, format: 'table' | 'json'): void {
  if (violations.length === 0) {
    console.log('✅ No violations found.')
    return
  }

  if (format === 'json') {
    console.log(JSON.stringify(violations, null, 2))
    return
  }

  console.log('Details:')
  violations.forEach(({ rule, severity, file, message }, index) => {
    console.log(`${index + 1}. [${severity.toUpperCase()}] ${rule}`)
    console.log(`   file: ${file}`)
    console.log(`   msg : ${message}`)
  })
}

function ensureDir(dirPath: string): void {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true })
  }
}

function parseArgs(): { command: CommandName; options: ConsoleOptions } {
  const argv = process.argv.slice(2)
  const command = (argv.shift() as CommandName) ?? 'help'
  const options: ConsoleOptions = {}

  while (argv.length > 0) {
    const token = argv.shift()
    if (!token) {
      continue
    }

    if (token.startsWith('--')) {
      const [key, rawValue] = token.replace(/^--/, '').split('=')
      const value = rawValue ?? argv.shift()
      switch (key) {
        case 'config':
          if (value) options.config = path.resolve(value)
          break
        case 'output':
          if (value) options.output = path.resolve(value)
          break
        case 'format':
          if (value === 'json' || value === 'table') {
            options.format = value
          }
          break
        default:
          break
      }
    }
  }

  return { command, options }
}

function printHelp(): void {
  console.log(`
Architecture Debug Console
Usage:
  arch-console lint [--config path] [--format table|json]
  arch-console report [--config path] [--output path]
  arch-console list [--format table|json]
`)
}

async function main(): Promise<void> {
  const { command, options } = parseArgs()

  switch (command) {
    case 'lint': {
      const exitCode = await runLint(options)
      process.exit(exitCode)
      break
    }
    case 'report': {
      const exitCode = await runReport(options)
      process.exit(exitCode)
      break
    }
    case 'list': {
      const exitCode = runList(options)
      process.exit(exitCode)
      break
    }
    default:
      printHelp()
      process.exit(0)
  }
}

main().catch(error => {
  console.error('Console execution failed:', error)
  process.exit(1)
})
