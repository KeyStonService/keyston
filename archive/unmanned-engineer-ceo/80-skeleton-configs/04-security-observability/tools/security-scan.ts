#!/usr/bin/env node
/**
 * Security Scanner
 * 掃描代碼中的安全問題
 */

import * as fs from 'fs'
import * as path from 'path'
import { glob } from 'glob'

interface SecurityIssue {
  severity: 'critical' | 'high' | 'medium' | 'low'
  category: string
  file: string
  line: number
  description: string
  recommendation: string
}

class SecurityScanner {
  private issues: SecurityIssue[] = []

  // 安全規則定義
  private readonly rules = [
    {
      id: 'hardcoded-secret',
      pattern: /(password|secret|key|token)\s*=\s*['"][^'"]{8,}['"]/gi,
      severity: 'critical' as const,
      category: 'Hardcoded Secrets',
      description: '偵測到硬編碼的密碼或密鑰',
      recommendation: '使用環境變數或密鑰管理系統'
    },
    {
      id: 'sql-injection',
      pattern: /execute\s*\(\s*['"].*\$\{.*\}.*['"]\s*\)/gi,
      severity: 'high' as const,
      category: 'SQL Injection',
      description: '可能存在 SQL 注入風險',
      recommendation: '使用參數化查詢或 ORM'
    },
    {
      id: 'eval-usage',
      pattern: /\beval\s*\(/gi,
      severity: 'high' as const,
      category: 'Code Injection',
      description: '使用 eval() 可能導致代碼注入',
      recommendation: '避免使用 eval，使用安全的替代方案'
    },
    {
      id: 'insecure-randomness',
      pattern: /Math\.random\(\)/gi,
      severity: 'medium' as const,
      category: 'Weak Randomness',
      description: 'Math.random() 不適合安全用途',
      recommendation: '使用 crypto.randomBytes() 或 crypto.randomUUID()'
    },
    {
      id: 'missing-input-validation',
      pattern: /(req\.body|req\.query|req\.params)\.\w+(?!.*validate|.*schema)/gi,
      severity: 'medium' as const,
      category: 'Input Validation',
      description: '缺少輸入驗證',
      recommendation: '使用 Zod, Joi 等進行輸入驗證'
    },
    {
      id: 'console-log',
      pattern: /console\.(log|debug|info|warn|error)\(/gi,
      severity: 'low' as const,
      category: 'Information Disclosure',
      description: '使用 console.log 可能洩漏敏感資訊',
      recommendation: '使用結構化日誌系統並過濾敏感資訊'
    }
  ]

  async scan(patterns: string[]): Promise<SecurityIssue[]> {
    for (const pattern of patterns) {
      const files = await glob(pattern, {
        ignore: ['node_modules/**', 'dist/**', 'build/**', '**/*.test.ts']
      })

      for (const file of files) {
        await this.scanFile(file)
      }
    }

    return this.issues
  }

  private async scanFile(filePath: string): Promise<void> {
    const content = fs.readFileSync(filePath, 'utf8')
    const lines = content.split('\n')

    for (const rule of this.rules) {
      let match
      const regex = new RegExp(rule.pattern)

      lines.forEach((line, index) => {
        regex.lastIndex = 0  // 重置 regex
        while ((match = regex.exec(line)) !== null) {
          // 跳過註釋中的匹配
          if (line.trim().startsWith('//') || line.trim().startsWith('*')) {
            continue
          }

          this.issues.push({
            severity: rule.severity,
            category: rule.category,
            file: filePath,
            line: index + 1,
            description: rule.description,
            recommendation: rule.recommendation
          })
        }
      })
    }
  }

  printReport(): void {
    if (this.issues.length === 0) {
      console.log('✅ 未發現安全問題!\n')
      return
    }

    console.log(`\n⚠️  發現 ${this.issues.length} 個安全問題:\n`)

    // 按嚴重程度分組
    const grouped = this.groupBy(this.issues, 'severity')
    const severityOrder = ['critical', 'high', 'medium', 'low']

    for (const severity of severityOrder) {
      const items = grouped[severity] || []
      if (items.length === 0) continue

      const icon = {
        critical: '🔴',
        high: '🟠',
        medium: '🟡',
        low: '🔵'
      }[severity]

      console.log(`${icon} ${severity.toUpperCase()} (${items.length})`)
      console.log('─'.repeat(60))

      items.forEach(issue => {
        console.log(`\n[${issue.category}] ${issue.file}:${issue.line}`)
        console.log(`  ${issue.description}`)
        console.log(`  💡 ${issue.recommendation}`)
      })

      console.log()
    }

    // 統計摘要
    console.log('\n📊 摘要')
    console.log('─'.repeat(60))
    severityOrder.forEach(severity => {
      const count = (grouped[severity] || []).length
      if (count > 0) {
        console.log(`${severity}: ${count}`)
      }
    })

    // 如果有 critical 或 high，建議失敗
    const criticalCount = (grouped.critical || []).length
    const highCount = (grouped.high || []).length

    if (criticalCount > 0 || highCount > 0) {
      console.log('\n❌ 存在高風險問題，建議修復後再繼續\n')
      process.exit(1)
    }
  }

  private groupBy<T>(array: T[], key: keyof T): Record<string, T[]> {
    return array.reduce((result, item) => {
      const group = String(item[key])
      if (!result[group]) {
        result[group] = []
      }
      result[group].push(item)
      return result
    }, {} as Record<string, T[]>)
  }
}

// CLI
if (require.main === module) {
  const patterns = process.argv.slice(2)
  
  if (patterns.length === 0) {
    patterns.push('**/*.ts', '**/*.js')
  }

  const scanner = new SecurityScanner()
  
  scanner.scan(patterns).then(() => {
    scanner.printReport()
  }).catch(error => {
    console.error('掃描失敗:', error)
    process.exit(1)
  })
}

export default SecurityScanner