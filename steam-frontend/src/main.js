import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // 引入路由配置

// 引入 Bootstrap 样式 (推荐放在实例创建之前)
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'

// 创建应用实例
const app = createApp(App)

// 挂载路由
app.use(router)

// 统一挂载到 #app
app.mount('#app')