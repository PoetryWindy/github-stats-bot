# GitHub 统计机器人配置指南

## 🚀 快速配置步骤

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 创建环境配置文件

复制 `env.example` 为 `.env` 并填入真实配置：

```bash
cp env.example .env
```

然后编辑 `.env` 文件，填入以下配置：

```bash
# GitHub API Token (必需)
GITHUB_TOKEN=ghp_your_actual_token_here

# 邮件配置（可选）
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_RECIPIENT=your_email@gmail.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true

# OneBot 配置（可选）
ONEBOT_URL=http://localhost:5700/send_private_msg
ONEBOT_QQ=123456789
```

### 3. 配置仓库列表

编辑 `config/repos.json`，添加要统计的仓库：

```json
[
  "microsoft/vscode",
  "facebook/react",
  "nodejs/node",
  "your-org/your-repo"
]
```

### 4. 运行测试

```bash
python test_bot.py
```

### 5. 运行实际报告

```bash
# 测试每日报告
python scripts/run_report.py daily

# 测试每周报告
python scripts/run_report.py weekly
```

## 📋 配置说明

### GitHub Token 获取

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token" > "Generate new token (classic)"
3. 选择权限：至少需要 `repo` 权限
4. 复制生成的 token 到 `.env` 文件

### Gmail 邮件配置

1. 启用两步验证
2. 生成应用专用密码：
   - 访问 https://myaccount.google.com/security
   - 点击 "应用专用密码"
   - 生成新密码用于此应用
3. 使用应用专用密码作为 `EMAIL_PASSWORD`

### OneBot 配置

如果您有 OneBot 服务，配置相应的 URL 和 QQ 号。如果没有，可以跳过此配置。

## 🔍 故障排除

### 常见问题

1. **ImportError: No module named 'github'**
   ```bash
   pip install PyGithub
   ```

2. **GitHub API 限流**
   - 检查 token 权限
   - 减少仓库数量
   - 等待限流重置

3. **邮件发送失败**
   - 检查 SMTP 配置
   - 确认使用应用专用密码
   - 检查网络连接

4. **仓库访问失败**
   - 确认仓库名称格式正确
   - 检查 token 权限
   - 确认仓库存在且可访问

## 📊 测试输出示例

成功的测试输出应该类似：

```
🚀 GitHub 统计机器人测试开始

🔍 测试配置文件...
✅ config/settings.json 加载成功
✅ 配置字段检查通过
✅ config/repos.json 加载成功
✅ 找到 3 个仓库

🔍 测试环境变量...
✅ 已加载 .env 文件
✅ GITHUB_TOKEN 已设置
✅ 邮件配置完整
ℹ️  OneBot 配置不完整（可选）

🔍 测试模块导入...
✅ stats_core 模块导入成功
✅ send_utils 模块导入成功

🔍 测试基本功能...
✅ GitHubStatsCollector 初始化成功
✅ 报告生成功能正常

📊 测试结果: 4/4 通过
🎉 所有测试通过！机器人配置正确
```
