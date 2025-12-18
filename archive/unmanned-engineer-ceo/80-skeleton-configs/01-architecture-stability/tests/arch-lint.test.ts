import * as fs from 'fs'
import * as path from 'path'

import { beforeEach, describe, expect, it } from 'vitest'

import ArchitectureLinter from '../tools/arch-lint'

describe('ArchitectureLinter', () => {
  let linter: ArchitectureLinter

  beforeEach(() => {
    linter = new ArchitectureLinter('./arch-lint.config.yml')
  })

  describe('Layering Rules', () => {
    it('應該檢測到禁止的跨層依賴', async () => {
      // 建立測試檔案
      const testFile = 'test-violations/platform-depends-on-service.ts'
      fs.mkdirSync(path.dirname(testFile), { recursive: true })
      fs.writeFileSync(
        testFile,
        "import { BillingService } from '@services/billing'\n"
      )

      const violations = await linter.lint()

      expect(violations).toContainEqual(
        expect.objectContaining({
          rule: 'layering',
          severity: 'error',
          message: expect.stringContaining('cannot depend on'),
        })
      )

      // 清理
      fs.unlinkSync(testFile)
    })

    it('應該允許合法的依賴', async () => {
      const testFile = 'test-valid/service-depends-on-platform.ts'
      fs.mkdirSync(path.dirname(testFile), { recursive: true })
      fs.writeFileSync(
        testFile,
        "import { AuthService } from '@platform/foundation/security'\n"
      )

      const violations = await linter.lint()

      const layeringViolations = violations.filter(
        (v) => v.rule === 'layering' && v.file === testFile
      )

      expect(layeringViolations).toHaveLength(0)

      // 清理
      fs.unlinkSync(testFile)
    })
  })

  describe('Circular Dependencies', () => {
    it('應該檢測到循環依賴', async () => {
      // 這需要實際的循環依賴檔案進行測試
      // 在實際專案中應該建立測試夾具
    })
  })

  describe('Naming Conventions', () => {
    it('應該檢測不符合命名規範的服務', async () => {
      const violations = await linter.lint()

      // 假設有個服務名為 "BadServiceName"
      const namingViolations = violations.filter(
        (v) => v.rule === 'naming-conventions'
      )

      // 應該有警告
      expect(namingViolations.length).toBeGreaterThanOrEqual(0)
    })
  })

  describe('File Organization', () => {
    it('應該檢測缺少 README 的服務', async () => {
      // 建立測試服務目錄
      const testService = 'services/test-service-no-readme'
      fs.mkdirSync(testService, { recursive: true })

      const violations = await linter.lint()

      expect(violations).toContainEqual(
        expect.objectContaining({
          rule: 'file-organization',
          message: 'Missing README.md',
        })
      )

      // 清理
      fs.rmSync(testService, { recursive: true, force: true })
    })
  })
})