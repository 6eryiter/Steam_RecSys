import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 设置中文字体，防止图表里的中文变成方块（Windows系统适用）
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

print("正在加载清洗后的干净数据...")
# 读取洗干净的 CSV 文件，速度会极快
reviews_df = pd.read_csv('./data/processed_data/clean_reviews.csv')

print(f"成功加载 {reviews_df.shape[0]} 条评论数据，开始绘制大数据特征图表...")

# 创建一个宽画布，左右放两张图对比
fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# ==========================================
# 左图：真实游玩时长的“长尾效应”验证
# ==========================================
# 限制 x 轴到 500 小时，排除极端离群值以保证图表美观
sns.histplot(reviews_df['hours'], bins=100, ax=axes[0], color='skyblue')
axes[0].set_title('图1：用户游玩时长原始分布 (长尾效应)', fontsize=14)
axes[0].set_xlabel('游玩时长 (小时)', fontsize=12)
axes[0].set_ylabel('用户交互次数 (频数)', fontsize=12)
axes[0].set_xlim(0, 500)

# ==========================================
# 右图：算法入模前的“对数平滑处理”
# ==========================================
# 将时长经过自然对数处理，拉近至正态分布
reviews_df['log_hours'] = np.log1p(reviews_df['hours']) # log(x+1) 平滑

sns.histplot(reviews_df['log_hours'], bins=50, ax=axes[1], color='coral', kde=True)
axes[1].set_title('图2：游玩时长对数平滑处理后 (Log Transformation)', fontsize=14)
axes[1].set_xlabel('Log(游玩时长 + 1)', fontsize=12)
axes[1].set_ylabel('频数', fontsize=12)

# 调整布局并保存高清大图
plt.tight_layout()
plt.savefig('./data/processed_data/playtime_distribution.png', dpi=300)
print("图表绘制完成！请前往 data/processed_data 目录下查看 playtime_distribution.png")

# 在屏幕上展示出来
plt.show()