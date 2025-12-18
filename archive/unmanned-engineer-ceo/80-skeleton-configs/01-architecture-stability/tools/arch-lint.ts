#!/usr/bin/env node
/**
 * Architecture Linter
 * 檢查代碼是否符合架構規則
 */

import * as fs from 'fs'
import * as path from 'path'
import * as yaml from 'js-yaml'
import { glob } from 'glob'
import madge from 'madge'

interface Config {
  rules: {
    layering: LayeringRule
    circularDependencies: { enabled: boolean; severity: string }
    externalDependencies: ExternalDepsRule
    namingConventions: NamingRule
    fileOrganization: FileOrgRule
  }
  exemptions: Exemption[]
}

interface LayeringRule {
  enabled: boolean
  layers: Layer[]
}

interface Layer {
  name: string
  path: string
  canDependOn?: string[]
  cannotDependOn?: string[]
}

interface Violation {
  rule: string
  severity: 'error' | 'warning'
  file: string
  message: string
}

class ArchitectureLinter {
  private config: Config
  private violations: Violation[] = []

  constructor(configPath: string) {
    this.config = yaml.load(
      fs.readFileSync(configPath, 'utf8')
    ) as Config
  }

  async lint(): Promise<Violation[]> {
    if (this.config.rules.layering.enabled) {
      await this.checkLayering()
    }

    if (this.config.rules.circularDependencies.enabled) {
      await this.checkCircularDependencies()
    }

    if (this.config.rules.namingConventions.enabled) {
      this.checkNamingConventions()
    }

    if (this.config.rules.fileOrganization.enabled) {
      this.checkFileOrganization()
    }

    return this.violations
  }

  private async checkLayering(): Promise<void> {
    const { layers } = this.config.rules.layering

    for (const layer of layers) {
      const files = await glob(layer.path)
      
      for (const file of files) {
        const content = fs.readFileSync(file, 'utf8')
        const imports = this.extractImports(content)

        for (const imp of imports) {
          const targetLayer = this.getLayerForPath(imp)
          
          if (!targetLayer) continue

          // 檢查是否允許依賴
          const canDepend = layer.canDependOn || []
          const cannotDepend = layer.cannotDependOn || []

          if (cannotDepend.includes(targetLayer.name)) {
            this.violations.push({
              rule: 'layering',
              severity: 'error',
              file,
              message: `Layer "${layer.name}" cannot depend on "${targetLayer.name}". Found import: ${imp}`
            })
          }

          if (canDepend.length > 0 && !canDepend.includes(targetLayer.name)) {
            this.violations.push({
              rule: 'layering',
              severity: 'error',
              file,
              message: `Layer "${layer.name}" can only depend on [${canDepend.join(', ')}]. Found import from "${targetLayer.name}": ${imp}`
            })
          }
        }
      }
    }
  }

  private async checkCircularDependencies(): Promise<void> {
    try {
      const res = await madge('./', {
        fileExtensions: ['ts', 'tsx', 'js', 'jsx'],
        excludeRegExp: [/node_modules/, /dist/, /build/]
      })

      const circular = res.circular()

      if (circular.length > 0) {
        circular.forEach((cycle: string[]) => {
          this.violations.push({
            rule: 'circular-dependencies',
            severity: 'error',
            file: cycle[0],
            message: `Circular dependency detected: ${cycle.join(' -> ')}`
          })
        })
      }
    } catch (error) {
      console.error('Error checking circular dependencies:', error)
    }
  }

  private checkNamingConventions(): void {
    const { patterns } = this.config.rules.namingConventions

    // 檢查服務命名
    const services = fs.readdirSync('services', { withFileTypes: true })
      .filter(d => d.isDirectory())

    services.forEach(service => {
      const regex = new RegExp(patterns.service)
      if (!regex.test(service.name)) {
        this.violations.push({
          rule: 'naming-conventions',
          severity: 'warning',
          file: `services/${service.name}`,
          message: `Service name "${service.name}" does not match pattern ${patterns.service}`
        })
      }
    })
  }

  private checkFileOrganization(): void {
    const { requireReadme, requireTests } = this.config.rules.fileOrganization

    const services = fs.readdirSync('services', { withFileTypes: true })
      .filter(d => d.isDirectory())

    services.forEach(service => {
      const servicePath = path.join('services', service.name)

      if (requireReadme) {
        const readmePath = path.join(servicePath, 'README.md')
        if (!fs.existsSync(readmePath)) {
          this.violations.push({
            rule: 'file-organization',
            severity: 'warning',
            file: servicePath,
            message: 'Missing README.md'
          })
        }
      }

      if (requireTests) {
        const testsPath = path.join(servicePath, 'tests')
        if (!fs.existsSync(testsPath)) {
          this.violations.push({
            rule: 'file-organization',
            severity: 'warning',
            file: servicePath,
            message: 'Missing tests directory'
          })
        }
      }
    })
  }

  private extractImports(content: string): string[] {
    const imports: string[] = []
    
    // ES6 imports
    const es6Regex = /import\s+(?:.*?\s+from\s+)?['"]([^'"]+)['"]/g
    let match
    while ((match = es6Regex.exec(content)) !== null) {
      imports.push(match[1])
    }

    // CommonJS requires
    const cjsRegex = /require\s*\(['"]([^'"]+)['"]\)/g
    while ((match = cjsRegex.exec(content)) !== null) {
      imports.push(match[1])
    }

    return imports
  }

  private getLayerForPath(importPath: string): Layer | null {
    const { layers } = this.config.rules.layering

    for (const layer of layers) {
      // 移除 path 中的 glob 符號進行匹配
      const layerBase = layer.path.replace('/**', '')
      if (importPath.startsWith(layerBase) || importPath.startsWith(`@${layerBase}`)) {
        return layer
      }
    }

    return null
  }

  printReport(): void {
    if (this.violations.length === 0) {
      console.log('✅ No architecture violations found!')
      return
    }

    console.log(`\n❌ Found ${this.violations.length} architecture violations:\n`)

    const errors = this.violations.filter(v => v.severity === 'error')
    const warnings = this.violations.filter(v => v.severity === 'warning')

    if (errors.length > 0) {
      console.log('Errors:')
      errors.forEach(v => {
        console.log(`  [${v.rule}] ${v.file}`)
        console.log(`    ${v.message}\n`)
      })
    }

    if (warnings.length > 0) {
      console.log('Warnings:')
      warnings.forEach(v => {
        console.log(`  [${v.rule}] ${v.file}`)
        console.log(`    ${v.message}\n`)
      })
    }

    process.exit(errors.length > 0 ? 1 : 0)
  }
}

// CLI
if (require.main === module) {
  const configPath = process.argv[2] || './arch-lint.config.yml'
  
  const linter = new ArchitectureLinter(configPath)
  
  linter.lint().then(() => {
    linter.printReport()
  }).catch(error => {
    console.error('Linting failed:', error)
    process.exit(1)
  })
}

export default ArchitectureLinter