# CI Integration - 如何整合 03_refactor 到 CI/CD 流程

本文件說明如何將 `03_refactor/` 重構劇本整合到 CI/CD、Auto-Fix Bot、語言治理 workflow 和 Dashboard。

---

## 1. 整合目標

`03_refactor/` 作為「重構控制平面」，應在以下場景中被使用：

### 1.1 語言治理 Pipeline

當 CI 偵測到語言違規時：

1. 根據違規檔案路徑，查詢 `index.yaml` 找到對應的 `cluster_id`
2. 讀取對應的 `*_refactor.md` 劇本
3. 在 CI 輸出中顯示：
   - 該違規屬於哪個 cluster
   - 對應的重構計畫連結
   - P0/P1/P2 優先順序建議

### 1.2 Auto-Fix Bot

Auto-Fix Bot 在執行自動修復前：

1. 讀取目標檔案所屬 cluster 的 `*_refactor.md`
2. 檢查「Auto-Fix Bot 可以處理的項目」章節
3. 僅執行劇本中明確允許的自動修復操作
4. 對於需要人工審查的項目，建立 issue 並標註 `needs-human-review`

### 1.3 Dashboard 顯示

語言治理 Dashboard 在顯示 cluster 狀態時：

1. 從 `index.yaml` 讀取 cluster 元資料
2. 顯示對應的 `*_refactor.md` 連結
3. 展示 P0/P1/P2 進度條
4. 顯示驗收條件達成率

### 1.4 Issue Auto-Assignment

當有新的治理 issue 時：

1. 根據受影響檔案查詢對應 cluster
2. 從 `*_refactor.md` 中提取上下文
3. 自動分配給負責該 cluster 的團隊
4. 在 issue 描述中引用相關重構計畫

---

## 2. CI Workflow 範例

### 2.1 語言治理檢查 + 劇本連結

```yaml
# .github/workflows/language-governance.yml
name: Language Governance Check

on:
  pull_request:
    paths:
      - 'core/**'
      - 'services/**'
      - 'automation/**'
      - 'apps/**'

jobs:
  governance-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Language Governance
        run: npm run governance:check
      
      - name: Map Violations to Refactor Playbooks
        if: failure()
        run: |
          python3 tools/map-violations-to-playbooks.py \
            --violations governance/language-governance-report.json \
            --index docs/refactor_playbooks/03_refactor/index.yaml \
            --output governance-summary.md
      
      - name: Comment PR with Refactor Plan
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const summary = fs.readFileSync('governance-summary.md', 'utf8');
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: summary
            });
```

### 2.2 Auto-Fix 整合

```yaml
# .github/workflows/auto-fix.yml
name: Auto-Fix with Playbook Guidance

on:
  workflow_dispatch:
    inputs:
      cluster_id:
        description: 'Cluster ID (e.g., core/architecture-stability)'
        required: true
      fix_level:
        description: 'Fix level (p0/p1/p2)'
        required: true
        default: 'p0'

jobs:
  auto-fix:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Load Refactor Playbook
        run: |
          python3 tools/load-playbook.py \
            --cluster "${{ github.event.inputs.cluster_id }}" \
            --index docs/refactor_playbooks/03_refactor/index.yaml \
            --output playbook-context.json
      
      - name: Execute Auto-Fix
        run: |
          python3 tools/ai-auto-fix.py \
            --playbook-context playbook-context.json \
            --fix-level "${{ github.event.inputs.fix_level }}" \
            --dry-run false
      
      - name: Create PR with Changes
        uses: peter-evans/create-pull-request@v6
        with:
          title: "auto-fix: ${{ github.event.inputs.cluster_id }} (${{ github.event.inputs.fix_level }})"
          body: |
            Auto-fix based on refactor playbook: ${{ github.event.inputs.cluster_id }}
            
            Refactor Plan: [View Playbook](../blob/main/docs/refactor_playbooks/03_refactor/...)
            
            Fix Level: ${{ github.event.inputs.fix_level }}
          branch: auto-fix/${{ github.event.inputs.cluster_id }}
          labels: auto-fix, ${{ github.event.inputs.fix_level }}
```

---

## 3. 工具腳本實作

### 3.1 map-violations-to-playbooks.py

```python
#!/usr/bin/env python3
"""
Map language governance violations to refactor playbooks.
"""
import json
import yaml
from pathlib import Path

def load_index(index_path: str) -> dict:
    """Load index.yaml"""
    with open(index_path) as f:
        return yaml.safe_load(f)

def map_file_to_cluster(file_path: str, clusters: list) -> dict | None:
    """Find which cluster a file belongs to"""
    for cluster in clusters:
        cluster_id = cluster['cluster_id']
        # Match file path to cluster (e.g., core/... -> core/architecture-stability)
        if file_path.startswith(cluster_id.split('/')[0] + '/'):
            return cluster
    return None

def generate_summary(violations: list, index: dict) -> str:
    """Generate markdown summary linking violations to playbooks"""
    clusters = index['clusters']
    summary = ["# 語言治理違規與重構劇本對應\n"]
    
    # Group violations by cluster
    cluster_violations = {}
    for violation in violations:
        cluster = map_file_to_cluster(violation['file'], clusters)
        if cluster:
            cluster_id = cluster['cluster_id']
            if cluster_id not in cluster_violations:
                cluster_violations[cluster_id] = {
                    'cluster': cluster,
                    'violations': []
                }
            cluster_violations[cluster_id]['violations'].append(violation)
    
    # Generate summary for each cluster
    for cluster_id, data in cluster_violations.items():
        cluster = data['cluster']
        violations = data['violations']
        
        summary.append(f"## {cluster_id}\n")
        summary.append(f"**重構劇本**: [查看計畫](../blob/main/docs/refactor_playbooks/03_refactor/{cluster['refactor_file']})\n")
        summary.append(f"**違規數量**: {len(violations)}\n")
        summary.append("\n### 違規清單\n")
        
        for v in violations[:5]:  # Show top 5
            summary.append(f"- `{v['file']}` - {v['rule']}\n")
        
        if len(violations) > 5:
            summary.append(f"\n_...以及 {len(violations) - 5} 個其他違規_\n")
        
        summary.append("\n")
    
    return ''.join(summary)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--violations', required=True)
    parser.add_argument('--index', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    
    with open(args.violations) as f:
        violations = json.load(f)
    
    index = load_index(args.index)
    summary = generate_summary(violations, index)
    
    with open(args.output, 'w') as f:
        f.write(summary)
```

### 3.2 load-playbook.py

```python
#!/usr/bin/env python3
"""
Load refactor playbook and extract auto-fix context.
"""
import yaml
import json
import re
from pathlib import Path

def load_playbook(cluster_id: str, index_path: str) -> dict:
    """Load refactor playbook for a cluster"""
    with open(index_path) as f:
        index = yaml.safe_load(f)
    
    # Find cluster in index
    cluster = None
    for c in index['clusters']:
        if c['cluster_id'] == cluster_id:
            cluster = c
            break
    
    if not cluster:
        raise ValueError(f"Cluster {cluster_id} not found in index")
    
    # Load playbook markdown
    playbook_path = Path(index_path).parent / cluster['refactor_file']
    with open(playbook_path) as f:
        content = f.read()
    
    # Extract auto-fix section
    auto_fix_section = extract_section(content, "Auto-Fix Bot 可以處理的項目")
    
    return {
        'cluster_id': cluster_id,
        'playbook_path': str(playbook_path),
        'auto_fix_allowed': parse_auto_fix_items(auto_fix_section),
        'manual_review_required': parse_manual_items(auto_fix_section),
        'p0_actions': extract_section(content, "P0"),
        'p1_actions': extract_section(content, "P1"),
        'p2_actions': extract_section(content, "P2")
    }

def extract_section(content: str, heading: str) -> str:
    """Extract content under a specific heading"""
    pattern = f"## .*?{heading}.*?\n(.*?)(?=\n## |\Z)"
    match = re.search(pattern, content, re.DOTALL)
    return match.group(1) if match else ""

def parse_auto_fix_items(section: str) -> list:
    """Parse allowed auto-fix items from section"""
    # Simple implementation - can be enhanced
    items = []
    for line in section.split('\n'):
        if line.strip().startswith('-') or line.strip().startswith('*'):
            items.append(line.strip()[1:].strip())
    return items

def parse_manual_items(section: str) -> list:
    """Parse manual review items from section"""
    # Look for "必須人工審查" subsection
    manual_section = extract_section(section, "必須人工審查")
    items = []
    for line in manual_section.split('\n'):
        if line.strip().startswith('-') or line.strip().startswith('*'):
            items.append(line.strip()[1:].strip())
    return items

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--cluster', required=True)
    parser.add_argument('--index', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    
    context = load_playbook(args.cluster, args.index)
    
    with open(args.output, 'w') as f:
        json.dump(context, f, indent=2, ensure_ascii=False)
```

---

## 4. Dashboard 整合

### 4.1 讀取劇本狀態

Dashboard 應該：

1. 定期讀取 `index.yaml` 獲取最新 cluster 列表
2. 解析各 `*_refactor.md` 提取狀態資訊
3. 顯示每個 cluster 的：
   - 重構進度（P0/P1/P2 完成率）
   - 驗收條件達成狀況
   - 最後更新時間

### 4.2 API Endpoint 建議

```typescript
// apps/web/api/refactor-playbooks.ts
import { readFile } from 'fs/promises';
import yaml from 'js-yaml';
import { marked } from 'marked';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const clusterId = searchParams.get('cluster_id');
  
  // Load index
  const indexContent = await readFile(
    'docs/refactor_playbooks/03_refactor/index.yaml',
    'utf-8'
  );
  const index = yaml.load(indexContent);
  
  // Find cluster
  const cluster = index.clusters.find(c => c.cluster_id === clusterId);
  if (!cluster) {
    return Response.json({ error: 'Cluster not found' }, { status: 404 });
  }
  
  // Load playbook
  const playbookPath = `docs/refactor_playbooks/03_refactor/${cluster.refactor_file}`;
  const playbookContent = await readFile(playbookPath, 'utf-8');
  
  // Parse markdown
  const html = marked(playbookContent);
  
  return Response.json({
    cluster_id: clusterId,
    playbook: {
      path: playbookPath,
      content: playbookContent,
      html: html
    },
    metadata: cluster
  });
}
```

---

## 5. 通知與告警

### 5.1 Slack 通知

當語言治理失敗時，發送包含劇本連結的 Slack 訊息：

```yaml
- name: Notify Slack on Governance Failure
  if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "語言治理檢查失敗 ❌",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*語言治理檢查失敗*\n\n請查看對應的重構劇本：\n- <https://github.com/${{ github.repository }}/blob/main/docs/refactor_playbooks/03_refactor/core/core__architecture_refactor.md|Core Architecture 重構計畫>"
            }
          }
        ]
      }
```

---

## 6. 未來擴充

### 6.1 自動化進度追蹤

- CI 定期檢查 P0/P1/P2 任務完成狀況
- 自動更新 `index.yaml` 中的 `status` 欄位
- 產生週報顯示重構進度

### 6.2 依賴關係追蹤

- 從劇本中解析上下游依賴
- 自動檢查重構順序是否正確
- 在 Dashboard 中顯示依賴圖

### 6.3 影響範圍分析

- 在 PR 中自動分析受影響的 clusters
- 顯示相關重構劇本
- 提醒需要更新的其他 clusters

---

最後更新：2025-12-06
