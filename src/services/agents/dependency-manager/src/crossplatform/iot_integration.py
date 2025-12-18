"""
IoT 整合模組
IoT Integration Module

提供邊緣運算、設備互聯、工業 4.0 整合評估
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class EdgeComputingType(Enum):
    """邊緣運算類型"""
    FOG_COMPUTING = "fog"
    MULTI_ACCESS_EDGE = "mec"
    CLOUDLET = "cloudlet"
    EDGE_GATEWAY = "gateway"


class IoTProtocol(Enum):
    """IoT 通訊協議"""
    MQTT = "mqtt"
    COAP = "coap"
    AMQP = "amqp"
    HTTP_REST = "http"
    WEBSOCKET = "websocket"
    LORAWAN = "lorawan"
    ZIGBEE = "zigbee"
    BLUETOOTH_LE = "ble"


class Industry40Component(Enum):
    """工業 4.0 組件"""
    SMART_FACTORY = "smart_factory"
    PREDICTIVE_MAINTENANCE = "predictive_maintenance"
    DIGITAL_TWIN = "digital_twin"
    SUPPLY_CHAIN_4_0 = "supply_chain"
    QUALITY_4_0 = "quality_management"
    ENERGY_MANAGEMENT = "energy_management"


@dataclass
class EdgeComputing:
    """邊緣運算評估"""
    computing_type: EdgeComputingType
    latency_requirement_ms: int
    bandwidth_requirement_mbps: float
    local_processing_percentage: int  # 0-100
    data_privacy_requirement: str  # low, medium, high

    # 評估結果
    suitability_score: float = 0.0
    recommended_type: EdgeComputingType | None = None
    hardware_recommendations: list[str] = field(default_factory=list)
    deployment_considerations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            'computing_type': self.computing_type.value,
            'latency_requirement_ms': self.latency_requirement_ms,
            'bandwidth_requirement_mbps': self.bandwidth_requirement_mbps,
            'local_processing_percentage': self.local_processing_percentage,
            'data_privacy_requirement': self.data_privacy_requirement,
            'suitability_score': self.suitability_score,
            'recommended_type': self.recommended_type.value if self.recommended_type else None,
            'hardware_recommendations': self.hardware_recommendations,
            'deployment_considerations': self.deployment_considerations
        }


@dataclass
class DeviceInterconnection:
    """設備互聯策略"""
    protocol: IoTProtocol
    device_count: int
    message_frequency_hz: float
    security_level: str  # basic, standard, advanced
    scalability_requirement: str  # fixed, moderate, high

    # 策略結果
    throughput_estimate: float = 0.0
    recommended_protocol: IoTProtocol | None = None
    security_measures: list[str] = field(default_factory=list)
    scaling_recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            'protocol': self.protocol.value,
            'device_count': self.device_count,
            'message_frequency_hz': self.message_frequency_hz,
            'security_level': self.security_level,
            'scalability_requirement': self.scalability_requirement,
            'throughput_estimate': self.throughput_estimate,
            'recommended_protocol': self.recommended_protocol.value if self.recommended_protocol else None,
            'security_measures': self.security_measures,
            'scaling_recommendations': self.scaling_recommendations
        }


@dataclass
class Industry40:
    """工業 4.0 整合"""
    component: Industry40Component
    automation_level: int  # 1-5
    data_integration_scope: str  # local, departmental, enterprise
    roi_target_months: int

    # 整合結果
    implementation_complexity: str = "medium"
    estimated_roi: float = 0.0
    key_technologies: list[str] = field(default_factory=list)
    implementation_phases: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            'component': self.component.value,
            'automation_level': self.automation_level,
            'data_integration_scope': self.data_integration_scope,
            'roi_target_months': self.roi_target_months,
            'implementation_complexity': self.implementation_complexity,
            'estimated_roi': self.estimated_roi,
            'key_technologies': self.key_technologies,
            'implementation_phases': self.implementation_phases
        }


class IoTIntegration:
    """IoT 整合評估器"""

    # 邊緣運算特性
    EDGE_SPECS = {
        EdgeComputingType.FOG_COMPUTING: {
            'latency_ms': 10,
            'processing_power': 'high',
            'deployment_cost': 'medium',
            'scalability': 'high'
        },
        EdgeComputingType.MULTI_ACCESS_EDGE: {
            'latency_ms': 5,
            'processing_power': 'very_high',
            'deployment_cost': 'high',
            'scalability': 'very_high'
        },
        EdgeComputingType.CLOUDLET: {
            'latency_ms': 20,
            'processing_power': 'medium',
            'deployment_cost': 'low',
            'scalability': 'medium'
        },
        EdgeComputingType.EDGE_GATEWAY: {
            'latency_ms': 50,
            'processing_power': 'low',
            'deployment_cost': 'very_low',
            'scalability': 'low'
        }
    }

    # 協議特性
    PROTOCOL_SPECS = {
        IoTProtocol.MQTT: {
            'max_throughput': 10000,
            'overhead': 'low',
            'reliability': 'high',
            'security': 'medium'
        },
        IoTProtocol.COAP: {
            'max_throughput': 5000,
            'overhead': 'very_low',
            'reliability': 'medium',
            'security': 'medium'
        },
        IoTProtocol.AMQP: {
            'max_throughput': 50000,
            'overhead': 'medium',
            'reliability': 'very_high',
            'security': 'high'
        },
        IoTProtocol.HTTP_REST: {
            'max_throughput': 1000,
            'overhead': 'high',
            'reliability': 'medium',
            'security': 'high'
        },
        IoTProtocol.LORAWAN: {
            'max_throughput': 100,
            'overhead': 'very_low',
            'reliability': 'medium',
            'security': 'medium'
        }
    }

    def __init__(self):
        self.edge_assessments: list[EdgeComputing] = []
        self.device_strategies: list[DeviceInterconnection] = []
        self.industry40_plans: list[Industry40] = []

    def assess_edge_computing(self, edge: EdgeComputing) -> EdgeComputing:
        """評估邊緣運算方案"""
        specs = self.EDGE_SPECS.get(edge.computing_type, {})
        score = 0.0

        # 延遲匹配
        if specs.get('latency_ms', 100) <= edge.latency_requirement_ms:
            score += 30
        else:
            edge.deployment_considerations.append(
                f"所選方案延遲 ({specs.get('latency_ms')}ms) 可能無法滿足需求 ({edge.latency_requirement_ms}ms)"
            )

        # 本地處理需求
        if edge.local_processing_percentage > 50:
            if specs.get('processing_power') in ['high', 'very_high']:
                score += 25
            else:
                edge.deployment_considerations.append("需要高本地處理能力，建議選擇更強大的邊緣方案")
        else:
            score += 15

        # 隱私需求
        privacy_scores = {'low': 10, 'medium': 20, 'high': 30}
        score += privacy_scores.get(edge.data_privacy_requirement, 15)

        edge.suitability_score = min(100, score)
        edge.recommended_type = self._recommend_edge_type(edge)
        edge.hardware_recommendations = self._generate_hardware_recommendations(edge)

        self.edge_assessments.append(edge)
        return edge

    def _recommend_edge_type(self, edge: EdgeComputing) -> EdgeComputingType:
        """推薦邊緣運算類型"""
        if edge.latency_requirement_ms < 10:
            return EdgeComputingType.MULTI_ACCESS_EDGE
        elif edge.latency_requirement_ms < 30 and edge.local_processing_percentage > 60:
            return EdgeComputingType.FOG_COMPUTING
        elif edge.local_processing_percentage < 30:
            return EdgeComputingType.CLOUDLET
        else:
            return EdgeComputingType.EDGE_GATEWAY

    def _generate_hardware_recommendations(self, edge: EdgeComputing) -> list[str]:
        """生成硬體建議"""
        recommendations = []

        if edge.computing_type == EdgeComputingType.MULTI_ACCESS_EDGE:
            recommendations.extend([
                "NVIDIA Jetson AGX Xavier 或同級",
                "Intel Xeon 處理器邊緣服務器",
                "高速 NVMe 存儲"
            ])
        elif edge.computing_type == EdgeComputingType.FOG_COMPUTING:
            recommendations.extend([
                "Raspberry Pi 4 集群",
                "Intel NUC 邊緣設備",
                "工業級邊緣網關"
            ])
        else:
            recommendations.extend([
                "ARM 架構邊緣設備",
                "工業 IoT 網關",
                "低功耗邊緣處理器"
            ])

        return recommendations

    def evaluate_device_interconnection(self, device: DeviceInterconnection) -> DeviceInterconnection:
        """評估設備互聯策略"""
        specs = self.PROTOCOL_SPECS.get(device.protocol, {})

        # 計算吞吐量估算
        device.throughput_estimate = device.device_count * device.message_frequency_hz

        # 檢查協議是否滿足需求
        max_throughput = specs.get('max_throughput', 1000)
        if device.throughput_estimate > max_throughput:
            device.scaling_recommendations.append(
                f"預估吞吐量 ({device.throughput_estimate}/s) 超過協議上限 ({max_throughput}/s)，建議分區或更換協議"
            )

        # 推薦協議
        device.recommended_protocol = self._recommend_protocol(device)

        # 安全措施
        device.security_measures = self._generate_security_measures(device)

        # 擴展建議
        if device.scalability_requirement == 'high':
            device.scaling_recommendations.extend([
                "實施消息分區策略",
                "部署多個 broker 節點",
                "使用負載均衡機制"
            ])

        self.device_strategies.append(device)
        return device

    def _recommend_protocol(self, device: DeviceInterconnection) -> IoTProtocol:
        """推薦通訊協議"""
        if device.device_count > 10000:
            return IoTProtocol.AMQP
        elif device.message_frequency_hz > 10:
            return IoTProtocol.MQTT
        elif device.security_level == 'advanced':
            return IoTProtocol.AMQP
        else:
            return IoTProtocol.MQTT

    def _generate_security_measures(self, device: DeviceInterconnection) -> list[str]:
        """生成安全措施"""
        measures = ["設備身份認證", "傳輸加密 (TLS)"]

        if device.security_level == 'standard':
            measures.extend([
                "訪問控制列表 (ACL)",
                "消息完整性驗證"
            ])
        elif device.security_level == 'advanced':
            measures.extend([
                "設備證書管理 (PKI)",
                "端到端加密",
                "入侵檢測系統",
                "安全啟動驗證"
            ])

        return measures

    def plan_industry40(self, plan: Industry40) -> Industry40:
        """規劃工業 4.0 實施"""
        # 實施複雜度評估
        complexity_map = {
            Industry40Component.SMART_FACTORY: 'high',
            Industry40Component.PREDICTIVE_MAINTENANCE: 'medium',
            Industry40Component.DIGITAL_TWIN: 'very_high',
            Industry40Component.SUPPLY_CHAIN_4_0: 'high',
            Industry40Component.QUALITY_4_0: 'medium',
            Industry40Component.ENERGY_MANAGEMENT: 'low'
        }
        plan.implementation_complexity = complexity_map.get(plan.component, 'medium')

        # ROI 估算
        roi_multipliers = {
            Industry40Component.SMART_FACTORY: 2.5,
            Industry40Component.PREDICTIVE_MAINTENANCE: 3.0,
            Industry40Component.DIGITAL_TWIN: 2.0,
            Industry40Component.SUPPLY_CHAIN_4_0: 2.2,
            Industry40Component.QUALITY_4_0: 2.8,
            Industry40Component.ENERGY_MANAGEMENT: 3.5
        }
        base_roi = roi_multipliers.get(plan.component, 2.0)
        automation_bonus = plan.automation_level * 0.1
        plan.estimated_roi = (base_roi + automation_bonus) * 100  # 百分比

        # 關鍵技術
        plan.key_technologies = self._get_key_technologies(plan.component)

        # 實施階段
        plan.implementation_phases = self._generate_implementation_phases(plan)

        self.industry40_plans.append(plan)
        return plan

    def _get_key_technologies(self, component: Industry40Component) -> list[str]:
        """獲取關鍵技術"""
        technologies = {
            Industry40Component.SMART_FACTORY: [
                "工業物聯網 (IIoT)",
                "機器人流程自動化 (RPA)",
                "人工智能與機器學習",
                "5G 工業網絡"
            ],
            Industry40Component.PREDICTIVE_MAINTENANCE: [
                "振動分析傳感器",
                "機器學習預測模型",
                "CMMS 系統整合",
                "即時監控儀表板"
            ],
            Industry40Component.DIGITAL_TWIN: [
                "3D 建模與模擬",
                "即時數據同步",
                "物理-數位映射引擎",
                "可視化平台"
            ],
            Industry40Component.SUPPLY_CHAIN_4_0: [
                "區塊鏈追溯",
                "RFID/NFC 追蹤",
                "需求預測 AI",
                "倉儲自動化"
            ],
            Industry40Component.QUALITY_4_0: [
                "機器視覺檢測",
                "統計過程控制 (SPC)",
                "自動缺陷分類",
                "品質數據分析"
            ],
            Industry40Component.ENERGY_MANAGEMENT: [
                "智能電表",
                "能源監控系統",
                "需求響應管理",
                "可再生能源整合"
            ]
        }
        return technologies.get(component, [])

    def _generate_implementation_phases(self, plan: Industry40) -> list[str]:
        """生成實施階段"""
        phases = [
            "第一階段：現況評估與需求分析 (1-2 個月)",
            "第二階段：技術選型與架構設計 (2-3 個月)",
            "第三階段：試點部署與驗證 (3-4 個月)",
            "第四階段：全面推廣與優化 (4-6 個月)",
            "第五階段：持續改進與創新 (持續)"
        ]

        if plan.data_integration_scope == 'enterprise':
            phases.insert(2, "附加階段：企業系統整合 (2-3 個月)")

        return phases

    def generate_iot_report(self) -> dict[str, Any]:
        """生成 IoT 整合報告"""
        return {
            'generated_at': datetime.now().isoformat(),
            'edge_computing_assessments': [e.to_dict() for e in self.edge_assessments],
            'device_interconnection_strategies': [d.to_dict() for d in self.device_strategies],
            'industry40_plans': [p.to_dict() for p in self.industry40_plans],
            'summary': {
                'total_edge_assessments': len(self.edge_assessments),
                'total_device_strategies': len(self.device_strategies),
                'total_industry40_plans': len(self.industry40_plans),
                'avg_edge_suitability': sum(e.suitability_score for e in self.edge_assessments) / len(self.edge_assessments) if self.edge_assessments else 0,
                'avg_estimated_roi': sum(p.estimated_roi for p in self.industry40_plans) / len(self.industry40_plans) if self.industry40_plans else 0
            }
        }
