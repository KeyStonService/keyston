#!/usr/bin/env python3
"""
Governance Integration Module for unmanned-island-agent

Integrates v2-multi-islands orchestrator with governance/30-agents framework.
Provides lifecycle hooks, monitoring, and compliance validation.
"""

import time
import yaml
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class GovernanceIntegration:
    """
    Governance integration for unmanned-island-agent
    
    Implements governance/30-agents requirements:
    - Lifecycle management
    - Health checks
    - Compliance monitoring
    - Audit logging
    """
    
    def __init__(self, agent_id: str = "unmanned-island-agent"):
        self.agent_id = agent_id
        self.project_root = self._find_project_root()
        self.governance_root = self.project_root / "governance" / "30-agents"
        self.agent_catalog_path = self.governance_root / "registry" / "agent-catalog.yaml"
        self.health_checks_path = self.governance_root / "monitoring" / "health-checks.yaml"
        
        # Agent state
        self.status = "active"
        self.start_time = datetime.now()
        self.health_status = "healthy"
        self.compliance_score = 100.0
        
    def _find_project_root(self) -> Path:
        """Find project root directory"""
        current = Path(__file__).resolve().parent
        while current != current.parent:
            if (current / 'governance').exists():
                return current
            if (current / 'package.json').exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def validate_governance_compliance(self) -> Dict[str, Any]:
        """
        Validate agent compliance with governance framework
        
        Returns:
            Compliance validation results
        """
        compliance_results = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id,
            "compliance_checks": {},
            "overall_status": "compliant",
            "compliance_score": 100.0
        }
        
        # Check 1: Agent catalog registration
        catalog_check = self._check_agent_catalog()
        compliance_results["compliance_checks"]["agent_catalog"] = catalog_check
        
        # Check 2: Health check configuration
        health_check = self._check_health_config()
        compliance_results["compliance_checks"]["health_config"] = health_check
        
        # Check 3: Permission alignment
        permission_check = self._check_permissions()
        compliance_results["compliance_checks"]["permissions"] = permission_check
        
        # Calculate overall compliance score
        passed = sum(1 for c in compliance_results["compliance_checks"].values() if c["status"] == "passed")
        total = len(compliance_results["compliance_checks"])
        compliance_results["compliance_score"] = (passed / total) * 100 if total > 0 else 0.0
        
        if compliance_results["compliance_score"] < 100:
            compliance_results["overall_status"] = "non_compliant"
        
        self.compliance_score = compliance_results["compliance_score"]
        
        return compliance_results
    
    def _check_agent_catalog(self) -> Dict[str, Any]:
        """Check if agent is properly registered in catalog"""
        if not self.agent_catalog_path.exists():
            return {
                "status": "failed",
                "message": f"Agent catalog not found: {self.agent_catalog_path}"
            }
        
        try:
            with open(self.agent_catalog_path, 'r', encoding='utf-8') as f:
                catalog = yaml.safe_load(f)
            
            # Check if agent is registered
            agents = catalog.get('agents', [])
            agent_found = any(a.get('agent_id') == self.agent_id for a in agents)
            
            if not agent_found:
                return {
                    "status": "failed",
                    "message": f"Agent {self.agent_id} not found in catalog"
                }
            
            return {
                "status": "passed",
                "message": "Agent properly registered in catalog"
            }
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Error checking catalog: {str(e)}"
            }
    
    def _check_health_config(self) -> Dict[str, Any]:
        """Check if health check configuration exists"""
        if not self.health_checks_path.exists():
            return {
                "status": "failed",
                "message": f"Health checks config not found: {self.health_checks_path}"
            }
        
        try:
            with open(self.health_checks_path, 'r', encoding='utf-8') as f:
                health_config = yaml.safe_load(f)
            
            # Check if agent has health check configuration
            agents = health_config.get('agents', {})
            if self.agent_id not in agents:
                return {
                    "status": "failed",
                    "message": f"Agent {self.agent_id} not found in health checks config"
                }
            
            agent_health = agents[self.agent_id]
            if not agent_health.get('enabled', False):
                return {
                    "status": "warning",
                    "message": "Health checks not enabled for agent"
                }
            
            return {
                "status": "passed",
                "message": "Health check configuration valid"
            }
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Error checking health config: {str(e)}"
            }
    
    def _check_permissions(self) -> Dict[str, Any]:
        """Check RBAC permission alignment"""
        rbac_path = self.governance_root / "permissions" / "rbac-policies.yaml"
        
        if not rbac_path.exists():
            return {
                "status": "failed",
                "message": f"RBAC policies not found: {rbac_path}"
            }
        
        try:
            with open(rbac_path, 'r', encoding='utf-8') as f:
                rbac = yaml.safe_load(f)
            
            # Check if agent has role assignment
            assignments = rbac.get('agent_assignments', {})
            if self.agent_id not in assignments:
                return {
                    "status": "failed",
                    "message": f"Agent {self.agent_id} not found in RBAC assignments"
                }
            
            agent_assignment = assignments[self.agent_id]
            if not agent_assignment.get('roles'):
                return {
                    "status": "failed",
                    "message": "No roles assigned to agent"
                }
            
            return {
                "status": "passed",
                "message": f"Roles assigned: {', '.join(agent_assignment['roles'])}"
            }
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Error checking permissions: {str(e)}"
            }
    
    def perform_health_check(self) -> Dict[str, Any]:
        """
        Perform health check based on governance/30-agents/monitoring specs
        
        Returns:
            Health check results
        """
        health_result = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id,
            "health_status": "healthy",
            "checks": {}
        }
        
        # Liveness check
        health_result["checks"]["liveness"] = {
            "status": "passed",
            "message": "Agent process is running"
        }
        
        # Readiness check
        readiness = self._check_readiness()
        health_result["checks"]["readiness"] = readiness
        
        # Performance check
        performance = self._check_performance()
        health_result["checks"]["performance"] = performance
        
        # Determine overall health
        failed_checks = [k for k, v in health_result["checks"].items() if v["status"] == "failed"]
        if failed_checks:
            health_result["health_status"] = "unhealthy"
        elif any(v["status"] == "warning" for v in health_result["checks"].values()):
            health_result["health_status"] = "degraded"
        
        self.health_status = health_result["health_status"]
        
        return health_result
    
    def _check_readiness(self) -> Dict[str, Any]:
        """Check if agent dependencies are available"""
        # Check governance framework files
        required_files = [
            self.governance_root / "framework.yaml",
            self.governance_root / "registry" / "agent-catalog.yaml",
        ]
        
        missing_files = [str(f) for f in required_files if not f.exists()]
        
        if missing_files:
            return {
                "status": "failed",
                "message": f"Missing required files: {', '.join(missing_files)}"
            }
        
        return {
            "status": "passed",
            "message": "All dependencies available"
        }
    
    def _check_performance(self) -> Dict[str, Any]:
        """Check performance metrics"""
        # Simple uptime check
        uptime_seconds = (datetime.now() - self.start_time).total_seconds()
        
        return {
            "status": "passed",
            "message": f"Uptime: {uptime_seconds:.0f}s",
            "metrics": {
                "uptime_seconds": uptime_seconds,
                "health_status": self.health_status
            }
        }
    
    def log_audit_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """
        Log audit event per governance/70-audit requirements
        
        Args:
            event_type: Type of audit event
            details: Event details
        """
        audit_event = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id,
            "event_type": event_type,
            "details": details,
            "compliance_score": self.compliance_score,
            "health_status": self.health_status
        }
        
        # In production, this would write to audit log system
        # For now, we just track the event structure
        print(f"[AUDIT] {event_type}: {details}")
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get current agent information"""
        return {
            "agent_id": self.agent_id,
            "status": self.status,
            "health_status": self.health_status,
            "compliance_score": self.compliance_score,
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "governance_root": str(self.governance_root)
        }
