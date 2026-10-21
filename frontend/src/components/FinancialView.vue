<!-- src/components/FinancialView.vue -->
<template>
  <div class="space-y-6">
    
    <!-- 🌟 顶部标题与导出按钮 -->
    <div class="flex items-center justify-between">
      <h2 class="text-xl font-bold text-slate-800 flex items-center gap-2">📊 财务利润中心</h2>
      <button 
        @click="exportProfitReport"
        class="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-xl text-xs font-bold shadow-md shadow-emerald-500/20 transition-all cursor-pointer hover:scale-105"
      >
        📥 一键导出利润报表
      </button>
    </div>

    <!-- 顶部核心指标卡片 (改为 5 列) -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
      <div class="bg-white/75 backdrop-blur-xl p-5 rounded-2xl border border-white/80 shadow-lg space-y-2">
        <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">{{ tExt.revenue }}</p>
        <h3 class="text-2xl font-black text-blue-600 font-mono">$ {{ analytics.total_revenue_usd.toFixed(2) }}</h3>
        <p class="text-xs text-slate-400 font-mono">Bs. {{ (analytics.total_revenue_usd * bcvRate).toFixed(2) }}</p>
      </div>

      <div class="bg-white/75 backdrop-blur-xl p-5 rounded-2xl border border-white/80 shadow-lg space-y-2">
        <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">{{ tExt.cost }}</p>
        <h3 class="text-2xl font-black text-slate-700 font-mono">$ {{ analytics.total_cost_usd.toFixed(2) }}</h3>
        <p class="text-xs text-slate-400 font-mono">Bs. {{ (analytics.total_cost_usd * bcvRate).toFixed(2) }}</p>
      </div>

      <div class="bg-white/75 backdrop-blur-xl p-5 rounded-2xl border border-white/80 shadow-lg space-y-2">
        <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">日常开支 (Expenses)</p>
        <h3 class="text-2xl font-black text-rose-500 font-mono">$ {{ analytics.total_expenses_usd.toFixed(2) }}</h3>
        <p class="text-xs text-rose-400 font-mono font-bold">Bs. {{ (analytics.total_expenses_usd * bcvRate).toFixed(2) }}</p>
      </div>

      <!-- 🌟 新增：客户应收欠款 -->
      <div class="bg-amber-50/80 backdrop-blur-xl p-5 rounded-2xl border border-amber-200 shadow-lg space-y-2">
        <p class="text-xs font-bold text-amber-600 uppercase tracking-wider">客户应收欠款 (Fiado)</p>
        <h3 class="text-2xl font-black text-amber-700 font-mono">$ {{ analytics.total_debt_usd.toFixed(2) }}</h3>
        <p class="text-xs text-amber-600 font-mono font-bold">Bs. {{ (analytics.total_debt_usd * bcvRate).toFixed(2) }}</p>
      </div>

      <div class="bg-emerald-50/80 backdrop-blur-xl p-5 rounded-2xl border border-emerald-300 shadow-lg space-y-2 relative overflow-hidden">
        <div class="absolute top-0 right-0 w-16 h-16 bg-emerald-500/10 rounded-bl-full"></div>
        <p class="text-xs font-bold text-emerald-600 uppercase tracking-wider">{{ tExt.netProfit }}</p>
        <h3 class="text-2xl font-black text-emerald-700 font-mono">$ {{ analytics.net_profit_usd.toFixed(2) }}</h3>
        <p class="text-xs text-emerald-600 font-mono font-bold">Bs. {{ (analytics.net_profit_usd * bcvRate).toFixed(2) }}</p>
      </div>
    </div>

    <!-- 今日收银对账分类 (保持不变，省略部分代码以节省空间) -->
    <div class="bg-white/75 backdrop-blur-xl rounded-2xl border border-white/80 shadow-xl p-6 space-y-4">
      <!-- ... 内部的支付方式卡片 ... -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <!-- 这里保留你原来的支付拆分代码，我没有改动它 -->
        <div class="bg-white/70 p-4 rounded-2xl border border-white/90 shadow-2xs">
          <div class="text-xs font-bold text-slate-500">💳 {{ t.pos.payCardPos }}</div>
          <div class="text-lg font-black font-mono mt-1">$ {{ paymentBreakdown.cardPos.totalUSD.toFixed(2) }}</div>
        </div>
        <div class="bg-white/70 p-4 rounded-2xl border border-white/90 shadow-2xs">
          <div class="text-xs font-bold text-slate-500">⚡ {{ t.pos.payPagoMovil }}</div>
          <div class="text-lg font-black font-mono mt-1">$ {{ paymentBreakdown.pagoMovil.totalUSD.toFixed(2) }}</div>
        </div>
        <div class="bg-white/70 p-4 rounded-2xl border border-white/90 shadow-2xs">
          <div class="text-xs font-bold text-slate-500">🇻🇪 {{ t.pos.payCashBs }}</div>
          <div class="text-lg font-black font-mono mt-1">$ {{ paymentBreakdown.cashBs.totalUSD.toFixed(2) }}</div>
        </div>
        <div class="bg-white/70 p-4 rounded-2xl border border-white/90 shadow-2xs">
          <div class="text-xs font-bold text-slate-500">💵 {{ t.pos.payCashUsd }}</div>
          <div class="text-lg font-black font-mono mt-1">$ {{ paymentBreakdown.cashUSD.totalUSD.toFixed(2) }}</div>
        </div>
        <div class="bg-white/70 p-4 rounded-2xl border border-white/90 shadow-2xs">
          <div class="text-xs font-bold text-slate-500">🔄 {{ tExt.mixedPay }}</div>
          <div class="text-lg font-black font-mono mt-1">$ {{ paymentBreakdown.pagoMixto.totalUSD.toFixed(2) }}</div>
        </div>
      </div>
    </div>

    <!-- 每日利润对账流水 -->
    <div class="bg-white/75 backdrop-blur-xl rounded-2xl border border-white/80 shadow-xl overflow-hidden">
      <div class="p-6 border-b border-slate-200/60 flex items-center justify-between bg-white/40 backdrop-blur-md">
        <div>
          <h3 class="font-bold text-slate-800 text-base">📈 {{ tExt.auditTitle }}</h3>
          <p class="text-xs text-slate-400 mt-0.5 font-medium">{{ tExt.auditSubtitle }}</p>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[850px]">
          <!-- 表头保持不变 -->
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

const tExt = computed(() => {
  const isZh = currentLang.value === 'zh'
  const isEs = currentLang.value === 'es'
  return {
    revenue: isZh ? '总营业收入' : 'Ingresos Totales',
    cost: isZh ? '总进货成本' : 'Costo Total',
    netProfit: isZh ? '净利润' : 'Utilidad Neta',
    mixedPay: isZh ? '组合支付' : 'Pago Mixto',
    unit: isZh ? '笔' : 'trans.',
    ratio: isZh ? '占比' : 'Porcentaje',
    auditTitle: isZh ? '多币种每日利润对账流水' : 'Auditoría Diaria',
    auditSubtitle: isZh ? '自动换算真实毛利' : 'Cálculo automático de ganancias',
    orderNo: isZh ? '单据编号' : 'Nro. Orden',
    time: isZh ? '交易时间' : 'Hora',
    payMethod: isZh ? '支付方式' : 'Método de Pago',
    revenueUsd: isZh ? '营业额 (USD)' : 'Ingresos (USD)',
    revenueVes: isZh ? '折算收入 (VES)' : 'Ingresos (VES)',
    costUsd: isZh ? '进货成本 (USD)' : 'Costo (USD)',
    realProfit: isZh ? '真实毛利' : 'Ganancia Real',
    noData: isZh ? '暂无数据' : 'Sin datos'
  }
})

const bcvRate = ref(36.50)
const analytics = ref({
  total_revenue_usd: 0,
  total_cost_usd: 0,
  total_expenses_usd: 0,
  total_debt_usd: 0, // 🌟 新增：应收欠款
  net_profit_usd: 0
})

const paymentBreakdown = ref({
  cardPos: { totalUSD: 0 },
  pagoMovil: { totalUSD: 0 },
  cashBs: { totalUSD: 0 },
  cashUSD: { totalUSD: 0 },
  pagoMixto: { totalUSD: 0 }
})

const dailyAuditList = ref([])

const fetchFinancialData = async () => {
  try {
    // 1. 获取本地手动汇率
    const rateRes = await apiFetch('/api/settings/bcv-rate')
    if (rateRes.ok) {
      const rateData = await rateRes.json()
      bcvRate.value = rateData.rate || 36.50
    }

    // 2. 获取 POS 订单流水
    let totalRevenue = 0
    let totalCost = 0
    
    const orderRes = await apiFetch('/api/pos/orders')
    if (orderRes.ok) {
      const orders = await orderRes.json()
      const activeOrders = orders.filter(o => o.status !== 'REFUNDED')
      
      let cpSum = 0, pmSum = 0, cbSum = 0, cuSum = 0, mixSum = 0;

      dailyAuditList.value = activeOrders.map(order => {
        const rev = Number(order.totalUsd || 0)
        let orderCost = 0
        if (order.items && order.items.length > 0) {
          order.items.forEach(item => {
            orderCost += (Number(item.cost_price || 0) * Number(item.quantity || 0))
          })
        }

        const profit = rev - orderCost
        totalRevenue += rev
        totalCost += orderCost

        const method = String(order.paymentMethod || 'Cash_USD').trim()
        const mUpper = method.toUpperCase()

        if (mUpper.includes('CARD_POS')) { cpSum += rev; }
        else if (mUpper.includes('PAGO_MOVIL')) { pmSum += rev; }
        else if (mUpper.includes('CASH_BS')) { cbSum += rev; }
        else if (mUpper.includes('CASH_USD')) { cuSum += rev; }
        else if (mUpper.includes('MIXTO') || mUpper.includes('MIX')) { mixSum += rev; }
        else { cuSum += rev; }

        return {
          id: order.orderId || order.dbId,
          date: order.time || order.created_at || 'Just now',
          payment_method: method,
          revenue_usd: rev,
          cost_usd: orderCost,
          profit_usd: profit
        }
      })

      paymentBreakdown.value = {
        cardPos: { totalUSD: cpSum },
        pagoMovil: { totalUSD: pmSum },
        cashBs: { totalUSD: cbSum },
        cashUSD: { totalUSD: cuSum },
        pagoMixto: { totalUSD: mixSum }
      }
    }

    // 3. 获取日常开支总额
    let totalExpenses = 0
    const expRes = await apiFetch('/api/expenses')
    if (expRes.ok) {
      const expenses = await expRes.json()
      expenses.forEach(e => {
        const usdVal = e.currency === 'USD' ? Number(e.amount) : Number(e.amount) / Number(e.exchange_rate || 1)
        totalExpenses += usdVal
      })
    }

    // 🌟 4. 获取客户欠款总额 (数据关联的核心)
    let totalDebt = 0
    const debtRes = await apiFetch('/api/clients/analytics/debt-summary')
    if (debtRes.ok) {
      const debtData = await debtRes.json()
      totalDebt = debtData.total_debt_usd
    }

    // 5. 结算总账
    analytics.value = {
      total_revenue_usd: totalRevenue,
      total_cost_usd: totalCost,
      total_expenses_usd: totalExpenses,
      total_debt_usd: totalDebt,
      net_profit_usd: totalRevenue - totalCost - totalExpenses // 净利润公式不变
    }

  } catch (e) {
    console.error("加载财务对账数据失败:", e)
  }
}

// 导出报表 (保持之前的强大逻辑，只补充了新增的字段)
const exportProfitReport = () => {
  const now = new Date()
  const dateStr = `${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}_${String(now.getHours()).padStart(2, '0')}${String(now.getMinutes()).padStart(2, '0')}`
  let csvContent = "\uFEFF"

  csvContent += "TOSTIKYK ERP - 财务利润综合报表\n"
  csvContent += `导出时间,${now.toLocaleString()}\n`
  csvContent += `当前 BCV 汇率,${bcvRate.value}\n\n`

  csvContent += "【核心财务指标 (USD / VES)】\n"
  csvContent += `总营业收入,$ ${analytics.value.total_revenue_usd.toFixed(2)},Bs. ${(analytics.value.total_revenue_usd * bcvRate.value).toFixed(2)}\n`
  csvContent += `总进货成本,$ ${analytics.value.total_cost_usd.toFixed(2)},Bs. ${(analytics.value.total_cost_usd * bcvRate.value).toFixed(2)}\n`
  csvContent += `日常开支总额,$ ${analytics.value.total_expenses_usd.toFixed(2)},Bs. ${(analytics.value.total_expenses_usd * bcvRate.value).toFixed(2)}\n`
  csvContent += `客户应收欠款,$ ${analytics.value.total_debt_usd.toFixed(2)},Bs. ${(analytics.value.total_debt_usd * bcvRate.value).toFixed(2)}\n`
  csvContent += `净利润 (Net Profit),$ ${analytics.value.net_profit_usd.toFixed(2)},Bs. ${(analytics.value.net_profit_usd * bcvRate.value).toFixed(2)}\n\n`

  csvContent += "【每日利润对账流水明细】\n"
  csvContent += "单据编号,交易时间,支付方式,营业额(USD),折算收入(VES),进货成本(USD),真实毛利(USD),真实毛利(Bs.)\n"
  dailyAuditList.value.forEach(row => {
    const safeMethod = `"${row.payment_method}"` 
    csvContent += `${row.id},${row.date},${safeMethod},${Number(row.revenue_usd).toFixed(2)},${(Number(row.revenue_usd) * bcvRate.value).toFixed(2)},${Number(row.cost_usd).toFixed(2)},${Number(row.profit_usd).toFixed(2)},${(Number(row.profit_usd) * bcvRate.value).toFixed(2)}\n`
  })

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement("a")
  link.href = url
  link.download = `TOSTIKYK_Profit_Report_${dateStr}.csv`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

onMounted(() => {
  fetchFinancialData()
})
</script>