#!/bin/bash

# Script to update workflow files to use forked repositories
# Run this after forking the repositories to RyotaKuzuya's account

echo "Updating workflow files to use forked repositories..."

# Update claude-oauth.yml to use the forked action
sed -i 's|your-username/claude-code-action@oauth-support|RyotaKuzuya/claude-code-action@main|g' .github/workflows/claude-oauth.yml

echo "Updated claude-oauth.yml"

# Search for any other files that might need updating
echo "Searching for other files that might reference the actions..."

# Find all YAML files that might contain action references
find . -name "*.yml" -o -name "*.yaml" | while read file; do
    if grep -q "anthropics/claude-code-action\|anthropics/claude-code-base-action\|your-username/claude-code-action" "$file"; then
        echo "Found reference in: $file"
        # Update references to use forked repositories
        sed -i 's|anthropics/claude-code-action|RyotaKuzuya/claude-code-action|g' "$file"
        sed -i 's|anthropics/claude-code-base-action|RyotaKuzuya/claude-code-base-action|g' "$file"
        sed -i 's|your-username/claude-code-action|RyotaKuzuya/claude-code-action|g' "$file"
        echo "Updated: $file"
    fi
done

echo "Update complete!"
echo ""
echo "Next steps:"
echo "1. Review the changes in .github/workflows/claude-oauth.yml"
echo "2. Commit and push the changes"
echo "3. Ensure you have set the following secrets in your repository:"
echo "   - CLAUDE_ACCESS_TOKEN"
echo "   - CLAUDE_REFRESH_TOKEN"
echo "   - CLAUDE_EXPIRES_AT"
echo "4. Test by creating an issue or PR with @claude mention"