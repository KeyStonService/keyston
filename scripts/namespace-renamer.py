#!/usr/bin/env python3
"""
AXM 到 MachineNativeOps 命名空間重構工具
符合 root.specs.naming.yaml 規範
"""

import os
import re
import sys
from pathlib import Path

def rename_axm_to_mno(content):
    """將 AXM 相關命名遷移到 MachineNativeOps 標準"""
    
    # 命名映射表
    replacements = {
        # 架構雜湊保持不變
        'e7f8a9b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9': 
        'e7f8a9b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9',
        
        # AXM → MNO (MachineNativeOps 縮寫)
        'AXM': 'MNO',
        'axm': 'mno',
        
        # AXIOM → MachineNativeOps (完整替換)
        'AXIOM': 'MachineNativeOps',
        'Axiom': 'MachineNativeOps',
        'axiom': 'machinenativenops',
        
        # 專有名詞保持不變（在引號內）
        '"AXIOM eXtended Multi-agent"': '"MachineNativeOps eXtended Multi-agent"',
        '"AXIOM"': '"MachineNativeOps"',
        
        # 系統命名
        'axiom-system': 'machinenativenops-system',
        'axiom.io': 'machinenativeops.io',
        'api.axiom.io': 'api.machinenativeops.io',
        
        # 類別名稱（Python）
        'AxiomAutoMonitor': 'MachineNativeOpsAutoMonitor',
        'AxiomConfigValidator': 'MachineNativeOpsConfigValidator',
        'AxiomPerformanceBenchmarker': 'MachineNativeOpsPerformanceBenchmarker',
        'AxiomQuantumOptimizer': 'MachineNativeOpsQuantumOptimizer',
        'AxiomSecurityScanner': 'MachineNativeOpsSecurityScanner',
        
        # 追蹤ID格式
        'axm-': 'mno-',
        
        # 配置鍵
        'axiom_system': 'machinenativenops_system',
        'axiom_monitor': 'machinenativenops_monitor',
        'axiom_validator': 'machinenativenops_validator',
    }
    
    # 按長度排序，先替換較長的字符串
    sorted_replacements = sorted(replacements.items(), key=lambda x: len(x[0]), reverse=True)
    
    new_content = content
    for old, new in sorted_replacements:
        new_content = new_content.replace(old, new)
    
    return new_content

def process_file(file_path):
    """處理單個文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        new_content = rename_axm_to_mno(content)
        
        if original_content != new_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ Updated: {file_path}")
            return True
        else:
            print(f"⏭️  No changes needed: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    """主函數"""
    if len(sys.argv) < 2:
        print("Usage: python namespace-renamer.py <directory>")
        sys.exit(1)
    
    target_dir = Path(sys.argv[1])
    if not target_dir.exists():
        print(f"Directory not found: {target_dir}")
        sys.exit(1)
    
    print(f"🔄 Processing AXM → MachineNativeOps namespace migration in: {target_dir}")
    print("=" * 60)
    
    # 要處理的文件類型
    file_patterns = ['*.py', '*.sh', '*.md', '*.yaml', '*.yml']
    
    updated_count = 0
    total_count = 0
    
    for pattern in file_patterns:
        for file_path in target_dir.rglob(pattern):
            total_count += 1
            if process_file(file_path):
                updated_count += 1
    
    print("=" * 60)
    print(f"✅ Migration Complete!")
    print(f"📊 Total files processed: {total_count}")
    print(f"📝 Files updated: {updated_count}")
    print(f"🎯 Migration: AXM/AXIOM → MachineNativeOps")

if __name__ == "__main__":
    main()