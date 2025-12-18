#!/usr/bin/env python3
"""
多語言橋接器 (Language Bridge)

負責不同語言島嶼之間的通信和數據轉換。
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Optional
import json
import subprocess


class BridgeProtocol:
    """橋接協議"""
    GRPC = "grpc"
    REST = "rest"
    WEBSOCKET = "websocket"
    MESSAGE_QUEUE = "message_queue"


class LanguageBridge:
    """
    多語言橋接器
    
    負責：
    - 島嶼間通信協調
    - 數據格式轉換
    - 協議適配
    - 錯誤處理與重試
    """
    
    def __init__(self) -> None:
        self.active_connections: dict[str, Any] = {}
        self.supported_protocols = [
            BridgeProtocol.GRPC,
            BridgeProtocol.REST,
            BridgeProtocol.WEBSOCKET,
        ]
        self._project_root = self._find_project_root()
    
    def _find_project_root(self) -> Path:
        """尋找專案根目錄"""
        current = Path(__file__).resolve().parent
        while current != current.parent:
            if (current / 'package.json').exists():
                return current
            current = current.parent
        return Path.cwd()
    
    @property
    def project_root(self) -> Path:
        return self._project_root
    
    def establish_bridge(
        self, 
        source_island: str, 
        target_island: str, 
        protocol: str = BridgeProtocol.REST
    ) -> bool:
        """
        建立島嶼間橋接
        
        Args:
            source_island: 來源島嶼 ID
            target_island: 目標島嶼 ID
            protocol: 通信協議
            
        Returns:
            是否建立成功
        """
        bridge_id = f"{source_island}->{target_island}"
        
        print(f"[Bridge][INFO] 建立橋接: {bridge_id} ({protocol})")
        
        self.active_connections[bridge_id] = {
            'source': source_island,
            'target': target_island,
            'protocol': protocol,
            'established_at': datetime.now().isoformat(),
            'status': 'active',
        }
        
        print(f"[Bridge][SUCCESS] 橋接已建立: {bridge_id}")
        return True
    
    def send_message(
        self, 
        bridge_id: str, 
        message: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        """
        透過橋接發送訊息
        
        Args:
            bridge_id: 橋接 ID
            message: 訊息內容
            
        Returns:
            回應內容
        """
        if bridge_id not in self.active_connections:
            print(f"[Bridge][ERROR] 橋接不存在: {bridge_id}")
            return None
        
        connection = self.active_connections[bridge_id]
        
        # 模擬訊息傳送
        return {
            'status': 'delivered',
            'bridge_id': bridge_id,
            'timestamp': datetime.now().isoformat(),
            'message_id': f"msg_{datetime.now().timestamp()}",
        }
    
    def close_bridge(self, bridge_id: str) -> bool:
        """關閉橋接"""
        if bridge_id in self.active_connections:
            del self.active_connections[bridge_id]
            print(f"[Bridge][INFO] 橋接已關閉: {bridge_id}")
            return True
        return False
    
    def get_active_bridges(self) -> list[dict[str, Any]]:
        """取得所有活躍橋接"""
        return list(self.active_connections.values())
    
    def invoke_typescript(self, script: str, args: list[str] = None) -> Optional[str]:
        """
        調用 TypeScript 腳本
        
        Args:
            script: 腳本路徑
            args: 命令行參數
            
        Returns:
            輸出結果
        """
        script_path = self.project_root / script
        if not script_path.exists():
            print(f"[Bridge][ERROR] 腳本不存在: {script_path}")
            return None
        
        cmd = ['npx', 'ts-node', str(script_path)]
        if args:
            cmd.extend(args)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=self.project_root
            )
            return result.stdout
        except Exception as e:
            print(f"[Bridge][ERROR] 執行失敗: {e}")
            return None
    
    def invoke_go(self, package: str, args: list[str] = None) -> Optional[str]:
        """調用 Go 程式"""
        cmd = ['go', 'run', package]
        if args:
            cmd.extend(args)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=self.project_root
            )
            return result.stdout
        except Exception as e:
            print(f"[Bridge][ERROR] 執行失敗: {e}")
            return None
    
    def invoke_rust(self, package: str, args: list[str] = None) -> Optional[str]:
        """調用 Rust 程式"""
        cmd = ['cargo', 'run', '-p', package]
        if args:
            cmd.extend(['--', *args])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                cwd=self.project_root
            )
            return result.stdout
        except Exception as e:
            print(f"[Bridge][ERROR] 執行失敗: {e}")
            return None
    
    def transform_data(
        self, 
        data: Any, 
        source_format: str, 
        target_format: str
    ) -> Any:
        """
        轉換數據格式
        
        Args:
            data: 原始數據
            source_format: 來源格式
            target_format: 目標格式
            
        Returns:
            轉換後的數據
        """
        # JSON 是通用中間格式
        if source_format == target_format:
            return data
        
        # 轉為 JSON 字串
        if target_format == 'json_string':
            return json.dumps(data)
        
        # 從 JSON 字串解析
        if source_format == 'json_string':
            return json.loads(data)
        
        return data
