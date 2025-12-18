#!/usr/bin/env python3
"""
Jira Integration for GitHub Security Alerts
自動將安全告警建立為 Jira Issues
"""

import requests
import os
import sys
from typing import Optional


class JiraIntegration:
    """Jira 整合類別"""
    
    def __init__(self, jira_url: str, username: str, api_token: str, project_key: str):
        self.jira_url = jira_url.rstrip('/')
        # WARNING: Jira credentials are stored in memory in plaintext.
        # NEVER log self.auth or pass it to any logging/debugging function.
        # Always source credentials from environment variables and ensure request debugging is disabled.
        self.auth = (username, api_token)
        self.project_key = project_key
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def create_security_issue(self, 
                            summary: str, 
                            description: str, 
                            severity: str,
                            alert_type: str = "Security Alert",
                            repository: str = "unknown",
                            alert_url: Optional[str] = None) -> Optional[str]:
        """建立安全 Issue"""
        
        # Map severity to Jira priority
        priority_map = {
            'critical': 'Highest',
            'high': 'High',
            'medium': 'Medium',
            'moderate': 'Medium',
            'low': 'Low'
        }
        
        priority = priority_map.get(severity.lower(), 'Medium')
        
        # Build description with additional info
        full_description = f"""
h2. Security Alert Details

*Type*: {alert_type}
*Severity*: {severity.upper()}
*Repository*: {repository}

h3. Description

{description}
"""
        
        if alert_url:
            full_description += f"\n\nh3. Alert URL\n\n{alert_url}"
        
        full_description += """

h3. Action Required

Please review and address this security alert according to the SLA:
* Critical: 4 hours
* High: 24 hours
* Medium: 1 week
* Low: 1 month

h3. Resources

* [GHAS Documentation|https://docs.github.com/en/code-security]
* [Security Best Practices|https://owasp.org/]
"""
        
        # Create issue payload
        issue_data = {
            "fields": {
                "project": {
                    "key": self.project_key
                },
                "summary": summary,
                "description": full_description,
                "issuetype": {
                    "name": "Bug"
                },
                "priority": {
                    "name": priority
                },
                "labels": [
                    "security",
                    f"severity-{severity.lower()}",
                    alert_type.lower().replace(" ", "-"),
                    "automated"
                ]
            }
        }
        
        try:
            response = requests.post(
                f"{self.jira_url}/rest/api/2/issue",
                auth=self.auth,
                headers=self.headers,
                json=issue_data,
                timeout=30
            )
            
            if response.status_code == 201:
                issue_key = response.json()['key']
                print(f"✅ Created Jira issue: {issue_key}")
                return issue_key
            else:
                print(f"❌ Failed to create Jira issue: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating Jira issue: {e}")
            return None
    
    def add_comment(self, issue_key: str, comment: str) -> bool:
        """新增評論到 Issue"""
        try:
            response = requests.post(
                f"{self.jira_url}/rest/api/2/issue/{issue_key}/comment",
                auth=self.auth,
                headers=self.headers,
                json={"body": comment},
                timeout=30
            )
            
            return response.status_code == 201
            
        except Exception as e:
            print(f"❌ Error adding comment: {e}")
            return False
    
    def transition_issue(self, issue_key: str, transition_name: str) -> bool:
        """轉換 Issue 狀態"""
        try:
            # Get available transitions
            response = requests.get(
                f"{self.jira_url}/rest/api/2/issue/{issue_key}/transitions",
                auth=self.auth,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code != 200:
                return False
            
            transitions = response.json()['transitions']
            transition_id = None
            
            for transition in transitions:
                if transition['name'].lower() == transition_name.lower():
                    transition_id = transition['id']
                    break
            
            if not transition_id:
                print(f"❌ Transition '{transition_name}' not found")
                return False
            
            # Execute transition
            response = requests.post(
                f"{self.jira_url}/rest/api/2/issue/{issue_key}/transitions",
                auth=self.auth,
                headers=self.headers,
                json={"transition": {"id": transition_id}},
                timeout=30
            )
            
            return response.status_code == 204
            
        except Exception as e:
            print(f"❌ Error transitioning issue: {e}")
            return False


def main():
    """主函數"""
    # Get configuration from environment
    jira_url = os.getenv('JIRA_URL')
    jira_username = os.getenv('JIRA_USERNAME')
    jira_api_token = os.getenv('JIRA_API_TOKEN')
    jira_project = os.getenv('JIRA_PROJECT', 'SEC')
    
    if not all([jira_url, jira_username, jira_api_token]):
        print("Error: Missing required environment variables")
        print("Required: JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN")
        sys.exit(1)
    
    # Get alert details from command line or environment
    severity = os.getenv('ALERT_SEVERITY', sys.argv[1] if len(sys.argv) > 1 else 'medium')
    summary = os.getenv('ALERT_SUMMARY', sys.argv[2] if len(sys.argv) > 2 else 'Security Alert')
    description = os.getenv('ALERT_DESCRIPTION', sys.argv[3] if len(sys.argv) > 3 else 'Security issue detected')
    alert_type = os.getenv('ALERT_TYPE', 'Security Alert')
    repository = os.getenv('GITHUB_REPOSITORY', 'unknown')
    alert_url = os.getenv('ALERT_URL')
    
    # Create Jira integration
    jira = JiraIntegration(jira_url, jira_username, jira_api_token, jira_project)
    
    # Create issue
    issue_key = jira.create_security_issue(
        summary=summary,
        description=description,
        severity=severity,
        alert_type=alert_type,
        repository=repository,
        alert_url=alert_url
    )
    
    if issue_key:
        print(f"Jira issue created: {jira_url}/browse/{issue_key}")
        sys.exit(0)
    else:
        print("Failed to create Jira issue")
        sys.exit(1)


if __name__ == "__main__":
    main()
