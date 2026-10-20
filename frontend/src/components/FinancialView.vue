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

    <!-- 顶部核心指标卡片 -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
      <!-- 1. 总营收 -->
      <div class="bg-white/75 backdrop-blur-xl p-6 rounded-2xl border border-white/80 shadow-lg space-y-2">
        <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">{{ tExt.revenue }}</p>
        <h3 class="text-2xl font-black text-blue-600 font-mono">$ {{ analytics.total_revenue_usd.toFixed(2) }}</h3>
        <p class="text-xs text-slate-400 font-mono">Bs. {{ (analytics.total_revenue_usd * bcvRate).toFixed(2) }}</p>
      </div>

      <!-- 2. 总商品成本 -->
      <div class="bg-white/75 backdrop-blur-xl p-6 rounded-2xl border border-white/80 shadow-lg space-y-2">
        <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">{{ tExt.cost }}</p>
        <h3 class="text-2xl font-black text-slate-700 font-mono">$ {{ analytics.total_cost_usd.toFixed(2) }}</h3>
        <p class="text-xs text-slate-400 font-mono">Bs. {{ (analytics.total_cost_usd * bcvRate).toFixed(2) }}</p>
      </div>

      <!-- 3. 日常开支总额 -->
      <div class="bg-white/75 backdrop-blur-xl p-6 rounded-2xl border border-white/80 shadow-lg space-y-2">
        <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">日常开支 (Expenses)</p>
        <h3 class="text-2xl font-black text-rose-600 font-mono">$ {{ analytics.total_expenses_usd.toFixed(2) }}</h3>
        <p class="text-xs text-rose-500 font-mono font-bold">Bs. {{ (analytics.total_expenses_usd * bcvRate).toFixed(2) }}</p>
      </div>

      <!-- 4. 真实净利润 -->
      <div class="bg-white/75 backdrop-blur-xl p-6 rounded-2xl border border-emerald-200 shadow-lg space-y-2 relative overflow-hidden">
        <div class="absolute top-0 right-0 w-16 h-16 bg-emerald-500/10 rounded-bl-full"></div>
        <p class="text-xs font-bold text-emerald-600 uppercase tracking-wider">{{ tExt.netProfit }}</p>
        <h3 class="text-2xl font-black text-emerald-700 font-mono">$ {{ analytics.net_profit_usd.toFixed(2) }}</h3>
        <p class="text-xs text-emerald-600 font-mono font-bold">Bs. {{ (analytics.net_profit_usd * bcvRate).toFixed(2) }}</p>
      </div>
    </div>

    <!-- 今日收银对账分类 -->
    <div class="bg-white/75 backdrop-blur-xl rounded-2xl border border-white/80 shadow-xl p-6 space-y-4">
      <div class="flex items-center justify-between flex-wrap gap-3">
        <h3 class="font-bold text-slate-800 text-base flex items-center gap-2">
          💳 {{ tExt.dailyReconciliation }}
        </h3>
        <span class="text-xs bg-blue-500/10 text-blue-700 border border-blue-200/60 px-3 py-1 rounded-xl font-mono font-bold shadow-2xs">
          {{ tExt.bcvBase }}: {{ bcvRate }}
        </span>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <div class="bg-white/70 hover:bg-white backdrop-blur-md border border-white/90 hover:border-blue-300 rounded-2xl p-4 space-y-1 shadow-2xs transition-all duration-200 hover:scale-[1.02]">
          <div class="flex items-center justify-between text-xs font-bold text-slate-500">
            <span>💳 {{ t.pos.payCardPos }}</span>
            <span class="text-blue-600 font-mono">{{ paymentBreakdown.cardPos.count }} {{ tExt.unit }}</span>
          </div>
          <div class="text-lg font-black text-slate-900 font-mono">$ {{ paymentBreakdown.cardPos.totalUSD.toFixed(2) }}</div>
          <div class="text-xs text-slate-400 font-mono">{{ tExt.ratio }}: {{ paymentBreakdown.cardPos.percentage }}%</div>
        </div>

        <div class="bg-white/70 hover:bg-white backdrop-blur-md border border-white/90 hover:border-blue-300 rounded-2xl p-4 space-y-1 shadow-2xs transition-all duration-200 hover:scale-[1.02]">
          <div class="flex items-center justify-between text-xs font-bold text-slate-500">
            <span>⚡ {{ t.pos.payPagoMovil }}</span>
            <span class="text-indigo-600 font-mono">{{ paymentBreakdown.pagoMovil.count }} {{ tExt.unit }}</span>
          </div>
          <div class="text-lg font-black text-slate-900 font-mono">$ {{ paymentBreakdown.pagoMovil.totalUSD.toFixed(2) }}</div>
          <div class="text-xs text-slate-400 font-mono">{{ tExt.ratio }}: {{ paymentBreakdown.pagoMovil.percentage }}%</div>
        </div>

        <div class="bg-white/70 hover:bg-white backdrop-blur-md border border-white/90 hover:border-blue-300 rounded-2xl p-4 space-y-1 shadow-2xs transition-all duration-200 hover:scale-[1.02]">
          <div class="flex items-center justify-between text-xs font-bold text-slate-500">
            <span>🇻🇪 {{ t.pos.payCashBs }}</span>
            <span class="text-emerald-600 font-mono">{{ paymentBreakdown.cashBs.count }} {{ tExt.unit }}</span>
          </div>
          <div class="text-lg font-black text-slate-900 font-mono">$ {{ paymentBreakdown.cashBs.totalUSD.toFixed(2) }}</div>
          <div class="text-xs text-slate-400 font-mono">{{ tExt.ratio }}: {{ paymentBreakdown.cashBs.percentage }}%</div>
        </div>

        <div class="bg-white/70 hover:bg-white backdrop-blur-md border border-white/90 hover:border-blue-300 rounded-2xl p-4 space-y-1 shadow-2xs transition-all duration-200 hover:scale-[1.02]">
          <div class="flex items-center justify-between text-xs font-bold text-slate-500">
            <span>💵 {{ t.pos.payCashUsd }}</span>
            <span class="text-emerald-600 font-mono">{{ paymentBreakdown.cashUSD.count }} {{ tExt.unit }}</span>
          </div>
          <div class="text-lg font-black text-slate-900 font-mono">$ {{ paymentBreakdown.cashUSD.totalUSD.toFixed(2) }}</div>
          <div class="text-xs text-slate-400 font-mono">{{ tExt.ratio }}: {{ paymentBreakdown.cashUSD.percentage }}%</div>
        </div>

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
    revenue: isZh ? '总营业收入 (Revenue)' : isEs ? 'Ingresos Totales' : 'Total Revenue',
    cost: isZh ? '总进货成本 (Cost)' : isEs ? 'Costo Total' : 'Total Cost',
    netProfit: isZh ? '净利润 (Net Profit)' : isEs ? 'Utilidad Neta' : 'Net Profit',
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
  total_expenses_usd: 0.00,
  net_profit_usd: 0.00
})

const paymentBreakdown = ref({
  cardPos: { count: 0, totalUSD: 0, percentage: 0 },
  pagoMovil: { count: 0, totalUSD: 0, percentage: 0 },
  cashBs: { count: 0, totalUSD: 0, percentage: 0 },
  cashUSD: { count: 0, totalUSD: 0, percentage: 0 },
  pagoMixto: { count: 0, totalUSD: 0, percentage: 0 }
})

const dailyAuditList = ref([])

const fetchFinancialData = async () => {
  try {
    // 1. 获取汇率
    const rateRes = await apiFetch('/api/bcv-rate')
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
      
      let cpCount = 0, cpSum = 0;
      let pmCount = 0, pmSum = 0;
      let cbCount = 0, cbSum = 0;
      let cuCount = 0, cuSum = 0;
      let mixCount = 0, mixSum = 0;
      let totalFlow = 0;

      dailyAuditList.value = activeOrders.map(order => {
        const rev = Number(order.totalUsd || 0)
        
        // 从订单明细中计算真实总成本
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
        totalFlow += rev
        const mUpper = method.toUpperCase()

        if (mUpper.includes('CARD_POS')) { cpCount++; cpSum += rev; }
        else if (mUpper.includes('PAGO_MOVIL')) { pmCount++; pmSum += rev; }
        else if (mUpper.includes('CASH_BS')) { cbCount++; cbSum += rev; }
        else if (mUpper.includes('CASH_USD')) { cuCount++; cuSum += rev; }
        else if (mUpper.includes('MIXTO') || mUpper.includes('MIX')) { mixCount++; mixSum += rev; }
        else { cuCount++; cuSum += rev; }

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
        cardPos: { count: cpCount, totalUSD: cpSum, percentage: totalFlow ? ((cpSum / totalFlow) * 100).toFixed(1) : 0 },
        pagoMovil: { count: pmCount, totalUSD: pmSum, percentage: totalFlow ? ((pmSum / totalFlow) * 100).toFixed(1) : 0 },
        cashBs: { count: cbCount, totalUSD: cbSum, percentage: totalFlow ? ((cbSum / totalFlow) * 100).toFixed(1) : 0 },
        cashUSD: { count: cuCount, totalUSD: cuSum, percentage: totalFlow ? ((cuSum / totalFlow) * 100).toFixed(1) : 0 },
        pagoMixto: { count: mixCount, totalUSD: mixSum, percentage: totalFlow ? ((mixSum / totalFlow) * 100).toFixed(1) : 0 }
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

    // 4. 结算总账
    analytics.value = {
      total_revenue_usd: totalRevenue,
      total_cost_usd: totalCost,
      total_expenses_usd: totalExpenses,
      net_profit_usd: totalRevenue - totalCost - totalExpenses
    }

  } catch (e) {
    console.error("加载财务对账数据失败:", e)
  }
}

// 🌟 核心功能：一键导出 CSV (Excel) 利润报表
const exportProfitReport = () => {
  const now = new Date()
  const dateStr = `${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}_${String(now.getHours()).padStart(2, '0')}${String(now.getMinutes()).padStart(2, '0')}`
  
  // 使用 Excel 的 \uFEFF BOM 头防止中文乱码
  let csvContent = "\uFEFF"

  // 1. 报表头
  csvContent += "TOSTIKYK ERP - 财务利润综合报表\n"
  csvContent += `导出时间,${now.toLocaleString()}\n`
  csvContent += `当前 BCV 汇率,${bcvRate.value}\n\n`

  // 2. 核心概览
  csvContent += "【核心财务指标 (USD / VES)】\n"
  csvContent += `总营业收入,$ ${analytics.value.total_revenue_usd.toFixed(2)},Bs. ${(analytics.value.total_revenue_usd * bcvRate.value).toFixed(2)}\n`
  csvContent += `总进货成本,$ ${analytics.value.total_cost_usd.toFixed(2)},Bs. ${(analytics.value.total_cost_usd * bcvRate.value).toFixed(2)}\n`
  csvContent += `日常开支总额,$ ${analytics.value.total_expenses_usd.toFixed(2)},Bs. ${(analytics.value.total_expenses_usd * bcvRate.value).toFixed(2)}\n`
  csvContent += `净利润 (Net Profit),$ ${analytics.value.net_profit_usd.toFixed(2)},Bs. ${(analytics.value.net_profit_usd * bcvRate.value).toFixed(2)}\n\n`

  // 3. 支付方式拆解
  csvContent += "【收银对账分类】\n"
  csvContent += `支付方式,笔数,折算营收(USD),占比\n`
  csvContent += `刷卡 POS,${paymentBreakdown.value.cardPos.count},$ ${paymentBreakdown.value.cardPos.totalUSD.toFixed(2)},${paymentBreakdown.value.cardPos.percentage}%\n`
  csvContent += `手机支付 Pago Móvil,${paymentBreakdown.value.pagoMovil.count},$ ${paymentBreakdown.value.pagoMovil.totalUSD.toFixed(2)},${paymentBreakdown.value.pagoMovil.percentage}%\n`
  csvContent += `玻利瓦尔现金,${paymentBreakdown.value.cashBs.count},$ ${paymentBreakdown.value.cashBs.totalUSD.toFixed(2)},${paymentBreakdown.value.cashBs.percentage}%\n`
  csvContent += `美金现金,${paymentBreakdown.value.cashUSD.count},$ ${paymentBreakdown.value.cashUSD.totalUSD.toFixed(2)},${paymentBreakdown.value.cashUSD.percentage}%\n`
  csvContent += `组合支付,${paymentBreakdown.value.pagoMixto.count},$ ${paymentBreakdown.value.pagoMixto.totalUSD.toFixed(2)},${paymentBreakdown.value.pagoMixto.percentage}%\n\n`

  // 4. 每日流水明细
  csvContent += "【每日利润对账流水明细】\n"
  csvContent += "单据编号,交易时间,支付方式,营业额(USD),折算收入(VES),进货成本(USD),真实毛利(USD),真实毛利(Bs.)\n"
  
  dailyAuditList.value.forEach(row => {
    // 防止支付方式中有逗号破坏 CSV 结构
    const safeMethod = `"${row.payment_method}"` 
    csvContent += `${row.id},${row.date},${safeMethod},${Number(row.revenue_usd).toFixed(2)},${(Number(row.revenue_usd) * bcvRate.value).toFixed(2)},${Number(row.cost_usd).toFixed(2)},${Number(row.profit_usd).toFixed(2)},${(Number(row.profit_usd) * bcvRate.value).toFixed(2)}\n`
  })

  // 触发下载
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