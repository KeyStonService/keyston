# -*- coding: utf-8 -*-
"""
低代碼整合模組 (Low-Code Integration Module)

功能：
- 公民開發者支援：非技術人員友好的界面
- 視覺化工作流：拖放式依賴管理
- 自動生成器：配置到代碼的自動轉換
- 模板系統：預設的依賴管理模板

Features:
- Citizen Developer Support: Non-technical friendly interface
- Visual Workflow: Drag-and-drop dependency management
- Auto Generator: Configuration to code conversion
- Template System: Preset dependency management templates
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from datetime import datetime
import json


class SkillLevel(Enum):
    """技能等級"""
    BEGINNER = "beginner"           # 初學者
    INTERMEDIATE = "intermediate"   # 中級
    ADVANCED = "advanced"           # 高級
    EXPERT = "expert"               # 專家


class WorkflowNodeType(Enum):
    """工作流節點類型"""
    TRIGGER = "trigger"             # 觸發器
    ACTION = "action"               # 動作
    CONDITION = "condition"         # 條件
    LOOP = "loop"                   # 循環
    TRANSFORM = "transform"         # 轉換
    OUTPUT = "output"               # 輸出


@dataclass
class CitizenDeveloper:
    """公民開發者配置"""
    user_id: str
    name: str
    skill_level: SkillLevel = SkillLevel.BEGINNER
    
    # 權限設置
    can_view: bool = True
    can_edit: bool = False
    can_execute: bool = False
    can_approve: bool = False
    
    # 使用統計
    workflows_created: int = 0
    templates_used: int = 0
    last_activity: Optional[datetime] = None
    
    # 學習進度
    tutorials_completed: List[str] = field(default_factory=list)
    achievements: List[str] = field(default_factory=list)
    
    def upgrade_skill(self) -> bool:
        """升級技能等級"""
        levels = list(SkillLevel)
        current_index = levels.index(self.skill_level)
        
        if current_index < len(levels) - 1:
            self.skill_level = levels[current_index + 1]
            self._update_permissions()
            return True
        return False
    
    def _update_permissions(self):
        """根據技能等級更新權限"""
        if self.skill_level == SkillLevel.INTERMEDIATE:
            self.can_edit = True
        elif self.skill_level == SkillLevel.ADVANCED:
            self.can_execute = True
        elif self.skill_level == SkillLevel.EXPERT:
            self.can_approve = True


@dataclass
class WorkflowNode:
    """工作流節點"""
    node_id: str
    node_type: WorkflowNodeType
    name: str
    description: str = ""
    
    # 配置
    config: Dict[str, Any] = field(default_factory=dict)
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    
    # 連接
    next_nodes: List[str] = field(default_factory=list)
    previous_nodes: List[str] = field(default_factory=list)
    
    # 狀態
    is_enabled: bool = True
    last_executed: Optional[datetime] = None
    execution_count: int = 0


@dataclass
class VisualWorkflow:
    """視覺化工作流"""
    workflow_id: str
    name: str
    description: str = ""
    
    # 節點
    nodes: Dict[str, WorkflowNode] = field(default_factory=dict)
    
    # 元數據
    created_by: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    version: str = "1.0.0"
    
    # 狀態
    is_active: bool = False
    is_published: bool = False
    execution_count: int = 0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def add_node(self, node: WorkflowNode) -> bool:
        """添加節點"""
        if node.node_id not in self.nodes:
            self.nodes[node.node_id] = node
            self.updated_at = datetime.now()
            return True
        return False
    
    def connect_nodes(self, from_id: str, to_id: str) -> bool:
        """連接節點"""
        if from_id in self.nodes and to_id in self.nodes:
            self.nodes[from_id].next_nodes.append(to_id)
            self.nodes[to_id].previous_nodes.append(from_id)
            self.updated_at = datetime.now()
            return True
        return False
    
    def validate(self) -> List[str]:
        """驗證工作流"""
        errors = []
        
        # 檢查是否有觸發器
        triggers = [n for n in self.nodes.values() 
                   if n.node_type == WorkflowNodeType.TRIGGER]
        if not triggers:
            errors.append("工作流必須有至少一個觸發器")
        
        # 檢查是否有輸出
        outputs = [n for n in self.nodes.values() 
                  if n.node_type == WorkflowNodeType.OUTPUT]
        if not outputs:
            errors.append("工作流必須有至少一個輸出節點")
        
        # 檢查孤立節點
        for node_id, node in self.nodes.items():
            if node.node_type != WorkflowNodeType.TRIGGER:
                if not node.previous_nodes:
                    errors.append(f"節點 {node.name} 沒有輸入連接")
        
        return errors


@dataclass
class WorkflowTemplate:
    """工作流模板"""
    template_id: str
    name: str
    description: str
    category: str
    
    # 模板內容
    workflow_definition: Dict[str, Any] = field(default_factory=dict)
    
    # 難度和適用性
    difficulty: SkillLevel = SkillLevel.BEGINNER
    use_cases: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    # 統計
    usage_count: int = 0
    rating: float = 0.0
    reviews: List[Dict[str, Any]] = field(default_factory=list)


class AutoGenerator:
    """
    自動生成器
    
    功能：
    - 從配置生成代碼
    - 從工作流生成腳本
    - 生成依賴管理配置
    """
    
    # 支援的目標格式
    SUPPORTED_FORMATS = {
        'yaml': 'YAML 配置',
        'json': 'JSON 配置',
        'python': 'Python 腳本',
        'bash': 'Bash 腳本',
        'dockerfile': 'Dockerfile',
        'github_actions': 'GitHub Actions'
    }
    
    def __init__(self):
        self.generators: Dict[str, Callable] = {
            'yaml': self._generate_yaml,
            'json': self._generate_json,
            'python': self._generate_python,
            'bash': self._generate_bash,
            'dockerfile': self._generate_dockerfile,
            'github_actions': self._generate_github_actions
        }
    
    def generate(
        self,
        config: Dict[str, Any],
        target_format: str
    ) -> str:
        """
        從配置生成目標格式代碼
        
        Args:
            config: 配置字典
            target_format: 目標格式
        
        Returns:
            str: 生成的代碼
        """
        if target_format not in self.generators:
            raise ValueError(f"不支援的格式: {target_format}")
        
        return self.generators[target_format](config)
    
    def _generate_yaml(self, config: Dict[str, Any]) -> str:
        """生成 YAML 配置"""
        import yaml
        
        # 將配置轉換為 YAML 格式
        yaml_content = yaml.dump(config, default_flow_style=False, 
                                 allow_unicode=True, sort_keys=False)
        
        return f"# 自動生成的依賴管理配置\n# 生成時間: {datetime.now().isoformat()}\n\n{yaml_content}"
    
    def _generate_json(self, config: Dict[str, Any]) -> str:
        """生成 JSON 配置"""
        return json.dumps(config, indent=2, ensure_ascii=False)
    
    def _generate_python(self, config: Dict[str, Any]) -> str:
        """生成 Python 腳本"""
        dependencies = config.get('dependencies', [])
        actions = config.get('actions', [])
        
        script = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動生成的依賴管理腳本
生成時間: {timestamp}
"""

import subprocess
import sys

# 依賴項列表
DEPENDENCIES = {dependencies}

# 動作列表
ACTIONS = {actions}

def install_dependencies():
    """安裝依賴項"""
    for dep in DEPENDENCIES:
        name = dep.get('name', '')
        version = dep.get('version', '')
        if name:
            package = f"{{name}}=={{version}}" if version else name
            print(f"安裝: {{package}}")
            subprocess.run([sys.executable, '-m', 'pip', 'install', package])

def run_actions():
    """執行動作"""
    for action in ACTIONS:
        action_type = action.get('type', '')
        print(f"執行動作: {{action_type}}")
        # 根據動作類型執行相應操作

if __name__ == '__main__':
    install_dependencies()
    run_actions()
'''.format(
            timestamp=datetime.now().isoformat(),
            dependencies=repr(dependencies),
            actions=repr(actions)
        )
        
        return script
    
    def _generate_bash(self, config: Dict[str, Any]) -> str:
        """生成 Bash 腳本"""
        dependencies = config.get('dependencies', [])
        ecosystem = config.get('ecosystem', 'npm')
        
        script_lines = [
            '#!/bin/bash',
            '# 自動生成的依賴管理腳本',
            f'# 生成時間: {datetime.now().isoformat()}',
            '',
            'set -e',
            '',
            '# 安裝依賴項',
        ]
        
        for dep in dependencies:
            name = dep.get('name', '')
            version = dep.get('version', '')
            
            if ecosystem == 'npm':
                package = f"{name}@{version}" if version else name
                script_lines.append(f'npm install {package}')
            elif ecosystem == 'pip':
                package = f"{name}=={version}" if version else name
                script_lines.append(f'pip install {package}')
            elif ecosystem == 'go':
                package = f"{name}@{version}" if version else name
                script_lines.append(f'go get {package}')
        
        script_lines.extend([
            '',
            'echo "依賴安裝完成！"'
        ])
        
        return '\n'.join(script_lines)
    
    def _generate_dockerfile(self, config: Dict[str, Any]) -> str:
        """生成 Dockerfile"""
        base_image = config.get('base_image', 'node:18-alpine')
        dependencies = config.get('dependencies', [])
        ecosystem = config.get('ecosystem', 'npm')
        
        dockerfile_lines = [
            f'# 自動生成的 Dockerfile',
            f'# 生成時間: {datetime.now().isoformat()}',
            '',
            f'FROM {base_image}',
            '',
            'WORKDIR /app',
            ''
        ]
        
        # 根據生態系統添加依賴安裝
        if ecosystem == 'npm':
            dockerfile_lines.extend([
                'COPY package*.json ./',
                'RUN npm ci --only=production',
                ''
            ])
        elif ecosystem == 'pip':
            dockerfile_lines.extend([
                'COPY requirements.txt ./',
                'RUN pip install --no-cache-dir -r requirements.txt',
                ''
            ])
        elif ecosystem == 'go':
            dockerfile_lines.extend([
                'COPY go.mod go.sum ./',
                'RUN go mod download',
                ''
            ])
        
        dockerfile_lines.extend([
            'COPY . .',
            '',
            'CMD ["npm", "start"]'
        ])
        
        return '\n'.join(dockerfile_lines)
    
    def _generate_github_actions(self, config: Dict[str, Any]) -> str:
        """生成 GitHub Actions 工作流"""
        name = config.get('name', 'Dependency Management')
        ecosystem = config.get('ecosystem', 'npm')
        
        workflow = {
            'name': name,
            'on': {
                'push': {'branches': ['main']},
                'pull_request': {'branches': ['main']},
                'schedule': [{'cron': '0 0 * * 0'}]
            },
            'jobs': {
                'dependency-check': {
                    'runs-on': 'ubuntu-latest',
                    'steps': [
                        {'uses': 'actions/checkout@v3'},
                    ]
                }
            }
        }
        
        # 根據生態系統添加步驟
        steps = workflow['jobs']['dependency-check']['steps']
        
        if ecosystem == 'npm':
            steps.extend([
                {'uses': 'actions/setup-node@v3', 'with': {'node-version': '18'}},
                {'run': 'npm ci'},
                {'run': 'npm audit'}
            ])
        elif ecosystem == 'pip':
            steps.extend([
                {'uses': 'actions/setup-python@v4', 'with': {'python-version': '3.11'}},
                {'run': 'pip install -r requirements.txt'},
                {'run': 'pip-audit'}
            ])
        elif ecosystem == 'go':
            steps.extend([
                {'uses': 'actions/setup-go@v4', 'with': {'go-version': '1.21'}},
                {'run': 'go mod download'},
                {'run': 'go mod verify'}
            ])
        
        import yaml
        return yaml.dump(workflow, default_flow_style=False, allow_unicode=True)


class LowCodeIntegration:
    """
    低代碼整合平台
    
    功能：
    - 管理公民開發者
    - 創建和執行視覺化工作流
    - 使用和管理模板
    - 自動生成配置和代碼
    
    Usage:
        platform = LowCodeIntegration()
        
        # 創建公民開發者
        user = platform.create_citizen_developer("user1", "張小明")
        
        # 創建工作流
        workflow = platform.create_workflow("wf1", "依賴更新工作流")
        
        # 使用模板
        workflow = platform.apply_template("security-scan")
        
        # 生成代碼
        code = platform.generate_code(workflow, 'python')
    """
    
    # 預設模板
    DEFAULT_TEMPLATES = {
        'security-scan': WorkflowTemplate(
            template_id='security-scan',
            name='安全掃描工作流',
            description='定期掃描依賴項漏洞',
            category='security',
            difficulty=SkillLevel.BEGINNER,
            use_cases=['漏洞檢測', '安全合規'],
            tags=['security', 'scan', 'vulnerability'],
            workflow_definition={
                'trigger': {'type': 'schedule', 'cron': '0 0 * * *'},
                'actions': [
                    {'type': 'scan', 'target': 'dependencies'},
                    {'type': 'notify', 'channel': 'slack'}
                ]
            }
        ),
        'auto-update': WorkflowTemplate(
            template_id='auto-update',
            name='自動更新工作流',
            description='自動更新過時的依賴項',
            category='maintenance',
            difficulty=SkillLevel.INTERMEDIATE,
            use_cases=['依賴更新', '維護自動化'],
            tags=['update', 'automation', 'maintenance'],
            workflow_definition={
                'trigger': {'type': 'schedule', 'cron': '0 0 * * 1'},
                'actions': [
                    {'type': 'check_updates'},
                    {'type': 'update', 'strategy': 'semver'},
                    {'type': 'create_pr'}
                ]
            }
        ),
        'license-check': WorkflowTemplate(
            template_id='license-check',
            name='許可證檢查工作流',
            description='檢查依賴項許可證合規性',
            category='compliance',
            difficulty=SkillLevel.BEGINNER,
            use_cases=['許可證合規', '法律風險'],
            tags=['license', 'compliance', 'legal'],
            workflow_definition={
                'trigger': {'type': 'push'},
                'actions': [
                    {'type': 'scan_licenses'},
                    {'type': 'check_policy'},
                    {'type': 'report'}
                ]
            }
        ),
        'dependency-report': WorkflowTemplate(
            template_id='dependency-report',
            name='依賴報告工作流',
            description='生成依賴項分析報告',
            category='reporting',
            difficulty=SkillLevel.BEGINNER,
            use_cases=['報告生成', '依賴分析'],
            tags=['report', 'analysis', 'documentation'],
            workflow_definition={
                'trigger': {'type': 'manual'},
                'actions': [
                    {'type': 'analyze'},
                    {'type': 'generate_report', 'format': 'markdown'},
                    {'type': 'save', 'path': 'reports/'}
                ]
            }
        )
    }
    
    def __init__(self):
        self.users: Dict[str, CitizenDeveloper] = {}
        self.workflows: Dict[str, VisualWorkflow] = {}
        self.templates: Dict[str, WorkflowTemplate] = dict(self.DEFAULT_TEMPLATES)
        self.generator = AutoGenerator()
    
    def create_citizen_developer(
        self,
        user_id: str,
        name: str,
        skill_level: SkillLevel = SkillLevel.BEGINNER
    ) -> CitizenDeveloper:
        """
        創建公民開發者
        
        Args:
            user_id: 用戶 ID
            name: 用戶名稱
            skill_level: 技能等級
        
        Returns:
            CitizenDeveloper: 新創建的公民開發者
        """
        user = CitizenDeveloper(
            user_id=user_id,
            name=name,
            skill_level=skill_level,
            last_activity=datetime.now()
        )
        
        # 根據技能等級設置權限
        user._update_permissions()
        
        self.users[user_id] = user
        return user
    
    def create_workflow(
        self,
        workflow_id: str,
        name: str,
        description: str = "",
        created_by: str = ""
    ) -> VisualWorkflow:
        """
        創建視覺化工作流
        
        Args:
            workflow_id: 工作流 ID
            name: 工作流名稱
            description: 描述
            created_by: 創建者 ID
        
        Returns:
            VisualWorkflow: 新創建的工作流
        """
        workflow = VisualWorkflow(
            workflow_id=workflow_id,
            name=name,
            description=description,
            created_by=created_by
        )
        
        self.workflows[workflow_id] = workflow
        
        # 更新創建者統計
        if created_by in self.users:
            self.users[created_by].workflows_created += 1
            self.users[created_by].last_activity = datetime.now()
        
        return workflow
    
    def apply_template(
        self,
        template_id: str,
        workflow_id: str,
        customizations: Optional[Dict[str, Any]] = None
    ) -> VisualWorkflow:
        """
        應用模板創建工作流
        
        Args:
            template_id: 模板 ID
            workflow_id: 新工作流 ID
            customizations: 自定義配置
        
        Returns:
            VisualWorkflow: 從模板創建的工作流
        """
        if template_id not in self.templates:
            raise ValueError(f"模板不存在: {template_id}")
        
        template = self.templates[template_id]
        
        # 創建工作流
        workflow = VisualWorkflow(
            workflow_id=workflow_id,
            name=f"{template.name} - {workflow_id}",
            description=template.description,
            version="1.0.0"
        )
        
        # 應用模板定義
        definition = template.workflow_definition.copy()
        if customizations:
            definition.update(customizations)
        
        # 創建觸發器節點
        trigger = definition.get('trigger', {})
        trigger_node = WorkflowNode(
            node_id='trigger_1',
            node_type=WorkflowNodeType.TRIGGER,
            name='觸發器',
            config=trigger
        )
        workflow.add_node(trigger_node)
        
        # 創建動作節點
        actions = definition.get('actions', [])
        prev_node_id = 'trigger_1'
        
        for i, action in enumerate(actions):
            action_node = WorkflowNode(
                node_id=f'action_{i+1}',
                node_type=WorkflowNodeType.ACTION,
                name=action.get('type', f'動作 {i+1}'),
                config=action
            )
            workflow.add_node(action_node)
            workflow.connect_nodes(prev_node_id, action_node.node_id)
            prev_node_id = action_node.node_id
        
        # 添加輸出節點
        output_node = WorkflowNode(
            node_id='output_1',
            node_type=WorkflowNodeType.OUTPUT,
            name='輸出',
            config={}
        )
        workflow.add_node(output_node)
        workflow.connect_nodes(prev_node_id, 'output_1')
        
        # 更新模板使用統計
        template.usage_count += 1
        
        self.workflows[workflow_id] = workflow
        return workflow
    
    def generate_code(
        self,
        workflow_id: str,
        target_format: str
    ) -> str:
        """
        從工作流生成代碼
        
        Args:
            workflow_id: 工作流 ID
            target_format: 目標格式
        
        Returns:
            str: 生成的代碼
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"工作流不存在: {workflow_id}")
        
        workflow = self.workflows[workflow_id]
        
        # 將工作流轉換為配置
        config = {
            'name': workflow.name,
            'description': workflow.description,
            'nodes': [
                {
                    'id': node.node_id,
                    'type': node.node_type.value,
                    'name': node.name,
                    'config': node.config
                }
                for node in workflow.nodes.values()
            ],
            'dependencies': [],
            'actions': [
                node.config
                for node in workflow.nodes.values()
                if node.node_type == WorkflowNodeType.ACTION
            ],
            'ecosystem': 'npm'
        }
        
        return self.generator.generate(config, target_format)
    
    def get_templates_for_user(
        self,
        user_id: str
    ) -> List[WorkflowTemplate]:
        """
        獲取適合用戶技能等級的模板
        
        Args:
            user_id: 用戶 ID
        
        Returns:
            List[WorkflowTemplate]: 適合的模板列表
        """
        if user_id not in self.users:
            return list(self.templates.values())
        
        user = self.users[user_id]
        skill_levels = list(SkillLevel)
        user_level_index = skill_levels.index(user.skill_level)
        
        # 返回用戶技能等級及以下的模板
        suitable_templates = [
            template for template in self.templates.values()
            if skill_levels.index(template.difficulty) <= user_level_index
        ]
        
        return sorted(suitable_templates, key=lambda t: t.usage_count, reverse=True)
    
    def validate_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        驗證工作流
        
        Args:
            workflow_id: 工作流 ID
        
        Returns:
            Dict: 驗證結果
        """
        if workflow_id not in self.workflows:
            return {'valid': False, 'errors': ['工作流不存在']}
        
        workflow = self.workflows[workflow_id]
        errors = workflow.validate()
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'workflow_id': workflow_id,
            'node_count': len(workflow.nodes),
            'validated_at': datetime.now().isoformat()
        }
    
    def get_user_progress(self, user_id: str) -> Dict[str, Any]:
        """
        獲取用戶學習進度
        
        Args:
            user_id: 用戶 ID
        
        Returns:
            Dict: 進度信息
        """
        if user_id not in self.users:
            return {'error': '用戶不存在'}
        
        user = self.users[user_id]
        
        # 計算下一等級所需
        next_level_requirements = {
            SkillLevel.BEGINNER: {'workflows': 3, 'templates': 5},
            SkillLevel.INTERMEDIATE: {'workflows': 10, 'templates': 15},
            SkillLevel.ADVANCED: {'workflows': 25, 'templates': 30},
            SkillLevel.EXPERT: None
        }
        
        reqs = next_level_requirements.get(user.skill_level)
        progress = {}
        
        if reqs:
            progress = {
                'workflows_progress': min(100, user.workflows_created / reqs['workflows'] * 100),
                'templates_progress': min(100, user.templates_used / reqs['templates'] * 100)
            }
        
        return {
            'user_id': user_id,
            'name': user.name,
            'skill_level': user.skill_level.value,
            'workflows_created': user.workflows_created,
            'templates_used': user.templates_used,
            'tutorials_completed': user.tutorials_completed,
            'achievements': user.achievements,
            'next_level_progress': progress,
            'last_activity': user.last_activity.isoformat() if user.last_activity else None
        }
