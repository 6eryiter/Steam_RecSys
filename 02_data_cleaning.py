import pandas as pd
import gzip
import os

# 自动创建目标文件夹（防止保存时报错）
os.makedirs('./data/processed_data', exist_ok=True)

# 修复了单引号问题的读取函数
def load_data_fast(path, max_rows=None):
    data = []
    # 使用 'rt' 模式直接读取文本
    with gzip.open(path, 'rt', encoding='utf-8') as g:
        for i, line in enumerate(g):
            if max_rows is not None and i >= max_rows:
                break
            # 填坑：因为数据集是不规范的单引号格式，必须用 eval 而不能用 json.loads
            data.append(eval(line))
    return pd.DataFrame(data)

print("开始执行大数据 ETL 清洗流程...\n")

# ==========================================
# 步骤 1：处理游戏元数据 (Games)
# ==========================================
print("1. 正在读取并清洗游戏元数据...")
# 读取游戏数据（全量）
games_df = load_data_fast('./data/raw_data/steam_games.json.gz')

# 只保留做推荐系统需要的核心列
# 注意：有些游戏可能没有 genres，我们保留 tags
cols_to_keep = ['id', 'app_name', 'tags']
# 如果列存在就保留，防止某些版本数据集字段名对不上
games_df = games_df[[c for c in cols_to_keep if c in games_df.columns]]

# 丢掉没有游戏ID或名字的“幽灵游戏”
games_df = games_df.dropna(subset=['id', 'app_name'])

# 将清洗后的数据保存到 processed_data 文件夹
games_df.to_csv('./data/processed_data/clean_games.csv', index=False, encoding='utf-8')
print(f"游戏数据清洗完毕！剩余高质量游戏: {games_df.shape[0]} 款。已保存至 clean_games.csv\n")


# ==========================================
# 步骤 2：处理用户评论数据 (Reviews)
# ==========================================
print("2. 正在读取并清洗用户评论数据...")

# 读取评论数据（全量读取，你的电脑扛得住！）
reviews_df = load_data_fast('./data/raw_data/steam_reviews.json.gz')

print(f"\n   - 原始评论总数: {reviews_df.shape[0]} 条")

# 只保留我们需要的列
reviews_df = reviews_df[['username', 'product_id', 'hours', 'text']]

# 【核心工作量体现】
# 1. 过滤掉游玩时间小于 0.1 小时的“退款/误触”数据
reviews_df = reviews_df[reviews_df['hours'] >= 0.1]
# 2. 过滤掉没有写评论文本的（必须有文本才能跑 BERT）
reviews_df = reviews_df.dropna(subset=['text'])
# 3. 过滤掉没有对应游戏ID的用户
reviews_df = reviews_df.dropna(subset=['product_id', 'username'])

print(f"   - 过滤后剩余的高质量评论数: {reviews_df.shape[0]} 条")

# 将清洗后的数据保存到 processed_data 文件夹
reviews_df.to_csv('./data/processed_data/clean_reviews.csv', index=False, encoding='utf-8')
print("评论数据清洗完毕！已保存至 clean_reviews.csv\n")

print("全部数据清洗完毕！")