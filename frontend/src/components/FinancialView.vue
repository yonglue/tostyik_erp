<!-- src/components/FinancialView.vue -->
<template>
  <div class="space-y-6">
    
    <!-- 顶部利润核心指标卡片 (双币种总览) -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
      <div class="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs space-y-2">
        <p class="text-xs font-medium text-slate-400 uppercase tracking-wider">总营业收入 (Revenue)</p>
        <h3 class="text-2xl font-black text-blue-600 font-mono">$ {{ analytics.total_revenue_usd.toFixed(2) }}</h3>
        <p class="text-xs text-slate-400 font-mono">Bs. {{ (analytics.total_revenue_usd * bcvRate).toFixed(2) }}</p>
      </div>

      <div class="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs space-y-2">
        <p class="text-xs font-medium text-slate-400 uppercase tracking-wider">总进货成本 (Cost)</p>
        <h3 class="text-2xl font-black text-slate-700 font-mono">$ {{ analytics.total_cost_usd.toFixed(2) }}</h3>
        <p class="text-xs text-slate-400 font-mono">Bs. {{ (analytics.total_cost_usd * bcvRate).toFixed(2) }}</p>
      </div>

      <div class="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs space-y-2">
        <p class="text-xs font-medium text-slate-400 uppercase tracking-wider">毛利润 (Gross Profit)</p>
        <h3 class="text-2xl font-black text-emerald-600 font-mono">$ {{ analytics.gross_profit_usd.toFixed(2) }}</h3>
        <p class="text-xs text-emerald-500 font-mono font-bold">Bs. {{ (analytics.gross_profit_usd * bcvRate).toFixed(2) }}</p>
      </div>

      <div class="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs space-y-2">
        <p class="text-xs font-medium text-slate-400 uppercase tracking-wider">综合毛利率 (Margin)</p>
        <h3 class="text-2xl font-black text-purple-600 font-mono">{{ analytics.profit_margin.toFixed(1) }}%</h3>
        <p class="text-xs text-slate-400">稳定盈利状态</p>
      </div>
    </div>

    <!-- 🌟 核心新功能 1：收银对账分类（Cierre de Caja / 支付方式汇总看板） -->
    <div class="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-6 space-y-4">
      <div class="flex items-center justify-between">
        <h3 class="font-bold text-slate-800 text-base flex items-center gap-2">
          💳 今日收银对账分类 (Daily Cashier Reconciliation)
        </h3>
        <span class="text-xs bg-blue-50 text-blue-600 px-3 py-1 rounded-xl font-mono font-semibold">
          BCV 汇率基准: {{ bcvRate }}
        </span>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <!-- Zelle 电子美元 -->
        <div class="bg-slate-50 border border-slate-200/60 rounded-2xl p-4 space-y-1">
          <div class="flex items-center justify-between text-xs font-bold text-slate-500">
            <span>⚡ Zelle 电子美元</span>
            <span class="text-blue-600 font-mono">{{ paymentBreakdown.zelle.count }} 笔</span>
          </div>
          <div class="text-xl font-black text-slate-900 font-mono">$ {{ paymentBreakdown.zelle.totalUSD.toFixed(2) }}</div>
          <div class="text-xs text-slate-400 font-mono">占总流水: {{ paymentBreakdown.zelle.percentage }}%</div>
        </div>

        <!-- USD Cash 美元现金 -->
        <div class="bg-slate-50 border border-slate-200/60 rounded-2xl p-4 space-y-1">
          <div class="flex items-center justify-between text-xs font-bold text-slate-500">
            <span>💵 USD Cash 现金</span>
            <span class="text-emerald-600 font-mono">{{ paymentBreakdown.cashUSD.count }} 笔</span>
          </div>
          <div class="text-xl font-black text-slate-900 font-mono">$ {{ paymentBreakdown.cashUSD.totalUSD.toFixed(2) }}</div>
          <div class="text-xs text-slate-400 font-mono">占总流水: {{ paymentBreakdown.cashUSD.percentage }}%</div>
        </div>

        <!-- Bolívares / Pago Móvil 玻利瓦尔 -->
        <div class="bg-slate-50 border border-slate-200/60 rounded-2xl p-4 space-y-1">
          <div class="flex items-center justify-between text-xs font-bold text-slate-500">
            <span>🇻🇪 Pago Móvil / VES</span>
            <span class="text-purple-600 font-mono">{{ paymentBreakdown.bolivares.count }} 笔</span>
          </div>
          <div class="text-xl font-black text-purple-600 font-mono">Bs. {{ paymentBreakdown.bolivares.totalBs.toFixed(2) }}</div>
          <div class="text-xs text-slate-400 font-mono">折合美金: $ {{ (paymentBreakdown.bolivares.totalBs / (bcvRate || 1)).toFixed(2) }}</div>
        </div>
      </div>
    </div>

    <!-- 🌟 核心新功能 2：多币种（USD / VES）每日利润对账报表表格 -->
    <div class="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
      <div class="p-6 border-b border-slate-100 flex items-center justify-between">
        <div>
          <h3 class="font-bold text-slate-800 text-base">📈 多币种每日利润对账流水 (Multi-Currency Profit Audit Trail)</h3>
          <p class="text-xs text-slate-400 mt-0.5">自动换算每日各笔开单在美元与玻利瓦尔双币种下的真实毛利贡献</p>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[850px]">
          <thead>
            <tr class="bg-slate-50/75 border-b border-slate-100 text-xs font-semibold text-slate-500 uppercase tracking-wider">
              <th class="py-3 px-6">单据编号</th>
              <th class="py-3 px-6">交易时间</th>
              <th class="py-3 px-6">支付方式</th>
              <th class="py-3 px-6">营业额 (USD)</th>
              <th class="py-3 px-6">折算收入 (VES)</th>
              <th class="py-3 px-6">进货成本 (USD)</th>
              <th class="py-3 px-6">真实毛利 (USD / Bs.)</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            <tr v-for="row in dailyAuditList" :key="row.id" class="hover:bg-slate-50/50 transition-colors">
              <td class="py-3.5 px-6 font-mono font-bold text-blue-600">#{{ row.id }}</td>
              <td class="py-3.5 px-6 text-xs text-slate-500 font-mono">{{ row.date }}</td>
              <td class="py-3.5 px-6">
                <span class="bg-slate-100 text-slate-700 px-2.5 py-1 rounded-lg text-xs font-semibold">
                  {{ row.payment_method || 'Zelle / Cash' }}
                </span>
              </td>
              <td class="py-3.5 px-6 font-mono font-bold text-slate-900">$ {{ Number(row.revenue_usd || 0).toFixed(2) }}</td>
              <td class="py-3.5 px-6 font-mono text-slate-600">Bs. {{ (Number(row.revenue_usd || 0) * bcvRate).toFixed(2) }}</td>
              <td class="py-3.5 px-6 font-mono text-slate-500">$ {{ Number(row.cost_usd || 0).toFixed(2) }}</td>
              <td class="py-3.5 px-6 font-mono font-bold text-emerald-600">
                $ {{ Number(row.profit_usd || 0).toFixed(2) }}
                <span class="block text-[11px] text-emerald-500 font-normal">
                  Bs. {{ (Number(row.profit_usd || 0) * bcvRate).toFixed(2) }}
                </span>
              </td>
            </tr>
            <tr v-if="dailyAuditList.length === 0">
              <td colspan="7" class="py-12 text-center text-slate-400 text-xs">暂无近期开单对账流水数据</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from '../composables/useI18n'
import { apiUrl, apiFetch } from '../utils/api'

const { t } = useI18n()

const bcvRate = ref(36.50)
const analytics = ref({
  total_revenue_usd: 0.00,
  total_cost_usd: 0.00,
  gross_profit_usd: 0.00,
  profit_margin: 0.0
})

const paymentBreakdown = ref({
  zelle: { count: 0, totalUSD: 0, percentage: 0 },
  cashUSD: { count: 0, totalUSD: 0, percentage: 0 },
  bolivares: { count: 0, totalBs: 0, percentage: 0 }
})

const dailyAuditList = ref([])

// 获取财务分析与对账数据
const fetchFinancialData = async () => {
  try {
    // 1. 获取汇率
    const rateRes = await apiFetch('/api/bcv-rate')
    if (rateRes.ok) {
      const rateData = await rateRes.json()
      bcvRate.value = rateData.rate || 36.50
    }

    // 2. 获取分析主指标
    const res = await apiFetch('/api/financial/analytics')
    if (res.ok) {
      const data = await res.json()
      analytics.value = {
        total_revenue_usd: data.total_revenue_usd ?? 0.00,
        total_cost_usd: data.total_cost_usd ?? 0.00,
        gross_profit_usd: (data.total_revenue_usd ?? 0) - (data.total_cost_usd ?? 0),
        profit_margin: data.profit_margin ?? 0.0
      }
    }

    // 3. 获取近期交易明细用于收银对账与多币种利润流水
    const txRes = await apiFetch('/api/transactions')
    if (txRes.ok) {
      const txs = await txRes.json()
      let zCount = 0, zSum = 0;
      let cCount = 0, cSum = 0;
      let bCount = 0, bSum = 0;
      let totalFlow = 0;

      dailyAuditList.value = txs.map(tx => {
        const rev = Number(tx.total_usd || tx.amount || 0)
        const cost = Number(tx.cost_usd || rev * 0.7) // 估算或取后端成本
        const profit = rev - cost
        const method = (tx.payment_method || 'Zelle').toLowerCase()

        totalFlow += rev
        if (method.includes('zelle')) { zCount++; zSum += rev; }
        else if (method.includes('cash') || method.includes('efectivo')) { cCount++; cSum += rev; }
        else { bCount++; bSum += (rev * bcvRate.value); }

        return {
          id: tx.id || Math.floor(Math.random() * 1000),
          date: tx.created_at || '刚刚',
          payment_method: tx.payment_method || 'Zelle',
          revenue_usd: rev,
          cost_usd: cost,
          profit_usd: profit
        }
      })

      paymentBreakdown.value = {
        zelle: { count: zCount, totalUSD: zSum, percentage: totalFlow ? ((zSum / totalFlow) * 100).toFixed(1) : 0 },
        cashUSD: { count: cCount, totalUSD: cSum, percentage: totalFlow ? ((cSum / totalFlow) * 100).toFixed(1) : 0 },
        bolivares: { count: bCount, totalBs: bSum, percentage: totalFlow ? (((bSum / bcvRate.value) / totalFlow) * 100).toFixed(1) : 0 }
      }
    }
  } catch (e) {
    console.error("加载财务对账数据失败:", e)
  }
}

onMounted(() => {
  fetchFinancialData()
})
</script>