#!/usr/bin/env ts-node
/**
 * SynergyMesh 代碼生成器 (Code Generator)
 * 作者: SynergyMesh Team
 * 版本: 2.0.0
 *
 * 此腳本負責根據模板生成代碼:
 * - 連接器模板
 * - 服務模板
 * - 整合模板
 */

import * as fs from 'fs';
import * as path from 'path';

// 顏色定義
const colors = {
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
  reset: '\x1b[0m',
};

/**
 * 帶顏色輸出
 */
function colorLog(color: keyof typeof colors, message: string): void {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

/**
 * 日誌輸出
 */
const logger = {
  info: (msg: string): void => colorLog('blue', `[INFO] ${msg}`),
  success: (msg: string): void => colorLog('green', `[SUCCESS] ${msg}`),
  warn: (msg: string): void => colorLog('yellow', `[WARN] ${msg}`),
  error: (msg: string): void => colorLog('red', `[ERROR] ${msg}`),
};

/**
 * 模板變數介面
 */
interface TemplateVariables {
  name: string;
  className: string;
  fileName: string;
  timestamp: string;
  [key: string]: string | number | boolean;
}

/**
 * 模板配置介面
 */
interface TemplateConfig {
  path: string;
  description: string;
  variables: string[];
  outputs: string[];
}

/**
 * 代碼生成器類別
 */
class CodeGenerator {
  private projectRoot: string;
  private templatesPath: string;
  private outputPath: string;

  constructor() {
    this.projectRoot = this.findProjectRoot();
    this.templatesPath = path.join(this.projectRoot, 'config/dev', 'templates');
    this.outputPath = path.join(this.projectRoot, 'generated');
  }

  /**
   * 尋找專案根目錄
   */
  private findProjectRoot(): string {
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
   * 載入模板
   */
  private loadTemplate(templateName: string): string | null {
    const templatePath = path.join(this.templatesPath, `${templateName}-template`);

    if (!fs.existsSync(templatePath)) {
      logger.warn(`模板目錄不存在: ${templatePath}`);
      return null;
    }

    // 尋找模板檔案
    const templateFiles = ['template.ts', 'template.js', 'template.py', 'index.ts', 'index.js'];
    for (const file of templateFiles) {
      const filePath = path.join(templatePath, file);
      if (fs.existsSync(filePath)) {
        return fs.readFileSync(filePath, 'utf8');
      }
    }

    logger.warn(`模板 ${templateName} 中沒有找到模板檔案`);
    return null;
  }

  /**
   * 替換模板變數
   */
  private replaceVariables(template: string, variables: TemplateVariables): string {
    let result = template;

    for (const [key, value] of Object.entries(variables)) {
      // 支援多種變數格式
      const patterns = [
        new RegExp(`\\{\\{\\s*${key}\\s*\\}\\}`, 'g'), // {{ variable }}
        new RegExp(`\\$\\{${key}\\}`, 'g'), // ${variable}
        new RegExp(`__${key.toUpperCase()}__`, 'g'), // __VARIABLE__
      ];

      for (const pattern of patterns) {
        result = result.replace(pattern, String(value));
      }
    }

    return result;
  }

  /**
   * 確保目錄存在
   */
  private ensureDirectory(dirPath: string): void {
    if (!fs.existsSync(dirPath)) {
      fs.mkdirSync(dirPath, { recursive: true });
    }
  }

  /**
   * 生成連接器
   */
  generateConnector(name: string, options: Partial<TemplateVariables> = {}): boolean {
    logger.info(`🔌 生成連接器: ${name}`);

    const variables: TemplateVariables = {
      name,
      type: options.type as string || 'rest',
      endpoint: options.endpoint as string || 'http://localhost:3000',
      className: this.toPascalCase(name),
      fileName: this.toKebabCase(name),
      timestamp: new Date().toISOString(),
    };

    const outputDir = path.join(this.outputPath, 'connectors', variables.fileName);
    this.ensureDirectory(outputDir);

    // 生成主文件
    const connectorContent = this.generateConnectorContent(variables);
    const filePath = path.join(outputDir, `${variables.fileName}.ts`);
    fs.writeFileSync(filePath, connectorContent, 'utf8');
    logger.success(`  已生成: ${filePath}`);

    // 生成測試文件
    const testContent = this.generateConnectorTestContent(variables);
    const testPath = path.join(outputDir, `${variables.fileName}.test.ts`);
    fs.writeFileSync(testPath, testContent, 'utf8');
    logger.success(`  已生成: ${testPath}`);

    // 生成配置文件
    const configContent = this.generateConnectorConfigContent(variables);
    const configPath = path.join(outputDir, 'config.json');
    fs.writeFileSync(configPath, configContent, 'utf8');
    logger.success(`  已生成: ${configPath}`);

    logger.success(`✅ 連接器 ${name} 生成完成`);
    return true;
  }

  /**
   * 生成連接器內容
   */
  private generateConnectorContent(variables: TemplateVariables): string {
    return `/**
 * ${variables.className} 連接器
 * 生成時間: ${variables.timestamp}
 * 類型: ${variables.type}
 */

export interface ${variables.className}Config {
  endpoint: string;
  timeout?: number;
  retries?: number;
}

export class ${variables.className}Connector {
  private config: ${variables.className}Config;

  constructor(config: ${variables.className}Config) {
    this.config = {
      timeout: 5000,
      retries: 3,
      ...config,
    };
  }

  /**
   * 連接到端點
   */
  async connect(): Promise<boolean> {
    console.log(\`連接到 \${this.config.endpoint}...\`);
    // 實作連接邏輯
    return true;
  }

  /**
   * 斷開連接
   */
  async disconnect(): Promise<void> {
    console.log('斷開連接...');
    // 實作斷開邏輯
  }

  /**
   * 發送請求
   */
  async send<T>(data: unknown): Promise<T> {
    // 實作發送邏輯
    throw new Error('Method not implemented');
  }

  /**
   * 健康檢查
   */
  async healthCheck(): Promise<boolean> {
    try {
      await this.connect();
      return true;
    } catch {
      return false;
    }
  }
}

export default ${variables.className}Connector;
`;
  }

  /**
   * 生成連接器測試內容
   */
  private generateConnectorTestContent(variables: TemplateVariables): string {
    return `/**
 * ${variables.className} 連接器測試
 * 生成時間: ${variables.timestamp}
 */

import { ${variables.className}Connector, ${variables.className}Config } from './${variables.fileName}';

describe('${variables.className}Connector', () => {
  let connector: ${variables.className}Connector;
  const config: ${variables.className}Config = {
    endpoint: '${variables.endpoint}',
    timeout: 5000,
  };

  beforeEach(() => {
    connector = new ${variables.className}Connector(config);
  });

  describe('connect', () => {
    it('should connect successfully', async () => {
      const result = await connector.connect();
      expect(result).toBe(true);
    });
  });

  describe('healthCheck', () => {
    it('should return true when healthy', async () => {
      const result = await connector.healthCheck();
      expect(result).toBe(true);
    });
  });
});
`;
  }

  /**
   * 生成連接器配置內容
   */
  private generateConnectorConfigContent(variables: TemplateVariables): string {
    return JSON.stringify(
      {
        name: variables.name,
        type: variables.type,
        endpoint: variables.endpoint,
        timeout: 5000,
        retries: 3,
        generated: variables.timestamp,
      },
      null,
      2
    );
  }

  /**
   * 生成服務
   */
  generateService(name: string, options: Partial<TemplateVariables> = {}): boolean {
    logger.info(`🔧 生成服務: ${name}`);

    const variables: TemplateVariables = {
      name,
      port: options.port as number || 3000,
      className: this.toPascalCase(name),
      fileName: this.toKebabCase(name),
      timestamp: new Date().toISOString(),
    };

    const outputDir = path.join(this.outputPath, 'services', variables.fileName);
    this.ensureDirectory(outputDir);
    this.ensureDirectory(path.join(outputDir, 'src'));

    // 生成主文件
    const serviceContent = this.generateServiceContent(variables);
    const filePath = path.join(outputDir, 'src', `${variables.fileName}.ts`);
    fs.writeFileSync(filePath, serviceContent, 'utf8');
    logger.success(`  已生成: ${filePath}`);

    logger.success(`✅ 服務 ${name} 生成完成`);
    return true;
  }

  /**
   * 生成服務內容
   */
  private generateServiceContent(variables: TemplateVariables): string {
    return `/**
 * ${variables.className} 服務
 * 生成時間: ${variables.timestamp}
 * 預設端口: ${variables.port}
 */

export interface ${variables.className}Options {
  port?: number;
}

export class ${variables.className}Service {
  private port: number;

  constructor(options: ${variables.className}Options = {}) {
    this.port = options.port || ${variables.port};
  }

  /**
   * 啟動服務
   */
  async start(): Promise<void> {
    console.log(\`${variables.className} 服務啟動於 port \${this.port}\`);
    // 實作啟動邏輯
  }

  /**
   * 停止服務
   */
  async stop(): Promise<void> {
    console.log('服務停止中...');
    // 實作停止邏輯
  }
}

export default ${variables.className}Service;
`;
  }

  /**
   * 列出可用模板
   */
  listTemplates(): void {
    logger.info('📋 可用模板:');

    const templates = ['connector', 'service', 'integration'];
    for (const template of templates) {
      const templatePath = path.join(this.templatesPath, `${template}-template`);
      const exists = fs.existsSync(templatePath);
      const icon = exists ? '✅' : '📁';
      console.log(`  ${icon} ${template}-template`);
    }
  }

  /**
   * 轉換為 PascalCase
   */
  private toPascalCase(str: string): string {
    return str
      .split(/[-_\s]+/)
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join('');
  }

  /**
   * 轉換為 kebab-case
   */
  private toKebabCase(str: string): string {
    return str
      .replace(/([a-z])([A-Z])/g, '$1-$2')
      .replace(/[\s_]+/g, '-')
      .toLowerCase();
  }
}

/**
 * 命令行介面
 */
function main(): void {
  const args = process.argv.slice(2);
  const command = args[0] || 'help';

  const generator = new CodeGenerator();

  colorLog(
    'cyan',
    `
+---------------------------------------+
|   SynergyMesh 代碼生成器 v2.0         |
+---------------------------------------+
  `
  );

  switch (command) {
    case 'connector':
      const connectorName = args[1];
      if (!connectorName) {
        logger.error('請提供連接器名稱');
        process.exit(1);
      }
      generator.generateConnector(connectorName, {
        type: args[2] || 'rest',
        endpoint: args[3] || 'http://localhost:3000',
      });
      break;

    case 'service':
      const serviceName = args[1];
      if (!serviceName) {
        logger.error('請提供服務名稱');
        process.exit(1);
      }
      generator.generateService(serviceName, {
        port: parseInt(args[2]) || 3000,
      });
      break;

    case 'list':
      generator.listTemplates();
      break;

    case 'help':
    default:
      console.log(`
用法: ts-node code-generator.ts [命令] [選項]

命令:
  connector <名稱> [類型] [端點]  生成連接器
  service <名稱> [端口]          生成服務
  list                           列出可用模板
  help                           顯示此幫助訊息

範例:
  ts-node code-generator.ts connector my-api rest http://api.example.com
  ts-node code-generator.ts service user-service 3001
      `);
      break;
  }
}

main();
