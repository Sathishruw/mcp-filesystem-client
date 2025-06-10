#!/usr/bin/env python3

"""
Practical Examples - Real-world workflows combining Filesystem and GitHub MCP
"""

import asyncio
import os
import json
from typing import Dict, Any, List
from unified_client import UnifiedMCPClient

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def workflow_1_repository_backup():
    """
    Workflow 1: Create a local backup of important files from a GitHub repository
    """
    print("\n🔄 Workflow 1: Repository Backup")
    print("=" * 50)
    
    github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not github_token:
        print("❌ GitHub token required for this workflow")
        return
    
    client = UnifiedMCPClient(github_token)
    
    try:
        await client.start()
        
        # Configuration
        owner = "Sathishruw"
        repo = "mcp-filesystem-client"
        backup_dir = "repo_backup"
        
        # Step 1: List repository files
        print(f"📂 Listing files in {owner}/{repo}...")
        repo_files = await client.github_client.list_directory_contents(owner, repo)
        print(f"Repository contents: {repo_files}")
        
        # Step 2: Download key files
        important_files = ["README.md", "fastmcp_client.py", "filesystem_server.py"]
        
        print(f"\n💾 Downloading important files to {backup_dir}/...")
        await client.sync_repo_to_local(owner, repo, backup_dir, important_files)
        
        # Step 3: Create backup manifest
        manifest = {
            "repository": f"{owner}/{repo}",
            "backup_date": "2025-05-31",
            "files": important_files,
            "backup_location": backup_dir
        }
        
        await client.fs_write_file(
            f"{backup_dir}/backup_manifest.json", 
            json.dumps(manifest, indent=2)
        )
        
        # Step 4: Verify backup
        print(f"\n✅ Backup verification:")
        local_files = await client.fs_list_files(backup_dir)
        print(f"Local backup files: {local_files}")
        
        print(f"\n🎉 Backup workflow completed successfully!")
        
    except Exception as e:
        logger.error(f"Backup workflow failed: {e}")
    finally:
        await client.close()


async def workflow_2_issue_analysis():
    """
    Workflow 2: Analyze repository issues and save analysis locally
    """
    print("\n📊 Workflow 2: Issue Analysis")
    print("=" * 50)
    
    github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not github_token:
        print("❌ GitHub token required for this workflow")
        return
    
    client = UnifiedMCPClient(github_token)
    
    try:
        await client.start()
        
        # Configuration
        owner = "Sathishruw"
        repo = "mcp-filesystem-client"
        analysis_dir = "issue_analysis"
        
        # Step 1: Get repository issues
        print(f"🔍 Fetching issues from {owner}/{repo}...")
        issues = await client.github_client.list_issues(owner, repo, state="all")
        print(f"Found issues: {issues}")
        
        # Step 2: Create analysis directory
        await client.fs_write_file(f"{analysis_dir}/.gitkeep", "")
        
        # Step 3: Analyze issues (simplified example)
        analysis = {
            "repository": f"{owner}/{repo}",
            "analysis_date": "2025-05-31",
            "total_issues": "Check the actual response format",
            "summary": "This is a simplified analysis. In practice, you'd parse the response."
        }
        
        # Save analysis
        await client.fs_write_file(
            f"{analysis_dir}/issue_analysis.json",
            json.dumps(analysis, indent=2)
        )
        
        # Step 4: Create readable report
        report = f"""# Issue Analysis Report

Repository: {owner}/{repo}
Analysis Date: 2025-05-31

## Summary
This report analyzes the issues in the repository.
The actual implementation would parse the GitHub response and provide:
- Open vs closed issue counts
- Common labels
- Issue age distribution
- Top contributors

## Raw Data
See issue_analysis.json for the raw GitHub API response.
"""
        
        await client.fs_write_file(f"{analysis_dir}/report.md", report)
        
        print(f"\n✅ Issue analysis saved to {analysis_dir}/")
        
    except Exception as e:
        logger.error(f"Issue analysis workflow failed: {e}")
    finally:
        await client.close()


async def workflow_3_code_search_and_save():
    """
    Workflow 3: Search for code patterns across repositories and save results
    """
    print("\n🔎 Workflow 3: Code Search & Save")
    print("=" * 50)
    
    github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not github_token:
        print("❌ GitHub token required for this workflow")
        return
    
    client = UnifiedMCPClient(github_token)
    
    try:
        await client.start()
        
        # Configuration
        search_queries = [
            "async def user:Sathishruw",
            "FastMCPClient user:Sathishruw",
            "mcp.tool user:Sathishruw"
        ]
        results_dir = "code_search_results"
        
        # Create results directory
        await client.fs_write_file(f"{results_dir}/.gitkeep", "")
        
        all_results = {}
        
        for i, query in enumerate(search_queries):
            print(f"\n🔍 Searching for: {query}")
            
            try:
                search_results = await client.github_client.search_code(query)
                all_results[f"query_{i+1}"] = {
                    "query": query,
                    "results": search_results
                }
                
                # Save individual result
                await client.fs_write_file(
                    f"{results_dir}/search_{i+1}.json",
                    json.dumps(all_results[f"query_{i+1}"], indent=2)
                )
                
                print(f"✅ Results saved for query {i+1}")
                
            except Exception as e:
                print(f"❌ Search failed for '{query}': {e}")
        
        # Save combined results
        await client.fs_write_file(
            f"{results_dir}/all_searches.json",
            json.dumps(all_results, indent=2)
        )
        
        # Create summary report
        summary = f"""# Code Search Summary

Search Date: 2025-05-31
Total Queries: {len(search_queries)}

## Queries Executed:
"""
        for i, query in enumerate(search_queries, 1):
            summary += f"{i}. `{query}`\n"
        
        summary += f"""
## Results Location:
- Individual results: search_1.json, search_2.json, etc.
- Combined results: all_searches.json

## Note:
This is a demonstration of combining GitHub search with local file storage.
In practice, you'd parse the results to extract meaningful insights.
"""
        
        await client.fs_write_file(f"{results_dir}/summary.md", summary)
        
        print(f"\n🎉 Code search workflow completed! Results in {results_dir}/")
        
    except Exception as e:
        logger.error(f"Code search workflow failed: {e}")
    finally:
        await client.close()


async def workflow_4_repository_monitoring():
    """
    Workflow 4: Monitor repository activity and maintain local logs
    """
    print("\n📈 Workflow 4: Repository Monitoring")
    print("=" * 50)
    
    github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not github_token:
        print("❌ GitHub token required for this workflow")
        return
    
    client = UnifiedMCPClient(github_token)
    
    try:
        await client.start()
        
        # Configuration
        repos_to_monitor = [
            {"owner": "Sathishruw", "repo": "mcp-filesystem-client"}
        ]
        monitoring_dir = "repo_monitoring"
        
        # Create monitoring directory
        await client.fs_write_file(f"{monitoring_dir}/.gitkeep", "")
        
        for repo_info in repos_to_monitor:
            owner = repo_info["owner"]
            repo = repo_info["repo"]
            
            print(f"\n📊 Monitoring {owner}/{repo}...")
            
            try:
                # Get repository info
                repo_data = await client.github_client.get_repository(owner, repo)
                
                # Get recent issues
                issues = await client.github_client.list_issues(owner, repo, state="open")
                
                # Get recent pull requests
                prs = await client.github_client.list_pull_requests(owner, repo, state="open")
                
                # Create monitoring report
                monitoring_data = {
                    "repository": f"{owner}/{repo}",
                    "check_date": "2025-05-31",
                    "repository_info": repo_data,
                    "open_issues": issues,
                    "open_pull_requests": prs,
                    "status": "monitored"
                }
                
                # Save monitoring data
                filename = f"{monitoring_dir}/{owner}_{repo}_monitor.json"
                await client.fs_write_file(
                    filename,
                    json.dumps(monitoring_data, indent=2)
                )
                
                print(f"✅ Monitoring data saved to {filename}")
                
            except Exception as e:
                print(f"❌ Failed to monitor {owner}/{repo}: {e}")
        
        # Create monitoring summary
        summary = f"""# Repository Monitoring Summary

Last Updated: 2025-05-31
Monitored Repositories: {len(repos_to_monitor)}

## Repositories:
"""
        for repo_info in repos_to_monitor:
            summary += f"- {repo_info['owner']}/{repo_info['repo']}\n"
        
        summary += """
## Monitoring Data:
Each repository has its own monitoring file with:
- Repository metadata
- Open issues count and details
- Open pull requests count and details
- Last check timestamp

## Usage:
This data can be used for:
- Tracking repository activity
- Identifying maintenance needs
- Monitoring project health
- Creating dashboards
"""
        
        await client.fs_write_file(f"{monitoring_dir}/monitoring_summary.md", summary)
        
        print(f"\n🎉 Repository monitoring completed! Data in {monitoring_dir}/")
        
    except Exception as e:
        logger.error(f"Repository monitoring workflow failed: {e}")
    finally:
        await client.close()


async def main():
    """Run example workflows"""
    print("🚀 GitHub MCP Integration - Practical Examples")
    print("=" * 60)
    
    if not os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN"):
        print("❌ Please set GITHUB_PERSONAL_ACCESS_TOKEN environment variable")
        print("Export your GitHub token: export GITHUB_PERSONAL_ACCESS_TOKEN=your_token")
        return
    
    print("\nRunning example workflows...")
    
    # Run workflows
    await workflow_1_repository_backup()
    await workflow_2_issue_analysis()
    await workflow_3_code_search_and_save()
    await workflow_4_repository_monitoring()
    
    print("\n" + "=" * 60)
    print("🎉 All example workflows completed!")
    print("\nCheck the generated directories:")
    print("  - repo_backup/")
    print("  - issue_analysis/")
    print("  - code_search_results/")
    print("  - repo_monitoring/")


if __name__ == "__main__":
    asyncio.run(main())
