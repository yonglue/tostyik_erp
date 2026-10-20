<!-- src/components/FinancialView.vue -->
<template>
  <div class="space-y-6">
    
    <!-- 顶部利润核心指标卡片 (双币种总览) -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
      <div class="bg-white/75 backdrop-blur-xl p-6 rounded-2xl border border-white/80 shadow-lg transition-all duration-300 hover:scale-[1.02] hover:bg-white/90 space-y-2">
        <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">{{ tExt.revenue }}</p>
        <h3 class="text-2xl font-black text-blue-600 font-mono">$ {{ analytics.total_revenue_usd.toFixed(2) }}</h3>
        <p class="text-xs text-slate-400 font-mono">Bs. {{ (analytics.total_revenue_usd * bcvRate).toFixed(2) }}</p>
      </div>

      <div class="bg-white/75 backdrop-blur-xl p-6 rounded-2xl border border-white/80 shadow-lg transition-all duration-300 hover:scale-[1.02] hover:bg-white/90 space-y-2">
        <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">{{ tExt.cost }}</p>
        <h3 class="text-2xl font-black text-slate-700 font-mono">$ {{ analytics.total_cost_usd.toFixed(2) }}</h3>
        <p class="text-xs text-slate-400 font-mono">Bs. {{ (analytics.total_cost_usd * bcvRate).toFixed(2) }}</p>
      </div>

      <div class="bg-white/75 backdrop-blur-xl p-6 rounded-2xl border border-white/80 shadow-lg transition-all duration-300 hover:scale-[1.02] hover:bg-white/90 space-y-2">
        <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">{{ tExt.grossProfit }}</p>
        <h3 class="text-2xl font-black text-emerald-600 font-mono">$ {{ analytics.gross_profit_usd.toFixed(2) }}</h3>
        <p class="text-xs text-emerald-500 font-mono font-bold">Bs. {{ (analytics.gross_profit_usd * bcvRate).toFixed(2) }}</p>
      </div>

      <div class="bg-white/75 backdrop-blur-xl p-6 rounded-2xl border border-white/80 shadow-lg transition-all duration-300 hover:scale-[1.02] hover:bg-white/90 space-y-2">
        <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">{{ tExt.profitMargin }}</p>
        <h3 class="text-2xl font-black text-purple-600 font-mono">{{ analytics.profit_margin.toFixed(1) }}%</h3>
        <p class="text-xs text-slate-400 font-semibold">{{ tExt.stableProfit }}</p>
      </div>
    </div>

    <!-- 🌟 今日收银对账分类（毛玻璃质感汇总看板） -->
    <div class="bg-white/75 backdrop-blur-xl rounded-2xl border border-white/80 shadow-xl p-6 space-y-4 transition-all duration-300">
      <div class="flex items-center justify-between flex-wrap gap-3">
        <h3 class="font-bold text-slate-800 text-base flex items-center gap-2">
          💳 {{ tExt.dailyReconciliation }}
        </h3>
        <span class="text-xs bg-blue-500/10 text-blue-700 border border-blue-200/60 px-3 py-1 rounded-xl font-mono font-bold shadow-2xs">
          {{ tExt.bcvBase }}: {{ bcvRate }}
        </span>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <!-- 1. Card POS -->
        <div class="bg-white/70 hover:bg-white backdrop-blur-md border border-white/90 hover:border-blue-300 rounded-2xl p-4 space-y-1 shadow-2xs transition-all duration-200 hover:scale-[1.02]">
          <div class="flex items-center justify-between text-xs font-bold text-slate-500">
            <span>💳 {{ t.pos.payCardPos }}</span>
            <span class="text-blue-600 font-mono">{{ paymentBreakdown.cardPos.count }} {{ tExt.unit }}</span>
          </div>
          <div class="text-lg font-black text-slate-900 font-mono">$ {{ paymentBreakdown.cardPos.totalUSD.toFixed(2) }}</div>
          <div class="text-xs text-slate-400 font-mono">{{ tExt.ratio }}: {{ paymentBreakdown.cardPos.percentage }}%</div>
        </div>

        <!-- 2. Pago Móvil -->
        <div class="bg-white/70 hover:bg-white backdrop-blur-md border border-white/90 hover:border-blue-300 rounded-2xl p-4 space-y-1 shadow-2xs transition-all duration-200 hover:scale-[1.02]">
          <div class="flex items-center justify-between text-xs font-bold text-slate-500">
            <span>⚡ {{ t.pos.payPagoMovil }}</span>
            <span class="text-indigo-600 font-mono">{{ paymentBreakdown.pagoMovil.count }} {{ tExt.unit }}</span>
          </div>
          <div class="text-lg font-black text-slate-900 font-mono">$ {{ paymentBreakdown.pagoMovil.totalUSD.toFixed(2) }}</div>
          <div class="text-xs text-slate-400 font-mono">{{ tExt.ratio }}: {{ paymentBreakdown.pagoMovil.percentage }}%</div>
        </div>

        <!-- 3. Cash Bs -->
        <div class="bg-white/70 hover:bg-white backdrop-blur-md border border-white/90 hover:border-blue-300 rounded-2xl p-4 space-y-1 shadow-2xs transition-all duration-200 hover:scale-[1.02]">
          <div class="flex items-center justify-between text-xs font-bold text-slate-500">
            <span>🇻🇪 {{ t.pos.payCashBs }}</span>
            <span class="text-emerald-600 font-mono">{{ paymentBreakdown.cashBs.count }} {{ tExt.unit }}</span>
          </div>
          <div class="text-lg font-black text-slate-900 font-mono">$ {{ paymentBreakdown.cashBs.totalUSD.toFixed(2) }}</div>
          <div class="text-xs text-slate-400 font-mono">{{ tExt.ratio }}: {{ paymentBreakdown.cashBs.percentage }}%</div>
        </div>

        <!-- 4. Cash USD -->
        <div class="bg-white/70 hover:bg-white backdrop-blur-md border border-white/90 hover:border-blue-300 rounded-2xl p-4 space-y-1 shadow-2xs transition-all duration-200 hover:scale-[1.02]">
          <div class="flex items-center justify-between text-xs font-bold text-slate-500">
            <span>💵 {{ t.pos.payCashUsd }}</span>
            <span class="text-emerald-600 font-mono">{{ paymentBreakdown.cashUSD.count }} {{ tExt.unit }}</span>
          </div>
          <div class="text-lg font-black text-slate-900 font-mono">$ {{ paymentBreakdown.cashUSD.totalUSD.toFixed(2) }}</div>
          <div class="text-xs text-slate-400 font-mono">{{ tExt.ratio }}: {{ paymentBreakdown.cashUSD.percentage }}%</div>
        </div>

        <!-- 5. Pago Mixto (组合支付) -->
        <div class="bg-white/70 hover:bg-white backdrop-blur-md border border-white/90 hover:border-blue-300 rounded-2xl p-4 space-y-1 shadow-2xs transition-all duration-200 hover:scale-[1.02]">
          <div class="flex items-center justify-between text-xs font-bold text-slate-500">
            <span>🔄 {{ tExt.mixedPay }}</span>
            <span class="text-purple-600 font-mono">{{ paymentBreakdown.pagoMixto.count }} {{ tExt.unit }}</span>
          </div>
          <div class="text-lg font-black text-slate-900 font-mono">$ {{ paymentBreakdown.pagoMixto.totalUSD.toFixed(2) }}</div>
          <div class="text-xs text-slate-400 font-mono">{{ tExt.ratio }}: {{ paymentBreakdown.pagoMixto.percentage }}%</div>
        </div>
      </div>
    </div>

    <!-- 🌟 多币种每日利润对账报表表格（毛玻璃质感） -->
    <div class="bg-white/75 backdrop-blur-xl rounded-2xl border border-white/80 shadow-xl overflow-hidden transition-all duration-300">
      <div class="p-6 border-b border-slate-200/60 flex items-center justify-between bg-white/40 backdrop-blur-md">
        <div>
          <h3 class="font-bold text-slate-800 text-base">📈 {{ tExt.auditTitle }}</h3>
          <p class="text-xs text-slate-400 mt-0.5 font-medium">{{ tExt.auditSubtitle }}</p>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[850px]">
          <thead>
            <tr class="bg-white/60 backdrop-blur-md border-b border-slate-200/60 text-xs font-black text-slate-600 uppercase tracking-wider">
              <th class="py-3.5 px-6">{{ tExt.orderNo }}</th>
              <th class="py-3.5 px-6">{{ tExt.time }}</th>
              <th class="py-3.5 px-6">{{ tExt.payMethod }}</th>
              <th class="py-3.5 px-6">{{ tExt.revenueUsd }}</th>
              <th class="py-3.5 px-6">{{ tExt.revenueVes }}</th>
              <th class="py-3.5 px-6">{{ tExt.costUsd }}</th>
              <th class="py-3.5 px-6">{{ tExt.realProfit }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200/60 text-sm font-medium">
            <tr v-for="row in dailyAuditList" :key="row.id" class="hover:bg-blue-500/10 transition-all duration-200 cursor-pointer">
              <td class="py-3.5 px-6 font-mono font-black text-blue-600">#{{ row.id }}</td>
              <td class="py-3.5 px-6 text-xs text-slate-500 font-mono">{{ row.date }}</td>
              <td class="py-3.5 px-6">
                <span class="bg-blue-500/15 text-blue-700 border border-blue-200/60 px-2.5 py-1 rounded-lg text-xs font-bold font-mono shadow-2xs">
                  {{ row.payment_method }}
                </span>
              </td>
              <td class="py-3.5 px-6 font-mono font-black text-slate-900">$ {{ Number(row.revenue_usd || 0).toFixed(2) }}</td>
              <td class="py-3.5 px-6 font-mono text-slate-600 font-bold">Bs. {{ (Number(row.revenue_usd || 0) * bcvRate).toFixed(2) }}</td>
              <td class="py-3.5 px-6 font-mono text-slate-500 font-bold">$ {{ Number(row.cost_usd || 0).toFixed(2) }}</td>
              <td class="py-3.5 px-6 font-mono font-black text-emerald-600">
                $ {{ Number(row.profit_usd || 0).toFixed(2) }}
                <span class="block text-[11px] text-emerald-700/80 font-normal">
                  Bs. {{ (Number(row.profit_usd || 0) * bcvRate).toFixed(2) }}
                </span>
              </td>
            </tr>
            <tr v-if="dailyAuditList.length === 0">
              <td colspan="7" class="py-16 text-center text-slate-400 text-xs font-bold">{{ tExt.noData }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useI18n } from '../composables/useI18n'
import { apiFetch } from '../utils/api'

const { t, currentLang } = useI18n()

// 🌟 扩展翻译字典
const tExt = computed(() => {
  const isZh = currentLang.value === 'zh'
  const isEs = currentLang.value === 'es'
  return {
    revenue: isZh ? '总营业收入 (Revenue)' : isEs ? 'Ingresos Totales (Revenue)' : 'Total Revenue',
    cost: isZh ? '总进货成本 (Cost)' : isEs ? 'Costo Total (Cost)' : 'Total Cost',
    grossProfit: isZh ? '毛利润 (Gross Profit)' : isEs ? 'Ganancia Bruta (Gross Profit)' : 'Gross Profit',
    profitMargin: isZh ? '综合毛利率 (Margin)' : isEs ? 'Margen de Ganancia (Margin)' : 'Profit Margin',
    stableProfit: isZh ? '稳定盈利状态' : isEs ? 'Estado Rentable' : 'Stable Profit',
    dailyReconciliation: isZh ? '今日收银对账分类' : isEs ? 'Conciliación Diaria de Caja' : 'Daily Cashier Reconciliation',
    bcvBase: isZh ? 'BCV 汇率基准' : isEs ? 'Tasa Base BCV' : 'BCV Rate Base',
    mixedPay: isZh ? '组合支付' : isEs ? 'Pago Mixto' : 'Mixed Payment',
    unit: isZh ? '笔' : isEs ? 'trans.' : 'txns',
    ratio: isZh ? '占比' : isEs ? 'Porcentaje' : 'Ratio',
    auditTitle: isZh ? '多币种每日利润对账流水' : isEs ? 'Auditoría Diaria de Ganancias' : 'Daily Profit Audit Trail',
    auditSubtitle: isZh ? '自动换算每日各笔开单在美元与玻利瓦尔双币种下的真实毛利贡献' : isEs ? 'Conversión automática de ganancias reales en USD y Bs.' : 'Automatic calculation of real profit in USD and Bs.',
    orderNo: isZh ? '单据编号' : isEs ? 'Nro. Orden' : 'Order No.',
    time: isZh ? '交易时间' : isEs ? 'Hora' : 'Time',
    payMethod: isZh ? '支付方式' : isEs ? 'Método de Pago' : 'Payment Method',
    revenueUsd: isZh ? '营业额 (USD)' : isEs ? 'Ingresos (USD)' : 'Revenue (USD)',
    revenueVes: isZh ? '折算收入 (VES)' : isEs ? 'Ingresos (VES)' : 'Revenue (VES)',
    costUsd: isZh ? '进货成本 (USD)' : isEs ? 'Costo (USD)' : 'Cost (USD)',
    realProfit: isZh ? '真实毛利 (USD / Bs.)' : isEs ? 'Ganancia Real' : 'Real Profit',
    noData: isZh ? '暂无近期开单对账流水数据' : isEs ? 'Sin datos recientes' : 'No recent data'
  }
})

const bcvRate = ref(36.50)
const analytics = ref({
  total_revenue_usd: 0.00,
  total_cost_usd: 0.00,
  gross_profit_usd: 0.00,
  profit_margin: 0.0
})

const paymentBreakdown = ref({
  cardPos: { count: 0, totalUSD: 0, percentage: 0 },
  pagoMovil: { count: 0, totalUSD: 0, percentage: 0 },
  cashBs: { count: 0, totalUSD: 0, percentage: 0 },
  cashUSD: { count: 0, totalUSD: 0, percentage: 0 },
  pagoMixto: { count: 0, totalUSD: 0, percentage: 0 }
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
        gross_profit_usd: data.gross_profit_usd ?? ((data.total_revenue_usd ?? 0) - (data.total_cost_usd ?? 0)),
        profit_margin: data.profit_margin ?? 0.0
      }
    }

    // 3. 请求真实的 POS 订单数据（Orders），获取准确的支付方式和金额
    const orderRes = await apiFetch('/api/pos/orders')
    if (orderRes.ok) {
      const orders = await orderRes.json()
      let cpCount = 0, cpSum = 0; // Card POS
      let pmCount = 0, pmSum = 0; // Pago Móvil
      let cbCount = 0, cbSum = 0; // Cash Bs
      let cuCount = 0, cuSum = 0; // Cash USD
      let mixCount = 0, mixSum = 0; // Pago Mixto
      let totalFlow = 0;

      dailyAuditList.value = orders.map(order => {
        const rev = Number(order.totalUsd || order.total_usd || 0)
        const cost = Number(order.totalCostUsd || rev * 0.7) 
        const profit = rev - cost
        const method = String(order.paymentMethod || order.payment_method || 'Cash_USD').trim()

        totalFlow += rev
        const mUpper = method.toUpperCase()

        if (mUpper.includes('CARD_POS')) { cpCount++; cpSum += rev; }
        else if (mUpper.includes('PAGO_MOVIL')) { pmCount++; pmSum += rev; }
        else if (mUpper.includes('CASH_BS')) { cbCount++; cbSum += rev; }
        else if (mUpper.includes('CASH_USD')) { cuCount++; cuSum += rev; }
        else if (mUpper.includes('MIXTO') || mUpper.includes('MIX')) { mixCount++; mixSum += rev; }
        else { cuCount++; cuSum += rev; } // 默认兜底

        return {
          id: order.orderId || order.dbId || order.id,
          date: order.time || order.created_at || 'Just now',
          payment_method: method,
          revenue_usd: rev,
          cost_usd: cost,
          profit_usd: profit
        }
      })

      paymentBreakdown.value = {
        cardPos: { count: cpCount, totalUSD: cpSum, percentage: totalFlow ? ((cpSum / totalFlow) * 100).toFixed(1) : 0 },
        pagoMovil: { count: pmCount, totalUSD: pmSum, percentage: totalFlow ? ((pmSum / totalFlow) * 100).toFixed(1) : 0 },
        cashBs: { count: cbCount, totalUSD: cbSum, percentage: totalFlow ? ((cbSum / totalFlow) * 100).toFixed(1) : 0 },
        cashUSD: { count: cuCount, totalUSD: cuSum, percentage: totalFlow ? ((cuSum / totalFlow) * 100).toFixed(1) : 0 },
        pagoMixto: { count: mixCount, totalUSD: mixSum, percentage: totalFlow ? ((mixSum / totalFlow) * 100).toFixed(1) : 0 }
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