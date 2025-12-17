#!/usr/bin/env python3
"""
Canonical Naming Migration Tool
用於檢測命名衝突、生成遷移建議、執行批量遷移

Usage:
    python naming-migration.py --spec canonical/machine-spec.yaml --scan
    python naming-migration.py --spec canonical/machine-spec.yaml --detect-conflicts
    python naming-migration.py --spec canonical/machine-spec.yaml --generate-plan migration-plan.yaml
"""

import yaml
import argparse
import re
import sys
import json
from typing import Dict, List, Tuple
from datetime import datetime

# Try to import Kubernetes client (optional)
try:
    from kubernetes import client, config
    K8S_AVAILABLE = True
except ImportError:
    K8S_AVAILABLE = False
    print("Warning: kubernetes package not installed. Cluster scanning will be unavailable.", file=sys.stderr)


class NamingMigrationTool:
    def __init__(self, spec_path: str):
        """載入 machine-spec.yaml"""
        try:
            with open(spec_path, 'r') as f:
                self.spec = yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Error: Spec file not found: {spec_path}", file=sys.stderr)
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"Error parsing spec file: {e}", file=sys.stderr)
            sys.exit(1)

        self.canonical_regex = self.spec['spec']['naming']['canonical_regex']
        self.naming_modes = self.spec['spec']['naming']['naming_modes']
        self.reserved_tokens = self.spec['spec']['naming']['reserved_tokens']
        self.environments = [e['name'] for e in self.spec['spec']['naming']['environments']]

    def scan_cluster(self) -> List[Dict]:
        """掃描集群中的所有 Namespace"""
        if not K8S_AVAILABLE:
            print("Error: kubernetes package required for cluster scanning", file=sys.stderr)
            print("Install with: pip install kubernetes", file=sys.stderr)
            sys.exit(1)

        try:
            config.load_kube_config()
            v1 = client.CoreV1Api()
            namespaces = v1.list_namespace()

            results = []
            for ns in namespaces.items:
                name = ns.metadata.name
                labels = ns.metadata.labels or {}
                annotations = ns.metadata.annotations or {}

                result = {
                    'name': name,
                    'labels': labels,
                    'annotations': annotations,
                    'compliant': self.validate_name(name),
                    'issues': self.check_issues(name, labels, annotations)
                }
                results.append(result)

            return results
        except Exception as e:
            print(f"Error scanning cluster: {e}", file=sys.stderr)
            sys.exit(1)

    def validate_name(self, name: str) -> bool:
        """驗證命名是否符合 canonical pattern"""
        return bool(re.match(self.canonical_regex, name))

    def check_issues(self, name: str, labels: Dict, annotations: Dict) -> List[str]:
        """檢查所有潛在問題"""
        issues = []

        # 檢查命名格式
        if not self.validate_name(name):
            issues.append(f"Name '{name}' does not match canonical pattern")

        # 檢查保留關鍵字
        for token in self.reserved_tokens:
            if token in name:
                issues.append(f"Name contains reserved keyword '{token}'")

        # 檢查必需標籤
        if 'environment' not in labels:
            issues.append("Missing required label 'environment'")
        elif labels['environment'] not in self.environments:
            issues.append(f"Invalid environment '{labels['environment']}'")

        if 'tenant' not in labels:
            issues.append("Missing required label 'tenant'")

        # 檢查 URN annotation
        if 'machinenativeops.io/canonical-urn' not in annotations:
            issues.append("Missing URN annotation 'machinenativeops.io/canonical-urn'")

        return issues

    def detect_conflicts(self, namespaces: List[Dict]) -> List[Dict]:
        """檢測命名衝突"""
        conflicts = []
        name_map = {}

        for ns in namespaces:
            name = ns['name']

            # 檢查重複命名
            if name in name_map:
                conflicts.append({
                    'type': 'duplicate',
                    'name': name,
                    'conflict_with': name_map[name]
                })
            name_map[name] = ns

            # 檢查相似命名（可能導致混淆）
            similar = self.find_similar_names(name, list(name_map.keys()))
            if similar:
                conflicts.append({
                    'type': 'similar',
                    'name': name,
                    'similar_to': similar
                })

        return conflicts

    def find_similar_names(self, name: str, existing: List[str]) -> List[str]:
        """查找相似命名（Levenshtein 距離）"""
        similar = []
        for existing_name in existing:
            if existing_name == name:
                continue

            distance = self.levenshtein_distance(name, existing_name)
            if distance <= 2:  # 距離閾值
                similar.append(existing_name)

        return similar

    def levenshtein_distance(self, s1: str, s2: str) -> int:
        """計算編輯距離"""
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def generate_suggestions(self, namespace: Dict) -> List[Dict]:
        """為不合規 Namespace 生成命名建議"""
        name = namespace['name']
        labels = namespace['labels']
        suggestions = []

        # 嘗試匹配各種命名模式
        for mode in self.naming_modes:
            try:
                suggestion = self.apply_naming_mode(name, labels, mode)
                if suggestion:
                    suggestions.append({
                        'pattern': mode['id'],
                        'suggested_name': suggestion,
                        'example': mode['example']
                    })
            except Exception as e:
                continue

        # 如果無法匹配，使用 fallback
        if not suggestions:
            env = labels.get('environment', 'dev')
            suggestions.append({
                'pattern': 'fallback',
                'suggested_name': f"team-{self.sanitize_name(name)}-{env}",
                'example': 'team-myapp-prod'
            })

        return suggestions

    def apply_naming_mode(self, name: str, labels: Dict, mode: Dict) -> str:
        """應用特定命名模式"""
        mode_id = mode['id']

        if mode_id == 'team-domain-env':
            domain = labels.get('domain', self.extract_domain(name))
            env = labels.get('environment', 'dev')
            return f"team-{domain}-{env}"

        elif mode_id == 'tenant-workload-env-region':
            tenant = labels.get('tenant', 'default')
            workload = labels.get('workload', self.extract_domain(name))
            env = labels.get('environment', 'dev')
            region = labels.get('region', 'useast')
            return f"tenant-{tenant}-{workload}-{env}-{region}"

        elif mode_id == 'env-app-version':
            env = labels.get('environment', 'dev')
            app = labels.get('app', self.extract_domain(name))
            version = labels.get('version', 'v1')
            return f"{env}-{app}-{version}"

        return None

    def extract_domain(self, name: str) -> str:
        """從現有名稱中提取 domain"""
        # 移除常見前綴/後綴
        cleaned = name.replace('prod-', '').replace('-prod', '')
        cleaned = cleaned.replace('staging-', '').replace('-staging', '')
        cleaned = cleaned.replace('dev-', '').replace('-dev', '')
        cleaned = self.sanitize_name(cleaned)
        return cleaned[:20]  # 限制長度

    def sanitize_name(self, name: str) -> str:
        """清理名稱使其符合規範"""
        # 轉小寫
        name = name.lower()
        # 移除非法字符
        name = re.sub(r'[^a-z0-9-]', '-', name)
        # 移除連續破折號
        name = re.sub(r'-+', '-', name)
        # 移除首尾破折號
        name = name.strip('-')
        return name

    def generate_migration_plan(self, namespaces: List[Dict], output_path: str):
        """生成完整遷移計劃"""
        plan = {
            'apiVersion': 'governance.machinenativeops.io/v1alpha1',
            'kind': 'MigrationPlan',
            'metadata': {
                'name': 'naming-migration-plan',
                'generated_at': datetime.now().isoformat()
            },
            'spec': {
                'total_resources': len(namespaces),
                'non_compliant': sum(1 for ns in namespaces if not ns['compliant']),
                'batches': []
            }
        }

        # 分批遷移
        non_compliant = [ns for ns in namespaces if not ns['compliant']]
        batch_size = 10

        for i in range(0, len(non_compliant), batch_size):
            batch = non_compliant[i:i+batch_size]
            batch_plan = {
                'batch_id': f"batch-{i//batch_size + 1}",
                'resources': []
            }

            for ns in batch:
                suggestions = self.generate_suggestions(ns)
                batch_plan['resources'].append({
                    'current_name': ns['name'],
                    'issues': ns['issues'],
                    'suggestions': suggestions
                })

            plan['spec']['batches'].append(batch_plan)

        # 寫入文件
        with open(output_path, 'w') as f:
            yaml.dump(plan, f, default_flow_style=False, allow_unicode=True)

        print(f"✅ Migration plan generated: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Canonical Naming Migration Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan cluster for namespaces
  python naming-migration.py --spec canonical/machine-spec.yaml --scan

  # Detect naming conflicts
  python naming-migration.py --spec canonical/machine-spec.yaml --scan --detect-conflicts

  # Generate migration plan
  python naming-migration.py --spec canonical/machine-spec.yaml --scan --generate-plan migration-plan.yaml

  # Output results as JSON
  python naming-migration.py --spec canonical/machine-spec.yaml --scan --output results.json
        """
    )

    parser.add_argument('--spec', required=True, help='Path to machine-spec.yaml')
    parser.add_argument('--scan', action='store_true', help='Scan cluster for namespaces')
    parser.add_argument('--detect-conflicts', action='store_true', help='Detect naming conflicts')
    parser.add_argument('--generate-plan', metavar='FILE', help='Generate migration plan (output path)')
    parser.add_argument('--output', metavar='FILE', help='Output results to file (JSON format)')

    args = parser.parse_args()

    tool = NamingMigrationTool(args.spec)

    if args.scan:
        print("🔍 Scanning cluster for namespaces...")
        namespaces = tool.scan_cluster()

        # 統計
        total = len(namespaces)
        compliant = sum(1 for ns in namespaces if ns['compliant'])
        non_compliant = total - compliant

        print(f"\n=== Namespace Scan Results ===")
        print(f"Total: {total}")
        print(f"Compliant: {compliant} ({compliant/total*100:.1f}%)" if total > 0 else "Compliant: 0")
        print(f"Non-compliant: {non_compliant} ({non_compliant/total*100:.1f}%)" if total > 0 else "Non-compliant: 0")

        print(f"\n=== Non-compliant Namespaces ===")
        for ns in namespaces:
            if not ns['compliant']:
                print(f"\n{ns['name']}:")
                for issue in ns['issues']:
                    print(f"  - {issue}")

        # 輸出 JSON
        if args.output:
            output_data = {
                'scan_results': namespaces,
                'summary': {
                    'total': total,
                    'compliant': compliant,
                    'non_compliant': non_compliant,
                    'compliance_rate': (compliant / total * 100) if total > 0 else 0
                }
            }

        if args.detect_conflicts:
            print("\n🔍 Detecting naming conflicts...")
            conflicts = tool.detect_conflicts(namespaces)
            if conflicts:
                print(f"\n=== Detected Conflicts ({len(conflicts)}) ===")
                for conflict in conflicts:
                    print(f"{conflict['type']}: {conflict['name']}")
                    if 'similar_to' in conflict:
                        print(f"  Similar to: {', '.join(conflict['similar_to'])}")

                if args.output:
                    output_data['conflicts'] = conflicts
            else:
                print("✅ No conflicts detected")

        if args.generate_plan:
            print(f"\n📝 Generating migration plan...")
            tool.generate_migration_plan(namespaces, args.generate_plan)

        # 寫入輸出文件
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=2)
            print(f"\n✅ Results written to: {args.output}")

    else:
        parser.print_help()
        print("\nError: --scan flag is required", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
