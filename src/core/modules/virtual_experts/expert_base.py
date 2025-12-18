"""
Virtual Expert Base Classes (虛擬專家基礎類)

Defines the foundation for virtual expert personas including:
- Expert personality traits
- Knowledge domains
- Work and communication styles

參考：知識庫為不同角色提供專業化資源 [2]
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ExpertiseLevel(Enum):
    """Expertise level for domain knowledge."""
    NOVICE = "novice"
    COMPETENT = "competent"
    PROFICIENT = "proficient"
    EXPERT = "expert"
    MASTER = "master"


@dataclass
class ExpertPersonality:
    """
    Personality traits of a virtual expert.
    
    虛擬專家的性格特徵
    """
    traits: list[str] = field(default_factory=list)
    # e.g., ["analytical", "methodical", "patient", "detail-oriented"]

    motto: str = ""
    # Personal philosophy or catchphrase

    approach: str = ""
    # How they typically approach problems

    strengths: list[str] = field(default_factory=list)
    # What they excel at

    working_preferences: list[str] = field(default_factory=list)
    # How they prefer to work


@dataclass
class WorkStyle:
    """
    Work style characteristics.
    
    工作風格特徵
    """
    methodology: str = ""
    # e.g., "data-driven", "intuition-based", "collaborative"

    pace: str = "balanced"
    # "fast", "methodical", "balanced"

    attention_to_detail: str = "high"
    # "low", "medium", "high"

    risk_tolerance: str = "medium"
    # "low", "medium", "high"

    collaboration_style: str = "team-oriented"
    # "independent", "team-oriented", "mentoring"

    decision_making: str = "analytical"
    # "intuitive", "analytical", "consensus-based"


@dataclass
class CommunicationStyle:
    """
    Communication style preferences.
    
    溝通風格偏好
    """
    tone: str = "professional"
    # "formal", "professional", "casual", "friendly"

    verbosity: str = "balanced"
    # "concise", "balanced", "detailed"

    explanation_style: str = "example-based"
    # "technical", "example-based", "analogy-based"

    feedback_style: str = "constructive"
    # "direct", "constructive", "encouraging"

    preferred_format: str = "structured"
    # "freeform", "structured", "visual"

    languages: list[str] = field(default_factory=lambda: ["english", "chinese"])


@dataclass
class ExpertKnowledge:
    """
    Domain knowledge of a virtual expert.
    
    虛擬專家的領域知識
    """
    primary_domains: list[str] = field(default_factory=list)
    # Main areas of expertise

    secondary_domains: list[str] = field(default_factory=list)
    # Supporting areas of knowledge

    specializations: list[str] = field(default_factory=list)
    # Specific specializations within domains

    certifications: list[str] = field(default_factory=list)
    # Professional certifications

    years_of_experience: int = 10
    # Years of experience in the field

    notable_achievements: list[str] = field(default_factory=list)
    # Notable accomplishments

    publications: list[str] = field(default_factory=list)
    # Papers or articles published

    tools_expertise: dict[str, ExpertiseLevel] = field(default_factory=dict)
    # Tools and their proficiency levels

    methodologies: list[str] = field(default_factory=list)
    # Methodologies they're proficient in


@dataclass
class VirtualExpert:
    """
    Virtual Expert base class.
    
    虛擬專家基礎類
    
    每個虛擬專家代表一個特定領域的專業角色，
    提供專業知識、指導和最佳實踐建議。
    """
    # Identity
    id: str
    name: str
    title: str
    avatar: str  # Emoji or icon

    # Role
    role: str
    department: str

    # Characteristics
    personality: ExpertPersonality = field(default_factory=ExpertPersonality)
    knowledge: ExpertKnowledge = field(default_factory=ExpertKnowledge)
    work_style: WorkStyle = field(default_factory=WorkStyle)
    communication_style: CommunicationStyle = field(default_factory=CommunicationStyle)

    # Availability
    availability: str = "available"  # "available", "busy", "offline"

    # Stats
    consultations_completed: int = 0
    satisfaction_rating: float = 0.0

    def can_handle(self, query_domains: list[str]) -> bool:
        """Check if expert can handle queries in given domains."""
        all_domains = (
            self.knowledge.primary_domains +
            self.knowledge.secondary_domains +
            self.knowledge.specializations
        )
        return any(domain in all_domains for domain in query_domains)

    def get_expertise_level(self, domain: str) -> ExpertiseLevel:
        """Get expertise level for a specific domain."""
        if domain in self.knowledge.primary_domains:
            return ExpertiseLevel.MASTER
        elif domain in self.knowledge.specializations:
            return ExpertiseLevel.EXPERT
        elif domain in self.knowledge.secondary_domains:
            return ExpertiseLevel.PROFICIENT
        return ExpertiseLevel.NOVICE

    def introduce(self) -> str:
        """Expert self-introduction."""
        intro = f"""
{self.avatar} **{self.name}**
*{self.title}*

{self.personality.motto}

**專業領域 (Primary Domains)**:
{', '.join(self.knowledge.primary_domains)}

**專長 (Specializations)**:
{', '.join(self.knowledge.specializations)}

**工作風格 (Work Style)**:
- 方法論: {self.work_style.methodology}
- 決策方式: {self.work_style.decision_making}
- 協作風格: {self.work_style.collaboration_style}

**經驗**: {self.knowledge.years_of_experience} 年

**如何幫助您 (How I Can Help)**:
{self.personality.approach}
"""
        return intro.strip()

    def format_response(self, content: str, include_signature: bool = True) -> str:
        """Format a response in the expert's communication style."""
        formatted = content

        if include_signature:
            formatted += f"\n\n---\n{self.avatar} *{self.name} | {self.title}*"

        return formatted

    def provide_guidance(self, topic: str, context: dict[str, Any]) -> dict[str, Any]:
        """
        Provide expert guidance on a topic.
        
        This is the base implementation. Specialized experts should override.
        """
        return {
            "expert": self.name,
            "topic": topic,
            "guidance": f"As a {self.role}, I would approach {topic} by...",
            "recommendations": [],
            "best_practices": [],
            "warnings": [],
        }

    def review_code(self, code: str, language: str) -> dict[str, Any]:
        """
        Review code from expert's perspective.
        
        This is the base implementation. Specialized experts should override.
        """
        return {
            "expert": self.name,
            "language": language,
            "issues": [],
            "suggestions": [],
            "quality_score": 0.0,
        }

    def answer_question(self, question: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Answer a question from expert's perspective.
        
        This is the base implementation. Specialized experts should override.
        """
        return {
            "expert": self.name,
            "question": question,
            "answer": "",
            "related_topics": [],
            "further_reading": [],
        }
