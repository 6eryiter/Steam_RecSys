import pandas as pd
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.decomposition import PCA
from tqdm import tqdm
import os
import gc

# 设置国内镜像源，加速下载预训练模型
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

print("正在加载环境与数据...")

# 1. 读取清洗后的数据
reviews_df = pd.read_csv('./data/processed_data/clean_reviews.csv')

# 按照你的要求，抽取 30 万条核心数据！
SAMPLE_SIZE = 300000
if len(reviews_df) > SAMPLE_SIZE:
    reviews_df = reviews_df.sample(n=SAMPLE_SIZE, random_state=42).reset_index(drop=True)

print(f"成功抽取 {SAMPLE_SIZE} 条核心数据。")

# 2. 加载轻量级 BERT 模型
print("正在加载 DistilBERT 模型...")
model_name = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"当前计算设备: {device}")
model.to(device)
model.eval()


# 3. 核心升级：批处理提速函数
def get_bert_embeddings_batch(texts, batch_size=64):
    all_embeddings = []

    # 每次取 64 条文本打包送进模型
    for i in tqdm(range(0, len(texts), batch_size), desc="BERT 批处理进度"):
        batch_texts = texts[i: i + batch_size].tolist()

        # 将文本转化为 BERT token
        inputs = tokenizer(batch_texts, return_tensors="pt", truncation=True, padding=True, max_length=128)
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model(**inputs)

        # 取平均值作为句子向量 (768维)
        embeddings = outputs.last_hidden_state.mean(dim=1).cpu().numpy()
        all_embeddings.extend(embeddings)

        # 释放内存，防止电脑卡死
        del inputs, outputs, embeddings
        if i % 5000 == 0:
            gc.collect()

    return np.array(all_embeddings)


print("\n引擎启动！开始提取高维语义特征...")
texts_series = reviews_df['text'].astype(str)

# 执行批处理提取
X_features = get_bert_embeddings_batch(texts_series, batch_size=64)
print(f"\n特征提取完成！当前原始特征矩阵维度: {X_features.shape}")

# 4. PCA 降维压缩 (将 768 维压缩到 32 维)
print("\n正在启动 PCA 主成分分析进行特征降维...")
pca = PCA(n_components=32, random_state=42)
X_pca = pca.fit_transform(X_features)

print(f"PCA 降维完成！当前降维后矩阵维度: {X_pca.shape}")
explained_var = sum(pca.explained_variance_ratio_) * 100
print(f"这 32 个核心维度保留了原始文本约 {explained_var:.2f}% 的信息量。")

# 5. 合并并保存最终的训练集
print("\n正在保存最终数据集...")
feature_cols = [f'bert_f_{i}' for i in range(32)]
pca_df = pd.DataFrame(X_pca, columns=feature_cols)

final_df = pd.concat([reviews_df, pca_df], axis=1)

final_df.to_csv('./data/processed_data/final_training_data_300k.csv', index=False)
print("10万条数据的多模态文本特征工程全部处理完毕！")
print("数据已安全保存至 final_training_data_300k.csv，现在可以随时关闭电脑了。")