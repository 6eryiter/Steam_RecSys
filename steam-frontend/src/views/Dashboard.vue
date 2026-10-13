<template>
  <div class="dashboard-wrapper scroll-container">
    <header class="dashboard-header">
      <h1 class="title">STEAM 全球游戏生态多维解析</h1>
    </header>

    <main class="bento-grid">

      <div class="bento-item span-8" style="height: 450px;">
        <div class="chart-box">
          <div class="chart-title">Steam 年度游戏发行繁荣趋势与产业周期</div>
          <div ref="yearLineRef" class="chart-inner"></div>
        </div>
      </div>
      <div class="bento-item span-4" style="height: 450px;">
        <div class="chart-box">
          <div class="chart-title">信仰之作：全球玩家累计好评总量版图</div>
          <div ref="treeMapRef" class="chart-inner"></div>
        </div>
      </div>

      <div class="bento-item span-7" style="height: 500px;">
        <div class="chart-box highlight-box">
          <div class="chart-title center-title">全局流派语义特征云图 (Semantic Analysis)</div>
          <div ref="wordCloudRef" class="chart-inner"></div>
        </div>
      </div>
      <div class="bento-item span-5" style="height: 500px;">
        <div class="chart-box">
          <div class="chart-title">全球玩家整体口碑情感极性</div>
          <div ref="sentimentRef" class="chart-inner"></div>
        </div>
      </div>

      <div class="bento-item span-6" style="height: 480px;">
        <div class="chart-box">
          <div class="chart-title">商业化分析：定价(USD) vs 好评率四象限矩阵</div>
          <div ref="quadrantRef" class="chart-inner"></div>
        </div>
      </div>
      <div class="bento-item span-6" style="height: 480px;">
        <div class="chart-box">
          <div class="chart-title">核心流派标签共现拓扑网络</div>
          <div ref="networkRef" class="chart-inner"></div>
        </div>
      </div>

      <div class="bento-item span-4" style="height: 440px;">
        <div class="chart-box">
          <div class="chart-title">市场发行定价域与口碑解构</div>
          <div ref="sunburstRef" class="chart-inner"></div>
        </div>
      </div>
      <div class="bento-item span-4" style="height: 440px;">
        <div class="chart-box">
          <div class="chart-title">单品多维属性生态基准雷达</div>
          <div ref="radarRef" class="chart-inner"></div>
        </div>
      </div>
      <div class="bento-item span-4" style="height: 440px;">
        <div class="chart-box">
          <div class="chart-title">内卷赛道：主流玩法标签分布漏斗</div>
          <div ref="funnelRef" class="chart-inner"></div>
        </div>
      </div>

      <div class="bento-item span-12" style="height: 450px; margin-bottom: 40px;">
        <div class="chart-box">
          <div class="chart-title">顶级开发商全球口碑贡献度排行榜 Top 10</div>
          <div ref="devBarRef" class="chart-inner"></div>
        </div>
      </div>

    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue';
import * as echarts from 'echarts';
import 'echarts-wordcloud';
import axios from 'axios';

// --- DOM Refs ---
const devBarRef = ref(null);
const yearLineRef = ref(null);
const funnelRef = ref(null); // 漏斗图
const wordCloudRef = ref(null);
const quadrantRef = ref(null);
const sunburstRef = ref(null);
const sentimentRef = ref(null);
const treeMapRef = ref(null);
const radarRef = ref(null);
const networkRef = ref(null);

const charts = [];

const initCharts = async () => {
  try {
    const res = await axios.get('http://127.0.0.1:5000/api/dashboard_data');
    const data = res.data.data;

    // 1. 年份折线图
    const yearLine = echarts.init(yearLineRef.value, 'dark');
    yearLine.setOption({
      backgroundColor: 'transparent', tooltip: { trigger: 'axis' },
      grid: { left: '5%', right: '4%', top: '15%', bottom: '10%', containLabel: true },
      xAxis: { type: 'category', boundaryGap: false, data: data.yearLine.x },
      yAxis: { type: 'value', splitLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } } },
      series: [{
        data: data.yearLine.y, type: 'line', smooth: true, symbolSize: 6,
        areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(0, 229, 255, 0.6)' }, { offset: 1, color: 'rgba(0, 229, 255, 0.05)' }]) },
        itemStyle: { color: '#00e5ff' }
      }]
    });

    // 2. 🌟 信仰之作：好评总数树形板块图
    const treeMapChart = echarts.init(treeMapRef.value, 'dark');
    treeMapChart.setOption({
      backgroundColor: 'transparent',
      tooltip: { formatter: '{b}<br/>累计好评数: {c} 条' },
      series: [{
        type: 'treemap',
        data: data.treeMap,
        roam: false, nodeClick: false, breadcrumb: { show: false },
        itemStyle: { borderColor: '#050914', borderWidth: 2, gapWidth: 2 },
        levels: [{
          colorMappingBy: 'value', itemStyle: { borderWidth: 1, gapWidth: 1 },
          color: ['#5A189A', '#7B2CBF', '#9D4EDD', '#C77DFF', '#E0AAFF'] // 赛博紫霓虹渐变
        }]
      }]
    });

    // 3. 词云图
    const wordCloud = echarts.init(wordCloudRef.value, 'dark');
    wordCloud.setOption({
      backgroundColor: 'transparent', tooltip: { show: true },
      series: [{
        type: 'wordCloud', shape: 'pentagon', sizeRange: [20, 90], rotationRange: [-45, 45],
        width: '90%', height: '90%',
        textStyle: {
          color: () => 'rgb(' + [Math.round(Math.random() * 155 + 100), Math.round(Math.random() * 255), Math.round(Math.random() * 255)].join(',') + ')',
          textShadowBlur: 5, textShadowColor: '#000'
        },
        data: data.wordCloud
      }]
    });

    // 4. 情感极性圆环图
    const sentimentChart = echarts.init(sentimentRef.value, 'dark');
    sentimentChart.setOption({
      backgroundColor: 'transparent', tooltip: { trigger: 'item' },
      color: ['#00e5ff', '#ff4b4b'], legend: { bottom: '5%', textStyle: { color: '#ccc' } },
      series: [{
        type: 'pie', radius: ['50%', '75%'], center: ['50%', '45%'],
        avoidLabelOverlap: false, itemStyle: { borderRadius: 10, borderColor: '#0b0f19', borderWidth: 4 },
        label: { show: true, formatter: '{d}%', fontSize: 18, fontWeight: 'bold' },
        data: data.sentiment
      }]
    });

    // 5. 商业四象限矩阵
    const quadrantChart = echarts.init(quadrantRef.value, 'dark');
    quadrantChart.setOption({
      backgroundColor: 'transparent',
      tooltip: { formatter: (obj) => `<b>${obj.value[3]}</b><br>售价: $${obj.value[0]}<br>好评率: ${obj.value[1].toFixed(1)}%<br>热度基准(好评数): ${obj.value[2]}` },
      grid: { left: '8%', right: '10%', top: '15%', bottom: '15%', containLabel: true },
      xAxis: { name: '售价(USD)', axisLabel: { formatter: '${value}' }, splitLine: { show: false } },
      yAxis: { name: '好评率(%)', max: 100, splitLine: { show: false } },
      series: [{
        type: 'scatter', data: data.quadrant.scatter,
        symbolSize: (val) => Math.min(Math.max(Math.sqrt(val[2]) / 20, 6), 45), // 按好评总数调整气泡大小
        itemStyle: { color: 'rgba(0, 229, 255, 0.7)', shadowBlur: 10, shadowColor: '#00e5ff' },
        markLine: {
          lineStyle: { type: 'dashed', color: '#ff416c', width: 2 },
          label: { color: '#ff416c', formatter: '{b}' },
          data: [{ xAxis: data.quadrant.avgPrice, name: '全盘均价线' }, { yAxis: data.quadrant.avgRate, name: '口碑及格线' }]
        }
      }]
    });

    // 6. 拓扑网络
    const networkChart = echarts.init(networkRef.value, 'dark');
    networkChart.setOption({
      backgroundColor: 'transparent', tooltip: {},
      series: [{
        type: 'graph', layout: 'force', data: data.network.nodes, links: data.network.links,
        roam: true, label: { show: true, position: 'right', color: '#fff', fontSize: 14 },
        force: { repulsion: 300, edgeLength: 100 },
        lineStyle: { color: 'source', curveness: 0.2, opacity: 0.6, width: 2 },
        itemStyle: { color: '#b388ff', shadowBlur: 20, shadowColor: '#b388ff' }
      }]
    });

    // 7. 定价域口碑解构 - 旭日图
    const sunburstChart = echarts.init(sunburstRef.value, 'dark');
    sunburstChart.setOption({
      backgroundColor: 'transparent',
      tooltip: { trigger: 'item', formatter: '{b}: {c} 款' },
      series: [{
        type: 'sunburst', data: data.sunburst,
        radius: ['15%', '85%'], center: ['50%', '50%'],
        itemStyle: { borderRadius: 4, borderWidth: 2, borderColor: '#050914' },
        label: { show: true, fontSize: 11, formatter: '{b}' }
      }]
    });

    // 8. 雷达图
    const radarChart = echarts.init(radarRef.value, 'dark');
    radarChart.setOption({
      backgroundColor: 'transparent', tooltip: {},
      radar: {
        indicator: data.radar.indicator, radius: '65%', center: ['50%', '50%'],
        splitArea: { areaStyle: { color: ['rgba(0, 229, 255, 0.1)', 'transparent'] } }, axisName: { color: '#00e5ff' }
      },
      series: [{
        type: 'radar', data: [{ value: data.radar.values, name: data.radar.gameName }],
        areaStyle: { color: 'rgba(255, 204, 0, 0.4)' }, itemStyle: { color: '#FFCC00' }, lineStyle: { width: 2 }
      }]
    });

    // 9. 🌟 开发者内卷赛道：主流玩法分布漏斗图
    const funnelChart = echarts.init(funnelRef.value, 'dark');
    funnelChart.setOption({
      backgroundColor: 'transparent',
      tooltip: { trigger: 'item', formatter: '{b} : {c} 款发行游戏' },
      color: ['#ff416c', '#ff7b59', '#f6d365', '#00e5ff', '#4facfe', '#00f2fe', '#a18cd1', '#fbc2eb'],
      series: [{
        type: 'funnel',
        left: '10%', top: '5%', bottom: '5%', width: '80%',
        minSize: '20%', maxSize: '100%',
        sort: 'descending', gap: 2,
        label: { show: true, position: 'inside', formatter: '{b}\n{c}', fontSize: 12, fontWeight: 'bold' },
        itemStyle: { borderColor: '#050914', borderWidth: 2, shadowBlur: 15, shadowColor: 'rgba(0, 0, 0, 0.5)' },
        data: data.funnel
      }]
    });

    // 10. 开发商柱状图
    const devBar = echarts.init(devBarRef.value, 'dark');
    devBar.setOption({
      backgroundColor: 'transparent', tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '3%', top: '15%', bottom: '15%', containLabel: true },
      xAxis: { type: 'category', data: data.devBar.x, axisLabel: { interval: 0, fontSize: 14, color: '#eee' } },
      yAxis: { type: 'value', splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } }, axisLabel: { formatter: (val) => val >= 10000 ? (val/10000)+'万' : val } },
      series: [{
        type: 'bar', barWidth: '40%', data: data.devBar.y,
        itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#a18cd1' }, { offset: 1, color: '#fbc2eb' }]), borderRadius: [8, 8, 0, 0] },
        label: { show: true, position: 'top', color: '#fff' }
      }]
    });

    charts.push(devBar, yearLine, funnelChart, wordCloud, quadrantChart, sunburstChart, sentimentChart, treeMapChart, radarChart, networkChart);

    window.addEventListener('resize', () => charts.forEach(c => c.resize()));

  } catch (error) {
    console.error("加载大屏数据失败:", error);
  }
};

onMounted(() => {
  nextTick(() => { initCharts(); });
});
</script>

<style scoped>
/* ==================== 核心容器 (允许滚动) ==================== */
.dashboard-wrapper {
  width: 100%; min-height: 100vh;
  background: #050914;
  background-image:
    radial-gradient(circle at 15% 50%, rgba(0, 229, 255, 0.08), transparent 25%),
    radial-gradient(circle at 85% 30%, rgba(255, 65, 108, 0.08), transparent 25%);
  color: #fff; font-family: 'Microsoft YaHei', sans-serif; overflow-x: hidden;
}

/* 自定义科技感滚动条 */
.scroll-container::-webkit-scrollbar { width: 8px; }
.scroll-container::-webkit-scrollbar-track { background: #0b1120; }
.scroll-container::-webkit-scrollbar-thumb { background: #1c3d6d; border-radius: 4px; }
.scroll-container::-webkit-scrollbar-thumb:hover { background: #00e5ff; }

/* ==================== 顶部导航栏 ==================== */
.dashboard-header {
  position: sticky; top: 0; z-index: 100;
  display: flex; justify-content: center; /* 改为 center 让内部元素绝对居中 */
  align-items: center;
  padding: 15px 40px;
  background: rgba(5, 9, 20, 0.85);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(0, 229, 255, 0.15);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
}

.title {
  font-size: 32px; /* 稍微调大一点字体，因为现在只有它了 */
  font-weight: 900;
  letter-spacing: 6px; /* 增加字间距更有大气感 */
  color: #fff;
  text-shadow: 0 0 20px rgba(0, 229, 255, 0.8);
  margin: 0;
}
/* ==================== Bento Box 网格布局 ==================== */
.bento-grid {
  display: grid; grid-template-columns: repeat(12, 1fr); gap: 20px;
  padding: 25px 40px; max-width: 1920px; margin: 0 auto;
}

.span-12 { grid-column: span 12; }
.span-8 { grid-column: span 8; }
.span-7 { grid-column: span 7; }
.span-6 { grid-column: span 6; }
.span-5 { grid-column: span 5; }
.span-4 { grid-column: span 4; }

/* ==================== 卡片容器样式 ==================== */
.chart-box {
  width: 100%; height: 100%;
  background: rgba(13, 22, 45, 0.5); backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 12px;
  padding: 20px; display: flex; flex-direction: column;
  transition: transform 0.3s ease, box-shadow 0.3s ease; box-sizing: border-box;
}

.chart-box:hover {
  transform: translateY(-5px); border-color: rgba(0, 229, 255, 0.3);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), inset 0 0 20px rgba(0, 229, 255, 0.05);
}

.highlight-box {
  background: linear-gradient(135deg, rgba(20, 30, 60, 0.8) 0%, rgba(10, 15, 30, 0.8) 100%);
  border: 1px solid rgba(255, 65, 108, 0.3);
}

/* ==================== 标题与内容 ==================== */
.chart-title {
  font-size: 16px; color: #e6f1ff; font-weight: bold;
  margin-bottom: 15px; padding-left: 12px; position: relative; z-index: 10;
}
.chart-title::before {
  content: ""; position: absolute; left: 0; top: 10%; height: 80%; width: 4px;
  background: #00e5ff; border-radius: 2px;
}
.center-title::before { background: #ff416c; }

.chart-inner { flex: 1; width: 100%; min-height: 0; }

@media (max-width: 1400px) {
  .span-8, .span-4, .span-7, .span-5, .span-6 { grid-column: span 12; }
  .chart-box { height: 400px !important; }
}
</style>