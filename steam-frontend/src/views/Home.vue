<template>
  <div class="home-page">
    <div class="steam-container">

      <div class="welcome-header">
        <h1 class="glow-text">精选与推荐</h1>
        <p>探索 Steam 海量佳作，获取您的专属推荐</p>
      </div>

      <div id="gameCarousel" class="carousel slide shadow-lg steam-carousel" data-bs-ride="carousel">
        <div class="carousel-indicators">
          <button v-for="(game, index) in featuredGames" :key="'ind-'+index"
                  type="button" data-bs-target="#gameCarousel" :data-bs-slide-to="index"
                  :class="{ active: index === 0 }" aria-current="true" :aria-label="'Slide ' + (index + 1)"></button>
        </div>
        <div class="carousel-inner">
          <div v-for="(game, index) in featuredGames" :key="game.id" class="carousel-item" :class="{ active: index === 0 }">
            <div class="carousel-image-wrapper">
              <img :src="game.image" class="d-block w-100 carousel-bg" :alt="game.name">
              <div class="gradient-overlay"></div>
            </div>
            <div class="carousel-caption steam-caption d-none d-md-block">
              <h2 class="game-title">{{ game.name }}</h2>
              <div class="game-tags">
                <span class="tag" v-for="tag in game.tags" :key="tag">{{ tag }}</span>
              </div>
              <p class="game-desc">{{ game.description }}</p>
              <div class="action-buttons">
                <a :href="'https://store.steampowered.com/app/' + game.id" target="_blank" class="steam-btn primary-btn">
                  查看详情
                </a>
              </div>
            </div>
          </div>
        </div>
        <button class="carousel-control-prev" type="button" data-bs-target="#gameCarousel" data-bs-slide="prev">
          <span class="carousel-control-prev-icon" aria-hidden="true"></span>
          <span class="visually-hidden">Previous</span>
        </button>
        <button class="carousel-control-next" type="button" data-bs-target="#gameCarousel" data-bs-slide="next">
          <span class="carousel-control-next-icon" aria-hidden="true"></span>
          <span class="visually-hidden">Next</span>
        </button>
      </div>

      <div v-if="!isLoggedIn" class="cta-section">
        <h3>想看专属你口味的游戏？</h3>
        <p>我们的混合协同过滤与语义理解引擎，将深度解析你的游戏偏好。</p>
        <div class="cta-actions">
          <router-link to="/login" class="steam-btn primary-btn">立即登录</router-link>
        </div>
      </div>

      <div v-else class="explore-section">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h3 class="glow-text" style="font-size: 22px;">探索 Steam 游戏库</h3>
          <router-link to="/recommend" class="btn btn-outline-info btn-sm">前往我的专属推荐</router-link>
        </div>

        <div class="row row-cols-1 row-cols-md-3 row-cols-lg-4 g-4">
          <div class="col" v-for="(game, index) in exploreGames" :key="index + '-' + game.game_id">
            <div class="card h-100 shadow-sm hover-shadow" style="background-color: #171a21; border: 1px solid #2a475e; color: #c6d4df; position: relative;">
              <button @click.stop="openStatsModal(game.game_id)" class="btn position-absolute top-0 end-0 m-2 shadow-sm viz-btn" title="查看数据面板">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" class="viz-icon">
                <path d="M3 3v18h18v-2H5V3H3zm6 14V8h4v9H9zm6 0V5h4v12h-4z"/>
              </svg>
            </button>
              <img :src="game.cover_image" class="card-img-top" :alt="game.game_name" @error="handleImageError">
              <div class="card-body">
                <h6 class="card-title fw-bold text-truncate" style="color: #ffffff;">{{ game.game_name }}</h6>
                <p class="card-text mb-2">
                  <span v-for="tag in formatTags(game.tags)" :key="tag" class="badge me-1 mb-1" style="background-color: #384959; color: #66c0f4; border: 1px solid rgba(102,192,244,0.2); font-weight: normal;">
                    {{ tag }}
                  </span>
                </p>

                <div class="d-flex align-items-center mt-3">
                  <div v-if="game.discount && game.discount > 0" class="badge bg-success me-2 py-1 px-2"
                       style="font-size: 1rem; background-color: #4c6b22 !important;">
                    -{{ game.discount }}%
                  </div>

                  <div class="d-flex flex-column">
                    <span v-if="game.discount && game.discount > 0" class="text-decoration-line-through small" style="color: #8f98a0; font-size: 0.8rem;">
                      {{ game.original_price }}
                    </span>
                    <span class="fw-bold" :class="(game.discount && game.discount > 0) ? 'text-success' : 'text-info'"
                          style="font-size: 1.1rem;">
                      {{ game.current_price || '暂无报价' }}
                    </span>
                  </div>
                </div>
              </div>
              <div class="card-footer border-top-0 d-grid" style="background-color: rgba(0,0,0,0.2); padding: 10px;">
                <a :href="'https://store.steampowered.com/app/' + game.game_id" target="_blank" class="btn btn-outline-info btn-sm">
                  查看商店页
                </a>
              </div>
            </div>
          </div>
        </div>

        <div v-if="loadingMore" class="text-center mt-5 mb-3">
          <div class="spinner-border text-info" role="status"></div>
          <p class="mt-2 text-info">加载中...</p>
        </div>
        <div v-if="noMoreData" class="text-center mt-5 mb-3 text-muted">
          没有更多游戏了~
        </div>
      </div>

    </div>
  </div>

  <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content-custom">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h4 style="color: #66c0f4;">{{ currentStatsGameName }} - 数据面板</h4>
          <button class="btn-close btn-close-white" @click="closeModal"></button>
        </div>

        <div v-if="statsLoading" class="text-center my-5">
          <div class="spinner-border text-info" role="status"></div>
          <p class="mt-2 text-white-50">正在连接 Steam 官方 API 获取实时数据...</p>
        </div>

        <div v-show="!statsLoading" class="row">
          <div class="col-md-6">
            <div ref="radarChartRef" style="width: 100%; height: 300px;"></div>
          </div>
          <div class="col-md-6">
            <div ref="barChartRef" style="width: 100%; height: 300px;"></div>
          </div>
        </div>
      </div>
    </div>
</template>

<script setup>
// 🌟 修复：引入了 nextTick，防止因为找不到该函数而报错崩溃
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'

// 轮播图数据
const featuredGames = ref([
  { id: '2358720', name: '黑神话：悟空', image: 'https://cdn.akamai.steamstatic.com/steam/apps/2358720/header.jpg', description: '一款以中国神话为背景的动作角色扮演游戏...', tags: ['动作', '角色扮演', '神话'] },
  { id: '1086940', name: '博德之门 3', image: 'https://cdn.akamai.steamstatic.com/steam/apps/1086940/header.jpg', description: '召集你的队伍，返回被遗忘的国度...', tags: ['CRPG', '角色扮演', '剧情丰富'] },
  { id: '1091500', name: '赛博朋克 2077', image: 'https://cdn.akamai.steamstatic.com/steam/apps/1091500/header.jpg', description: '一款开放世界动作冒险RPG游戏...', tags: ['赛博朋克', '开放世界', '科幻'] },
  { id: '1245620', name: '艾尔登法环', image: 'https://cdn.akamai.steamstatic.com/steam/apps/1245620/header.jpg', description: '起来吧，褪色者。在广袤的交界地中探索未知的险境...', tags: ['类魂', '黑暗奇幻', '开放世界'] }
])

const isLoggedIn = ref(false)
const exploreGames = ref([])
const loadingMore = ref(false)
const noMoreData = ref(false)

// --- 可视化相关变量与方法 ---
const showModal = ref(false)
const statsLoading = ref(false)
const currentStatsGameName = ref('')
const radarChartRef = ref(null)
const barChartRef = ref(null)

let radarChartInstance = null
let barChartInstance = null

const openStatsModal = async (gameId) => {
  if (!gameId) return
  if (statsLoading.value) return // 🌟 防抖：防止没加载完就疯狂点击导致报错

  showModal.value = true
  statsLoading.value = true

  try {
    const res = await axios.get(`http://127.0.0.1:5000/api/game_stats/${gameId}`)

    if (res.data.code === 200) {
      currentStatsGameName.value = res.data.data.game_name
      statsLoading.value = false

      await nextTick() // 这里不再会报错了
      renderCharts(res.data.data)
    } else {
      throw new Error(res.data.msg || '获取失败')
    }
  } catch (err) {
    console.error('【可视化抓取失败】', err)
    alert('获取数据失败，请检查网络或刷新重试')
    showModal.value = false
    statsLoading.value = false // 🌟 修复：无论成功失败都要关闭转圈圈
  }
}

const renderCharts = (data) => {
  if (radarChartRef.value) {
    radarChartInstance = echarts.init(radarChartRef.value)
    radarChartInstance.setOption({
      title: {
        text: `全网评价 (总计: ${data.total_reviews})`,
        left: 'center',
        color: '#c6d4df', // 🌟 修复 ECharts 黄色警告：直接写颜色，不用 textStyle
        fontSize: 16,
        fontWeight: 'normal'
      },
      tooltip: { trigger: 'item', formatter: '{b} : {c} ({d}%)' },
      legend: { bottom: '0', textStyle: { color: '#8f98a0' } },
      series: [{
        name: '评价分布', type: 'pie', radius: ['40%', '70%'], avoidLabelOverlap: false,
        itemStyle: { borderRadius: 4, borderColor: '#1b2838', borderWidth: 2 },
        label: { show: false, position: 'center' },
        emphasis: { label: { show: true, fontSize: 16, fontWeight: 'bold', color: '#fff' } },
        labelLine: { show: false },
        // 🌟 防御性编程：防止个别游戏没有数据时导致 spread 操作符崩溃
        data: [
          { value: data.review_pie?.[0]?.value || 0, name: data.review_pie?.[0]?.name || '好评', itemStyle: { color: '#4c6b22' } },
          { value: data.review_pie?.[1]?.value || 0, name: data.review_pie?.[1]?.name || '差评', itemStyle: { color: '#a94847' } }
        ]
      }]
    })
  }

  if (barChartRef.value) {
    barChartInstance = echarts.init(barChartRef.value)
    const ccuVal = parseInt(String(data.curr_ccu).replace(/,/g, '')) || 0;
    let maxRange = 1000;
    if (ccuVal > 1000) maxRange = 10000;
    if (ccuVal > 10000) maxRange = 100000;
    if (ccuVal > 100000) maxRange = 1000000;
    if (ccuVal > 1000000) maxRange = 10000000;

    barChartInstance.setOption({
      title: {
        text: '实时在线玩家',
        left: 'center',
        color: '#c6d4df', // 🌟 修复 ECharts 黄色警告
        fontSize: 16,
        fontWeight: 'normal'
      },
      tooltip: { formatter: '{b} : {c} 人' },
      series: [{
        name: 'Player Count', type: 'gauge', min: 0, max: maxRange, splitNumber: 10,
        progress: { show: true, width: 10, itemStyle: { color: '#66c0f4' } },
        axisLine: { lineStyle: { width: 10, color: [[1, '#2a475e']] } },
        axisTick: { show: false },
        splitLine: { length: 10, lineStyle: { width: 2, color: '#8f98a0' } },
        axisLabel: { distance: 15, color: '#8f98a0', fontSize: 10, formatter: (value) => value >= 1000 ? (value / 1000) + 'k' : value },
        anchor: { show: true, showAbove: true, size: 12, itemStyle: { borderWidth: 2, borderColor: '#66c0f4', color: '#1b2838' } },
        pointer: { itemStyle: { color: '#66c0f4' } },
        title: { offsetCenter: [0, '70%'], textStyle: { color: '#8f98a0', fontSize: 12 } },
        detail: { valueAnimation: true, offsetCenter: [0, '100%'], formatter: () => String(data.curr_ccu), color: '#ffffff', fontSize: 20, fontWeight: 'bold' },
        data: data.ccu_gauge || [{value: 0, name: '当前在线'}]
      }]
    })
  }
}

const closeModal = () => {
  showModal.value = false
  if (radarChartInstance) radarChartInstance.dispose()
  if (barChartInstance) barChartInstance.dispose()
}

onMounted(() => {
  const token = localStorage.getItem('username')
  if (token) {
    isLoggedIn.value = true
    const cachedExplore = sessionStorage.getItem('explore_games_cache')
    if (cachedExplore) {
      exploreGames.value = JSON.parse(cachedExplore)
    } else {
      loadMoreGames()
    }
    window.addEventListener('scroll', handleScroll)
  }
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})

const handleScroll = () => {
  if (loadingMore.value || noMoreData.value) return;
  const scrollHeight = document.documentElement.scrollHeight
  const scrollTop = document.documentElement.scrollTop || document.body.scrollTop
  const clientHeight = document.documentElement.clientHeight

  if (scrollTop + clientHeight >= scrollHeight - 150) {
    loadMoreGames()
  }
}

const loadMoreGames = async () => {
  loadingMore.value = true
  try {
    const response = await axios.get('http://127.0.0.1:5000/api/explore_games', {
      params: { limit: 20 }
    })
    if (response.data.code === 200) {
      const newGames = response.data.data
      if (newGames.length === 0) {
        noMoreData.value = true
      } else {
        exploreGames.value.push(...newGames)
        sessionStorage.setItem('explore_games_cache', JSON.stringify(exploreGames.value))
      }
    }
  } catch (err) {
    console.error('加载游戏失败', err)
  } finally {
    loadingMore.value = false
  }
}

const formatTags = (tagsData) => {
  if (!tagsData) return [];
  if (Array.isArray(tagsData)) {
    return tagsData.slice(0, 3);
  }
  try {
    return tagsData.replace(/[\[\]']/g, '').split(',').map(tag => tag.trim()).slice(0, 3);
  } catch (e) {
    return ['游戏'];
  }
}

// 🌟 防墙防报错：替换为 Base64 纯代码图片
const handleImageError = (e) => {
  e.target.src = 'data:image/svg+xml;charset=UTF-8,%3Csvg%20width%3D%22292%22%20height%3D%22136%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%20292%20136%22%20preserveAspectRatio%3D%22none%22%3E%3Crect%20width%3D%22292%22%20height%3D%22136%22%20fill%3D%22%232a475e%22%2F%3E%3Ctext%20x%3D%22146%22%20y%3D%2268%22%20fill%3D%22%2366c0f4%22%20font-family%3D%22sans-serif%22%20font-size%3D%2216%22%20text-anchor%3D%22middle%22%20alignment-baseline%3D%22middle%22%3ENo%20Image%3C%2Ftext%3E%3C%2Fsvg%3E'
}
</script>

<style scoped>
/* 保持全局暗黑基调 */
.home-page {
  background-color: #1b2838;
  min-height: calc(100vh - 104px);
  padding: 40px 0;
  color: #c6d4df;
}

.steam-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 欢迎标题 */
.welcome-header {
  text-align: left;
  margin-bottom: 20px;
}
.glow-text {
  color: #ffffff;
  font-size: 28px;
  text-transform: uppercase;
  letter-spacing: 2px;
  font-weight: 300;
  text-shadow: 0 0 10px rgba(102, 192, 244, 0.3);
}
.welcome-header p {
  color: #8f98a0;
  font-size: 14px;
}

/* 轮播图样式重置与 Steam 化 */
.steam-carousel {
  background-color: #000;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8) !important;
  margin-bottom: 50px;
}

.carousel-image-wrapper {
  position: relative;
  height: 450px; /* 固定高度，让大图展示更丰满 */
}

.carousel-bg {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center 20%;
}

/* 渐变遮罩，让文字更容易看清，同时拥有 Steam 的质感 */
.gradient-overlay {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: linear-gradient(to right, rgba(15, 25, 34, 0.95) 0%, rgba(15, 25, 34, 0.6) 40%, rgba(0,0,0,0) 100%);
}

.steam-caption {
  text-align: left;
  left: 5%;
  bottom: 15%;
  max-width: 50%;
  padding-bottom: 0;
}

.game-title {
  font-size: 32px;
  font-weight: bold;
  color: #ffffff;
  margin-bottom: 15px;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
}

.game-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 15px;
}
.tag {
  background-color: rgba(56, 73, 89, 0.8);
  color: #66c0f4;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 2px;
  backdrop-filter: blur(4px);
}

.game-desc {
  font-size: 14px;
  line-height: 1.6;
  color: #acb2b8;
  margin-bottom: 25px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 按钮通用样式 */
.steam-btn {
  display: inline-block;
  padding: 10px 24px;
  border-radius: 2px;
  font-size: 15px;
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
  transform: scale(1.02);
}
.secondary-btn {
  background-color: #2a475e;
  color: #c6d4df;
}
.secondary-btn:hover {
  background-color: #66c0f4;
  color: #1b2838;
}

/* 底部引导区 */
.cta-section {
  text-align: center;
  background-color: rgba(0, 0, 0, 0.3);
  padding: 40px;
  border-radius: 4px;
  border: 1px solid #2a475e;
}
.cta-section h3 {
  color: #ffffff;
  font-weight: 300;
  margin-bottom: 10px;
}
.cta-section p {
  color: #8f98a0;
  margin-bottom: 25px;
}
.cta-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
}
/* 🌟 优化后的可视化按钮样式：毛玻璃 + 悬浮显示 */
.viz-btn {
  background-color: rgba(23, 26, 33, 0.7);
  backdrop-filter: blur(4px);
  border: 1px solid rgba(102, 192, 244, 0.3);
  color: #c6d4df;
  border-radius: 6px;
  padding: 6px 8px;
  z-index: 10;
  opacity: 0; /* 默认隐藏 */
  transition: all 0.3s ease;
}

.card:hover .viz-btn {
  opacity: 1; /* 鼠标悬浮在卡片时显示 */
}

.viz-btn:hover {
  background-color: rgba(102, 192, 244, 0.2);
  border-color: #66c0f4;
  color: #ffffff;
  transform: scale(1.05);
}

/* 🌟 弹窗遮罩层 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.7);
  z-index: 1050;
  display: flex;
  justify-content: center;
  align-items: center;
  backdrop-filter: blur(5px);
}

/* 🌟 弹窗主体内容 */
.modal-content-custom {
  background-color: #1b2838;
  border: 2px solid #2a475e;
  border-radius: 8px;
  width: 90%;
  max-width: 800px;
  padding: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8);
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from { transform: translateY(-20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}
</style>