<template>
  <div class="steam-auth-container">
    <div class="auth-box">
      <div class="logo-area">
        <h2>登录</h2>
        <p>登录以获取您的专属游戏推荐</p>
      </div>

      <form @submit.prevent="handleLogin" class="auth-form">
        <div class="input-group">
          <label>账户名称</label>
          <input type="text" v-model="form.username" required />
        </div>

        <div class="input-group">
          <label>密码</label>
          <input type="password" v-model="form.password" required />
        </div>

        <button type="submit" class="steam-btn primary-btn">登 录</button>
      </form>

      <div class="auth-links">
        <router-link to="/register">没有账户？加入我们</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'Login',
  data() {
    return {
      form: {
        username: '',
        password: ''
      }
    };
  },
  methods: {
    async handleLogin() {
  try {
    const res = await axios.post('http://127.0.0.1:5000/api/login', this.form);
    if (res.data.code === 200) {
      alert('登录成功！');
      const data = res.data.data;
      // 存下所有关键信息
      localStorage.setItem('token', data.token);
      localStorage.setItem('username', data.username);
      localStorage.setItem('uid', data.uid); // 专属ID 10000+
      localStorage.setItem('nickname', data.nickname);
      localStorage.setItem('avatar', data.avatar);
      localStorage.setItem('steam_identifier', data.steam_identifier || '');

      // 关键：派发全局事件，告诉 App.vue 导航栏该更新头像了
      window.dispatchEvent(new Event('auth-change'));

      this.$router.push('/recommend');
    }
  } catch (err) {
    alert(err.response?.data?.msg || '登录失败');
  }
}
  }
}
</script>

<style scoped>
/* Steam 风格公共样式 (复制到两个页面的 <style scoped> 中，或者放在全局 css 里) */
.steam-auth-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  /* Steam 经典的深蓝色渐变背景 */
  background: radial-gradient(circle at top left, #2a475e 0%, #1b2838 50%, #171a21 100%);
  color: #c6d4df;
  font-family: 'Motiva Sans', Arial, Helvetica, sans-serif;
}

.auth-box {
  width: 100%;
  max-width: 420px;
  background-color: rgba(0, 0, 0, 0.4); /* 半透明黑色盒子 */
  padding: 40px;
  border-radius: 4px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.6);
  backdrop-filter: blur(5px);
}

.logo-area {
  text-align: center;
  margin-bottom: 30px;
}

.logo-area h2 {
  color: #ffffff;
  font-size: 28px;
  letter-spacing: 2px;
  margin: 0 0 10px 0;
  text-transform: uppercase;
  font-weight: 300;
}

.logo-area p {
  color: #8f98a0;
  font-size: 14px;
}

.input-group {
  margin-bottom: 20px;
}

.input-group label {
  display: block;
  margin-bottom: 8px;
  color: #1999ff; /* Steam 蓝色标签 */
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.input-group input {
  width: 100%;
  padding: 12px;
  background-color: #32353c; /* 深灰底色 */
  border: 1px solid #32353c;
  border-radius: 3px;
  color: #ffffff;
  font-size: 15px;
  transition: all 0.2s;
  box-sizing: border-box;
}

.input-group input:focus {
  outline: none;
  background-color: #3a3e47;
  border-color: #1999ff;
  box-shadow: 0 0 5px rgba(25, 153, 255, 0.5);
}

.steam-id-group input {
  background-color: #2b3b48; /* 稍微不同的底色区分选填区 */
}

.hint {
  display: block;
  margin-top: 6px;
  font-size: 11px;
  color: #8f98a0;
}

.required {
  color: #ff5e5e;
}
.optional {
  color: #8f98a0;
  font-size: 10px;
}

.steam-btn {
  width: 100%;
  padding: 14px;
  border: none;
  border-radius: 2px;
  font-size: 16px;
  color: #d2efa9;
  cursor: pointer;
  text-transform: uppercase;
  font-weight: bold;
  letter-spacing: 1px;
  transition: all 0.2s;
  margin-top: 10px;
}

/* 经典 Steam 绿渐变按钮 */
.primary-btn {
  background: linear-gradient(to right, #799905 5%, #536904 95%);
}

.primary-btn:hover {
  background: linear-gradient(to right, #a4d007 5%, #6b8705 95%);
  color: #ffffff;
}

.auth-links {
  margin-top: 25px;
  text-align: center;
  font-size: 13px;
}

.auth-links a {
  color: #ebebeb;
  text-decoration: none;
  transition: color 0.2s;
}

.auth-links a:hover {
  color: #ffffff;
  text-decoration: underline;
}
</style>