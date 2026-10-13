# Steam_RecSys 前端（steam-frontend）

基于 **Vue 3 + Vite** 构建的单页应用，负责推荐系统的全部可视化交互。

## 技术栈

| 分类 | 选型 |
| --- | --- |
| 框架 | Vue 3 |
| 构建 | Vite 8 |
| 路由 | vue-router 4（含登录路由守卫） |
| UI | Bootstrap 5 |
| 图表 | ECharts 5 + echarts-wordcloud |
| 请求 | axios |

## 快速开始

```bash
cd steam-frontend
npm install        # 或 pnpm install / yarn
npm run dev        # 开发模式，默认 http://localhost:5173
npm run build      # 生产构建，产物在 dist/
npm run preview    # 预览生产构建
```

> 后端默认运行在 `http://127.0.0.1:5000`，前端各页面中的接口地址目前为**硬编码**。
> 若后端不在本机或改了端口，请全局搜索 `127.0.0.1:5000` 统一替换
> （建议后续抽成 `.env` 中的 `VITE_API_BASE`）。

## 目录结构

```
steam-frontend/
├── index.html              # 单页入口
├── vite.config.js          # Vite 配置
├── public/                 # 静态资源（favicon.svg）
└── src/
    ├── main.js             # 应用入口，注册路由与 Bootstrap
    ├── App.vue             # 全局布局 / 导航栏
    ├── style.css           # 全局样式（Steam 深色主题）
    ├── router/index.js     # 路由表 + requiresAuth 全局守卫
    ├── assets/             # 图片资源
    └── views/
        ├── Home.vue         # 首页：轮播精选 + 无限滚动探索
        ├── Login.vue        # 登录
        ├── Register.vue     # 注册（含头像上传）
        ├── Recommend.vue    # 个性化推荐 + 绑定 Steam + AI 推荐语
        ├── Search.vue       # 游戏搜索
        ├── Ranking.vue      # SteamSpy 热玩榜
        ├── Dashboard.vue    # 数据可视化大屏（8 张 ECharts 图表）
        ├── UserPersona.vue  # AI 玩家灵魂画像
        └── Unauthorized.vue # 未登录拦截页
```

## 页面与后端接口对应关系

| 页面 | 调用接口 |
| --- | --- |
| Home | `GET /api/explore_games`、`GET /api/game_stats/<id>` |
| Login / Register | `POST /api/login`、`POST /api/register` |
| Recommend | `GET /api/recommend`、`POST /api/bind_steam`、`POST /api/ai_reason` |
| Search | `GET /api/search` |
| Ranking | `GET /api/ranking` |
| Dashboard | `GET /api/dashboard_data` |
| UserPersona | `GET /api/user_persona` |

完整接口说明见仓库根目录 README 的「API 接口文档」章节。

## 登录态说明

登录成功后后端返回 `token` 与用户信息，前端将 `username` 写入 `localStorage`；
路由守卫 `router.beforeEach` 依据 `meta.requiresAuth` 判断是否放行到 `/unauthorized`。
