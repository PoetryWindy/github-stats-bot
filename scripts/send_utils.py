"""
通知发送工具模块
负责发送邮件和 OneBot 消息
"""

import os
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import requests


class NotificationSender:
    """通知发送器"""
    
    def __init__(self):
        """初始化通知发送器"""
        self.email_config = self._get_email_config()
        self.onebot_config = self._get_onebot_config()
    
    def _get_email_config(self) -> Optional[dict]:
        """获取邮件配置
        
        Returns:
            邮件配置字典，如果配置不完整则返回 None
        """
        required_vars = ['EMAIL_USER', 'EMAIL_PASSWORD', 'SMTP_HOST', 'SMTP_PORT']
        
        # 检查必需的环境变量
        for var in required_vars:
            if not os.getenv(var):
                print(f"邮件配置不完整，缺少环境变量: {var}")
                return None
        
        try:
            return {
                'user': os.getenv('EMAIL_USER'),
                'password': os.getenv('EMAIL_PASSWORD'),
                'host': os.getenv('SMTP_HOST'),
                'port': int(os.getenv('SMTP_PORT')),
                'use_tls': os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
            }
        except ValueError:
            print("SMTP 端口配置无效")
            return None
    
    def _get_onebot_config(self) -> Optional[dict]:
        """获取 OneBot 配置
        
        Returns:
            OneBot 配置字典，如果配置不完整则返回 None
        """
        required_vars = ['ONEBOT_URL', 'ONEBOT_QQ']
        
        # 检查必需的环境变量
        for var in required_vars:
            if not os.getenv(var):
                print(f"OneBot 配置不完整，缺少环境变量: {var}")
                return None
        
        return {
            'url': os.getenv('ONEBOT_URL'),
            'qq': os.getenv('ONEBOT_QQ')
        }
    
    def send_email(self, subject: str, content: str, recipients: Optional[list] = None) -> bool:
        """发送邮件
        
        Args:
            subject: 邮件主题
            content: 邮件内容
            recipients: 收件人列表，如果为 None 则使用环境变量或配置文件
            
        Returns:
            发送是否成功
        """
        if not self.email_config:
            print("邮件配置不完整，跳过邮件发送")
            return False
        
        try:
            # 确定收件人
            if recipients is None:
                # 优先使用环境变量
                env_recipient = os.getenv('EMAIL_RECIPIENT')
                if env_recipient:
                    recipients = [env_recipient]
                else:
                    # 使用配置文件中的收件人
                    recipients = self._get_config_recipients()
            
            if not recipients:
                print("未找到收件人配置")
                return False
            
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = self.email_config['user']
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            
            # 添加纯文本内容
            msg.attach(MIMEText(content, 'plain', 'utf-8'))
            
            # 发送邮件
            with smtplib.SMTP(self.email_config['host'], self.email_config['port']) as server:
                if self.email_config['use_tls']:
                    server.starttls()
                
                server.login(self.email_config['user'], self.email_config['password'])
                server.send_message(msg)
            
            print(f"邮件发送成功，收件人: {', '.join(recipients)}")
            return True
            
        except Exception as e:
            print(f"发送邮件时出错: {e}")
            return False
    
    def send_onebot(self, message: str) -> bool:
        """发送 OneBot 消息
        
        Args:
            message: 消息内容
            
        Returns:
            发送是否成功
        """
        if not self.onebot_config:
            print("OneBot 配置不完整，跳过 OneBot 发送")
            return False
        
        try:
            # 格式化消息（将 \n 转换为实际换行符）
            formatted_message = message.replace('\\n', '\n')
            
            # 准备请求数据
            data = {
                'user_id': int(self.onebot_config['qq']),
                'message': formatted_message
            }
            
            # 发送请求
            response = requests.post(
                self.onebot_config['url'],
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'ok':
                    print(f"OneBot 消息发送成功，QQ: {self.onebot_config['qq']}")
                    return True
                else:
                    print(f"OneBot 返回错误: {result.get('msg', '未知错误')}")
                    return False
            else:
                print(f"OneBot 请求失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"发送 OneBot 消息时出错: {e}")
            return False
    
    def _get_config_recipients(self) -> list:
        """从配置文件获取收件人列表
        
        Returns:
            收件人列表
        """
        try:
            import json
            with open('config/settings.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('email_recipients', [])
        except Exception as e:
            print(f"读取配置文件时出错: {e}")
            return []
    
    def send_all(self, subject: str, content: str, recipients: Optional[list] = None) -> dict:
        """发送所有类型的通知
        
        Args:
            subject: 邮件主题
            content: 消息内容
            recipients: 邮件收件人列表
            
        Returns:
            发送结果字典
        """
        results = {
            'email': False,
            'onebot': False
        }
        
        # 发送邮件
        if self.email_config:
            results['email'] = self.send_email(subject, content, recipients)
        
        # 发送 OneBot 消息
        if self.onebot_config:
            results['onebot'] = self.send_onebot(content)
        
        return results


def send_notification(subject: str, content: str, recipients: Optional[list] = None) -> dict:
    """发送通知的便捷函数
    
    Args:
        subject: 邮件主题
        content: 消息内容
        recipients: 邮件收件人列表
        
    Returns:
        发送结果字典
    """
    sender = NotificationSender()
    return sender.send_all(subject, content, recipients)
