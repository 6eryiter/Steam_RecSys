import pandas as pd
import numpy as np
import scipy.sparse as sp
from lightfm import LightFM
from lightfm.evaluation import auc_score
from lightfm.cross_validation import random_train_test_split
from sklearn.preprocessing import StandardScaler
import pickle
import os

print("[1/6] 正在加载包含游玩时长与文本语义特征的训练数据...")
df = pd.read_csv('final_training_data_300k.csv')

# 清洗基础数据
df = df.dropna(subset=['username', 'product_id'])
df['hours'] = df['hours'].fillna(0).clip(lower=0)

print(f"成功加载 {df.shape[0]} 条全量交互数据。")

# ==========================================
# 1. 构建 ID 映射字典
# ==========================================
print("[2/6] 正在构建用户和游戏的数学映射字典...")
unique_users = df['username'].unique()
unique_items = df['product_id'].unique()

user_to_index = {user: idx for idx, user in enumerate(unique_users)}
item_to_index = {item: idx for idx, item in enumerate(unique_items)}

os.makedirs('./model', exist_ok=True)
with open('./model/user_mapping.pkl', 'wb') as f:
    pickle.dump(user_to_index, f)
with open('./model/item_mapping.pkl', 'wb') as f:
    pickle.dump(item_to_index, f)

# ==========================================
# 2. 构建商品混合特征矩阵 (引入标准化)
# ==========================================
print("[3/6] 正在提取并标准化 BERT 语义特征...")
bert_cols = [f'bert_f_{i}' for i in range(32)]

item_semantics = df.groupby('product_id')[bert_cols].mean()

semantic_matrix = np.zeros((len(unique_items), 32), dtype=np.float32)
for prod_id, row_data in item_semantics.iterrows():
    if prod_id in item_to_index:
        idx = item_to_index[prod_id]
        semantic_matrix[idx] = row_data.values

scaler = StandardScaler()
semantic_matrix_scaled = scaler.fit_transform(semantic_matrix)

eye = sp.eye(len(unique_items), format='csr', dtype=np.float32)
semantic_sparse = sp.csr_matrix(semantic_matrix_scaled)
item_features = sp.hstack([eye, semantic_sparse]).tocsr()

with open('./model/item_features.pkl', 'wb') as f:
    pickle.dump(item_features, f)

# ==========================================
# 3. 构建交互稀疏矩阵
# ==========================================
print("[4/6] 正在构建交互矩阵并计算时长权重...")
user_indices = df['username'].map(user_to_index).values.astype(np.int32)
item_indices = df['product_id'].map(item_to_index).values.astype(np.int32)

weights = np.log1p(df['hours'].values) + 1.0
weights = weights.astype(np.float32)

interactions = sp.coo_matrix(
    (weights, (user_indices, item_indices)),
    shape=(len(unique_users), len(unique_items))
)

interactions = interactions.tocsr()
interactions.eliminate_zeros()
interactions = interactions.tocoo()

train, test = random_train_test_split(interactions, test_percentage=0.2, random_state=42)
print(f"数据处理完毕！总用户数: {len(unique_users)}, 游戏数: {len(unique_items)}。")

# ==========================================
# 4. 训练深度混合模型 (黄金平衡参数)
# ==========================================
print("\n[5/6] 开始训练")

# 参数说明：
# 恢复使用全量 30w 数据，让模型看遍所有的关联图谱
# no_components=64: 经典的隐向量维度
# item_alpha/user_alpha=1e-4: 中度正则化，防止 1.0 过拟合
# max_sampled=20: 降低负采样，大幅提升训练和预测的速度
model = LightFM(
    loss='warp',
    no_components=64,
    learning_rate=0.05,
    item_alpha=1e-4,
    user_alpha=1e-4,
    max_sampled=20,
    random_state=42
)

model.fit(
    train,
    item_features=item_features,
    epochs=40,
    num_threads=4,
    verbose=True
)

# ==========================================
# 5. 模型评估与保存
# ==========================================
print("\n[6/6] 训练完成！正在计算最终得分...")

test_auc = auc_score(
    model,
    test,
    train_interactions=train,
    item_features=item_features,
    num_threads=4
).mean()

train_auc = auc_score(
    model,
    train,
    item_features=item_features,
    num_threads=4
).mean()

print(f"模型在 [训练集] 上的 AUC 得分: {train_auc:.4f}")
print(f"模型在 [测试集] 上的 AUC 得分: {test_auc:.4f}")

with open('./model/lightfm_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("\n模型及相关组件已保存至 ./model 目录。")