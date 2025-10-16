#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub 统计机器人测试脚本
用于验证配置和基本功能
"""

import os
import sys
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 设置 UTF-8 编码
if sys.platform.startswith('win'):
    os.system('chcp 65001 > nul')

# 添加当前目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_config():
    """测试配置文件"""
    print("🔍 测试配置文件...")
    
    # 测试 settings.json
    try:
        with open('config/settings.json', 'r', encoding='utf-8') as f:
            settings = json.load(f)
        print("✅ config/settings.json 加载成功")
        
        # 检查必需字段
        required_fields = ['daily_report', 'weekly_report']
        for field in required_fields:
            if field not in settings:
                print(f"[ERROR] 缺少字段: {field}")
                return False
            if 'enabled' not in settings[field]:
                print(f"[ERROR] {field} 缺少 enabled 字段")
                return False
        print("✅ 配置字段检查通过")
        
    except Exception as e:
        print(f"[ERROR] 加载 config/settings.json 失败: {e}")
        return False
    
    # 测试 repos.json
    try:
        with open('config/repos.json', 'r', encoding='utf-8') as f:
            repos = json.load(f)
        print("✅ config/repos.json 加载成功")
        
        if not isinstance(repos, list):
            print("[ERROR] repos.json 应该包含一个数组")
            return False
        
        if not repos:
            print("[ERROR] repos.json 为空")
            return False
        
        print(f"✅ 找到 {len(repos)} 个仓库")
        
    except Exception as e:
        print(f"[ERROR] 加载 config/repos.json 失败: {e}")
        return False
    
    return True

def test_environment():
    """测试环境变量"""
    print("\n🔍 测试环境变量...")
    
    # 加载 .env 文件（如果存在）
    if os.path.exists('.env'):
        load_dotenv()
        print("✅ 已加载 .env 文件")
    else:
        print("ℹ️  未找到 .env 文件，使用系统环境变量")
    
    # 检查 GitHub Token
    github_token = os.getenv('GITHUB_TOKEN')
    if github_token:
        print("✅ GITHUB_TOKEN 已设置")
    else:
        print("❌ GITHUB_TOKEN 未设置")
        return False
    
    # 检查邮件配置
    email_vars = ['EMAIL_USER', 'EMAIL_PASSWORD', 'SMTP_HOST', 'SMTP_PORT']
    email_configured = all(os.getenv(var) for var in email_vars)
    if email_configured:
        print("✅ 邮件配置完整")
    else:
        print("ℹ️  邮件配置不完整（可选）")
    
    # 检查 OneBot 配置
    onebot_vars = ['ONEBOT_URL', 'ONEBOT_QQ']
    onebot_configured = all(os.getenv(var) for var in onebot_vars)
    if onebot_configured:
        print("✅ OneBot 配置完整")
    else:
        print("ℹ️  OneBot 配置不完整（可选）")
    
    return True

def test_imports():
    """测试模块导入"""
    print("\n🔍 测试模块导入...")
    
    try:
        from stats_core import GitHubStatsCollector, generate_report
        print("✅ stats_core 模块导入成功")
    except Exception as e:
        print(f"❌ stats_core 模块导入失败: {e}")
        return False
    
    try:
        from send_utils import NotificationSender, send_notification
        print("[OK] send_utils 模块导入成功")
    except Exception as e:
        print(f"❌ send_utils 模块导入失败: {e}")
        return False
    
    return True

def test_basic_functionality():
    """测试基本功能"""
    print("\n测试基本功能...")
    
    try:
        from stats_core import GitHubStatsCollector, generate_report
        
        # 测试统计收集器初始化
        github_token = os.getenv('GITHUB_TOKEN')
        collector = GitHubStatsCollector(github_token)
        print("[OK] GitHubStatsCollector 初始化成功")
        
        # 测试报告生成（使用模拟数据）
        mock_stats = [{
            'repo_name': 'test/repo',
            'commits': {'total_commits': 10, 'additions': 100, 'deletions': 50},
            'issues': {'new_issues': 2, 'closed_issues': 1, 'comments': 5}
        }]
        
        since = datetime.utcnow() - timedelta(days=1)
        until = datetime.utcnow()
        
        report = generate_report(mock_stats, 'daily', since, until, True)
        if report and len(report) > 100:
            print("[OK] 报告生成功能正常")
        else:
            print("❌ 报告生成失败")
            return False
        
    except Exception as e:
        print(f"❌ 基本功能测试失败: {e}")
        return False
    
    return True

def main():
    """主测试函数"""
    print("🚀 GitHub 统计机器人测试开始\n")
    
    tests = [
        ("配置文件测试", test_config),
        ("环境变量测试", test_environment),
        ("模块导入测试", test_imports),
        ("基本功能测试", test_basic_functionality)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"❌ {test_name} 异常: {e}")
    
    print(f"\n测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("所有测试通过！机器人配置正确")
        return 0
    else:
        print("部分测试失败，请检查配置")
        return 1

if __name__ == '__main__':
    sys.exit(main())
