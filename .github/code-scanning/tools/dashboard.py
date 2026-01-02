#!/usr/bin/env python3
"""
高階代碼掃描儀表板
Advanced Code Scanning Dashboard

功能：
1. Web 界面顯示掃描結果
2. 根因分析可視化
3. 修復狀態追蹤
4. 實時報告生成
"""

from flask import Flask, render_template, jsonify, send_file
from werkzeug.utils import secure_filename
from pathlib import Path
import json
import os
import ipaddress
from datetime import datetime
from typing import Dict

app = Flask(__name__)

# 配置
REPORTS_DIR = Path(".github/code-scanning/reports")
TEMPLATE_DIR = Path(".github/code-scanning/templates")

# 本機地址 / Localhost addresses for security checks
LOCALHOST_ADDRESSES = ('127.0.0.1', 'localhost', '::1')
# 預設配置 / Default configuration
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 5000
DEFAULT_DEBUG = False
# 有效端口範圍 / Valid port range
MIN_PORT = 1
MAX_PORT = 65535
# 確保模板目錄存在
TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__, template_folder=str(TEMPLATE_DIR))

class DashboardData:
    """儀表板數據管理"""
    
    @staticmethod
    def get_latest_scan_results() -> Dict:
        """獲取最新掃描結果"""
        scan_files = sorted(
            REPORTS_DIR.glob("scan-results-*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        if scan_files:
            with open(scan_files[0]) as f:
                return json.load(f)
        
        return {
            "metadata": {"scan_time": datetime.utcnow().isoformat()},
            "summary": {"total_findings": 0, "critical": 0, "high": 0, "medium": 0, "low": 0}
        }
    
    @staticmethod
    def get_root_cause_analysis() -> Dict:
        """獲取根因分析結果"""
        analysis_file = REPORTS_DIR / "root-cause-analysis.json"
        
        if analysis_file.exists():
            with open(analysis_file) as f:
                return json.load(f)
        
        return {"risk_assessment": {"total_risk_score": 0, "risk_level": "unknown"}}
    
    @staticmethod
    def get_fix_report() -> Dict:
        """獲取修復報告"""
        fix_files = sorted(
            REPORTS_DIR.glob("fix-report-*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        if fix_files:
            with open(fix_files[0]) as f:
                return json.load(f)
        
        return {"summary": {"total_issues": 0, "fixed": 0, "failed": 0}}

# API 路由
@app.route('/')
def index():
    """主頁"""
    return render_template('dashboard.html')

@app.route('/api/scan-summary')
def scan_summary():
    """掃描摘要 API"""
    data = DashboardData.get_latest_scan_results()
    summary = data.get('summary', {})
    
    return jsonify({
        'total_findings': summary.get('total_findings', 0),
        'critical': summary.get('critical', 0),
        'high': summary.get('high', 0),
        'medium': summary.get('medium', 0),
        'low': summary.get('low', 0),
        'scan_time': data.get('metadata', {}).get('scan_time', '')
    })

@app.route('/api/root-causes')
def root_causes():
    """根因分析 API"""
    data = DashboardData.get_root_cause_analysis()
    
    return jsonify({
        'root_causes': data.get('root_causes', []),
        'risk_assessment': data.get('risk_assessment', {}),
        'affected_components': data.get('affected_components', [])
    })

@app.route('/api/fix-status')
def fix_status():
    """修復狀態 API"""
    data = DashboardData.get_fix_report()
    
    return jsonify({
        'fixed': data.get('fixed', []),
        'failed': data.get('failed', []),
        'manual_review_required': data.get('manual_review_required', []),
        'summary': data.get('summary', {})
    })

@app.route('/api/findings')
def findings():
    """詳細發現 API"""
    data = DashboardData.get_latest_scan_results()
    
    all_findings = []
    for category in ['security', 'dependencies', 'code_quality', 'performance', 'compliance']:
        findings = data.get(category, [])
        for finding in findings:
            finding['category'] = category
            all_findings.append(finding)
    
    return jsonify(all_findings)

@app.route('/api/reports/<filename>')
def download_report(filename):
    """下載報告 / Download report"""
    # Sanitize the filename to prevent path traversal attacks
    # This removes any directory components and dangerous characters
    safe_filename = secure_filename(filename)
    
    # Additional validation: ensure the sanitized filename is not empty
    if not safe_filename:
        return jsonify({'error': 'Invalid filename'}), 400
    
    # Construct the safe path within REPORTS_DIR
    report_path = REPORTS_DIR / safe_filename
    
    # Ensure the resolved path is still within REPORTS_DIR (defense in depth)
    try:
        base_path = REPORTS_DIR.resolve()
        resolved_path = report_path.resolve()
        
        # Validate path is within base directory - raises ValueError if outside
        _ = resolved_path.relative_to(base_path)
        
        # Ensure it's not the base directory itself and is a file
        if resolved_path == base_path or not resolved_path.is_file():
            return jsonify({'error': 'Report not found'}), 404
            
    except (OSError, ValueError):
        # Invalid path or path outside base directory
        return jsonify({'error': 'Invalid path'}), 400
    
    # Return the safe file
    return send_file(resolved_path, as_attachment=True)

@app.route('/dashboard')
def dashboard():
    """儀表板頁面"""
    return render_template('dashboard.html')

def main() -> None:
    """
    主函數
    
    啟動 Web 儀表板服務器。
    
    預設監聽 127.0.0.1:5000（僅本機訪問）以確保安全性。
    僅在受信任的開發環境中使用 DASHBOARD_HOST 允許外部訪問。
    
    環境變數：
    - DASHBOARD_HOST: 監聽地址（預設：127.0.0.1）
      支援任何有效的 IP 地址或主機名，但建議僅在開發環境使用非 localhost 地址
    - DASHBOARD_PORT: 監聽端口（預設：5000）
    - DASHBOARD_DEBUG: 啟用 Flask 除錯模式（預設：false）
      警告：除錯模式不應在生產環境使用
    
    如果模板文件不存在，會自動創建默認模板。
    """
    # 確保目錄存在
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
    
    # 創建模板（如果不存在）
    template_file = TEMPLATE_DIR / "dashboard.html"
    if not template_file.exists():
        create_default_template(template_file)
    
    # 從環境變數讀取配置，預設為安全的 localhost 綁定
    host = os.environ.get('DASHBOARD_HOST', DEFAULT_HOST)
    
    # 驗證 host 格式 - 接受任何有效的 IP 地址或主機名
    if host not in LOCALHOST_ADDRESSES:
        # 嘗試驗證是否為有效的 IP 地址
        try:
            # 支援 IPv4 和 IPv6
            ipaddress.ip_address(host)
            # Valid IP address - will show warning if not localhost
        except ValueError:
            # 不是有效的 IP 地址，可能是主機名
            # 允許常見的特殊值
            if host not in ('0.0.0.0', '::', 'localhost'):
                print(f"⚠️  警告：無效的 DASHBOARD_HOST 值，使用預設值 {DEFAULT_HOST}")
                host = DEFAULT_HOST
    
    # 驗證並解析端口
    try:
        port = int(os.environ.get('DASHBOARD_PORT', DEFAULT_PORT))
        if not (MIN_PORT <= port <= MAX_PORT):
            print(f"⚠️  警告：指定的端口超出有效範圍 ({MIN_PORT}-{MAX_PORT})，使用預設值 {DEFAULT_PORT}")
            port = DEFAULT_PORT
    except (ValueError, TypeError):
        print(f"⚠️  警告：環境變數 DASHBOARD_PORT 無效，使用預設值 {DEFAULT_PORT}")
        port = DEFAULT_PORT
    
    # 驗證並解析除錯模式
    debug_mode_str = os.environ.get('DASHBOARD_DEBUG', 'false').lower()
    debug_mode = debug_mode_str in ('true', '1', 'yes', 'on')
    
    # 安全警告（在啟動服務器之前顯示）
    if host not in LOCALHOST_ADDRESSES:
        print("⚠️  警告：服務器將監聽外部網絡接口")
        print("   建議僅在受信任的開發環境中使用此配置")
        print("   切勿在生產或共享環境中暴露儀表板")
    
    if debug_mode:
        print("⚠️  警告：Flask 除錯模式已啟用")
        print("   除錯模式會暴露敏感資訊，切勿在生產環境使用")
    
    # 啟動服務器
    print("🚀 啟動高階代碼掃描儀表板...")
    print(f"📊 訪問 http://{host}:{port} 查看儀表板")
    print(f"🔧 除錯模式: {'啟用' if debug_mode else '停用'}")
    app.run(debug=debug_mode, host=host, port=port)

def create_default_template(template_path: Path) -> None:
    """
    創建默認 HTML 模板
    
    Args:
        template_path: 模板文件的輸出路徑
    """
    html_content = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>高階代碼掃描儀表板</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; }
        .header h1 { font-size: 28px; margin-bottom: 10px; }
        .header p { opacity: 0.9; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .card h3 { margin-bottom: 15px; color: #333; }
        .metric { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #eee; }
        .metric:last-child { border-bottom: none; }
        .metric-value { font-size: 24px; font-weight: bold; }
        .critical { color: #dc2626; }
        .high { color: #ea580c; }
        .medium { color: #ca8a04; }
        .low { color: #16a34a; }
        .badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 500; }
        .badge.critical { background: #fee2e2; color: #dc2626; }
        .badge.high { background: #ffedd5; color: #ea580c; }
        .badge.medium { background: #fef9c3; color: #ca8a04; }
        .badge.low { background: #dcfce7; color: #16a34a; }
        .loading { text-align: center; padding: 40px; color: #666; }
        .section { margin-bottom: 30px; }
        .section-title { font-size: 20px; margin-bottom: 15px; color: #333; }
        .finding-item { padding: 15px; border-left: 4px solid #667eea; margin-bottom: 10px; background: #f9fafb; }
        .finding-type { font-weight: 500; color: #333; }
        .finding-location { color: #666; font-size: 14px; margin-top: 5px; }
        .progress-bar { height: 8px; background: #e5e7eb; border-radius: 4px; overflow: hidden; }
        .progress-fill { height: 100%; background: linear-gradient(90deg, #667eea, #764ba2); transition: width 0.3s; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 高階代碼掃描儀表板</h1>
            <p>Advanced Code Scanning Dashboard</p>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>📊 掃描摘要</h3>
                <div id="scan-summary" class="loading">載入中...</div>
            </div>
            
            <div class="card">
                <h3>🎯 根因分析</h3>
                <div id="root-cause" class="loading">載入中...</div>
            </div>
            
            <div class="card">
                <h3>🔧 修復狀態</h3>
                <div id="fix-status" class="loading">載入中...</div>
            </div>
        </div>
        
        <div class="card">
            <h3>📋 詳細發現</h3>
            <div id="findings" class="loading">載入中...</div>
        </div>
    </div>
    
    <script>
        async function loadData() {
            try {
                // 載入掃描摘要
                const summary = await fetch('/api/scan-summary').then(r => r.json());
                document.getElementById('scan-summary').innerHTML = `
                    <div class="metric">
                        <span>總計</span>
                        <span class="metric-value">${summary.total_findings}</span>
                    </div>
                    <div class="metric">
                        <span>🔴 關鍵</span>
                        <span class="metric-value critical">${summary.critical}</span>
                    </div>
                    <div class="metric">
                        <span>🟠 高</span>
                        <span class="metric-value high">${summary.high}</span>
                    </div>
                    <div class="metric">
                        <span>🟡 中</span>
                        <span class="metric-value medium">${summary.medium}</span>
                    </div>
                    <div class="metric">
                        <span>🟢 低</span>
                        <span class="metric-value low">${summary.low}</span>
                    </div>
                `;
                
                // 載入根因分析
                const rootCause = await fetch('/api/root-causes').then(r => r.json());
                document.getElementById('root-cause').innerHTML = `
                    <div class="metric">
                        <span>風險評分</span>
                        <span class="metric-value">${rootCause.risk_assessment.total_risk_score}</span>
                    </div>
                    <div class="metric">
                        <span>風險等級</span>
                        <span class="badge ${rootCause.risk_assessment.risk_level}">${rootCause.risk_assessment.risk_level.toUpperCase()}</span>
                    </div>
                    <div class="metric">
                        <span>識別根因</span>
                        <span class="metric-value">${rootCause.root_causes.length}</span>
                    </div>
                `;
                
                // 載入修復狀態
                const fixStatus = await fetch('/api/fix-status').then(r => r.json());
                document.getElementById('fix-status').innerHTML = `
                    <div class="metric">
                        <span>✅ 已修復</span>
                        <span class="metric-value" style="color: #16a34a;">${fixStatus.summary.fixed}</span>
                    </div>
                    <div class="metric">
                        <span>👁️ 需要審查</span>
                        <span class="metric-value" style="color: #ca8a04;">${fixStatus.summary.manual_review_required}</span>
                    </div>
                    <div class="metric">
                        <span>❌ 失敗</span>
                        <span class="metric-value" style="color: #dc2626;">${fixStatus.summary.failed}</span>
                    </div>
                `;
                
                // 載入詳細發現
                const findings = await fetch('/api/findings').then(r => r.json());
                const findingsHtml = findings.slice(0, 10).map(f => `
                    <div class="finding-item">
                        <div class="finding-type">
                            <span class="badge ${f.severity}">${f.severity.toUpperCase()}</span>
                            ${f.type}
                        </div>
                        <div class="finding-location">📍 ${f.location}</div>
                    </div>
                `).join('');
                
                document.getElementById('findings').innerHTML = findingsHtml || '<p>沒有發現問題</p>';
                
            } catch (error) {
                console.error('載入失敗:', error);
                document.querySelectorAll('.loading').forEach(el => {
                    el.innerHTML = '載入失敗，請檢查後端服務';
                });
            }
        }
        
        loadData();
        setInterval(loadData, 30000); // 每30秒刷新一次
    </script>
</body>
</html>"""
    
    with open(template_path, 'w') as f:
        f.write(html_content)

if __name__ == "__main__":
    main()