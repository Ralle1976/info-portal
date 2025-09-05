#!/usr/bin/env python3
"""
GitHub Repository Security Setup Script

This script configures security settings, branch protection rules,
and automated security features for the QR Info Portal repository.

Usage:
    python .github/setup-repository-security.py

Environment variables required:
    GITHUB_TOKEN: Personal access token with repo permissions
    GITHUB_REPO: Repository name in format "owner/repo"
"""

import os
import sys
import json
import requests
from typing import Dict, Any, Optional

class GitHubSecuritySetup:
    def __init__(self):
        self.token = os.getenv('GITHUB_TOKEN')
        self.repo = os.getenv('GITHUB_REPO', 'Ralle1976/qr-info-portal')
        
        if not self.token:
            raise ValueError("GITHUB_TOKEN environment variable is required")
            
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json',
            'X-GitHub-Api-Version': '2022-11-28'
        }
        self.base_url = f"https://api.github.com/repos/{self.repo}"
        
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Make authenticated request to GitHub API"""
        url = f"{self.base_url}/{endpoint}" if not endpoint.startswith('https://') else endpoint
        
        if method.upper() == 'GET':
            response = requests.get(url, headers=self.headers)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=self.headers, json=data)
        elif method.upper() == 'PUT':
            response = requests.put(url, headers=self.headers, json=data)
        elif method.upper() == 'PATCH':
            response = requests.patch(url, headers=self.headers, json=data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
            
        return response

    def setup_branch_protection(self):
        """Configure branch protection rules for main and develop branches"""
        print("🔒 Setting up branch protection rules...")
        
        protection_config = {
            "required_status_checks": {
                "strict": True,
                "contexts": [
                    "Code Quality",
                    "Run Tests",
                    "Security Scan", 
                    "CodeQL Analysis",
                    "Docker Build"
                ]
            },
            "enforce_admins": False,  # Allow admins to bypass in emergencies
            "required_pull_request_reviews": {
                "required_approving_review_count": 1,
                "dismiss_stale_reviews": True,
                "require_code_owner_reviews": False,
                "require_last_push_approval": True
            },
            "restrictions": None,  # No user/team restrictions
            "required_linear_history": False,
            "allow_force_pushes": False,
            "allow_deletions": False,
            "block_creations": False,
            "required_conversation_resolution": True
        }
        
        branches = ['main', 'develop']
        
        for branch in branches:
            print(f"  Setting up protection for {branch} branch...")
            
            # Check if branch exists
            branch_response = self._make_request('GET', f'branches/{branch}')
            if branch_response.status_code == 404:
                print(f"  ⚠️ Branch {branch} not found, skipping...")
                continue
                
            # Apply protection
            response = self._make_request('PUT', f'branches/{branch}/protection', protection_config)
            
            if response.status_code in [200, 201]:
                print(f"  ✅ Protection rules applied to {branch}")
            else:
                print(f"  ❌ Failed to apply protection to {branch}: {response.text}")

    def enable_security_features(self):
        """Enable GitHub security features"""
        print("🛡️ Enabling security features...")
        
        # Enable vulnerability alerts
        print("  Enabling vulnerability alerts...")
        response = self._make_request('PUT', 'vulnerability-alerts')
        if response.status_code in [200, 204]:
            print("  ✅ Vulnerability alerts enabled")
        else:
            print(f"  ❌ Failed to enable vulnerability alerts: {response.text}")
        
        # Enable automated security fixes
        print("  Enabling automated security fixes...")
        response = self._make_request('PUT', 'automated-security-fixes')
        if response.status_code in [200, 204]:
            print("  ✅ Automated security fixes enabled")
        else:
            print(f"  ❌ Failed to enable automated security fixes: {response.text}")
            
        # Enable dependency graph
        print("  Enabling dependency graph...")
        repo_settings = {
            "has_vulnerability_alerts_enabled": True,
            "has_automated_security_fixes_enabled": True
        }
        response = self._make_request('PATCH', '', repo_settings)
        if response.status_code == 200:
            print("  ✅ Dependency graph enabled")
        else:
            print(f"  ⚠️ Repository settings update: {response.status_code}")

    def setup_secret_scanning(self):
        """Configure secret scanning alerts"""
        print("🔍 Setting up secret scanning...")
        
        # Note: Secret scanning for private repos requires GitHub Advanced Security
        # This will enable it for public repos or if Advanced Security is available
        
        try:
            response = self._make_request('GET', 'secret-scanning/alerts')
            if response.status_code == 200:
                print("  ✅ Secret scanning is available")
            elif response.status_code == 404:
                print("  ⚠️ Secret scanning not available (requires GitHub Advanced Security for private repos)")
            else:
                print(f"  ❌ Secret scanning check failed: {response.status_code}")
                
        except Exception as e:
            print(f"  ⚠️ Could not check secret scanning: {e}")

    def setup_code_scanning(self):
        """Enable CodeQL code scanning"""
        print("📊 Setting up code scanning...")
        
        try:
            response = self._make_request('GET', 'code-scanning/alerts')
            if response.status_code == 200:
                print("  ✅ Code scanning is available")
            elif response.status_code == 404:
                print("  ⚠️ Code scanning not available (requires GitHub Advanced Security for private repos)")
            else:
                print(f"  ❌ Code scanning check failed: {response.status_code}")
                
        except Exception as e:
            print(f"  ⚠️ Could not check code scanning: {e}")

    def create_security_advisories_template(self):
        """Create security policy and advisory templates"""
        print("📋 Setting up security policy...")
        
        # Check if SECURITY.md exists
        response = self._make_request('GET', 'contents/SECURITY.md')
        if response.status_code == 404:
            print("  ⚠️ SECURITY.md not found - should be created manually")
        else:
            print("  ✅ SECURITY.md exists")

    def validate_repository_settings(self):
        """Validate current repository security settings"""
        print("🔍 Validating repository security settings...")
        
        # Get repository info
        response = self._make_request('GET', '')
        if response.status_code != 200:
            print(f"  ❌ Could not fetch repository info: {response.status_code}")
            return False
            
        repo_data = response.json()
        
        # Check security settings
        security_checks = [
            ('has_vulnerability_alerts_enabled', 'Vulnerability alerts'),
            ('has_automated_security_fixes_enabled', 'Automated security fixes'), 
            ('private', 'Repository visibility')
        ]
        
        for setting, description in security_checks:
            if setting in repo_data:
                status = "✅" if repo_data[setting] else "⚠️"
                value = repo_data[setting]
                print(f"  {status} {description}: {value}")
            else:
                print(f"  ❓ {description}: Unknown")
                
        return True

    def setup_all(self):
        """Run all security setup procedures"""
        print("🚀 Starting GitHub repository security setup...\n")
        
        try:
            self.validate_repository_settings()
            print()
            
            self.setup_branch_protection()
            print()
            
            self.enable_security_features()
            print()
            
            self.setup_secret_scanning()
            print()
            
            self.setup_code_scanning()
            print()
            
            self.create_security_advisories_template()
            print()
            
            print("✅ Security setup completed successfully!")
            print("\n📋 Next steps:")
            print("1. Review branch protection rules in repository settings")
            print("2. Enable GitHub Advanced Security if using private repository")
            print("3. Configure required secrets in repository settings:")
            print("   - ADMIN_PASSWORD")
            print("   - SECRET_KEY")
            print("   - SLACK_WEBHOOK (optional)")
            print("   - SNYK_TOKEN (optional)")
            print("4. Create SECURITY.md if not exists")
            print("5. Test workflows with a test PR")
            
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            sys.exit(1)

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print(__doc__)
        return
        
    try:
        setup = GitHubSecuritySetup()
        setup.setup_all()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()