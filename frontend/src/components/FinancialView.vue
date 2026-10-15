<!-- src/components/FinancialView.vue -->
<template>
  <div class="space-y-6">
    <!-- 顶部利润核心指标卡片 -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
      <div class="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs space-y-2">
        <p class="text-xs font-medium text-slate-400 uppercase tracking-wider">{{ t.finRevenue || '总营业收入 (Revenue)' }}</p>
        <h3 class="text-2xl font-black text-blue-600">$ {{ analytics.total_revenue_usd.toFixed(2) }}</h3>
      </div>

      <div class="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs space-y-2">
        <p class="text-xs font-medium text-slate-400 uppercase tracking-wider">{{ t.finCost || '总进货成本 (Cost)' }}</p>
        <h3 class="text-2xl font-black text-slate-700">$ {{ analytics.total_cost_usd.toFixed(2) }}</h3>
      </div>

      <div class="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs space-y-2">
        <p class="text-xs font-medium text-slate-400 uppercase tracking-wider">{{ t.finGrossProfit || '毛利润 (Gross Profit)' }}</p>
        <h3 class="text-2xl font-black text-emerald-600">$ {{ analytics.gross_profit_usd.toFixed(2) }}</h3>
      </div>

      <div class="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs space-y-2">
        <p class="text-xs font-medium text-slate-400 uppercase tracking-wider">{{ t.finMargin || '综合毛利率 (Margin)' }}</p>
        <h3 class="text-2xl font-black text-purple-600">{{ analytics.profit_margin.toFixed(1) }}%</h3>
      </div>
    </div>

    <!-- 财务图表或品牌盈利占比说明 -->
    <div class="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-6 space-y-4">
      <h3 class="font-bold text-slate-800">📊 {{ t.finAnalysisTitle || '委内瑞拉汽配业务盈利分析提示' }}</h3>
      <div class="bg-emerald-50 border border-emerald-100 rounded-xl p-4 flex items-start gap-3">
        <span class="text-emerald-600 font-bold text-lg">💡</span>
        <div class="text-xs text-emerald-900 space-y-1">
          <p class="font-semibold">{{ t.finTipTitle || '多渠道支付与利润折算' }}</p>
          <p>{{ t.finTipDesc || '系统已自动将 Zelle、Cash USD 及 Bolívares (按 BCV 汇率折算) 统一换算为美元基准，帮您精准剔除通货膨胀带来的虚假营收，锁定真实利润。' }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from '../composables/useI18n'
import { apiUrl } from '../utils/api'

const { t } = useI18n()

// 🌟 核心修复：把所有数字字段初始化为 0.0，防止 undefined.toFixed() 报错
const analytics = ref({
  total_revenue_usd: 0.00,
  total_cost_usd: 0.00,
  gross_profit_usd: 0.00,
  profit_margin: 0.0
})

const loading = ref(true)

const fetchAnalytics = async () => {
  try {
    const res = await fetch(apiUrl('/api/financial/analytics'))
    if (res.ok) {
      const data = await res.json()
      // 🌟 使用后端返回的数据，如果没有对应字段则用 0.0 兜底
      analytics.value = {
        total_revenue_usd: data.total_revenue_usd ?? 0.00,
        total_cost_usd: data.total_cost_usd ?? 0.00,
        gross_profit_usd: (data.total_revenue_usd ?? 0) - (data.total_cost_usd ?? 0),
        profit_margin: data.profit_margin ?? 0.0
      }
    }
  } catch (e) {
    console.error("获取财务分析数据失败:", e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchAnalytics()
})
</script>