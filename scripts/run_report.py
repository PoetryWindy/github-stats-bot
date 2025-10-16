#!/usr/bin/env python3
"""
GitHub 统计报告主入口脚本
支持每日和每周报告生成
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 添加当前目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stats_core import GitHubStatsCollector, generate_report
from send_utils import send_notification


def load_config(report_type: str) -> dict:
    """加载配置文件
    
    Args:
        report_type: 报告类型（"daily" 或 "weekly"）
        
    Returns:
        配置字典
    """
    try:
        with open('config/settings.json', 'r', encoding='utf-8') as f:
            settings = json.load(f)
        
        config_key = f"{report_type}_report"
        if config_key not in settings:
            raise ValueError(f"配置文件中未找到 {config_key} 配置")
        
        return settings[config_key]
    except Exception as e:
        print(f"加载配置文件时出错: {e}")
        sys.exit(1)


def load_repos() -> list:
    """加载仓库列表
    
    Returns:
        仓库列表
    """
    try:
        with open('config/repos.json', 'r', encoding='utf-8') as f:
            repos = json.load(f)
        
        if not isinstance(repos, list):
            raise ValueError("repos.json 应该包含一个仓库列表")
        
        if not repos:
            raise ValueError("repos.json 中未找到任何仓库")
        
        return repos
    except Exception as e:
        print(f"加载仓库列表时出错: {e}")
        sys.exit(1)


def get_time_range(days_back: int) -> tuple:
    """获取时间范围
    
    Args:
        days_back: 回溯天数
        
    Returns:
        (开始时间, 结束时间) 元组
    """
    now = datetime.utcnow()
    until = now.replace(hour=0, minute=0, second=0, microsecond=0)
    since = until - timedelta(days=days_back)
    
    return since, until


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='GitHub 统计报告生成器')
    parser.add_argument('report_type', choices=['daily', 'weekly'], 
                       help='报告类型：daily（每日）或 weekly（每周）')
    args = parser.parse_args()
    
    print(f"开始生成 {args.report_type} 统计报告...")
    
    # 加载环境变量（如果存在 .env 文件）
    if os.path.exists('.env'):
        load_dotenv()
        print("已加载 .env 文件中的环境变量")
    
    # 检查 GitHub Token
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        print("错误: 未找到 GITHUB_TOKEN 环境变量")
        sys.exit(1)
    
    # 加载配置
    config = load_config(args.report_type)
    if not config.get('enabled', False):
        print(f"{args.report_type} 报告已禁用，退出")
        sys.exit(0)
    
    repos = load_repos()
    print(f"将统计 {len(repos)} 个仓库: {', '.join(repos)}")
    
    # 获取时间范围
    since, until = get_time_range(config['days_back'])
    print(f"统计时间范围: {since.strftime('%Y-%m-%d %H:%M')} UTC 至 {until.strftime('%Y-%m-%d %H:%M')} UTC")
    
    # 创建统计收集器
    collector = GitHubStatsCollector(github_token)
    
    # 收集统计数据
    print("正在收集统计数据...")
    try:
        stats_list = collector.collect_all_stats(
            repos, 
            since, 
            until, 
            config.get('include_issues', True)
        )
        print("统计数据收集完成")
    except Exception as e:
        print(f"收集统计数据时出错: {e}")
        sys.exit(1)
    
    # 生成报告
    print("正在生成报告...")
    try:
        report_content = generate_report(
            stats_list,
            args.report_type,
            since,
            until,
            config.get('include_issues', True)
        )
        print("报告生成完成")
    except Exception as e:
        print(f"生成报告时出错: {e}")
        sys.exit(1)
    
    # 发送通知
    print("正在发送通知...")
    try:
        subject = f"GitHub {args.report_type.capitalize()} 统计报告"
        results = send_notification(subject, report_content)
        
        # 输出发送结果
        if results['email']:
            print("✓ 邮件发送成功")
        else:
            print("✗ 邮件发送失败或未配置")
        
        if results['onebot']:
            print("✓ OneBot 消息发送成功")
        else:
            print("✗ OneBot 消息发送失败或未配置")
        
        if not results['email'] and not results['onebot']:
            print("警告: 所有通知方式都未成功发送")
            # 将报告内容输出到控制台作为备选
            print("\n" + "="*50)
            print("报告内容:")
            print("="*50)
            print(report_content)
            print("="*50)
    
    except Exception as e:
        print(f"发送通知时出错: {e}")
        # 将报告内容输出到控制台作为备选
        print("\n" + "="*50)
        print("报告内容:")
        print("="*50)
        print(report_content)
        print("="*50)
    
    print(f"{args.report_type} 统计报告处理完成")


if __name__ == '__main__':
    main()
