"""
GitHub 统计核心模块
负责从 GitHub API 获取提交和 Issue 数据，并生成统计报告
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from github import Github, GithubException


class GitHubStatsCollector:
    """GitHub 统计收集器"""
    
    def __init__(self, token: str):
        """初始化统计收集器
        
        Args:
            token: GitHub API token
        """
        self.github = Github(token)
    
    def fetch_commits(self, repo_name: str, since: datetime, until: datetime) -> Dict[str, int]:
        """获取指定时间范围内的提交统计
        
        Args:
            repo_name: 仓库名称，格式为 "owner/repo"
            since: 开始时间
            until: 结束时间
            
        Returns:
            包含统计数据的字典：{
                'total_commits': 总提交数,
                'additions': 新增行数,
                'deletions': 删除行数
            }
        """
        try:
            repo = self.github.get_repo(repo_name)
            commits = repo.get_commits(since=since, until=until)
            
            total_commits = 0
            total_additions = 0
            total_deletions = 0
            
            for commit in commits:
                # 排除 Merge 提交
                if len(commit.parents) <= 1:
                    total_commits += 1
                    
                    # 获取提交的统计信息
                    try:
                        stats = commit.stats
                        if stats:
                            total_additions += stats.additions
                            total_deletions += stats.deletions
                    except GithubException:
                        # 如果无法获取统计信息，跳过
                        pass
            
            return {
                'total_commits': total_commits,
                'additions': total_additions,
                'deletions': total_deletions
            }
            
        except GithubException as e:
            print(f"获取仓库 {repo_name} 的提交数据时出错: {e}")
            return {
                'total_commits': 0,
                'additions': 0,
                'deletions': 0
            }
    
    def fetch_issues(self, repo_name: str, since: datetime, until: datetime) -> Dict[str, int]:
        """获取指定时间范围内的 Issue 统计
        
        Args:
            repo_name: 仓库名称，格式为 "owner/repo"
            since: 开始时间
            until: 结束时间
            
        Returns:
            包含统计数据的字典：{
                'new_issues': 新增 Issue 数,
                'closed_issues': 关闭 Issue 数,
                'comments': 评论数
            }
        """
        try:
            repo = self.github.get_repo(repo_name)
            
            # 获取新增的 Issue
            new_issues_count = 0
            closed_issues_count = 0
            comments_count = 0
            
            # 获取所有 Issue（包括已关闭的）
            all_issues = repo.get_issues(state='all', since=since)
            for issue in all_issues:
                # 统计新增的 Issue
                if issue.created_at >= since and issue.created_at <= until:
                    new_issues_count += 1
                    comments_count += issue.comments
                
                # 统计关闭的 Issue
                if (issue.closed_at and 
                    issue.closed_at >= since and 
                    issue.closed_at <= until):
                    closed_issues_count += 1
            
            return {
                'new_issues': new_issues_count,
                'closed_issues': closed_issues_count,
                'comments': comments_count
            }
            
        except GithubException as e:
            print(f"获取仓库 {repo_name} 的 Issue 数据时出错: {e}")
            return {
                'new_issues': 0,
                'closed_issues': 0,
                'comments': 0
            }
    
    def collect_repo_stats(self, repo_name: str, since: datetime, until: datetime, include_issues: bool = True) -> Dict:
        """收集单个仓库的完整统计信息
        
        Args:
            repo_name: 仓库名称
            since: 开始时间
            until: 结束时间
            include_issues: 是否包含 Issue 统计
            
        Returns:
            包含仓库统计信息的字典
        """
        print(f"正在收集仓库 {repo_name} 的统计数据...")
        
        # 获取提交统计
        commit_stats = self.fetch_commits(repo_name, since, until)
        
        # 获取 Issue 统计（如果启用）
        issue_stats = {}
        if include_issues:
            issue_stats = self.fetch_issues(repo_name, since, until)
        
        return {
            'repo_name': repo_name,
            'commits': commit_stats,
            'issues': issue_stats if include_issues else None
        }
    
    def collect_all_stats(self, repo_list: List[str], since: datetime, until: datetime, include_issues: bool = True) -> List[Dict]:
        """收集所有仓库的统计信息
        
        Args:
            repo_list: 仓库列表
            since: 开始时间
            until: 结束时间
            include_issues: 是否包含 Issue 统计
            
        Returns:
            包含所有仓库统计信息的列表
        """
        all_stats = []
        
        for repo_name in repo_list:
            try:
                stats = self.collect_repo_stats(repo_name, since, until, include_issues)
                all_stats.append(stats)
            except Exception as e:
                print(f"处理仓库 {repo_name} 时出错: {e}")
                # 添加空统计信息以保持一致性
                all_stats.append({
                    'repo_name': repo_name,
                    'commits': {'total_commits': 0, 'additions': 0, 'deletions': 0},
                    'issues': {'new_issues': 0, 'closed_issues': 0, 'comments': 0} if include_issues else None
                })
        
        return all_stats


def generate_report(stats_list: List[Dict], report_type: str, since: datetime, until: datetime, include_issues: bool = True) -> str:
    """生成统计报告文本
    
    Args:
        stats_list: 统计信息列表
        report_type: 报告类型（"daily" 或 "weekly"）
        since: 开始时间
        until: 结束时间
        include_issues: 是否包含 Issue 统计
        
    Returns:
        格式化的报告文本
    """
    # 计算总计
    total_commits = sum(repo['commits']['total_commits'] for repo in stats_list)
    total_additions = sum(repo['commits']['additions'] for repo in stats_list)
    total_deletions = sum(repo['commits']['deletions'] for repo in stats_list)
    
    total_new_issues = 0
    total_closed_issues = 0
    total_comments = 0
    
    if include_issues:
        total_new_issues = sum(repo['issues']['new_issues'] for repo in stats_list if repo['issues'])
        total_closed_issues = sum(repo['issues']['closed_issues'] for repo in stats_list if repo['issues'])
        total_comments = sum(repo['issues']['comments'] for repo in stats_list if repo['issues'])
    
    # 生成报告标题
    report_title = f"GitHub {report_type.capitalize()} 统计报告"
    time_range = f"{since.strftime('%Y-%m-%d %H:%M')} UTC 至 {until.strftime('%Y-%m-%d %H:%M')} UTC"
    
    # 生成报告内容
    report_lines = [
        f"📊 {report_title}",
        f"⏰ 时间范围: {time_range}",
        f"📁 统计仓库数: {len(stats_list)}",
        "",
        "📈 总体统计:",
        f"  • 代码提交: {total_commits:,} 次",
        f"  • 新增代码: {total_additions:,} 行",
        f"  • 删除代码: {total_deletions:,} 行",
        f"  • 净增代码: {total_additions - total_deletions:,} 行"
    ]
    
    if include_issues:
        report_lines.extend([
            f"  • 新增 Issue: {total_new_issues:,} 个",
            f"  • 关闭 Issue: {total_closed_issues:,} 个",
            f"  • 评论总数: {total_comments:,} 条"
        ])
    
    report_lines.extend([
        "",
        "📋 各仓库详情:",
        ""
    ])
    
    # 添加各仓库详情
    for repo in stats_list:
        repo_name = repo['repo_name']
        commits = repo['commits']
        
        report_lines.extend([
            f"🔹 {repo_name}:",
            f"  • 提交: {commits['total_commits']:,} 次",
            f"  • 新增: {commits['additions']:,} 行",
            f"  • 删除: {commits['deletions']:,} 行",
            f"  • 净增: {commits['additions'] - commits['deletions']:,} 行"
        ])
        
        if include_issues and repo['issues']:
            issues = repo['issues']
            report_lines.extend([
                f"  • 新增 Issue: {issues['new_issues']:,} 个",
                f"  • 关闭 Issue: {issues['closed_issues']:,} 个",
                f"  • 评论: {issues['comments']:,} 条"
            ])
        
        report_lines.append("")
    
    report_lines.extend([
        "---",
        f"报告生成时间: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
        "Powered by GitHub Stats Bot"
    ])
    
    return "\n".join(report_lines)
