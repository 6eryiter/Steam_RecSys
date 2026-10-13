import pandas as pd
import gzip
import json

# 这是一个专门用来读取 UCSD .json.gz 格式数据的辅助函数
def parse(path):
    g = gzip.open(path, 'rb')
    for l in g:
        yield eval(l)

def getDF(path):
    i = 0
    df = {}
    for d in parse(path):
        df[i] = d
        i += 1
    return pd.DataFrame.from_dict(df, orient='index')

# 1. 读取游戏元数据 (请确保路径和你的文件名一致)
print("正在读取游戏数据...")
steam_reviews = getDF('./data/raw_data/steam_reviews.json.gz')
steam_games = getDF('./data/raw_data/steam_games.json.gz')


# 2. 打印看看我们拿到了什么
print(f"成功加载游戏总数: {steam_reviews.shape[0]} 款")
print("\n数据集的前 3 行样子：")
print(steam_reviews.head(3)) # 如果用的是普通的.py文件，把 display 换成 print

print(f"成功加载游戏总数: {steam_games.shape[0]} 款")
print("\n数据集的前 3 行样子：")
print(steam_games.head(3)) # 如果用的是普通的.py文件，把 display 换成 print

# 3. 看看包含哪些列（比如 tags, description）
print("\n包含的数据字段有：", steam_reviews.columns.tolist())
print("\n包含的数据字段有：", steam_games.columns.tolist())