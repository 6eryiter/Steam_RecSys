// 文件路径: src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'

import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Recommend from '../views/Recommend.vue'
import Unauthorized from '../views/Unauthorized.vue' // 1. 引入我们刚写的拦截页
import Search from '../views/Search.vue';
import Ranking from '../views/Ranking.vue'; // 引入组件
import Dashboard from '../views/Dashboard.vue' // 确保路径正确
import UserPersona from '../views/UserPersona.vue'


const routes = [
  { path: '/', component: Home },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  {
    path: '/recommend',
    component: Recommend,
    meta: { requiresAuth: true } // 2. 解开这里的注释！给这个路由加上“必须登录”的锁
  },
  {
    path: '/unauthorized',
    component: Unauthorized // 3. 注册拦截页路由
  },
  {
    path: '/search',
    name: 'Search',
    component: Search
  },
  {
    path: '/ranking',
    name: 'Ranking',
    component: Ranking,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { title: '数据分析大屏',requiresAuth: true}

  },
  {
    path: '/persona',
    name: 'Persona',
    component: UserPersona,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// ==========================================
// 4. 核心：全局路由守卫 (每次切换页面前都会执行)
// ==========================================
router.beforeEach((to, from, next) => {
  // 检查要去的目标页面是否带有 requiresAuth 这把“锁”
  if (to.meta.requiresAuth) {

    // 从 localStorage 检查是否存有用户名（判断是否已登录）
    const isLoggedIn = localStorage.getItem('username')

    if (!isLoggedIn) {
      // 没登录：强制跳转到未登录拦截页
      next('/unauthorized')
    } else {
      // 已登录：绿灯放行
      next()
    }

  } else {
    // 目标页面不需要登录（如主页、登录页等）：直接放行
    next()
  }
})

export default router