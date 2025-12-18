"""
SynergyMesh Virtual Expert Team (虛擬專家團隊)

Phase 7: Virtual AI Experts with specialized domain expertise

This module provides virtual expert personas that serve as role models
for AI agents, providing specialized knowledge and guidance.

核心創新：
1. 憲章定義「規則」
2. 訓練系統教導「技能」
3. 虛擬專家提供「角色模型」

參考：AI 代理需要專業化和明確的角色定位 [1]
"""

from .expert_base import (
    VirtualExpert,
    ExpertPersonality,
    ExpertKnowledge,
    WorkStyle,
    CommunicationStyle,
    ExpertiseLevel,
)

from .expert_team import (
    VirtualExpertTeam,
    ExpertConsultation,
    ConsultationResult,
)

from .domain_experts import (
    # Core AI Team
    DrAlexChen,        # AI 架構師
    SarahWong,         # 自然語言處理專家
    
    # Security Team
    MarcusJohnson,     # 安全架構師
    
    # Database Team
    LiWei,             # 數據庫專家
    
    # DevOps Team
    EmmaThompson,      # DevOps 專家
    
    # Architecture Team
    JamesMiller,       # 系統架構師
)

__all__ = [
    # Base classes
    'VirtualExpert',
    'ExpertPersonality',
    'ExpertKnowledge',
    'WorkStyle',
    'CommunicationStyle',
    'ExpertiseLevel',
    # Team
    'VirtualExpertTeam',
    'ExpertConsultation',
    'ConsultationResult',
    # Domain Experts
    'DrAlexChen',
    'SarahWong',
    'MarcusJohnson',
    'LiWei',
    'EmmaThompson',
    'JamesMiller',
]

__version__ = '1.0.0'
