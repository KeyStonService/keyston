#!/usr/bin/env python3
"""
Governance Compliance Validator for unmanned-island-agent

Validates that the agent meets all governance/30-agents requirements.
Run this script to verify governance integration is correct.
"""

import sys
from pathlib import Path

# Add v2-multi-islands to path
_current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(_current_dir))

from governance_integration import GovernanceIntegration


def print_section(title: str) -> None:
    """Print section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_result(check_name: str, result: dict) -> None:
    """Print check result"""
    status = result.get("status", "unknown")
    message = result.get("message", "")
    
    if status == "passed":
        icon = "✅"
    elif status == "warning":
        icon = "⚠️"
    else:
        icon = "❌"
    
    print(f"{icon} {check_name}: {message}")


def main() -> int:
    """Main validation function"""
    print_section("Unmanned Island Agent - Governance Compliance Validation")
    
    # Initialize governance integration
    print("\n🔧 Initializing governance integration...")
    try:
        gov = GovernanceIntegration("unmanned-island-agent")
        print(f"✅ Governance integration initialized")
        print(f"   Project root: {gov.project_root}")
        print(f"   Governance root: {gov.governance_root}")
    except Exception as e:
        print(f"❌ Failed to initialize governance integration: {e}")
        return 1
    
    # Run compliance validation
    print_section("Compliance Validation")
    
    try:
        compliance_result = gov.validate_governance_compliance()
        
        print(f"\n📊 Compliance Score: {compliance_result['compliance_score']:.1f}%")
        print(f"📋 Overall Status: {compliance_result['overall_status']}")
        
        print("\n🔍 Detailed Checks:")
        for check_name, result in compliance_result["compliance_checks"].items():
            print_result(check_name.replace('_', ' ').title(), result)
        
    except Exception as e:
        print(f"❌ Compliance validation failed: {e}")
        return 1
    
    # Run health check
    print_section("Health Check")
    
    try:
        health_result = gov.perform_health_check()
        
        print(f"\n🏥 Health Status: {health_result['health_status']}")
        
        print("\n🔍 Health Checks:")
        for check_name, result in health_result["checks"].items():
            print_result(check_name.replace('_', ' ').title(), result)
            
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return 1
    
    # Display agent info
    print_section("Agent Information")
    
    try:
        agent_info = gov.get_agent_info()
        
        print(f"\n📌 Agent ID: {agent_info['agent_id']}")
        print(f"📊 Status: {agent_info['status']}")
        print(f"🏥 Health: {agent_info['health_status']}")
        print(f"✅ Compliance Score: {agent_info['compliance_score']:.1f}%")
        print(f"⏱️  Uptime: {agent_info['uptime_seconds']:.0f}s")
        
    except Exception as e:
        print(f"❌ Failed to get agent info: {e}")
        return 1
    
    # Final summary
    print_section("Validation Summary")
    
    all_passed = (
        compliance_result['overall_status'] == 'compliant' and
        health_result['health_status'] in ['healthy', 'degraded']
    )
    
    if all_passed:
        print("\n✅ All governance requirements validated successfully!")
        print("   The unmanned-island-agent is properly integrated with")
        print("   the governance/30-agents framework.")
        return_code = 0
    else:
        print("\n⚠️ Some governance requirements need attention.")
        print("   Please review the failed checks above.")
        return_code = 1
    
    print("\n" + "="*60 + "\n")
    
    return return_code


if __name__ == "__main__":
    sys.exit(main())
