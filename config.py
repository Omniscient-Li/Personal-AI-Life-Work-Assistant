#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀助手配置文件
Configuration for Linx Assistant
"""

import os
from typing import Optional

class Config:
    """配置管理类"""
    
    def __init__(self):
        self.azure_openai_api_key: Optional[str] = None
        self.azure_openai_endpoint: Optional[str] = None
        self.azure_openai_deployment: Optional[str] = None
        self.azure_openai_api_version: str = "2024-02-15-preview"
        
        # 从环境变量加载配置
        self._load_from_env()
    
    def _load_from_env(self):
        """从环境变量加载配置"""
        self.azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_openai_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        
        if api_version := os.getenv("AZURE_OPENAI_API_VERSION"):
            self.azure_openai_api_version = api_version
    
    def setup_azure_openai(self, api_key: str, endpoint: str, deployment: str):
        """设置Azure OpenAI配置"""
        self.azure_openai_api_key = api_key
        self.azure_openai_endpoint = endpoint
        self.azure_openai_deployment = deployment
        
        # 设置环境变量
        os.environ["AZURE_OPENAI_API_KEY"] = api_key
        os.environ["AZURE_OPENAI_ENDPOINT"] = endpoint
        os.environ["AZURE_OPENAI_DEPLOYMENT"] = deployment
        os.environ["AZURE_OPENAI_API_VERSION"] = self.azure_openai_api_version
        
        print("✅ Azure OpenAI 配置已设置")
    
    def is_azure_configured(self) -> bool:
        """检查Azure OpenAI是否已配置"""
        return all([
            self.azure_openai_api_key,
            self.azure_openai_endpoint,
            self.azure_openai_deployment
        ])
    
    def get_config_summary(self) -> str:
        """获取配置摘要"""
        summary = "🔧 当前配置:\n"
        summary += f"  Azure OpenAI API Key: {'✅ 已设置' if self.azure_openai_api_key else '❌ 未设置'}\n"
        summary += f"  Azure OpenAI Endpoint: {'✅ 已设置' if self.azure_openai_endpoint else '❌ 未设置'}\n"
        summary += f"  Azure OpenAI Deployment: {'✅ 已设置' if self.azure_openai_deployment else '❌ 未设置'}\n"
        summary += f"  API Version: {self.azure_openai_api_version}\n"
        return summary

def setup_config():
    """交互式配置设置"""
    print("🔧 灵犀助手配置向导")
    print("=" * 40)
    
    config = Config()
    
    if config.is_azure_configured():
        print("✅ Azure OpenAI 已配置")
        print(config.get_config_summary())
        return config
    
    print("📝 请设置Azure OpenAI配置:")
    print("💡 您可以在Azure门户中找到这些信息")
    print()
    
    # 获取用户输入
    api_key = input("请输入Azure OpenAI API Key: ").strip()
    endpoint = input("请输入Azure OpenAI Endpoint (例如: https://your-resource.openai.azure.com/): ").strip()
    deployment = input("请输入Azure OpenAI Deployment名称: ").strip()
    
    if api_key and endpoint and deployment:
        config.setup_azure_openai(api_key, endpoint, deployment)
        print("\n✅ 配置完成！")
        return config
    else:
        print("\n⚠️ 配置不完整，将使用基础处理模式")
        return config

if __name__ == "__main__":
    config = setup_config()
    print("\n" + config.get_config_summary()) 