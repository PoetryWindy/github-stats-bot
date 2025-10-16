# GitHub 统计机器人

基于 GitHub Actions 和 Python 的自动化 GitHub 统计机器人，支持每日和每周报告生成，通过邮件和 OneBot 发送通知。

## ✨ 功能特性

- 📊 **多仓库统计**: 支持统计多个 GitHub 仓库的代码提交和 Issue 活动
- ⏰ **灵活周期**: 支持每日报告（24小时）和每周报告（7天）
- 📧 **多种通知**: 支持邮件和 OneBot 消息通知
- 🔒 **安全配置**: 敏感信息通过环境变量管理，配置文件仅存储非敏感设置
- 🚀 **自动化部署**: 基于 GitHub Actions 实现完全自动化
- 🛡️ **容错机制**: 完善的错误处理，单个仓库失败不影响整体流程
- 📈 **详细统计**: 排除 Merge 提交，提供净增代码行数等关键指标

## 项目结构

```
github_bot/
├── .github/workflows/          # GitHub Actions 工作流
│   ├── daily-stats.yml        # 每日报告工作流
│   └── weekly-stats.yml       # 每周报告工作流
├── config/                     # 配置文件目录
│   ├── settings.json          # 报告配置
│   └── repos.json             # 仓库列表
├── scripts/                    # Python 脚本
│   ├── run_report.py          # 主入口脚本
│   ├── stats_core.py          # 统计核心模块
│   └── send_utils.py          # 通知发送模块
├── requirements.txt            # Python 依赖
├── env.example                # 环境变量模板
├── .gitignore                 # Git 忽略文件
└── README.md                  # 项目说明
```

## 🚀 快速开始

### 1. Fork 或克隆仓库

```bash
git clone [https://github.com/your-username/github_bot.git](https://github.com/PoetryWindy/github-stats-bot.git)
cd github_bot
```

### 2. 配置仓库列表

编辑 `config/repos.json` 文件，添加要统计的仓库：

```json
[
  "microsoft/vscode",
  "facebook/react", 
  "nodejs/node",
  "your-org/your-repo"
]
```

### 3. 配置报告设置

编辑 `config/settings.json` 文件：

```json
{
  "daily_report": {
    "enabled": true,
    "days_back": 1,
    "include_issues": true
  },
  "weekly_report": {
    "enabled": true,
    "days_back": 7,
    "include_issues": true
  },
  "email_recipients": [
    "admin@example.com"
  ]
}
```

### 4. 配置环境变量

在 GitHub 仓库的 Settings > Secrets and variables > Actions 中添加以下 Secrets：

#### 必需的环境变量
- `GITHUB_TOKEN`: GitHub API Token（通常由 GitHub Actions 自动提供）

#### 邮件配置（可选）
- `EMAIL_USER`: 发件人邮箱
- `EMAIL_PASSWORD`: 邮箱密码或应用专用密码
- `EMAIL_RECIPIENT`: 收件人邮箱（优先级高于配置文件）
- `SMTP_HOST`: SMTP 服务器地址
- `SMTP_PORT`: SMTP 端口
- `SMTP_USE_TLS`: 是否使用 TLS（true/false）

#### OneBot 配置（可选）
- `ONEBOT_URL`: OneBot HTTP API 地址
- `ONEBOT_QQ`: 目标 QQ 号

### 5. 本地测试

1. 复制 `env.example` 为 `.env` 并填入真实配置：
   ```bash
   cp env.example .env
   # 编辑 .env 文件，填入真实配置
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 运行测试：
   ```bash
   # 测试每日报告
   python scripts/run_report.py daily
   
   # 测试每周报告  
   python scripts/run_report.py weekly
   ```

4. 运行测试脚本验证配置：
   ```bash
   python test_bot.py
   ```

5. 检查输出，确保统计数据和通知发送正常

## 统计内容

### 代码提交统计
- 总提交次数（排除 Merge 提交）
- 新增代码行数
- 删除代码行数
- 净增代码行数

### Issue 活动统计
- 新增 Issue 数量
- 关闭 Issue 数量
- 评论总数

## 报告格式

报告采用纯文本格式，包含：
- 时间范围信息
- 总体统计数据
- 各仓库详细统计
- 生成时间戳

示例报告：
```
📊 GitHub Daily 统计报告
⏰ 时间范围: 2024-01-15 00:00 UTC 至 2024-01-16 00:00 UTC
📁 统计仓库数: 3

📈 总体统计:
  • 代码提交: 1,234 次
  • 新增代码: 45,678 行
  • 删除代码: 12,345 行
  • 净增代码: 33,333 行
  • 新增 Issue: 56 个
  • 关闭 Issue: 42 个
  • 评论总数: 234 条

📋 各仓库详情:
...
```

## 工作流说明

### 每日报告
- 触发时间：每天 UTC 0:00（北京时间 8:00）
- 统计范围：过去 24 小时
- 支持手动触发

### 每周报告
- 触发时间：每周一 UTC 0:00（北京时间 8:00）
- 统计范围：过去 7 天
- 支持手动触发

## 🔧 故障排除

### 常见问题

1. **API 限流**: GitHub API 有速率限制，如果仓库过多可能触发限流
   - 解决方案：减少仓库数量或增加请求间隔
   
2. **权限不足**: 确保 GITHUB_TOKEN 有足够权限访问目标仓库
   - 解决方案：检查 token 权限，确保有 `repo` 权限
   
3. **邮件发送失败**: 检查 SMTP 配置和邮箱设置
   - 解决方案：验证 SMTP 服务器地址、端口、用户名密码
   - 注意：Gmail 需要使用应用专用密码
   
4. **OneBot 连接失败**: 确认 OneBot 服务运行正常且 URL 正确
   - 解决方案：检查 OneBot 服务状态和 API 地址
   
5. **仓库不存在或无法访问**: 检查仓库名称格式和访问权限
   - 解决方案：确保仓库名称格式为 `owner/repo`，且 token 有访问权限

### 调试模式

使用 `workflow_dispatch` 触发工作流时，可以启用 dry run 模式，只生成报告不上传，便于调试。

### 日志查看

在 GitHub Actions 中查看详细日志：
1. 进入仓库的 Actions 页面
2. 点击对应的 workflow 运行记录
3. 查看 "Run daily/weekly stats report" 步骤的日志

### 本地调试

如果本地运行出现问题，可以添加调试输出：
```bash
# 启用详细输出
python -u scripts/run_report.py daily 2>&1 | tee debug.log
```

## 📋 配置示例

### 邮件配置示例（Gmail）

```bash
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_RECIPIENT=admin@company.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
```

### OneBot 配置示例

```bash
ONEBOT_URL=http://localhost:5700/send_private_msg
ONEBOT_QQ=123456789
```

### 仓库配置示例

```json
[
  "microsoft/vscode",
  "facebook/react",
  "nodejs/node",
  "your-org/private-repo",
  "another-org/another-repo"
]
```

## 💡 最佳实践

1. **仓库选择**: 建议选择活跃度适中的仓库，避免选择过于活跃的仓库导致 API 限流
2. **时间设置**: 每日报告建议在 UTC 0:00 运行，避免跨时区问题
3. **通知配置**: 建议同时配置邮件和 OneBot，确保重要信息不遗漏
4. **权限管理**: 使用最小权限原则，GITHUB_TOKEN 只需要 `repo` 权限
5. **监控告警**: 定期检查 GitHub Actions 运行状态，确保报告正常生成

## 🔄 更新和维护

### 更新依赖

```bash
pip install --upgrade -r requirements.txt
```

### 修改配置

1. 修改 `config/settings.json` 调整报告设置
2. 修改 `config/repos.json` 更新仓库列表
3. 在 GitHub Secrets 中更新环境变量

### 版本升级

1. 拉取最新代码：`git pull origin main`
2. 检查配置文件是否有变更
3. 测试新版本：`python scripts/run_report.py daily`

## 技术栈

- **Python 3.10+**: 主要编程语言
- **PyGithub**: GitHub API 客户端
- **requests**: HTTP 请求库
- **python-dotenv**: 环境变量管理
- **GitHub Actions**: 自动化部署平台

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 开发指南

1. Fork 仓库
2. 创建功能分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -m 'Add some feature'`
4. 推送分支：`git push origin feature/your-feature`
5. 创建 Pull Request

## 📞 支持

如果遇到问题，请：
1. 查看 [故障排除](#-故障排除) 部分
2. 搜索已有的 [Issues](https://github.com/your-username/github_bot/issues)
3. 创建新的 Issue 描述问题
