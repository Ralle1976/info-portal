#!/bin/bash
set -e

# QR Info Portal - Complete GitHub Repository Security Setup
# This script configures all security settings, workflows, and best practices

echo "🚀 QR Info Portal - GitHub Repository Security Setup"
echo "=================================================="
echo ""

# Check prerequisites
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed. Please install it first:"
    echo "   https://cli.github.com/"
    exit 1
fi

if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub CLI. Please run:"
    echo "   gh auth login"
    exit 1
fi

# Get repository info
REPO=$(gh repo view --json owner,name --jq '.owner.login + "/" + .name')
echo "📂 Repository: $REPO"
echo ""

# Function to check if command succeeded
check_result() {
    if [ $? -eq 0 ]; then
        echo "✅ $1"
    else
        echo "❌ $1 failed"
        return 1
    fi
}

# Enable repository security features
echo "🛡️  Enabling repository security features..."

# Enable vulnerability alerts
echo "  Enabling vulnerability alerts..."
gh api -X PUT "repos/$REPO/vulnerability-alerts" &> /dev/null
check_result "Vulnerability alerts enabled"

# Enable automated security fixes  
echo "  Enabling automated security fixes..."
gh api -X PUT "repos/$REPO/automated-security-fixes" &> /dev/null
check_result "Automated security fixes enabled"

# Enable dependency graph
echo "  Enabling dependency graph..."
gh api -X PATCH "repos/$REPO" -f has_vulnerability_alerts_enabled=true -f has_automated_security_fixes_enabled=true &> /dev/null
check_result "Dependency graph enabled"

echo ""

# Set up branch protection rules
echo "🔒 Setting up branch protection rules..."

PROTECTION_CONFIG='{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "Code Quality",
      "Run Tests", 
      "Security Scan",
      "CodeQL Analysis"
    ]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "require_last_push_approval": true
  },
  "restrictions": null,
  "required_linear_history": false,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true
}'

# Main branch protection
echo "  Setting up main branch protection..."
echo "$PROTECTION_CONFIG" | gh api -X PUT "repos/$REPO/branches/main/protection" --input - &> /dev/null
check_result "Main branch protection enabled"

# Develop branch protection (if exists)
if gh api "repos/$REPO/branches/develop" &> /dev/null; then
    echo "  Setting up develop branch protection..."
    echo "$PROTECTION_CONFIG" | gh api -X PUT "repos/$REPO/branches/develop/protection" --input - &> /dev/null
    check_result "Develop branch protection enabled"
else
    echo "  ℹ️  Develop branch not found, skipping protection setup"
fi

echo ""

# Set up repository secrets (with prompts)
echo "🔐 Setting up repository secrets..."

# Check if secrets already exist
existing_secrets=$(gh secret list --json name --jq '.[].name')

setup_secret() {
    local secret_name="$1"
    local secret_description="$2"
    local secret_example="$3"
    
    if echo "$existing_secrets" | grep -q "^$secret_name$"; then
        echo "  ℹ️  Secret $secret_name already exists, skipping"
        return
    fi
    
    echo "  Setting up secret: $secret_name"
    echo "    Description: $secret_description"
    echo "    Example: $secret_example"
    
    read -s -p "    Enter value for $secret_name (or press Enter to skip): " secret_value
    echo ""
    
    if [ -n "$secret_value" ]; then
        echo "$secret_value" | gh secret set "$secret_name"
        check_result "$secret_name secret set"
    else
        echo "    ⚠️  Skipped $secret_name - you can set this later in repository settings"
    fi
}

setup_secret "ADMIN_PASSWORD" "Password for admin interface" "secure-admin-password-123"
setup_secret "SECRET_KEY" "Flask secret key for sessions" "your-very-secure-secret-key-here"
setup_secret "SLACK_WEBHOOK" "Slack webhook for notifications (optional)" "https://hooks.slack.com/services/..."
setup_secret "SNYK_TOKEN" "Snyk API token for security scanning (optional)" "your-snyk-api-token"

echo ""

# Enable GitHub Pages (if not already enabled)
echo "📄 Setting up GitHub Pages..."
gh api -X POST "repos/$REPO/pages" -f source.branch=main -f source.path=/docs &> /dev/null || {
    echo "  ℹ️  GitHub Pages may already be configured or requires manual setup"
}

echo ""

# Create repository labels for better issue management
echo "🏷️  Setting up repository labels..."

# Security labels
gh label create "security" --color "d73a4a" --description "Security-related issue or PR" &> /dev/null || true
gh label create "vulnerability" --color "b60205" --description "Security vulnerability report" &> /dev/null || true
gh label create "critical" --color "b60205" --description "Critical priority issue" &> /dev/null || true
gh label create "high-priority" --color "d93f0b" --description "High priority issue" &> /dev/null || true

# Automation labels  
gh label create "automated" --color "0366d6" --description "Created by automation" &> /dev/null || true
gh label create "dependencies" --color "0366d6" --description "Dependency updates" &> /dev/null || true
gh label create "github-actions" --color "2088ff" --description "GitHub Actions related" &> /dev/null || true

# Type labels
gh label create "enhancement" --color "a2eeef" --description "New feature or request" &> /dev/null || true
gh label create "bug" --color "d73a4a" --description "Something isn't working" &> /dev/null || true
gh label create "documentation" --color "0075ca" --description "Improvements or additions to documentation" &> /dev/null || true

echo "✅ Repository labels configured"

echo ""

# Validate setup
echo "🔍 Validating security setup..."

# Check that workflows exist
REQUIRED_WORKFLOWS=(
    ".github/workflows/ci.yml"
    ".github/workflows/security-scan.yml" 
    ".github/workflows/codeql-analysis.yml"
    ".github/workflows/security-monitoring.yml"
)

for workflow in "${REQUIRED_WORKFLOWS[@]}"; do
    if [ -f "$workflow" ]; then
        echo "✅ $workflow exists"
    else
        echo "❌ $workflow missing"
    fi
done

# Check Dependabot config
if [ -f ".github/dependabot.yml" ]; then
    echo "✅ Dependabot configuration exists"
else
    echo "❌ Dependabot configuration missing"
fi

# Check security policy
if [ -f ".github/SECURITY.md" ]; then
    echo "✅ Security policy exists"
else
    echo "❌ Security policy missing"
fi

echo ""

# Final instructions
echo "🎉 Repository security setup completed!"
echo ""
echo "📋 Next Steps:"
echo "1. Review all created workflows in .github/workflows/"
echo "2. Test workflows by creating a test PR"
echo "3. Configure any missing secrets in repository settings"
echo "4. Enable GitHub Advanced Security if using private repository"
echo "5. Review and customize security policies as needed"
echo ""
echo "🔗 Useful Links:"
echo "- Repository Settings: https://github.com/$REPO/settings"
echo "- Security & Analysis: https://github.com/$REPO/settings/security_analysis"  
echo "- Secrets: https://github.com/$REPO/settings/secrets/actions"
echo "- Branch Protection: https://github.com/$REPO/settings/branches"
echo ""
echo "💡 Pro Tips:"
echo "- Enable GitHub Advanced Security for private repositories"
echo "- Review Dependabot PRs promptly for security updates"
echo "- Monitor security alerts in the Security tab"
echo "- Keep workflows updated monthly"
echo ""
echo "🛡️  Your repository is now secure and ready for development!"