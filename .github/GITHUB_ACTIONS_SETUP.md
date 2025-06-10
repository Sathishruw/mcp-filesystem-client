# GitHub Actions Setup for MCP Client Tests

## Setting up GitHub Token for Integration Tests

To run the GitHub integration tests in GitHub Actions, you need to add a GitHub Personal Access Token as a secret in your repository.

### Steps:

1. **Create a GitHub Personal Access Token**
   - Go to https://github.com/settings/tokens
   - Click "Generate new token" → "Generate new token (classic)"
   - Give it a descriptive name like "MCP Integration Tests"
   - Select the following permissions:
     - `repo` (Full control of private repositories)
     - `read:user` (Read user profile data)
     - `read:org` (Read org and team membership)
   - Click "Generate token"
   - **Copy the token immediately** (you won't see it again)

2. **Add the Token to Your Repository Secrets**
   - Go to your repository on GitHub
   - Click "Settings" → "Secrets and variables" → "Actions"
   - Click "New repository secret"
   - Name: `MCP_GITHUB_TOKEN`
   - Value: Paste your GitHub Personal Access Token
   - Click "Add secret"

3. **Verify the Workflow**
   - The workflow will automatically use the `MCP_GITHUB_TOKEN` secret
   - GitHub integration tests will run when the token is available
   - If no token is set, the tests will show a warning but won't fail

## Workflow Jobs

The updated workflow includes:

1. **test**: Basic filesystem MCP client tests
2. **test-github-integration**: Tests for GitHub MCP server (requires token)
3. **test-unified-server**: Tests for unified server (optional)
4. **test-multiple-python**: Tests across Python versions
5. **test-import**: Import validation tests

## Running Tests Locally

To run the GitHub integration tests locally:

```bash
# Set your GitHub token
export GITHUB_PERSONAL_ACCESS_TOKEN=your_token_here

# Run the tests
python test_github_integration.py
```

## Security Notes

- Never commit your GitHub token to the repository
- Use repository secrets for GitHub Actions
- The token in the workflow is accessed via `${{ secrets.MCP_GITHUB_TOKEN }}`
- Consider using a token with minimal required permissions
- Rotate tokens regularly for security

## Troubleshooting

If tests fail with authentication errors:
1. Verify the token has correct permissions
2. Check that the secret name is exactly `MCP_GITHUB_TOKEN`
3. Ensure the token hasn't expired
4. Try regenerating the token if issues persist
