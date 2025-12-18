#!/usr/bin/env python3
"""
SynergyMesh Governance - Dimension Generator
Machine-First Governance Framework (00-80 Dimensions)
Generates standardized dimension modules with YAML, JSON Schema, and Rego policies
"""

import os
import json
from datetime import datetime

# Dimension definitions (00-80)
DIMENSIONS = [
    # Strategic Layer (00-09)
    ("00", "vision-strategy", "願景策略治理", "Vision Strategy Governance", "組織願景、策略目標與長期規劃治理", ["vision", "strategy", "planning", "objectives"], "strategic", []),
    ("01", "architecture", "架構治理", "Architecture Governance", "企業架構、技術架構與治理框架設計", ["architecture", "design", "framework", "patterns"], "strategic", ["00-vision-strategy"]),
    ("02", "decision", "決策治理", "Decision Governance", "決策流程、審批機制與決策追蹤", ["decision", "approval", "workflow", "tracking"], "strategic", ["00-vision-strategy", "01-architecture"]),
    ("03", "change", "變更治理", "Change Governance", "變更管理、版本控制與影響評估", ["change", "version", "impact", "management"], "strategic", ["02-decision"]),
    ("04", "risk", "風險治理", "Risk Governance", "風險識別、評估、緩解與監控", ["risk", "assessment", "mitigation", "monitoring"], "strategic", ["00-vision-strategy"]),
    ("05", "compliance", "合規治理", "Compliance Governance", "法規遵循、標準符合與合規驗證", ["compliance", "regulation", "standard", "verification"], "strategic", ["04-risk"]),
    ("06", "security", "安全治理", "Security Governance", "資訊安全、存取控制與威脅管理", ["security", "access", "threat", "protection"], "strategic", ["04-risk", "05-compliance"]),
    ("07", "audit", "稽核治理", "Audit Governance", "稽核流程、證據收集與報告生成", ["audit", "evidence", "report", "trail"], "strategic", ["05-compliance", "06-security"]),
    ("08", "process", "流程治理", "Process Governance", "流程定義、優化與自動化", ["process", "workflow", "optimization", "automation"], "strategic", ["01-architecture"]),
    ("09", "performance", "績效治理", "Performance Governance", "績效指標、KPI定義與目標追蹤", ["performance", "kpi", "metrics", "goals"], "strategic", ["00-vision-strategy", "08-process"]),

    # Operational Layer (10-29)
    ("10", "policy", "政策治理", "Policy Governance", "Policy-as-Code框架、政策定義與執行", ["policy", "rules", "enforcement", "pac"], "operational", ["00-vision-strategy", "05-compliance"]),
    ("11", "tools-systems", "工具系統治理", "Tools Systems Governance", "治理工具、系統整合與平台管理", ["tools", "systems", "platform", "integration"], "operational", ["01-architecture"]),
    ("12", "culture-capability", "文化能力治理", "Culture Capability Governance", "組織文化、能力建設與培訓治理", ["culture", "capability", "training", "competency"], "operational", ["00-vision-strategy"]),
    ("13", "metrics-reporting", "指標報告治理", "Metrics Reporting Governance", "指標定義、數據收集與報告生成", ["metrics", "reporting", "dashboard", "analytics"], "operational", ["09-performance"]),
    ("14", "improvement", "改善治理", "Improvement Governance", "持續改善、PDCA循環與優化治理", ["improvement", "pdca", "optimization", "continuous"], "operational", ["08-process", "09-performance"]),
    ("15", "economic", "經濟治理", "Economic Governance", "成本管理、預算控制與經濟效益治理", ["economic", "cost", "budget", "roi"], "operational", ["00-vision-strategy", "04-risk"]),
    ("16", "psychological", "心理治理", "Psychological Governance", "認知負荷、心理安全與使用者體驗治理", ["psychological", "cognitive", "safety", "ux"], "operational", ["12-culture-capability"]),
    ("17", "sociological", "社會學治理", "Sociological Governance", "社會互動、協作模式與組織行為治理", ["sociological", "collaboration", "interaction", "behavior"], "operational", ["12-culture-capability"]),
    ("18", "complex-system", "複雜系統治理", "Complex System Governance", "複雜適應系統、湧現行為與系統動力學治理", ["complex", "system", "emergence", "dynamics"], "operational", ["01-architecture", "04-risk"]),
    ("19", "evolutionary", "演化治理", "Evolutionary Governance", "演化架構、適應性變化與治理演進", ["evolutionary", "adaptive", "evolution", "fitness"], "operational", ["14-improvement", "18-complex-system"]),
    ("20", "intent", "意圖治理", "Intent Governance", "Intent-based Orchestration、語意映射與自動執行", ["intent", "orchestration", "semantic", "automation"], "operational", ["10-policy", "01-architecture"]),
    ("21", "ecological", "生態治理", "Ecological Governance", "環境考量、永續發展與綠色IT治理", ["ecological", "sustainability", "green", "environment"], "operational", ["00-vision-strategy"]),
    ("22", "aesthetic", "美學治理", "Aesthetic Governance", "設計美學、使用者介面與體驗治理", ["aesthetic", "design", "ui", "experience"], "operational", ["16-psychological"]),
    ("23", "policies", "政策定義", "Policy Definitions", "具體政策規則、例外處理與政策模板", ["policies", "rules", "templates", "exceptions"], "operational", ["10-policy"]),
    ("24", "registry", "登錄治理", "Registry Governance", "元件登錄、服務目錄與依賴管理", ["registry", "catalog", "dependencies", "discovery"], "operational", ["01-architecture"]),
    ("25", "principles", "原則治理", "Principles Governance", "治理原則、指導方針與價值觀定義", ["principles", "guidelines", "values", "standards"], "operational", ["00-vision-strategy"]),
    ("26", "tools", "工具治理", "Tools Governance", "治理工具集、自動化腳本與輔助程式", ["tools", "scripts", "utilities", "automation"], "operational", ["11-tools-systems"]),
    ("27", "templates", "模板治理", "Templates Governance", "配置模板、標準範本與快速啟動", ["templates", "boilerplate", "quickstart", "standards"], "operational", ["01-architecture"]),
    ("28", "tests", "測試治理", "Tests Governance", "測試框架、驗證策略與品質保證", ["tests", "validation", "qa", "verification"], "operational", ["07-audit"]),
    ("29", "docs", "文檔治理", "Documentation Governance", "文檔標準、知識管理與內容治理", ["docs", "documentation", "knowledge", "content"], "operational", ["00-vision-strategy"]),

    # Execution Layer (30-49)
    ("30", "agents", "代理治理", "Agents Governance", "AI Agent生命週期、權限管理與合規追蹤", ["agents", "ai", "lifecycle", "permissions"], "execution", ["10-policy", "20-intent"]),
    ("31", "schemas", "結構治理", "Schemas Governance", "JSON Schema、資料結構與驗證規則", ["schemas", "validation", "structure", "types"], "execution", ["01-architecture"]),
    ("32", "rules", "規則治理", "Rules Governance", "業務規則、決策邏輯與規則引擎", ["rules", "logic", "engine", "decision"], "execution", ["10-policy", "23-policies"]),
    ("33", "common", "共用治理", "Common Governance", "共用元件、工具函式與基礎設施", ["common", "shared", "utilities", "infrastructure"], "execution", []),
    ("34", "config", "配置治理", "Config Governance", "配置管理、環境變數與參數化設定", ["config", "environment", "parameters", "settings"], "execution", ["27-templates"]),
    ("35", "scripts", "腳本治理", "Scripts Governance", "自動化腳本、批次作業與任務執行", ["scripts", "automation", "batch", "tasks"], "execution", ["26-tools"]),
    ("36", "modules", "模組治理", "Modules Governance", "模組定義、介面規範與依賴管理", ["modules", "interface", "dependencies", "packaging"], "execution", ["01-architecture", "24-registry"]),
    ("37", "behavior-contracts", "行為契約治理", "Behavior Contracts Governance", "行為契約、不變量定義與副作用聲明", ["contracts", "behavior", "invariants", "effects"], "execution", ["30-agents", "36-modules"]),
    ("38", "sbom", "軟體物料清單治理", "SBOM Governance", "軟體供應鏈、來源追蹤與簽章驗證", ["sbom", "supply-chain", "provenance", "signing"], "execution", ["06-security", "05-compliance"]),
    ("39", "automation", "自動化治理", "Automation Governance", "自動化引擎、任務調度與工作流程", ["automation", "engine", "scheduling", "workflow"], "execution", ["08-process", "35-scripts"]),
    ("40", "self-healing", "自癒治理", "Self-Healing Governance", "自動復原、故障偵測與預防性維護", ["self-healing", "recovery", "detection", "prevention"], "execution", ["39-automation", "04-risk"]),
    ("41", "orchestration", "編排治理", "Orchestration Governance", "服務編排、容器調度與資源管理", ["orchestration", "kubernetes", "containers", "resources"], "execution", ["20-intent", "39-automation"]),
    ("42", "deployment", "部署治理", "Deployment Governance", "部署策略、發布管理與環境管理", ["deployment", "release", "environment", "strategy"], "execution", ["41-orchestration", "03-change"]),
    ("43", "scaling", "擴展治理", "Scaling Governance", "自動擴展、容量規劃與資源優化", ["scaling", "autoscaling", "capacity", "optimization"], "execution", ["41-orchestration", "09-performance"]),
    ("44", "resilience", "韌性治理", "Resilience Governance", "系統韌性、故障容忍與災難復原", ["resilience", "fault-tolerance", "disaster-recovery"], "execution", ["04-risk", "40-self-healing"]),
    ("45", "recovery", "復原治理", "Recovery Governance", "備份策略、復原程序與RTO/RPO管理", ["recovery", "backup", "rto", "rpo"], "execution", ["44-resilience", "40-self-healing"]),
    ("46", "migration", "遷移治理", "Migration Governance", "資料遷移、系統遷移與現代化治理", ["migration", "modernization", "data", "system"], "execution", ["03-change", "42-deployment"]),
    ("47", "versioning", "版本治理", "Versioning Governance", "語意版本控制、相容性管理與棄用策略", ["versioning", "semver", "compatibility", "deprecation"], "execution", ["03-change", "36-modules"]),
    ("48", "rollback", "回滾治理", "Rollback Governance", "回滾策略、狀態恢復與安全回退", ["rollback", "revert", "recovery", "safety"], "execution", ["42-deployment", "47-versioning"]),
    ("49", "canary", "金絲雀治理", "Canary Governance", "金絲雀部署、漸進式發布與A/B測試", ["canary", "progressive", "ab-testing", "rollout"], "execution", ["42-deployment", "43-scaling"]),

    # Observability Layer (50-69)
    ("50", "monitoring", "監控治理", "Monitoring Governance", "系統監控、指標收集與健康檢查", ["monitoring", "metrics", "health", "observability"], "observability", ["09-performance"]),
    ("51", "logging", "日誌治理", "Logging Governance", "結構化日誌、日誌聚合與保留策略", ["logging", "structured", "aggregation", "retention"], "observability", ["07-audit"]),
    ("52", "tracing", "追蹤治理", "Tracing Governance", "分散式追蹤、span收集與因果關係", ["tracing", "distributed", "spans", "causality"], "observability", ["50-monitoring"]),
    ("53", "alerting", "告警治理", "Alerting Governance", "告警規則、通知管道與告警疲勞管理", ["alerting", "notifications", "rules", "fatigue"], "observability", ["50-monitoring", "04-risk"]),
    ("54", "dashboards", "儀表板治理", "Dashboards Governance", "儀表板設計、視覺化標準與即時展示", ["dashboards", "visualization", "grafana", "display"], "observability", ["50-monitoring", "13-metrics-reporting"]),
    ("55", "slo-sli", "SLO/SLI治理", "SLO SLI Governance", "服務等級目標、指標定義與錯誤預算", ["slo", "sli", "sla", "error-budget"], "observability", ["09-performance", "50-monitoring"]),
    ("56", "incidents", "事件治理", "Incidents Governance", "事件管理、分類分級與響應流程", ["incidents", "response", "classification", "management"], "observability", ["53-alerting", "04-risk"]),
    ("57", "postmortems", "事後分析治理", "Postmortems Governance", "事後分析、根因分析與改善行動", ["postmortems", "rca", "blameless", "improvement"], "observability", ["56-incidents", "14-improvement"]),
    ("58", "capacity", "容量治理", "Capacity Governance", "容量規劃、資源預測與成本優化", ["capacity", "planning", "prediction", "optimization"], "observability", ["43-scaling", "50-monitoring"]),
    ("59", "forecasting", "預測治理", "Forecasting Governance", "趨勢預測、異常預警與容量預估", ["forecasting", "trends", "anomaly", "prediction"], "observability", ["58-capacity", "13-metrics-reporting"]),
    ("60", "contracts", "契約治理", "Contracts Governance", "契約登錄、介面驗證與相容性檢查", ["contracts", "interface", "compatibility", "registry"], "observability", ["37-behavior-contracts", "36-modules"]),
    ("61", "lineage", "血緣治理", "Lineage Governance", "資料血緣、依賴追蹤與影響分析", ["lineage", "data", "dependencies", "impact"], "observability", ["07-audit", "52-tracing"]),
    ("62", "provenance", "來源治理", "Provenance Governance", "來源追蹤、版本歷史與變更記錄", ["provenance", "origin", "history", "tracking"], "observability", ["38-sbom", "61-lineage"]),
    ("63", "evidence", "證據治理", "Evidence Governance", "證據收集、證據鏈與不可變儲存", ["evidence", "chain", "immutable", "collection"], "observability", ["07-audit", "62-provenance"]),
    ("64", "attestation", "認證治理", "Attestation Governance", "數位簽章、認證聲明與信任驗證", ["attestation", "signature", "trust", "verification"], "observability", ["63-evidence", "06-security"]),
    ("65", "certification", "驗證治理", "Certification Governance", "合規驗證、標準認證與持續合規", ["certification", "compliance", "standards", "continuous"], "observability", ["05-compliance", "64-attestation"]),
    ("66", "reporting", "報告治理", "Reporting Governance", "自動報告生成、排程與分發", ["reporting", "generation", "scheduling", "distribution"], "observability", ["13-metrics-reporting", "07-audit"]),
    ("67", "analytics", "分析治理", "Analytics Governance", "資料分析、洞察發現與決策支援", ["analytics", "insights", "decision-support", "data"], "observability", ["50-monitoring", "59-forecasting"]),
    ("68", "visualization", "視覺化治理", "Visualization Governance", "資料視覺化、圖表標準與互動展示", ["visualization", "charts", "interactive", "display"], "observability", ["54-dashboards", "67-analytics"]),
    ("69", "correlation", "關聯治理", "Correlation Governance", "事件關聯、因果分析與模式識別", ["correlation", "causality", "patterns", "analysis"], "observability", ["52-tracing", "67-analytics"]),

    # Feedback Layer (70-80)
    ("70", "audit-trail", "稽核軌跡治理", "Audit Trail Governance", "完整稽核軌跡、時間戳與不可變記錄", ["audit-trail", "timestamp", "immutable", "records"], "feedback", ["07-audit", "63-evidence"]),
    ("71", "feedback-loops", "回饋迴路治理", "Feedback Loops Governance", "閉環回饋、持續監控與自動調整", ["feedback", "loops", "closed-loop", "adjustment"], "feedback", ["14-improvement", "50-monitoring"]),
    ("72", "optimization", "優化治理", "Optimization Governance", "效能優化、資源優化與成本優化", ["optimization", "performance", "resources", "cost"], "feedback", ["71-feedback-loops", "67-analytics"]),
    ("73", "learning", "學習治理", "Learning Governance", "機器學習、模型訓練與知識積累", ["learning", "ml", "training", "knowledge"], "feedback", ["72-optimization", "30-agents"]),
    ("74", "adaptation", "適應治理", "Adaptation Governance", "自適應調整、動態配置與環境適應", ["adaptation", "dynamic", "environment", "adjustment"], "feedback", ["73-learning", "19-evolutionary"]),
    ("75", "evolution", "演化治理", "Evolution Governance", "系統演化、架構演進與治理進化", ["evolution", "architecture", "progression", "fitness"], "feedback", ["74-adaptation", "19-evolutionary"]),
    ("76", "innovation", "創新治理", "Innovation Governance", "創新管理、實驗文化與新興技術治理", ["innovation", "experimentation", "emerging", "technology"], "feedback", ["75-evolution", "00-vision-strategy"]),
    ("77", "experimentation", "實驗治理", "Experimentation Governance", "A/B測試、特徵標誌與實驗框架", ["experimentation", "ab-testing", "feature-flags", "framework"], "feedback", ["76-innovation", "49-canary"]),
    ("78", "simulation", "模擬治理", "Simulation Governance", "數位孿生、場景模擬與what-if分析", ["simulation", "digital-twin", "scenarios", "what-if"], "feedback", ["77-experimentation", "18-complex-system"]),
    ("79", "prediction", "預測治理", "Prediction Governance", "預測模型、趨勢分析與前瞻性治理", ["prediction", "models", "trends", "proactive"], "feedback", ["59-forecasting", "73-learning"]),
    ("80", "synthesis", "綜合治理", "Synthesis Governance", "跨維度綜合、整體優化與治理整合", ["synthesis", "integration", "holistic", "optimization"], "feedback", ["79-prediction", "00-vision-strategy"]),
]

BASE_DIR = "/home/user/SynergyMesh/governance/dimensions"
TIMESTAMP = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

def generate_dimension_yaml(dim_id, name, name_zh, name_en, description, tags, category, dependencies):
    """Generate dimension.yaml content"""
    return f'''# =============================================================================
# SynergyMesh Governance - Dimension Module
# {dim_id}-{name}: {name_en}
# =============================================================================
# Machine-First Format: YAML
# Validation: JSON Schema Enforced
# =============================================================================

apiVersion: governance.synergymesh.io/v2
kind: DimensionModule
metadata:
  id: "{dim_id}-{name}"
  name: "{name_zh}"
  name_en: "{name_en}"
  version: "1.0.0"
  created_at: "{TIMESTAMP}"
  updated_at: "{TIMESTAMP}"
  owner: governance-bot
  category: {category}
  tags: {json.dumps(tags)}

spec:
  description: "{description}"

  # Schema reference
  schema:
    path: "./schema.json"
    format: json-schema
    validation: required

  # Policy reference
  policy:
    path: "./policy.rego"
    engine: opa
    enforcement: required

  # Dependencies
  dependencies:
    required: {json.dumps(dependencies)}
    optional: []

  # Interface definition
  interface:
    inputs:
      - name: config
        type: object
        required: true
        schema_ref: "#/definitions/config"
      - name: context
        type: object
        required: false
        schema_ref: "#/definitions/context"
    outputs:
      - name: result
        type: object
        schema_ref: "#/definitions/result"
      - name: audit_log
        type: object
        schema_ref: "#/definitions/audit_log"
    errors:
      - code: "E{dim_id}001"
        name: "ValidationError"
        description: "Input validation failed"
      - code: "E{dim_id}002"
        name: "PolicyViolation"
        description: "Policy check failed"
      - code: "E{dim_id}003"
        name: "DependencyError"
        description: "Required dependency unavailable"

  # Behavior contracts
  behavior:
    invariants:
      - "All operations must be auditable"
      - "State changes require validation"
      - "Dependencies must be satisfied"
    preconditions:
      - "Input must conform to schema"
      - "Required dependencies available"
    postconditions:
      - "Output conforms to schema"
      - "Audit log generated"
    side_effects:
      - "Generates audit trail"
      - "May update metrics"

  # Lifecycle management
  lifecycle:
    states:
      - pending
      - initializing
      - active
      - degraded
      - maintenance
      - retiring
      - retired
    transitions:
      - from: pending
        to: initializing
        trigger: initialize
      - from: initializing
        to: active
        trigger: activation_complete
      - from: active
        to: degraded
        trigger: health_check_failed
      - from: degraded
        to: active
        trigger: recovery_complete
      - from: active
        to: maintenance
        trigger: maintenance_start
      - from: maintenance
        to: active
        trigger: maintenance_complete
      - from: active
        to: retiring
        trigger: deprecation_start
      - from: retiring
        to: retired
        trigger: retirement_complete

  # Metrics
  metrics:
    - name: "{name}_operations_total"
      type: counter
      description: "Total operations executed"
    - name: "{name}_operation_duration_seconds"
      type: histogram
      description: "Operation duration in seconds"
    - name: "{name}_errors_total"
      type: counter
      description: "Total errors encountered"
    - name: "{name}_health_status"
      type: gauge
      description: "Current health status (0=unhealthy, 1=healthy)"

  # Compliance
  compliance:
    frameworks:
      - ISO-42001
      - NIST-AI-RMF
      - COBIT-2019
    controls: []
    audit_frequency: continuous

status: active
'''

def generate_schema_json(dim_id, name, name_en, description, tags):
    """Generate schema.json content"""
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$id": f"https://synergymesh.io/governance/dimensions/{dim_id}-{name}/schema.json",
        "title": f"{name_en} Schema",
        "description": description,
        "type": "object",
        "definitions": {
            "config": {
                "type": "object",
                "description": f"Configuration for {name_en}",
                "properties": {
                    "enabled": {
                        "type": "boolean",
                        "description": "Whether this dimension is enabled",
                        "default": True
                    },
                    "mode": {
                        "type": "string",
                        "description": "Operating mode",
                        "enum": ["strict", "permissive", "audit"],
                        "default": "strict"
                    },
                    "settings": {
                        "type": "object",
                        "description": "Dimension-specific settings",
                        "additionalProperties": True
                    }
                },
                "required": ["enabled"]
            },
            "context": {
                "type": "object",
                "description": "Execution context",
                "properties": {
                    "trace_id": {
                        "type": "string",
                        "description": "Distributed trace ID"
                    },
                    "actor": {
                        "type": "object",
                        "description": "Actor information",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["human", "ai_agent", "system"]
                            },
                            "id": {
                                "type": "string"
                            }
                        }
                    },
                    "timestamp": {
                        "type": "string",
                        "format": "date-time"
                    }
                }
            },
            "result": {
                "type": "object",
                "description": "Operation result",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "description": "Whether operation succeeded"
                    },
                    "data": {
                        "type": "object",
                        "description": "Result data"
                    },
                    "errors": {
                        "type": "array",
                        "description": "Error details if any",
                        "items": {
                            "type": "object",
                            "properties": {
                                "code": {"type": "string"},
                                "message": {"type": "string"}
                            }
                        }
                    }
                },
                "required": ["success"]
            },
            "audit_log": {
                "type": "object",
                "description": "Audit log entry",
                "properties": {
                    "log_id": {
                        "type": "string",
                        "description": "Unique log identifier"
                    },
                    "trace_id": {
                        "type": "string",
                        "description": "Distributed trace ID"
                    },
                    "timestamp": {
                        "type": "string",
                        "format": "date-time"
                    },
                    "dimension": {
                        "type": "string",
                        "const": f"{dim_id}-{name}"
                    },
                    "action": {
                        "type": "string",
                        "description": "Action performed"
                    },
                    "actor": {
                        "$ref": "#/definitions/context/properties/actor"
                    },
                    "outcome": {
                        "type": "string",
                        "enum": ["success", "failure", "partial"]
                    },
                    "details": {
                        "type": "object"
                    }
                },
                "required": ["log_id", "timestamp", "dimension", "action", "outcome"]
            }
        },
        "properties": {
            "id": {
                "type": "string",
                "description": "Resource identifier",
                "pattern": f"^{dim_id}-{name}-[a-z0-9-]+$"
            },
            "name": {
                "type": "string",
                "description": "Resource name"
            },
            "config": {
                "$ref": "#/definitions/config"
            },
            "status": {
                "type": "string",
                "description": "Current status",
                "enum": ["pending", "active", "inactive", "error", "deprecated"]
            },
            "metadata": {
                "type": "object",
                "properties": {
                    "created_at": {
                        "type": "string",
                        "format": "date-time"
                    },
                    "updated_at": {
                        "type": "string",
                        "format": "date-time"
                    },
                    "version": {
                        "type": "string",
                        "pattern": "^\\d+\\.\\d+\\.\\d+$"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            }
        },
        "required": ["id", "status"],
        "additionalProperties": False
    }
    return json.dumps(schema, indent=2, ensure_ascii=False)

def generate_policy_rego(dim_id, name, name_en, tags):
    """Generate policy.rego content"""
    package_name = name.replace("-", "_")
    return f'''# =============================================================================
# SynergyMesh Governance - {name_en} Policy
# Dimension: {dim_id}-{name}
# =============================================================================
# Policy Engine: OPA (Open Policy Agent)
# Language: Rego
# =============================================================================

package governance.{package_name}

import future.keywords.in
import future.keywords.if
import future.keywords.contains

# =============================================================================
# DEFAULT DENY
# =============================================================================
default allow := false
default compliant := false

# =============================================================================
# METADATA
# =============================================================================
metadata := {{
    "dimension_id": "{dim_id}-{name}",
    "dimension_name": "{name_en}",
    "version": "1.0.0",
    "tags": {json.dumps(tags)}
}}

# =============================================================================
# ALLOW RULES
# =============================================================================

# Allow if all validation rules pass
allow if {{
    valid_input
    valid_config
    no_policy_violations
}}

# =============================================================================
# COMPLIANCE RULES
# =============================================================================

# Resource is compliant if all compliance checks pass
compliant if {{
    allow
    audit_trail_exists
    dependencies_satisfied
}}

# =============================================================================
# VALIDATION RULES
# =============================================================================

# Input validation
valid_input if {{
    input.id
    input.status
}}

# Configuration validation
valid_config if {{
    input.config.enabled != null
}}

# Default for missing config
valid_config if {{
    not input.config
}}

# =============================================================================
# POLICY VIOLATION CHECKS
# =============================================================================

# No violations if violations set is empty
no_policy_violations if {{
    count(violations) == 0
}}

# Collect all violations
violations contains msg if {{
    not input.id
    msg := "Resource ID is required"
}}

violations contains msg if {{
    not input.status
    msg := "Resource status is required"
}}

violations contains msg if {{
    input.status == "error"
    not input.error_details
    msg := "Error status requires error_details"
}}

# =============================================================================
# AUDIT RULES
# =============================================================================

# Audit trail exists (always true for new resources)
audit_trail_exists if {{
    input.metadata.created_at
}}

# Default audit trail for resources without metadata
audit_trail_exists if {{
    not input.metadata
}}

# =============================================================================
# DEPENDENCY RULES
# =============================================================================

# Dependencies are satisfied if all required deps are available
dependencies_satisfied if {{
    # Placeholder: check dependencies in context
    true
}}

# =============================================================================
# ENFORCEMENT ACTIONS
# =============================================================================

# Deny response with reasons
deny[reason] if {{
    violation := violations[_]
    reason := {{
        "code": "E{dim_id}001",
        "dimension": "{dim_id}-{name}",
        "message": violation
    }}
}}

# =============================================================================
# AUDIT LOG GENERATION
# =============================================================================

audit_entry := {{
    "dimension": "{dim_id}-{name}",
    "timestamp": time.now_ns(),
    "input_id": input.id,
    "decision": {{
        "allow": allow,
        "compliant": compliant,
        "violations": violations
    }}
}}

# =============================================================================
# METRICS
# =============================================================================

metrics := {{
    "policy_evaluations": 1,
    "violations_count": count(violations),
    "compliant": compliant
}}
'''

def generate_test_rego(dim_id, name, name_en):
    """Generate test file content"""
    package_name = name.replace("-", "_")
    return f'''# =============================================================================
# SynergyMesh Governance - {name_en} Policy Tests
# Dimension: {dim_id}-{name}
# =============================================================================

package governance.{package_name}_test

import data.governance.{package_name}

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {{
    {package_name}.allow with input as {{
        "id": "{dim_id}-{name}-test-001",
        "status": "active",
        "config": {{
            "enabled": true
        }}
    }}
}}

test_deny_missing_id {{
    not {package_name}.allow with input as {{
        "status": "active"
    }}
}}

test_deny_missing_status {{
    not {package_name}.allow with input as {{
        "id": "{dim_id}-{name}-test-001"
    }}
}}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {{
    {package_name}.compliant with input as {{
        "id": "{dim_id}-{name}-test-001",
        "status": "active",
        "config": {{
            "enabled": true
        }},
        "metadata": {{
            "created_at": "2025-12-11T00:00:00Z"
        }}
    }}
}}

# =============================================================================
# TEST: VIOLATION RULES
# =============================================================================

test_violations_empty_for_valid {{
    violations := {package_name}.violations with input as {{
        "id": "{dim_id}-{name}-test-001",
        "status": "active"
    }}
    count(violations) == 0
}}

test_violations_for_error_without_details {{
    violations := {package_name}.violations with input as {{
        "id": "{dim_id}-{name}-test-001",
        "status": "error"
    }}
    count(violations) > 0
}}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {{
    {package_name}.metadata.dimension_id == "{dim_id}-{name}"
}}

test_metadata_version {{
    {package_name}.metadata.version == "1.0.0"
}}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {{
    entry := {package_name}.audit_entry with input as {{
        "id": "{dim_id}-{name}-test-001",
        "status": "active"
    }}
    entry.dimension == "{dim_id}-{name}"
}}
'''

def main():
    """Generate all dimension modules"""
    print(f"Generating {len(DIMENSIONS)} dimension modules...")

    for dim in DIMENSIONS:
        dim_id, name, name_zh, name_en, description, tags, category, dependencies = dim
        dir_path = os.path.join(BASE_DIR, f"{dim_id}-{name}")
        tests_path = os.path.join(dir_path, "tests")

        # Create directories
        os.makedirs(tests_path, exist_ok=True)

        # Generate dimension.yaml
        with open(os.path.join(dir_path, "dimension.yaml"), "w", encoding="utf-8") as f:
            f.write(generate_dimension_yaml(dim_id, name, name_zh, name_en, description, tags, category, dependencies))

        # Generate schema.json
        with open(os.path.join(dir_path, "schema.json"), "w", encoding="utf-8") as f:
            f.write(generate_schema_json(dim_id, name, name_en, description, tags))

        # Generate policy.rego
        with open(os.path.join(dir_path, "policy.rego"), "w", encoding="utf-8") as f:
            f.write(generate_policy_rego(dim_id, name, name_en, tags))

        # Generate test file
        with open(os.path.join(tests_path, f"{name.replace('-', '_')}_test.rego"), "w", encoding="utf-8") as f:
            f.write(generate_test_rego(dim_id, name, name_en))

        print(f"  Generated: {dim_id}-{name}")

    print(f"\nCompleted! Generated {len(DIMENSIONS)} dimension modules.")

if __name__ == "__main__":
    main()
