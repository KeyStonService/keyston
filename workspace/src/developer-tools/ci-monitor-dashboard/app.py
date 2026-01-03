# ==============================================================================
# CI 監控儀表板 - 高階開發者工具
# CI Monitor Dashboard - Advanced Developer Tool
# ==============================================================================

import os
import json
import time
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import requests
from github import Github
import redis


class PipelineStatus(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    PENDING = "pending"
    RUNNING = "running"
    CANCELLED = "cancelled"


@dataclass
class PipelineMetrics:
    """流水線指標數據類"""
    pipeline_id: str
    name: str
    status: PipelineStatus
    duration: int
    queue_time: int
    timestamp: datetime
    triggered_by: str
    branch: str
    commit_sha: str
    test_count: int = 0
    test_passed: int = 0
    coverage_percent: float = 0.0
    security_issues: int = 0
    code_quality_score: float = 0.0


class CIMonitorDashboard:
    """CI 監控儀表板核心類"""
    
    def __init__(self, config_path: str = "config/ci-monitor-config.yaml"):
        self.config = self._load_config(config_path)
        self.github_client = self._init_github_client()
        self.redis_client = self._init_redis_client()
        self.app = self._create_dash_app()
        self.pipeline_data: List[PipelineMetrics] = []
        self.metrics_cache = {}
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """載入配置文件"""
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # 默認配置
            return {
                'github': {
                    'token': os.getenv('GITHUB_TOKEN'),
                    'repo': os.getenv('GITHUB_REPO', 'MachineNativeOps/MachineNativeOps')
                },
                'redis': {
                    'host': os.getenv('REDIS_HOST', 'localhost'),
                    'port': int(os.getenv('REDIS_PORT', 6379)),
                    'db': int(os.getenv('REDIS_DB', 0))
                },
                'dashboard': {
                    'title': 'CI/CD 監控儀表板',
                    'refresh_interval': 30000,  # 30秒
                    'max_history_days': 30
                }
            }
    
    def _init_github_client(self) -> Github:
        """初始化 GitHub 客戶端"""
        token = self.config['github']['token']
        if token:
            return Github(token)
        return Github()
    
    def _init_redis_client(self) -> redis.Redis:
        """初始化 Redis 客戶端"""
        try:
            redis_config = self.config['redis']
            return redis.Redis(
                host=redis_config['host'],
                port=redis_config['port'],
                db=redis_config['db'],
                decode_responses=True
            )
        except Exception:
            return None
    
    def _create_dash_app(self) -> dash.Dash:
        """創建 Dash 應用"""
        app = dash.Dash(
            __name__,
            external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
            title=self.config['dashboard']['title'],
            meta_tags=[
                {"name": "viewport", "content": "width=device-width, initial-scale=1"}
            ]
        )
        
        # 設置應用配置
        app.config.suppress_callback_exceptions = True
        app.config.update({
            'requests_pathname_prefix': '/ci-monitor/',
            'routes_pathname_prefix': '/ci-monitor/'
        })
        
        return app
    
    def fetch_github_workflows(self) -> List[Dict[str, Any]]:
        """獲取 GitHub Actions 工作流數據"""
        try:
            repo = self.github_client.get_repo(self.config['github']['repo'])
            
            workflows_data = []
            workflows = repo.get_workflows()
            
            for workflow in workflows:
                # 獲取最近的運行記錄
                runs = workflow.get_runs(per_page=10)
                
                for run in runs:
                    try:
                        run_started_at = run.run_started_at
                    except AttributeError:
                        run_started_at = None
                    workflow_data = {
                        'id': run.id,
                        'name': workflow.name,
                        'status': run.status,
                        'conclusion': run.conclusion,
                        'created_at': run.created_at,
                        'updated_at': run.updated_at,
                        'duration': (run.updated_at - run.created_at).total_seconds() if run.updated_at and run.created_at else 0,
                        'queue_time': (run_started_at - run.created_at).total_seconds() if run_started_at and run.created_at else 0,
                        'head_branch': run.head_branch,
                        'head_sha': run.head_sha,
                        'triggered_by': run.triggered_by,
                        'event': run.event
                    }
                    
                    # 獲取運行日誌和工件信息
                    try:
                        jobs = run.jobs()
                        workflow_data['jobs'] = [
                            {
                                'name': job.name,
                                'status': job.status,
                                'conclusion': job.conclusion,
                                'started_at': job.started_at,
                                'completed_at': job.completed_at
                            }
                            for job in jobs
                        ]
                    except Exception:
                        workflow_data['jobs'] = []
                    
                    workflows_data.append(workflow_data)
            
            return workflows_data
            
        except Exception as e:
            print(f"獲取 GitHub 工作流數據失敗: {e}")
            return []
    
    def fetch_pipeline_metrics(self) -> List[PipelineMetrics]:
        """獲取流水線指標"""
        workflows_data = self.fetch_github_workflows()
        
        metrics = []
        for workflow in workflows_data:
            # 轉換狀態
            status = PipelineStatus.SUCCESS
            if workflow['conclusion'] == 'failure':
                status = PipelineStatus.FAILURE
            elif workflow['conclusion'] == 'cancelled':
                status = PipelineStatus.CANCELLED
            elif workflow['status'] == 'in_progress':
                status = PipelineStatus.RUNNING
            elif workflow['status'] == 'queued':
                status = PipelineStatus.PENDING
            
            # 從 Redis 獲取詳細指標（如果可用）
            detailed_metrics = self._get_detailed_metrics_from_cache(workflow['id'])
            
            metric = PipelineMetrics(
                pipeline_id=str(workflow['id']),
                name=workflow['name'],
                status=status,
                duration=int(workflow['duration']),
                queue_time=int(workflow.get('queue_time', 0)),
                timestamp=workflow['created_at'],
                triggered_by=workflow['triggered_by'],
                branch=workflow['head_branch'],
                commit_sha=workflow['head_sha'],
                test_count=detailed_metrics.get('test_count', 0),
                test_passed=detailed_metrics.get('test_passed', 0),
                coverage_percent=detailed_metrics.get('coverage_percent', 0.0),
                security_issues=detailed_metrics.get('security_issues', 0),
                code_quality_score=detailed_metrics.get('code_quality_score', 0.0)
            )
            
            metrics.append(metric)
        
        return metrics
    
    def _get_detailed_metrics_from_cache(self, pipeline_id: str) -> Dict[str, Any]:
        """從 Redis 緩存獲取詳細指標"""
        if not self.redis_client:
            return {}
        
        try:
            cached_data = self.redis_client.hgetall(f"pipeline_metrics:{pipeline_id}")
            if cached_data:
                return {
                    'test_count': int(cached_data.get('test_count', 0)),
                    'test_passed': int(cached_data.get('test_passed', 0)),
                    'coverage_percent': float(cached_data.get('coverage_percent', 0.0)),
                    'security_issues': int(cached_data.get('security_issues', 0)),
                    'code_quality_score': float(cached_data.get('code_quality_score', 0.0))
                }
        except Exception as e:
            print(f"從緩存獲取指標失敗: {e}")
        
        return {}
    
    def create_layout(self) -> html.Div:
        """創建儀表板佈局"""
        return dbc.Container([
            # 頭部
            dbc.Row([
                dbc.Col([
                    html.H1([
                        html.I(className="bi bi-activity me-2"),
                        self.config['dashboard']['title']
                    ], className="text-center mb-4"),
                    html.P("實時監控 CI/CD 流水線狀態與性能指標", 
                          className="text-center text-muted mb-4")
                ])
            ]),
            
            # 總覽卡片
            dbc.Row([
                dbc.Col([
                    self._create_overview_cards()
                ], width=12)
            ], className="mb-4"),
            
            # 組織月度指標卡片
            dbc.Row([
                dbc.Col([
                    self._create_org_overview_cards()
                ], width=12)
            ], className="mb-4"),
            
            # 圖表區域
            dbc.Row([
                # 流水線狀態分佈
                dbc.Col([
                    dcc.Graph(
                        id="status-distribution-chart",
                        config={'displayModeBar': False}
                    )
                ], width=4),
                
                # 執行時間趨勢
                dbc.Col([
                    dcc.Graph(
                        id="duration-trend-chart",
                        config={'displayModeBar': False}
                    )
                ], width=8),
            ], className="mb-4"),
            
            # 詳細指標
            dbc.Row([
                # 測試覆蓋率趨勢
                dbc.Col([
                    dcc.Graph(
                        id="coverage-trend-chart",
                        config={'displayModeBar': False}
                    )
                ], width=6),
                
                # 代碼品質評分
                dbc.Col([
                    dcc.Graph(
                        id="quality-score-chart",
                        config={'displayModeBar': False}
                    )
                ], width=6),
            ], className="mb-4"),
            
            # 流水線詳細表格
            dbc.Row([
                dbc.Col([
                    self._create_pipeline_table()
                ], width=12)
            ], className="mb-4"),
            
            # 自動刷新間隔
            dcc.Interval(
                id='interval-component',
                interval=self.config['dashboard']['refresh_interval'],
                n_intervals=0
            ),
            
            # 存儲組件
            dcc.Store(id='pipeline-data-store')
            
        ], fluid=True)
    
    def _create_overview_cards(self) -> html.Div:
        """創建總覽卡片"""
        return dbc.Row([
            # 成功率卡片
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4([
                            html.I(className="bi bi-check-circle me-2 text-success"),
                            html.Span("成功率", id="success-rate-value")
                        ], className="card-title"),
                        html.P("過去7天流水線成功率", className="card-text text-muted")
                    ])
                ], color="light")
            ], width=3),
            
            # 平均執行時間卡片
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4([
                            html.I(className="bi bi-clock me-2 text-info"),
                            html.Span("0分鐘", id="avg-duration-value")
                        ], className="card-title"),
                        html.P("平均執行時間", className="card-text text-muted")
                    ])
                ], color="light")
            ], width=3),
            
            # 活躍流水線卡片
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4([
                            html.I(className="bi bi-lightning me-2 text-warning"),
                            html.Span("0", id="active-pipelines-value")
                        ], className="card-title"),
                        html.P("正在運行的流水線", className="card-text text-muted")
                    ])
                ], color="light")
            ], width=3),
            
            # 安全問題卡片
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4([
                            html.I(className="bi bi-shield-exclamation me-2 text-danger"),
                            html.Span("0", id="security-issues-value")
                        ], className="card-title"),
                        html.P("待解決的安全問題", className="card-text text-muted")
                    ])
                ], color="light")
            ], width=3),
        ])
    
    def _create_org_overview_cards(self) -> html.Div:
        """創建組織月度指標卡片"""
        return dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("平均作業運行時間", className="card-title mb-2"),
                        html.H2(html.Span("0秒", id="org-avg-runtime"), className="mb-0"),
                        html.P("本組織本月作業的平均運行時間", className="text-muted mb-0")
                    ])
                ], color="light")
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("平均作業排隊時間", className="card-title mb-2"),
                        html.H2(html.Span("0秒", id="org-avg-queue"), className="mb-0"),
                        html.P("本組織本月作業平均排隊時間", className="text-muted mb-0")
                    ])
                ], color="light")
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("工作失敗率", className="card-title mb-2"),
                        html.H2(html.Span("0%", id="org-failure-rate"), className="mb-0"),
                        html.P("本組織本月各項工作的失敗率", className="text-muted mb-0")
                    ])
                ], color="light")
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("失敗的作業使用", className="card-title mb-2"),
                        html.H2(html.Span("0秒", id="org-failed-usage"), className="mb-0"),
                        html.P("本組織本月所有失敗作業所用總時長", className="text-muted mb-0")
                    ])
                ], color="light")
            ], width=3),
        ])
    
    def _create_pipeline_table(self) -> html.Div:
        """創建流水線詳細表格"""
        return dbc.Card([
            dbc.CardHeader([
                html.H5([
                    html.I(className="bi bi-table me-2"),
                    "流水線詳細記錄"
                ], className="mb-0")
            ]),
            dbc.CardBody([
                html.Div(id="pipeline-table-container")
            ])
        ])
    
    def setup_callbacks(self):
        """設置回調函數"""
        
        @self.app.callback(
            [
                Output('pipeline-data-store', 'data'),
                Output('success-rate-value', 'children'),
                Output('avg-duration-value', 'children'),
                Output('active-pipelines-value', 'children'),
                Output('security-issues-value', 'children'),
                Output('org-avg-runtime', 'children'),
                Output('org-avg-queue', 'children'),
                Output('org-failure-rate', 'children'),
                Output('org-failed-usage', 'children')
            ],
            [Input('interval-component', 'n_intervals')]
        )
        def update_data(n_intervals):
            """更新數據"""
            # 獲取流水線數據
            metrics = self.fetch_pipeline_metrics()
            
            # 計算總覽指標
            if metrics:
                current_time = datetime.now(timezone.utc)
                # 計算成功率（過去7天）
                seven_days_ago = current_time - timedelta(days=7)
                recent_metrics = [m for m in metrics if m.timestamp > seven_days_ago]
                
                success_count = sum(1 for m in recent_metrics if m.status == PipelineStatus.SUCCESS)
                success_rate = (success_count / len(recent_metrics) * 100) if recent_metrics else 0
                
                # 計算平均執行時間
                completed_metrics = [m for m in metrics if m.duration > 0]
                avg_duration = sum(m.duration for m in completed_metrics) / len(completed_metrics) if completed_metrics else 0
                
                # 計算活躍流水線數
                active_count = sum(1 for m in metrics if m.status == PipelineStatus.RUNNING)
                
                # 計算安全問題總數
                security_issues = sum(m.security_issues for m in metrics)
                
                # 計算本月組織指標
                month_ago = current_time - timedelta(days=30)
                monthly_metrics = [m for m in metrics if m.timestamp > month_ago]
                total_monthly = len(monthly_metrics)
                runtime_sum = queue_sum = failure_count_month = failed_usage_month = 0
                
                for m in monthly_metrics:
                    runtime_sum += m.duration
                    queue_sum += m.queue_time
                    if m.status == PipelineStatus.FAILURE:
                        failure_count_month += 1
                        failed_usage_month += m.duration
                
                avg_runtime_month = (runtime_sum / total_monthly) if total_monthly else 0
                avg_queue_month = (queue_sum / total_monthly) if total_monthly else 0
                failure_rate_month = (failure_count_month / total_monthly * 100) if total_monthly else 0
                
                return [
                    [self._metric_to_dict(m) for m in metrics],
                    f"{success_rate:.1f}%",
                    f"{avg_duration/60:.1f}分鐘",
                    str(active_count),
                    str(security_issues),
                    f"{avg_runtime_month:.0f}秒",
                    f"{avg_queue_month:.0f}秒",
                    f"{failure_rate_month:.1f}%",
                    f"{failed_usage_month:.0f}秒"
                ]
            else:
                return [[], "0%", "0分鐘", "0", "0", "0秒", "0秒", "0%", "0秒"]
        
        @self.app.callback(
            Output('status-distribution-chart', 'figure'),
            [Input('pipeline-data-store', 'data')]
        )
        def update_status_distribution(data):
            """更新狀態分佈圖"""
            if not data:
                return go.Figure()
            
            # 統計各狀態數量
            status_counts = {}
            for metric in data:
                status = metric['status']
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # 創建餅圖
            fig = go.Figure(data=[
                go.Pie(
                    labels=list(status_counts.keys()),
                    values=list(status_counts.values()),
                    hole=0.3,
                    marker_colors=['#28a745', '#dc3545', '#ffc107', '#17a2b8', '#6c757d']
                )
            ])
            
            fig.update_layout(
                title="流水線狀態分佈",
                height=300,
                showlegend=True,
                font=dict(size=12)
            )
            
            return fig
        
        @self.app.callback(
            Output('duration-trend-chart', 'figure'),
            [Input('pipeline-data-store', 'data')]
        )
        def update_duration_trend(data):
            """更新執行時間趨勢圖"""
            if not data:
                return go.Figure()
            
            # 按時間排序
            sorted_data = sorted(data, key=lambda x: x['timestamp'])
            
            # 提取數據
            timestamps = [datetime.fromisoformat(x['timestamp'].replace('Z', '+00:00')) for x in sorted_data[-20:]]  # 最近20條
            durations = [x['duration']/60 for x in sorted_data[-20:]]  # 轉換為分鐘
            pipeline_names = [x['name'] for x in sorted_data[-20:]]
            
            fig = go.Figure()
            
            # 添加趨勢線
            fig.add_trace(go.Scatter(
                x=timestamps,
                y=durations,
                mode='lines+markers',
                name='執行時間',
                line=dict(color='#007bff', width=2),
                marker=dict(size=6),
                hovertemplate='<b>%{fullData.name}</b><br>' +
                             '時間: %{x}<br>' +
                             '執行時間: %{y:.1f} 分鐘<br>' +
                             '流水線: %{text}<extra></extra>',
                text=pipeline_names
            ))
            
            fig.update_layout(
                title="流水線執行時間趨勢",
                height=300,
                xaxis_title="時間",
                yaxis_title="執行時間 (分鐘)",
                hovermode='x unified',
                font=dict(size=12)
            )
            
            return fig
        
        @self.app.callback(
            Output('coverage-trend-chart', 'figure'),
            [Input('pipeline-data-store', 'data')]
        )
        def update_coverage_trend(data):
            """更新測試覆蓋率趨勢"""
            if not data:
                return go.Figure()
            
            # 過濾有覆蓋率數據的記錄
            coverage_data = [x for x in data if x['coverage_percent'] > 0]
            
            if not coverage_data:
                return go.Figure()
            
            # 按時間排序
            sorted_data = sorted(coverage_data, key=lambda x: x['timestamp'])
            
            timestamps = [datetime.fromisoformat(x['timestamp'].replace('Z', '+00:00')) for x in sorted_data[-15:]]
            coverage = [x['coverage_percent'] for x in sorted_data[-15:]]
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=timestamps,
                y=coverage,
                mode='lines+markers',
                name='測試覆蓋率',
                line=dict(color='#28a745', width=2),
                marker=dict(size=6),
                fill='tonexty',
                fillcolor='rgba(40, 167, 69, 0.1)'
            ))
            
            # 添加目標線
            fig.add_hline(y=80, line_dash="dash", line_color="red", annotation_text="目標: 80%")
            
            fig.update_layout(
                title="測試覆蓋率趨勢",
                height=300,
                xaxis_title="時間",
                yaxis_title="覆蓋率 (%)",
                yaxis=dict(range=[0, 100]),
                hovermode='x unified',
                font=dict(size=12)
            )
            
            return fig
        
        @self.app.callback(
            Output('quality-score-chart', 'figure'),
            [Input('pipeline-data-store', 'data')]
        )
        def update_quality_score(data):
            """更新代碼品質評分圖"""
            if not data:
                return go.Figure()
            
            # 過濾有品質分數的記錄
            quality_data = [x for x in data if x['code_quality_score'] > 0]
            
            if not quality_data:
                return go.Figure()
            
            # 按流水線分組
            pipeline_scores = {}
            for metric in quality_data:
                name = metric['name']
                if name not in pipeline_scores:
                    pipeline_scores[name] = []
                pipeline_scores[name].append(metric['code_quality_score'])
            
            # 計算平均值
            avg_scores = {name: sum(scores)/len(scores) for name, scores in pipeline_scores.items()}
            
            names = list(avg_scores.keys())
            scores = list(avg_scores.values())
            
            # 根據分數設置顏色
            colors = ['#28a745' if score >= 8 else '#ffc107' if score >= 6 else '#dc3545' for score in scores]
            
            fig = go.Figure(data=[
                go.Bar(
                    x=names,
                    y=scores,
                    marker_color=colors,
                    hovertemplate='<b>%{x}</b><br>品質分數: %{y:.1f}<extra></extra>'
                )
            ])
            
            fig.update_layout(
                title="各流水線代碼品質評分",
                height=300,
                xaxis_title="流水線",
                yaxis_title="品質分數",
                yaxis=dict(range=[0, 10]),
                font=dict(size=12)
            )
            
            return fig
        
        @self.app.callback(
            Output('pipeline-table-container', 'children'),
            [Input('pipeline-data-store', 'data')]
        )
        def update_pipeline_table(data):
            """更新流水線表格"""
            if not data:
                return html.P("暫無數據", className="text-center text-muted")
            
            # 按時間倒序排列
            sorted_data = sorted(data, key=lambda x: x['timestamp'], reverse=True)[:10]  # 最近10條
            
            # 創建表格數據
            table_data = []
            for metric in sorted_data:
                status_badge = self._create_status_badge(metric['status'])
                
                row = html.Tr([
                    html.Td(metric['name']),
                    html.Td(metric['branch']),
                    html.Td(status_badge),
                    html.Td(f"{metric['duration']/60:.1f}分"),
                    html.Td(f"{metric['coverage_percent']:.1f}%" if metric['coverage_percent'] > 0 else "-"),
                    html.Td(metric['security_issues'] if metric['security_issues'] > 0 else "-"),
                    html.Td(datetime.fromisoformat(metric['timestamp'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M'))
                ])
                
                table_data.append(row)
            
            # 創建表格
            table = dbc.Table([
                html.Thead([
                    html.Tr([
                        html.Th("流水線"),
                        html.Th("分支"),
                        html.Th("狀態"),
                        html.Th("執行時間"),
                        html.Th("覆蓋率"),
                        html.Th("安全問題"),
                        html.Th("執行時間")
                    ])
                ]),
                html.Tbody(table_data)
            ], striped=True, bordered=True, hover=True, responsive=True, size="sm")
            
            return table
    
    def _create_status_badge(self, status: str) -> dbc.Badge:
        """創建狀態徽章"""
        status_config = {
            'success': {'color': 'success', 'text': '成功', 'icon': 'check-circle'},
            'failure': {'color': 'danger', 'text': '失敗', 'icon': 'x-circle'},
            'running': {'color': 'info', 'text': '運行中', 'icon': 'arrow-repeat'},
            'pending': {'color': 'warning', 'text': '等待中', 'icon': 'clock'},
            'cancelled': {'color': 'secondary', 'text': '已取消', 'icon': 'x-circle'}
        }
        
        config = status_config.get(status, status_config['pending'])
        
        return dbc.Badge([
            html.I(className=f"bi bi-{config['icon']} me-1"),
            config['text']
        ], color=config['color'])
    
    def _metric_to_dict(self, metric: PipelineMetrics) -> Dict[str, Any]:
        """將 PipelineMetrics 轉換為字典"""
        return {
            'pipeline_id': metric.pipeline_id,
            'name': metric.name,
            'status': metric.status.value,
            'duration': metric.duration,
            'queue_time': metric.queue_time,
            'timestamp': metric.timestamp.isoformat(),
            'triggered_by': metric.triggered_by,
            'branch': metric.branch,
            'commit_sha': metric.commit_sha,
            'test_count': metric.test_count,
            'test_passed': metric.test_passed,
            'coverage_percent': metric.coverage_percent,
            'security_issues': metric.security_issues,
            'code_quality_score': metric.code_quality_score
        }
    
    def run(self, host: str = "0.0.0.0", port: int = 8050, debug: bool = False):
        """運行應用"""
        self.app.layout = self.create_layout()
        self.setup_callbacks()
        
        print(f"CI 監控儀表板啟動: http://{host}:{port}/ci-monitor/")
        self.app.run_server(host=host, port=port, debug=debug)


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="CI 監控儀表板")
    parser.add_argument("--host", default="0.0.0.0", help="主機地址")
    parser.add_argument("--port", type=int, default=8050, help="端口號")
    parser.add_argument("--debug", action="store_true", help="調試模式")
    parser.add_argument("--config", default="config/ci-monitor-config.yaml", help="配置文件路徑")
    
    args = parser.parse_args()
    
    # 創建並運行儀表板
    dashboard = CIMonitorDashboard(args.config)
    dashboard.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
