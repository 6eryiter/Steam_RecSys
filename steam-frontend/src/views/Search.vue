<template>
  <div class="search-page-wrapper">
    <div class="steam-container">

      <div class="page-header">
        <h1 class="glow-text">搜索结果：</h1>
        <p class="subtitle">
          为您匹配关键字：
          <span class="highlight-query">"{{ keyword }}"</span>
          <template v-if="!loading && results.length > 0">
             (共有 {{ results.length }} 款相关游戏)
          </template>
        </p>
      </div>

      <div v-if="loading" class="status-state loading-state">
        <div class="spinner-border text-info" role="status"></div>
        <p class="mt-3 text-info">正在从 Steam 数据库中检索并实时校验...</p>
      </div>

      <div v-else-if="results.length === 0" class="status-state empty-state">
        <div class="icon-wrapper">
          <svg xmlns="http://www.w3.org/2000/svg" width="80" height="80" fill="currentColor" class="warning-icon" viewBox="0 0 16 16">
            <path d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/>
          </svg>
        </div>
        <h3 class="status-title">找不到匹配的游戏</h3>
        <p class="status-desc">找不到与 "{{ keyword }}" 相关的存活游戏，可能已下架或锁区。</p>
        <button @click="$router.push('/')" class="back-btn steam-btn secondary-btn">返回主页</button>
      </div>

      <div v-else class="game-grid">
        <div v-for="game in results" :key="game.game_id" class="game-card">
          <img :src="game.cover_image" :alt="game.game_name" class="game-img" @error="handleImageError" />

          <div class="card-body">
            <h6 class="game-title fw-bold text-truncate" :title="game.game_name">{{ game.game_name }}</h6>

            <p class="tags-row mb-2">
              <span v-for="(tag, index) in game.tags.slice(0, 3)" :key="index" class="game-tag">
                {{ tag }}
              </span>
            </p>

            <div class="price-discount-area d-flex align-items-center mt-3">
              <div v-if="game.discount && game.discount > 0" class="badge bg-success me-2 discount-badge">
                -{{ game.discount }}%
              </div>

              <div class="prices-stack d-flex flex-column">
                <span v-if="game.discount && game.discount > 0" class="original-price text-decoration-line-through small">
                  {{ game.original_price }}
                </span>
                <span class="fw-bold current-price-text" :class="(game.discount && game.discount > 0) ? 'text-success' : 'text-info'">
                  {{ game.current_price }}
                </span>
              </div>
            </div>
          </div>

          <div class="card-footer border-top-0 d-grid">
            <a :href="'https://store.steampowered.com/app/' + game.game_id" target="_blank" class="steam-btn secondary-btn btn-sm text-center">
              查看详情
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const keyword = ref(route.query.keyword || '')
const results = ref([])
const loading = ref(false)

// 发送搜索请求给后端 (保持接口逻辑不变)
const performSearch = async () => {
  if (!keyword.value) return;

  loading.value = true
  results.value = []
  try {
    const response = await axios.get(`http://127.0.0.1:5000/api/search`, {
      params: { keyword: keyword.value }
    })

    if (response.data.code === 200) {
      results.value = response.data.data
    }
  } catch (err) {
    console.error('搜索失败:', err)
  } finally {
    loading.value = false
  }
}

// 标签处理与图片处理函数 (兼容数组和字符串)
const handleImageError = (e) => { e.target.src = 'https://via.placeholder.com/460x215?text=Steam+Image' }

// 页面第一次加载时执行
onMounted(() => {
  performSearch()
})

// 监听 URL 参数的变化
watch(
  () => route.query.keyword,
  (newKeyword) => {
    if (newKeyword) {
      keyword.value = newKeyword
      performSearch()
    }
  }
)
</script>

<style scoped>
/* 🌟 完全还原系统整体一致样式的 CSS 🌟 */

.search-page-wrapper {
  background-color: #1b2838; /* 统一的 Navy Navy 底色 */
  min-height: calc(100vh - 104px);
  padding: 40px 0;
  color: #c6d4df;
}

/* 统一的主容器 (和首页一样) */
.steam-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 20px;
}

.page-header {
  text-align: left;
  margin-bottom: 30px;
  border-bottom: 1px solid rgba(102, 192, 244, 0.2);
  padding-bottom: 15px;
}

/* 统一的 Glow 标题效果 */
.glow-text {
  color: #ffffff;
  font-size: 28px;
  text-transform: uppercase;
  letter-spacing: 2px;
  font-weight: 300;
  margin: 0;
  text-shadow: 0 0 10px rgba(102, 192, 244, 0.3);
}

.subtitle {
  color: #8f98a0;
  font-size: 14px;
  margin-top: 5px;
  margin-bottom: 0;
}

.highlight-query {
  color: #66c0f4; /* Steam 亮蓝色高亮关键字 */
  font-weight: bold;
}

/* 状态展示 UI (加载中/找不到结果) */
.status-state {
  text-align: center;
  padding: 60px 0;
  margin-top: 40px;
  background-color: rgba(0, 0, 0, 0.3);
  border: 1px solid #2a475e;
  border-radius: 4px;
}

.status-title {
  color: #ffffff;
  font-weight: 300;
  margin-bottom: 10px;
}

.status-desc {
  color: #8f98a0;
  margin-bottom: 25px;
}

.warning-icon {
  color: #e5c158; /* Steam风格警告黄 */
  filter: drop-shadow(0 0 15px rgba(229, 193, 88, 0.3));
  margin-bottom: 20px;
}

/* 网格布局 (借用你主页的样式) */
.game-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

/* 🌟 完全还原首页的卡片特效 (底色、边框、悬停阴影) 🌟 */
.game-card {
  background-color: #171a21; /* 统一的 Dark 底色 */
  border: 1px solid #2a475e; /* 统一的蓝色边框 */
  color: #c6d4df;
  border-radius: 4px;
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  display: flex;
  flex-direction: column;
}

.game-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 1rem 3rem rgba(0, 0, 0, 0.5) !important;
}

.game-img {
  width: 100%;
  height: 140px;
  object-fit: cover;
}

.card-body {
  padding: 15px;
  flex-grow: 1;
}

.game-title {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #ffffff; /* 统一亮白色标题 */
}

.tags-row {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

/* 统一的标签样式 */
.game-tag {
  background-color: #384959;
  color: #66c0f4;
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 2px;
  border: 1px solid rgba(102,192,244,0.2);
}

/* 完美复原你之前的价格排版 */
.discount-badge {
  font-size: 1rem;
  background-color: #4c6b22 !important; /* 统一的 Steam 绿 */
}

.original-price {
  color: #8f98a0;
  font-size: 0.8rem;
}

.current-price-text {
  font-size: 1.1rem;
}

.card-footer {
  background-color: rgba(0,0,0,0.2);
  padding: 10px;
  margin-top: auto;
}

/* 统一的framed按钮样式 */
.steam-btn {
  display: inline-block;
  padding: 8px 20px;
  border-radius: 2px;
  font-size: 14px;
  font-weight: bold;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.secondary-btn {
  background-color: transparent;
  border: 1px solid #66c0f4; /* framed ghost 样式 */
  color: #66c0f4;
}

.secondary-btn:hover {
  background-color: #66c0f4;
  color: #1b2838;
  transform: scale(1.03);
}

.btn-sm {
  font-size: 12px;
  padding: 6px 15px;
}
</style>