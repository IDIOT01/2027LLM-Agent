#!/usr/bin/env python3
"""
Gmail 手动授权脚本
运行后复制链接到浏览器，授权完成后把跳转后的完整URL粘贴回来
"""
import json
import warnings
warnings.filterwarnings("ignore")

from pathlib import Path
from google_auth_oauthlib.flow import Flow

BASE_DIR = Path(__file__).parent
CREDENTIALS_PATH = BASE_DIR / "credentials.json"
TOKEN_PATH = BASE_DIR / "token.json"
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"

flow = Flow.from_client_secrets_file(
    str(CREDENTIALS_PATH),
    scopes=SCOPES,
    redirect_uri=REDIRECT_URI,
)

auth_url, _ = flow.authorization_url(prompt="consent")

print("=" * 60)
print("  Gmail 授权")
print("=" * 60)
print()
print("请复制以下链接到浏览器打开：")
print()
print(auth_url)
print()
code = input("授权完成后，把页面上显示的授权码粘贴到这里: ").strip()

flow.fetch_token(code=code)
creds = flow.credentials

with open(TOKEN_PATH, "w") as f:
    f.write(creds.to_json())

print()
print("[DONE] 授权成功！token 已保存到 token.json")
