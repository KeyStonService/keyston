"""
執行與偵錯引擎核心模組
Run & Debug Engine Core Module

這個模組提供了完整的執行與偵錯功能，支援多語言、終端機命令和聊天介面。
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import subprocess
import signal
import os


class DebugState(Enum):
    """偵錯狀態"""
    IDLE = "idle"
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


class BreakpointType(Enum):
    """斷點類型"""
    LINE = "line"
    CONDITIONAL = "conditional"
    LOGPOINT = "logpoint"
    EXCEPTION = "exception"
    DATA = "data"


@dataclass
class Breakpoint:
    """斷點資料結構"""
    id: int
    file: str
    line: int
    type: BreakpointType = BreakpointType.LINE
    condition: Optional[str] = None
    log_message: Optional[str] = None
    enabled: bool = True
    hit_count: int = 0
    verified: bool = False


@dataclass
class StackFrame:
    """堆疊框架"""
    id: int
    name: str
    file: str
    line: int
    column: int
    source: Optional[str] = None


@dataclass
class Variable:
    """變數資料"""
    name: str
    value: Any
    type: str
    evaluatable: bool = True
    children: List['Variable'] = field(default_factory=list)


@dataclass
class LaunchConfiguration:
    """啟動配置"""
    name: str
    type: str
    request: str  # "launch" or "attach"
    program: Optional[str] = None
    args: List[str] = field(default_factory=list)
    cwd: Optional[str] = None
    env: Dict[str, str] = field(default_factory=dict)
    console: str = "integratedTerminal"
    stop_on_entry: bool = False
    just_my_code: bool = True
    additional_options: Dict[str, Any] = field(default_factory=dict)


class DebugSession:
    """偵錯會話管理"""
    
    def __init__(self, session_id: str, config: LaunchConfiguration):
        self.session_id = session_id
        self.config = config
        self.state = DebugState.IDLE
        self.breakpoints: Dict[int, Breakpoint] = {}
        self.stack_frames: List[StackFrame] = []
        self.variables: Dict[str, Variable] = {}
        self.process: Optional[subprocess.Popen] = None
        self.logger = logging.getLogger(f"DebugSession.{session_id}")
        self._breakpoint_counter = 0
        self._event_handlers: Dict[str, List[Callable]] = {}
        
    def add_breakpoint(self, file: str, line: int, 
                      bp_type: BreakpointType = BreakpointType.LINE,
                      condition: Optional[str] = None,
                      log_message: Optional[str] = None) -> Breakpoint:
        """新增斷點"""
        self._breakpoint_counter += 1
        bp = Breakpoint(
            id=self._breakpoint_counter,
            file=file,
            line=line,
            type=bp_type,
            condition=condition,
            log_message=log_message
        )
        self.breakpoints[bp.id] = bp
        self.logger.info(f"Breakpoint {bp.id} added at {file}:{line}")
        self._emit_event("breakpoint_added", bp)
        return bp
    
    def remove_breakpoint(self, breakpoint_id: int) -> bool:
        """移除斷點"""
        if breakpoint_id in self.breakpoints:
            bp = self.breakpoints.pop(breakpoint_id)
            self.logger.info(f"Breakpoint {breakpoint_id} removed from {bp.file}:{bp.line}")
            self._emit_event("breakpoint_removed", bp)
            return True
        return False
    
    def get_breakpoints(self, file: Optional[str] = None) -> List[Breakpoint]:
        """取得斷點列表"""
        if file:
            return [bp for bp in self.breakpoints.values() if bp.file == file]
        return list(self.breakpoints.values())
    
    def on(self, event: str, handler: Callable):
        """註冊事件處理器"""
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)
    
    def _emit_event(self, event: str, data: Any):
        """觸發事件"""
        if event in self._event_handlers:
            for handler in self._event_handlers[event]:
                try:
                    handler(data)
                except Exception as e:
                    self.logger.error(f"Error in event handler: {e}")


class DebugEngine:
    """執行與偵錯引擎"""
    
    def __init__(self):
        self.sessions: Dict[str, DebugSession] = {}
        self.adapters: Dict[str, 'DebugAdapter'] = {}
        self.logger = logging.getLogger("DebugEngine")
        self._session_counter = 0
        
    def register_adapter(self, language: str, adapter: 'DebugAdapter'):
        """註冊語言適配器"""
        self.adapters[language] = adapter
        self.logger.info(f"Registered debug adapter for {language}")
    
    async def create_session(self, config: LaunchConfiguration) -> DebugSession:
        """建立偵錯會話"""
        self._session_counter += 1
        session_id = f"session_{self._session_counter}"
        
        session = DebugSession(session_id, config)
        self.sessions[session_id] = session
        
        # 取得對應的語言適配器
        adapter = self.adapters.get(config.type)
        if not adapter:
            raise ValueError(f"No debug adapter found for type: {config.type}")
        
        # 初始化適配器
        await adapter.initialize(session)
        
        self.logger.info(f"Created debug session {session_id} for {config.name}")
        return session
    
    async def start_session(self, session_id: str) -> bool:
        """啟動偵錯會話"""
        session = self.sessions.get(session_id)
        if not session:
            self.logger.error(f"Session {session_id} not found")
            return False
        
        adapter = self.adapters.get(session.config.type)
        if not adapter:
            self.logger.error(f"No adapter for {session.config.type}")
            return False
        
        try:
            session.state = DebugState.INITIALIZING
            await adapter.launch(session)
            session.state = DebugState.RUNNING
            self.logger.info(f"Session {session_id} started")
            return True
        except Exception as e:
            session.state = DebugState.ERROR
            self.logger.error(f"Failed to start session {session_id}: {e}")
            return False
    
    async def pause_session(self, session_id: str) -> bool:
        """暫停偵錯會話"""
        session = self.sessions.get(session_id)
        if not session or session.state != DebugState.RUNNING:
            return False
        
        adapter = self.adapters.get(session.config.type)
        if adapter:
            await adapter.pause(session)
            session.state = DebugState.PAUSED
            return True
        return False
    
    async def continue_session(self, session_id: str) -> bool:
        """繼續執行"""
        session = self.sessions.get(session_id)
        if not session or session.state != DebugState.PAUSED:
            return False
        
        adapter = self.adapters.get(session.config.type)
        if adapter:
            await adapter.continue_execution(session)
            session.state = DebugState.RUNNING
            return True
        return False
    
    async def step_over(self, session_id: str) -> bool:
        """單步執行（跳過）"""
        session = self.sessions.get(session_id)
        if not session or session.state != DebugState.PAUSED:
            return False
        
        adapter = self.adapters.get(session.config.type)
        if adapter:
            await adapter.step_over(session)
            return True
        return False
    
    async def step_into(self, session_id: str) -> bool:
        """單步執行（進入）"""
        session = self.sessions.get(session_id)
        if not session or session.state != DebugState.PAUSED:
            return False
        
        adapter = self.adapters.get(session.config.type)
        if adapter:
            await adapter.step_into(session)
            return True
        return False
    
    async def step_out(self, session_id: str) -> bool:
        """單步執行（跳出）"""
        session = self.sessions.get(session_id)
        if not session or session.state != DebugState.PAUSED:
            return False
        
        adapter = self.adapters.get(session.config.type)
        if adapter:
            await adapter.step_out(session)
            return True
        return False
    
    async def evaluate_expression(self, session_id: str, expression: str) -> Optional[Variable]:
        """評估表達式"""
        session = self.sessions.get(session_id)
        if not session or session.state != DebugState.PAUSED:
            return None
        
        adapter = self.adapters.get(session.config.type)
        if adapter:
            return await adapter.evaluate(session, expression)
        return None
    
    async def get_stack_trace(self, session_id: str) -> List[StackFrame]:
        """取得堆疊追蹤"""
        session = self.sessions.get(session_id)
        if not session or session.state != DebugState.PAUSED:
            return []
        
        adapter = self.adapters.get(session.config.type)
        if adapter:
            return await adapter.get_stack_trace(session)
        return []
    
    async def get_variables(self, session_id: str, scope: str = "local") -> List[Variable]:
        """取得變數"""
        session = self.sessions.get(session_id)
        if not session or session.state != DebugState.PAUSED:
            return []
        
        adapter = self.adapters.get(session.config.type)
        if adapter:
            return await adapter.get_variables(session, scope)
        return []
    
    async def stop_session(self, session_id: str) -> bool:
        """停止偵錯會話"""
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        adapter = self.adapters.get(session.config.type)
        if adapter:
            await adapter.terminate(session)
        
        session.state = DebugState.STOPPED
        self.logger.info(f"Session {session_id} stopped")
        return True
    
    def get_session(self, session_id: str) -> Optional[DebugSession]:
        """取得會話"""
        return self.sessions.get(session_id)
    
    def list_sessions(self) -> List[DebugSession]:
        """列出所有會話"""
        return list(self.sessions.values())


class DebugAdapter:
    """偵錯適配器基類"""
    
    def __init__(self, language: str):
        self.language = language
        self.logger = logging.getLogger(f"DebugAdapter.{language}")
    
    async def initialize(self, session: DebugSession):
        """初始化適配器"""
        raise NotImplementedError
    
    async def launch(self, session: DebugSession):
        """啟動程式"""
        raise NotImplementedError
    
    async def attach(self, session: DebugSession):
        """附加到執行中的程式"""
        raise NotImplementedError
    
    async def pause(self, session: DebugSession):
        """暫停執行"""
        raise NotImplementedError
    
    async def continue_execution(self, session: DebugSession):
        """繼續執行"""
        raise NotImplementedError
    
    async def step_over(self, session: DebugSession):
        """單步執行（跳過）"""
        raise NotImplementedError
    
    async def step_into(self, session: DebugSession):
        """單步執行（進入）"""
        raise NotImplementedError
    
    async def step_out(self, session: DebugSession):
        """單步執行（跳出）"""
        raise NotImplementedError
    
    async def evaluate(self, session: DebugSession, expression: str) -> Optional[Variable]:
        """評估表達式"""
        raise NotImplementedError
    
    async def get_stack_trace(self, session: DebugSession) -> List[StackFrame]:
        """取得堆疊追蹤"""
        raise NotImplementedError
    
    async def get_variables(self, session: DebugSession, scope: str) -> List[Variable]:
        """取得變數"""
        raise NotImplementedError
    
    async def terminate(self, session: DebugSession):
        """終止程式"""
        raise NotImplementedError


class ConfigurationManager:
    """配置管理器"""
    
    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.launch_json_path = workspace_path / ".vscode" / "launch.json"
        self.configurations: List[LaunchConfiguration] = []
        self.logger = logging.getLogger("ConfigurationManager")
    
    def load_configurations(self) -> List[LaunchConfiguration]:
        """載入配置"""
        if not self.launch_json_path.exists():
            self.logger.warning(f"launch.json not found at {self.launch_json_path}")
            return []
        
        try:
            with open(self.launch_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            configs = []
            for config_data in data.get('configurations', []):
                config = self._parse_configuration(config_data)
                if config:
                    configs.append(config)
            
            self.configurations = configs
            self.logger.info(f"Loaded {len(configs)} configurations")
            return configs
            
        except Exception as e:
            self.logger.error(f"Failed to load configurations: {e}")
            return []
    
    def _parse_configuration(self, data: Dict) -> Optional[LaunchConfiguration]:
        """解析配置"""
        try:
            # 替換變數
            data = self._substitute_variables(data)
            
            config = LaunchConfiguration(
                name=data.get('name', 'Unnamed'),
                type=data.get('type', 'unknown'),
                request=data.get('request', 'launch'),
                program=data.get('program'),
                args=data.get('args', []),
                cwd=data.get('cwd'),
                env=data.get('env', {}),
                console=data.get('console', 'integratedTerminal'),
                stop_on_entry=data.get('stopOnEntry', False),
                just_my_code=data.get('justMyCode', True),
                additional_options={k: v for k, v in data.items() 
                                  if k not in ['name', 'type', 'request', 'program', 
                                             'args', 'cwd', 'env', 'console', 
                                             'stopOnEntry', 'justMyCode']}
            )
            return config
        except Exception as e:
            self.logger.error(f"Failed to parse configuration: {e}")
            return None
    
    def _substitute_variables(self, data: Dict) -> Dict:
        """替換變數"""
        import copy
        result = copy.deepcopy(data)
        
        substitutions = {
            '${workspaceFolder}': str(self.workspace_path),
            '${workspaceFolderBasename}': self.workspace_path.name,
        }
        
        def substitute_value(value):
            if isinstance(value, str):
                for key, replacement in substitutions.items():
                    value = value.replace(key, replacement)
                # 處理環境變數
                if '${env:' in value:
                    import re
                    for match in re.finditer(r'\$\{env:(\w+)\}', value):
                        env_var = match.group(1)
                        env_value = os.environ.get(env_var, '')
                        value = value.replace(match.group(0), env_value)
                return value
            elif isinstance(value, dict):
                return {k: substitute_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [substitute_value(item) for item in value]
            return value
        
        return substitute_value(result)
    
    def get_configuration(self, name: str) -> Optional[LaunchConfiguration]:
        """取得指定配置"""
        for config in self.configurations:
            if config.name == name:
                return config
        return None
    
    def save_configuration(self, config: LaunchConfiguration):
        """儲存配置"""
        # 確保目錄存在
        self.launch_json_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 載入現有配置
        if self.launch_json_path.exists():
            with open(self.launch_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {'version': '0.2.0', 'configurations': []}
        
        # 更新或新增配置
        config_dict = {
            'name': config.name,
            'type': config.type,
            'request': config.request,
            'program': config.program,
            'args': config.args,
            'cwd': config.cwd,
            'env': config.env,
            'console': config.console,
            'stopOnEntry': config.stop_on_entry,
            'justMyCode': config.just_my_code,
            **config.additional_options
        }
        
        # 移除 None 值
        config_dict = {k: v for k, v in config_dict.items() if v is not None}
        
        # 尋找並更新現有配置
        found = False
        for i, existing in enumerate(data['configurations']):
            if existing.get('name') == config.name:
                data['configurations'][i] = config_dict
                found = True
                break
        
        if not found:
            data['configurations'].append(config_dict)
        
        # 儲存
        with open(self.launch_json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Saved configuration: {config.name}")


# 全域引擎實例
_engine = DebugEngine()

def get_engine() -> DebugEngine:
    """取得全域引擎實例"""
    return _engine