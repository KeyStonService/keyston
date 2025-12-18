#!/usr/bin/env node
/**
 * Log Validator
 * 驗證日誌是否符合 schema
 */

import Ajv from 'ajv'
import addFormats from 'ajv-formats'
import * as fs from 'fs'
import * as readline from 'readline'

class LogValidator {
  private ajv: Ajv
  private schema: any
  private errors: Array<{line: number, error: string, log: any}> = []

  constructor(schemaPath: string) {
    this.ajv = new Ajv({ allErrors: true, strict: false })
    addFormats(this.ajv)
    
    this.schema = JSON.parse(fs.readFileSync(schemaPath, 'utf8'))
  }

  async validateFile(logFile: string): Promise<void> {
    const fileStream = fs.createReadStream(logFile)
    const rl = readline.createInterface({
      input: fileStream,
      crlfDelay: Infinity
    })

    let lineNumber = 0

    for await (const line of rl) {
      lineNumber++
      
      if (!line.trim()) continue

      try {
        const log = JSON.parse(line)
        const valid = this.ajv.validate(this.schema, log)

        if (!valid) {
          this.errors.push({
            line: lineNumber,
            error: this.ajv.errorsText(),
            log
          })
        }

        // 額外檢查
        this.checkSensitiveData(log, lineNumber)
        
      } catch (error) {
        this.errors.push({
          line: lineNumber,
          error: `Invalid JSON: ${error}`,
          log: line
        })
      }
    }
  }

  private checkSensitiveData(log: any, lineNumber: number): void {
    const sensitivePatterns = [
      { pattern: /password/i, name: 'password' },
      { pattern: /token/i, name: 'token' },
      { pattern: /secret/i, name: 'secret' },
      { pattern: /\b\d{16}\b/, name: 'credit card' },
      { pattern: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/, name: 'email' }
    ]

    const logStr = JSON.stringify(log)

    for (const { pattern, name } of sensitivePatterns) {
      if (pattern.test(logStr)) {
        this.errors.push({
          line: lineNumber,
          error: `Potential sensitive data: ${name}`,
          log
        })
      }
    }
  }

  printReport(): void {
    if (this.errors.length === 0) {
      console.log('✅ 所有日誌符合 schema!\n')
      return
    }

    console.log(`\n❌ 發現 ${this.errors.length} 個問題:\n`)

    this.errors.forEach(({ line, error, log }) => {
      console.log(`Line ${line}:`)
      console.log(`  Error: ${error}`)
      console.log(`  Log: ${JSON.stringify(log).substring(0, 100)}...`)
      console.log()
    })

    process.exit(1)
  }
}

// CLI
if (require.main === module) {
  const schemaPath = process.argv[2] || './config/log-schema.json'
  const logFile = process.argv[3]

  if (!logFile) {
    console.error('Usage: log-validator.ts [schema-path] <log-file>')
    process.exit(1)
  }

  const validator = new LogValidator(schemaPath)
  
  validator.validateFile(logFile).then(() => {
    validator.printReport()
  }).catch(error => {
    console.error('驗證失敗:', error)
    process.exit(1)
  })
}

export default LogValidator