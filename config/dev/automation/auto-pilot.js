#!/usr/bin/env node
/**
 * SynergyMesh 自動駕駛邏輯 (Auto-Pilot)
 * 作者: SynergyMesh Team
 * 版本: 2.0.0
 *
 * 此腳本負責自動化任務的執行邏輯:
 * - 監控文件變更
 * - 觸發自動化任務
 * - 管理工作流程
 */

const fs = require('fs');
const path = require('path');
const { execSync, spawn } = require('child_process');

// 顏色輸出
const colors = {
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  purple: '\x1b[35m',
  cyan: '\x1b[36m',
  reset: '\x1b[0m',
};

/**
 * 帶顏色輸出
 */
function colorLog(color, message) {
  console.log(`${colors[color] || ''}${message}${colors.reset}`);
}

/**
 * 日誌輸出函數
 */
const logger = {
  info: (msg) => colorLog('blue', `[INFO] ${msg}`),
  success: (msg) => colorLog('green', `[SUCCESS] ${msg}`),
  warn: (msg) => colorLog('yellow', `[WARN] ${msg}`),
  error: (msg) => colorLog('red', `[ERROR] ${msg}`),
};

/**
 * 自動駕駛類別
 */
class AutoPilot {
  constructor() {
    this.projectRoot = this.findProjectRoot();
    this.config = {};
    this.watchers = [];
    this.taskQueue = [];
    this.isRunning = false;
  }

  /**
   * 尋找專案根目錄
   */
  findProjectRoot() {
    let current = __dirname;
    while (current !== path.dirname(current)) {
      if (
        fs.existsSync(path.join(current, 'drone-config.yml')) ||
        fs.existsSync(path.join(current, 'package.json'))
      ) {
        return current;
      }
      current = path.dirname(current);
    }
    return process.cwd();
  }

  /**
   * 載入配置
   */
  loadConfig() {
    const configPath = path.join(this.projectRoot, 'auto-scaffold.json');

    if (!fs.existsSync(configPath)) {
      logger.warn(`配置檔案不存在: ${configPath}`);
      this.config = this.getDefaultConfig();
      return false;
    }

    try {
      const content = fs.readFileSync(configPath, 'utf8');
      this.config = JSON.parse(content);
      logger.success(`配置已載入: ${configPath}`);
      return true;
    } catch (error) {
      logger.error(`載入配置失敗: ${error.message}`);
      this.config = this.getDefaultConfig();
      return false;
    }
  }

  /**
   * 取得預設配置
   */
  getDefaultConfig() {
    return {
      automation: {
        triggers: {
          onFileCreate: {
            patterns: ['*.ts', '*.py', '*.js'],
            actions: ['lint', 'format'],
          },
        },
      },
      codeGeneration: {
        enabled: true,
        languages: ['typescript', 'python', 'javascript'],
      },
    };
  }

  /**
   * 初始化監控器
   */
  initWatchers() {
    logger.info('🔍 初始化文件監控...');

    const triggers = this.config?.automation?.triggers || {};

    if (triggers.onFileCreate) {
      const patterns = triggers.onFileCreate.patterns || [];
      logger.info(`  監控模式: ${patterns.join(', ')}`);
    }

    logger.success('監控器初始化完成');
  }

  /**
   * 執行任務
   */
  async executeTask(taskName, options = {}) {
    logger.info(`🚀 執行任務: ${taskName}`);

    const tasks = {
      lint: () => this.runLint(),
      format: () => this.runFormat(),
      test: () => this.runTests(),
      build: () => this.runBuild(),
      'system-diagnosis': () => this.runDiagnosis(),
    };

    const task = tasks[taskName];
    if (!task) {
      logger.warn(`未知任務: ${taskName}`);
      return false;
    }

    try {
      await task();
      logger.success(`任務完成: ${taskName}`);
      return true;
    } catch (error) {
      logger.error(`任務失敗: ${taskName} - ${error.message}`);
      return false;
    }
  }

  /**
   * 執行 Lint
   */
  runLint() {
    logger.info('  執行程式碼檢查...');
    try {
      execSync('npm run lint --if-present', {
        cwd: this.projectRoot,
        stdio: 'pipe',
      });
      return true;
    } catch {
      logger.warn('  Lint 檢查有警告或錯誤');
      return false;
    }
  }

  /**
   * 執行格式化
   */
  runFormat() {
    logger.info('  執行程式碼格式化...');
    // 格式化通常是選用的
    return true;
  }

  /**
   * 執行測試
   */
  runTests() {
    logger.info('  執行測試...');
    try {
      execSync('npm test --if-present', {
        cwd: this.projectRoot,
        stdio: 'pipe',
      });
      return true;
    } catch {
      logger.warn('  部分測試失敗');
      return false;
    }
  }

  /**
   * 執行建置
   */
  runBuild() {
    logger.info('  執行建置...');
    try {
      execSync('npm run build --if-present', {
        cwd: this.projectRoot,
        stdio: 'pipe',
      });
      return true;
    } catch (error) {
      logger.error(`  建置失敗: ${error.message}`);
      return false;
    }
  }

  /**
   * 執行系統診斷
   */
  runDiagnosis() {
    logger.info('📊 系統診斷');

    const checks = [];

    // 檢查 Node.js
    try {
      const nodeVersion = execSync('node --version', { encoding: 'utf8' }).trim();
      checks.push({ name: 'Node.js', status: 'ok', version: nodeVersion });
    } catch {
      checks.push({ name: 'Node.js', status: 'error', version: null });
    }

    // 檢查 npm
    try {
      const npmVersion = execSync('npm --version', { encoding: 'utf8' }).trim();
      checks.push({ name: 'npm', status: 'ok', version: npmVersion });
    } catch {
      checks.push({ name: 'npm', status: 'error', version: null });
    }

    // 檢查 Docker
    try {
      const dockerVersion = execSync('docker --version', { encoding: 'utf8' }).trim();
      checks.push({ name: 'Docker', status: 'ok', version: dockerVersion });
    } catch {
      checks.push({ name: 'Docker', status: 'warn', version: '未安裝' });
    }

    // 輸出結果
    console.log('');
    for (const check of checks) {
      const icon = check.status === 'ok' ? '✅' : check.status === 'warn' ? '⚠️' : '❌';
      console.log(`  ${icon} ${check.name}: ${check.version || '未知'}`);
    }
    console.log('');

    return true;
  }

  /**
   * 處理任務佇列
   */
  async processQueue() {
    if (this.isRunning || this.taskQueue.length === 0) {
      return;
    }

    this.isRunning = true;

    while (this.taskQueue.length > 0) {
      const task = this.taskQueue.shift();
      await this.executeTask(task.name, task.options);
    }

    this.isRunning = false;
  }

  /**
   * 新增任務到佇列
   */
  queueTask(taskName, options = {}) {
    this.taskQueue.push({ name: taskName, options });
    this.processQueue();
  }

  /**
   * 啟動自動駕駛
   */
  start() {
    colorLog(
      'cyan',
      `
+---------------------------------------+
|   SynergyMesh 自動駕駛系統 v2.0       |
|         Auto-Pilot 啟動中             |
+---------------------------------------+
    `
    );

    // 載入配置
    this.loadConfig();

    // 初始化監控
    this.initWatchers();

    // 執行初始診斷
    this.runDiagnosis();

    logger.success('🚀 自動駕駛系統已啟動');
    logger.info('按 Ctrl+C 停止');
  }

  /**
   * 停止自動駕駛
   */
  stop() {
    logger.info('停止自動駕駛系統...');

    // 清理監控器
    for (const watcher of this.watchers) {
      watcher.close();
    }
    this.watchers = [];

    logger.success('自動駕駛系統已停止');
  }
}

/**
 * 命令行介面
 */
function main() {
  const args = process.argv.slice(2);
  const command = args[0] || 'start';

  const pilot = new AutoPilot();

  switch (command) {
    case 'start':
      pilot.start();
      break;

    case 'diagnose':
    case 'diagnosis':
      pilot.loadConfig();
      pilot.runDiagnosis();
      break;

    case 'task':
      const taskName = args[1];
      if (!taskName) {
        logger.error('請指定任務名稱');
        process.exit(1);
      }
      pilot.loadConfig();
      pilot.executeTask(taskName);
      break;

    case 'help':
    default:
      console.log(`
SynergyMesh 自動駕駛系統

用法: node auto-pilot.js [命令]

命令:
  start       啟動自動駕駛 (預設)
  diagnose    執行系統診斷
  task <名稱>  執行指定任務 (lint, format, test, build)
  help        顯示此幫助訊息
      `);
      break;
  }
}

// 處理程序退出
process.on('SIGINT', () => {
  console.log('\n收到中斷訊號，正在停止...');
  process.exit(0);
});

// 執行主程式
main();
