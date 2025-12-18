"""
技術棧矩陣
Tech Stack Matrix Module

提供前端/後端/數據/部署技術組合策略
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime


class FrontendTech(Enum):
    """前端技術"""
    REACT = "react"
    VUE = "vue"
    ANGULAR = "angular"
    SVELTE = "svelte"
    FLUTTER = "flutter"
    REACT_NATIVE = "react_native"
    NEXTJS = "nextjs"
    NUXTJS = "nuxtjs"


class BackendArch(Enum):
    """後端架構"""
    MICROSERVICES = "microservices"
    SERVERLESS = "serverless"
    MONOLITH = "monolith"
    MODULAR_MONOLITH = "modular_monolith"
    EVENT_DRIVEN = "event_driven"


class DataProcessing(Enum):
    """數據處理方式"""
    REALTIME = "realtime"
    BATCH = "batch"
    STREAMING = "streaming"
    HYBRID = "hybrid"
    LAMBDA = "lambda_architecture"


class DeploymentStrategy(Enum):
    """部署策略"""
    CLOUD_NATIVE = "cloud_native"
    HYBRID_CLOUD = "hybrid_cloud"
    EDGE = "edge"
    ON_PREMISE = "on_premise"
    MULTI_CLOUD = "multi_cloud"


@dataclass
class StackRecommendation:
    """技術棧推薦"""
    frontend: FrontendTech
    backend: BackendArch
    data_processing: DataProcessing
    deployment: DeploymentStrategy
    
    # 評估結果
    compatibility_score: float = 0.0
    complexity_rating: str = "medium"
    scalability_rating: str = "medium"
    cost_estimate: str = "medium"
    recommended_tools: Dict[str, List[str]] = field(default_factory=dict)
    considerations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'frontend': self.frontend.value,
            'backend': self.backend.value,
            'data_processing': self.data_processing.value,
            'deployment': self.deployment.value,
            'compatibility_score': self.compatibility_score,
            'complexity_rating': self.complexity_rating,
            'scalability_rating': self.scalability_rating,
            'cost_estimate': self.cost_estimate,
            'recommended_tools': self.recommended_tools,
            'considerations': self.considerations
        }


class TechStackMatrix:
    """技術棧矩陣評估器"""
    
    # 技術組合相容性矩陣
    COMPATIBILITY_MATRIX = {
        (FrontendTech.REACT, BackendArch.MICROSERVICES): 95,
        (FrontendTech.REACT, BackendArch.SERVERLESS): 90,
        (FrontendTech.REACT, BackendArch.MONOLITH): 80,
        (FrontendTech.VUE, BackendArch.MICROSERVICES): 90,
        (FrontendTech.VUE, BackendArch.SERVERLESS): 85,
        (FrontendTech.VUE, BackendArch.MONOLITH): 85,
        (FrontendTech.NEXTJS, BackendArch.SERVERLESS): 95,
        (FrontendTech.NEXTJS, BackendArch.MICROSERVICES): 90,
        (FrontendTech.FLUTTER, BackendArch.SERVERLESS): 85,
        (FrontendTech.FLUTTER, BackendArch.MICROSERVICES): 90,
        (FrontendTech.ANGULAR, BackendArch.MONOLITH): 90,
        (FrontendTech.ANGULAR, BackendArch.MICROSERVICES): 85,
    }
    
    # 數據處理與部署相容性
    DATA_DEPLOY_COMPATIBILITY = {
        (DataProcessing.REALTIME, DeploymentStrategy.CLOUD_NATIVE): 95,
        (DataProcessing.REALTIME, DeploymentStrategy.EDGE): 90,
        (DataProcessing.STREAMING, DeploymentStrategy.CLOUD_NATIVE): 95,
        (DataProcessing.STREAMING, DeploymentStrategy.HYBRID_CLOUD): 85,
        (DataProcessing.BATCH, DeploymentStrategy.ON_PREMISE): 90,
        (DataProcessing.BATCH, DeploymentStrategy.CLOUD_NATIVE): 80,
        (DataProcessing.HYBRID, DeploymentStrategy.HYBRID_CLOUD): 95,
        (DataProcessing.LAMBDA, DeploymentStrategy.CLOUD_NATIVE): 90,
    }
    
    # 推薦工具
    RECOMMENDED_TOOLS = {
        FrontendTech.REACT: ['Redux', 'React Query', 'Tailwind CSS', 'Jest'],
        FrontendTech.VUE: ['Vuex', 'Pinia', 'Vuetify', 'Vitest'],
        FrontendTech.NEXTJS: ['Prisma', 'NextAuth', 'Vercel', 'tRPC'],
        FrontendTech.FLUTTER: ['Provider', 'Riverpod', 'Firebase', 'Hive'],
        BackendArch.MICROSERVICES: ['Kubernetes', 'Docker', 'Istio', 'gRPC'],
        BackendArch.SERVERLESS: ['AWS Lambda', 'Azure Functions', 'Vercel', 'Cloudflare Workers'],
        BackendArch.MONOLITH: ['Django', 'Rails', 'Spring Boot', 'Express'],
        DataProcessing.REALTIME: ['Apache Kafka', 'Redis Streams', 'WebSocket', 'Socket.io'],
        DataProcessing.STREAMING: ['Apache Flink', 'Spark Streaming', 'Kinesis', 'Pulsar'],
        DataProcessing.BATCH: ['Apache Spark', 'Hadoop', 'Airflow', 'dbt'],
        DeploymentStrategy.CLOUD_NATIVE: ['Kubernetes', 'Helm', 'ArgoCD', 'Prometheus'],
        DeploymentStrategy.EDGE: ['Cloudflare Workers', 'Lambda@Edge', 'Fly.io', 'Deno Deploy'],
    }
    
    # 複雜度評級
    COMPLEXITY_RATINGS = {
        BackendArch.MONOLITH: 'low',
        BackendArch.MODULAR_MONOLITH: 'medium',
        BackendArch.SERVERLESS: 'medium',
        BackendArch.MICROSERVICES: 'high',
        BackendArch.EVENT_DRIVEN: 'high',
    }
    
    # 可擴展性評級
    SCALABILITY_RATINGS = {
        BackendArch.MONOLITH: 'low',
        BackendArch.MODULAR_MONOLITH: 'medium',
        BackendArch.SERVERLESS: 'very_high',
        BackendArch.MICROSERVICES: 'high',
        BackendArch.EVENT_DRIVEN: 'high',
    }
    
    # 成本估算
    COST_ESTIMATES = {
        (BackendArch.SERVERLESS, DeploymentStrategy.CLOUD_NATIVE): 'low_variable',
        (BackendArch.MICROSERVICES, DeploymentStrategy.CLOUD_NATIVE): 'high',
        (BackendArch.MONOLITH, DeploymentStrategy.ON_PREMISE): 'medium_fixed',
        (BackendArch.MICROSERVICES, DeploymentStrategy.HYBRID_CLOUD): 'very_high',
    }
    
    def __init__(self):
        self.recommendations: List[StackRecommendation] = []
    
    def evaluate_stack(
        self,
        frontend: FrontendTech,
        backend: BackendArch,
        data_processing: DataProcessing,
        deployment: DeploymentStrategy
    ) -> StackRecommendation:
        """評估技術棧組合"""
        recommendation = StackRecommendation(
            frontend=frontend,
            backend=backend,
            data_processing=data_processing,
            deployment=deployment
        )
        
        # 計算相容性分數
        frontend_backend = self.COMPATIBILITY_MATRIX.get(
            (frontend, backend), 
            75  # 預設分數
        )
        data_deploy = self.DATA_DEPLOY_COMPATIBILITY.get(
            (data_processing, deployment),
            75
        )
        recommendation.compatibility_score = (frontend_backend + data_deploy) / 2
        
        # 設定評級
        recommendation.complexity_rating = self.COMPLEXITY_RATINGS.get(backend, 'medium')
        recommendation.scalability_rating = self.SCALABILITY_RATINGS.get(backend, 'medium')
        recommendation.cost_estimate = self.COST_ESTIMATES.get(
            (backend, deployment),
            'medium'
        )
        
        # 推薦工具
        recommendation.recommended_tools = {
            'frontend': self.RECOMMENDED_TOOLS.get(frontend, []),
            'backend': self.RECOMMENDED_TOOLS.get(backend, []),
            'data': self.RECOMMENDED_TOOLS.get(data_processing, []),
            'deployment': self.RECOMMENDED_TOOLS.get(deployment, [])
        }
        
        # 生成考量事項
        recommendation.considerations = self._generate_considerations(recommendation)
        
        self.recommendations.append(recommendation)
        return recommendation
    
    def _generate_considerations(self, rec: StackRecommendation) -> List[str]:
        """生成考量事項"""
        considerations = []
        
        # 前後端考量
        if rec.frontend == FrontendTech.NEXTJS and rec.backend == BackendArch.MICROSERVICES:
            considerations.append("Next.js 的 API Routes 可簡化部分後端邏輯")
        
        if rec.frontend == FrontendTech.FLUTTER and rec.backend == BackendArch.SERVERLESS:
            considerations.append("考慮使用 Firebase 作為後端服務")
        
        # 數據處理考量
        if rec.data_processing == DataProcessing.REALTIME:
            considerations.append("確保網絡延遲足夠低以支援即時處理")
        elif rec.data_processing == DataProcessing.STREAMING:
            considerations.append("需要專門的串流處理團隊技能")
        
        # 部署考量
        if rec.deployment == DeploymentStrategy.EDGE:
            considerations.append("邊緣部署需要考慮代碼大小限制")
        elif rec.deployment == DeploymentStrategy.MULTI_CLOUD:
            considerations.append("多雲策略增加運維複雜度")
        
        # 組合特定考量
        if rec.backend == BackendArch.MICROSERVICES:
            considerations.extend([
                "需要完善的服務發現機制",
                "考慮分佈式追蹤和日誌聚合"
            ])
        
        if rec.compatibility_score < 80:
            considerations.append("⚠️ 此組合相容性較低，建議重新評估")
        
        return considerations
    
    def recommend_optimal_stack(
        self,
        project_type: str,
        team_size: int,
        scalability_need: str,
        budget_level: str
    ) -> StackRecommendation:
        """推薦最佳技術棧"""
        # 基於項目類型選擇前端
        frontend_map = {
            'web_app': FrontendTech.REACT,
            'enterprise': FrontendTech.ANGULAR,
            'startup': FrontendTech.NEXTJS,
            'mobile_first': FrontendTech.FLUTTER,
            'content': FrontendTech.VUE
        }
        frontend = frontend_map.get(project_type, FrontendTech.REACT)
        
        # 基於團隊規模選擇後端架構
        if team_size < 5:
            backend = BackendArch.MONOLITH
        elif team_size < 15:
            backend = BackendArch.MODULAR_MONOLITH if budget_level == 'low' else BackendArch.SERVERLESS
        else:
            backend = BackendArch.MICROSERVICES
        
        # 基於可擴展性需求選擇數據處理
        data_map = {
            'low': DataProcessing.BATCH,
            'medium': DataProcessing.HYBRID,
            'high': DataProcessing.STREAMING,
            'very_high': DataProcessing.REALTIME
        }
        data_processing = data_map.get(scalability_need, DataProcessing.HYBRID)
        
        # 基於預算選擇部署策略
        deploy_map = {
            'low': DeploymentStrategy.CLOUD_NATIVE,
            'medium': DeploymentStrategy.CLOUD_NATIVE,
            'high': DeploymentStrategy.HYBRID_CLOUD,
            'enterprise': DeploymentStrategy.MULTI_CLOUD
        }
        deployment = deploy_map.get(budget_level, DeploymentStrategy.CLOUD_NATIVE)
        
        return self.evaluate_stack(frontend, backend, data_processing, deployment)
    
    def compare_stacks(self, stacks: List[StackRecommendation]) -> Dict[str, Any]:
        """比較多個技術棧"""
        if not stacks:
            return {'error': '沒有可比較的技術棧'}
        
        comparison = {
            'stacks': [s.to_dict() for s in stacks],
            'best_compatibility': max(stacks, key=lambda s: s.compatibility_score).to_dict(),
            'lowest_complexity': min(stacks, key=lambda s: self._complexity_to_score(s.complexity_rating)).to_dict(),
            'highest_scalability': max(stacks, key=lambda s: self._scalability_to_score(s.scalability_rating)).to_dict(),
            'comparison_matrix': self._create_comparison_matrix(stacks)
        }
        
        return comparison
    
    def _complexity_to_score(self, rating: str) -> int:
        """複雜度轉換為分數"""
        scores = {'low': 1, 'medium': 2, 'high': 3, 'very_high': 4}
        return scores.get(rating, 2)
    
    def _scalability_to_score(self, rating: str) -> int:
        """可擴展性轉換為分數"""
        scores = {'low': 1, 'medium': 2, 'high': 3, 'very_high': 4}
        return scores.get(rating, 2)
    
    def _create_comparison_matrix(self, stacks: List[StackRecommendation]) -> List[Dict[str, Any]]:
        """創建比較矩陣"""
        matrix = []
        for stack in stacks:
            matrix.append({
                'stack': f"{stack.frontend.value}/{stack.backend.value}",
                'compatibility': stack.compatibility_score,
                'complexity': stack.complexity_rating,
                'scalability': stack.scalability_rating,
                'cost': stack.cost_estimate
            })
        return matrix
    
    def generate_stack_report(self) -> Dict[str, Any]:
        """生成技術棧報告"""
        return {
            'generated_at': datetime.now().isoformat(),
            'recommendations': [r.to_dict() for r in self.recommendations],
            'summary': {
                'total_evaluations': len(self.recommendations),
                'avg_compatibility': sum(r.compatibility_score for r in self.recommendations) / len(self.recommendations) if self.recommendations else 0,
                'most_common_frontend': self._get_most_common([r.frontend.value for r in self.recommendations]),
                'most_common_backend': self._get_most_common([r.backend.value for r in self.recommendations])
            }
        }
    
    def _get_most_common(self, items: List[str]) -> Optional[str]:
        """獲取最常見項目"""
        if not items:
            return None
        from collections import Counter
        counter = Counter(items)
        return counter.most_common(1)[0][0]
