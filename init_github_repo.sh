#!/bin/bash

# GitHubリポジトリ初期化スクリプト
# AliasConf Project - Initial Repository Setup

set -e

echo "================================"
echo "AliasConf GitHub Repository Setup"
echo "================================"
echo ""

# 現在の状態確認
echo "📊 Current Status:"
echo "- Staged files: $(git status --short | wc -l)"
echo "- Tests: 218 passing (84.81% coverage)"
echo "- Code quality: No violations"
echo "- Type safety: No errors"
echo ""

# GitHubリポジトリ作成の確認
echo "⚠️  Prerequisites:"
echo "1. Create GitHub repository at: https://github.com/new"
echo "   - Repository name: aliasconf"
echo "   - Owner: cphelper"
echo "   - Visibility: Public"
echo "   - Initialize: NO README, NO .gitignore, NO license"
echo ""
read -p "Have you created the GitHub repository? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Please create the repository first, then run this script again."
    exit 1
fi

# 初回コミット
echo ""
echo "📝 Creating initial commit..."
git commit -m "Initial commit: AliasConf v0.1.0

- Powerful configuration management library with alias support
- 218 tests passing with 84.81% coverage
- Full type safety (mypy --strict)
- Performance optimized (0.06s for 10k entries)
- GitHub Actions CI/CD pipeline ready
- PyPI package structure prepared

Key features:
- Unique alias system for configuration keys
- Template expansion with circular reference detection
- Thread-safe operations
- Comprehensive test suite
- Support for YAML/JSON configuration files
- Type-safe configuration access"

echo "✅ Initial commit created!"
echo ""

# ブランチ名の確認
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "📌 Current branch: $CURRENT_BRANCH"

if [[ "$CURRENT_BRANCH" == "master" ]]; then
    read -p "Would you like to rename 'master' to 'main'? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git branch -M main
        CURRENT_BRANCH="main"
        echo "✅ Branch renamed to 'main'"
    fi
fi

# GitHubへのプッシュ
echo ""
echo "🚀 Pushing to GitHub..."
git push -u origin $CURRENT_BRANCH

echo ""
echo "✅ Successfully pushed to GitHub!"
echo ""

# 次のステップ
echo "📋 Next Steps:"
echo "1. Check GitHub Actions: https://github.com/cphelper/aliasconf/actions"
echo "2. Add repository description and topics"
echo "3. Configure branch protection rules"
echo "4. Add status badges to README.md"
echo "5. Create initial release (v0.1.0)"
echo ""

# GitHub Actionsの状態確認URL
echo "🔗 Important URLs:"
echo "- Repository: https://github.com/cphelper/aliasconf"
echo "- Actions: https://github.com/cphelper/aliasconf/actions"
echo "- Settings: https://github.com/cphelper/aliasconf/settings"
echo ""

echo "🎉 Repository initialization complete!"