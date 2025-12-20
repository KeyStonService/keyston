"""
執行與偵錯命令列介面
Run & Debug Command Line Interface

提供終端機命令來控制偵錯會話。
"""

import asyncio
import click
import sys
from pathlib import Path
from typing import Optional
import logging

from .engine import (
    get_engine, ConfigurationManager, LaunchConfiguration,
    DebugState, BreakpointType
)
from .adapters.python_adapter import PythonDebugAdapter


# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class DebugCLI:
    """偵錯命令列介面"""
    
    def __init__(self):
        self.engine = get_engine()
        self.current_session_id: Optional[str] = None
        self.workspace_path = Path.cwd()
        self.config_manager = ConfigurationManager(self.workspace_path)
        
        # 註冊 Python 適配器
        self.engine.register_adapter('python', PythonDebugAdapter())
    
    async def start_debug(self, config_name: str):
        """啟動偵錯會話"""
        # 載入配置
        configs = self.config_manager.load_configurations()
        config = self.config_manager.get_configuration(config_name)
        
        if not config:
            click.echo(f"❌ Configuration '{config_name}' not found", err=True)
            click.echo(f"Available configurations:")
            for c in configs:
                click.echo(f"  - {c.name}")
            return False
        
        try:
            # 建立會話
            session = await self.engine.create_session(config)
            self.current_session_id = session.session_id
            
            click.echo(f"✅ Created debug session: {session.session_id}")
            click.echo(f"📝 Configuration: {config.name}")
            click.echo(f"🔧 Type: {config.type}")
            
            # 啟動會話
            success = await self.engine.start_session(session.session_id)
            if success:
                click.echo(f"🚀 Debug session started")
                return True
            else:
                click.echo(f"❌ Failed to start debug session", err=True)
                return False
                
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            return False
    
    async def set_breakpoint(self, file: str, line: int, 
                           condition: Optional[str] = None,
                           log_message: Optional[str] = None):
        """設定斷點"""
        if not self.current_session_id:
            click.echo("❌ No active debug session", err=True)
            return False
        
        session = self.engine.get_session(self.current_session_id)
        if not session:
            click.echo("❌ Session not found", err=True)
            return False
        
        bp_type = BreakpointType.LOGPOINT if log_message else \
                  BreakpointType.CONDITIONAL if condition else \
                  BreakpointType.LINE
        
        bp = session.add_breakpoint(file, line, bp_type, condition, log_message)
        
        click.echo(f"✅ Breakpoint {bp.id} set at {file}:{line}")
        if condition:
            click.echo(f"   Condition: {condition}")
        if log_message:
            click.echo(f"   Log message: {log_message}")
        
        return True
    
    async def list_breakpoints(self):
        """列出所有斷點"""
        if not self.current_session_id:
            click.echo("❌ No active debug session", err=True)
            return
        
        session = self.engine.get_session(self.current_session_id)
        if not session:
            click.echo("❌ Session not found", err=True)
            return
        
        breakpoints = session.get_breakpoints()
        if not breakpoints:
            click.echo("No breakpoints set")
            return
        
        click.echo("📍 Breakpoints:")
        for bp in breakpoints:
            status = "✓" if bp.enabled else "✗"
            click.echo(f"  {status} [{bp.id}] {bp.file}:{bp.line} ({bp.type.value})")
            if bp.condition:
                click.echo(f"      Condition: {bp.condition}")
            if bp.log_message:
                click.echo(f"      Log: {bp.log_message}")
            click.echo(f"      Hit count: {bp.hit_count}")
    
    async def remove_breakpoint(self, breakpoint_id: int):
        """移除斷點"""
        if not self.current_session_id:
            click.echo("❌ No active debug session", err=True)
            return False
        
        session = self.engine.get_session(self.current_session_id)
        if not session:
            click.echo("❌ Session not found", err=True)
            return False
        
        if session.remove_breakpoint(breakpoint_id):
            click.echo(f"✅ Breakpoint {breakpoint_id} removed")
            return True
        else:
            click.echo(f"❌ Breakpoint {breakpoint_id} not found", err=True)
            return False
    
    async def continue_execution(self):
        """繼續執行"""
        if not self.current_session_id:
            click.echo("❌ No active debug session", err=True)
            return False
        
        success = await self.engine.continue_session(self.current_session_id)
        if success:
            click.echo("▶️  Continuing execution...")
            return True
        else:
            click.echo("❌ Failed to continue", err=True)
            return False
    
    async def step_over(self):
        """單步執行（跳過）"""
        if not self.current_session_id:
            click.echo("❌ No active debug session", err=True)
            return False
        
        success = await self.engine.step_over(self.current_session_id)
        if success:
            click.echo("⏭️  Stepped over")
            await self.show_current_location()
            return True
        else:
            click.echo("❌ Failed to step over", err=True)
            return False
    
    async def step_into(self):
        """單步執行（進入）"""
        if not self.current_session_id:
            click.echo("❌ No active debug session", err=True)
            return False
        
        success = await self.engine.step_into(self.current_session_id)
        if success:
            click.echo("⤵️  Stepped into")
            await self.show_current_location()
            return True
        else:
            click.echo("❌ Failed to step into", err=True)
            return False
    
    async def step_out(self):
        """單步執行（跳出）"""
        if not self.current_session_id:
            click.echo("❌ No active debug session", err=True)
            return False
        
        success = await self.engine.step_out(self.current_session_id)
        if success:
            click.echo("⤴️  Stepped out")
            await self.show_current_location()
            return True
        else:
            click.echo("❌ Failed to step out", err=True)
            return False
    
    async def show_stack_trace(self):
        """顯示堆疊追蹤"""
        if not self.current_session_id:
            click.echo("❌ No active debug session", err=True)
            return
        
        frames = await self.engine.get_stack_trace(self.current_session_id)
        if not frames:
            click.echo("No stack trace available")
            return
        
        click.echo("📚 Stack Trace:")
        for i, frame in enumerate(frames):
            marker = "→" if i == 0 else " "
            click.echo(f"  {marker} {frame.name}")
            click.echo(f"    at {frame.file}:{frame.line}:{frame.column}")
    
    async def show_variables(self, scope: str = "local"):
        """顯示變數"""
        if not self.current_session_id:
            click.echo("❌ No active debug session", err=True)
            return
        
        variables = await self.engine.get_variables(self.current_session_id, scope)
        if not variables:
            click.echo(f"No {scope} variables")
            return
        
        click.echo(f"📊 {scope.capitalize()} Variables:")
        for var in variables:
            click.echo(f"  {var.name} = {var.value} ({var.type})")
    
    async def evaluate_expression(self, expression: str):
        """評估表達式"""
        if not self.current_session_id:
            click.echo("❌ No active debug session", err=True)
            return
        
        result = await self.engine.evaluate_expression(self.current_session_id, expression)
        if result:
            click.echo(f"💡 {result.name} = {result.value} ({result.type})")
        else:
            click.echo("❌ Failed to evaluate expression", err=True)
    
    async def show_current_location(self):
        """顯示當前位置"""
        if not self.current_session_id:
            return
        
        frames = await self.engine.get_stack_trace(self.current_session_id)
        if frames:
            frame = frames[0]
            click.echo(f"📍 {frame.file}:{frame.line}")
    
    async def stop_debug(self):
        """停止偵錯會話"""
        if not self.current_session_id:
            click.echo("❌ No active debug session", err=True)
            return False
        
        success = await self.engine.stop_session(self.current_session_id)
        if success:
            click.echo(f"⏹️  Debug session stopped")
            self.current_session_id = None
            return True
        else:
            click.echo("❌ Failed to stop session", err=True)
            return False
    
    async def list_sessions(self):
        """列出所有會話"""
        sessions = self.engine.list_sessions()
        if not sessions:
            click.echo("No active debug sessions")
            return
        
        click.echo("🔍 Active Debug Sessions:")
        for session in sessions:
            marker = "→" if session.session_id == self.current_session_id else " "
            click.echo(f"  {marker} {session.session_id}")
            click.echo(f"    Config: {session.config.name}")
            click.echo(f"    State: {session.state.value}")
            click.echo(f"    Breakpoints: {len(session.breakpoints)}")


# Click 命令群組
@click.group()
def debug():
    """執行與偵錯命令列工具"""
    pass


@debug.command()
@click.option('--config', '-c', required=True, help='Configuration name')
def start(config):
    """啟動偵錯會話"""
    cli = DebugCLI()
    asyncio.run(cli.start_debug(config))


@debug.command()
@click.argument('file')
@click.argument('line', type=int)
@click.option('--condition', help='Breakpoint condition')
@click.option('--log', help='Log message')
def breakpoint(file, line, condition, log):
    """設定斷點"""
    cli = DebugCLI()
    asyncio.run(cli.set_breakpoint(file, line, condition, log))


@debug.command()
def list_breakpoints():
    """列出所有斷點"""
    cli = DebugCLI()
    asyncio.run(cli.list_breakpoints())


@debug.command()
@click.argument('breakpoint_id', type=int)
def remove(breakpoint_id):
    """移除斷點"""
    cli = DebugCLI()
    asyncio.run(cli.remove_breakpoint(breakpoint_id))


@debug.command()
def continue_cmd():
    """繼續執行"""
    cli = DebugCLI()
    asyncio.run(cli.continue_execution())


@debug.command()
def next():
    """單步執行（跳過）"""
    cli = DebugCLI()
    asyncio.run(cli.step_over())


@debug.command()
def step():
    """單步執行（進入）"""
    cli = DebugCLI()
    asyncio.run(cli.step_into())


@debug.command()
def out():
    """單步執行（跳出）"""
    cli = DebugCLI()
    asyncio.run(cli.step_out())


@debug.command()
def stack():
    """顯示堆疊追蹤"""
    cli = DebugCLI()
    asyncio.run(cli.show_stack_trace())


@debug.command()
@click.option('--scope', default='local', help='Variable scope (local/global/all)')
def variables(scope):
    """顯示變數"""
    cli = DebugCLI()
    asyncio.run(cli.show_variables(scope))


@debug.command()
@click.argument('expression')
def eval(expression):
    """評估表達式"""
    cli = DebugCLI()
    asyncio.run(cli.evaluate_expression(expression))


@debug.command()
def stop():
    """停止偵錯會話"""
    cli = DebugCLI()
    asyncio.run(cli.stop_debug())


@debug.command()
def sessions():
    """列出所有會話"""
    cli = DebugCLI()
    asyncio.run(cli.list_sessions())


@debug.command()
def repl():
    """啟動互動式偵錯 REPL"""
    cli = DebugCLI()
    click.echo("🔧 MachineNativeOps Debug REPL")
    click.echo("Type 'help' for available commands, 'exit' to quit")
    
    while True:
        try:
            command = click.prompt('(mno-debug)', type=str)
            command = command.strip()
            
            if command == 'exit' or command == 'quit':
                break
            elif command == 'help':
                click.echo("""
Available commands:
  start <config>          - Start debug session
  break <file> <line>     - Set breakpoint
  list                    - List breakpoints
  remove <id>             - Remove breakpoint
  continue                - Continue execution
  next                    - Step over
  step                    - Step into
  out                     - Step out
  stack                   - Show stack trace
  vars [scope]            - Show variables
  eval <expr>             - Evaluate expression
  stop                    - Stop debug session
  sessions                - List sessions
  help                    - Show this help
  exit                    - Exit REPL
                """)
            else:
                # 解析並執行命令
                parts = command.split()
                if not parts:
                    continue
                
                cmd = parts[0]
                args = parts[1:]
                
                if cmd == 'start' and args:
                    asyncio.run(cli.start_debug(args[0]))
                elif cmd == 'break' and len(args) >= 2:
                    asyncio.run(cli.set_breakpoint(args[0], int(args[1])))
                elif cmd == 'list':
                    asyncio.run(cli.list_breakpoints())
                elif cmd == 'remove' and args:
                    asyncio.run(cli.remove_breakpoint(int(args[0])))
                elif cmd == 'continue':
                    asyncio.run(cli.continue_execution())
                elif cmd == 'next':
                    asyncio.run(cli.step_over())
                elif cmd == 'step':
                    asyncio.run(cli.step_into())
                elif cmd == 'out':
                    asyncio.run(cli.step_out())
                elif cmd == 'stack':
                    asyncio.run(cli.show_stack_trace())
                elif cmd == 'vars':
                    scope = args[0] if args else 'local'
                    asyncio.run(cli.show_variables(scope))
                elif cmd == 'eval' and args:
                    asyncio.run(cli.evaluate_expression(' '.join(args)))
                elif cmd == 'stop':
                    asyncio.run(cli.stop_debug())
                elif cmd == 'sessions':
                    asyncio.run(cli.list_sessions())
                else:
                    click.echo(f"Unknown command: {cmd}")
                    
        except KeyboardInterrupt:
            click.echo("\nUse 'exit' to quit")
        except Exception as e:
            click.echo(f"Error: {e}", err=True)


if __name__ == '__main__':
    debug()