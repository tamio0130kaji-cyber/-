"""Anthropic APIクライアントのヘルパー。"""
import os

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = "claude-sonnet-5"


def get_client() -> Anthropic:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            ".envにANTHROPIC_API_KEYが設定されていません。.env.exampleを参考に設定してください。"
        )
    return Anthropic(api_key=api_key)


def get_model() -> str:
    return os.environ.get("CLAUDE_MODEL", DEFAULT_MODEL)
