# -*- coding: utf-8 -*-
"""
Steam_RecSys 本地配置模板
--------------------------------------------------------------
使用方式：
    1. 复制本文件并重命名为 config.py（与 app.py 同一目录）
    2. 按自己的环境填写下面的密钥与数据库信息
    3. config.py 已被 .gitignore 排除，不会被提交到 GitHub / Gitee

注意：请勿把填写了真实密钥的 config.py 提交到任何公开仓库。
"""

# ==========================================================
# 1. Steam Web API Key
#    申请地址：https://steamcommunity.com/dev/apikey
#    用途：新用户冷启动时通过 GetOwnedGames 接口读取玩家游戏库
# ==========================================================
STEAM_API_KEY = "YOUR_STEAM_API_KEY"

# ==========================================================
# 2. DeepSeek API Key（用于生成推荐语与玩家"灵魂画像"）
#    申请地址：https://platform.deepseek.com/api_keys
# ==========================================================
DEEPSEEK_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# ==========================================================
# 3. MySQL 数据库连接信息
#    数据库名默认 steam_recsys，建表语句见 README
# ==========================================================
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = "your_mysql_password"
DB_NAME = "steam_recsys"

# 供 pymysql.connect(**DB_CONFIG) 使用
DB_CONFIG = dict(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
)

# 供 SQLAlchemy / pandas.read_sql 使用
DB_URI = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    "?charset=utf8mb4"
)
