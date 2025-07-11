# Claude OAuth Authentication Setup Guide

This guide will help you complete the setup of Claude OAuth authentication for your GitHub Actions.

## Step 1: Fork Required Repositories

Since GitHub CLI is not authenticated on this system, you'll need to manually fork these repositories:

1. **Fork claude-code-action**:
   - Go to: https://github.com/anthropics/claude-code-action
   - Click the "Fork" button in the top-right corner
   - Select your account (RyotaKuzuya) as the destination

2. **Fork claude-code-base-action**:
   - Go to: https://github.com/anthropics/claude-code-base-action
   - Click the "Fork" button in the top-right corner
   - Select your account (RyotaKuzuya) as the destination

## Step 2: Obtain Claude OAuth Tokens

To get your Claude OAuth tokens:

1. Visit the Claude OAuth application page (provided by Anthropic)
2. Authorize the application for your Claude account
3. Save the following tokens:
   - `CLAUDE_ACCESS_TOKEN`: Your OAuth access token
   - `CLAUDE_REFRESH_TOKEN`: Your OAuth refresh token
   - `CLAUDE_EXPIRES_AT`: Token expiration timestamp

## Step 3: Add Secrets to Your GitHub Repository

1. Go to your repository settings: https://github.com/RyotaKuzuya/webai/settings/secrets/actions
2. Add the following secrets:
   - `CLAUDE_ACCESS_TOKEN`
   - `CLAUDE_REFRESH_TOKEN`
   - `CLAUDE_EXPIRES_AT`

## Step 4: Update Workflow Files

The workflow files have been updated to use your forked repositories:
- `.github/workflows/claude-oauth.yml` - Main OAuth workflow
- `.github/workflows/claude-oauth-test.yml` - Test workflow for verification

## Step 5: Test the Setup

### Option A: Manual Workflow Test
1. Go to Actions tab in your repository
2. Select "Test Claude OAuth Setup" workflow
3. Click "Run workflow"
4. Optionally provide a test message
5. Check the workflow run results

### Option B: Issue/PR Test
1. Create a new issue with "@claude" mention
2. Claude should respond using OAuth authentication

## Workflow Files Updated

### claude-oauth.yml
- Updated to use `RyotaKuzuya/claude-code-action@main`
- Configured for OAuth authentication
- Triggers on @claude mentions in issues, PRs, and comments

### claude-oauth-test.yml
- Manual workflow for testing OAuth setup
- Can be triggered from Actions tab
- Displays Claude's response for verification

## Token Refresh

The refresh token workflow (`.github/workflows/refresh-claude-tokens.yml`) will automatically refresh your OAuth tokens when they expire. Make sure this workflow has the necessary permissions.

## Troubleshooting

1. **Authentication Errors**: Verify all three OAuth secrets are correctly set
2. **Action Not Found**: Ensure repositories are properly forked to RyotaKuzuya account
3. **Permission Errors**: Check repository permissions for the GitHub token
4. **Token Expiration**: The refresh workflow should handle this automatically

## Next Steps

1. Complete the repository forking
2. Add OAuth secrets to repository
3. Run the test workflow to verify setup
4. Start using @claude mentions in your issues and PRs!