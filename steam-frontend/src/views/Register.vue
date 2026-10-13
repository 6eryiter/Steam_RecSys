<template>
  <div class="steam-auth-container">
    <div class="auth-box">
      <div class="logo-area">
        <h2>创建账户</h2>
        <p>加入社区，探索海量佳作</p>
      </div>

      <form @submit.prevent="handleRegister" class="auth-form">
        <div class="input-group">
          <label>账户名称 (用于登录) <span class="required">*</span></label>
          <input type="text" v-model="form.username" required />
        </div>

        <div class="input-group">
          <label>玩家昵称 (用于展示) <span class="required">*</span></label>
          <input type="text" v-model="form.nickname" required placeholder="起个响亮的名字吧" />
        </div>

        <div class="input-group">
          <label>密码 <span class="required">*</span></label>
          <input type="password" v-model="form.password" required />
        </div>

        <div class="input-group">
          <label>设置头像 <span class="optional">(选填，支持 jpg/png)</span></label>
          <input type="file" @change="handleFileChange" accept="image/*" class="file-input" />
        </div>

        <div class="input-group steam-id-group">
          <label>Steam 昵称 / 17位 ID <span class="optional">(选填)</span></label>
          <input type="text" v-model="form.steam_identifier" placeholder="绑定后可开启个性化推荐" />
        </div>

        <button type="submit" class="steam-btn primary-btn">创 建 账 户</button>
      </form>

      <div class="auth-links">
        <router-link to="/login">已有账户？立即登录</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'Register',
  data() {
    return {
      form: {
        username: '',
        nickname: '',
        password: '',
        steam_identifier: ''
      },
      avatarFile: null // 用来存本地文件
    };
  },
  methods: {
    handleFileChange(event) {
      // 捕获用户选择的本地图片
      this.avatarFile = event.target.files[0];
    },
    async handleRegister() {
      // 必须用 FormData 来传文件和数据
      const formData = new FormData();
      formData.append('username', this.form.username);
      formData.append('nickname', this.form.nickname);
      formData.append('password', this.form.password);
      formData.append('steam_identifier', this.form.steam_identifier);

      if (this.avatarFile) {
        formData.append('avatar', this.avatarFile);
      }

      try {
        const res = await axios.post('http://127.0.0.1:5000/api/register', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        if (res.data.code === 200) {
          alert('注册成功，请登录！');
          this.$router.push('/login');
        }
      } catch (err) {
        alert(err.response?.data?.msg || '注册失败，请检查网络！');
      }
    }
  }
};
</script>

<style scoped>
/* 严格的 Steam 暗黑风格 */
.steam-auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 104px); /* 减去顶部导航栏高度 */
  background-color: #1b2838; /* 强制页面底色为 Steam 蓝黑 */
  padding: 40px 20px;
}

.auth-box {
  background-color: #171a21;
  padding: 40px;
  border-radius: 4px;
  width: 100%;
  max-width: 450px;
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.5);
  color: #c6d4df;
}

.logo-area {
  text-align: center;
  margin-bottom: 30px;
}

.logo-area h2 {
  color: #ffffff;
  font-size: 28px;
  margin-bottom: 10px;
  text-transform: uppercase;
  letter-spacing: 2px;
  font-weight: 300;
}

.input-group {
  margin-bottom: 20px;
}

.input-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #8f98a0;
}

.input-group input[type="text"], .input-group input[type="password"] {
  width: 100%;
  padding: 12px;
  background-color: #32353c;
  border: 1px solid #32353c;
  border-radius: 3px;
  color: #ffffff;
  box-sizing: border-box;
}

.input-group input:focus {
  outline: none;
  border-color: #66c0f4;
  background-color: #3a3e47;
}

/* 文件上传框样式美化 */
.file-input {
  width: 100%;
  color: #c6d4df;
  font-size: 13px;
  background-color: #2a3f5a;
  padding: 8px;
  border-radius: 3px;
  cursor: pointer;
}

.file-input::file-selector-button {
  background: #384959;
  border: none;
  padding: 6px 12px;
  border-radius: 2px;
  color: #66c0f4;
  cursor: pointer;
  margin-right: 10px;
  transition: 0.2s;
}

.file-input::file-selector-button:hover {
  background: #455a6f;
  color: #ffffff;
}

.steam-btn {
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: 2px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: 0.2s;
  margin-top: 10px;
  text-transform: uppercase;
}

.primary-btn {
  background: linear-gradient(to right, #47bfff 5%, #1a44c2 60%);
  color: #ffffff;
}

.primary-btn:hover {
  background: linear-gradient(to right, #47bfff 5%, #1a44c2 80%);
}

.auth-links {
  margin-top: 25px;
  text-align: center;
  font-size: 13px;
}

.auth-links a {
  color: #66c0f4;
  text-decoration: none;
  transition: 0.2s;
}

.auth-links a:hover {
  color: #ffffff;
}

.required {
  color: #ff5e5e;
}

.optional {
  color: #66c0f4;
  font-size: 10px;
}
</style>