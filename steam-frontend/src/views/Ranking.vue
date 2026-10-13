<template>
  <div class="ranking-page-wrapper">
    <div class="steam-container">

      <div class="page-header text-center mb-5">
        <h1 class="glow-text">实时在线人数排行</h1>
        <p class="subtitle mt-2">基于 Steam 全球实时活跃玩家数据</p>
      </div>

      <div v-if="loading" class="text-center my-5">
        <div class="spinner-border text-warning" role="status" style="width: 3rem; height: 3rem;"></div>
        <h5 class="mt-3 text-warning">正在拉取全球实时数据...</h5>
      </div>

      <div v-else class="ranking-list">
        <div
          v-for="(game, index) in rankingData"
          :key="game.game_id"
          class="ranking-item d-flex align-items-center"
        >
          <div class="rank-number" :class="'rank-' + (index + 1)">
            {{ index + 1 }}
          </div>

          <img :src="game.cover_image" :alt="game.game_name" class="game-img ms-3" @error="handleImageError" />

          <div class="game-info ms-4 flex-grow-1">
            <h4 class="game-title fw-bold text-white mb-2">{{ game.game_name }}</h4>
            <div class="tags-row">
              <span v-for="(tag, i) in game.tags" :key="i" class="game-tag">{{ tag }}</span>
            </div>
          </div>

          <div class="ccu-badge me-4 text-center">
            <div class="ccu-title">当前在线</div>
            <div class="ccu-count">{{ game.ccu.toLocaleString() }}</div>
          </div>

          <div class="price-action-area text-end ms-3">
            <div class="d-flex align-items-center justify-content-end mb-2">
              <div v-if="game.discount && game.discount > 0" class="badge bg-success me-2 discount-badge">
                -{{ game.discount }}%
              </div>
              <div class="prices-stack d-flex flex-column text-end">
                <span v-if="game.discount && game.discount > 0" class="original-price text-decoration-line-through small">
                  {{ game.original_price }}
                </span>
                <span class="fw-bold current-price-text" :class="(game.discount && game.discount > 0) ? 'text-success' : 'text-info'">
                  {{ game.current_price }}
                </span>
              </div>
            </div>
            <a :href="'https://store.steampowered.com/app/' + game.game_id" target="_blank" class="steam-btn secondary-btn">
              去商店看看
            </a>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const rankingData = ref([])
const loading = ref(true)

const fetchRanking = async () => {
  try {
    const res = await axios.get('http://127.0.0.1:5000/api/ranking')
    if (res.data.code === 200) {
      rankingData.value = res.data.data

      // 🌟 获取成功后，将数据存入 sessionStorage 缓存
      sessionStorage.setItem('daily_ranking_cache', JSON.stringify(rankingData.value))
    }
  } catch (error) {
    console.error('获取排行榜失败', error)
  } finally {
    loading.value = false
  }
}

// 纯代码 Base64 占位图，防网络断连
const handleImageError = (e) => {
  e.target.src = 'data:image/svg+xml;charset=UTF-8,%3Csvg%20width%3D%22292%22%20height%3D%22136%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%20292%20136%22%20preserveAspectRatio%3D%22none%22%3E%3Crect%20width%3D%22292%22%20height%3D%22136%22%20fill%3D%22%232a475e%22%2F%3E%3Ctext%20x%3D%22146%22%20y%3D%2268%22%20fill%3D%22%2366c0f4%22%20font-family%3D%22sans-serif%22%20font-size%3D%2216%22%20text-anchor%3D%22middle%22%20alignment-baseline%3D%22middle%22%3ENo%20Image%3C%2Ftext%3E%3C%2Fsvg%3E'
}

onMounted(() => {
  // 🌟 页面挂载时，先检查有没有缓存
  const cachedData = sessionStorage.getItem('daily_ranking_cache')

  if (cachedData) {
    // 如果有缓存，直接解析赋值，瞬间渲染
    rankingData.value = JSON.parse(cachedData)
    loading.value = false // 别忘了关闭加载动画
  } else {
    // 如果没有缓存（比如第一次打开或刷新了页面），再去请求后端
    fetchRanking()
  }
})
</script>

<style scoped>
.ranking-page-wrapper {
  background-color: #1b2838;
  min-height: calc(100vh - 104px);
  padding: 40px 0;
  color: #c6d4df;
}

.steam-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 20px;
}

.glow-text {
  color: #ffffff;
  font-size: 36px;
  font-weight: bold;
  text-shadow: 0 0 15px rgba(229, 193, 88, 0.4); /* 偏金色的光晕 */
}

/* 列表容器 */
.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

/* 每一行的样式 */
.ranking-item {
  background-color: rgba(0, 0, 0, 0.4);
  border: 1px solid #2a475e;
  padding: 15px 20px;
  border-radius: 6px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.ranking-item:hover {
  background-color: #171a21;
  transform: translateX(10px); /* 悬停时往右浮动一下 */
  box-shadow: -5px 5px 15px rgba(0,0,0,0.5);
  border-color: #66c0f4;
}

/* 左侧名次 */
.rank-number {
  font-size: 32px;
  font-weight: 900;
  color: #4f697a;
  width: 50px;
  text-align: center;
  font-style: italic;
}

/* 前三名专属金色、银色、铜色特效 */
.rank-1 { color: #FFD700; text-shadow: 0 0 10px rgba(255,215,0,0.5); font-size: 40px; }
.rank-2 { color: #C0C0C0; text-shadow: 0 0 10px rgba(192,192,192,0.5); font-size: 36px; }
.rank-3 { color: #CD7F32; text-shadow: 0 0 10px rgba(205,127,50,0.5); font-size: 34px; }

.game-img {
  width: 220px;
  height: 103px;
  object-fit: cover;
  border-radius: 4px;
}

.game-title {
  font-size: 20px;
}

.game-tag {
  display: inline-block;
  background-color: #384959;
  color: #66c0f4;
  font-size: 12px;
  padding: 3px 8px;
  border-radius: 2px;
  margin-right: 6px;
}

/* 在线人数区域 */
.ccu-badge {
  background: linear-gradient(135deg, #1f2c38 0%, #2a475e 100%);
  border: 1px solid rgba(102,192,244,0.3);
  padding: 10px 15px;
  border-radius: 4px;
  min-width: 120px;
}
.ccu-title {
  font-size: 12px;
  color: #8f98a0;
  margin-bottom: 2px;
}
.ccu-count {
  font-size: 18px;
  font-weight: bold;
  color: #66c0f4;
}

/* 价格模块精美排版 */
.discount-badge { font-size: 1rem; background-color: #4c6b22 !important; padding: 6px 8px; }
.original-price { color: #8f98a0; font-size: 0.8rem; }
.current-price-text { font-size: 1.2rem; }

.steam-btn {
  display: inline-block;
  padding: 8px 20px;
  border-radius: 2px;
  font-size: 14px;
  font-weight: bold;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s;
}

.secondary-btn {
  background-color: transparent;
  border: 1px solid #66c0f4;
  color: #66c0f4;
}

.secondary-btn:hover {
  background-color: #66c0f4;
  color: #1b2838;
}
</style>