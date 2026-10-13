<template>
  <div class="recommend-container py-5">

    <div class="text-center mb-5">
      <h1 class="display-4 fw-bold" style="color: #ffffff;">Steam 游戏推荐系统</h1>
      <p class="lead" style="color: #66c0f4;">基于混合协同过滤与语义理解算法</p>
    </div>

    <div v-if="!hasSteamId" class="row justify-content-center mb-5">
      <div class="col-md-6">
        <div class="alert text-center" style="background-color: #2a475e; color: #fff; border: 1px solid #66c0f4;" role="alert">
          <h5 class="mb-3">⚠️ 您还未绑定 Steam 账号</h5>
          <p class="mb-0 text-white-50">系统需要读取您的 Steam 游戏库才能生成个性化推荐。</p>
        </div>
        <div class="input-group input-group-lg shadow-sm mt-3">
          <input
            v-model="bindInput"
            type="text"
            class="form-control"
            style="background-color: #32353c; color: #fff; border-color: #2a475e;"
            placeholder="请输入 Steam 用户名或 17位 ID"
            @keyup.enter="bindSteamId"
          >
          <button class="btn btn-primary" @click="bindSteamId">
            立即绑定
          </button>
        </div>
      </div>
    </div>

    <div v-else>

      <div v-if="loading && recommendations.length === 0" class="text-center my-5">
        <div class="spinner-border text-info" role="status" style="width: 3rem; height: 3rem;"></div>
        <h5 class="mt-3" style="color: #c6d4df;">正在分析您的游戏口味...</h5>
      </div>

      <div v-if="error" class="alert alert-danger text-center mx-auto" style="max-width: 600px;" role="alert">
        {{ error }}
      </div>

      <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
        <div class="col" v-for="game in recommendations" :key="game.game_id">
          <div class="card h-100 shadow-sm hover-shadow position-relative" style="background-color: #171a21; border: 1px solid #2a475e; color: #c6d4df;">

            <button @click.stop="openStatsModal(game.game_id)" class="btn position-absolute m-2 shadow-sm viz-btn" style="top: 0px; right: 0px;" title="查看数据面板">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" class="viz-icon">
                <path d="M3 3v18h18v-2H5V3H3zm6 14V8h4v9H9zm6 0V5h4v12h-4z"/>
              </svg>
            </button>

            <button
              @click.stop="getAiReason(game)"
              class="btn position-absolute shadow-sm viz-btn ai-icon-btn"
              style="top: 45px; right: 8px;"
              :title="game.isAiLoading ? 'AI 深度思考中...' : '生成 AI 推荐理由'"
              :disabled="game.isAiLoading">
              <span v-if="game.isAiLoading" class="spinner-border spinner-border-sm ai-spinner" role="status" aria-hidden="true"></span>
              <svg v-else xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" viewBox="0 0 16 16">
                <path d="M8 16a2 2 0 0 0 2-2H6a2 2 0 0 0 2 2zm.995-14.901a1 1 0 1 0-1.99 0A5.002 5.002 0 0 0 3 6c0 1.098-.5 6-2 7h14c-1.5-1-2-5.902-2-7 0-2.42-1.72-4.44-4.005-4.901z"/>
              </svg>
            </button>

            <img :src="game.cover_image" class="card-img-top" :alt="game.game_name" @error="handleImageError">
            <div class="card-body pb-2">
              <h5 class="card-title fw-bold text-truncate" style="color: #ffffff;" :title="game.game_name">{{ game.game_name }}</h5>
              <p class="card-text mb-2">
                <span v-for="tag in formatTags(game.tags)" :key="tag" class="badge me-1 mb-1" style="background-color: #384959; color: #66c0f4; border: 1px solid rgba(102,192,244,0.2);">
                  {{ tag }}
                </span>
              </p>
              <div class="d-flex align-items-center mt-3">
                <div v-if="game.discount && game.discount > 0" class="badge bg-success me-2 py-2 px-2" style="font-size: 1.1rem; background-color: #4c6b22 !important;">
                  -{{ game.discount }}%
                </div>
                <div class="d-flex flex-column">
                  <span v-if="game.discount && game.discount > 0" class="text-decoration-line-through small" style="color: #8f98a0;">
                    {{ game.original_price }}
                  </span>
                  <span class="fw-bold" :class="(game.discount && game.discount > 0) ? 'text-success' : 'text-info'" style="font-size: 1.2rem;">
                    {{ game.current_price || '暂无报价' }}
                  </span>
                </div>
              </div>

              <div v-if="game.aiReason" class="ai-text-box mt-3">
                <div class="ai-badge">AI 洞察</div>
                <p class="mb-0">{{ game.aiReason }}</p>
              </div>

            </div>
            <div class="card-footer border-top-0 d-grid" style="background-color: rgba(0,0,0,0.2);">
              <a :href="'https://store.steampowered.com/app/' + game.game_id" target="_blank" class="btn btn-outline-info btn-sm">
                查看 Steam 商店页
              </a>
            </div>

          </div>
        </div>
      </div>

      <div v-if="loadingMore" class="text-center my-4 py-3" style="color: #66c0f4;">
        <div class="spinner-border spinner-border-sm" role="status"></div>
        <span class="ms-2">正在获取更多推荐...</span>
      </div>

      <div v-if="noMoreData && recommendations.length > 0" class="text-center mt-5 mb-3" style="color: #8f98a0;">
        <p>— 已经到底啦，以上是为您精选的 50 款游戏 —</p>
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
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'

const hasSteamId = ref(false)
const bindInput = ref('')
const recommendations = ref([])
const loading = ref(false)
const loadingMore = ref(false)
const error = ref('')
const page = ref(1)
const noMoreData = ref(false)

const showModal = ref(false)
const statsLoading = ref(false)
const currentStatsGameName = ref('')
const radarChartRef = ref(null)
const barChartRef = ref(null)

let radarChartInstance = null
let barChartInstance = null

const getAiReason = async (game) => {
  if (game.isAiLoading || game.aiReason) return;
  game.isAiLoading = true;
  try {
    const res = await axios.post('http://127.0.0.1:5000/api/ai_reason', {
      game_name: game.game_name || '未知游戏',
      game_tags: Array.isArray(game.tags) ? game.tags.join('、') : game.tags
    });
    if (res.data.code === 200) {
      game.aiReason = res.data.reason;
    } else {
      alert("AI 开小差了：" + res.data.msg);
    }
  } catch (err) {
    console.error("AI 接口请求失败", err);
    alert("AI 服务暂时不可用，请检查后端是否开启。");
  } finally {
    game.isAiLoading = false;
  }
}

const openStatsModal = async (gameId) => {
  showModal.value = true
  statsLoading.value = true
  try {
    const res = await axios.get(`http://127.0.0.1:5000/api/game_stats/${gameId}`)
    if (res.data.code === 200) {
      currentStatsGameName.value = res.data.data.game_name
      statsLoading.value = false
      await nextTick()
      renderCharts(res.data.data)
    }
  } catch (err) {
    alert('获取数据失败，请检查网络或后端状态')
    showModal.value = false
  }
}

const renderCharts = (data) => {
  if (radarChartRef.value) {
    radarChartInstance = echarts.init(radarChartRef.value)
    radarChartInstance.setOption({
      title: {
        text: `全网评价 (总计: ${data.total_reviews})`,
        left: 'center',
        textStyle: {color: '#c6d4df', fontSize: 16, fontWeight: 'normal'}
      },
      tooltip: {trigger: 'item', formatter: '{b} : {c} ({d}%)'},
      legend: {bottom: '0', textStyle: {color: '#8f98a0'}},
      series: [{
        name: '评价分布',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {borderRadius: 4, borderColor: '#1b2838', borderWidth: 2},
        label: {show: false, position: 'center'},
        emphasis: { label: {show: true, fontSize: 16, fontWeight: 'bold', color: '#fff'} },
        labelLine: {show: false},
        data: [
          {...data.review_pie[0], itemStyle: {color: '#4c6b22'}},
          {...data.review_pie[1], itemStyle: {color: '#a94847'}}
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
        textStyle: {color: '#c6d4df', fontSize: 16, fontWeight: 'normal'}
      },
      tooltip: {formatter: '{b} : {c} 人'},
      series: [{
        name: 'Player Count',
        type: 'gauge',
        min: 0,
        max: maxRange,
        splitNumber: 10,
        progress: {show: true, width: 10, itemStyle: {color: '#66c0f4'}},
        axisLine: {lineStyle: {width: 10, color: [[1, '#2a475e']]}},
        axisTick: {show: false},
        splitLine: {length: 10, lineStyle: {width: 2, color: '#8f98a0'}},
        axisLabel: {
          distance: 15, color: '#8f98a0', fontSize: 10, formatter: (value) => {
            if (value >= 1000) return (value / 1000) + 'k';
            return value;
          }
        },
        anchor: { show: true, showAbove: true, size: 12, itemStyle: {borderWidth: 2, borderColor: '#66c0f4', color: '#1b2838'} },
        pointer: {itemStyle: {color: '#66c0f4'}},
        title: {offsetCenter: [0, '70%'], textStyle: {color: '#8f98a0', fontSize: 12}},
        detail: {
          valueAnimation: true, offsetCenter: [0, '100%'],
          formatter: () => String(data.curr_ccu),
          color: '#ffffff', fontSize: 20, fontWeight: 'bold'
        },
        data: data.ccu_gauge
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
  const steamId = localStorage.getItem('steam_identifier')

  // 严格判断：只有本地存在有效的 steam_identifier，才认为是已绑定
  if (steamId && steamId !== 'null' && steamId.trim() !== '') {
    hasSteamId.value = true
    const cachedData = sessionStorage.getItem('recommend_games_cache')
    if (cachedData) {
      recommendations.value = JSON.parse(cachedData)
      page.value = Math.floor(recommendations.value.length / 10) + 1
      if (recommendations.value.length >= 50) {
        noMoreData.value = true
      }
    } else {
      getRecommendations(steamId)
    }
    window.addEventListener('scroll', handleScroll)
  } else {
    hasSteamId.value = false
  }
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})

const handleScroll = () => {
  if (loading.value || loadingMore.value || noMoreData.value || !hasSteamId.value) return
  const scrollY = window.scrollY
  const visibleHeight = window.innerHeight
  const documentHeight = document.documentElement.scrollHeight

  if (scrollY + visibleHeight >= documentHeight - 200) {
    const steamId = localStorage.getItem('steam_identifier')
    const userToFetch = (steamId && steamId !== 'null') ? steamId : localStorage.getItem('username')
    getRecommendations(userToFetch, true)
  }
}

const bindSteamId = async () => {
  if (!bindInput.value) {
    alert('请输入 Steam ID！')
    return
  }
  try {
    const username = localStorage.getItem('username')
    const res = await axios.post('http://127.0.0.1:5000/api/bind_steam', {
      username: username,
      steam_identifier: bindInput.value
    })

    if (res.data.code === 200) {
      alert('绑定成功！')
      localStorage.setItem('steam_identifier', bindInput.value)
      hasSteamId.value = true
      page.value = 1
      noMoreData.value = false
      recommendations.value = []
      getRecommendations(bindInput.value)
      window.addEventListener('scroll', handleScroll)
    }
  } catch (err) {
    alert(err.response?.data?.msg || '绑定失败，请检查网络')
  }
}

const getRecommendations = async (steamIdToFetch, isLoadMore = false) => {
  if (isLoadMore) {
    loadingMore.value = true
  } else {
    loading.value = true
  }
  error.value = ''

  try {
    const response = await axios.get(`http://127.0.0.1:5000/api/recommend`, {
      params: {
        username: steamIdToFetch,
        page: page.value
      }
    })

    if (response.data.code === 200) {
      const newRecs = response.data.data.recommendations
      const hasMore = response.data.data.has_more

      if (isLoadMore) {
        recommendations.value.push(...newRecs)
      } else {
        recommendations.value = newRecs
      }
      sessionStorage.setItem('recommend_games_cache', JSON.stringify(recommendations.value))

      if (!hasMore || recommendations.value.length >= 50 || newRecs.length === 0) {
        noMoreData.value = true
      } else {
        page.value++
      }
    }
  } catch (err) {
    error.value = err.response?.data?.msg || '连接后端服务器失败，请确保 Flask 程序正在运行！'
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

const formatTags = (tagsRaw) => {
  if (!tagsRaw) return [];
  if (Array.isArray(tagsRaw)) {
    return tagsRaw.slice(0, 5);
  }
  try {
    return tagsRaw.replace(/[\[\]']/g, '').split(',').map(tag => tag.trim()).slice(0, 5);
  } catch (e) {
    return ['Game'];
  }
}

const handleImageError = (e) => {
  e.target.src = 'data:image/svg+xml;charset=UTF-8,%3Csvg%20width%3D%22292%22%20height%3D%22136%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%20292%20136%22%20preserveAspectRatio%3D%22none%22%3E%3Crect%20width%3D%22292%22%20height%3D%22136%22%20fill%3D%22%232a475e%22%2F%3E%3Ctext%20x%3D%22146%22%20y%3D%2268%22%20fill%3D%22%2366c0f4%22%20font-family%3D%22sans-serif%22%20font-size%3D%2216%22%20text-anchor%3D%22middle%22%20alignment-baseline%3D%22middle%22%3ENo%20Image%3C%2Ftext%3E%3C%2Fsvg%3E'
}
</script>

<style scoped>
.recommend-container {
  background-color: #1b2838;
  min-height: calc(100vh - 104px);
}

.hover-shadow:hover {
  transform: translateY(-5px);
  transition: all 0.3s ease;
  box-shadow: 0 1rem 3rem rgba(0, 0, 0, 0.5) !important;
}

.card-img-top {
  height: 180px;
  object-fit: cover;
}

.form-control:focus {
  background-color: #3a3e47 !important;
  color: #fff !important;
  border-color: #66c0f4 !important;
  box-shadow: none;
}

/* 共用的悬浮按钮样式 */
.viz-btn {
  background-color: rgba(23, 26, 33, 0.7);
  backdrop-filter: blur(4px);
  border: 1px solid rgba(102, 192, 244, 0.3);
  color: #c6d4df;
  border-radius: 6px;
  padding: 6px 8px;
  z-index: 10;
  opacity: 0;
  transition: all 0.3s ease;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 特别给 AI 按钮定制的悬浮发光颜色 */
.ai-icon-btn:hover {
  background-color: rgba(153, 242, 200, 0.2) !important;
  border-color: #99f2c8 !important;
  color: #99f2c8 !important;
}

.ai-spinner {
  width: 1rem;
  height: 1rem;
  color: #99f2c8;
}

.card:hover .viz-btn {
  opacity: 1;
}

.viz-btn:hover {
  background-color: rgba(102, 192, 244, 0.2);
  border-color: #66c0f4;
  color: #ffffff;
  transform: scale(1.05);
}

/* 🌟 AI 理由展示区样式 */
.ai-text-box {
  padding: 12px 10px 10px 10px;
  background: rgba(153, 242, 200, 0.08);
  border-left: 3px solid #99f2c8;
  border-radius: 0 4px 4px 0;
  font-size: 13px;
  color: #c6d4df;
  line-height: 1.6;
  position: relative;
  animation: fadeIn 0.4s ease-in-out;
}

.ai-badge {
  position: absolute;
  top: -10px;
  left: 10px;
  background: #99f2c8;
  color: #0b0f19;
  font-size: 11px;
  font-weight: bold;
  padding: 2px 8px;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-5px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

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
  from {
    transform: translateY(-20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
</style>