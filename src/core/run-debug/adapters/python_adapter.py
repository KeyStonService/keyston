"""
Python 偵錯適配器
Python Debug Adapter

實作 Python 語言的偵錯功能，支援 debugpy 協議。
"""

import asyncio
import json
import socket
import subprocess
from typing import List, Optional, Dict, Any
from pathlib import Path
import sys

from ..engine import (
    DebugAdapter, DebugSession, Variable, StackFrame,
    DebugState, BreakpointType
)


class PythonDebugAdapter(DebugAdapter):
    """Python 偵錯適配器"""
    
    def __init__(self):
        super().__init__("python")
        self.debugpy_port = 5678
        self.socket: Optional[socket.socket] = None
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self.seq = 0
        self.pending_requests: Dict[int, asyncio.Future] = {}
        
    async def initialize(self, session: DebugSession):
        """初始化 Python 偵錯器"""
        self.logger.info(f"Initializing Python debug adapter for session {session.session_id}")
        
        # 檢查 debugpy 是否已安裝
        try:
            import debugpy
            self.logger.info(f"debugpy version: {debugpy.__version__}")
        except ImportError:
            self.logger.warning("debugpy not installed, installing...")
            subprocess.run([sys.executable, "-m", "pip", "install", "debugpy"],
                         check=True, capture_output=True)
        
        session.state = DebugState.INITIALIZING
    
    async def launch(self, session: DebugSession):
        """啟動 Python 程式進行偵錯"""
        config = session.config
        
        # 準備啟動命令
        cmd = [sys.executable, "-m", "debugpy", 
               "--listen", f"localhost:{self.debugpy_port}",
               "--wait-for-client"]
        
        if config.program:
            cmd.append(config.program)
        
        if config.args:
            cmd.extend(config.args)
        
        # 設定環境變數
        env = dict(os.environ)
        if config.env:
            env.update(config.env)
        
        # 設定工作目錄
        cwd = config.cwd or str(Path(config.program).parent) if config.program else None
        
        self.logger.info(f"Launching Python program: {' '.join(cmd)}")
        
        # 啟動程式
        session.process = subprocess.Popen(
            cmd,
            env=env,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE
        )
        
        # 等待 debugpy 準備好
        await asyncio.sleep(1)
        
        # 連接到 debugpy
        await self._connect_to_debugpy(session)
        
        # 發送初始化請求
        await self._send_initialize_request(session)
        
        # 設定斷點
        await self._set_breakpoints(session)
        
        # 開始執行
        await self._send_configuration_done(session)
        
        session.state = DebugState.RUNNING
        
        # 啟動輸出監聽
        asyncio.create_task(self._monitor_output(session))
    
    async def _connect_to_debugpy(self, session: DebugSession):
        """連接到 debugpy 伺服器"""
        max_retries = 10
        for i in range(max_retries):
            try:
                self.reader, self.writer = await asyncio.open_connection(
                    'localhost', self.debugpy_port
                )
                self.logger.info(f"Connected to debugpy on port {self.debugpy_port}")
                
                # 啟動訊息接收任務
                asyncio.create_task(self._receive_messages(session))
                return
            except ConnectionRefusedError:
                if i < max_retries - 1:
                    await asyncio.sleep(0.5)
                else:
                    raise
    
    async def _send_request(self, command: str, arguments: Optional[Dict] = None) -> Dict:
        """發送 DAP 請求"""
        self.seq += 1
        request = {
            "seq": self.seq,
            "type": "request",
            "command": command,
            "arguments": arguments or {}
        }
        
        # 創建 Future 等待回應
        future = asyncio.Future()
        self.pending_requests[self.seq] = future
        
        # 發送請求
        message = json.dumps(request)
        content = f"Content-Length: {len(message)}\r\n\r\n{message}"
        self.writer.write(content.encode('utf-8'))
        await self.writer.drain()
        
        self.logger.debug(f"Sent request: {command}")
        
        # 等待回應
        try:
            response = await asyncio.wait_for(future, timeout=10.0)
            return response
        except asyncio.TimeoutError:
            self.logger.error(f"Request {command} timed out")
            raise
    
    async def _receive_messages(self, session: DebugSession):
        """接收 DAP 訊息"""
        buffer = b""
        
        while True:
            try:
                data = await self.reader.read(4096)
                if not data:
                    break
                
                buffer += data
                
                # 解析訊息
                while b"\r\n\r\n" in buffer:
                    header_end = buffer.index(b"\r\n\r\n")
                    header = buffer[:header_end].decode('utf-8')
                    
                    # 解析 Content-Length
                    content_length = 0
                    for line in header.split('\r\n'):
                        if line.startswith('Content-Length:'):
                            content_length = int(line.split(':')[1].strip())
                            break
                    
                    # 檢查是否有完整的訊息
                    message_start = header_end + 4
                    message_end = message_start + content_length
                    
                    if len(buffer) < message_end:
                        break
                    
                    # 提取訊息
                    message_data = buffer[message_start:message_end]
                    buffer = buffer[message_end:]
                    
                    # 解析 JSON
                    message = json.loads(message_data.decode('utf-8'))
                    
                    # 處理訊息
                    await self._handle_message(session, message)
                    
            except Exception as e:
                self.logger.error(f"Error receiving messages: {e}")
                break
    
    async def _handle_message(self, session: DebugSession, message: Dict):
        """處理 DAP 訊息"""
        msg_type = message.get('type')
        
        if msg_type == 'response':
            # 回應訊息
            seq = message.get('request_seq')
            if seq in self.pending_requests:
                future = self.pending_requests.pop(seq)
                if message.get('success'):
                    future.set_result(message.get('body', {}))
                else:
                    future.set_exception(Exception(message.get('message', 'Request failed')))
        
        elif msg_type == 'event':
            # 事件訊息
            event = message.get('event')
            body = message.get('body', {})
            
            if event == 'stopped':
                session.state = DebugState.PAUSED
                reason = body.get('reason', 'unknown')
                self.logger.info(f"Program stopped: {reason}")
                
                # 更新堆疊追蹤
                session.stack_frames = await self.get_stack_trace(session)
                
            elif event == 'continued':
                session.state = DebugState.RUNNING
                self.logger.info("Program continued")
                
            elif event == 'terminated':
                session.state = DebugState.STOPPED
                self.logger.info("Program terminated")
                
            elif event == 'output':
                output = body.get('output', '')
                category = body.get('category', 'console')
                self.logger.info(f"Output ({category}): {output}")
    
    async def _send_initialize_request(self, session: DebugSession):
        """發送初始化請求"""
        response = await self._send_request('initialize', {
            'clientID': 'machinenativeops',
            'clientName': 'MachineNativeOps Debug',
            'adapterID': 'python',
            'pathFormat': 'path',
            'linesStartAt1': True,
            'columnsStartAt1': True,
            'supportsVariableType': True,
            'supportsVariablePaging': True,
            'supportsRunInTerminalRequest': True
        })
        self.logger.info("Initialized debug adapter")
    
    async def _set_breakpoints(self, session: DebugSession):
        """設定斷點"""
        # 按檔案分組斷點
        breakpoints_by_file: Dict[str, List] = {}
        for bp in session.breakpoints.values():
            if bp.file not in breakpoints_by_file:
                breakpoints_by_file[bp.file] = []
            breakpoints_by_file[bp.file].append({
                'line': bp.line,
                'condition': bp.condition,
                'logMessage': bp.log_message
            })
        
        # 為每個檔案設定斷點
        for file, bps in breakpoints_by_file.items():
            await self._send_request('setBreakpoints', {
                'source': {'path': file},
                'breakpoints': bps
            })
    
    async def _send_configuration_done(self, session: DebugSession):
        """發送配置完成"""
        await self._send_request('configurationDone')
    
    async def _monitor_output(self, session: DebugSession):
        """監控程式輸出"""
        if not session.process:
            return
        
        async def read_stream(stream, prefix):
            while True:
                line = await asyncio.get_event_loop().run_in_executor(
                    None, stream.readline
                )
                if not line:
                    break
                self.logger.info(f"{prefix}: {line.decode('utf-8').strip()}")
        
        await asyncio.gather(
            read_stream(session.process.stdout, "STDOUT"),
            read_stream(session.process.stderr, "STDERR")
        )
    
    async def attach(self, session: DebugSession):
        """附加到執行中的 Python 程式"""
        # 連接到已經在執行的 debugpy 伺服器
        await self._connect_to_debugpy(session)
        await self._send_initialize_request(session)
        await self._set_breakpoints(session)
        await self._send_configuration_done(session)
    
    async def pause(self, session: DebugSession):
        """暫停執行"""
        await self._send_request('pause', {
            'threadId': 1
        })
    
    async def continue_execution(self, session: DebugSession):
        """繼續執行"""
        await self._send_request('continue', {
            'threadId': 1
        })
    
    async def step_over(self, session: DebugSession):
        """單步執行（跳過）"""
        await self._send_request('next', {
            'threadId': 1
        })
    
    async def step_into(self, session: DebugSession):
        """單步執行（進入）"""
        await self._send_request('stepIn', {
            'threadId': 1
        })
    
    async def step_out(self, session: DebugSession):
        """單步執行（跳出）"""
        await self._send_request('stepOut', {
            'threadId': 1
        })
    
    async def evaluate(self, session: DebugSession, expression: str) -> Optional[Variable]:
        """評估表達式"""
        try:
            response = await self._send_request('evaluate', {
                'expression': expression,
                'frameId': session.stack_frames[0].id if session.stack_frames else 0,
                'context': 'repl'
            })
            
            return Variable(
                name=expression,
                value=response.get('result', ''),
                type=response.get('type', 'unknown'),
                evaluatable=True
            )
        except Exception as e:
            self.logger.error(f"Failed to evaluate expression: {e}")
            return None
    
    async def get_stack_trace(self, session: DebugSession) -> List[StackFrame]:
        """取得堆疊追蹤"""
        try:
            response = await self._send_request('stackTrace', {
                'threadId': 1
            })
            
            frames = []
            for i, frame_data in enumerate(response.get('stackFrames', [])):
                source = frame_data.get('source', {})
                frames.append(StackFrame(
                    id=frame_data.get('id', i),
                    name=frame_data.get('name', 'unknown'),
                    file=source.get('path', ''),
                    line=frame_data.get('line', 0),
                    column=frame_data.get('column', 0),
                    source=source.get('name')
                ))
            
            return frames
        except Exception as e:
            self.logger.error(f"Failed to get stack trace: {e}")
            return []
    
    async def get_variables(self, session: DebugSession, scope: str = "local") -> List[Variable]:
        """取得變數"""
        try:
            if not session.stack_frames:
                return []
            
            frame_id = session.stack_frames[0].id
            
            # 取得作用域
            scopes_response = await self._send_request('scopes', {
                'frameId': frame_id
            })
            
            variables = []
            for scope_data in scopes_response.get('scopes', []):
                scope_name = scope_data.get('name', '').lower()
                if scope == 'all' or scope in scope_name:
                    # 取得該作用域的變數
                    vars_response = await self._send_request('variables', {
                        'variablesReference': scope_data.get('variablesReference', 0)
                    })
                    
                    for var_data in vars_response.get('variables', []):
                        variables.append(Variable(
                            name=var_data.get('name', ''),
                            value=var_data.get('value', ''),
                            type=var_data.get('type', 'unknown'),
                            evaluatable=var_data.get('evaluateName') is not None
                        ))
            
            return variables
        except Exception as e:
            self.logger.error(f"Failed to get variables: {e}")
            return []
    
    async def terminate(self, session: DebugSession):
        """終止程式"""
        try:
            await self._send_request('disconnect', {
                'terminateDebuggee': True
            })
        except Exception as e:
            self.logger.error(f"Failed to terminate: {e}")
        
        if session.process:
            try:
                session.process.terminate()
                session.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                session.process.kill()
        
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()


# 匯入 os 模組
import os