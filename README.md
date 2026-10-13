# Steam_RecSys · Steam 游戏智能推荐与生态分析系统

> 一个融合 **协同过滤（LightFM）+ 文本语义理解（DistilBERT）** 的 Steam 游戏推荐系统，
> 配套完整的数据清洗 / 特征工程 / 模型训练管线，以及 Vue 3 可视化前端与实时数据大屏。

![status](https://img.shields.io/badge/status-active-brightgreen)
![python](https://img.shields.io/badge/python-3.10-blue)
![vue](https://img.shields.io/badge/vue-3-42b883)
![flask](https://img.shields.io/badge/flask-3.0-000000)
![license](https://img.shields.io/badge/license-MIT-yellow)

---

## 目录

- [一、项目简介](#一项目简介)
- [二、核心功能](#二核心功能)
- [三、系统架构](#三系统架构)
- [四、推荐算法设计](#四推荐算法设计)
- [五、技术栈](#五技术栈)
- [六、项目结构](#六项目结构)
- [七、快速开始](#七快速开始)
- [八、API 接口文档](#八api-接口文档)
- [九、数据库表结构](#九数据库表结构)
- [十、常见问题 FAQ](#十常见问题-faq)
- [十一、已知限制与后续规划](#十一已知限制与后续规划)
- [十二、关于仓库中的大文件](#十二关于仓库中的大文件)

---

## 一、项目简介

Steam 平台拥有数万款游戏，玩家面对庞大的商店页面常常陷入「选择困难」。
本项目从 **UCSD Steam 公开数据集**（游戏元数据 + 用户评论）出发，构建了一套完整的
「数据清洗 → 语义特征提取 → 混合推荐模型 → Web 服务 → 可视化前端」链路：

- 用 **DistilBERT** 把用户评论编码成 768 维语义向量，PCA 压缩到 32 维，
  让「评论写了什么」这一文本信号真正进入推荐模型；
- 用 **LightFM（WARP 损失）** 同时建模用户–游戏交互与游戏内容特征，
  并以 `log(1 + 游玩时长)` 作为隐式反馈权重，让「玩得久」比「只点开过」更有话语权；
- 用 **Steam 官方接口 + SteamSpy + DeepSeek 大模型** 为推荐结果补充实时价格、
  好评率过滤、热玩榜与自然语言推荐理由，解决「推荐得准但说服力不足」的问题。

项目既是一个可直接运行的推荐系统 Demo，也是一份可复现的推荐算法工程实践。

## 二、核心功能

| 模块 | 功能 | 说明 |
| --- | --- | --- |
| 个性化推荐 | 老用户协同过滤推荐 | LightFM 打分 → 排序取 Top100 → 好评率过滤 → 分页返回 |
| 个性化推荐 | 新用户冷启动 | 输入 17 位 SteamID64，读取真实游戏库，用物品向量的余弦相似度推荐 |
| 质量过滤 | 实时好评率漏斗 | 多线程调用 Steam 评论接口，剔除「评价数 < 100」或「好评率 < 70%」的游戏 |
| 实时数据 | 价格 / 折扣 / 在线人数 | Steam Store API + `GetNumberOfCurrentPlayers`，带内存缓存与超时兜底 |
| 热玩榜 | SteamSpy Top20 | 近两周热玩榜 + 本地保底数据，接口异常也不会白屏 |
| AI 能力 | 推荐理由生成 | DeepSeek Chat 生成 60 字推荐语，按标签提炼玩法亮点 |
| AI 能力 | 玩家灵魂画像 | DeepSeek 依据玩家游戏库生成称号与口味性格分析 |
| 用户系统 | 注册 / 登录 / 绑定 Steam | Werkzeug 密码哈希 + 头像上传 + Steam 账号绑定 |
| 可视化大屏 | 8 张 ECharts 图表 | 发行趋势、词云、旭日图、四象限矩阵、漏斗、极性饼图、矩形树图等 |
| 内容探索 | 首页无限滚动、游戏搜索 | 随机抽样 + 图片存活探测，保证展示质量 |

## 三、系统架构

```
                       ┌──────────────────────────────────────┐
                       │   浏览器 · Vue 3 SPA (Vite)          │
                       │   Home/Recommend/Search/Ranking/     │
                       │   Dashboard/UserPersona ...          │
                       └───────────────┬──────────────────────┘
                                       │ axios · JSON (HTTP/CORS)
                                       ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                    Flask REST API  (app.py · :5000)                       │
│                                                                           │
│  推荐引擎                       业务能力                     外部依赖      │
│  ├ LightFM (WARP/64维)          ├ 用户注册登录                ├ Steam      │
│  ├ 物品语义向量 (BERT 32维)      ├ 头像上传 / Steam 绑定        │  Store API  │
│  └ 冷启动余弦相似度              ├ 内存缓存 (推荐 30min)        ├ Steam      │
│                                  └ 多线程并发请求              │  Web API   │
│                                                               ├ SteamSpy   │
│                                                               ├ Steam 评论 │
│                                                               └ DeepSeek   │
└───────────────────────┬───────────────────────────────────────────────────┘
                        │ PyMySQL / SQLAlchemy
                        ▼
          ┌─────────────────────────────────────────┐
          │  MySQL · steam_recsys                   │
          │  games │ users │ clean_reviews │ games_data │
          └─────────────────────────────────────────┘

────────────────────────── 离线训练管线 ──────────────────────────
 steam_games.json.gz ┐
                     ├─▶ 01 数据探查 ─▶ 02 清洗 ─▶ 03 分布可视化
 steam_reviews.json.gz ┘                      │
                                              ▼
                     04 DistilBERT 编码 (768维) ─▶ PCA (32维) ─▶ 30 万条训练集
                                              │
                                              ▼
                     05 LightFM 训练 (时长加权 + 物品特征) ─▶ model/*.pkl
```

## 四、推荐算法设计

### 1. 数据侧：从「打分」到「行为强度」

- 过滤游玩时长 < 0.1 小时的记录（退款 / 误触），并且必须有评论文本；
- 交互权重取 `w = log1p(hours) + 1`，对数平滑既保留「时长 = 喜爱程度」的先验，
  又避免少数上万小时的记录主导训练（长尾分布见 `03_data_visualization.py` 输出）；
- 交互矩阵经 `random_train_test_split(test_percentage=0.2)` 划分 80% / 20%。

### 2. 特征侧：让评论文本进入模型

```
评论文本 ─▶ DistilBERT (均值池化) ─▶ 768 维 ─▶ PCA ─▶ 32 维（bert_f_0 ... bert_f_31）
                                                          │
                       按 product_id 聚合求均值 ────────────┘
                                                          ▼
        item_features = [ 单位矩阵 (物品 ID 特征) │ 标准化后的 32 维语义特征 ]
```

单位矩阵让模型仍能学习每个游戏独立的隐向量（纯协同过滤信号），
语义特征则让特征稀疏、交互很少的游戏也能借助「玩法标签相似」被推荐出去。

### 3. 模型侧：LightFM 混合矩阵分解

| 参数 | 取值 | 说明 |
| --- | --- | --- |
| `loss` | `warp` | 针对隐式反馈的排序损失，比 BPR 更贴合「推荐 TopN」目标 |
| `no_components` | 64 | 隐向量维度 |
| `learning_rate` | 0.05 | 学习率 |
| `item_alpha` / `user_alpha` | 1e-4 | L2 正则，抑制过拟合 |
| `max_sampled` | 20 | 负采样上限，兼顾效果与训练速度 |
| `epochs` | 40 | 训练轮数 |

评估使用 `lightfm.evaluation.auc_score`，训练结束后脚本会打印训练集 / 测试集 AUC。

### 4. 服务侧：双引擎 + 质量漏斗

```
请求 /api/recommend?username=xxx&page=n
        │
        ├─ 命中 30 分钟内存缓存 ─▶ 直接分页返回
        │
        ├─ 老用户 ─▶ LightFM 全量打分 ─▶ Top100 ─┐
        │                                        ├─▶ 多线程好评率过滤
        └─ 新用户 (17 位 SteamID64)              │    (≥100 条评价 且 好评率 ≥70%)
              ├ GetOwnedGames 拉取库存            │            │
              ├ 物品向量均值 = 用户口味向量        │            ▼
              ├ 余弦相似度排序（剔除已拥有）───────┘    每页 10 条返回
              └ 库存私密 / 为空 ─▶ 明确提示 404
```

这条「算法排序 → 业务过滤」的分层设计是本项目与传统协同过滤 Demo 最大的差异点：
模型只负责「像不像你的口味」，质量漏斗负责「值不值得推荐给你」。

## 五、技术栈

| 层次 | 技术选型 |
| --- | --- |
| 算法 | LightFM 1.17、DistilBERT (`distilbert-base-uncased`)、scikit-learn PCA / StandardScaler |
| 后端 | Python 3.10、Flask 3、Flask-Cors、Werkzeug Security、PyMySQL、SQLAlchemy |
| 数据 | pandas、NumPy、SciPy 稀疏矩阵、Matplotlib / Seaborn |
| 前端 | Vue 3、Vite 8、vue-router 4、Bootstrap 5、ECharts 5 + echarts-wordcloud、axios |
| 存储 | MySQL 8 |
| 外部服务 | Steam Store API、Steam Web API、SteamSpy、DeepSeek Chat API |

## 六、项目结构

```
Steam_RecSys/
├── 01_inspect_data.py              # 数据探查：读取 json.gz，检查字段与规模
├── 02_data_cleaning.py             # 数据清洗：剔除噪声，产出 clean_games / clean_reviews
├── 03_data_visualization.py        # 分布可视化：游玩时长长尾效应 + 对数平滑对比
├── 04_bert_feature_engineering.py  # BERT 语义特征：768 维 → PCA 32 维，产出训练集
├── 05_train_lightfm_model.py       # LightFM 训练与 AUC 评估，产出 model/*.pkl
├── app.py                          # Flask 后端主程序（推荐 / 用户 / 榜单 / 大屏 / AI）
├── peek_users.py                   # 小工具：查看可用于测试的真实用户名
├── config.example.py               # 配置模板（复制为 config.py 后填入密钥）
├── requirements.txt                # Python 依赖
├── data/                           # 数据集目录（raw_data 与 processed_data 不入库）
│   ├── raw_data/                   # 需自行下载的原始 json.gz
│   └── processed_data/             # 清洗结果、可视化图表、最终训练集
├── model/                          # 训练产物：模型与 ID 映射（体积过大，不入库）
├── static/avatars/                 # 用户上传的头像（运行时生成，不入库）
└── steam-frontend/                 # Vue 3 前端工程（详见其 README）
    ├── src/views/                  # 9 个页面组件
    └── src/router/index.js         # 路由与登录守卫
```

## 七、快速开始

### 0. 环境要求

| 组件 | 版本建议 |
| --- | --- |
| Python | 3.9 – 3.11（推荐 3.10） |
| Node.js | ≥ 18（Vite 8 要求） |
| MySQL | 5.7 / 8.0 |
| 显卡（可选） | 支持 CUDA 的 NVIDIA 显卡可显著加速 BERT 特征提取 |

### 1. 获取代码

```bash
git clone <本仓库地址> Steam_RecSys
cd Steam_RecSys
pip install -r requirements.txt
```

### 2. 数据准备

下载 UCSD（Julian McAuley）公开的 Steam 数据集，并把两个文件放进 `data/raw_data/`：

```
data/raw_data/steam_games.json.gz     # 游戏元数据（含 tags）
data/raw_data/steam_reviews.json.gz   # 用户评论（含 hours / text）
```

数据集主页：<https://cseweb.ucsd.edu/~jmcauley/datasets.html#steam_data>

> 目录中的原始数据集**不会**随仓库分发：体积过大，且属于第三方数据，请自行下载。
> 若只需要跑通线上服务，可以跳过第 3 步，直接使用自己已有的 `model/*.pkl` 与数据库。

### 3. 运行离线训练管线

```bash
# ① 探查数据结构与规模
python 01_inspect_data.py

# ② 清洗，产出 data/processed_data/clean_games.csv 与 clean_reviews.csv
python 02_data_cleaning.py

# ③ 查看游玩时长分布与对数平滑效果（生成 playtime_distribution.png）
python 03_data_visualization.py

# ④ BERT 语义特征 + PCA 降维，产出 final_training_data_300k.csv
#    默认抽样 30 万条评论；无 GPU 时请下调脚本中的 SAMPLE_SIZE
python 04_bert_feature_engineering.py

# ⑤ 训练 LightFM 模型并输出 AUC，产出 model/*.pkl
#    注意：脚本按相对路径读取 final_training_data_300k.csv
cd data/processed_data && python ../../05_train_lightfm_model.py
```

`04` 默认通过 `HF_ENDPOINT=https://hf-mirror.com` 下载 `distilbert-base-uncased`，
国内网络无需额外配置；如需切换到官方源，删除脚本中的该环境变量即可。

### 4. 初始化数据库

```sql
CREATE DATABASE steam_recsys DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
```

建表语句见 [九、数据库表结构](#九数据库表结构)。
`games` 与 `clean_reviews` 两张表的数据请从第 3 步产出的 CSV 导入；
`games_data` 表供可视化大屏使用，可自行整理或直接复用清洗结果。

### 5. 配置密钥与数据库连接

```bash
# Windows
copy config.example.py config.py
# macOS / Linux
cp config.example.py config.py
```

然后编辑 `config.py`，填入 Steam Web API Key、DeepSeek API Key 与 MySQL 账号密码。
`config.py` 已在 `.gitignore` 中，**不会被提交到仓库**。

### 6. 启动后端

```bash
python app.py
# 服务地址：http://127.0.0.1:5000
```

启动日志出现 `引擎唤醒成功！等待前端请求...` 表示模型与数据库连接均正常。

### 7. 启动前端

```bash
cd steam-frontend
npm install
npm run dev
# 打开 http://localhost:5173
```

### 8. 快速体验建议

1. 注册一个账号，或在 `model/user_mapping.pkl` 中用 `peek_users.py` 查一个真实玩家名；
2. 老用户直接进入「智能推荐」页查看协同过滤结果；
3. 想体验冷启动，可在绑定处填入一个 **17 位 SteamID64**（需将「游戏详情」设为公开）；
4. 「数据大屏」与「玩家画像」分别展示统计分析与大模型生成内容。

## 八、API 接口文档

统一前缀 `/api`，默认端口 `5000`，全部开启 CORS。

| 方法 | 路径 | 参数 | 返回要点 |
| --- | --- | --- | --- |
| GET | `/api/recommend` | `username`、`page` | 每页 10 条：游戏名、标签、封面、现价/原价/折扣；`has_more` 控制翻页 |
| POST | `/api/register` | form-data：`username`、`password`、`nickname`、`steam_identifier`(可选)、`avatar`(文件，可选) | 密码经 `generate_password_hash` 存储；用户名重复返回 409 |
| POST | `/api/login` | JSON：`username`、`password` | 返回 `token`(uuid) 与用户信息；失败返回 401 |
| POST | `/api/bind_steam` | JSON：`username`、`steam_identifier` | 更新用户的 Steam 绑定，冷启动推荐的前提 |
| GET | `/api/explore_games` | `limit`（默认 20） | 随机抽样 + 实时价格 + 封面存活探测，自动剔除下架游戏 |
| GET | `/api/search` | `keyword` | 游戏名模糊匹配（`LIKE`，最多 20 条） |
| GET | `/api/ranking` | — | SteamSpy 近两周 Top20 热玩榜，含在线人数与实时价格（失败时返回本地保底数据） |
| GET | `/api/game_stats/<game_id>` | 路径参数为 Steam AppID | 评价分布（饼图）与当前在线人数（仪表盘）所需数据 |
| GET | `/api/dashboard_data` | — | 大屏所需 8 组聚合数据（年度趋势、标签词云、价格–口碑旭日图、四象限矩阵、开发商 Top10 等） |
| POST | `/api/ai_reason` | JSON：`game_name`、`game_tags` | DeepSeek 生成的约 60 字推荐语 |
| GET | `/api/user_persona` | `username`（或 17 位 SteamID64） | DeepSeek 生成的 `{title, content}` 玩家画像 |

调用示例：

```bash
curl "http://127.0.0.1:5000/api/recommend?username=steam_player&page=1"
curl "http://127.0.0.1:5000/api/search?keyword=Portal"
curl -X POST "http://127.0.0.1:5000/api/login" -H "Content-Type: application/json" \
     -d '{"username":"demo","password":"123456"}'
```

## 九、数据库表结构

> 以下 DDL 依据 `app.py` 中的查询语句整理，可直接执行；字段长度可按数据规模自行调整。

```sql
-- 游戏元数据（推荐结果与榜单的标签来源）
CREATE TABLE games (
    id        BIGINT       NOT NULL COMMENT 'Steam AppID',
    app_name  VARCHAR(255) NOT NULL COMMENT '游戏名称',
    tags      TEXT                  COMMENT '标签，Python 列表字面量字符串，如 ["Indie","RPG"]',
    PRIMARY KEY (id),
    KEY idx_app_name (app_name)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- 用户表
CREATE TABLE users (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    username         VARCHAR(64)  NOT NULL COMMENT '登录名',
    password         VARCHAR(255) NOT NULL COMMENT 'Werkzeug 哈希后的密码',
    steam_identifier VARCHAR(64)           COMMENT 'Steam 用户名或 17 位 SteamID64',
    nickname         VARCHAR(64)           COMMENT '昵称',
    avatar           VARCHAR(255)          COMMENT '头像地址',
    UNIQUE KEY uk_username (username)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- 清洗后的评论/行为表（训练数据的线上副本，用于老用户画像查询）
CREATE TABLE clean_reviews (
    username   VARCHAR(64) NOT NULL,
    product_id VARCHAR(32) NOT NULL COMMENT 'Steam AppID（字符串形式）',
    hours      FLOAT                COMMENT '游玩时长（小时）',
    text       TEXT                 COMMENT '评论正文',
    KEY idx_username (username),
    KEY idx_product (product_id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- 可视化大屏专用宽表
CREATE TABLE games_data (
    id                   INT AUTO_INCREMENT PRIMARY KEY,
    game_name            VARCHAR(255) NOT NULL,
    tags                 TEXT                  COMMENT '英文标签，逗号分隔，如 "Indie,Action"',
    positive_reviews     INT DEFAULT 0,
    negative_reviews     INT DEFAULT 0,
    avg_playtime_forever FLOAT DEFAULT 0       COMMENT '平均总时长（分钟）',
    peak_ccu             INT DEFAULT 0,
    price                FLOAT DEFAULT 0       COMMENT '价格（USD，0 表示免费）',
    release_date         DATE                  COMMENT '发行日期，用于年度趋势统计',
    developers           VARCHAR(255)          COMMENT '开发商，用于 Top10 统计'
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;
```

## 十、常见问题 FAQ

**Q1：`app.py` 启动时报「缺少配置文件 config.py」？**
请按第 5 步从 `config.example.py` 复制出 `config.py` 并填写真实值。密钥不会随仓库分发。

**Q2：推荐接口返回 404「未找到该玩家」？**
说明该用户名既不在 `model/user_mapping.pkl` 中，也不是合法的 17 位 SteamID64。
老用户请使用训练数据中出现过的用户名（可用 `peek_users.py` 查看）。

**Q3：输入 SteamID64 提示「库存为空或未公开」？**
需要在 Steam 隐私设置中把「游戏详情」设为公开，`GetOwnedGames` 才能读取库存。

**Q4：`05_train_lightfm_model.py` 报找不到 `final_training_data_300k.csv`？**
该脚本使用相对路径读取文件，请先 `cd data/processed_data` 再执行（见第 3 步第 ⑤ 条）。

**Q5：Windows 上 `pip install lightfm` 编译失败？**
LightFM 需要 C 编译器，推荐使用 conda 安装：
`conda install -c conda-forge lightfm`。

**Q6：BERT 特征提取太慢 / 显存不足？**
脚本会自动选择 `cuda` 或 `cpu`；无 GPU 时请调小 `SAMPLE_SIZE`（如 3 万条）与 `batch_size`。

**Q7：大屏或首页偶尔有游戏显示不出来？**
这是预期行为：`/api/explore_games` 会主动剔除下架、锁区、无报价或封面 404 的游戏。

## 十一、已知限制与后续规划

作为课程 / 毕设项目，当前实现为「先跑通、再优化」的取舍结果，以下问题已明确识别：

| 类别 | 现状 | 改进方向 |
| --- | --- | --- |
| 接口地址 | 前端硬编码 `127.0.0.1:5000` | 抽取 `VITE_API_BASE`，支持多环境配置 |
| 认证 | 登录仅返回 uuid，接口不做鉴权校验 | 引入 JWT + 统一鉴权装饰器 |
| 数据一致性 | 物品向量均值在训练脚本中 `iterrows` 逐行写入 | 改为向量化 `reindex` 或稀疏矩阵直构 |
| 缓存 | 内存字典缓存，进程重启即失效 | 迁移到 Redis，支持多实例部署 |
| 统计口径 | `/api/game_stats` 的好评率为估算值 | 直接调用 Steam 评论接口的真实正负评数 |
| 评估 | 仅离线 AUC | 补充 Precision@K / Recall@K / NDCG 与 A/B 实验框架 |
| 特征 | 仅文本语义 + 交互 | 引入价格、发行年份、开发商等更多内容特征 |
| 部署 | 本地 `debug=True` 直跑 | gunicorn + Nginx + Docker Compose 一键部署 |

## 十二、关于仓库中的大文件

为保证仓库可以被正常 `clone` 与 `push`（GitHub 单文件上限 100 MB），以下内容
**已通过 `.gitignore` 排除**，请按第七节自行生成或下载：

| 路径 | 体积（约） | 说明 |
| --- | --- | --- |
| `model/lightfm_model.pkl` | 188 MB | LightFM 训练产物，由 `05` 生成 |
| `model/user_mapping.pkl` / `item_mapping.pkl` / `item_features.pkl` | 4 MB / 0.2 MB / 2.5 MB | ID 映射与物品特征，由 `05` 生成 |
| `data/raw_data/*.json.gz` | 数十 GB | 第三方原始数据集，需自行下载 |
| `data/processed_data/*` | 视抽样规模 | 清洗结果与训练集，由 `02` / `04` 生成 |
| `static/avatars/*` | 随使用增长 | 用户上传的头像，属运行时数据 |
| `config.py` | — | 个人密钥与数据库口令 |
| `steam-frontend/node_modules/` | 129 MB | 前端依赖，`npm install` 还原 |

如需把模型一并纳入版本管理，推荐改用 **Git LFS**：

```bash
git lfs install
git lfs track "model/*.pkl"
git add .gitattributes && git commit -m "chore: 使用 Git LFS 管理模型产物"
```

## 致谢

- 数据集：[UCSD Steam Datasets](https://cseweb.ucsd.edu/~jmcauley/datasets.html#steam_data)（Julian McAuley 等）
- 推荐算法：[LightFM](https://github.com/lyst/lightfm)（Lyst）
- 文本模型：[DistilBERT](https://huggingface.co/distilbert-base-uncased)（Hugging Face）
- 数据来源：Steam Store API、Steam Web API、SteamSpy
- 大模型能力：DeepSeek Chat API

## License

本项目基于 MIT License 开源，仅供学习与研究使用。
使用 Steam 相关接口时请遵守 [Steam Web API 使用条款](https://steamcommunity.com/dev/apiterms)，
并注意控制请求频率。
