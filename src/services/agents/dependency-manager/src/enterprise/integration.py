"""
企業整合模組 (Enterprise Integration Module)

提供企業級系統整合功能：
- REST API 整合
- Webhook 事件通知
- LDAP/SSO 認證支援
- 企業訊息平台整合 (Slack, Teams, etc.)
- CI/CD 平台深度整合

第一優先級：基礎建設階段 - 企業級應用開發
"""

import hashlib
import hmac
import json
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class IntegrationType(Enum):
    """整合類型"""
    REST_API = "rest_api"
    WEBHOOK = "webhook"
    LDAP = "ldap"
    SSO = "sso"
    SLACK = "slack"
    TEAMS = "teams"
    JIRA = "jira"
    GITHUB = "github"
    GITLAB = "gitlab"
    JENKINS = "jenkins"
    AZURE_DEVOPS = "azure_devops"


class AuthMethod(Enum):
    """認證方法"""
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    JWT = "jwt"
    LDAP = "ldap"
    SAML = "saml"
    OIDC = "oidc"


@dataclass
class IntegrationConfig:
    """整合配置"""
    type: IntegrationType
    name: str
    endpoint: str
    auth_method: AuthMethod
    credentials: dict[str, str] = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)
    options: dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    retry_count: int = 3
    timeout_seconds: int = 30
    rate_limit_per_minute: int = 60


@dataclass
class WebhookEvent:
    """Webhook 事件"""
    event_type: str
    payload: dict[str, Any]
    timestamp: datetime
    signature: str | None = None
    delivery_id: str | None = None


@dataclass
class IntegrationResult:
    """整合操作結果"""
    success: bool
    integration_name: str
    operation: str
    response: dict[str, Any] | None = None
    error: str | None = None
    duration_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


class EnterpriseIntegration:
    """
    企業級整合管理器
    
    提供統一的企業系統整合介面，支援：
    - 多種認證機制
    - Webhook 事件處理
    - 訊息平台通知
    - CI/CD 整合
    """

    def __init__(self):
        """初始化整合管理器"""
        self._integrations: dict[str, IntegrationConfig] = {}
        self._webhook_handlers: dict[str, list[Callable]] = {}
        self._event_history: list[WebhookEvent] = []
        self._rate_limiters: dict[str, list[datetime]] = {}

    def register_integration(self, config: IntegrationConfig) -> bool:
        """
        註冊整合配置
        
        Args:
            config: 整合配置
            
        Returns:
            是否註冊成功
        """
        if config.name in self._integrations:
            return False

        self._integrations[config.name] = config
        self._rate_limiters[config.name] = []
        return True

    def unregister_integration(self, name: str) -> bool:
        """
        取消註冊整合
        
        Args:
            name: 整合名稱
            
        Returns:
            是否取消成功
        """
        if name not in self._integrations:
            return False

        del self._integrations[name]
        if name in self._rate_limiters:
            del self._rate_limiters[name]
        return True

    def get_integration(self, name: str) -> IntegrationConfig | None:
        """取得整合配置"""
        return self._integrations.get(name)

    def list_integrations(self,
                         integration_type: IntegrationType | None = None,
                         enabled_only: bool = False) -> list[IntegrationConfig]:
        """
        列出整合
        
        Args:
            integration_type: 篩選特定類型
            enabled_only: 僅顯示啟用的整合
            
        Returns:
            整合配置列表
        """
        result = list(self._integrations.values())

        if integration_type:
            result = [i for i in result if i.type == integration_type]

        if enabled_only:
            result = [i for i in result if i.enabled]

        return result

    # ==================== Webhook 管理 ====================

    def register_webhook_handler(self,
                                 event_type: str,
                                 handler: Callable[[WebhookEvent], None]) -> None:
        """
        註冊 Webhook 事件處理器
        
        Args:
            event_type: 事件類型
            handler: 處理函數
        """
        if event_type not in self._webhook_handlers:
            self._webhook_handlers[event_type] = []
        self._webhook_handlers[event_type].append(handler)

    def process_webhook(self,
                       event_type: str,
                       payload: dict[str, Any],
                       signature: str | None = None,
                       secret: str | None = None) -> IntegrationResult:
        """
        處理 Webhook 事件
        
        Args:
            event_type: 事件類型
            payload: 事件資料
            signature: 簽名（用於驗證）
            secret: 密鑰（用於驗證）
            
        Returns:
            處理結果
        """
        start_time = datetime.now()

        # 驗證簽名
        if signature and secret and not self._verify_signature(payload, signature, secret):
            return IntegrationResult(
                success=False,
                integration_name="webhook",
                operation="process",
                error="簽名驗證失敗"
            )

        # 建立事件
        event = WebhookEvent(
            event_type=event_type,
            payload=payload,
            timestamp=datetime.now(),
            signature=signature
        )

        self._event_history.append(event)

        # 執行處理器
        handlers = self._webhook_handlers.get(event_type, [])
        errors = []

        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                errors.append(str(e))

        duration = (datetime.now() - start_time).total_seconds() * 1000

        if errors:
            return IntegrationResult(
                success=False,
                integration_name="webhook",
                operation="process",
                error="; ".join(errors),
                duration_ms=duration
            )

        return IntegrationResult(
            success=True,
            integration_name="webhook",
            operation="process",
            response={"handlers_executed": len(handlers)},
            duration_ms=duration
        )

    def _verify_signature(self,
                         payload: dict[str, Any],
                         signature: str,
                         secret: str) -> bool:
        """驗證 Webhook 簽名"""
        payload_str = json.dumps(payload, sort_keys=True)
        expected = hmac.new(
            secret.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, expected)

    # ==================== 訊息通知 ====================

    def send_notification(self,
                         integration_name: str,
                         message: str,
                         channel: str | None = None,
                         mentions: list[str] | None = None,
                         attachments: list[dict] | None = None) -> IntegrationResult:
        """
        發送通知訊息
        
        Args:
            integration_name: 整合名稱
            message: 訊息內容
            channel: 頻道（可選）
            mentions: 提及用戶（可選）
            attachments: 附件（可選）
            
        Returns:
            發送結果
        """
        config = self._integrations.get(integration_name)
        if not config:
            return IntegrationResult(
                success=False,
                integration_name=integration_name,
                operation="send_notification",
                error=f"整合 '{integration_name}' 不存在"
            )

        if not config.enabled:
            return IntegrationResult(
                success=False,
                integration_name=integration_name,
                operation="send_notification",
                error=f"整合 '{integration_name}' 已停用"
            )

        # 速率限制檢查
        if not self._check_rate_limit(integration_name):
            return IntegrationResult(
                success=False,
                integration_name=integration_name,
                operation="send_notification",
                error="超過速率限制"
            )

        # 根據類型格式化訊息
        formatted_payload = self._format_notification(
            config.type, message, channel, mentions, attachments
        )

        # 模擬發送（實際實現需要 HTTP 客戶端）
        return IntegrationResult(
            success=True,
            integration_name=integration_name,
            operation="send_notification",
            response={"payload": formatted_payload}
        )

    def _format_notification(self,
                            integration_type: IntegrationType,
                            message: str,
                            channel: str | None,
                            mentions: list[str] | None,
                            attachments: list[dict] | None) -> dict[str, Any]:
        """格式化通知訊息"""
        if integration_type == IntegrationType.SLACK:
            payload = {"text": message}
            if channel:
                payload["channel"] = channel
            if mentions:
                payload["text"] = " ".join(f"<@{m}>" for m in mentions) + " " + message
            if attachments:
                payload["attachments"] = attachments
            return payload

        elif integration_type == IntegrationType.TEAMS:
            payload = {
                "@type": "MessageCard",
                "text": message
            }
            if mentions:
                payload["text"] = " ".join(f"@{m}" for m in mentions) + " " + message
            return payload

        else:
            return {"message": message, "channel": channel}

    def _check_rate_limit(self, integration_name: str) -> bool:
        """檢查速率限制"""
        config = self._integrations.get(integration_name)
        if not config:
            return False

        now = datetime.now()
        window_start = now.timestamp() - 60  # 1 分鐘視窗

        # 清理舊記錄
        self._rate_limiters[integration_name] = [
            t for t in self._rate_limiters[integration_name]
            if t.timestamp() > window_start
        ]

        # 檢查是否超過限制
        if len(self._rate_limiters[integration_name]) >= config.rate_limit_per_minute:
            return False

        # 記錄此次請求
        self._rate_limiters[integration_name].append(now)
        return True

    # ==================== CI/CD 整合 ====================

    def trigger_ci_build(self,
                        integration_name: str,
                        repository: str,
                        branch: str = "main",
                        parameters: dict[str, str] | None = None) -> IntegrationResult:
        """
        觸發 CI 構建
        
        Args:
            integration_name: CI 整合名稱
            repository: 儲存庫
            branch: 分支
            parameters: 構建參數
            
        Returns:
            觸發結果
        """
        config = self._integrations.get(integration_name)
        if not config:
            return IntegrationResult(
                success=False,
                integration_name=integration_name,
                operation="trigger_ci_build",
                error=f"整合 '{integration_name}' 不存在"
            )

        ci_types = [
            IntegrationType.GITHUB,
            IntegrationType.GITLAB,
            IntegrationType.JENKINS,
            IntegrationType.AZURE_DEVOPS
        ]

        if config.type not in ci_types:
            return IntegrationResult(
                success=False,
                integration_name=integration_name,
                operation="trigger_ci_build",
                error=f"整合類型 '{config.type.value}' 不支援 CI 構建"
            )

        # 模擬觸發構建
        build_payload = {
            "repository": repository,
            "branch": branch,
            "parameters": parameters or {},
            "triggered_at": datetime.now().isoformat()
        }

        return IntegrationResult(
            success=True,
            integration_name=integration_name,
            operation="trigger_ci_build",
            response=build_payload
        )

    def create_issue(self,
                    integration_name: str,
                    title: str,
                    description: str,
                    labels: list[str] | None = None,
                    assignees: list[str] | None = None,
                    priority: str | None = None) -> IntegrationResult:
        """
        建立工單/Issue
        
        Args:
            integration_name: 整合名稱
            title: 標題
            description: 描述
            labels: 標籤
            assignees: 指派人員
            priority: 優先級
            
        Returns:
            建立結果
        """
        config = self._integrations.get(integration_name)
        if not config:
            return IntegrationResult(
                success=False,
                integration_name=integration_name,
                operation="create_issue",
                error=f"整合 '{integration_name}' 不存在"
            )

        issue_types = [
            IntegrationType.GITHUB,
            IntegrationType.GITLAB,
            IntegrationType.JIRA
        ]

        if config.type not in issue_types:
            return IntegrationResult(
                success=False,
                integration_name=integration_name,
                operation="create_issue",
                error=f"整合類型 '{config.type.value}' 不支援工單建立"
            )

        # 格式化工單
        issue_payload = self._format_issue(
            config.type, title, description, labels, assignees, priority
        )

        return IntegrationResult(
            success=True,
            integration_name=integration_name,
            operation="create_issue",
            response=issue_payload
        )

    def _format_issue(self,
                     integration_type: IntegrationType,
                     title: str,
                     description: str,
                     labels: list[str] | None,
                     assignees: list[str] | None,
                     priority: str | None) -> dict[str, Any]:
        """格式化工單"""
        if integration_type == IntegrationType.JIRA:
            return {
                "fields": {
                    "summary": title,
                    "description": description,
                    "labels": labels or [],
                    "assignee": {"name": assignees[0]} if assignees else None,
                    "priority": {"name": priority} if priority else None
                }
            }
        else:  # GitHub/GitLab
            return {
                "title": title,
                "body": description,
                "labels": labels or [],
                "assignees": assignees or []
            }

    # ==================== 報告生成 ====================

    def generate_integration_report(self) -> dict[str, Any]:
        """
        生成整合狀態報告
        
        Returns:
            整合報告
        """
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_integrations": len(self._integrations),
            "enabled_integrations": len([i for i in self._integrations.values() if i.enabled]),
            "integrations_by_type": {},
            "webhook_handlers": {},
            "recent_events": []
        }

        # 按類型統計
        for config in self._integrations.values():
            type_name = config.type.value
            if type_name not in report["integrations_by_type"]:
                report["integrations_by_type"][type_name] = []
            report["integrations_by_type"][type_name].append({
                "name": config.name,
                "enabled": config.enabled,
                "auth_method": config.auth_method.value
            })

        # Webhook 處理器統計
        for event_type, handlers in self._webhook_handlers.items():
            report["webhook_handlers"][event_type] = len(handlers)

        # 最近事件
        report["recent_events"] = [
            {
                "event_type": e.event_type,
                "timestamp": e.timestamp.isoformat()
            }
            for e in self._event_history[-10:]
        ]

        return report

    def format_report_zh_tw(self, report: dict[str, Any]) -> str:
        """
        格式化繁體中文報告
        
        Args:
            report: 報告資料
            
        Returns:
            格式化報告
        """
        lines = [
            "=" * 60,
            "📊 企業整合狀態報告",
            "=" * 60,
            "",
            f"📅 生成時間：{report['generated_at']}",
            f"🔗 總整合數：{report['total_integrations']}",
            f"✅ 已啟用：{report['enabled_integrations']}",
            "",
            "📋 整合類型分佈：",
        ]

        for type_name, integrations in report.get("integrations_by_type", {}).items():
            lines.append(f"  • {type_name}：{len(integrations)} 個")
            for i in integrations:
                status = "✅" if i["enabled"] else "⏸️"
                lines.append(f"    {status} {i['name']} ({i['auth_method']})")

        lines.extend([
            "",
            "🔔 Webhook 處理器：",
        ])

        for event_type, count in report.get("webhook_handlers", {}).items():
            lines.append(f"  • {event_type}：{count} 個處理器")

        if report.get("recent_events"):
            lines.extend([
                "",
                "📨 最近事件：",
            ])
            for event in report["recent_events"]:
                lines.append(f"  • [{event['timestamp']}] {event['event_type']}")

        lines.extend(["", "=" * 60])

        return "\n".join(lines)
