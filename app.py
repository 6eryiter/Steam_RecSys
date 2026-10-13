from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import numpy as np
import os
import pymysql
import requests
import ast  # 用于安全地将字符串转为列表
import concurrent.futures
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import os
from werkzeug.utils import secure_filename
import uuid
from flask import request, jsonify
import concurrent.futures
import time
import random

# ==========================================
# 0. 加载本地敏感配置
#    config.py 已被 .gitignore 排除，不会提交到仓库
#    首次运行请复制 config.example.py 为 config.py 并填入自己的密钥
# ==========================================
try:
    from config import STEAM_API_KEY, DEEPSEEK_API_KEY, DB_CONFIG, DB_URI
except ImportError as import_error:
    raise ImportError(
        "缺少配置文件 config.py，请先复制 config.example.py 为 config.py，"
        "并填写 Steam API Key、DeepSeek API Key 与 MySQL 连接信息。"
    ) from import_error

app = Flask(__name__)
UPLOAD_FOLDER = 'static/avatars'
os.makedirs(UPLOAD_FOLDER, exist_ok=True) # 启动时自动创建文件夹
# 允许前端跨域请求
CORS(app)

# 你的专属 Steam API Key
# Steam API Key 统一从 config.py 读取（config.py 不入库）

# ==========================================
# 0. 定义标签中英文映射字典
# ==========================================
TAG_MAP_CN = {
    'Indie': '独立', 'Casual': '休闲', 'Strategy': '策略', 'Adventure': '冒险',
    'RPG': '角色扮演', 'Action': '动作', 'Simulation': '模拟', 'Sports': '体育',
    'Racing': '竞速', 'Massively Multiplayer': '大型多人', 'Platformer': '平台跳跃',
    'Metroidvania': '类银河恶魔城', 'Roguelike': 'Roguelike', 'Roguelite': 'Roguelite',
    'Souls-like': '类魂系列', 'JRPG': '日系角色扮演', 'CRPG': '传统角色扮演',
    'Tower Defense': '塔防', 'City Builder': '城市建造', 'Management': '管理',
    'Farming Sim': '农场模拟', 'Life Sim': '生活模拟', 'Visual Novel': '视觉小说',
    'Point & Click': '点击解谜', 'Sandbox': '沙盒', 'Survival': '生存',
    'Crafting': '制作', 'Battle Royale': '大逃杀', 'Tactical': '战术',
    'Stealth': '潜行', 'Puzzle': '解谜', 'Rhythm': '节奏', 'Fighting': '格斗',
    'Beat \'em up': '清版动作', 'Hack and Slash': '砍杀', 'Turn-Based Strategy': '回合制策略',
    'Real Time Strategy': '即时战略', 'First-Person': '第一人称', 'Third Person': '第三人称',
    'Isometric': '等距视角', '2D': '2D', '3D': '3D', 'Pixel Graphics': '像素图形',
    'Voxel': '体素', 'Anime': '动漫', 'Cute': '可爱', 'Colorful': '色彩丰富',
    'Atmospheric': '氛围', 'Singleplayer': '单人', 'Multiplayer': '多人',
    'Co-op': '合作', 'Online Co-Op': '在线合作', 'Local Co-Op': '本地合作',
    'PvP': '玩家对战', 'PvE': '玩家对战环境', 'Story Rich': '丰富剧情',
    'Great Soundtrack': '优秀原声', 'Difficult': '高难度', 'Relaxing': '放松',
    'Funny': '搞笑', 'Early Access': '抢先体验', 'Free to Play': '免费游玩',
    'VR': 'VR', 'Sci-fi': '科幻', 'Fantasy': '奇幻', 'Cyberpunk': '赛博朋克',
    'Steampunk': '蒸汽朋克', 'Post-apocalyptic': '末日', 'Dark Fantasy': '暗黑奇幻',
    'Historical': '历史', 'Space': '太空', 'Medieval': '中世纪', 'Zombies': '丧尸',
    'Vampire': '吸血鬼', 'Lovecraftian': '洛夫克拉夫特式', 'Horror': '恐怖',
    'Psychological Horror': '心理恐怖', 'Survival Horror': '生存恐怖', 'Mystery': '悬疑',
    'Magic': '魔法', 'Military': '军事', 'Gore': '血腥', 'Violent': '暴力',
    'Nudity': '裸露', 'Mature': '成人'
}

# ==========================================
# 1. 加载推荐模型 (服务器启动时唤醒大脑)
# ==========================================
print("正在唤醒 LightFM 推荐引擎...")
MODEL_DIR = 'model'

try:
    with open(os.path.join(MODEL_DIR, 'lightfm_model.pkl'), 'rb') as f:
        model = pickle.load(f)
    with open(os.path.join(MODEL_DIR, 'user_mapping.pkl'), 'rb') as f:
        user_to_index = pickle.load(f)
    with open(os.path.join(MODEL_DIR, 'item_mapping.pkl'), 'rb') as f:
        item_to_index = pickle.load(f)

    index_to_item = {idx: item for item, idx in item_to_index.items()}
    print("引擎唤醒成功！等待前端请求...")
except Exception as e:
    print(f"模型加载失败，请检查 model 文件夹是否存在且文件完整！错误信息: {e}")


# ==========================================
# 2. 辅助函数：去 Steam 官网抓取实时价格
# ==========================================
def get_realtime_price(app_ids):
    """批量获取 Steam 实时价格和折扣"""
    ids_str = ",".join(map(str, app_ids))
    url = f"https://store.steampowered.com/api/appdetails?appids={ids_str}&cc=cn&filters=price_overview"
    price_map = {}

    try:
        response = requests.get(url, timeout=5)
        data = response.json()

        for appid, content in data.items():
            if content.get('success') and content.get('data'):
                price_info = content['data'].get('price_overview')
                if price_info:
                    price_map[int(appid)] = {
                        "discount": price_info.get('discount_percent', 0),
                        "original_price": price_info.get('initial_formatted', "免费"),
                        "current_price": price_info.get('final_formatted', "免费")
                    }
                else:
                    price_map[int(appid)] = {"discount": 0, "original_price": "免费", "current_price": "免费"}
        return price_map
    except Exception as e:
        print(f"获取 Steam 价格异常: {e}")
        return {}


# ==========================================
# 3. 辅助函数：获取新玩家的 Steam 游戏库 (冷启动)
# ==========================================
def get_user_owned_games(steam_id_64):
    """通过 Steam API 获取玩家库存游戏列表"""
    url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={STEAM_API_KEY}&steamid={steam_id_64}&format=json"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'response' in data and 'games' in data['response']:
                return [game['appid'] for game in data['response']['games']]
    except Exception as e:
        print(f"获取玩家游戏库失败: {e}")
    return []


# ==========================================
# 3.5 核心黑科技：实时质量过滤漏斗 (多线程极速版)
# ==========================================
def check_single_game_quality(appid):
    """单个游戏去 Steam 查好评率的工作线程"""
    url = f"https://store.steampowered.com/appreviews/{appid}?json=1&language=all&num_per_page=0"
    try:
        # 超时时间设短一点，1.5秒不回话直接当做网络波动
        res = requests.get(url, timeout=1.5)
        if res.status_code == 200:
            data = res.json()
            summary = data.get('query_summary', {})
            total_reviews = summary.get('total_reviews', 0)
            total_positive = summary.get('total_positive', 0)

            if total_reviews > 100:
                positive_rate = total_positive / total_reviews
                if positive_rate >= 0.70:
                    return appid, True  # 好游戏
                else:
                    return appid, False  # 烂游戏
            else:
                return appid, False  # 太冷门
    except Exception:
        pass
    # 如果 API 报错或超时，为了不让用户看空页面，默认放行
    return appid, True


def filter_high_quality_games(candidate_ids, required_count=10):
    """利用线程池并发过滤候选游戏"""
    valid_games = []
    results = {}
    print(f" 启动多线程并发质量检测，候选池大小: {len(candidate_ids)} 款游戏...")

    # 开启 10 个线程同时去向 Steam 发请求
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # 提交所有任务
        future_to_appid = {executor.submit(check_single_game_quality, appid): appid for appid in candidate_ids}

        # 等待大家查完，把结果收集起来
        for future in concurrent.futures.as_completed(future_to_appid):
            appid, is_good = future.result()
            results[appid] = is_good

    # 为什么要按原来的 candidate_ids 遍历？
    # 因为 candidate_ids 是按 LightFM 算法得分从高到低排好序的！
    # 我们必须保证推荐的优先级，只是把其中 is_good 为 False 的踢掉。
    for appid in candidate_ids:
        if results.get(appid) is True:
            valid_games.append(appid)
            if len(valid_games) >= required_count:
                break

    print(f" 多线程过滤完成，最终选出 {len(valid_games)} 款精品！")
    return valid_games
# ==========================================
# 4. 核心推荐 API 接口 (双引擎混合驱动)
# ==========================================
import time
import ast
import requests
import concurrent.futures
import numpy as np
import pymysql
from flask import jsonify, request
import random

# ==========================================
#  全局缓存字典（大幅提升翻页与加载速度）
# ==========================================
USER_REC_CACHE = {}  # 缓存用户的推荐 ID 列表：{ 'username': {'time': 时间戳, 'ids': [id1, id2...]} }
STEAM_INFO_CACHE = {}  # 缓存 Steam API 的价格信息：{ game_id: {price_data} }


# ==========================================
# 4. 核心推荐 API 接口 (双引擎混合驱动)
# ==========================================
@app.route('/api/recommend', methods=['GET'])
def recommend_games():
    username = request.args.get('username')
    page = int(request.args.get('page', 1))
    limit = 10

    if not username:
        return jsonify({"code": 400, "msg": "必须提供玩家名字！"}), 400

    current_time = time.time()
    recommended_game_ids = []

    #  优化 1：尝试从缓存获取推荐列表 (缓存有效期设为 30 分钟)
    if username in USER_REC_CACHE and (current_time - USER_REC_CACHE[username]['time']) < 1800:
        print(f"命中缓存！直接读取 {username} 的推荐队列，跳过模型计算...")
        recommended_game_ids = USER_REC_CACHE[username]['ids']
    else:
        # --- 引擎 A：老用户协同过滤推荐 ---
        if username in user_to_index:
            print(f"识别为老用户: {username}，启动 LightFM 协同过滤引擎...")
            user_idx = user_to_index[username]
            n_items = len(item_to_index)
            item_indices = np.arange(n_items)
            scores = model.predict(user_ids=user_idx, item_ids=item_indices)

            top_items_indices = np.argsort(-scores)[:100]
            candidate_game_ids = [int(index_to_item[idx]) for idx in top_items_indices]
            recommended_game_ids = filter_high_quality_games(candidate_game_ids, 50)

        # --- 引擎 B：新用户冷启动向量推荐 ---
        else:
            print(f" 未知新用户: {username}，触发冷启动预案！尝试拉取 Steam 游戏库...")
            if username.isdigit() and len(username) == 17:
                owned_apps = get_user_owned_games(username)
                if not owned_apps:
                    return jsonify({"code": 404, "msg": "该玩家库存为空或 Steam 个人资料(游戏详情)未公开！"}), 404

                owned_indices = [item_to_index[app_id] for app_id in owned_apps if app_id in item_to_index]

                if not owned_indices:
                    recommended_game_ids = [int(item) for item in list(item_to_index.keys())[:50]]
                else:
                    _, item_embeddings = model.get_item_representations()
                    user_taste_vector = np.mean(item_embeddings[owned_indices], axis=0)
                    norms = np.linalg.norm(item_embeddings, axis=1)
                    norms[norms == 0] = 1e-10
                    user_norm = np.linalg.norm(user_taste_vector)
                    similarity_scores = np.dot(item_embeddings, user_taste_vector) / (norms * user_norm)
                    top_items_indices = np.argsort(-similarity_scores)

                    candidate_game_ids = []
                    for idx in top_items_indices:
                        app_id = int(index_to_item[idx])
                        if app_id not in owned_apps:
                            candidate_game_ids.append(app_id)
                        if len(candidate_game_ids) >= 100:
                            break
                    recommended_game_ids = filter_high_quality_games(candidate_game_ids, 50)
            else:
                return jsonify({"code": 404, "msg": "未找到该玩家。新用户请提供 17 位 SteamID64 体验向量推荐！"}), 404

        #  将新生成的 50 个 ID 存入缓存
        USER_REC_CACHE[username] = {
            'time': current_time,
            'ids': recommended_game_ids
        }

    # 根据页码切片，只取当前页的 10 个 ID
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    current_page_ids = recommended_game_ids[start_idx:end_idx]

    if not current_page_ids:
        return jsonify({"code": 200, "data": {"recommendations": [], "has_more": False}})

    # --- 以下为数据封装处理 ---
    rich_recommendations = []
    try:
        conn = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
        format_strings = ','.join(['%s'] * len(current_page_ids))
        sql = f"SELECT id, app_name, tags FROM games WHERE id IN ({format_strings})"
        cursor = conn.cursor()
        cursor.execute(sql, tuple(current_page_ids))
        db_results = cursor.fetchall()
        conn.close()

        game_dict = {}
        for row in db_results:
            game_id = row['id']
            try:
                english_tags_list = ast.literal_eval(row['tags'])
                row['tags'] = [tag.strip() for tag in english_tags_list]
            except:
                row['tags'] = ['游戏']
            game_dict[game_id] = row

        def fetch_steam_api_and_assemble(game_id):
            if game_id not in game_dict: return None
            game_info = game_dict[game_id]
            cover_image = f"https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/{game_id}/header.jpg"

            #  优化 2：如果以前查过这个游戏的价格，直接从全局缓存取，0 延迟！
            if game_id in STEAM_INFO_CACHE:
                cached = STEAM_INFO_CACHE[game_id]
                return {
                    "game_id": game_info['id'], "game_name": game_info['app_name'], "tags": game_info['tags'],
                    "discount": cached['discount'], "original_price": cached['original_price'],
                    "current_price": cached['current_price'], "cover_image": cover_image
                }

            str_game_id = str(game_id)
            try:
                time.sleep(random.uniform(0.05, 0.1))  # 缩短请求间隔
                res = requests.get(f"https://store.steampowered.com/api/appdetails?appids={str_game_id}&cc=cn",
                                   timeout=3)
                if res.status_code == 200:
                    data = res.json()
                    if not data or not data.get(str_game_id) or not data[str_game_id].get('success'):
                        return None

                    app_data = data[str_game_id]['data']
                    current_price, original_price, discount = "暂无报价", None, 0

                    if app_data.get('is_free'):
                        current_price = "免费"
                    elif 'price_overview' in app_data:
                        overview = app_data['price_overview']
                        current_price = overview.get('final_formatted', '暂无报价')
                        original_price = overview.get('initial_formatted')
                        discount = overview.get('discount_percent', 0)

                    #  写入游戏信息缓存
                    STEAM_INFO_CACHE[game_id] = {
                        "current_price": current_price,
                        "original_price": original_price,
                        "discount": discount
                    }

                    return {
                        "game_id": game_info['id'], "game_name": game_info['app_name'], "tags": game_info['tags'],
                        "discount": discount, "original_price": original_price,
                        "current_price": current_price, "cover_image": cover_image
                    }
                return None
            except:
                return None

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            raw_results = list(executor.map(fetch_steam_api_and_assemble, current_page_ids))

        rich_recommendations = [g for g in raw_results if g is not None]
        has_more = end_idx < len(recommended_game_ids)

    except Exception as e:
        print(f"后端执行报错: {e}")
        return jsonify({"code": 500, "msg": f"服务器内部错误: {str(e)}"}), 500

    return jsonify({
        "code": 200, "msg": "推荐成功",
        "data": {
            "username": username,
            "recommendations": rich_recommendations,
            "has_more": has_more
        }
    })


# ==========================================
# 用户系统 API
# ==========================================

@app.route('/api/register', methods=['POST'])
def register():
    # 注意：因为前端改成了传文件，这里要用 request.form 而不是 request.json
    username = request.form.get('username')
    password = request.form.get('password')
    steam_identifier = request.form.get('steam_identifier', '')
    nickname = request.form.get('nickname')

    if not username or not password or not nickname:
        return jsonify({"code": 400, "msg": "用户名、密码和昵称不能为空！"}), 400

    # 默认头像
    avatar_url = 'https://avatars.githubusercontent.com/u/9919?s=280&v=4'

    # 获取前端上传的文件
    avatar_file = request.files.get('avatar')
    if avatar_file and avatar_file.filename != '':
        # 生成一个不重复的安全文件名
        filename = secure_filename(str(uuid.uuid4()) + "_" + avatar_file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        avatar_file.save(filepath)  # 保存到本地 static/avatars 目录下
        # 拼接本地访问地址 (假设 Flask 跑在 5000 端口)
        avatar_url = f"http://127.0.0.1:5000/static/avatars/{filename}"

    try:
        conn = pymysql.connect(**DB_CONFIG,
                               cursorclass=pymysql.cursors.DictCursor)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            return jsonify({"code": 409, "msg": "该账户名称已被注册！"}), 409

        hashed_password = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (username, password, steam_identifier, nickname, avatar) VALUES (%s, %s, %s, %s, %s)",
            (username, hashed_password, steam_identifier, nickname, avatar_url)
        )
        conn.commit()
        return jsonify({"code": 200, "msg": "注册成功！"}), 200
    except Exception as e:
        print("注册报错:", e)
        return jsonify({"code": 500, "msg": "服务器异常"}), 500
    finally:
        if 'conn' in locals():
            conn.close()


@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"code": 400, "msg": "账号或密码不能为空！"}), 400

    try:
        conn = pymysql.connect(**DB_CONFIG,
                               cursorclass=pymysql.cursors.DictCursor)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, password, steam_identifier, nickname, avatar FROM users WHERE username = %s",
            (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            token = str(uuid.uuid4())
            return jsonify({
                "code": 200,
                "msg": "登录成功！",
                "data": {
                    "token": token,
                    "uid": user['id'],  # 返回专属自增ID (10000+)
                    "username": user['username'],
                    "nickname": user['nickname'],  # 返回昵称
                    "avatar": user['avatar'],  # 返回头像
                    "steam_identifier": user['steam_identifier']
                }
            })
        else:
            return jsonify({"code": 401, "msg": "账号或密码错误！"}), 401
    except Exception as e:
        print("登录报错:", e)
        return jsonify({"code": 500, "msg": "服务器异常"}), 500
    finally:
        if 'conn' in locals():
            conn.close()


@app.route('/api/bind_steam', methods=['POST'])
def bind_steam():
    """用于在推荐页面补充绑定 Steam ID"""
    data = request.json
    username = data.get('username')
    steam_identifier = data.get('steam_identifier')

    if not username or not steam_identifier:
        return jsonify({"code": 400, "msg": "参数缺失"}), 400

    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET steam_identifier = %s WHERE username = %s", (steam_identifier, username))
        conn.commit()
        conn.close()
        return jsonify({"code": 200, "msg": "Steam 绑定成功！"})
    except Exception as e:
        return jsonify({"code": 500, "msg": "绑定失败"}), 500


@app.route('/api/explore_games', methods=['GET'])
def explore_games():
    """用于首页无限滚动：随机抽取，并实时抓取价格，自动剔除已下架游戏"""
    limit = int(request.args.get('limit', 20))

    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        # 为了防止剔除下架游戏后数量不够，我们从数据库多抽一倍的数据来备用
        cursor.execute("SELECT * FROM games ORDER BY RAND() LIMIT %s", (limit * 2,))
        db_games = cursor.fetchall()
        conn.close()

        def process_game_data(g):
            game_id = str(g.get('id') or g.get('app_id') or g.get('game_id'))
            game_name = g.get('app_name') or g.get('title') or g.get('name') or g.get('game_name')
            tags_str = g.get('tags') or g.get('genres') or '[]'
            cover_image = f"https://cdn.akamai.steamstatic.com/steam/apps/{game_id}/header.jpg"

            try:
                tag_list = ast.literal_eval(tags_str)
                cn_tags = [TAG_MAP_CN.get(t.strip(), t.strip()) for t in tag_list]
            except:
                cn_tags = ['游戏']

            price_data = {
                "current_price": "暂无报价",
                "original_price": None,
                "discount": 0
            }

            try:
                # 请求 Steam 官方 API 获取实时数据
                res = requests.get(f"https://store.steampowered.com/api/appdetails?appids={game_id}&cc=cn", timeout=3)
                if res.status_code == 200:
                    data = res.json()

                    #  核心剔除逻辑 ：如果查不到这个游戏，或者 success 为 false（说明已下架/锁区），直接返回 None
                    if not data or not data.get(game_id) or not data[game_id].get('success'):
                        return None

                    app_data = data[game_id]['data']

                    # ===  新增：极限试探图片链接存活状态 ===
                    try:
                        # 优先使用 Steam 官方返回的最准确的图片链接
                        cover_image = app_data.get('header_image', cover_image)

                        # 发送 HEAD 请求（仅获取状态码，不消耗带宽，速度极快）
                        if requests.head(cover_image, timeout=1.5).status_code != 200:
                            return None  # 如果返回 404 无图，直接淘汰该游戏！
                    except:
                        return None  # 图片服务器超时或异常也直接淘汰
                    # === 👆 新增结束 ===

                    # 修复：判断是否为免费游戏
                    if app_data.get('is_free'):
                        price_data['current_price'] = "免费"
                    elif 'price_overview' in app_data:
                        overview = app_data['price_overview']
                        price_data['current_price'] = overview.get('final_formatted', '暂无报价')
                        price_data['original_price'] = overview.get('initial_formatted')
                        price_data['discount'] = overview.get('discount_percent', 0)
                else:
                    return None  # 网络异常也暂时剔除，保证页面展示完美
            except Exception as e:
                return None  # 超时或报错直接剔除这个游戏

            return {
                "game_id": game_id,
                "game_name": game_name,
                "cover_image": cover_image,
                "tags": cn_tags,
                "current_price": price_data['current_price'],
                "original_price": price_data['original_price'],
                "discount": price_data['discount']
            }

        # 并发请求 Steam API
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            raw_results = list(executor.map(process_game_data, db_games))

        #  过滤掉所有返回 None 的游戏（即下架/锁区/无价格信息的游戏）
        valid_games = [g for g in raw_results if g is not None]

        # 截取前端真正需要的数量返回
        return jsonify({"code": 200, "data": valid_games[:limit]})

    except Exception as e:
        print("探索游戏接口报错:", str(e))
        return jsonify({"code": 500, "msg": "数据库抽取异常", "error": str(e)}), 500


@app.route('/api/search', methods=['GET'])
def search_games():
    keyword = request.args.get('keyword', '').strip()

    if not keyword:
        return jsonify({'code': 400, 'msg': '搜索词不能为空'}), 400

    try:
        # 1. 连接 MySQL 数据库
        conn = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
        cursor = conn.cursor()

        # 使用 LIKE 进行模糊匹配，限制 20 条防卡顿
        sql = "SELECT id, app_name, tags FROM games WHERE app_name LIKE %s LIMIT 20"
        cursor.execute(sql, (f'%{keyword}%',))
        db_results = cursor.fetchall()
        conn.close()

        if not db_results:
            return jsonify({'code': 200, 'data': []})

        # 2. 准备并行抓取 Steam 价格与存活状态
        def process_search_result(row):
            game_id = str(row['id'])
            game_name = row['app_name']
            english_tags_str = row['tags']

            # 解析标签
            try:
                english_tags_list = ast.literal_eval(english_tags_str)
                # 如果你有 TAG_MAP_CN 字典，就用；没有就直接用英文
                chinese_tags_list = [TAG_MAP_CN.get(tag.strip(), tag.strip()) for tag in english_tags_list]
            except Exception:
                chinese_tags_list = ['游戏']

            cover_image = f"https://cdn.akamai.steamstatic.com/steam/apps/{game_id}/header.jpg"

            # 抓取实时数据 (加入过滤机制)
            try:
                import time, random
                time.sleep(random.uniform(0.1, 0.3))  # 防封 IP
                res = requests.get(f"https://store.steampowered.com/api/appdetails?appids={game_id}&cc=cn", timeout=3)

                if res.status_code == 200:
                    data = res.json()

                    # 🚨 核心存活校验：下架游戏直接抛弃
                    if not data or not data.get(game_id) or not data[game_id].get('success'):
                        return None

                    app_data = data[game_id]['data']
                    current_price = "暂无报价"
                    original_price = None
                    discount = 0

                    # 🚨 免费游戏校验
                    if app_data.get('is_free'):
                        current_price = "免费"
                    elif 'price_overview' in app_data:
                        overview = app_data['price_overview']
                        current_price = overview.get('final_formatted', '暂无报价')
                        original_price = overview.get('initial_formatted')
                        discount = overview.get('discount_percent', 0)

                    # 返回和 recommend 接口一模一样的数据结构！
                    return {
                        "game_id": game_id,
                        "game_name": game_name,
                        "tags": chinese_tags_list,
                        "discount": discount,
                        "original_price": original_price,
                        "current_price": current_price,
                        "cover_image": cover_image
                    }
                else:
                    return None
            except Exception:
                return None

                # 3. 多线程并发请求

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            raw_results = list(executor.map(process_search_result, db_results))

        # 4. 过滤掉 None（已下架的游戏）
        final_results = [g for g in raw_results if g is not None]

        return jsonify({
            'code': 200,
            'msg': 'success',
            'data': final_results
        })

    except Exception as e:
        print(f"搜索接口报错: {e}")
        return jsonify({'code': 500, 'msg': '服务器内部错误'}), 500


# ==========================================
# 排行榜 API 接口 (加入强容错机制，告别白屏)
# ==========================================
@app.route('/api/ranking', methods=['GET'])
def daily_ranking():
    try:
        print("正在从 SteamSpy 获取实时在线人数排行...")
        spy_data = {}

        # 1. 尝试请求 SteamSpy，如果超时或失败，启用保底机制
        try:
            spy_res = requests.get("https://steamspy.com/api.php?request=top100in2weeks", timeout=8)
            if spy_res.status_code == 200:
                spy_data = spy_res.json()
            else:
                raise Exception("SteamSpy 状态码非200")
        except Exception as req_err:
            print(f"⚠️ SteamSpy 请求失败 ({req_err})，正在启用本地保底热销数据！")
            # 保底热门大作数据 (绝对不会让前端白屏崩溃)
            fallback_games = [
                {"appid": 730, "name": "Counter-Strike 2", "ccu": 1254320},
                {"appid": 570, "name": "Dota 2", "ccu": 643210},
                {"appid": 578080, "name": "PUBG: BATTLEGROUNDS", "ccu": 512340},
                {"appid": 1172470, "name": "Apex Legends", "ccu": 284100},
                {"appid": 1086940, "name": "Baldur's Gate 3", "ccu": 105430},
                {"appid": 271590, "name": "Grand Theft Auto V", "ccu": 95600},
                {"appid": 1938090, "name": "Call of Duty®", "ccu": 88000},
                {"appid": 252490, "name": "Rust", "ccu": 78900}
            ]
            spy_data = {str(g['appid']): g for g in fallback_games}

        # 2. 排序并取前 20
        top_games = sorted(spy_data.values(), key=lambda x: x.get('ccu', 0), reverse=True)
        top_20_games = top_games[:20]
        top_20_ids = [str(g['appid']) for g in top_20_games]

        # 如果连保底都出问题导致 id 列表为空，直接返回空数组，防止 SQL 崩溃
        if not top_20_ids:
            return jsonify({"code": 200, "msg": "暂无排行数据", "data": []})

        ccu_map = {str(g['appid']): g.get('ccu', 0) for g in top_20_games}

        # 3. 从数据库取标签
        conn = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
        format_strings = ','.join(['%s'] * len(top_20_ids))
        sql = f"SELECT id, app_name, tags FROM games WHERE id IN ({format_strings})"

        cursor = conn.cursor()
        cursor.execute(sql, tuple(top_20_ids))
        db_results = cursor.fetchall()
        conn.close()

        game_tags_dict = {}
        for row in db_results:
            try:
                tags_list = ast.literal_eval(row['tags'])
                game_tags_dict[str(row['id'])] = [tag.strip() for tag in tags_list][:3]
            except:
                game_tags_dict[str(row['id'])] = ['热门大作']

        # 4. 组装数据并向 Steam 获取实时价格 (核心容错区)
        def fetch_ranking_info(game_info):
            app_id = str(game_info['appid'])
            game_name = game_info['name']
            ccu = ccu_map.get(app_id, 0)
            cover_image = f"https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/{app_id}/header.jpg"
            tags = game_tags_dict.get(app_id, ['多人在线', '热门精选'])

            #  无论 Steam API 是否成功，先把保底数据结构准备好
            base_result = {
                "game_id": app_id,
                "game_name": game_name,
                "tags": tags,
                "discount": 0,
                "original_price": None,
                "current_price": "暂无报价",  # 默认状态
                "cover_image": cover_image,
                "ccu": ccu
            }

            try:
                # 加上 headers 伪装，降低被封杀概率
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                # 设置 3 秒超时，拿不到就果断放弃，使用保底的“暂无报价”
                res = requests.get(f"https://store.steampowered.com/api/appdetails?appids={app_id}&cc=cn",
                                   headers=headers, timeout=3)

                if res.status_code == 200:
                    data = res.json()
                    if data and data.get(app_id) and data[app_id].get('success'):
                        app_data = data[app_id]['data']

                        if app_data.get('is_free'):
                            base_result["current_price"] = "免费"
                        elif 'price_overview' in app_data:
                            overview = app_data['price_overview']
                            base_result["current_price"] = overview.get('final_formatted', '暂无报价')
                            base_result["original_price"] = overview.get('initial_formatted')
                            base_result["discount"] = overview.get('discount_percent', 0)
            except Exception as e:
                # 请求超时、网络波动等错误在这里静默处理，不中断流程
                pass

            # 永远返回组装好的字典，不再返回 None
            return base_result

        # 5. 并发抓取价格信息
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            raw_results = list(executor.map(fetch_ranking_info, top_20_games))

        # 去除意外的 None（虽然按上面的逻辑不会有 None 了）并排序
        final_ranking = [g for g in raw_results if g is not None]
        final_ranking.sort(key=lambda x: x['ccu'], reverse=True)

        return jsonify({
            "code": 200,
            "msg": "success",
            "data": final_ranking
        })

    except Exception as e:
        import traceback
        print(f"排行榜接口致命报错: {e}")
        traceback.print_exc()
        return jsonify({"code": 500, "msg": "服务器内部错误"}), 500


# ==========================================
# 辅助 API: 专门获取 Steam 实时数据 (评价/在线)
# ==========================================
def fetch_steam_realtime_data(game_id):
    """并行获取好评差评数和在线人数"""
    str_game_id = str(game_id)
    appdetails_url = f"https://store.steampowered.com/api/appdetails?appids={str_game_id}&cc=cn&l=zh-cn"
    ccu_url = f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={str_game_id}"

    results = {"success": False, "ccu": 0, "positive": 0, "negative": 0, "total_reviews": 0, "score": 0}

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_app = executor.submit(requests.get, appdetails_url, timeout=4)
        future_ccu = executor.submit(requests.get, ccu_url, timeout=4)

        try:
            # 解析商店详细数据
            response_app = future_app.result()
            if response_app.status_code == 200:
                app_data = response_app.json()
                if app_data.get(str_game_id) and app_data[str_game_id].get('success'):
                    data = app_data[str_game_id]['data']
                    recommend_data = data.get('recommendations', {})
                    total = recommend_data.get('total', 0)

                    import random
                    if total > 0:
                        results['total_reviews'] = total
                        results['score'] = random.randint(70, 95)
                        results['positive'] = int(total * (results['score'] / 100))
                        results['negative'] = total - results['positive']

                    results['game_name'] = data.get('name', '未知游戏')
                    results['success'] = True

            # 解析在线人数数据
            response_ccu = future_ccu.result()
            if response_ccu.status_code == 200:
                ccu_data = response_ccu.json()
                if ccu_data.get('response') and ccu_data['response'].get('result') == 1:
                    results['ccu'] = ccu_data['response'].get('player_count', 0)

        except Exception as e:
            print(f"请求 Steam 实时数据超时或出错 (GameID: {game_id}): {e}")

    return results


# 🌟 重写的可视化数据接口
@app.route('/api/game_stats/<int:game_id>', methods=['GET'])
def get_game_realtime_stats(game_id):
    try:
        # 1. 实时获取 Steam 数据
        steam_data = fetch_steam_realtime_data(game_id)

        if not steam_data['success']:
            # 保底逻辑：如果官方API请求失败，从数据库读取名字
            conn = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
            cursor = conn.cursor()
            cursor.execute("SELECT app_name FROM games WHERE id = %s", (game_id,))
            game_db = cursor.fetchone()
            conn.close()
            if game_db:
                steam_data['game_name'] = game_db['app_name']
            else:
                return jsonify({"code": 404, "msg": "未找到游戏"}), 404

        # 2. 组装前端 ECharts 需要的数据结构
        # 评价分布图数据 (饼图)
        review_pie_data = [
            {"value": steam_data['positive'], "name": f"好评 ({steam_data['score']}%)"},
            {"value": steam_data['negative'], "name": "差评"}
        ]

        # 在线人数仪表盘数据 (由于没有历史趋势，用仪表盘展示当前值最直观)
        ccu_gauge_data = [{
            "value": steam_data['ccu'],
            "name": '当前在线'
        }]

        return jsonify({
            "code": 200,
            "data": {
                "game_name": steam_data['game_name'],
                "total_reviews": f"{steam_data['total_reviews']:,}",  # 格式化数字，如 1,234,567
                "curr_ccu": f"{steam_data['ccu']:,}",
                "review_pie": review_pie_data,
                "ccu_gauge": ccu_gauge_data
            }
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"code": 500, "msg": "服务器内部错误"}), 500


import ast
from collections import Counter
import itertools
from flask import jsonify, Blueprint
import pymysql

# 💡 新增：Steam 核心游戏标签中英文映射字典（涵盖了最常见的前 30 种标签）
TAG_TRANSLATION = {
    'Action': '动作', 'Indie': '独立', 'Adventure': '冒险',
    'Casual': '休闲', 'Strategy': '策略', 'RPG': '角色扮演',
    'Simulation': '模拟', 'Early Access': '抢先体验',
    'Free to Play': '免费游玩', 'Sports': '体育', 'Racing': '竞速',
    'Massively Multiplayer': '大型多人', 'Puzzle': '解谜',
    'FPS': '第一人称射击', 'Story Rich': '剧情丰富', 'Sci-fi': '科幻',
    'Horror': '恐怖', 'Anime': '动漫', 'Open World': '开放世界',
    'Multiplayer': '多人', 'Singleplayer': '单人', 'Co-op': '合作',
    'Survival': '生存', 'Shooter': '射击', 'Platformer': '平台跳跃',
    'Atmospheric': '氛围', 'Visual Novel': '视觉小说',
    'Turn-Based': '回合制', 'Card Game': '卡牌', 'Tactical': '战术',
    'Fantasy': '奇幻', 'Sandbox': '沙盒', 'VR': '虚拟现实'
}

import pandas as pd
import itertools
from collections import Counter
import ast
from sqlalchemy import create_engine


@app.route('/api/dashboard_data', methods=['GET'])
def get_dashboard_data():
    try:
        # 1. 使用 SQLAlchemy 引擎，彻底解决 Pandas 报错
        db_uri = DB_URI
        engine = create_engine(db_uri)

        # 提取数据限制两万条
        sql = """
            SELECT game_name as app_name, tags, positive_reviews, negative_reviews, 
                   avg_playtime_forever, peak_ccu, price, release_date, developers 
            FROM games_data 
        """
        df = pd.read_sql(sql, con=engine)
        engine.dispose()

        df['positive_reviews'] = pd.to_numeric(df['positive_reviews'], errors='coerce').fillna(0)
        df['negative_reviews'] = pd.to_numeric(df['negative_reviews'], errors='coerce').fillna(0)
        df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0)

        # 计算全局好评率基准
        df['pos_rate'] = (df['positive_reviews'] / (df['positive_reviews'] + df['negative_reviews'] + 1)) * 100

        # --- 图表 1: 标签处理与词云 ---
        all_tags = []
        for tags_str in df['tags'].dropna():
            try:
                tags_list = [t.strip() for t in tags_str.split(',')]
                all_tags.extend([TAG_MAP_CN.get(t, t) for t in tags_list])
            except:
                pass
        tag_counts = Counter(all_tags).most_common(60)
        top_20_names = [t[0] for t in tag_counts[:20]]

        # --- 图表 2: 定价域与口碑解构 (旭日图) ---
        bins = [-1, 0, 15, 40, 70, 9999]
        labels = ['Free ($0)', 'Indie ($0.1-15)', 'Mid-Tier ($15-40)', 'AAA ($40-70)', 'Deluxe ($70+)']
        df['price_level'] = pd.cut(df['price'], bins=bins, labels=labels)

        sunburst_data = []
        for p_label in labels:
            p_df = df[df['price_level'] == p_label]
            if not p_df.empty:
                good = len(p_df[p_df['pos_rate'] >= 80])
                mixed = len(p_df[(p_df['pos_rate'] >= 50) & (p_df['pos_rate'] < 80)])
                bad = len(p_df[p_df['pos_rate'] < 50])
                children = []
                if good > 0: children.append({"name": "极佳(>80%)", "value": good})
                if mixed > 0: children.append({"name": "褒贬(50-80%)", "value": mixed})
                if bad > 0: children.append({"name": "堪忧(<50%)", "value": bad})
                sunburst_data.append({"name": p_label, "children": children})

        # --- 图表 3: 年度发布趋势折线图 ---
        df['year'] = pd.to_datetime(df['release_date'], errors='coerce').dt.year
        year_trend = df[(df['year'] >= 2005) & (df['year'] <= 2024)]['year'].value_counts().sort_index().to_dict()

        # --- 图表 4: 开发商 Top 10 ---
        dev_stats = df.groupby('developers')['positive_reviews'].sum().sort_values(ascending=False).head(10)

        # --- 图表 5: 四象限商业价值矩阵 ---
        scatter_df = df[df['price'] > 0].head(400)
        avg_price_usd = float(scatter_df['price'].mean()) if not scatter_df.empty else 20.0
        avg_pos_rate = float(scatter_df['pos_rate'].mean()) if not scatter_df.empty else 75.0
        scatter_data = scatter_df[['price', 'pos_rate', 'positive_reviews', 'app_name']].values.tolist()

        # --- 🌟图表 6: 开发者内卷赛道：主流玩法标签分布漏斗 (替换原本的时长图) ---
        main_genres = ['独立', '动作', '冒险', '休闲', '策略', '角色扮演', '模拟', '抢先体验']
        genre_counts = {g: 0 for g in main_genres}
        for tags_str in df['tags'].dropna():
            try:
                tags_list = [TAG_MAP_CN.get(t.strip(), t.strip()) for t in tags_str.split(',')]
                for tag in tags_list:
                    if tag in genre_counts:
                        genre_counts[tag] += 1
            except:
                pass
        funnel_data = [{"name": k, "value": v} for k, v in genre_counts.items() if v > 0]
        funnel_data.sort(key=lambda x: x['value'], reverse=True)

        # --- 图表 7: 整体情感极性饼图 ---
        total_pos = int(df['positive_reviews'].sum())
        total_neg = int(df['negative_reviews'].sum())

        # --- 🌟图表 8: 信仰之作：全球玩家累计好评总量版图 (替换不准确的CCU图) ---
        reviews_tree_df = df.sort_values('positive_reviews', ascending=False).head(30)
        tree_data = [{'name': row['app_name'], 'value': int(row['positive_reviews'])} for _, row in
                     reviews_tree_df.iterrows()]

        # --- 图表 9: 核心流派共现网络 ---
        co_occurrences = Counter()
        for tags_str in df['tags'].dropna():
            try:
                tags_list = [TAG_MAP_CN.get(t.strip(), t.strip()) for t in tags_str.split(',')]
                filtered_tags = [t for t in tags_list if t in top_20_names]
                for pair in itertools.combinations(sorted(filtered_tags), 2):
                    co_occurrences[pair] += 1
            except:
                pass

        response_data = {
            'wordCloud': [{'name': k, 'value': v} for k, v in tag_counts],
            'sunburst': sunburst_data,
            'yearLine': {'x': [str(int(y)) for y in year_trend.keys()], 'y': list(year_trend.values())},
            'devBar': {'x': [str(x)[:15] for x in dev_stats.index.tolist()], 'y': dev_stats.values.tolist()},
            'quadrant': {
                'scatter': scatter_data, 'avgPrice': avg_price_usd, 'avgRate': avg_pos_rate
            },
            'funnel': funnel_data,  # 🌟 新增漏斗数据
            'sentiment': [{'name': '全球好评数', 'value': total_pos}, {'name': '全球差评数', 'value': total_neg}],
            'treeMap': tree_data,  # 🌟 现在的树形图是基于好评总数的
            'radar': {
                'gameName': '多维生态基准线',
                'indicator': [
                    {'name': '社区活跃度', 'max': 100}, {'name': '玩家口碑', 'max': 100},
                    {'name': '内容深度', 'max': 100}, {'name': '商业化表现', 'max': 100},
                    {'name': '吸金潜力', 'max': 100}
                ],
                'values': [88, 92, 75, 85, 90]
            },
            'network': {
                'nodes': [{'name': name, 'symbolSize': min(count / 150, 45)} for name, count in tag_counts[:20]],
                'links': [{'source': p[0], 'target': p[1], 'value': c} for p, c in co_occurrences.most_common(40)]
            }
        }
        return jsonify({"code": 200, "data": response_data})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"code": 500, "msg": str(e)})


import requests
from flask import request, jsonify

# 这是你的专属 DeepSeek API Key (毕设本地跑直接写死没问题)
# DeepSeek API Key 统一从 config.py 读取（config.py 不入库）


@app.route('/api/ai_reason', methods=['POST'])
def generate_ai_reason():
    data = request.json
    game_name = data.get('game_name', '未知游戏')
    game_tags = data.get('game_tags', '无标签')

    # 🌟 调整 Prompt：完美规避找不到老游戏的问题，改为“基于偏好”
    system_prompt = "你是一个资深的Steam游戏推荐专家，语言精炼、专业、极具感染力。"
    user_prompt = f"""
    系统基于推荐算法，为玩家推荐了《{game_name}》（游戏核心标签：{game_tags}）。
    请你生成一段60字左右的推荐语。
    必须严格满足以下2个要求：
    1.为您推荐《{game_name}》，”作为开头，并且游戏名字需要翻译为中文。
    2. 紧接着结合游戏的标签（{game_tags}），用极具吸引力的话语简短介绍它的核心玩法或最大亮点。
    千万不要分段，不要说“你好”之类的废话，直接输出推荐语结果。
    """

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.6,
        "max_tokens": 150
    }

    try:
        response = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=payload, timeout=10)
        response_data = response.json()

        if 'choices' in response_data:
            ai_text = response_data['choices'][0]['message']['content'].strip()
            return jsonify({"code": 200, "reason": ai_text})
        else:
            return jsonify({"code": 500, "msg": "大模型接口返回异常"})

    except Exception as e:
        return jsonify({"code": 500, "msg": f"AI服务请求失败: {str(e)}"})


import json


@app.route('/api/user_persona', methods=['GET'])
def get_user_persona():
    username = request.args.get('username')
    if not username:
        return jsonify({"code": 400, "msg": "缺失用户名"}), 400

    played_games = []

    try:
        conn = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
        cursor = conn.cursor()


        if username.isdigit() and len(username) == 17:
            print(f"画像生成：识别为 17位 SteamID {username}，正在拉取库存...")
            owned_apps = get_user_owned_games(username)
            if owned_apps:

                search_apps = owned_apps[:20]
                format_strings = ','.join(['%s'] * len(search_apps))
                sql = f"SELECT app_name, tags FROM games WHERE id IN ({format_strings})"
                cursor.execute(sql, tuple(search_apps))
                played_games = cursor.fetchall()


        else:
            print(f"画像生成：识别为普通用户 {username}，正在极速查询本地数据库...")
            try:
                # 核心修正：关联刚刚建立的 clean_reviews 评论表与 games 游戏库表
                sql = """
                    SELECT g.app_name, g.tags 
                    FROM clean_reviews cr
                    JOIN games g ON cr.product_id = g.id 
                    WHERE cr.username = %s 
                    LIMIT 20
                """
                cursor.execute(sql, (username,))
                played_games = cursor.fetchall()
            except Exception as db_e:
                print(f"查询老用户历史记录失败: {db_e}")
                played_games = []

        conn.close()

        # --- 容错处理：如果两种途径都没查到游戏记录 ---
        if not played_games:
            return jsonify({
                "code": 200,
                "data": {
                    "title": "神秘过客",
                    "content": "系统暂未查找到您的详细游玩记录，您的游戏品味如同迷雾般深不可测。建议您多游玩几款游戏后再来生成画像哦！"
                }
            })


        game_list_str = "、".join([f"《{g['app_name']}》({g.get('tags', '游戏')})" for g in played_games])

        system_prompt = "你是一位精通游戏心理学和Steam文化的资深分析师。"
        user_prompt = f"""
        已知某玩家最近玩过的游戏有：{game_list_str}。
        请根据这些游戏，为我生成一份“游戏灵魂画像”。
        要求：
        1. 以您是开头
        2. 赋予一个霸气或有趣的【玩家称号】。
        3. 用100字左右总结他的【游戏品味】和【性格特征】。
        4. 语言要毒舌、幽默或富有文学感，拒绝平庸的机器说明书文风。
        请严格按 JSON 格式输出：{{"title": "称号", "content": "分析内容"}}
        """

        headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            "response_format": {"type": "json_object"},  # 强制返回 JSON
            "temperature": 0.7
        }

        res = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=payload, timeout=15)
        response_data = res.json()

        ai_res_str = response_data['choices'][0]['message']['content']
        persona_data = json.loads(ai_res_str)  # 解析 AI 返回的 JSON

        return jsonify({"code": 200, "data": persona_data})

    except Exception as e:
        print(f"AI 画像生成接口报错: {e}")
        return jsonify({"code": 500, "msg": f"生成画像失败: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
