"""
API 規格與治理邊界定義
- 定義模組間的調用契約
- 強制語言邊界一致性
- 提供自動化驗證
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List
import json

class ModuleRole(Enum):
    """模組責任分類"""
    SENSOR_FUSION = "sensor_fusion"
    FLIGHT_CONTROL = "flight_control"
    NAVIGATION = "navigation"
    SAFETY_MONITOR = "safety_monitor"
    OBSERVABILITY = "observability"

class ErrorCategory(Enum):
    """錯誤分類"""
    SENSOR_ERROR = "sensor_error"
    CONTROL_ERROR = "control_error"
    NAVIGATION_ERROR = "navigation_error"
    SAFETY_VIOLATION = "safety_violation"
    SYSTEM_ERROR = "system_error"

@dataclass
class APIContract:
    """API 契約定義"""
    module_name: str
    module_role: ModuleRole
    input_schema: Dict
    output_schema: Dict
    max_latency_ms: float
    error_handling: Dict[ErrorCategory, str]
    dependencies: List[str]

class GovernanceValidator:
    """治理邊界驗證器"""
    
    def __init__(self):
        self.contracts: Dict[str, APIContract] = {}
        self.load_contracts()
    
    def load_contracts(self):
        """載入所有 API 契約"""
        contracts_data = {
            "sensor_fusion": APIContract(
                module_name="sensor_fusion",
                module_role=ModuleRole.SENSOR_FUSION,
                input_schema={
                    "type": "object",
                    "properties": {
                        "imu_data": {"type": "object"},
                        "gps_data": {"type": "object"}
                    }
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "fused_state": {"type": "object"},
                        "confidence": {"type": "number"}
                    }
                },
                max_latency_ms=50.0,
                error_handling={
                    ErrorCategory.SENSOR_ERROR: "use_fallback_sensor"
                },
                dependencies=[]
            ),
            "flight_controller": APIContract(
                module_name="flight_controller",
                module_role=ModuleRole.FLIGHT_CONTROL,
                input_schema={
                    "type": "object",
                    "properties": {
                        "target_altitude": {"type": "number"},
                        "target_velocity": {"type": "array", "items": {"type": "number"}}
                    }
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "motor_commands": {"type": "array", "items": {"type": "number"}},
                        "status": {"type": "string"}
                    }
                },
                max_latency_ms=10.0,
                error_handling={
                    ErrorCategory.SENSOR_ERROR: "fallback_to_last_known_state",
                    ErrorCategory.CONTROL_ERROR: "emergency_landing"
                },
                dependencies=["sensor_fusion", "safety_monitor"]
            ),
            "safety_monitor": APIContract(
                module_name="safety_monitor",
                module_role=ModuleRole.SAFETY_MONITOR,
                input_schema={
                    "type": "object",
                    "properties": {
                        "current_state": {"type": "object"},
                        "control_command": {"type": "object"}
                    }
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "is_safe": {"type": "boolean"},
                        "violation_reason": {"type": "string"}
                    }
                },
                max_latency_ms=5.0,
                error_handling={
                    ErrorCategory.SAFETY_VIOLATION: "trigger_emergency_protocol"
                },
                dependencies=[]
            )
        }
        
        for name, contract in contracts_data.items():
            self.contracts[name] = contract
    
    def validate_api_call(self, module_name: str, input_data: Dict) -> bool:
        """驗證 API 調用是否符合契約"""
        if module_name not in self.contracts:
            raise ValueError(f"Unknown module: {module_name}")
        
        contract = self.contracts[module_name]
        
        # 驗證輸入 schema
        required_keys = set(contract.input_schema.get("properties", {}).keys())
        provided_keys = set(input_data.keys())
        
        if not required_keys.issubset(provided_keys):
            missing = required_keys - provided_keys
            raise ValueError(f"Missing required fields: {missing}")
        
        return True
    
    def validate_dependency_chain(self, module_name: str, visited: set = None) -> bool:
        """驗證模組依賴鏈是否存在循環"""
        if visited is None:
            visited = set()
        
        if module_name in visited:
            raise ValueError(f"Circular dependency detected: {module_name}")
        
        visited.add(module_name)
        contract = self.contracts[module_name]
        
        for dep in contract.dependencies:
            self.validate_dependency_chain(dep, visited.copy())
        
        return True
    
    def generate_governance_report(self) -> str:
        """生成治理報告"""
        report = {
            "total_modules": len(self.contracts),
            "modules": {}
        }
        
        for name, contract in self.contracts.items():
            report["modules"][name] = {
                "role": contract.module_role.value,
                "max_latency_ms": contract.max_latency_ms,
                "dependencies": contract.dependencies,
                "error_categories": [e.value for e in contract.error_handling.keys()]
            }
        
        return json.dumps(report, indent=2, ensure_ascii=False)

# 使用範例
if __name__ == "__main__":
    validator = GovernanceValidator()
    
    # 驗證 API 調用
    try:
        validator.validate_api_call("flight_controller", {
            "target_altitude": 10.0,
            "target_velocity": [1.0, 2.0, 3.0]
        })
        print("✓ API call validated successfully")
    except ValueError as e:
        print(f"✗ API validation failed: {e}")
    
    # 驗證依賴鏈
    try:
        validator.validate_dependency_chain("flight_controller")
        print("✓ Dependency chain validated")
    except ValueError as e:
        print(f"✗ Dependency validation failed: {e}")
    
    # 生成治理報告
    print("\n治理報告：")
    print(validator.generate_governance_report())
