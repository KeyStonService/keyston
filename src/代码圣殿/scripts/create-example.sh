#!/usr/bin/env bash

# ============================================================================
# 示例创建脚本 / Example Creation Script
# ============================================================================
# 使用模板快速创建新的示例代码
#
# 用法:
#   ./scripts/create-example.sh --name <name> --category <category> --language <lang>
#
# 示例:
#   ./scripts/create-example.sh \
#     --name custom-integration \
#     --category integration \
#     --language typescript \
#     --description "自定义集成示例"
# ============================================================================

set -euo pipefail

# 默认值
NAME=""
CATEGORY=""
LANGUAGE="typescript"
DESCRIPTION=""
AUTHOR="${USER:-SynergyMesh Team}"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 显示帮助信息
show_help() {
    cat << EOF
示例创建脚本 / Example Creation Script

用法:
    $0 [选项]

选项:
    -n, --name NAME           示例名称（必需）
    -c, --category CATEGORY   示例类别（必需）
                              可选值: basic, integration, configuration, 
                                     best-practices, troubleshooting, advanced
    -l, --language LANGUAGE   编程语言（默认: typescript）
                              可选值: typescript, python, java, go, yaml
    -d, --description DESC    示例描述
    -a, --author AUTHOR       作者名称（默认: 当前用户）
    -h, --help               显示此帮助信息

示例:
    # 创建TypeScript集成示例
    $0 -n custom-api -c integration -l typescript -d "自定义API集成"

    # 创建Python基础示例
    $0 -n hello-world -c basic -l python

    # 创建YAML配置示例
    $0 -n production-config -c configuration -l yaml
EOF
}

# 解析命令行参数
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -n|--name)
                NAME="$2"
                shift 2
                ;;
            -c|--category)
                CATEGORY="$2"
                shift 2
                ;;
            -l|--language)
                LANGUAGE="$2"
                shift 2
                ;;
            -d|--description)
                DESCRIPTION="$2"
                shift 2
                ;;
            -a|--author)
                AUTHOR="$2"
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# 验证参数
validate_args() {
    if [[ -z "$NAME" ]]; then
        log_error "示例名称不能为空"
        show_help
        exit 1
    fi

    if [[ -z "$CATEGORY" ]]; then
        log_error "示例类别不能为空"
        show_help
        exit 1
    fi

    # 验证类别
    case $CATEGORY in
        basic|integration|configuration|best-practices|troubleshooting|advanced)
            ;;
        *)
            log_error "无效的类别: $CATEGORY"
            log_info "有效类别: basic, integration, configuration, best-practices, troubleshooting, advanced"
            exit 1
            ;;
    esac

    # 验证语言
    case $LANGUAGE in
        typescript|python|java|go|yaml)
            ;;
        *)
            log_error "无效的语言: $LANGUAGE"
            log_info "有效语言: typescript, python, java, go, yaml"
            exit 1
            ;;
    esac
}

# 映射类别到目录
get_category_dir() {
    case $CATEGORY in
        basic) echo "基础示例" ;;
        integration) echo "集成示例" ;;
        configuration) echo "配置示例" ;;
        best-practices) echo "最佳实践" ;;
        troubleshooting) echo "故障排除" ;;
        advanced) echo "高级用法" ;;
    esac
}

# 获取文件扩展名
get_file_extension() {
    case $LANGUAGE in
        typescript) echo "ts" ;;
        python) echo "py" ;;
        java) echo "java" ;;
        go) echo "go" ;;
        yaml) echo "yaml" ;;
    esac
}

# 创建示例文件
create_example_file() {
    local category_dir=$(get_category_dir)
    local file_ext=$(get_file_extension)
    local example_dir="src/代码圣殿/${category_dir}/examples"
    local file_path="${example_dir}/${NAME}.${file_ext}"

    log_info "创建示例文件: ${file_path}"

    # 创建目录（如果不存在）
    mkdir -p "$example_dir"

    # 创建示例文件
    case $LANGUAGE in
        typescript)
            cat > "$file_path" << 'EOF'
/**
 * ${NAME}
 * ${DESCRIPTION}
 * 
 * @author ${AUTHOR}
 * @created $(date +%Y-%m-%d)
 */

import { IntelligentAutomation } from '@machinenativeops/automation-sdk';

async function main() {
  const automation = new IntelligentAutomation({
    apiKey: process.env.API_KEY,
    baseUrl: process.env.BASE_URL
  });

  // TODO: 实现示例逻辑
  console.log('示例: ${NAME}');
}

if (require.main === module) {
  main().catch(console.error);
}

export { main };
EOF
            ;;
        python)
            cat > "$file_path" << 'EOF'
"""
${NAME}
${DESCRIPTION}

Author: ${AUTHOR}
Created: $(date +%Y-%m-%d)
"""

import os
from typing import Any


def main() -> None:
    """主函数"""
    # TODO: 实现示例逻辑
    print(f"示例: ${NAME}")


if __name__ == "__main__":
    main()
EOF
            ;;
        yaml)
            cat > "$file_path" << 'EOF'
# ${NAME}
# ${DESCRIPTION}
#
# Author: ${AUTHOR}
# Created: $(date +%Y-%m-%d)

apiVersion: automation.io/v1
kind: Configuration
metadata:
  name: ${NAME}
  description: ${DESCRIPTION}
spec:
  # TODO: 添加配置内容
EOF
            ;;
    esac

    # 替换变量
    sed -i.bak "s/\${NAME}/${NAME}/g" "$file_path"
    sed -i.bak "s/\${DESCRIPTION}/${DESCRIPTION:-示例代码}/g" "$file_path"
    sed -i.bak "s/\${AUTHOR}/${AUTHOR}/g" "$file_path"
    rm "${file_path}.bak"

    log_success "已创建示例文件: ${file_path}"
}

# 创建README文件
create_readme() {
    local category_dir=$(get_category_dir)
    local example_dir="src/代码圣殿/${category_dir}/examples"
    local readme_path="${example_dir}/${NAME}.md"

    log_info "创建README文件: ${readme_path}"

    cat > "$readme_path" << EOF
# ${NAME}

> **类别**: ${category_dir}  
> **语言**: ${LANGUAGE}  
> **作者**: ${AUTHOR}  
> **创建日期**: $(date +%Y-%m-%d)

---

## 📋 概述

${DESCRIPTION:-待添加描述}

---

## 🚀 快速开始

### 前置条件

- 已安装相关运行环境
- 已配置必要的环境变量

### 运行示例

\`\`\`bash
# 运行示例
npm run example:${NAME}
# 或
node examples/${NAME}.js
\`\`\`

---

## 📝 代码说明

### 核心逻辑

TODO: 添加代码说明

### 关键函数

TODO: 添加关键函数说明

---

## 🔗 相关资源

- [完整文档](../../README.md)
- [API参考](../../../../docs/API_REFERENCE.md)

---

**最后更新**: $(date +%Y-%m-%d)
EOF

    log_success "已创建README文件: ${readme_path}"
}

# 主函数
main() {
    log_info "开始创建示例..."
    
    parse_args "$@"
    validate_args
    
    create_example_file
    create_readme
    
    log_success "示例创建完成！"
    log_info "文件位置: src/代码圣殿/$(get_category_dir)/examples/${NAME}.*"
    log_info ""
    log_info "下一步:"
    log_info "  1. 编辑示例代码"
    log_info "  2. 添加测试"
    log_info "  3. 运行验证: ./scripts/validate-examples.sh --example ${NAME}"
    log_info "  4. 提交PR"
}

# 运行主函数
main "$@"
