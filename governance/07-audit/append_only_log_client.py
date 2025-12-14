#!/usr/bin/env python3
"""
==============================================================================
Append-Only Log Client - 不可變審計日誌客戶端
==============================================================================
用途: 將所有策略決定、測試結果、CD 決策寫入不可變事件帳本
語言: 繁體中文註解
==============================================================================
"""

import hashlib
import hmac
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class AppendOnlyLogClient:
    """
    Append-Only Log Client
    提供不可變審計日誌的寫入與驗證功能
    """

    def __init__(
        self,
        log_dir: Optional[str] = None,
        log_file: str = "audit-log.jsonl",
        enable_signature: bool = True,
        verbose: bool = False,
    ):
        """
        初始化審計日誌客戶端

        Args:
            log_dir: 日誌目錄路徑
            log_file: 日誌檔案名稱
            enable_signature: 是否啟用簽章
            verbose: 是否顯示詳細輸出
        """
        self.log_dir = Path(log_dir or Path.cwd() / "audit" / "logs")
        self.current_log_file = log_file
        self.enable_signature = enable_signature
        self.verbose = verbose

        # 確保日誌目錄存在
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def hash_event(self, event: Dict[str, Any]) -> str:
        """
        計算事件雜湊 (SHA3-512)

        Args:
            event: 事件資料

        Returns:
            事件雜湊值
        """
        # 排序鍵以確保一致性
        sorted_data = json.dumps(event, sort_keys=True)
        return hashlib.sha3_512(sorted_data.encode()).hexdigest()

    def get_previous_hash(self) -> str:
        """
        取得前一個事件的雜湊

        Returns:
            前一個事件的雜湊值，若無則返回創世區塊雜湊
        """
        log_path = self.log_dir / self.current_log_file

        if not log_path.exists():
            return "0" * 128  # 創世區塊雜湊

        content = log_path.read_text(encoding="utf-8")
        lines = [line.strip() for line in content.strip().split("\n") if line.strip()]

        if not lines:
            return "0" * 128

        last_event = json.loads(lines[-1])
        return last_event["hash"]

    def get_next_sequence(self) -> int:
        """
        取得下一個序號

        Returns:
            下一個序號
        """
        log_path = self.log_dir / self.current_log_file

        if not log_path.exists():
            return 1

        content = log_path.read_text(encoding="utf-8")
        lines = [line.strip() for line in content.strip().split("\n") if line.strip()]

        return len(lines) + 1

    def sign_event(self, event: Dict[str, Any]) -> str:
        """
        簽署事件 (簡易版，實際應使用真實密鑰)

        Args:
            event: 事件資料

        Returns:
            事件簽章
        """
        data = json.dumps(event)
        secret = os.environ.get("AUDIT_SECRET", "default-secret")
        return hmac.new(secret.encode(), data.encode(), hashlib.sha256).hexdigest()

    def append(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        添加事件到審計日誌

        Args:
            event: 事件資料，必須包含:
                - type: 事件類型 (policy_test, cd_decision, deployment, rollback)
                - action: 執行動作
                - data: 事件資料 (可選)
                - metadata: 元資料 (可選)

        Returns:
            完整的審計事件

        Raises:
            ValueError: 若事件缺少必要欄位
        """
        try:
            # 驗證必要欄位
            if "type" not in event or "action" not in event:
                raise ValueError("事件必須包含 type 和 action 欄位")

            # 建立審計事件
            metadata = event.get("metadata", {})
            audit_event = {
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "type": event["type"],
                "action": event["action"],
                "data": event.get("data", {}),
                "metadata": {
                    **metadata,
                    "source": metadata.get("source", "unknown"),
                    "actor": metadata.get("actor")
                    or os.environ.get("USER", "system"),
                    "environment": metadata.get("environment")
                    or os.environ.get("NODE_ENV", "production"),
                    "commit_sha": metadata.get("commit_sha")
                    or os.environ.get("GITHUB_SHA", "unknown"),
                    "workflow_id": metadata.get("workflow_id")
                    or os.environ.get("GITHUB_RUN_ID", "unknown"),
                },
                "previousHash": self.get_previous_hash(),
                "sequence": self.get_next_sequence(),
            }

            # 計算當前事件雜湊
            audit_event["hash"] = self.hash_event(audit_event)

            # 如果啟用簽章，添加簽章
            if self.enable_signature:
                audit_event["signature"] = self.sign_event(audit_event)

            # 寫入日誌檔案
            log_path = self.log_dir / self.current_log_file
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(audit_event) + "\n")

            if self.verbose:
                print(
                    f"✅ 審計事件已記錄: {{"
                    f"type: {audit_event['type']}, "
                    f"action: {audit_event['action']}, "
                    f"sequence: {audit_event['sequence']}, "
                    f"hash: {audit_event['hash'][:16]}..."
                    f"}}"
                )

            return audit_event

        except Exception as error:
            print(f"❌ 寫入審計日誌失敗: {str(error)}")
            raise

    def verify(self) -> Dict[str, Any]:
        """
        驗證日誌完整性

        Returns:
            驗證結果，包含:
                - valid: 是否有效
                - totalEvents: 總事件數
                - errors: 錯誤列表
        """
        log_path = self.log_dir / self.current_log_file

        if not log_path.exists():
            print("⚠️  日誌檔案不存在")
            return {"valid": True, "totalEvents": 0, "errors": []}

        content = log_path.read_text(encoding="utf-8")
        lines = [line.strip() for line in content.strip().split("\n") if line.strip()]

        errors = []
        previous_hash = "0" * 128

        for i, line in enumerate(lines):
            event = json.loads(line)

            # 驗證序號
            if event["sequence"] != i + 1:
                errors.append(f"序號錯誤: 預期 {i + 1}, 實際 {event['sequence']}")

            # 驗證前一個雜湊
            if event["previousHash"] != previous_hash:
                errors.append(f"雜湊鏈斷裂: 事件 {event['sequence']}")

            # 驗證當前雜湊
            event_copy = {k: v for k, v in event.items() if k not in ["hash", "signature"]}
            computed_hash = self.hash_event(event_copy)

            if event["hash"] != computed_hash:
                errors.append(f"雜湊不符: 事件 {event['sequence']}")

            previous_hash = event["hash"]

        result = {"valid": len(errors) == 0, "totalEvents": len(lines), "errors": errors}

        if self.verbose:
            if result["valid"]:
                print(f"✅ 日誌驗證通過: {result['totalEvents']} 個事件")
            else:
                print(f"❌ 日誌驗證失敗: {len(errors)} 個錯誤")
                for error in errors:
                    print(f"  - {error}")

        return result

    def query(
        self,
        event_type: Optional[str] = None,
        action: Optional[str] = None,
        since: Optional[str] = None,
        until: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        查詢事件

        Args:
            event_type: 事件類型過濾
            action: 動作過濾
            since: 開始時間過濾 (ISO 8601 格式)
            until: 結束時間過濾 (ISO 8601 格式)

        Returns:
            符合條件的事件列表
        """
        log_path = self.log_dir / self.current_log_file

        if not log_path.exists():
            return []

        content = log_path.read_text(encoding="utf-8")
        lines = [line.strip() for line in content.strip().split("\n") if line.strip()]

        events = [json.loads(line) for line in lines]

        # 應用過濾器
        if event_type:
            events = [e for e in events if e["type"] == event_type]

        if action:
            events = [e for e in events if e["action"] == action]

        if since:
            since_dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
            events = [
                e
                for e in events
                if datetime.fromisoformat(e["timestamp"].replace("Z", "+00:00"))
                >= since_dt
            ]

        if until:
            until_dt = datetime.fromisoformat(until.replace("Z", "+00:00"))
            events = [
                e
                for e in events
                if datetime.fromisoformat(e["timestamp"].replace("Z", "+00:00"))
                <= until_dt
            ]

        return events

    def generate_report(
        self, include_events: bool = False, **filter_kwargs
    ) -> Dict[str, Any]:
        """
        生成審計報告

        Args:
            include_events: 是否包含事件詳情
            **filter_kwargs: 查詢過濾參數

        Returns:
            審計報告
        """
        events = self.query(**filter_kwargs)

        report = {
            "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "total_events": len(events),
            "period": {
                "start": events[0]["timestamp"] if events else None,
                "end": events[-1]["timestamp"] if events else None,
            },
            "by_type": {},
            "by_action": {},
        }

        if include_events:
            report["events"] = events

        # 統計事件類型
        for event in events:
            event_type = event["type"]
            action = event["action"]
            report["by_type"][event_type] = report["by_type"].get(event_type, 0) + 1
            report["by_action"][action] = report["by_action"].get(action, 0) + 1

        return report


# CLI 介面
def main():
    """CLI 主函數"""
    import sys

    args = sys.argv[1:]
    if not args:
        print("用法:")
        print("  append <type> <action> <message>  - 添加事件")
        print("  verify                            - 驗證日誌完整性")
        print("  query <type>                      - 查詢事件")
        print("  report                            - 生成報告")
        sys.exit(0)

    command = args[0]
    client = AppendOnlyLogClient(verbose=True)

    if command == "append":
        event = {
            "type": args[1] if len(args) > 1 else "test",
            "action": args[2] if len(args) > 2 else "test_action",
            "data": {"message": args[3] if len(args) > 3 else "Test event"},
            "metadata": {},
        }
        client.append(event)

    elif command == "verify":
        client.verify()

    elif command == "query":
        event_type = args[1] if len(args) > 1 else None
        events = client.query(event_type=event_type)
        print(json.dumps(events, indent=2, ensure_ascii=False))

    elif command == "report":
        report = client.generate_report(include_events=False)
        print(json.dumps(report, indent=2, ensure_ascii=False))

    else:
        print(f"❌ 未知命令: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()


# ==============================================================================
# 使用範例
# ==============================================================================
# from append_only_log_client import AppendOnlyLogClient
#
# log = AppendOnlyLogClient()
#
# # 記錄策略測試
# log.append({
#     'type': 'policy_test',
#     'action': 'conftest_run',
#     'data': {'result': 'passed', 'violations': 0},
#     'metadata': {'source': 'ci', 'actor': 'github-actions'}
# })
#
# # 記錄部署決策
# log.append({
#     'type': 'cd_decision',
#     'action': 'deploy_approved',
#     'data': {'environment': 'production', 'version': 'v2.0.0'},
#     'metadata': {'source': 'argocd', 'actor': 'platform-team'}
# })
#
# # 驗證日誌
# log.verify()
# ==============================================================================
