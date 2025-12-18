"""
Web3 整合模組
Web3 Integration Module

提供區塊鏈、DApp、NFT、智能合約整合評估和策略
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime


class BlockchainType(Enum):
    """區塊鏈類型"""
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    SOLANA = "solana"
    AVALANCHE = "avalanche"
    BINANCE_SMART_CHAIN = "bsc"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"


class ConsensusType(Enum):
    """共識機制"""
    PROOF_OF_WORK = "pow"
    PROOF_OF_STAKE = "pos"
    DELEGATED_POS = "dpos"
    PROOF_OF_AUTHORITY = "poa"


class NFTAssetType(Enum):
    """NFT 資產類型"""
    ART = "art"
    COLLECTIBLE = "collectible"
    GAMING = "gaming"
    MUSIC = "music"
    VIDEO = "video"
    REAL_ESTATE = "real_estate"
    MEMBERSHIP = "membership"
    TICKET = "ticket"


@dataclass
class DAppAssessment:
    """DApp 開發評估"""
    project_name: str
    blockchain: BlockchainType
    consensus: ConsensusType
    use_case: str
    decentralization_level: int  # 1-10
    gas_optimization_needed: bool
    smart_contract_complexity: str  # low, medium, high
    estimated_tps_requirement: int
    
    # 評估結果
    feasibility_score: float = 0.0
    recommended_blockchain: Optional[BlockchainType] = None
    risks: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'project_name': self.project_name,
            'blockchain': self.blockchain.value,
            'consensus': self.consensus.value,
            'use_case': self.use_case,
            'decentralization_level': self.decentralization_level,
            'gas_optimization_needed': self.gas_optimization_needed,
            'smart_contract_complexity': self.smart_contract_complexity,
            'estimated_tps_requirement': self.estimated_tps_requirement,
            'feasibility_score': self.feasibility_score,
            'recommended_blockchain': self.recommended_blockchain.value if self.recommended_blockchain else None,
            'risks': self.risks,
            'recommendations': self.recommendations
        }


@dataclass
class NFTStrategy:
    """NFT 應用策略"""
    asset_type: NFTAssetType
    marketplace_strategy: str  # owned, third_party, hybrid
    royalty_percentage: float
    minting_approach: str  # lazy, batch, on_demand
    storage_type: str  # ipfs, arweave, centralized
    
    # 策略建議
    estimated_gas_cost: float = 0.0
    market_potential_score: float = 0.0
    technical_complexity: str = "medium"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'asset_type': self.asset_type.value,
            'marketplace_strategy': self.marketplace_strategy,
            'royalty_percentage': self.royalty_percentage,
            'minting_approach': self.minting_approach,
            'storage_type': self.storage_type,
            'estimated_gas_cost': self.estimated_gas_cost,
            'market_potential_score': self.market_potential_score,
            'technical_complexity': self.technical_complexity
        }


@dataclass
class SmartContractDev:
    """智能合約開發評估"""
    contract_type: str  # token, defi, nft, dao, custom
    programming_language: str  # solidity, vyper, rust
    security_audit_required: bool
    upgrade_pattern: str  # proxy, diamond, immutable
    
    # 評估結果
    estimated_development_hours: int = 0
    estimated_audit_cost: float = 0.0
    security_risks: List[str] = field(default_factory=list)
    best_practices: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'contract_type': self.contract_type,
            'programming_language': self.programming_language,
            'security_audit_required': self.security_audit_required,
            'upgrade_pattern': self.upgrade_pattern,
            'estimated_development_hours': self.estimated_development_hours,
            'estimated_audit_cost': self.estimated_audit_cost,
            'security_risks': self.security_risks,
            'best_practices': self.best_practices
        }


class Web3Integration:
    """Web3 整合評估器"""
    
    # 區塊鏈特性
    BLOCKCHAIN_SPECS = {
        BlockchainType.ETHEREUM: {
            'tps': 15,
            'avg_gas_price': 30,  # gwei
            'finality': 12,  # blocks
            'smart_contract': True,
            'ecosystem_maturity': 10
        },
        BlockchainType.POLYGON: {
            'tps': 7000,
            'avg_gas_price': 30,  # gwei but much cheaper
            'finality': 128,
            'smart_contract': True,
            'ecosystem_maturity': 8
        },
        BlockchainType.SOLANA: {
            'tps': 65000,
            'avg_gas_price': 0.00025,
            'finality': 0.4,  # seconds
            'smart_contract': True,
            'ecosystem_maturity': 7
        },
        BlockchainType.AVALANCHE: {
            'tps': 4500,
            'avg_gas_price': 25,
            'finality': 1,
            'smart_contract': True,
            'ecosystem_maturity': 7
        },
        BlockchainType.BINANCE_SMART_CHAIN: {
            'tps': 300,
            'avg_gas_price': 5,
            'finality': 3,
            'smart_contract': True,
            'ecosystem_maturity': 8
        }
    }
    
    # 智能合約開發估算
    CONTRACT_ESTIMATES = {
        'token': {'hours': 40, 'audit_cost': 5000},
        'defi': {'hours': 200, 'audit_cost': 30000},
        'nft': {'hours': 80, 'audit_cost': 10000},
        'dao': {'hours': 120, 'audit_cost': 20000},
        'custom': {'hours': 160, 'audit_cost': 25000}
    }
    
    def __init__(self):
        self.assessments: List[DAppAssessment] = []
        self.nft_strategies: List[NFTStrategy] = []
        self.contracts: List[SmartContractDev] = []
    
    def assess_dapp(self, assessment: DAppAssessment) -> DAppAssessment:
        """評估 DApp 開發可行性"""
        # 計算可行性分數
        score = 0.0
        
        # 區塊鏈匹配度
        specs = self.BLOCKCHAIN_SPECS.get(assessment.blockchain, {})
        if specs:
            # TPS 需求匹配
            if specs['tps'] >= assessment.estimated_tps_requirement:
                score += 30
            else:
                assessment.risks.append(f"區塊鏈 TPS ({specs['tps']}) 可能無法滿足需求 ({assessment.estimated_tps_requirement})")
            
            # 生態系統成熟度
            score += specs['ecosystem_maturity'] * 3
            
            # Gas 優化考量
            if assessment.gas_optimization_needed and specs['avg_gas_price'] > 20:
                assessment.risks.append("需要 Gas 優化，建議考慮 L2 解決方案")
                score -= 10
        
        # 去中心化程度
        score += assessment.decentralization_level * 2
        
        # 複雜度調整
        complexity_penalty = {'low': 0, 'medium': -5, 'high': -15}
        score += complexity_penalty.get(assessment.smart_contract_complexity, -10)
        
        # 最終分數標準化
        assessment.feasibility_score = max(0, min(100, score))
        
        # 推薦區塊鏈
        assessment.recommended_blockchain = self._recommend_blockchain(assessment)
        
        # 生成建議
        assessment.recommendations = self._generate_dapp_recommendations(assessment)
        
        self.assessments.append(assessment)
        return assessment
    
    def _recommend_blockchain(self, assessment: DAppAssessment) -> BlockchainType:
        """推薦最適合的區塊鏈"""
        best_match = assessment.blockchain
        best_score = 0
        
        for blockchain, specs in self.BLOCKCHAIN_SPECS.items():
            score = 0
            
            # TPS 匹配
            if specs['tps'] >= assessment.estimated_tps_requirement:
                score += 30
            
            # Gas 成本
            if assessment.gas_optimization_needed:
                score += max(0, 30 - specs['avg_gas_price'])
            
            # 生態系統
            score += specs['ecosystem_maturity'] * 4
            
            if score > best_score:
                best_score = score
                best_match = blockchain
        
        return best_match
    
    def _generate_dapp_recommendations(self, assessment: DAppAssessment) -> List[str]:
        """生成 DApp 開發建議"""
        recommendations = []
        
        if assessment.feasibility_score >= 70:
            recommendations.append("✅ 項目可行性高，建議按計畫推進")
        elif assessment.feasibility_score >= 50:
            recommendations.append("⚠️ 項目可行性中等，建議進行進一步技術驗證")
        else:
            recommendations.append("❌ 項目可行性較低，建議重新評估技術選型")
        
        if assessment.recommended_blockchain != assessment.blockchain:
            recommendations.append(f"💡 建議考慮使用 {assessment.recommended_blockchain.value} 替代 {assessment.blockchain.value}")
        
        if assessment.smart_contract_complexity == 'high':
            recommendations.append("🔒 複雜度高，強烈建議進行安全審計")
        
        return recommendations
    
    def evaluate_nft_strategy(self, strategy: NFTStrategy) -> NFTStrategy:
        """評估 NFT 策略"""
        # 市場潛力評估
        market_scores = {
            NFTAssetType.ART: 8,
            NFTAssetType.COLLECTIBLE: 7,
            NFTAssetType.GAMING: 9,
            NFTAssetType.MUSIC: 6,
            NFTAssetType.VIDEO: 5,
            NFTAssetType.REAL_ESTATE: 7,
            NFTAssetType.MEMBERSHIP: 8,
            NFTAssetType.TICKET: 6
        }
        strategy.market_potential_score = market_scores.get(strategy.asset_type, 5) * 10
        
        # Gas 成本估算
        minting_costs = {
            'lazy': 0.01,
            'batch': 0.05,
            'on_demand': 0.02
        }
        storage_costs = {
            'ipfs': 0.01,
            'arweave': 0.05,
            'centralized': 0.001
        }
        strategy.estimated_gas_cost = minting_costs.get(strategy.minting_approach, 0.02) + storage_costs.get(strategy.storage_type, 0.01)
        
        # 技術複雜度
        complexity_map = {
            ('owned', 'batch'): 'high',
            ('owned', 'lazy'): 'medium',
            ('third_party', 'lazy'): 'low',
            ('hybrid', 'on_demand'): 'medium'
        }
        strategy.technical_complexity = complexity_map.get(
            (strategy.marketplace_strategy, strategy.minting_approach), 
            'medium'
        )
        
        self.nft_strategies.append(strategy)
        return strategy
    
    def evaluate_smart_contract(self, contract: SmartContractDev) -> SmartContractDev:
        """評估智能合約開發"""
        estimates = self.CONTRACT_ESTIMATES.get(contract.contract_type, self.CONTRACT_ESTIMATES['custom'])
        
        contract.estimated_development_hours = estimates['hours']
        contract.estimated_audit_cost = estimates['audit_cost'] if contract.security_audit_required else 0
        
        # 安全風險
        contract.security_risks = self._identify_security_risks(contract)
        
        # 最佳實踐
        contract.best_practices = self._generate_best_practices(contract)
        
        self.contracts.append(contract)
        return contract
    
    def _identify_security_risks(self, contract: SmartContractDev) -> List[str]:
        """識別安全風險"""
        risks = []
        
        if contract.contract_type == 'defi':
            risks.extend([
                "重入攻擊風險",
                "閃電貸攻擊風險",
                "預言機操縱風險",
                "前端運行風險"
            ])
        elif contract.contract_type == 'token':
            risks.extend([
                "無限鑄造漏洞",
                "轉帳邏輯錯誤",
                "授權管理不當"
            ])
        elif contract.contract_type == 'nft':
            risks.extend([
                "元數據篡改",
                "鑄造邏輯漏洞",
                "版稅規避"
            ])
        
        if contract.upgrade_pattern == 'proxy':
            risks.append("代理合約存儲衝突風險")
        
        if not contract.security_audit_required:
            risks.append("⚠️ 未計劃安全審計，風險較高")
        
        return risks
    
    def _generate_best_practices(self, contract: SmartContractDev) -> List[str]:
        """生成最佳實踐建議"""
        practices = [
            "使用經過審計的標準庫 (OpenZeppelin)",
            "實施完整的單元測試覆蓋",
            "進行模糊測試和形式化驗證",
            "部署前在測試網充分測試"
        ]
        
        if contract.programming_language == 'solidity':
            practices.append("使用 Solidity 0.8.x 以獲得內建溢出檢查")
        
        if contract.upgrade_pattern != 'immutable':
            practices.append("使用 UUPS 或透明代理模式進行升級")
        
        if contract.contract_type == 'defi':
            practices.extend([
                "實施時間鎖和多簽機制",
                "設置合理的滑點保護"
            ])
        
        return practices
    
    def generate_web3_report(self) -> Dict[str, Any]:
        """生成 Web3 整合報告"""
        return {
            'generated_at': datetime.now().isoformat(),
            'dapp_assessments': [a.to_dict() for a in self.assessments],
            'nft_strategies': [s.to_dict() for s in self.nft_strategies],
            'smart_contracts': [c.to_dict() for c in self.contracts],
            'summary': {
                'total_dapps': len(self.assessments),
                'total_nft_strategies': len(self.nft_strategies),
                'total_contracts': len(self.contracts),
                'avg_feasibility_score': sum(a.feasibility_score for a in self.assessments) / len(self.assessments) if self.assessments else 0
            }
        }
