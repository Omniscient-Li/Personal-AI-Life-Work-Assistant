#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀助手配置文件
Configuration for Linx Assistant
"""

import os
from typing import Optional


class Config:
    """DeepSeek / SiliconFlow 配置管理类"""

    def __init__(self):
        # 核心配置
        self.deepseek_api_key: Optional[str] = None
        self.deepseek_api_url: str = "https://api.siliconflow.cn/v1/chat/completions"
        self.model: Optional[str] = None

        # 生成相关参数（与 silicon_client 中环境变量保持一致）
        self.max_token: Optional[int] = None
        self.temperature: Optional[float] = None
        self.top_p: Optional[float] = None
        self.top_k: Optional[int] = None
        self.frequency_penalty: Optional[float] = None
        self.min_p: Optional[float] = None

        # 从环境变量加载配置
        self._load_from_env()

    def _load_from_env(self):
        """从环境变量加载 DeepSeek / SiliconFlow 配置"""
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.deepseek_api_url = os.getenv("DEEPSEEK_API_URL", self.deepseek_api_url)
        self.model = os.getenv("MODEL")

        self.max_token = self._get_int("MAX_TOKEN")
        self.temperature = self._get_float("TEMPERATURE")
        self.top_p = self._get_float("TOP_P")
        self.top_k = self._get_int("TOP_K")
        self.frequency_penalty = self._get_float("FREQUENCY_PENALTY")
        self.min_p = self._get_float("MIN_P")

    @staticmethod
    def _get_int(name: str) -> Optional[int]:
        v = os.getenv(name)
        if v is None or v == "":
            return None
        try:
            return int(v)
        except ValueError:
            return None

    @staticmethod
    def _get_float(name: str) -> Optional[float]:
        v = os.getenv(name)
        if v is None or v == "":
            return None
        try:
            return float(v)
        except ValueError:
            return None

    def setup_deepseek(self, api_key: str, api_url: Optional[str] = None, model: Optional[str] = None):
        """交互式设置 DeepSeek / SiliconFlow 配置，并写入环境变量"""
        self.deepseek_api_key = api_key
        if api_url:
            self.deepseek_api_url = api_url
        if model:
            self.model = model

        os.environ["DEEPSEEK_API_KEY"] = self.deepseek_api_key
        os.environ["DEEPSEEK_API_URL"] = self.deepseek_api_url
        if self.model:
            os.environ["MODEL"] = self.model

        print("DeepSeek / SiliconFlow 配置已设置")

    def is_deepseek_configured(self) -> bool:
        """检查 DeepSeek API 是否已配置"""
        return bool(self.deepseek_api_key)

    def get_config_summary(self) -> str:
        """获取配置摘要"""
        summary = "当前 DeepSeek / SiliconFlow 配置:\n"
        summary += f"  API Key: {'已设置' if self.deepseek_api_key else '未设置'}\n"
        summary += f"  API URL: {self.deepseek_api_url}\n"
        summary += f"  模型(Model): {self.model or '未设置 (将使用 silicon_client 默认)'}\n"
        summary += f"  MAX_TOKEN: {self.max_token if self.max_token is not None else '未设置'}\n"
        summary += f"  TEMPERATURE: {self.temperature if self.temperature is not None else '未设置'}\n"
        summary += f"  TOP_P: {self.top_p if self.top_p is not None else '未设置'}\n"
        summary += f"  TOP_K: {self.top_k if self.top_k is not None else '未设置'}\n"
        summary += f"  FREQUENCY_PENALTY: {self.frequency_penalty if self.frequency_penalty is not None else '未设置'}\n"
        summary += f"  MIN_P: {self.min_p if self.min_p is not None else '未设置'}\n"
        return summary

def setup_config():
    """交互式配置设置（用于本地测试环境）"""
    print("灵犀助手 DeepSeek / SiliconFlow 配置向导")
    print("=" * 40)

    config = Config()

    if config.is_deepseek_configured():
        print("已检测到 DEEPSEEK_API_KEY")
        print(config.get_config_summary())
        return config

    print("请设置 DeepSeek / SiliconFlow 配置:")
    print("建议在项目根目录的 .env 中设置，也可以在这里临时输入")
    print()

    # 获取用户输入
    api_key = input("请输入 DEEPSEEK_API_KEY: ").strip()
    api_url = input("请输入 DEEPSEEK_API_URL (回车使用默认 https://api.siliconflow.cn/v1/chat/completions): ").strip()
    model = input("请输入模型名称 MODEL (例如: Qwen/Qwen2.5-7B-Instruct，回车使用系统默认): ").strip()

    if api_key:
        config.setup_deepseek(api_key, api_url or None, model or None)
        print("\n配置完成！")
        return config
    else:
        print("\n未提供 API Key，将使用基础处理/Mock 模式")
        return config

if __name__ == "__main__":
    config = setup_config()
    print("\n" + config.get_config_summary()) 