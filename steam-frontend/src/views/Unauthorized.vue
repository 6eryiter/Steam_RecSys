<template>
  <div class="unauthorized-page">
    <div class="unauthorized-card">
      <div class="icon-wrapper">
        <svg xmlns="http://www.w3.org/2000/svg" width="80" height="80" fill="currentColor" class="warning-icon" viewBox="0 0 16 16">
          <path d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/>
        </svg>
      </div>
      <h2 class="title">您尚未登录</h2>
      <p class="subtitle">登录以获取基于高维语义的专属游戏推荐及更多高级功能</p>

      <div class="action-buttons">
        <router-link to="/login" class="steam-btn primary-btn">立即登录</router-link>
        <router-link to="/" class="steam-btn secondary-btn">返回主页</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.unauthorized-page {
  display: flex;
  justify-content: center;
  align-items: center;
  /* 减去顶栏高度，保证绝对居中 */
  min-height: calc(100vh - 104px);
  background-color: #1b2838;
}

.unauthorized-card {
  background-color: rgba(0, 0, 0, 0.4);
  border: 1px solid #2a475e;
  border-radius: 8px;
  padding: 60px 80px;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(5px);
}

.warning-icon {
  color: #e5c158; /* Steam风格警告黄 */
  filter: drop-shadow(0 0 15px rgba(229, 193, 88, 0.3));
  margin-bottom: 25px;
}

.title {
  color: #ffffff;
  font-size: 32px;
  font-weight: bold;
  letter-spacing: 2px;
  margin-bottom: 15px;
}

.subtitle {
  color: #8f98a0;
  font-size: 16px;
  margin-bottom: 40px;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
}

/* 按钮样式复用 */
.steam-btn {
  padding: 12px 30px;
  border-radius: 2px;
  font-size: 16px;
  font-weight: bold;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.primary-btn {
  background: linear-gradient(to right, #47bfff 5%, #1a44c2 60%);
  color: #ffffff;
}

.primary-btn:hover {
  background: linear-gradient(to right, #47bfff 5%, #1a44c2 80%);
  color: #fff;
  transform: scale(1.05);
}

.secondary-btn {
  background-color: #2a475e;
  color: #c6d4df;
}

.secondary-btn:hover {
  background-color: #66c0f4;
  color: #1b2838;
  transform: scale(1.05);
}
</style>