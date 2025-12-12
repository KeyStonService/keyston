#!/usr/bin/env python3
"""
Secret Pattern Management Script
動態管理 GitHub Secret Scanning 自定義模式

Security Note:
This script handles sensitive pattern data. All logging has been sanitized to:
- Remove pattern names and regex details from console output
- Truncate error responses to prevent sensitive data leakage
- Provide warnings when exporting full pattern details
- Use generic success/error messages without exposing identifiers
"""

import requests
import json
import os
import sys
import argparse
from typing import Dict, List, Optional


class SecretPatternManager:
    """管理 GitHub Secret Scanning 自定義模式"""
    
    def __init__(self, token: str, base_url: str = "https://api.github.com"):
        self.token = token
        self.base_url = base_url
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28'
        }
    
    @staticmethod
    def _sanitize_response(response_text: str, max_length: int = 100) -> str:
        """Sanitize response text to avoid logging sensitive information"""
        if not response_text:
            return "Empty response"
        # Truncate and remove potentially sensitive details
        sanitized = response_text[:max_length]
        if len(response_text) > max_length:
            sanitized += "... (truncated for security)"
        return sanitized
    
    @staticmethod
    def sanitize_pattern_data(pattern: Dict) -> Dict:
        """Remove sensitive fields from pattern data for safe logging
        
        Returns only metadata that is safe to display:
        - Pattern ID (numeric, non-sensitive identifier)
        - Timestamps (created_at, updated_at)
        
        Excludes sensitive fields like name, regex, and secret_type.
        """
        safe_fields = ['id', 'created_at', 'updated_at']
        return {k: v for k, v in pattern.items() if k in safe_fields}
    
    def create_custom_pattern(self, org: str, pattern_data: Dict) -> Optional[Dict]:
        """建立自定義秘密掃描模式"""
        url = f'{self.base_url}/orgs/{org}/secret-scanning/custom-patterns'
        
        try:
            response = requests.post(url, headers=self.headers, json=pattern_data)
            
            if response.status_code == 201:
                print("✅ Custom pattern created successfully")
                return response.json()
            else:
                print(f"❌ Failed to create pattern: HTTP {response.status_code}")
                print(f"   Error details: {self._sanitize_response(response.text)}")
                return None
        except Exception as e:
            print(f"❌ Error creating pattern: {str(e)}")
            return None
    
    def update_custom_pattern(self, org: str, pattern_id: int, pattern_data: Dict) -> Optional[Dict]:
        """更新自定義模式"""
        url = f'{self.base_url}/orgs/{org}/secret-scanning/custom-patterns/{pattern_id}'
        
        try:
            response = requests.patch(url, headers=self.headers, json=pattern_data)
            
            if response.status_code == 200:
                print("✅ Pattern updated successfully")
                return response.json()
            else:
                print(f"❌ Failed to update pattern: HTTP {response.status_code}")
                print(f"   Error details: {self._sanitize_response(response.text)}")
                return None
        except Exception as e:
            print(f"❌ Error updating pattern: {str(e)}")
            return None
    
    def delete_custom_pattern(self, org: str, pattern_id: int) -> bool:
        """刪除自定義模式"""
        url = f'{self.base_url}/orgs/{org}/secret-scanning/custom-patterns/{pattern_id}'
        
        try:
            response = requests.delete(url, headers=self.headers)
            
            if response.status_code == 204:
                print("✅ Pattern deleted successfully")
                return True
            else:
                print(f"❌ Failed to delete pattern: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error deleting pattern: {str(e)}")
            return False
    
    def list_custom_patterns(self, org: str) -> List[Dict]:
        """列出所有自定義模式"""
        url = f'{self.base_url}/orgs/{org}/secret-scanning/custom-patterns'
        
        try:
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                patterns = response.json()
                print(f"✅ Found {len(patterns)} custom patterns")
                return patterns
            else:
                print(f"❌ Failed to list patterns: HTTP {response.status_code}")
                print(f"   Error details: {self._sanitize_response(response.text)}")
                return []
        except Exception as e:
            print(f"❌ Error listing patterns: {str(e)}")
            return []
    
    def get_pattern(self, org: str, pattern_id: int) -> Optional[Dict]:
        """獲取特定模式詳情"""
        url = f'{self.base_url}/orgs/{org}/secret-scanning/custom-patterns/{pattern_id}'
        
        try:
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to get pattern: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error getting pattern: {str(e)}")
            return None
    
    def deploy_enterprise_patterns(self, org: str) -> None:
        """部署企業級模式"""
        patterns = [
            {
                "name": "Enterprise Database Password",
                "regex": r"(?i)enterprise_db_pass_[a-zA-Z0-9]{24}",
                "secret_type": "enterprise_database_password"
            },
            {
                "name": "Internal Service Token",
                "regex": r"int_svc_[0-9a-f]{48}",
                "secret_type": "internal_service_token"
            },
            {
                "name": "Enterprise API Key",
                "regex": r"ent_api_[A-Za-z0-9]{40}",
                "secret_type": "enterprise_api_key"
            },
            {
                "name": "Master Encryption Key",
                "regex": r"emk_[0-9A-Fa-f]{128}",
                "secret_type": "encryption_master_key"
            },
            {
                "name": "JWT Signing Secret",
                "regex": r"jwt_secret_[A-Za-z0-9_-]{43}",
                "secret_type": "jwt_signing_secret"
            }
        ]
        
        print(f"Deploying {len(patterns)} enterprise patterns to {org}...")
        
        success_count = 0
        for pattern in patterns:
            result = self.create_custom_pattern(org, pattern)
            if result:
                success_count += 1
        
        print(f"\n{'='*50}")
        print(f"✅ Successfully deployed {success_count}/{len(patterns)} patterns")
        print(f"{'='*50}")
    
    def export_patterns(self, org: str, output_file: str) -> None:
        """導出所有自定義模式到 JSON 文件
        
        Warning: Exported file may contain sensitive pattern data.
        Store securely and restrict access appropriately.
        """
        patterns = self.list_custom_patterns(org)
        
        if patterns:
            try:
                with open(output_file, 'w') as f:
                    json.dump(patterns, f, indent=2)
                print(f"✅ Patterns exported to {output_file}")
                print("⚠️  Warning: Exported file contains sensitive pattern data")
            except Exception as e:
                print(f"❌ Error exporting patterns: {str(e)}")
    
    def import_patterns(self, org: str, input_file: str) -> None:
        """從 JSON 文件導入模式"""
        try:
            with open(input_file, 'r') as f:
                patterns = json.load(f)
            
            print(f"Importing {len(patterns)} patterns from {input_file}...")
            
            success_count = 0
            for pattern in patterns:
                # Remove fields that shouldn't be in create request
                pattern_data = {
                    'name': pattern.get('name'),
                    'regex': pattern.get('regex'),
                    'secret_type': pattern.get('secret_type')
                }
                
                result = self.create_custom_pattern(org, pattern_data)
                if result:
                    success_count += 1
            
            print(f"✅ Successfully imported {success_count}/{len(patterns)} patterns")
        except Exception as e:
            print(f"❌ Error importing patterns: {str(e)}")


def main():
    parser = argparse.ArgumentParser(
        description='Manage GitHub Secret Scanning custom patterns'
    )
    parser.add_argument('action', 
                       choices=['list', 'create', 'update', 'delete', 'deploy', 'export', 'import'],
                       help='Action to perform')
    parser.add_argument('--org', required=True, help='GitHub organization name')
    parser.add_argument('--token', help='GitHub token (or set GITHUB_TOKEN env var)')
    parser.add_argument('--pattern-id', type=int, help='Pattern ID for update/delete/get')
    parser.add_argument('--file', help='File path for export/import')
    parser.add_argument('--name', help='Pattern name for create')
    parser.add_argument('--regex', help='Pattern regex for create')
    parser.add_argument('--secret-type', help='Secret type for create')
    
    args = parser.parse_args()
    
    # Get token from args or environment
    token = args.token or os.getenv('GITHUB_TOKEN')
    if not token:
        print("❌ Error: GitHub token required. Set GITHUB_TOKEN env var or use --token")
        sys.exit(1)
    
    manager = SecretPatternManager(token)
    
    try:
        if args.action == 'list':
            patterns = manager.list_custom_patterns(args.org)
            if patterns:
                print("\nCustom Patterns (sanitized view):")
                # Show only non-sensitive metadata
                safe_patterns = [manager.sanitize_pattern_data(p) for p in patterns]
                print(json.dumps(safe_patterns, indent=2))
                print(f"\n💡 Use 'export' action to save full pattern details to a secure file")
        
        elif args.action == 'create':
            if not all([args.name, args.regex, args.secret_type]):
                print("❌ Error: --name, --regex, and --secret-type required for create")
                sys.exit(1)
            
            pattern_data = {
                'name': args.name,
                'regex': args.regex,
                'secret_type': args.secret_type
            }
            manager.create_custom_pattern(args.org, pattern_data)
        
        elif args.action == 'update':
            if not args.pattern_id:
                print("❌ Error: --pattern-id required for update")
                sys.exit(1)
            
            pattern_data = {}
            if args.name:
                pattern_data['name'] = args.name
            if args.regex:
                pattern_data['regex'] = args.regex
            if args.secret_type:
                pattern_data['secret_type'] = args.secret_type
            
            manager.update_custom_pattern(args.org, args.pattern_id, pattern_data)
        
        elif args.action == 'delete':
            if not args.pattern_id:
                print("❌ Error: --pattern-id required for delete")
                sys.exit(1)
            
            manager.delete_custom_pattern(args.org, args.pattern_id)
        
        elif args.action == 'deploy':
            manager.deploy_enterprise_patterns(args.org)
        
        elif args.action == 'export':
            if not args.file:
                print("❌ Error: --file required for export")
                sys.exit(1)
            
            manager.export_patterns(args.org, args.file)
        
        elif args.action == 'import':
            if not args.file:
                print("❌ Error: --file required for import")
                sys.exit(1)
            
            manager.import_patterns(args.org, args.file)
    
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
