<template>
  <div id="app">
    <header class="global-header">
      <div class="header-content">

        <div class="header-left">
          <div class="logo">
            <h1>STEAM 混合推荐系统</h1>
          </div>
          <nav class="main-nav">
            <router-link to="/">系统主页</router-link>
            <router-link to="/recommend">专属推荐</router-link>
            <router-link to="/ranking" class="nav-link">实时排行</router-link>
            <router-link to="/dashboard" class="nav-link data-v-link">数据大屏</router-link>

            <router-link to="/persona" class="nav-link">专属画像</router-link>

          </nav>
        </div>

        <div class="header-right">
          <div class="search-container">
            <input
              type="text"
              v-model="searchQuery"
              @keyup.enter="handleSearch"
              placeholder="搜索游戏..."
              class="search-input"
            />
            <button @click="handleSearch" class="search-submit-btn">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"/>
              </svg>
            </button>
          </div>

          <div class="user-actions">
            <template v-if="isLoggedIn">
              <div class="user-profile">
                <img :src="avatar" alt="avatar" class="user-avatar" />
                <div class="user-info">
                  <span class="user-nickname">{{ nickname }}</span>
                  <span class="user-uid">UID: {{ uid }}</span>
                </div>
                <button @click="handleLogout" class="logout-btn">退出</button>
              </div>
            </template>
            <template v-else>
              <router-link to="/login" class="login-btn">登录</router-link>
            </template>
          </div>
        </div>

      </div>
    </header>

    <main class="main-content">
      <router-view :key="$route.fullPath"></router-view>
    </main>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      isLoggedIn: false,
      nickname: '',
      avatar: '',
      uid: '',
      searchQuery: '' // 🌟 新增：绑定搜索框输入的内容
    }
  },
  methods: {
    checkAuth() {
      const token = localStorage.getItem('token');
      if (token) {
        this.isLoggedIn = true;
        this.nickname = localStorage.getItem('nickname') || '玩家';
        this.avatar = localStorage.getItem('avatar') || '';
        this.uid = localStorage.getItem('uid') || '';
      } else {
        this.isLoggedIn = false;
      }
    },
    handleLogout() {
      localStorage.clear();
      // 清除推荐和探索页面的缓存
      sessionStorage.removeItem('recommend_games_cache');
      sessionStorage.removeItem('explore_games_cache');
      this.checkAuth();
      if (this.$route.path !== '/') {
        this.$router.push('/');
      }
    },
    // 🌟 新增：处理搜索事件
    handleSearch() {
      const query = this.searchQuery.trim();
      if (query) {
        // 跳转到搜索结果页面，并将搜索词作为 URL 参数传递
        // 例如：会跳转到 /search?keyword=赛博朋克
        this.$router.push({ path: '/search', query: { keyword: query } });

        // 搜索后可以不清空，方便用户修改搜索词，或者如果你想清空可以取消注释下面这行：
        // this.searchQuery = '';
      }
    }
  },
  mounted() {
    this.checkAuth();
    window.addEventListener('auth-change', this.checkAuth);
  },
  beforeUnmount() {
    window.removeEventListener('auth-change', this.checkAuth);
  }
}
</script>


<style>
/* ================= 全局头部样式 ================= */
.global-header {
  background-color: #171a21; /* Steam经典深邃黑底色 */
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.4); /* 增加底部阴影，更有层次感 */
  position: sticky;
  top: 0;
  z-index: 1000;
  height: 76px; /* 固定高度，大气一点 */
}

.header-content {
  max-width: 1400px; /* 限制最大宽度，宽屏下也不会太散 */
  margin: 0 auto;
  height: 100%;
  padding: 0 30px;
  display: flex;
  justify-content: space-between; /* 核心：把左右两侧推到两端 */
  align-items: center;
}

/* 🌟 左侧布局 */
.header-left {
  display: flex;
  align-items: center;
  gap: 50px; /* Logo和导航菜单拉开 50px 的距离 */
}

.logo h1 {
  margin: 0;
  font-size: 24px;
  color: #c6d4df;
  letter-spacing: 1px;
  white-space: nowrap; /* 绝对不换行 */
}

.main-nav {
  display: flex;
  gap: 30px; /* 菜单项之间的距离，以后再加3-4个页面都毫无压力 */
}

.main-nav a {
  color: #b8b6b4;
  text-decoration: none;
  font-size: 16px;
  font-weight: bold;
  letter-spacing: 1px;
  transition: color 0.3s;
  white-space: nowrap;
}

.main-nav a:hover,
.main-nav a.router-link-active {
  color: #ffffff; /* 选中或悬停变成亮白 */
}

/* 🌟 右侧布局 */
.header-right {
  display: flex;
  align-items: center;
  gap: 40px; /* 搜索框和用户头像拉开 40px 距离 */
}

/* 搜索框 */
.search-container {
  display: flex;
  align-items: center;
  background-color: #316282;
  border-radius: 3px;
  padding: 3px;
  width: 280px; /* 给搜索框一个固定宽度，不乱缩放 */
  box-shadow: 0 0 5px rgba(0,0,0,0.3) inset;
}

.search-input {
  flex: 1;
  background: transparent;
  border: none;
  color: #fff;
  padding: 6px 12px;
  font-size: 14px;
  outline: none;
}

.search-input::placeholder {
  color: #17202b;
  font-style: italic;
  font-weight: bold;
  opacity: 0.6;
}

.search-submit-btn {
  background-color: #66c0f4;
  border: none;
  border-radius: 2px;
  color: #1b2838;
  width: 32px;
  height: 30px;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  transition: all 0.2s;
}

.search-submit-btn:hover {
  background-color: #ffffff;
}

/* 用户操作区保持圆润质感 */
.user-profile {
  display: flex;
  align-items: center;
  gap: 15px;
  background: rgba(0, 0, 0, 0.25); /* 稍微给点底色框住头像 */
  padding: 6px 15px 6px 6px;
  border-radius: 30px; /* 大圆角 */
  border: 1px solid rgba(255,255,255,0.1);
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 2px solid #66c0f4; /* 加上Steam标志性的蓝边框 */
}

.user-info {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.user-nickname {
  color: #fff;
  font-size: 14px;
  font-weight: bold;
}

.user-uid {
  color: #8f98a0;
  font-size: 12px;
}

.logout-btn {
  background: transparent;
  color: #8f98a0;
  border: 1px solid #8f98a0;
  border-radius: 3px;
  padding: 4px 10px;
  cursor: pointer;
  margin-left: 10px;
  transition: all 0.3s;
}

.logout-btn:hover {
  color: #fff;
  border-color: #fff;
}
.login-btn {
  background: transparent;
  color: #8f98a0;
  border: 1px solid #8f98a0;
  border-radius: 3px;
  padding: 4px 10px;
  cursor: pointer;
  margin-left: 10px;
  transition: all 0.3s;
}

.login-btn:hover {
  color: #fff;
  border-color: #fff;
}
/* ================= 🌟 响应式布局适配 (媒体查询) ================= */

/* 1. 当屏幕宽度小于 1100px 时（如小尺寸笔记本） */
@media (max-width: 1100px) {
  .header-left { gap: 20px; }       /* 缩小 Logo 和导航的间距 */
  .header-right { gap: 20px; }      /* 缩小搜索框和头像的间距 */
  .main-nav { gap: 15px; }          /* 缩小导航菜单项的间距 */
  .search-container { width: 200px; } /* 稍微缩小搜索框 */
  .logo h1 { font-size: 20px; }     /* 稍微缩小 Logo 字体 */
}

/* 2. 当屏幕宽度小于 850px 时（如平板竖屏） */
@media (max-width: 850px) {
  .header-content { padding: 0 15px; }
  .search-container { width: 140px; } /* 进一步缩小搜索框 */
  .main-nav a { font-size: 14px; }    /* 缩小导航字体 */

  /* 空间不够了，隐藏用户昵称和 UID，只保留头像和退出按钮 */
  .user-nickname, .user-uid { display: none; }
  .user-profile {
    padding: 4px;
    border-radius: 50%; /* 让头像框变回圆形 */
    gap: 8px;
  }
}

/* 3. 当屏幕宽度小于 650px 时（如手机端极窄屏） */
@media (max-width: 650px) {
  .global-header {
    height: auto;
    padding: 15px 0;
  }
  .header-content {
    flex-direction: column; /* 核心：将左右布局改为上下排布 */
    gap: 15px;
  }
  .header-left {
    width: 100%;
    justify-content: space-between; /* Logo和导航两端对齐 */
    flex-direction: column;
    gap: 15px;
  }
  .header-right {
    width: 100%;
    justify-content: space-between;
  }
  .search-container { width: 60%; } /* 搜索框占一半多 */

  /* 让导航栏在极窄屏幕下允许横向滑动，防止折行太丑 */
  .main-nav {
    width: 100%;
    overflow-x: auto;
    padding-bottom: 5px;
    justify-content: center;
  }
  /* 隐藏滑动的滚动条，更美观 */
  .main-nav::-webkit-scrollbar { display: none; }
}
</style>