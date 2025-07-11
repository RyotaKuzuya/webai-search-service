# Claude Max OAuth Authentication for GitHub Actions

This guide explains how to set up Claude Max OAuth authentication for GitHub Actions, replacing the traditional API key approach.

## Overview

Claude Max OAuth authentication provides a more secure and flexible way to authenticate with Claude in GitHub Actions. Instead of using API keys, it uses OAuth tokens that can be refreshed automatically.

## Prerequisites

1. **Claude Max Subscription**: You need an active Claude Max subscription
2. **OAuth Tokens**: You must obtain OAuth tokens from Claude Max
3. **GitHub Repository**: Write access to configure secrets
4. **GitHub CLI**: Install `gh` CLI for easier secret management

## Setup Steps

### 1. Obtain OAuth Tokens

First, you need to obtain OAuth tokens from Claude Max:

```bash
# Run the OAuth setup script (if available)
./setup-claude-oauth-token.sh
```

This will provide you with:
- `CLAUDE_ACCESS_TOKEN`: The access token for API calls
- `CLAUDE_REFRESH_TOKEN`: Token used to refresh the access token
- `CLAUDE_EXPIRES_AT`: Unix timestamp when the access token expires

### 2. Configure GitHub Secrets

Run the setup script to configure GitHub secrets:

```bash
./setup-claude-oauth-secrets.sh
```

Or manually add the secrets via GitHub UI:
1. Go to Settings → Secrets and variables → Actions
2. Add the following secrets:
   - `CLAUDE_ACCESS_TOKEN`
   - `CLAUDE_REFRESH_TOKEN`
   - `CLAUDE_EXPIRES_AT`

### 3. Fork Required Repositories

You need to fork the Claude Code Action repository and add OAuth support:

1. Fork `anthropics/claude-code-action`
2. Fork `anthropics/claude-code-base-action` (if using base action)
3. Add OAuth authentication support to your forked action

### 4. Update Workflow File

The workflow file (`claude-oauth.yml`) is already configured to use OAuth authentication:

```yaml
- name: Run Claude Code with OAuth
  uses: your-username/claude-code-action@oauth-support
  with:
    claude_access_token: ${{ secrets.CLAUDE_ACCESS_TOKEN }}
    claude_refresh_token: ${{ secrets.CLAUDE_REFRESH_TOKEN }}
    claude_expires_at: ${{ secrets.CLAUDE_EXPIRES_AT }}
    github_token: ${{ secrets.GITHUB_TOKEN }}
```

Update `your-username` to your GitHub username where you forked the action.

## Token Refresh

The OAuth tokens need to be refreshed periodically. You can:

1. **Manual Refresh**: Run the refresh script when tokens expire
2. **Automated Refresh**: Set up a scheduled workflow to refresh tokens
3. **Action-based Refresh**: The forked action can handle token refresh automatically

### Example Token Refresh Workflow

Create `.github/workflows/refresh-claude-tokens.yml`:

```yaml
name: Refresh Claude OAuth Tokens

on:
  schedule:
    # Run daily at 2 AM UTC
    - cron: '0 2 * * *'
  workflow_dispatch:

jobs:
  refresh:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Refresh Tokens
        run: |
          # Add your token refresh logic here
          python refresh_claude_token.py
        env:
          CLAUDE_REFRESH_TOKEN: ${{ secrets.CLAUDE_REFRESH_TOKEN }}
```

## Troubleshooting

### Common Issues

1. **Token Expired**: 
   - Check `CLAUDE_EXPIRES_AT` timestamp
   - Run token refresh process
   - Update GitHub secrets

2. **Authentication Failed**:
   - Verify all three secrets are set correctly
   - Check token format and validity
   - Ensure forked action supports OAuth

3. **Action Not Found**:
   - Verify you've updated the action reference to your fork
   - Check the branch name (e.g., `@oauth-support`)

### Debug Mode

Add debug logging to your workflow:

```yaml
env:
  ACTIONS_RUNNER_DEBUG: true
  ACTIONS_STEP_DEBUG: true
```

## Security Best Practices

1. **Never commit tokens**: Always use GitHub secrets
2. **Limit token scope**: Use minimal required permissions
3. **Rotate tokens regularly**: Set up automated rotation
4. **Monitor usage**: Check GitHub Actions logs for unauthorized access
5. **Use environment protection**: Limit which workflows can access secrets

## Migration from API Keys

To migrate from API key authentication:

1. Keep both workflows during transition
2. Test OAuth workflow thoroughly
3. Update all references to use OAuth workflow
4. Remove API key workflow once confirmed working
5. Delete `ANTHROPIC_API_KEY` secret

## Additional Resources

- [GitHub Encrypted Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [OAuth 2.0 Best Practices](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics)
- [GitHub Actions Security Hardening](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)