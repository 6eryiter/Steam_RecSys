<template>
  <div class="persona-wrapper">
    <div class="bg-glow"></div>

    <div v-if="loading" class="loading-box">
      <div class="spinner"></div>
      <p>正在读取神经链路数据...</p>
    </div>

    <div v-else-if="!hasSteamId" class="persona-card error-card">
      <div class="alert-icon">⚠️</div>
      <h2 class="error-title">数据链路缺失</h2>
      <p class="error-text">
        系统未检测到您的 Steam 账户绑定信息。<br>
        AI 需要读取您的真实游戏库数据，才能为您生成专属的“灵魂画像”。
      </p>
      <div class="button-group mt-4">
        <button class="btn return-btn" @click="$router.push('/recommend')">前往绑定 Steam</button>
      </div>
    </div>

    <div v-else class="persona-card">
      <div class="avatar-section">
        <div class="hex-frame">
          <img :src="userAvatar" class="avatar-img" @error="handleAvatarError" />
        </div>
        <div class="ai-badge">AI 已认证</div>
      </div>

      <div class="title-section">
        <p class="label">—— 玩家称号 ——</p>
        <h1 class="persona-title">{{ personaData.title || '像素哲人' }}</h1>
      </div>

      <div class="cyber-divider">
        <span class="line"></span>
        <span class="dot"></span>
        <span class="line"></span>
      </div>

      <div class="content-box">
        <p class="persona-text">{{ personaData.content }}</p>
      </div>

      <div class="button-group">
        <button class="btn return-btn" @click="$router.push('/recommend')">返回推荐</button>
        <button class="btn retry-btn" @click="fetchPersona">重新扫描</button>
      </div>
    </div>

  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      loading: true,
      hasSteamId: false, // 新增：用于标识是否绑定了 Steam
      personaData: {title: '', content: ''},
      userAvatar: localStorage.getItem('avatar') || '',
      defaultAvatar: 'https://avatars.steamstatic.com/fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb_full.jpg'
    };
  },
  mounted() {
    this.fetchPersona();
  },
  methods: {
    async fetchPersona() {
      this.loading = true;
      const steamId = localStorage.getItem('steam_identifier');

      // 核心修复：严格校验 Steam ID
      if (!steamId || steamId === 'null' || steamId.trim() === '') {
        this.hasSteamId = false;
        this.loading = false;
        return; // 直接打断，绝不向后端发送无效请求
      }

      this.hasSteamId = true;

      try {
        // 确保只拿真实的 steamId 去请求 AI
        const res = await axios.get(`http://127.0.0.1:5000/api/user_persona`, {
          params: {username: steamId}
        });
        if (res.data.code === 200) {
          this.personaData = res.data.data;
        }
      } catch (err) {
        console.error("生成失败", err);
      } finally {
        this.loading = false;
      }
    },
    handleAvatarError(e) {
      e.target.src = this.defaultAvatar;
    }
  }
};
</script>

<style scoped>
/* 1. 基础容器：确保全屏居中 */
.persona-wrapper {
  min-height: 100vh;
  width: 100%;
  background: #0b0e14;
  display: flex;
  justify-content: center;
  align-items: center;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: #fff;
  position: relative;
  overflow: hidden;
}

.bg-glow {
  position: absolute;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle at 50% 50%, rgba(25, 153, 255, 0.15) 0%, transparent 80%);
}

/* 2. 卡片主体 */
.persona-card {
  position: relative;
  z-index: 10;
  width: 450px;
  background: rgba(23, 26, 33, 0.9);
  border: 1px solid rgba(25, 153, 255, 0.4);
  padding: 50px 40px;
  border-radius: 15px;
  box-shadow: 0 0 40px rgba(0, 0, 0, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

/* 针对错误提示卡片的特殊样式 */
.error-card {
  border-color: #a94847;
  box-shadow: 0 0 40px rgba(169, 72, 71, 0.4);
}

.alert-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.error-title {
  color: #a94847;
  font-weight: bold;
  margin-bottom: 15px;
}

.error-text {
  color: #c6d4df;
  line-height: 1.6;
  background: rgba(0, 0, 0, 0.3);
  padding: 15px;
  border-radius: 8px;
  border-left: 3px solid #a94847;
}

.mt-4 {
  margin-top: 1.5rem;
}

/* 3. 头像区域 */
.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 30px;
}

.hex-frame {
  width: 110px;
  height: 110px;
  background: #1999ff;
  padding: 3px;
  clip-path: polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%);
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  clip-path: polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%);
}

.ai-badge {
  margin-top: -15px;
  background: #1999ff;
  color: #fff;
  font-size: 12px;
  font-weight: bold;
  padding: 4px 15px;
  border-radius: 20px;
  box-shadow: 0 0 15px rgba(25, 153, 255, 0.6);
  z-index: 2;
}

/* 4. 标题文字 */
.label {
  color: #1999ff;
  font-size: 14px;
  letter-spacing: 3px;
  margin-bottom: 10px;
  font-weight: bold;
}

.persona-title {
  color: #ffffff;
  font-size: 42px;
  font-weight: 800;
  margin: 0;
  text-shadow: 0 0 10px rgba(25, 153, 255, 0.8), 0 0 20px rgba(25, 153, 255, 0.4);
}

/* 5. 分割线 */
.cyber-divider {
  display: flex;
  align-items: center;
  width: 100%;
  margin: 30px 0;
}

.line {
  flex: 1;
  height: 1px;
  background: rgba(25, 153, 255, 0.3);
}

.dot {
  width: 6px;
  height: 6px;
  background: #1999ff;
  border-radius: 50%;
  margin: 0 10px;
}

/* 6. 内容文本 */
.persona-text {
  color: #c6d4df;
  font-size: 16px;
  line-height: 1.8;
  background: rgba(0, 0, 0, 0.3);
  padding: 20px;
  border-radius: 8px;
  border-left: 3px solid #1999ff;
  text-align: justify;
}

/* 7. 按钮组 */
.button-group {
  margin-top: 40px;
  display: flex;
  gap: 15px;
}

.btn {
  padding: 10px 25px;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  transition: 0.3s;
}

.return-btn {
  background: #1999ff;
  border: none;
  color: white;
}

.return-btn:hover {
  background: #0076d1;
  transform: translateY(-2px);
}

.retry-btn {
  background: transparent;
  border: 1px solid #1999ff;
  color: #1999ff;
}

.retry-btn:hover {
  background: rgba(25, 153, 255, 0.1);
}

/* 加载动画 */
.loading-box {
  text-align: center;
  color: #1999ff;
  position: relative;
  z-index: 10;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(25, 153, 255, 0.2);
  border-top-color: #1999ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>